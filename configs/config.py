# 项目配置文件
import os

# 数据配置
DATA_CONFIG = {
    'data_dir': 'road_vehicle_pedestrian_det_datasets',
    'masks_dir': 'outputs/masks',
    'classes': ['car', 'truck', 'bus'],  # 要分割的车辆类别
    'num_classes': 4,  # 包括背景
}

# 模型配置
MODEL_CONFIG = {
    'encoder': 'vgg19',
    'pretrained': True,
    'deep_supervision': True,
}

# 训练配置 - CPU版本
TRAIN_CONFIG_CPU = {
    'batch_size': 4,  # CPU训练使用较小的批次
    'epochs': 50,
    'lr': 1e-4,
    'weight_decay': 1e-5,
    'img_size': [512, 512],
    'num_workers': 0,  # CPU训练时设置为0
    'use_gpu': False,
    'save_interval': 10,
}

# 训练配置 - GPU版本
TRAIN_CONFIG_GPU = {
    'batch_size': 16,  # GPU训练使用更大的批次
    'epochs': 100,
    'lr': 1e-4,
    'weight_decay': 1e-5,
    'img_size': [512, 512],
    'num_workers': 4,
    'use_gpu': True,
    'save_interval': 10,
}

# 推理配置
INFERENCE_CONFIG = {
    'model_path': 'outputs/checkpoints/best_model.pth',
    'output_dir': 'outputs/visualizations',
    'device': 'cpu',  # 'cpu' 或 'cuda'
}

# 类别颜色映射 (BGR格式)
CLASS_COLORS = {
    0: [0, 0, 0],        # 背景 - 黑色
    1: [0, 0, 255],      # car - 红色
    2: [0, 255, 0],      # truck - 绿色
    3: [255, 0, 0],      # bus - 蓝色
}

# 目录配置
OUTPUT_DIR = 'outputs'
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, 'checkpoints')
LOG_DIR = os.path.join(OUTPUT_DIR, 'logs')
VIS_DIR = os.path.join(OUTPUT_DIR, 'visualizations')
