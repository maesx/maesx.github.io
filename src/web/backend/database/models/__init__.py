"""
数据库模型初始化文件
导入所有模型以便SQLAlchemy识别和创建表
"""
from src.web.backend.database.models.user import User
from src.web.backend.database.models.model import Model
from src.web.backend.database.models.segmentation import SegmentationRecord
from src.web.backend.database.models.augmentation import AugmentationRecord
from src.web.backend.database.models.augmentation_result import AugmentationResult
from src.web.backend.database.models.dataset import Dataset
from src.web.backend.database.models.dataset_image import DatasetImage
from src.web.backend.database.models.log import OperationLog

__all__ = [
    'User',
    'Model',
    'SegmentationRecord',
    'AugmentationRecord',
    'AugmentationResult',
    'Dataset',
    'DatasetImage',
    'OperationLog'
]
