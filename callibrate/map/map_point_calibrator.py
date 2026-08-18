from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import yaml
from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "params.yaml"
DEFAULT_POINTS_PATH = ROOT_DIR / "config" / "map_point.yaml"
FIELD_X_RANGE_M = 28.0
FIELD_Y_RANGE_M = 15.0


@dataclass
class MapPoint:
    name: str
    faction: str
    center_x_m: float
    center_y_m: float
    radius_m: float


def resolve_repo_path(path_text: str | Path) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_map_path(config_path: Path) -> Path:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return resolve_repo_path(config["transform"]["map_path"])


def load_points(points_path: Path) -> list[MapPoint]:
    if not points_path.exists():
        return []
    with points_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    points = []
    point_items = data.get("points") or []
    if not isinstance(point_items, list):
        raise ValueError(f"{points_path} 中的 points 必须是列表。")
    for item in point_items:
        center = item["center"]
        points.append(
            MapPoint(
                name=str(item["name"]),
                faction=str(item["faction"]),
                center_x_m=float(center[0]),
                center_y_m=float(center[1]),
                radius_m=float(item["radius_m"]),
            )
        )
    return points


def save_points(points_path: Path, map_path: Path, points: list[MapPoint]) -> None:
    data = {
        "field": {
            "x_range_m": FIELD_X_RANGE_M,
            "y_range_m": FIELD_Y_RANGE_M,
            "map_path": str(map_path.relative_to(ROOT_DIR) if map_path.is_relative_to(ROOT_DIR) else map_path),
        },
        "points": [
            {
                "name": point.name,
                "faction": point.faction,
                "center": [
                    round(point.center_x_m, 4),
                    round(point.center_y_m, 4),
                ],
                "radius_m": round(point.radius_m, 4),
            }
            for point in points
        ],
    }
    points_path.parent.mkdir(parents=True, exist_ok=True)
    with points_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


def mirror_point_name(name: str) -> str:
    if name.startswith("R"):
        return "B" + name[1:]
    if name.startswith("B"):
        return "R" + name[1:]
    raise ValueError("标定点名称必须以 R 或 B 开头，才能生成中心对称点。")


def make_symmetric_points(name: str, center_x_m: float, center_y_m: float, radius_m: float) -> list[MapPoint]:
    faction = "red" if name.startswith("R") else "blue"
    mirror_name = mirror_point_name(name)
    mirror_faction = "blue" if faction == "red" else "red"
    return [
        MapPoint(name, faction, center_x_m, center_y_m, radius_m),
        MapPoint(
            mirror_name,
            mirror_faction,
            FIELD_X_RANGE_M - center_x_m,
            FIELD_Y_RANGE_M - center_y_m,
            radius_m,
        ),
    ]


def faction_from_name(name: str) -> str:
    if name.startswith("R"):
        return "red"
    if name.startswith("B"):
        return "blue"
    raise ValueError("标定点名称必须以 R 或 B 开头，才能判断所属阵营。")


