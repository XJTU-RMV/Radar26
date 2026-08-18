from typing import List


# def solidwork2uwb(pos_3d: List[float], faction: str = "red") -> List[float]:
#     x, y, z = pos_3d
#     if (
#         faction == "red"
#         or faction == "unknown"
#     ):
#         pos_x = (-z + 14.0)
#         pos_y = (-x + 7.5)
#     elif faction == "blue":
#         x, y, z = pos_3d
#         pos_x = 28.0 - (-z + 14.0)
#         pos_y = 15.0 - (-x + 7.5)
#     return pos_x, pos_y

# 2026地图坐标系对应关系
def solidwork2uwb(pos_3d: List[float], faction: str = "red") -> List[float]:
    x, y, z = pos_3d
    if faction == "red":
        pos_x = (x + 14.0)
        pos_y = (y + 7.5)
    elif faction == "blue":
        pos_x = (-x + 14.0)
        pos_y = (-y + 7.5)
    return pos_x, pos_y

def position3dto2d_bathroom(pos_3d: List[float], faction: str = "red"):

    return pos_3d[0], pos_3d[1]

