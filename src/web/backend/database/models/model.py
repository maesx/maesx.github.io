"""
模型管理模型
存储AI模型元数据和管理信息
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.session import Base


class Model(Base):
    """模型管理模型类"""
    __tablename__ = 'models'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='模型ID')
    
    # 基本信息
    model_name = Column(String(100), unique=True, nullable=False, index=True, comment='模型名称')
    model_type = Column(
        Enum('segmentation', 'classification', 'detection', name='model_type_enum'),
        nullable=False,
        comment='模型类型'
    )
    version = Column(String(20), comment='模型版本号（如"1.0.0"）')
    parent_model_id = Column(BigInteger, ForeignKey('models.id', ondelete='SET NULL'), comment='父模型ID（用于版本继承）')
    changelog = Column(Text, comment='版本变更日志')
    description = Column(Text, comment='模型描述')
    
    # 文件信息
    model_path = Column(String(255), comment='模型文件路径')
    model_size = Column(BigInteger, comment='模型文件大小（字节）')
    
    # 模型参数
    input_size = Column(String(20), comment='输入尺寸（如"512x512"）')
    num_classes = Column(Integer, comment='类别数量')
    supported_types = Column(JSON, comment='支持的分割类型列表')
    
    # 性能指标
    performance_metrics = Column(JSON, comment='性能指标')
    
    # 状态管理
    is_active = Column(SmallInteger, default=1, index=True, comment='是否启用')
    is_default = Column(SmallInteger, default=0, comment='是否默认模型')
    is_latest = Column(SmallInteger, default=1, index=True, comment='是否为最新版本')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    segmentation_records = relationship("SegmentationRecord", back_populates="model")
    
    def __repr__(self):
        return f"<Model(id={self.id}, model_name='{self.model_name}', type='{self.model_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_type': self.model_type,
            'version': self.version,
            'parent_model_id': self.parent_model_id,
            'changelog': self.changelog,
            'description': self.description,
            'model_path': self.model_path,
            'model_size': self.model_size,
            'input_size': self.input_size,
            'num_classes': self.num_classes,
            'supported_types': self.supported_types,
            'performance_metrics': self.performance_metrics,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'is_latest': self.is_latest,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
