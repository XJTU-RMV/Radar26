import unittest

import numpy as np

from lisar.common.gimbal_control import (
    ObservedAngleBounds,
    SweepSearchBounds,
    SweepSearchConfig,
    SweepSearchController,
)
from lisar.common.search_state import CountermeasureSearchState, CountermeasureState
from lisar.common.laser_reference import ObservedLaserDotReference
from lisar.common.tracking_behavior import (
    LisarTrackingBehavior,
    MODULE_HOLD_FRAMES,
    TargetAngleStabilizer,
)
from lisar.common.types import LaserReferencePoint, TargetDetection
from lisar.difficulty.model_detector import Yolo26TargetDetector
from lisar.easy.tracking_cv import CvCountermeasureTracker
from lisar.lisar_tracker import LisarTracker


class FakeAlignController:
    def __init__(self):
        self.steps = []
        self.reset_count = 0

    def step(self, gimbal, laser_center, target_center, current_angle):
        self.steps.append((laser_center, target_center, current_angle))

    def reset(self):
        self.reset_count += 1


class FakeSearchController:
    def __init__(self):
        self.reset_count = 0
        self.step_count = 0
        self.remembered = []

    def reset(self, reset_target_memory=False):
        self.reset_count += 1

    def remember_target(self, target_world_angle, current_angle):
        self.remembered.append((target_world_angle, current_angle))

    def step(self, gimbal, current_angle):
        self.step_count += 1


class FakeYoloDetector:
    def __init__(self, detections=None):
        self.detections = detections or [(0, (40, 40, 60, 60), 0.9)]
        self.last_shape = None

    def predict(self, frame_bgr):
        self.last_shape = frame_bgr.shape
        return self.detections, {"source": "fake"}


class FakeGimbal:
    def __init__(self):
        self.angles = []

    def set_angle(self, yaw, pitch):
        self.angles.append((float(yaw), float(pitch)))


