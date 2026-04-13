"""
数据集模型
存储数据集元数据和管理信息
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, Enum
from sqlalchemy.orm import relationship

from src.web.backend.database.session import Base


class Dataset(Base):
    """数据集模型类"""
    __tablename__ = 'datasets'

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='数据集ID')

    # 基本信息
    name = Column(String(100), unique=True, nullable=False, index=True, comment='数据集名称')
    description = Column(Text, comment='数据集描述')
    dataset_type = Column(
        Enum('training', 'validation', 'test', 'custom', name='dataset_type_enum'),
        default='custom',
        comment='数据集类型'
    )

    # 统计信息
    image_count = Column(Integer, default=0, comment='图像数量')
    annotation_count = Column(Integer, default=0, comment='已标注数量')
    total_size = Column(BigInteger, default=0, comment='总大小（字节）')

    # 访问控制
    is_public = Column(SmallInteger, default=0, index=True, comment='是否公开（0=私密, 1=公开）')

    # 时间信息
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    images = relationship("DatasetImage", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', type='{self.dataset_type}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dataset_type': self.dataset_type,
            'image_count': self.image_count,
            'annotation_count': self.annotation_count,
            'total_size': self.total_size,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }