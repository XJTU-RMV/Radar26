from collections import deque
from enum import Enum
from typing import Hashable, List
import numpy as np
from dataclasses import dataclass
try:
    from tracker.kalman import KalmanFilterBox, KalmanFilter2d
except ImportError:
    from kalman import KalmanFilterBox, KalmanFilter2d


@dataclass
class SingleDetectionResult:

    ## 0 - 14 for known classes, -1 for unknown
    class_id: int

    ## confidence score for armor detection
    class_conf: float

    ## armor bounding box in [x1, y1, x2, y2] format
    armor_box: List[float]

    ## car bounding box in [x1, y1, x2, y2] format
    car_box: List[float]

    ## Confidence score for thecar  detection
    car_conf: float

    ## 3D position in [x, y, z] format
    pos_3d: List[float]

    time_stamp: float

    bot_id: Hashable
    

# 追踪状态机
class State(Enum):
    INACTIVE = "inactive"  # 未激活
    TENTATIVE = "tentative"  # 暂定
    CONFIRMED = "confirmed"  # 确认
    LOST = "lost"  # 丢失


HIT_COUNT_THRESHOLD = 3
MISS_COUNT_THRESHOLD = 10

class BotIdTrack:
    """维护每个trajecotry的追踪状态"""
    def __init__(self, bot_id: Hashable, class_id: int, class_conf: float):
        self.class_id_queue = deque([], maxlen=30)
        self.class_conf_queue = deque([], maxlen=30)
        self.class_id_queue.append(class_id)
        self.class_conf_queue.append(class_conf)
        self.bot_id = bot_id
        self.lost_counter = 0
        self.updated = False
    
    def update(self, class_id: int, class_conf: float) -> None:
        self.class_id_queue.append(class_id)
        self.class_conf_queue.append(class_conf)
        
    def get_class_id_exponent_confidence(self, history_length: int = 10, tau: float = 0.5) -> np.ndarray:
        """
        获取class_id的指数分布，整合死亡class_id（10-14）到活机器人（0-9），
        无人机（15, 16）映射到10, 11，未知class_id（-1）均匀分配到活机器人。
        
        Args:
            history_length: 考虑的历史帧数（默认10）。
            tau: 指数衰减因子（默认0.5）。
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: 长度为 12 的数组，表示各 class_id 的置信度 and normalized distribution。
        """
        # 初始化置信度数组，长度为 12
        # 0-9: 地面机器人 (R1-R7, B1-B7)
        # 10: 红方无人机 (RA)
        # 11: 蓝方无人机 (BA)
        distribution = np.zeros(12, dtype=np.float32)
        
        # 获取最近history_length帧的class_id，限制为队列长度
        valid_length = min(history_length, len(self.class_id_queue), len(self.class_conf_queue))
        if valid_length == 0:
            return distribution, distribution
        
        # 计算每帧的权重，最近帧权重更高，使用指数衰减
        weights = np.array([np.exp(-tau * (valid_length - 1 - i)) for i in range(valid_length)])
        weights /= weights.sum()  # 归一化权重
        
        # 统计class_id的加权出现次数
        for i, (class_id, class_conf) in enumerate(zip(list(self.class_id_queue)[-valid_length:], list(self.class_conf_queue)[-valid_length:])):
            if 0 <= class_id <= 9:  # 活机器人
                distribution[class_id] += weights[i] * class_conf
            elif 10 <= class_id <= 14:  # 死亡机器人，映射到对应活机器人
                mapped_id_candidates = [class_id - 5, class_id - 10] 
                for mapped_id in mapped_id_candidates:
                    if 0 <= mapped_id <= 9:
                        distribution[mapped_id] += weights[i] * 0.8 * class_conf
            elif class_id == 15:  # 红方无人机
                distribution[10] += weights[i] * class_conf
            elif class_id == 16:  # 蓝方无人机
                distribution[11] += weights[i] * class_conf
            elif class_id == -1:  # 未知class_id，均匀分配到0-9
                distribution[:10] += weights[i] / 10.0 * class_conf
        
        confidence = distribution.copy()
        # 归一化分布
        if distribution.sum() > 0:
            distribution /= distribution.sum()
        
        return confidence, distribution
        
        
        
       

class TrackingState:
    """维护每个兵种的追踪状态"""

    def __init__(
        self,
        class_id: int,
        name: str,
        max_frames: int = 30,
        box_trajectories: List[List[float]] = None,
    ):
        """
        初始化追踪状态

        Args:
            class_id: 兵种ID（例如，R1为0，B1为5）
            name: 兵种名称（例如，R1，B1）
            max_frames: 最大历史帧数
            box_trajectories: 边界框历史 [x1, y1, x2, y2]
        """
        if class_id == 15 or class_id == 16:    #将无人机id映射到10和11, 防止后续数组越界
            self.class_id = class_id - 5
        else:
            self.class_id = class_id
        self.name = name

        self.state = State.INACTIVE # 追踪状态机
        self.is_active = False  # 替代状态机
        self.confidence = 0.0

        # 历史轨迹属性, 使用循环队列
        self.box_trajectories = deque(box_trajectories or [], maxlen=max_frames)
        self.class_id_trajectory = deque([], maxlen=max_frames)
        self.bot_id_trajectory = deque([], maxlen=max_frames)

        self.is_dead = False
        self.inactive_count = 0 # 目标处于非活跃状态累计时长
        self.miss_count = 0
        self.hit_count = 0
        self.bot_id = -1        
        
        self.kalman_filter = KalmanFilterBox()
        self.kalman_filter_2d: KalmanFilter2d = KalmanFilter2d(initial_pos=[0.0, 0.0], dt = 0.1) ## 10HZ

        self.car_box = [0.0, 0.0, 0.0, 0.0]  # 当前边界框 [x1, y1, x2, y2]
        self.pos_3d = [0.0, 0.0, 0.0]
        self.pos_2d_uwb_det = [0.0, 0.0]
        self.pos_2d_uwb = [0.0, 0.0]
        
        self.is_start_guess = False  # 是否开始预测点
        self.guess_point = [0.0, 0.0]  # 预测点 [x, y]

    def reset(self, xywh: List[float]) -> None:
        self.confidence = 0.0
        self.miss_count = 0
        self.hit_count = 0
        self.box_trajectories.clear()
        self.kalman_filter.reset(xywh)
    