class TrackingBehaviorTest(unittest.TestCase):
    def test_legacy_hold_reacquires_immediately_before_first_target(self):
        state = CountermeasureSearchState(hold_after_seen_frames=MODULE_HOLD_FRAMES)

        self.assertEqual(state.update(False), CountermeasureState.REACQUIRE)

    def test_legacy_hold_waits_80_frames_after_seen_target(self):
        state = CountermeasureSearchState(hold_after_seen_frames=MODULE_HOLD_FRAMES)

        self.assertEqual(state.update(True), CountermeasureState.TRACK)
        for _ in range(MODULE_HOLD_FRAMES):
            self.assertEqual(state.update(False), CountermeasureState.LOST)
        self.assertEqual(state.update(False), CountermeasureState.REACQUIRE)

    def test_tracking_behavior_uses_passive_offset_when_inactive(self):
        behavior = LisarTrackingBehavior()
        align = FakeAlignController()
        search = FakeSearchController()
        detection = TargetDetection(
            center=(400, 300),
            bbox=None,
            confidence=1.0,
            source="test",
            debug={"world_angle": (10.0, -2.0)},
        )
        laser = LaserReferencePoint(center=(390, 300), predicted=False, source="test")

        state = behavior.step(None, detection, laser, (5.0, 0.0), False, align, search)

        self.assertEqual(state, CountermeasureState.TRACK)
        self.assertEqual(align.steps[-1][1], (300, 300))
        self.assertEqual(search.reset_count, 1)
        self.assertEqual(search.remembered[-1], ((10.0, -2.0), (5.0, 0.0)))

    def test_tracking_behavior_searches_after_hold_expires(self):
        behavior = LisarTrackingBehavior()
        align = FakeAlignController()
        search = FakeSearchController()
        detection = TargetDetection(center=(400, 300), bbox=None, confidence=1.0, source="test")
        laser = LaserReferencePoint(center=(390, 300), predicted=False, source="test")

        behavior.step(None, detection, laser, (5.0, 0.0), True, align, search)
        for _ in range(MODULE_HOLD_FRAMES):
            state = behavior.step(None, None, laser, (5.0, 0.0), True, align, search)
            self.assertEqual(state, CountermeasureState.LOST)
        state = behavior.step(None, None, laser, (5.0, 0.0), True, align, search)

        self.assertEqual(state, CountermeasureState.REACQUIRE)
        self.assertEqual(search.step_count, 1)

    def test_observed_angle_bounds_uses_strict_min_max(self):
        bounds = ObservedAngleBounds()

        self.assertIsNone(bounds.search_bounds())
        bounds.update((12.0, -3.0))
        self.assertIsNone(bounds.search_bounds())
        bounds.update((10.0, -3.0))

        search_bounds = bounds.search_bounds()
        self.assertEqual(search_bounds, SweepSearchBounds(10.0, 12.0, -3.0, -3.0))

    def test_sweep_search_clips_start_to_learned_bounds(self):
        gimbal = FakeGimbal()
        search = SweepSearchController(SweepSearchConfig(-5.0, 20.0, -10.0, 1.0))
        search.set_search_bounds(SweepSearchBounds(10.0, 15.0, -2.0, -2.0))

        target_yaw, target_pitch = search.step(gimbal, (17.0, 0.0))

        self.assertEqual(target_yaw, 15.0)
        self.assertAlmostEqual(target_pitch, -2.0)
        self.assertEqual(gimbal.angles[-1][0], 15.0)
        self.assertAlmostEqual(gimbal.angles[-1][1], -2.0)

    def test_target_stabilizer_reprojects_world_angle_and_rejects_out_of_range(self):
        camera_K = np.array([[100.0, 0.0, 50.0], [0.0, 100.0, 50.0], [0.0, 0.0, 1.0]])
        stabilizer = TargetAngleStabilizer(camera_K, np.zeros(5))
        detection = TargetDetection(
            center=(50, 50),
            bbox=None,
            confidence=1.0,
            source="test",
            debug={"world_angle": (0.0, 0.0)},
        )

        stabilized = stabilizer.update(detection, (0.0, 0.0))

        self.assertEqual(stabilized.center, (50, 50))
        self.assertEqual(stabilized.debug["raw_center"], (50, 50))
        out_of_range = TargetDetection(
            center=(50, 50),
            bbox=None,
            confidence=1.0,
            source="test",
            debug={"world_angle": (-6.0, 0.0)},
        )
        self.assertIsNone(stabilizer.update(out_of_range, (0.0, 0.0)))

    def test_yolo_detector_exposes_world_angle_for_common_stabilizer(self):
        camera_K = np.array([[100.0, 0.0, 50.0], [0.0, 100.0, 50.0], [0.0, 0.0, 1.0]])
        detector = Yolo26TargetDetector(
            detector=FakeYoloDetector(),
            img_size=100,
            camera_K=camera_K,
            dist_coeffs=np.zeros(5),
        )

        detection = detector.detect(np.zeros((100, 100, 3), dtype=np.uint8), {"current_angle": (1.0, 2.0)})

        self.assertEqual(detection.center, (50, 50))
        self.assertEqual(detection.debug["world_angle"], (1.0, 2.0))

    def test_yolo_detector_resizes_for_model_and_scales_back_to_frame(self):
        fake = FakeYoloDetector(detections=[(0, (10, 20, 30, 40), 0.9)])
        detector = Yolo26TargetDetector(detector=fake, img_size=50)

        detection = detector.detect(np.zeros((100, 200, 3), dtype=np.uint8), {"current_angle": (0.0, 0.0)})

        self.assertEqual(fake.last_shape, (50, 50, 3))
        self.assertEqual(detection.bbox, (40, 40, 120, 80))
        self.assertEqual(detection.center, (80, 60))
        self.assertEqual(detection.debug["model_center"], (20, 30))
        self.assertEqual(detection.debug["model_bbox"], (10, 20, 30, 40))
        self.assertEqual(detection.debug["detections"], [(0, [40, 40, 120, 80], 0.9)])

    def test_observed_laser_reference_matches_legacy_prediction_default(self):
        reference = ObservedLaserDotReference(allow_prediction=True)

        point = reference.locate(np.zeros((1000, 1200, 3), dtype=np.uint8))

        self.assertEqual(point.center, (1036, 967))
        self.assertTrue(point.predicted)

    def test_legacy_lisar_tracker_is_tracking_cv_wrapper(self):
        self.assertTrue(issubclass(LisarTracker, CvCountermeasureTracker))


if __name__ == "__main__":
    unittest.main()
