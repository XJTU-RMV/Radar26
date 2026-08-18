from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence
import cv2
import numpy as np

from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QImage, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from callibrate.camera.extrinsic_calibration_core import parse_pp_file, resolve_keypoints_path
from ui.extrinsic_calibration_dialog import ExtrinsicCalibrationDialog
from ui.radar_runtime_controller import (
    RadarMapTarget,
    RadarRuntimeController,
    RadarRuntimeOptions,
    RadarRuntimeStatus,
    build_runtime_config,
    parse_runtime_options,
)
from utils.config import resolve_runtime_flags

DEFAULT_MAP_CLASS_NAMES = ("R1", "R2", "R3", "R4", "R7", "B1", "B2", "B3", "B4", "B7")
FIELD_MAP_DISPLAY_SIZE = QSize(1120, 600)
FIELD_X_RANGE_CM = 2800.0
FIELD_Y_RANGE_CM = 1500.0
HOT_REGION_MIN_ENEMY_GROUND = 2
HOT_REGION_MIN_ALLY_GROUND = 2

def prepare_qt_plugin_path() -> None:
    """Prefer PyQt5 plugins over OpenCV plugins when available."""
    for site_package in sys.path:
        if "site-packages" not in site_package:
            continue
        plugin_path = Path(site_package) / "PyQt5" / "Qt5" / "plugins"
        if plugin_path.exists():
            os.environ.setdefault("QT_PLUGIN_PATH", str(plugin_path))
            os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(plugin_path))
            break

#设置ui中字体颜色等格式
def build_stylesheet() -> str:
    return """
    QMainWindow, QWidget#centralWidget {
        background: rgb(191, 188, 188);
        color: rgb(0, 0, 0);
        font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
        font-size: 13px;
    }

    /* 1. 顶层卡片：最强层次感，使用纯黑粗边框 */
    QFrame[card="true"] {
        background: rgba(255, 255, 255, 225);
        border: 2px solid #000000;
        border-radius: 16px;
    }

    /* 2. 标题：无需边框，通过字重拉开层次 */
    QLabel[cardTitle="true"] {
        color: #000000;
        font-size: 18px;
        font-weight: 800;
        background: transparent;
    }

    /* 3. 视频/主展示区：稍微柔和的深灰边框 */
    QLabel[videoLabel="true"] {
        background: #fdfdfd;
        border: 2px solid #333333;
        border-radius: 14px;
    }

    /* 4. 状态小标签：细边框，弱化存在感，增加精致度 */
    QLabel[statusValue="true"] {
        color: #222222;
        font-weight: 600;
        background: rgba(255, 255, 255, 150);
        border: 1px solid #666666; 
        border-radius: 8px;
        padding: 2px 8px;
    }

    /* 5. 按钮：增加悬停时的边框加粗效果 */
    QPushButton {
        background: #ffffff;
        color: #000000;
        border: 1.5px solid #222222;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 700;
    }
    QPushButton:hover {
        background: #000000;
        color: #ffffff; /* 悬停反色，极强交互感 */
        border: 1.5px solid #000000;
    }
    QPushButton:pressed {
        background: #333333;
    }

    /* 6. 文本编辑框：使用“内嵌”感的边框 */
    QPlainTextEdit {
        background: rgba(255, 255, 255, 240);
        color: #000000;
        border: 2px solid #222222;
        border-radius: 10px;
        padding: 10px;
        /* 选中时使用深绿色，增加专业感 */
        selection-background-color: #228B22; 
        selection-color: #ffffff;
        font-family: "JetBrains Mono", "Consolas", monospace;
    }
    QPlainTextEdit:focus {
        border: 2px solid #000000; /* 聚焦时边框变黑，提示正在输入 */
    }

    QLineEdit {
        background: rgba(255, 255, 255, 240);
        color: #000000;
        border: 1.5px solid #222222;
        border-radius: 10px;
        padding: 8px 10px;
        font-weight: 700;
        font-family: "JetBrains Mono", "Consolas", monospace;
    }
    QLineEdit:focus {
        border: 2px solid #000000;
    }
    """


def load_image_bgr(path: Path) -> np.ndarray | None:
    # 使用 np.fromfile + imdecode 读取图片，兼容包含中文的文件路径。
    try:
        encoded = np.fromfile(str(path), dtype=np.uint8)
    except OSError:
        return None
    if encoded.size == 0:
        return None
    return cv2.imdecode(encoded, cv2.IMREAD_COLOR)


def load_runtime_class_names(runtime_options: RadarRuntimeOptions) -> tuple[str, ...]:
    # 地图标注名称优先与运行时配置保持一致，读取失败时再回退默认值。
    try:
        cfg = build_runtime_config(runtime_options)
        class_names = tuple(cfg.get("armor_detector", {}).get("class_names", ()))
        if class_names:
            return class_names
    except Exception:
        pass
    return DEFAULT_MAP_CLASS_NAMES


def resolve_map_target_label(target: RadarMapTarget, class_names: Sequence[str]) -> str:
    if target.class_id == 10:
        return "RA"
    if target.class_id == 11:
        return "BA"
    if 0 <= target.class_id < len(class_names):
        return class_names[target.class_id]
    return f"ID:{target.class_id}"


def resolve_map_target_color(class_id: int) -> tuple[int, int, int]:
    return (50, 50, 255) if class_id < 5 or class_id == 10 else (255, 100, 0)


def is_enemy_ground_class(class_id: int, faction: str) -> bool:
    return class_id in ({5, 6, 7, 8, 9} if faction == "red" else {0, 1, 2, 3, 4})


def is_ally_ground_class(class_id: int, faction: str) -> bool:
    return class_id in ({0, 1, 2, 3, 4} if faction == "red" else {5, 6, 7, 8, 9})


def resolve_map_region_cell(target: RadarMapTarget) -> tuple[int, int] | None:
    x_ratio = target.x_m * 100.0 / FIELD_X_RANGE_CM
    y_ratio = target.y_m * 100.0 / FIELD_Y_RANGE_CM
    if not (0.0 <= x_ratio <= 1.0 and 0.0 <= y_ratio <= 1.0):
        return None
    col = min(2, max(0, int(x_ratio * 3)))
    row = 0 if y_ratio >= 0.5 else 1
    return row, col


