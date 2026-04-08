"""
Flask应用配置
"""
import os


class Config:
    """应用配置"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    
    # 服务器配置
    HOST = os.environ.get('HOST') or '127.0.0.1'
    PORT = int(os.environ.get('PORT') or 5002)  # 改为 5002 避免冲突
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
    
    # 目录配置
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'outputs', 'uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, 'outputs', 'results')
    CHECKPOINT_FOLDER = os.path.join(BASE_DIR, 'outputs', 'checkpoints')
    
    # 模型配置
    MODEL_INPUT_SIZE = (512, 512)
    NUM_CLASSES = 4
    CLASS_NAMES = ['Background', 'Road', 'Vehicle', 'Pedestrian']
    CLASS_COLORS = [
        [0, 0, 0],        # 背景 - 黑色
        [128, 128, 128],  # 道路 - 灰色
        [243, 156, 18],   # 车辆 - 亮橙色 (RGB: #F39C12)
        [255, 0, 0]       # 行人 - 红色
    ]
    
    # YOLOv8配置
    YOLO_MODEL_SIZE = 'n'  # nano版本，可选: n, s, m, l, x
    YOLO_CONF_THRESHOLD = 0.25
    
    # 历史记录配置
    MAX_HISTORY_SIZE = 100  # 最多保存100条历史记录
    
    # GPU监控配置
    GPU_MONITOR_INTERVAL = 2  # 每2秒更新一次