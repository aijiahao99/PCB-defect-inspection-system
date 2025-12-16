import warnings
from ultralytics import YOLO
# 导入库
# 该文件用于训练模型 【环境未配置下，不可运行】

warnings.filterwarnings('ignore')
# model = YOLO("yolo11n.yaml").load("weights/yolo11n.pt")
# 构建结构并加载权重

model = YOLO("yolo11n.pt")
# 加载预训练模型 快一点

if __name__ == "__main__":
    train_results = model.train(
        data="new_data.yaml", # yaml文件
        epochs=100, # 训练次数
        imgsz=640, # 图片大小
        device="0", # GPU训练 device='cpu' - CPU训练
        batch=6, # 每次训练的样本数
        amp=True, # 开启混合精度训练
        name='exp', # 文件名称
        project='runs/train', #文件保存路径
        cache=True, #加快数据加载 也会加快模型训练
        workers=0,
        single_cls=False
    )
    # 模型的验证
    metrics = model.val()

