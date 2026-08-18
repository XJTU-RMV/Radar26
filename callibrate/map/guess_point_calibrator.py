from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
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
DEFAULT_POINTS_PATH = ROOT_DIR / "config" / "guess_pts.yaml"
FIELD_X_RANGE_M = 28.0
FIELD_Y_RANGE_M = 15.0
ROBOT_NAMES = ("R1", "R2", "R3", "R4", "R7", "B1", "B2", "B3", "B4", "B7", "RA", "BA")


def resolve_repo_path(path_text: str | Path) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def load_map_path(config_path: Path) -> Path:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return resolve_repo_path(config["transform"]["map_path"])


def mirror_robot_name(robot_name: str) -> str:
    if robot_name.startswith("R"):
        return "B" + robot_name[1:]
    if robot_name.startswith("B"):
        return "R" + robot_name[1:]
    raise ValueError(f"无法生成 {robot_name} 的中心对称机器人名称。")


def mirror_point(point: list[float]) -> list[float]:
    return [
        round(FIELD_X_RANGE_M - float(point[0]), 4),
        round(FIELD_Y_RANGE_M - float(point[1]), 4),
    ]


def robot_color(robot_name: str) -> QColor:
    if robot_name.startswith("R"):
        return QColor(220, 0, 0)
    return QColor(0, 70, 230)


def load_guess_config(points_path: Path) -> dict:
    if not points_path.exists():
        return {"guess_points": {name: [] for name in ROBOT_NAMES}, "d_factor": 0.01, "cos_factor": 0.003}

    with points_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    guess_points = data.get("guess_points") or {}
    if not isinstance(guess_points, dict):
        raise ValueError(f"{points_path} 中的 guess_points 必须是字典。")

    for robot_name in ROBOT_NAMES:
        guess_points.setdefault(robot_name, [])
    data["guess_points"] = guess_points
    data.setdefault("d_factor", 0.01)
    data.setdefault("cos_factor", 0.003)
    return data


def save_guess_config(points_path: Path, config: dict) -> None:
    points_path.parent.mkdir(parents=True, exist_ok=True)
    with points_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, allow_unicode=True, sort_keys=False, default_flow_style=None)


class GuessPointCanvas(QLabel):
    image_clicked = pyqtSignal(float, float)
    image_moved = pyqtSignal(float, float)

    def __init__(self, map_pixmap: QPixmap, guess_points: dict[str, list[list[float]]], selected_robot: str) -> None:
        super().__init__()
        self._base_pixmap = map_pixmap
        self._guess_points = guess_points
        self._selected_robot = selected_robot
        self._zoom = 1.0
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setMouseTracking(True)
        self._redraw()

    def set_guess_points(self, guess_points: dict[str, list[list[float]]]) -> None:
        self._guess_points = guess_points
        self._redraw()

    def set_selected_robot(self, robot_name: str) -> None:
        self._selected_robot = robot_name
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
        for robot_name in ROBOT_NAMES:
            for index, point in enumerate(self._guess_points.get(robot_name, []), start=1):
                self._draw_guess_point(painter, robot_name, index, point)
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

    def _draw_guess_point(self, painter: QPainter, robot_name: str, index: int, point: list[float]) -> None:
        px, py = self.field_to_pixel(float(point[0]), float(point[1]))
        center = QPointF(px * self._zoom, py * self._zoom)
        is_selected = robot_name == self._selected_robot
        radius = (7 if is_selected else 4) * self._zoom
        pen_width = 3 if is_selected else 1

        painter.setPen(QPen(QColor(0, 0, 0), pen_width))
        painter.setBrush(robot_color(robot_name))
        painter.drawEllipse(center, radius, radius)

        if is_selected:
            self._draw_label(painter, center.x() + 9 * self._zoom, center.y() - 9 * self._zoom, f"{robot_name}-{index}")

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


