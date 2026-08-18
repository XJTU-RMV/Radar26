from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from callibrate.camera.extrinsic_calibration_core import (
    solve_main_camera_extrinsic,
    update_main_camera_extrinsic,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
DEMO_IMAGE_PATH = ROOT_DIR / "demo" / "demo1.jpg"


@dataclass
class CalibrationResult:
    rotation_matrix: np.ndarray
    translation_vector: np.ndarray
    reprojection_error: float
    image_points: np.ndarray


class CalibrationImageLabel(QLabel):
    point_added = pyqtSignal(float, float)

    def __init__(
        self,
        image: np.ndarray,
        parent: QWidget | None = None,
        *,
        enable_point_input: bool = True,
    ) -> None:
        super().__init__(parent)
        self._image = image
        self._base_pixmap = self._frame_to_pixmap(image)
        self._zoom = 1.0
        self._points: list[tuple[float, float]] = []
        self._enable_point_input = enable_point_input
        self._is_panning = False
        self._pan_start = QPoint()
        self._h_scroll_start = 0
        self._v_scroll_start = 0
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self._redraw()

    @property
    def points(self) -> list[tuple[float, float]]:
        return list(self._points)

    def set_points(self, points: list[tuple[float, float]]) -> None:
        self._points = list(points)
        self._redraw()

    def set_zoom(self, zoom: float) -> None:
        self._zoom = max(0.05, min(float(zoom), 8.0))
        self._redraw()

    def zoom_in(self) -> None:
        self._zoom = min(self._zoom * 1.25, 8.0)
        self._redraw()

    def zoom_out(self) -> None:
        self._zoom = max(self._zoom / 1.25, 0.2)
        self._redraw()

    def reset_zoom(self) -> None:
        self._zoom = 1.0
        self._redraw()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() in {Qt.MiddleButton, Qt.RightButton}:
            scroll_area = self.parent()
            if scroll_area is None:
                event.ignore()
                return
            self._is_panning = True
            self._pan_start = event.globalPos()
            self._h_scroll_start = scroll_area.horizontalScrollBar().value()
            self._v_scroll_start = scroll_area.verticalScrollBar().value()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        if not self._enable_point_input:
            event.ignore()
            return
        if event.button() != Qt.LeftButton:
            return
        x = event.pos().x() / self._zoom
        y = event.pos().y() / self._zoom
        if x < 0 or y < 0 or x >= self._image.shape[1] or y >= self._image.shape[0]:
            return
        self.point_added.emit(float(x), float(y))

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if not self._is_panning:
            super().mouseMoveEvent(event)
            return

        scroll_area = self.parent()
        if scroll_area is None:
            event.ignore()
            return

        delta = event.globalPos() - self._pan_start
        scroll_area.horizontalScrollBar().setValue(self._h_scroll_start - delta.x())
        scroll_area.verticalScrollBar().setValue(self._v_scroll_start - delta.y())
        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() in {Qt.MiddleButton, Qt.RightButton} and self._is_panning:
            self._is_panning = False
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:  # type: ignore[override]
        delta_y = event.angleDelta().y()
        if delta_y == 0:
            event.ignore()
            return

        old_zoom = self._zoom
        zoom_factor = 1.15 if delta_y > 0 else (1.0 / 1.15)
        new_zoom = max(0.05, min(old_zoom * zoom_factor, 8.0))
        if abs(new_zoom - old_zoom) < 1e-9:
            event.accept()
            return

        cursor_pos = event.pos()
        image_x = cursor_pos.x() / old_zoom
        image_y = cursor_pos.y() / old_zoom

        self._zoom = new_zoom
        self._redraw()

        scroll_area = self.parent()
        if scroll_area is not None and hasattr(scroll_area, "horizontalScrollBar"):
            hbar = scroll_area.horizontalScrollBar()
            vbar = scroll_area.verticalScrollBar()
            viewport_pos = scroll_area.viewport().mapFromGlobal(event.globalPos())
            hbar.setValue(int(round(image_x * new_zoom - viewport_pos.x())))
            vbar.setValue(int(round(image_y * new_zoom - viewport_pos.y())))

        event.accept()

    def _redraw(self) -> None:
        scaled_width = max(1, int(round(self._base_pixmap.width() * self._zoom)))
        scaled_height = max(1, int(round(self._base_pixmap.height() * self._zoom)))
        canvas = self._base_pixmap.scaled(
            scaled_width,
            scaled_height,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        for index, (x, y) in enumerate(self._points):
            px = int(round(x * self._zoom))
            py = int(round(y * self._zoom))
            cross_half = 8
            painter.drawLine(px - cross_half, py, px + cross_half, py)
            painter.drawLine(px, py - cross_half, px, py + cross_half)
            painter.drawText(px + 10, py - 10, f"P{index}")

        painter.end()
        self.setPixmap(canvas)
        self.resize(canvas.size())

    @staticmethod
    def _frame_to_pixmap(frame: np.ndarray) -> QPixmap:
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
        image = QImage(
            rgb_frame.data,
            rgb_frame.shape[1],
            rgb_frame.shape[0],
            rgb_frame.strides[0],
            QImage.Format_RGB888,
        )
        return QPixmap.fromImage(image.copy())


class ImageViewerDialog(QDialog):
    def __init__(
        self,
        *,
        title: str,
        image: np.ndarray,
        info_text: str,
        enable_point_input: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1400, 900)
        self._auto_fit_enabled = True

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        self._image_label = CalibrationImageLabel(
            image,
            enable_point_input=enable_point_input,
        )
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setWidget(self._image_label)
        self._image_label.setParent(self._scroll_area)
        root_layout.addWidget(self._scroll_area, 1)

        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(10)
        self._side_layout = side_layout

        tips = QLabel(info_text)
        tips.setWordWrap(True)
        side_layout.addWidget(tips)

        buttons = [
            ("适应窗口", self._fit_image_to_window)
        ]
        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            side_layout.addWidget(button)

        side_layout.addStretch(1)
        root_layout.addWidget(side_panel)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._fit_image_to_window()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._auto_fit_enabled:
            self._fit_image_to_window()

    def _zoom_in(self) -> None:
        self._auto_fit_enabled = False
        self._image_label.zoom_in()

    def _zoom_out(self) -> None:
        self._auto_fit_enabled = False
        self._image_label.zoom_out()

    def _reset_zoom(self) -> None:
        self._auto_fit_enabled = False
        self._image_label.reset_zoom()

    def _fit_image_to_window(self) -> None:
        viewport_size = self._scroll_area.viewport().size()
        if viewport_size.width() <= 1 or viewport_size.height() <= 1:
            return

        image_height, image_width = self._image_label._image.shape[:2]
        fit_scale = min(
            viewport_size.width() / image_width,
            viewport_size.height() / image_height,
        )
        if fit_scale <= 0:
            return

        self._auto_fit_enabled = True
        self._image_label.set_zoom(fit_scale)


class ExampleImageDialog(ImageViewerDialog):
    def __init__(self, image: np.ndarray, parent: QWidget | None = None) -> None:
        super().__init__(
            title="标定示例",
            image=image,
            info_text=(
                "示例说明:\n"
                "1. 这张图用于提示标定点位的大致位置与点击顺序\n"
                "2. 请按示例中标出的顺序，从 P0 开始依次点击\n"
                "3. 示例图只做参考，不会写入任何标定结果\n"
                "4. 同样支持滚轮缩放、右键或中键拖动平移"
            ),
            enable_point_input=False,
            parent=parent,
        )


class ExtrinsicCalibrationDialog(ImageViewerDialog):
    def __init__(
        self,
        *,
        image: np.ndarray,
        world_points: np.ndarray,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        config_path: str,
        keypoints_label: str,
        initial_exposure_us: float | None = None,
        image_loader: Callable[[float], np.ndarray] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            title="主相机外参标定",
            image=image,
            info_text="",
            enable_point_input=True,
            parent=parent,
        )

        self._world_points = np.asarray(world_points, dtype=np.float32)
        self._camera_matrix = np.asarray(camera_matrix, dtype=np.float64)
        self._dist_coeffs = np.asarray(dist_coeffs, dtype=np.float64)
        self._config_path = config_path
        self._image_loader = image_loader
        self._result: CalibrationResult | None = None
        self._image_points: list[tuple[float, float]] = []
        self._image_label.point_added.connect(self._handle_point_added)

        self._progress_label = QLabel()
        self._current_point_label = QLabel()
        self._clicked_pixel_label = QLabel()
        self._error_label = QLabel("重投影误差: --")
        self._keypoints_label = QLabel(f"keypoints_file: {keypoints_label}")
        self._keypoints_label.setWordWrap(True)
        operation_label = QLabel(
            "操作说明:\n"
            "1. 按 .pp 中按 name 排序后的顺序逐点点击\n"
            "2. 点击“加载示例”查看 demo/demo1.jpg 中的点位和顺序提示\n"
            "3. 滚轮缩放，鼠标右键或中键拖动平移视图\n"
            "4. 缩放和平移只改变显示，不改变点击顺序\n"
            "5. 点满后点击“计算并保存”更新 main_camera 外参"
        )
        operation_label.setWordWrap(True)

        self._side_layout.insertWidget(0, self._progress_label)
        self._side_layout.insertWidget(1, self._current_point_label)
        self._side_layout.insertWidget(2, self._clicked_pixel_label)
        self._side_layout.insertWidget(3, self._error_label)
        self._side_layout.insertWidget(4, self._keypoints_label)
        self._side_layout.insertWidget(5, operation_label)

        insert_pos = self._side_layout.count() - 1
        if self._image_loader is not None:
            exposure_label = QLabel("标定曝光(us)")
            self._side_layout.insertWidget(insert_pos, exposure_label)

            self._exposure_input = QDoubleSpinBox()
            self._exposure_input.setRange(1.0, 1_000_000.0)
            self._exposure_input.setDecimals(0)
            self._exposure_input.setSingleStep(1000.0)
            self._exposure_input.setValue(float(initial_exposure_us if initial_exposure_us is not None else 30000.0))
            self._exposure_input.setSuffix(" us")
            self._side_layout.insertWidget(insert_pos + 1, self._exposure_input)

            refresh_button = QPushButton("按当前曝光重新抓图")
            refresh_button.clicked.connect(self._reload_image)
            self._side_layout.insertWidget(insert_pos + 2, refresh_button)
            insert_pos += 3

        example_button = QPushButton("加载示例")
        example_button.clicked.connect(self._show_example)
        self._side_layout.insertWidget(insert_pos, example_button)

        delete_button = QPushButton("删除上一个点")
        delete_button.clicked.connect(self._remove_last_point)
        self._side_layout.insertWidget(insert_pos + 1, delete_button)

        reset_points_button = QPushButton("重置点位")
        reset_points_button.clicked.connect(self._reset_points)
        self._side_layout.insertWidget(insert_pos + 2, reset_points_button)

        save_button = QPushButton("计算并保存")
        save_button.clicked.connect(self._save_calibration)
        self._side_layout.insertWidget(insert_pos + 3, save_button)

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        self._side_layout.insertWidget(insert_pos + 4, cancel_button)

        self._refresh_status()

    @property
    def result(self) -> CalibrationResult | None:
        return self._result

    def _show_example(self) -> None:
        image = cv2.imread(str(DEMO_IMAGE_PATH))
        if image is None:
            QMessageBox.warning(self, "加载示例失败", f"未能读取示例图像: {DEMO_IMAGE_PATH}")
            return
        dialog = ExampleImageDialog(image, parent=self)
        dialog.exec_()

    def _save_calibration(self) -> None:
        if len(self._image_points) != len(self._world_points):
            QMessageBox.warning(
                self,
                "点数不足",
                f"当前已有 {len(self._image_points)} 个图像点，需要 {len(self._world_points)} 个。",
            )
            return

        try:
            rotation_matrix, translation_vector, reprojection_error = solve_main_camera_extrinsic(
                self._world_points,
                np.asarray(self._image_points, dtype=np.float32),
                self._camera_matrix,
                self._dist_coeffs,
            )
            update_main_camera_extrinsic(
                self._config_path,
                rotation_matrix,
                translation_vector,
            )
        except Exception as exc:
            QMessageBox.critical(self, "标定失败", str(exc))
            return

        self._result = CalibrationResult(
            rotation_matrix=rotation_matrix,
            translation_vector=translation_vector,
            reprojection_error=reprojection_error,
            image_points=np.asarray(self._image_points, dtype=np.float32),
        )
        self._error_label.setText(f"重投影误差: {reprojection_error:.4f} px")
        QMessageBox.information(
            self,
            "标定完成",
            f"main_camera 外参已更新。\n重投影误差: {reprojection_error:.4f} px",
        )
        self.accept()

    def _remove_last_point(self) -> None:
        if not self._image_points:
            return
        self._image_points.pop()
        self._image_label.set_points(self._image_points)
        self._refresh_status()

    def _reset_points(self) -> None:
        self._image_points = []
        self._image_label.set_points(self._image_points)
        self._error_label.setText("重投影误差: --")
        self._refresh_status()

    def _handle_point_added(self, x: float, y: float) -> None:
        if len(self._image_points) >= len(self._world_points):
            QMessageBox.information(self, "点位已满", "当前图像点数量已经与世界点数量一致。")
            return
        self._image_points.append((x, y))
        self._image_label.set_points(self._image_points)
        self._refresh_status()

    def _reload_image(self) -> None:
        if self._image_loader is None:
            return

        try:
            image = self._image_loader(float(self._exposure_input.value()))
        except Exception as exc:
            QMessageBox.critical(self, "抓图失败", str(exc))
            return

        self._image_label._image = image
        self._image_label._base_pixmap = self._image_label._frame_to_pixmap(image)
        self._reset_points()
        self._auto_fit_enabled = True
        self._fit_image_to_window()

    def _refresh_status(self) -> None:
        count = len(self._image_points)
        total = len(self._world_points)
        self._progress_label.setText(f"已标点数: {count}/{total}")
        if count > 0:
            x, y = self._image_points[-1]
            self._clicked_pixel_label.setText(f"当前像素坐标: ({x:.1f}, {y:.1f})")
        else:
            self._clicked_pixel_label.setText("当前像素坐标: --")
        if count < total:
            self._current_point_label.setText(f"当前应点击点: P{count}")
        else:
            self._current_point_label.setText("当前应点击点: 已完成，可计算")