def resolve_hot_region_cells(
    map_targets: Sequence[RadarMapTarget],
    faction: str,
) -> set[tuple[int, int]]:
    faction = str(faction).strip().lower()
    counts = {(row, col): [0, 0] for row in range(2) for col in range(3)}
    for target in map_targets:
        cell = resolve_map_region_cell(target)
        if cell is None:
            continue
        if is_enemy_ground_class(target.class_id, faction):
            counts[cell][0] += 1
        elif is_ally_ground_class(target.class_id, faction):
            counts[cell][1] += 1
    return {
        cell
        for cell, (enemy_count, ally_count) in counts.items()
        if enemy_count >= HOT_REGION_MIN_ENEMY_GROUND
        and ally_count >= HOT_REGION_MIN_ALLY_GROUND
    }


def draw_hot_regions_on_map(
    display_map: np.ndarray,
    hot_cells: set[tuple[int, int]],
) -> None:
    if not hot_cells:
        return

    map_h, map_w = display_map.shape[:2]
    col_edges = [round(map_w * index / 3) for index in range(4)]
    row_edges = [0, round(map_h / 2), map_h]
    pulse = 0.18 + 0.06 * np.sin(time.monotonic() * 5.0)
    fill_color = (40, 40, 180)
    border_color = (30, 30, 220)
    for row, col in hot_cells:
        x1, x2 = col_edges[col], col_edges[col + 1]
        y1, y2 = row_edges[row], row_edges[row + 1]
        roi = display_map[y1:y2, x1:x2]
        overlay = roi.copy()
        cv2.rectangle(overlay, (0, 0), (x2 - x1 - 1, y2 - y1 - 1), fill_color, -1)
        cv2.addWeighted(overlay, pulse, roi, 1.0 - pulse, 0, dst=roi)
        cv2.rectangle(display_map, (x1 + 5, y1 + 5), (x2 - 6, y2 - 6), (255, 255, 255), 5)
        cv2.rectangle(display_map, (x1 + 8, y1 + 8), (x2 - 9, y2 - 9), border_color, 3)


def draw_region_grid_on_map(base_map_img: np.ndarray, faction: str) -> np.ndarray:
    display_map = base_map_img.copy()
    map_h, map_w = display_map.shape[:2]
    col_edges = [round(map_w * index / 3) for index in range(4)]
    row_edges = [0, round(map_h / 2), map_h]
    is_blue = str(faction).strip().lower() == "blue"

    overlay = display_map.copy()
    line_color = (255, 255, 255)
    shadow_color = (0, 0, 0)
    for x in col_edges[1:-1]:
        cv2.line(overlay, (x, 0), (x, map_h - 1), line_color, 2)
        cv2.line(display_map, (x, 0), (x, map_h - 1), shadow_color, 5)
    cv2.line(overlay, (0, row_edges[1]), (map_w - 1, row_edges[1]), line_color, 2)
    cv2.line(display_map, (0, row_edges[1]), (map_w - 1, row_edges[1]), shadow_color, 5)
    display_map = cv2.addWeighted(overlay, 0.65, display_map, 0.35, 0)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.1
    thickness = 2
    for row in range(2):
        for col in range(3):
            faction_row = 1 - row if is_blue else row
            faction_col = 2 - col if is_blue else col
            label = faction_row * 3 + faction_col + 1
            x1, x2 = col_edges[col], col_edges[col + 1]
            y1, y2 = row_edges[row], row_edges[row + 1]
            text = str(label)
            (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            text_origin = (
                x1 + 18,
                y1 + 18 + text_h,
            )
            cv2.putText(
                display_map,
                text,
                text_origin,
                font,
                font_scale,
                (255, 255, 255),
                thickness + 3,
                cv2.LINE_AA,
            )
            cv2.putText(
                display_map,
                text,
                text_origin,
                font,
                font_scale,
                (0, 0, 0),
                thickness,
                cv2.LINE_AA,
            )
    return display_map


def draw_targets_on_map(
    base_map_img: np.ndarray,
    map_targets: Sequence[RadarMapTarget],
    class_names: Sequence[str],
    faction: str,
) -> np.ndarray:
    # 每次都从底图副本开始绘制，避免上一帧的结果残留到下一帧。
    display_map = base_map_img.copy()
    map_h, map_w = display_map.shape[:2]

    # 地图坐标系：原点在左下角，x+ 向右，y+ 向上。
    # 下方坐标轴绘制代码当前保留为参考，便于后续需要时快速恢复调试显示。
    # origin = (50, map_h - 55)
    # arrow_len = 35
    # cv2.arrowedLine(
    #     display_map,
    #     origin,
    #     (origin[0] + arrow_len, origin[1]),
    #     (0, 180, 0),
    #     2,
    #     tipLength=0.3,
    # )
    # cv2.putText(
    #     display_map,
    #     "x+",
    #     (origin[0] + arrow_len + 5, origin[1] - 5),
    #     cv2.FONT_HERSHEY_SIMPLEX,
    #     0.6,
    #     (0, 180, 0),
    #     2,
    # )
    # cv2.arrowedLine(
    #     display_map,
    #     origin,
    #     (origin[0], origin[1] - arrow_len),
    #     (0, 165, 255),
    #     2,
    #     tipLength=0.3,
    # )
    # cv2.putText(
    #     display_map,
    #     "y+",
    #     (origin[0] - 10, origin[1] - arrow_len - 8),
    #     cv2.FONT_HERSHEY_SIMPLEX,
    #     0.6,
    #     (0, 165, 255),
    #     2,
    # )

    draw_hot_regions_on_map(display_map, resolve_hot_region_cells(map_targets, faction))

    for target in map_targets:
        pos_x_cm = target.x_m * 100.0
        pos_y_cm = target.y_m * 100.0

        # RadarMapTarget 使用的是场地坐标（米），这里统一换算到地图像素坐标。
        x_ratio = float(np.clip(pos_x_cm / FIELD_X_RANGE_CM, 0.0, 1.0))
        y_ratio = float(np.clip(pos_y_cm / FIELD_Y_RANGE_CM, 0.0, 1.0))
        px = int(round(x_ratio * (map_w - 1)))
        py = int(round((1.0 - y_ratio) * (map_h - 1)))

        color = resolve_map_target_color(target.class_id)
        label = resolve_map_target_label(target, class_names)
        text_y = min(max(py, 18), map_h - 8)

        # 预测点与稳定跟踪点使用不同样式，便于值班时快速区分状态。
        if target.is_guess:
            cv2.circle(display_map, (px, py), 10, color, 2)
            cv2.circle(display_map, (px, py), 3, color, -1)
            text = label
        elif target.source == "demod":
            cv2.rectangle(display_map, (px - 8, py - 8), (px + 8, py + 8), color, -1)
            cv2.rectangle(display_map, (px - 10, py - 10), (px + 10, py + 10), (0, 0, 0), 2)
            text = label
        else:
            cv2.circle(display_map, (px, py), 8, color, -1)
            cv2.circle(display_map, (px, py), 10, (0, 0, 0), 2)
            text = label

        cv2.putText(
            display_map,
            text,
            (px + 12, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 0),
            2,
        )

    return display_map


class CardFrame(QFrame):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        *,
        content_margins: tuple[int, int, int, int] = (16, 14, 16, 16),
        spacing: int = 12,
        body_spacing: int = 10,
    ) -> None:
        super().__init__()
        self.setProperty("card", True)
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(*content_margins)
        self.outer_layout.setSpacing(spacing)

        if title:
            title_label = QLabel(title)
            title_label.setProperty("cardTitle", True)
            self.outer_layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setProperty("cardSubtitle", True)
            subtitle_label.setWordWrap(True)
            self.outer_layout.addWidget(subtitle_label)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(body_spacing)
        self.outer_layout.addLayout(self.body_layout, 1)


