from ultralytics import YOLO


model = YOLO("weights/best.pt")  
model.export(
    format="engine",  # 导出为TensorRT engine格
    dynamic=False,     # 启用动态批大小
    imgsz=640, # 固定输入尺寸或范围
    half=True,
    device=0,
    int8=False,
    simplify=True
)
