GAME_PROGRESS_ACTIVE = 4


class CountermeasureDifficultyTracker:
    """Track countermeasure difficulty from referee-system state transitions."""

    def __init__(self, camera, sub_camera_config):
        self.camera = camera
        self.default_exposure = float(sub_camera_config.exposure_time)
        self.default_gain = float(sub_camera_config.gain)
        self.default_gamma_enable = (
            bool(sub_camera_config.gamma_enable) if "gamma_enable" in sub_camera_config else None
        )
        self.default_gamma = float(sub_camera_config.gamma) if self.default_gamma_enable else 1.0
        self.stage3_exposure = float(sub_camera_config.stage3.exposure_time)
        self.stage3_gain = float(sub_camera_config.stage3.gain)
        self.stage3_gamma_enable = (
            bool(sub_camera_config.stage3.gamma_enable)
            if "gamma_enable" in sub_camera_config.stage3
            else None
        )
        self.stage3_gamma = float(sub_camera_config.stage3.gamma) if self.stage3_gamma_enable else 1.0
        self.game_active = False
        self.success_count = 0
        self.difficulty = 1
        self._countered = False

    def update(self, game_progress, enemy_aircraft_countered):
        game_active = int(game_progress) == GAME_PROGRESS_ACTIVE
        if game_active != self.game_active:
            self.game_active = game_active
            self.reset()
            return self.difficulty

        if not game_active:
            return self.difficulty

        countered = bool(enemy_aircraft_countered)
        if countered and not self._countered:
            self.success_count += 1
            if self.success_count == 1:
                self.difficulty = 2
            elif self.success_count == 3:
                self.difficulty = 3
                self._set_camera(self.stage3_exposure, self.stage3_gain)
                self._set_gamma(self.stage3_gamma_enable, self.stage3_gamma)
        self._countered = countered
        return self.difficulty

    def reset(self):
        self.success_count = 0
        self.difficulty = 1
        self._countered = False
        self._set_gamma(self.default_gamma_enable, self.default_gamma)
        self._set_camera(self.default_exposure, self.default_gain)

    def _set_camera(self, exposure, gain):
        if not self.camera.set_exposure(exposure):
            raise RuntimeError(f"Failed to set sub-camera exposure to {exposure}")
        if not self.camera.set_gain(gain):
            raise RuntimeError(f"Failed to set sub-camera gain to {gain}")

    def _set_gamma(self, gamma_enable, gamma):
        if gamma_enable is None:
            return
        if not self.camera.set_gamma(gamma, enable=gamma_enable):
            raise RuntimeError(f"Failed to set sub-camera gamma to enable={gamma_enable}, gamma={gamma}")
