"""
数据库模型初始化文件
导入所有模型以便SQLAlchemy识别和创建表
"""
from backend.database.models.user import User
from backend.database.models.model import Model
from backend.database.models.segmentation import SegmentationRecord
from backend.database.models.augmentation import AugmentationRecord
from backend.database.models.augmentation_result import AugmentationResult
from backend.database.models.dataset import Dataset
from backend.database.models.dataset_image import DatasetImage
from backend.database.models.log import OperationLog

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