# 用于视频流区域的 QLabel，负责在控件大小变化时重新裁切或缩放画面。
class VideoFeedLabel(QLabel):
    def __init__(self, title: str, mode: str) -> None:
        super().__init__()
        self.title = title
        self.mode = mode
        self._live_pixmap: QPixmap | None = None
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("videoLabel", True)
        self.setMinimumSize(320, 180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(960, 540) if self.mode == "tracking" else QSize(560, 420)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self.has_live_frame():
            self._apply_live_pixmap()

    def has_live_frame(self) -> bool:
        return self._live_pixmap is not None and not self._live_pixmap.isNull()

    def set_frame_pixmap(self, pixmap: QPixmap) -> None:
        self._live_pixmap = pixmap
        self._apply_live_pixmap()

    def clear_frame(self) -> None:
        self._live_pixmap = None
        super().clear()

    def _apply_live_pixmap(self) -> None:
        if not self.has_live_frame():
            return

        width = max(self.width(), 320)
        height = max(self.height(), 180)
        # 保留完整图像内容，允许四周留白，避免主/副相机画面被裁剪。
        canvas = QPixmap(width, height)
        canvas.fill(Qt.transparent)
        scaled = self._live_pixmap.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        painter = QPainter(canvas)
        painter.drawPixmap((width - scaled.width()) // 2, (height - scaled.height()) // 2, scaled)
        painter.end()
        self.setPixmap(canvas)

    def refresh_demo(self, phase: float) -> None:
        self.clear_frame()


# 通用图像面板，地图、波形和激光预览都复用这一套显示逻辑。
class BlankPanelWidget(QLabel):
    def __init__(self, size_hint: QSize, minimum_height: int = 0) -> None:
        super().__init__()
        self._size_hint = size_hint
        self._panel_pixmap: QPixmap | None = None
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("videoLabel", True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWordWrap(True)
        if minimum_height > 0:
            self.setMinimumHeight(minimum_height)

    def sizeHint(self) -> QSize:
        return self._size_hint

    def minimumSizeHint(self) -> QSize:
        # 避免 QLabel 因加载大图后抬高最小宽度，把左右布局比例撑坏。
        return QSize(max(self.minimumWidth(), 1), max(self.minimumHeight(), 1))

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self._panel_pixmap is not None and not self._panel_pixmap.isNull():
            self._apply_panel_pixmap()

    def set_panel_pixmap(self, pixmap: QPixmap) -> None:
        self._panel_pixmap = pixmap
        self.setText("")
        # 每次设置新图后立即按当前控件尺寸重绘，避免看到旧帧缩放结果。
        self._apply_panel_pixmap()
        self.updateGeometry()

    def clear_panel_pixmap(self) -> None:
        self._panel_pixmap = None
        super().clear()
        self.updateGeometry()

    def _apply_panel_pixmap(self) -> None:
        if self._panel_pixmap is None or self._panel_pixmap.isNull():
            return

        width = max(self.width(), 1)
        height = max(self.height(), 1)
        canvas = QPixmap(width, height)
        canvas.fill(Qt.transparent)
        scaled = self._panel_pixmap.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        painter = QPainter(canvas)
        painter.drawPixmap((width - scaled.width()) // 2, (height - scaled.height()) // 2, scaled)
        painter.end()
        self.setPixmap(canvas)


class DemodLogPanel(CardFrame):
    def __init__(self, title: str, subtitle: str, initial_lines: Sequence[str]) -> None:
        super().__init__(title, subtitle)
        self.text_box = QPlainTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setPlainText("\n".join(initial_lines))
        self._scroll_to_bottom()
        self.body_layout.addWidget(self.text_box, 1)

    def set_lines(self, lines: Sequence[str]) -> None:
        self.text_box.setPlainText("\n".join(lines))
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        cursor = self.text_box.textCursor()
        cursor.movePosition(cursor.End)
        self.text_box.setTextCursor(cursor)
        self.text_box.ensureCursorVisible()


class ConsolePanel(CardFrame):
    def __init__(self, main_exposure_default: float, sub_exposure_default: float) -> None:
        super().__init__("控制台")

        button_grid = QGridLayout()
        button_grid.setHorizontalSpacing(10)
        button_grid.setVerticalSpacing(10)
        self.buttons: Dict[str, QPushButton] = {}
        button_specs = [
            ("start", "启动雷达站"),
            ("calib", "启动标定"),
            ("clear", "清空日志"),
        ]
        for index, (key, text) in enumerate(button_specs):
            button = QPushButton(text)
            button_grid.addWidget(button, index // 2, index % 2)
            self.buttons[key] = button
        self.body_layout.addLayout(button_grid)

        exposure_grid = QGridLayout()
        exposure_grid.setHorizontalSpacing(12)
        exposure_grid.setVerticalSpacing(10)

        main_exposure_title = QLabel("主相机曝光(us)")
        main_exposure_title.setProperty("metaLabel", True)
        self.main_exposure_input = QDoubleSpinBox()
        self.main_exposure_input.setRange(1.0, 1_000_000.0)
        self.main_exposure_input.setDecimals(0)
        self.main_exposure_input.setSingleStep(1000.0)
        self.main_exposure_input.setValue(float(main_exposure_default))
        self.main_exposure_input.setSuffix(" us")

        sub_exposure_title = QLabel("副相机曝光(us)")
        sub_exposure_title.setProperty("metaLabel", True)
        self.sub_exposure_input = QDoubleSpinBox()
        self.sub_exposure_input.setRange(1.0, 1_000_000.0)
        self.sub_exposure_input.setDecimals(0)
        self.sub_exposure_input.setSingleStep(1000.0)
        self.sub_exposure_input.setValue(float(sub_exposure_default))
        self.sub_exposure_input.setSuffix(" us")

        apply_exposure_button = QPushButton("应用曝光")
        self.buttons["apply_exposure"] = apply_exposure_button

        exposure_grid.addWidget(main_exposure_title, 0, 0)
        exposure_grid.addWidget(self.main_exposure_input, 0, 1)
        exposure_grid.addWidget(sub_exposure_title, 1, 0)
        exposure_grid.addWidget(self.sub_exposure_input, 1, 1)
        exposure_grid.addWidget(apply_exposure_button, 2, 0, 1, 2)
        self.body_layout.addLayout(exposure_grid)

        key_test_grid = QGridLayout()
        key_test_grid.setHorizontalSpacing(12)
        key_test_grid.setVerticalSpacing(10)
        key_test_title = QLabel("测试密钥")
        key_test_title.setProperty("metaLabel", True)
        self.break_key_input = QLineEdit()
        self.break_key_input.setMaxLength(6)
        self.break_key_input.setPlaceholderText("输入6位ASCII密钥")
        send_break_key_button = QPushButton("发送密钥")
        self.buttons["send_break_key"] = send_break_key_button
        key_test_grid.addWidget(key_test_title, 0, 0)
        key_test_grid.addWidget(self.break_key_input, 0, 1)
        key_test_grid.addWidget(send_break_key_button, 0, 2)
        key_test_grid.setColumnStretch(1, 1)
        self.body_layout.addLayout(key_test_grid)

        status_grid = QGridLayout()
        status_grid.setHorizontalSpacing(14)
        status_grid.setVerticalSpacing(10)
        self.status_labels: Dict[str, QLabel] = {}

        status_layout_specs = [
            ("当前阵容", 0, 0),
            ("己方加密等级", 1, 0),
            ("当前密钥", 2, 0),
            ("双倍易伤状态", 0, 2),
            ("双倍易伤次数", 1, 2),
            ("反制成功次数", 2, 2),
        ]
        for name, row, column in status_layout_specs:
            title = QLabel(name)
            title.setProperty("metaLabel", True)
            title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            value = QLabel("待机")
            value.setProperty("statusValue", True)
            value.setAlignment(Qt.AlignCenter)
            if name == "当前密钥":
                value.setMinimumWidth(110)
            status_grid.addWidget(title, row, column)
            status_grid.addWidget(value, row, column + 1)
            self.status_labels[name] = value
        status_grid.setColumnStretch(0, 0)
        status_grid.setColumnStretch(1, 1)
        status_grid.setColumnStretch(2, 0)
        status_grid.setColumnStretch(3, 1)
        self.body_layout.addLayout(status_grid)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.body_layout.addWidget(self.log_box, 1)
        self.log_lines: List[str] = []
        self.log_box.setPlainText("\n".join(self.log_lines))

        self.buttons["clear"].clicked.connect(self.clear_log)

    def set_status(self, name: str, value: str) -> None:
        if name in self.status_labels:
            self.status_labels[name].setText(value)

    def append_log(self, line: str) -> None:
        self.log_lines.append(line)
        self.log_lines = self.log_lines[-12:]
        self.log_box.setPlainText("\n".join(self.log_lines))
        cursor = self.log_box.textCursor()
        cursor.movePosition(cursor.End)
        self.log_box.setTextCursor(cursor)

    def clear_log(self) -> None:
        self.log_lines = []
        self.log_box.setPlainText("\n".join(self.log_lines))

    def set_log_lines(self, lines: Sequence[str]) -> None:
        self.log_lines = list(lines)[-12:]
        self.log_box.setPlainText("\n".join(self.log_lines))
        cursor = self.log_box.textCursor()
        cursor.movePosition(cursor.End)
        self.log_box.setTextCursor(cursor)


class MainWindow(QMainWindow):
    def __init__(
        self,
        runtime_options: RadarRuntimeOptions | None = None
    ) -> None:
        super().__init__()
        self.setWindowTitle("DX雷达")
        self.resize(1600, 900)
        self.setMinimumSize(1280, 720)
        self.setStyleSheet(build_stylesheet())

        # runtime_controller 负责启动主线程，并向 UI 暴露统一的状态快照接口。
        self.runtime_options = runtime_options or RadarRuntimeOptions()
        self.runtime_controller = RadarRuntimeController(self.runtime_options)
        self.runtime_cfg = build_runtime_config(self.runtime_options)
        resolve_runtime_flags(self.runtime_cfg)

        self.map_path = Path(self.runtime_cfg.transform.map_path)
        self.map_class_names = load_runtime_class_names(self.runtime_options)
        self.field_map_base_img: np.ndarray | None = None
        self._last_runtime_state: str | None = None
        self._last_runtime_message = ""
        self._latest_runtime_status = self.runtime_controller.get_status()
        self._console_local_lines: List[str] = []
        self._manual_break_key_request: dict[str, str] | None = None

        # 处理布局和组件
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(18)

        self.left_column = self._build_left_column()
        self.right_column = self._build_right_column()
        self.main_layout.addWidget(self.left_column, 5)
        self.main_layout.addWidget(self.right_column, 3)

        # 关联按键和线程函数
        self.console_panel.buttons["start"].clicked.connect(self._start_radar_station)
        self.console_panel.buttons["calib"].clicked.connect(self._start_main_camera_calibration)
        self.console_panel.buttons["apply_exposure"].clicked.connect(self._apply_camera_exposure)
        self.console_panel.buttons["send_break_key"].clicked.connect(self._send_manual_break_key)
        self.console_panel.break_key_input.returnPressed.connect(self._send_manual_break_key)
        self.console_panel.buttons["clear"].clicked.connect(self._clear_console_local_log)
        self._load_field_map()
        self._refresh_ui_by_status(self._latest_runtime_status, log_transition=False)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._tick_status)
        self.status_timer.start(100)

        self.image_timer = QTimer(self)
        self.image_timer.timeout.connect(self._tick_image)
        self.image_timer.start(33)

        # self._tick_status()
        # self._tick_image()

    def _build_left_column(self) -> QWidget:
        # 左侧聚焦视觉主链路：Tracking、辅助画面和赛场地图。
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        top_row = QWidget()
        self.video_top_layout = QHBoxLayout(top_row)
        self.video_top_layout.setContentsMargins(0, 0, 0, 0)
        self.video_top_layout.setSpacing(16)

        self.tracking_card = CardFrame(
            "",
            "",
            content_margins=(8, 8, 8, 8),
            spacing=0,
            body_spacing=0,
        )
        self.tracking_label = VideoFeedLabel("Tracking 检测画面", "tracking")
        self.tracking_card.body_layout.addWidget(self.tracking_label, 1)
        self.tracking_meta = QLabel("")
        self.tracking_meta.setProperty("metaLabel", True)
        self.tracking_meta.hide()
        self.tracking_card.body_layout.addWidget(self.tracking_meta)

        self.sub_camera_card = CardFrame(
            "",
            "",
            content_margins=(8, 8, 8, 8),
            spacing=0,
            body_spacing=0,
        )
        self.sub_camera_label = VideoFeedLabel("副相机画面", "sub")
        self.sub_camera_card.body_layout.addWidget(self.sub_camera_label, 1)
        self.sub_camera_meta = QLabel("")
        self.sub_camera_meta.setProperty("metaLabel", True)
        self.sub_camera_meta.hide()
        self.sub_camera_card.body_layout.addWidget(self.sub_camera_meta)

        self.video_top_layout.addWidget(self.tracking_card, 4)
        self.video_top_layout.addWidget(self.sub_camera_card, 3)

        map_card = CardFrame(
            "",
            "",
            content_margins=(8, 8, 8, 8),
            spacing=0,
            body_spacing=0,
        )
        self.field_map = BlankPanelWidget(QSize(1120, 600), minimum_height=280)
        map_card.body_layout.addWidget(self.field_map, 1)

        layout.addWidget(top_row, 1)
        layout.addWidget(map_card, 1)
        return container

    def _should_use_single_sub_camera_view(self, _status: RadarRuntimeStatus) -> bool:
        if bool(self.runtime_cfg.get("enable_vision_localization", True)):
            return False
        return bool(self.runtime_cfg.get("enable_laser_tracking", False)) and not bool(
            self.runtime_cfg.get("use_video", False)
        )

    def _update_video_layout(self, status: RadarRuntimeStatus) -> None:
        single_sub_view = self._should_use_single_sub_camera_view(status)
        self.tracking_card.setVisible(not single_sub_view)
        self.video_top_layout.setStretch(0, 0 if single_sub_view else 4)
        self.video_top_layout.setStretch(1, 1 if single_sub_view else 3)

    def _build_right_column(self) -> QWidget:
        # 右侧放辅助观测面板和控制台，尽量不打断主画面浏览。
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        info_lines: Sequence[str] = []
        jam_lines: Sequence[str] = []
        self.info_panel = DemodLogPanel("信息波解调输出", "", info_lines)
        self.jam_panel = DemodLogPanel("干扰波解调输出", "", jam_lines)

        self.console_panel = ConsolePanel(
            main_exposure_default=float(self.runtime_cfg.main_camera.exposure_time),
            sub_exposure_default=float(self.runtime_cfg.sub_camera.exposure_time),
        )

        layout.addWidget(self.info_panel, 3)
        layout.addWidget(self.jam_panel, 2)
        layout.addWidget(self.console_panel, 1)
        return container

    def _append_console_log(self, line: str) -> None:
        self._console_local_lines.append(line)
        self._console_local_lines = self._console_local_lines[-12:]
        self._refresh_console_log(self._latest_runtime_status)

    def _clear_console_local_log(self) -> None:
        self._console_local_lines = []
        self._refresh_console_log(self._latest_runtime_status)

    def _refresh_console_log(self, status: RadarRuntimeStatus) -> None:
        self.console_panel.set_log_lines(
            [*status.match_log_lines, *self._console_local_lines]
        )

    def _send_manual_break_key(self) -> None:
        key = self.console_panel.break_key_input.text().strip()
        if len(key) != 6 or not key.isascii():
            self._append_console_log("[密钥测试] 请输入6位ASCII密钥。")
            return

        try:
            result = self.runtime_controller.send_break_key(key)
        except Exception as exc:
            self._append_console_log(f"[密钥测试] 发送失败: {exc}")
            return

        self.console_panel.break_key_input.clear()
        if bool(result["sent_now"]):
            self._manual_break_key_request = {"key": key, "phase": "sent"}
            self._append_console_log(f"[密钥测试] 已发送密钥 {key}，等待裁判系统确认。")
            return

        self._manual_break_key_request = {"key": key, "phase": "queued"}
        remaining = float(result["cooldown_remaining"])
        self._append_console_log(
            f"[密钥测试] 密钥 {key} 已进入冷却队列，约 {remaining:.1f}s 后发送。"
        )

    def _poll_manual_break_key_result(self, status: RadarRuntimeStatus) -> None:
        if self._manual_break_key_request is None:
            return

        key = self._manual_break_key_request["key"]
        phase = self._manual_break_key_request["phase"]
        if phase == "queued":
            if status.pending_break_key == key:
                return
            if status.break_key_last_key != key:
                return
            self._manual_break_key_request["phase"] = "sent"
            if status.break_key_pending:
                self._append_console_log(
                    f"[密钥测试] 已发送队列中的密钥 {key}，等待裁判系统确认。"
                )
                return

        if status.break_key_last_key != key:
            return
        if status.break_key_correct is True:
            self._append_console_log(
                f"[密钥测试] 密钥 {key} 破解成功，当前加密等级={status.encryption_level}。"
            )
            self._manual_break_key_request = None
        elif status.break_key_correct is False:
            self._append_console_log(f"[密钥测试] 密钥 {key} 破解失败，裁判系统未确认。")
            self._manual_break_key_request = None

    def _start_radar_station(self) -> None:
        """
        ”启动雷达站“槽函数
        """
        if not self.runtime_controller.start():
            self._append_console_log("[控制] 雷达站已经在启动中或运行中。")
            return
        self._refresh_ui_by_status(self.runtime_controller.get_status())

    def _start_main_camera_calibration(self) -> None:
        self._append_console_log("[控制] 正在准备主相机外参标定...")
        try:
            image = self._load_calibration_image()
            world_points, keypoints_path = self._load_main_camera_world_points()
        except Exception as exc:
            self._append_console_log(f"[异常] 标定准备失败: {exc}")
            QMessageBox.critical(self, "标定准备失败", str(exc))
            return

        image_loader = None if self.runtime_cfg.use_video else self._capture_main_camera_frame
        initial_exposure_us = None if self.runtime_cfg.use_video else float(self.runtime_cfg.main_camera.exposure_time)

        dialog = ExtrinsicCalibrationDialog(
            image=image,
            world_points=world_points,
            camera_matrix=np.array(self.runtime_cfg.main_camera.K, dtype=np.float64).reshape(3, 3),
            dist_coeffs=np.array(self.runtime_cfg.main_camera.dist_coeffs, dtype=np.float64),
            config_path=str(Path(self.runtime_options.config_path).resolve()),
            keypoints_label=str(keypoints_path),
            initial_exposure_us=initial_exposure_us,
            image_loader=image_loader,
            parent=self,
        )
        if dialog.exec_() != QDialog.Accepted or dialog.result is None:
            self._append_console_log("[控制] 已取消主相机标定。")
            return

        self._append_console_log(
            f"[系统] 主相机外参已更新，重投影误差 {dialog.result.reprojection_error:.4f} px。"
        )

    def _apply_camera_exposure(self) -> None:
        main_exposure = float(self.console_panel.main_exposure_input.value())
        sub_exposure = float(self.console_panel.sub_exposure_input.value())

        try:
            if self.runtime_controller.set_main_exposure(main_exposure):
                self._append_console_log(f"[控制] 主相机曝光已设置为 {main_exposure:.0f} us")
            else:
                self._append_console_log("[异常] 主相机曝光设置失败")
        except Exception as exc:
            self._append_console_log(f"[异常] 主相机曝光设置失败: {exc}")

        try:
            if self.runtime_cfg.use_video:
                raise RuntimeError("当前为视频模式，副相机未启用")
            if self.runtime_controller.set_sub_exposure(sub_exposure):
                self._append_console_log(f"[控制] 副相机曝光已设置为 {sub_exposure:.0f} us")
            else:
                self._append_console_log("[异常] 副相机曝光设置失败")
        except Exception as exc:
            self._append_console_log(f"[异常] 副相机曝光设置失败: {exc}")

    def _load_main_camera_world_points(self) -> tuple[np.ndarray, Path]:
        keypoints_file = self.runtime_cfg.transform.keypoints_file
        if not keypoints_file:
            raise RuntimeError("params.yaml 中未配置 transform.keypoints_file")

        keypoints_path = resolve_keypoints_path(self.runtime_options.config_path, keypoints_file)
        if not keypoints_path.exists():
            raise FileNotFoundError(f"未找到关键点文件: {keypoints_path}")

        world_points = parse_pp_file(keypoints_path)
        if len(world_points) == 0:
            raise RuntimeError(f"关键点文件为空: {keypoints_path}")
        return world_points, keypoints_path

    def _load_calibration_image(self) -> np.ndarray:
        if self.runtime_cfg.use_video:
            frame = self._load_first_video_frame(Path(self.runtime_cfg.video_path))
            if frame is None:
                raise RuntimeError(f"无法从视频中读取首帧: {self.runtime_cfg.video_path}")
            return frame
        return self._capture_main_camera_frame()

    @staticmethod
    def _load_first_video_frame(video_path: Path) -> np.ndarray | None:
        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            return None
        try:
            ok, frame = capture.read()
            if not ok:
                return None
            return frame
        finally:
            capture.release()

    def _capture_main_camera_frame(self, exposure_us: float | None = None) -> np.ndarray:
        from driver.hik_camera.hik import SimpleHikCamera

        if exposure_us is not None:
            self.runtime_cfg.main_camera.exposure_time = float(exposure_us)
        camera = SimpleHikCamera(self.runtime_cfg.main_camera, camera_role="main")
        camera.start_streaming()
        camera.register_group("ui_calibration")
        latest_rgb = None
        try:
            for _ in range(20):
                frame_rgb, _ = camera.get_image_latest("ui_calibration", timeout=1.0)
                if frame_rgb is not None:
                    latest_rgb = frame_rgb
            if latest_rgb is None:
                raise RuntimeError("主相机未返回图像帧")
            return cv2.cvtColor(latest_rgb, cv2.COLOR_RGB2BGR)
        finally:
            camera.close()

    def _load_field_map(self) -> bool:
        # 地图底图只在加载时缩放一次，后续每帧只叠加目标点，减少重复开销。
        self.field_map.setToolTip(str(self.map_path))
        self.field_map_base_img = None
        if not self.map_path.exists():
            self.field_map.clear_panel_pixmap()
            self.field_map.setText(f"未找到地图文件:\n{self.map_path.name}")
            return False

        map_image = load_image_bgr(self.map_path)
        if map_image is None:
            self.field_map.clear_panel_pixmap()
            self.field_map.setText(f"地图加载失败:\n{self.map_path.name}")
            return False

        resized_map = cv2.resize(
            map_image,
            (FIELD_MAP_DISPLAY_SIZE.width(), FIELD_MAP_DISPLAY_SIZE.height()),
            interpolation=cv2.INTER_AREA,
        )
        self.field_map_base_img = draw_region_grid_on_map(
            resized_map,
            self.runtime_cfg.faction,
        )
        self._update_field_map_panel(self.runtime_controller.get_status())
        return True

    def _reload_field_map(self) -> None:
        if self._load_field_map():
            self._append_console_log(f"[控制] 已装载赛场地图: {self.map_path.name}")
            return
        self._append_console_log(f"[异常] 地图加载失败: {self.map_path.name}")

    def _refresh_ui_by_status(
        self,
        status: RadarRuntimeStatus,
        log_transition: bool = True,
    ) -> None:
        # 运行状态相关的按钮、状态栏和地图刷新都统一收敛到这里处理。
        state_changed = (
            status.state != self._last_runtime_state
            or status.message != self._last_runtime_message
        )
        if log_transition and state_changed:
            log_line = self._build_runtime_log_line(status)
            if log_line:
                self._append_console_log(log_line)

        self._last_runtime_state = status.state
        self._last_runtime_message = status.message
        self._update_video_layout(status)

        start_button = self.console_panel.buttons["start"]
        calib_button = self.console_panel.buttons["calib"]
        if status.state == "starting":
            start_button.setText("启动中...")
            start_button.setEnabled(False)
            calib_button.setEnabled(False)
        elif status.state == "running":
            start_button.setText("雷达站运行中")
            start_button.setEnabled(False)
            calib_button.setEnabled(False)
        elif status.state == "error":
            start_button.setText("重新启动雷达站")
            start_button.setEnabled(True)
            calib_button.setEnabled(True)
        else:
            start_button.setText("启动雷达站")
            start_button.setEnabled(True)
            calib_button.setEnabled(True)

        exposure_enabled = status.state == "running" and (
            status.main_camera_available or status.sub_camera_available
        )
        self.console_panel.main_exposure_input.setEnabled(
            status.state == "running" and status.main_camera_available
        )
        self.console_panel.sub_exposure_input.setEnabled(
            status.state == "running" and status.sub_camera_available and not self.runtime_cfg.use_video
        )
        self.console_panel.buttons["apply_exposure"].setEnabled(exposure_enabled)
        self.console_panel.break_key_input.setEnabled(status.state == "running")
        self.console_panel.buttons["send_break_key"].setEnabled(status.state == "running")

        self.console_panel.set_status("己方加密等级", self._format_encryption_level(status))
        self.console_panel.set_status("当前密钥", self._format_current_key(status))
        self.console_panel.set_status("当前阵容", self._format_faction(status))
        self.console_panel.set_status("双倍易伤状态", self._format_double_vulnerability_status(status))
        self.console_panel.set_status("双倍易伤次数", self._format_double_vulnerability_count(status))
        self.console_panel.set_status("反制成功次数", self._format_countermeasure_success_count(status))
        self._update_field_map_panel(status)

    def _build_runtime_log_line(self, status: RadarRuntimeStatus) -> str | None:
        if status.state == "starting":
            return "[控制] 正在启动雷达站主线程..."
        if status.state == "running":
            if status.message != "运行中":
                return f"[系统] 主线程已启动，{status.message}"
            return "[系统] 主线程已启动，Tracking 画面正在刷新。"
        if status.state == "error":
            return f"[异常] 雷达站启动失败: {status.message}"
        if status.state == "idle" and self._last_runtime_state not in {None, "idle"}:
            return "[系统] 雷达站已停止，界面回到待机状态。"
        return None

    def _format_radar_status(self, status: RadarRuntimeStatus) -> str:
        return {
            "idle": "待机",
            "starting": "启动中",
            "running": "运行中",
            "error": "异常",
        }.get(status.state, status.message)

    def _format_encryption_level(self, status: RadarRuntimeStatus) -> str:
        if status.state != "running":
            return "待机"
        if status.encryption_level is None:
            return "--"
        return str(status.encryption_level)

    def _format_current_key(self, status: RadarRuntimeStatus) -> str:
        if status.state != "running":
            return "待机"
        return status.current_key or "--"

    def _format_faction(self, status: RadarRuntimeStatus) -> str:
        if status.state != "running":
            return "待机"
        if status.faction == "red":
            return "红方"
        if status.faction == "blue":
            return "蓝方"
        return "--"

    def _format_double_vulnerability_status(self, status: RadarRuntimeStatus) -> str:
        if status.state != "running":
            return "待机"
        return "已触发" if status.is_double_vulnerability else "未触发"

    def _format_double_vulnerability_count(self, status: RadarRuntimeStatus) -> str:
        if status.state != "running":
            return "待机"
        return (
            f"{status.used_double_vulnerability_count}/"
            f"{status.total_double_vulnerability_count}"
        )

    def _format_countermeasure_success_count(self, status: RadarRuntimeStatus) -> str:
        if status.state != "running":
            return "待机"
        if status.countermeasure_success_count is None:
            return "--"
        return str(status.countermeasure_success_count)

    def _format_main_camera_status(self, status: RadarRuntimeStatus) -> str:
        if status.state == "running":
            return "在线"
        if status.state == "starting":
            return "连接中"
        if status.state == "error":
            return "异常"
        return "待机"

    def _format_sub_camera_status(self, status: RadarRuntimeStatus) -> str:
        if self.runtime_cfg.use_video:
            return "关闭"
        if status.state == "running":
            return "在线"
        if status.state == "starting":
            return "连接中"
        if status.state == "error":
            return "异常"
        return "待机"


    @staticmethod
    def _set_optional_label_text(label: QLabel, text: str) -> None:
        label.setText(text)
        label.setVisible(bool(text))

    def _update_field_map_panel(self, status: RadarRuntimeStatus) -> None:
        # status.map_targets 来自 MainEventLoop 对 tracker 输出的整理结果。
        if self.field_map_base_img is None:
            return

        map_frame = draw_targets_on_map(
            self.field_map_base_img,
            status.map_targets,
            self.map_class_names,
            status.faction or self.runtime_cfg.faction,
        )
        pixmap = self._frame_to_pixmap(map_frame)
        if pixmap is not None:
            self.field_map.set_panel_pixmap(pixmap)

    def _update_tracking_panel(self, status: RadarRuntimeStatus) -> None:
        # Tracking 面板优先显示主线程返回的可视化图像；没有帧时保持空白。
        if status.state == "running":
            if not status.main_camera_available:
                self.tracking_label.clear_frame()
                self._set_optional_label_text(self.tracking_meta, "主相机不可用，视觉检测未启动")
                return
            frame = self.runtime_controller.get_latest_track_frame()
            if frame is not None:
                pixmap = self._frame_to_pixmap(frame)
                self.tracking_label.set_frame_pixmap(pixmap)

            
            self._set_optional_label_text(
                self.tracking_meta,
                f"推理帧率: {status.inference_fps:.2f}"
            )
            return

        self.tracking_label.clear_frame()
        self._set_optional_label_text(self.tracking_meta, "")

    def _update_sub_camera_panel(self, status: RadarRuntimeStatus) -> None:
        if status.state != "running":
            self.sub_camera_label.clear_frame()
            self._set_optional_label_text(self.sub_camera_meta, "")
            return

        if not status.sub_camera_available:
            self.sub_camera_label.clear_frame()
            text = "副相机关闭" if self.runtime_cfg.use_video else "副相机不可用"
            self._set_optional_label_text(self.sub_camera_meta, text)
            return

        frame = self.runtime_controller.get_latest_sub_vis_frame()
        if frame is None:
            self.sub_camera_label.clear_frame()
            self._set_optional_label_text(self.sub_camera_meta, "")
            return

        pixmap = self._frame_to_pixmap(frame)
        if pixmap is not None:
            self.sub_camera_label.set_frame_pixmap(pixmap)
            self._set_optional_label_text(self.sub_camera_meta, "")

    def _update_demod_info_panel(self, status: RadarRuntimeStatus) -> None:
        if status.state != "running":
            self.info_panel.set_lines(())
            self.jam_panel.set_lines(())
            return

        self.info_panel.set_lines(status.demod_info_lines)
        self.jam_panel.set_lines(status.demod_jam_lines)

    @staticmethod
    def _frame_to_pixmap(frame: np.ndarray) -> QPixmap | None:
        # 复制一份 Qt 自己管理的数据，避免 numpy/OpenCV 底层缓冲区失效。
        if np is None:
            return None
        if frame is None or frame.size == 0:
            return None

        if frame.ndim == 2:
            image = QImage(
                frame.data,
                frame.shape[1],
                frame.shape[0],
                frame.strides[0],
                QImage.Format_Grayscale8,
            )
            return QPixmap.fromImage(image.copy())

        if frame.ndim == 3 and frame.shape[2] == 3:
            rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
            image = QImage(
                rgb_frame.data,
                rgb_frame.shape[1],
                rgb_frame.shape[0],
                rgb_frame.strides[0],
                QImage.Format_RGB888,
            )
            return QPixmap.fromImage(image.copy())

        if frame.ndim == 3 and frame.shape[2] == 4:
            rgba_frame = np.ascontiguousarray(frame[:, :, [2, 1, 0, 3]])
            image = QImage(
                rgba_frame.data,
                rgba_frame.shape[1],
                rgba_frame.shape[0],
                rgba_frame.strides[0],
                QImage.Format_RGBA8888,
            )
            return QPixmap.fromImage(image.copy())

        return None

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.status_timer.stop()
        self.image_timer.stop()
        self.runtime_controller.stop()
        super().closeEvent(event)

    def _tick_status(self) -> None:
        # 低频状态轮询负责按钮、状态字和地图，不承担图像搬运。
        status = self.runtime_controller.get_status()
        self._latest_runtime_status = status
        self._refresh_ui_by_status(status)
        self._update_demod_info_panel(status)
        self._poll_manual_break_key_result(status)
        self._refresh_console_log(status)

    def _tick_image(self) -> None:
        # 高频图像轮询只处理主/副相机画面，减少状态刷新开销。
        status = self._latest_runtime_status
        self._update_tracking_panel(status)
        self._update_sub_camera_panel(status)


def run(
    argv: Sequence[str] | None = None,
    runtime_options: RadarRuntimeOptions | None = None
):
    # UI 主入口：准备 Qt 环境、创建窗口并进入事件循环。
    prepare_qt_plugin_path()
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    qt_argv = list(argv) if argv is not None else sys.argv
    app = QApplication.instance() or QApplication(qt_argv)
    window = MainWindow(
        runtime_options=runtime_options,
    )
    window.show()
    return app.exec_()


if __name__ == "__main__":
    runtime_options = parse_runtime_options(sys.argv[1:])
    run(argv=[sys.argv[0]], runtime_options=runtime_options)
    sys.exit()