class GuessPointCalibrator(QMainWindow):
    def __init__(self, map_path: Path, points_path: Path) -> None:
        super().__init__()
        self.map_path = map_path
        self.points_path = points_path
        self.config = load_guess_config(points_path)
        self.guess_points = self.config["guess_points"]

        map_pixmap = QPixmap(str(map_path))
        if map_pixmap.isNull():
            raise RuntimeError(f"地图加载失败: {map_path}")

        self.setWindowTitle("猜点标定")
        self.resize(1500, 900)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        self.robot_combo = QComboBox()
        self.robot_combo.addItems(ROBOT_NAMES)
        selected_robot = self.robot_combo.currentText()

        self.canvas = GuessPointCanvas(map_pixmap, self.guess_points, selected_robot)
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

        side_layout.addWidget(QLabel("机器人"))
        self.robot_combo.currentTextChanged.connect(self._handle_robot_changed)
        side_layout.addWidget(self.robot_combo)

        self.undo_button = QPushButton("删除最后一个点")
        self.undo_button.clicked.connect(self._delete_last_point)
        side_layout.addWidget(self.undo_button)

        self.clear_button = QPushButton("清空当前机器人")
        self.clear_button.clicked.connect(self._clear_current_robot)
        side_layout.addWidget(self.clear_button)

        self.status_label = QLabel("选择机器人后在地图上连续点击猜点。")
        self.status_label.setWordWrap(True)
        side_layout.addWidget(self.status_label)

        side_layout.addWidget(QLabel("当前机器人猜点"))
        self.point_list = QListWidget()
        side_layout.addWidget(self.point_list, 1)

        side_layout.addStretch(1)
        root_layout.addWidget(side_panel)
        self.setCentralWidget(root)
        self._refresh_point_list()

    def _handle_robot_changed(self, robot_name: str) -> None:
        self.canvas.set_selected_robot(robot_name)
        self._refresh_point_list()
        self.status_label.setText(f"当前机器人: {robot_name}。")

    def _handle_map_moved(self, px: float, py: float) -> None:
        x_m, y_m = self.canvas.pixel_to_field(px, py)
        self.status_label.setText(f"当前坐标: ({x_m:.2f}, {y_m:.2f}) m。")

    def _handle_map_clicked(self, px: float, py: float) -> None:
        robot_name = self.robot_combo.currentText()
        mirror_name = mirror_robot_name(robot_name)
        x_m, y_m = self.canvas.pixel_to_field(px, py)
        point = [round(x_m, 4), round(y_m, 4)]
        mirror = mirror_point(point)

        self.guess_points[robot_name].append(point)
        self.guess_points[mirror_name].append(mirror)
        save_guess_config(self.points_path, self.config)

        self.canvas.set_guess_points(self.guess_points)
        self._refresh_point_list()
        self.status_label.setText(
            f"已保存 {robot_name}: ({point[0]:.2f}, {point[1]:.2f})，"
            f"{mirror_name}: ({mirror[0]:.2f}, {mirror[1]:.2f})。"
        )

    def _delete_last_point(self) -> None:
        robot_name = self.robot_combo.currentText()
        mirror_name = mirror_robot_name(robot_name)
        if not self.guess_points[robot_name]:
            return

        self.guess_points[robot_name].pop()
        if self.guess_points[mirror_name]:
            self.guess_points[mirror_name].pop()
        save_guess_config(self.points_path, self.config)

        self.canvas.set_guess_points(self.guess_points)
        self._refresh_point_list()
        self.status_label.setText(f"已删除 {robot_name} 和 {mirror_name} 的最后一个猜点。")

    def _clear_current_robot(self) -> None:
        robot_name = self.robot_combo.currentText()
        mirror_name = mirror_robot_name(robot_name)
        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确认清空 {robot_name} 和 {mirror_name} 的全部猜点吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.guess_points[robot_name] = []
        self.guess_points[mirror_name] = []
        save_guess_config(self.points_path, self.config)

        self.canvas.set_guess_points(self.guess_points)
        self._refresh_point_list()
        self.status_label.setText(f"已清空 {robot_name} 和 {mirror_name} 的猜点。")

    def _refresh_point_list(self) -> None:
        robot_name = self.robot_combo.currentText()
        self.point_list.clear()
        for index, point in enumerate(self.guess_points.get(robot_name, []), start=1):
            self.point_list.addItem(f"{index}. ({float(point[0]):.2f}, {float(point[1]):.2f})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="猜点位置标定工具")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="params.yaml 路径")
    parser.add_argument("--map", default=None, help="地图图片路径；不填则读取 params.yaml 的 transform.map_path")
    parser.add_argument("--points", default=str(DEFAULT_POINTS_PATH), help="guess_pts.yaml 保存路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = resolve_repo_path(args.config)
    map_path = resolve_repo_path(args.map) if args.map is not None else load_map_path(config_path)
    points_path = resolve_repo_path(args.points)

    app = QApplication([])
    window = GuessPointCalibrator(map_path, points_path)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