class MapCanvas(QLabel):
    image_clicked = pyqtSignal(float, float)
    image_moved = pyqtSignal(float, float)

    def __init__(self, map_pixmap: QPixmap, points: list[MapPoint]) -> None:
        super().__init__()
        self._base_pixmap = map_pixmap
        self._points = list(points)
        self._zoom = 1.0
        self._pending_center_px: tuple[float, float] | None = None
        self._preview_px: tuple[float, float] | None = None
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setMouseTracking(True)
        self._redraw()

    def set_points(self, points: list[MapPoint]) -> None:
        self._points = list(points)
        self._redraw()

    def set_pending_center(self, center_px: tuple[float, float] | None) -> None:
        self._pending_center_px = center_px
        self._preview_px = None
        self._redraw()

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        old_zoom = self._zoom
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self._zoom = max(0.2, min(5.0, self._zoom * factor))
        if abs(old_zoom - self._zoom) > 1e-9:
            self._redraw()
        event.accept()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton:
            super().mousePressEvent(event)
            return
        image_pos = self._event_to_image_pos(event)
        if image_pos is None:
            return
        self.image_clicked.emit(image_pos[0], image_pos[1])

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        image_pos = self._event_to_image_pos(event)
        if image_pos is None:
            return
        self.image_moved.emit(image_pos[0], image_pos[1])
        if self._pending_center_px is not None:
            self._preview_px = image_pos
            self._redraw()

    def pixel_to_field(self, px: float, py: float) -> tuple[float, float]:
        width = self._base_pixmap.width()
        height = self._base_pixmap.height()
        x_m = px / max(1, width - 1) * FIELD_X_RANGE_M
        y_m = (1.0 - py / max(1, height - 1)) * FIELD_Y_RANGE_M
        return x_m, y_m

    def field_to_pixel(self, x_m: float, y_m: float) -> tuple[float, float]:
        width = self._base_pixmap.width()
        height = self._base_pixmap.height()
        px = x_m / FIELD_X_RANGE_M * (width - 1)
        py = (1.0 - y_m / FIELD_Y_RANGE_M) * (height - 1)
        return px, py

    def point_faction(self, px: float) -> str:
        return "red" if px < self._base_pixmap.width() / 2.0 else "blue"

    def _event_to_image_pos(self, event) -> tuple[float, float] | None:
        px = event.pos().x() / self._zoom
        py = event.pos().y() / self._zoom
        if px < 0 or py < 0 or px >= self._base_pixmap.width() or py >= self._base_pixmap.height():
            return None
        return px, py

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
        self._draw_team_regions(painter, scaled_width, scaled_height)
        for point in self._points:
            self._draw_map_point(painter, point)
        self._draw_pending_circle(painter)
        painter.end()
        self.setPixmap(canvas)
        self.resize(canvas.size())

    def _draw_team_regions(self, painter: QPainter, width: int, height: int) -> None:
        painter.fillRect(QRectF(0, 0, width / 2.0, height), QColor(255, 0, 0, 28))
        painter.fillRect(QRectF(width / 2.0, 0, width / 2.0, height), QColor(0, 80, 255, 28))
        pen = QPen(QColor(0, 0, 0, 130))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(int(width / 2.0), 0, int(width / 2.0), height)

    def _draw_map_point(self, painter: QPainter, point: MapPoint) -> None:
        px, py = self.field_to_pixel(point.center_x_m, point.center_y_m)
        center = QPointF(px * self._zoom, py * self._zoom)
        radius_x = point.radius_m / FIELD_X_RANGE_M * (self._base_pixmap.width() - 1) * self._zoom
        radius_y = point.radius_m / FIELD_Y_RANGE_M * (self._base_pixmap.height() - 1) * self._zoom

        circle_pen = QPen(QColor(30, 190, 50))
        circle_pen.setWidth(2)
        circle_pen.setStyle(Qt.DashLine)
        painter.setPen(circle_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius_x, radius_y)

        center_color = QColor(220, 0, 0) if point.faction == "red" else QColor(0, 70, 230)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(center_color)
        painter.drawEllipse(center, 6 * self._zoom, 6 * self._zoom)
        self._draw_label(painter, center.x() + 10 * self._zoom, center.y() - 10 * self._zoom, point.name)

    def _draw_pending_circle(self, painter: QPainter) -> None:
        if self._pending_center_px is None or self._preview_px is None:
            if self._pending_center_px is not None:
                cx, cy = self._pending_center_px
                center_color = QColor(220, 0, 0) if self.point_faction(cx) == "red" else QColor(0, 70, 230)
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                painter.setBrush(center_color)
                painter.drawEllipse(QPointF(cx * self._zoom, cy * self._zoom), 6 * self._zoom, 6 * self._zoom)
            return

        cx, cy = self._pending_center_px
        bx, by = self._preview_px
        center_x_m, center_y_m = self.pixel_to_field(cx, cy)
        border_x_m, border_y_m = self.pixel_to_field(bx, by)
        radius_m = math.hypot(border_x_m - center_x_m, border_y_m - center_y_m)
        radius_x = radius_m / FIELD_X_RANGE_M * (self._base_pixmap.width() - 1) * self._zoom
        radius_y = radius_m / FIELD_Y_RANGE_M * (self._base_pixmap.height() - 1) * self._zoom
        center = QPointF(cx * self._zoom, cy * self._zoom)

        painter.setPen(QPen(QColor(255, 210, 0), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius_x, radius_y)
        painter.drawLine(center, QPointF(bx * self._zoom, by * self._zoom))

        center_color = QColor(220, 0, 0) if self.point_faction(cx) == "red" else QColor(0, 70, 230)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(center_color)
        painter.drawEllipse(center, 6 * self._zoom, 6 * self._zoom)

    def _draw_label(self, painter: QPainter, x: float, y: float, text: str) -> None:
        font = QFont()
        font.setPointSize(max(8, int(round(10 * self._zoom))))
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_rect = metrics.boundingRect(text).adjusted(-5, -3, 5, 3)
        text_rect.moveTopLeft(QPointF(x, y).toPoint())
        painter.fillRect(text_rect, QColor(255, 255, 255, 210))
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(text_rect, Qt.AlignCenter, text)


class MapPointCalibrator(QMainWindow):
    def __init__(self, map_path: Path, points_path: Path) -> None:
        super().__init__()
        self.map_path = map_path
        self.points_path = points_path
        self.points = load_points(points_path)
        self.pending_center_px: tuple[float, float] | None = None
        self.is_calibrating = False

        map_pixmap = QPixmap(str(map_path))
        if map_pixmap.isNull():
            raise RuntimeError(f"地图加载失败: {map_path}")

        self.setWindowTitle("地图点标定")
        self.resize(1500, 900)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        self.canvas = MapCanvas(map_pixmap, self.points)
        self.canvas.image_clicked.connect(self._handle_map_clicked)
        self.canvas.image_moved.connect(self._handle_map_moved)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setWidget(self.canvas)
        root_layout.addWidget(scroll_area, 1)

        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(8)

        side_layout.addWidget(QLabel(f"地图: {map_path.name}"))
        side_layout.addWidget(QLabel(f"保存: {points_path.relative_to(ROOT_DIR)}"))

        side_layout.addWidget(QLabel("标定点名称"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如 R1_snipe_1")
        side_layout.addWidget(self.name_input)

        self.calibrate_button = QPushButton("标定地图点")
        self.calibrate_button.setCheckable(True)
        self.calibrate_button.clicked.connect(self._toggle_calibration)
        side_layout.addWidget(self.calibrate_button)

        self.cancel_button = QPushButton("取消当前标定")
        self.cancel_button.clicked.connect(self._cancel_calibration)
        side_layout.addWidget(self.cancel_button)

        self.status_label = QLabel("输入名称后点击“标定地图点”。滚轮可缩放地图。")
        self.status_label.setWordWrap(True)
        side_layout.addWidget(self.status_label)

        side_layout.addWidget(QLabel("已标定点"))
        self.point_list = QListWidget()
        side_layout.addWidget(self.point_list, 1)

        side_layout.addStretch(1)
        root_layout.addWidget(side_panel)
        self.setCentralWidget(root)
        self._refresh_point_list()

    def _toggle_calibration(self) -> None:
        if not self.calibrate_button.isChecked():
            self._cancel_calibration()
            return

        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "缺少名称", "请先输入标定点名称。")
            self.calibrate_button.setChecked(False)
            return
        if not name.startswith(("R", "B")):
            QMessageBox.warning(self, "名称错误", "标定点名称必须以 R 或 B 开头，例如 R1_snipe_1。")
            self.calibrate_button.setChecked(False)
            return

        self.is_calibrating = True
        self.pending_center_px = None
        self.canvas.set_pending_center(None)
        self.status_label.setText("请在地图上点击标定区域中心点。")

    def _cancel_calibration(self) -> None:
        self.is_calibrating = False
        self.pending_center_px = None
        self.calibrate_button.setChecked(False)
        self.canvas.set_pending_center(None)
        self.status_label.setText("当前标定已取消。")

    def _handle_map_moved(self, px: float, py: float) -> None:
        x_m, y_m = self.canvas.pixel_to_field(px, py)
        faction = self.canvas.point_faction(px)
        faction_text = "红方" if faction == "red" else "蓝方"
        if self.pending_center_px is None:
            self.status_label.setText(f"当前坐标: ({x_m:.2f}, {y_m:.2f}) m，{faction_text}区域。")

    def _handle_map_clicked(self, px: float, py: float) -> None:
        if not self.is_calibrating:
            return

        if self.pending_center_px is None:
            name = self.name_input.text().strip()
            expected_faction = faction_from_name(name)
            clicked_faction = self.canvas.point_faction(px)
            if clicked_faction != expected_faction:
                expected_text = "左半红方区域" if expected_faction == "red" else "右半蓝方区域"
                QMessageBox.warning(self, "区域不匹配", f"{name} 应标在{expected_text}。")
                self._cancel_calibration()
                return
            self.pending_center_px = (px, py)
            self.canvas.set_pending_center(self.pending_center_px)
            x_m, y_m = self.canvas.pixel_to_field(px, py)
            self.status_label.setText(f"中心点: ({x_m:.2f}, {y_m:.2f}) m。请点击圆周上的一个点确定半径。")
            return

        center_x_px, center_y_px = self.pending_center_px
        center_x_m, center_y_m = self.canvas.pixel_to_field(center_x_px, center_y_px)
        border_x_m, border_y_m = self.canvas.pixel_to_field(px, py)
        radius_m = math.hypot(border_x_m - center_x_m, border_y_m - center_y_m)
        name = self.name_input.text().strip()
        try:
            new_points = make_symmetric_points(name, center_x_m, center_y_m, radius_m)
        except ValueError as exc:
            QMessageBox.warning(self, "名称错误", str(exc))
            self._cancel_calibration()
            return

        new_names = {point.name for point in new_points}
        self.points = [point for point in self.points if point.name not in new_names]
        self.points.extend(new_points)
        save_points(self.points_path, self.map_path, self.points)

        self.canvas.set_points(self.points)
        self._refresh_point_list()
        self.pending_center_px = None
        self.is_calibrating = False
        self.calibrate_button.setChecked(False)
        self.canvas.set_pending_center(None)
        mirror_point = new_points[1]
        self.status_label.setText(
            f"已保存 {name} 和 {mirror_point.name}: "
            f"({center_x_m:.2f}, {center_y_m:.2f}) -> "
            f"({mirror_point.center_x_m:.2f}, {mirror_point.center_y_m:.2f}) m, "
            f"半径 {radius_m:.2f} m。"
        )

    def _refresh_point_list(self) -> None:
        self.point_list.clear()
        for point in self.points:
            faction_text = "红" if point.faction == "red" else "蓝"
            self.point_list.addItem(
                f"{point.name} [{faction_text}] "
                f"({point.center_x_m:.2f}, {point.center_y_m:.2f}) r={point.radius_m:.2f}m"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="地图圆形区域标定工具")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="params.yaml 路径")
    parser.add_argument("--map", default=None, help="地图图片路径；不填则读取 params.yaml 的 transform.map_path")
    parser.add_argument("--points", default=str(DEFAULT_POINTS_PATH), help="map_point.yaml 保存路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = resolve_repo_path(args.config)
    map_path = resolve_repo_path(args.map) if args.map is not None else load_map_path(config_path)
    points_path = resolve_repo_path(args.points)

    app = QApplication([])
    window = MapPointCalibrator(map_path, points_path)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
