"""
数据增强记录模型
存储数据增强历史记录和结果
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT as LongText
from sqlalchemy.orm import relationship

from backend.database.session import Base


class AugmentationRecord(Base):
    """数据增强记录模型类"""
    __tablename__ = 'augmentation_records'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='记录ID')
    
    # 外键关联
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=True, comment='用户ID（可为空）')
    
    # 图像数据（Base64编码）
    original_image = Column(LongText, nullable=False, comment='原图（Base64编码）')
    
    # 增强信息
    augmentation_type = Column(String(255), nullable=False, comment='增强类型（中文描述+参数）')
    methods_used = Column(JSON, nullable=False, comment='使用的增强方法列表')
    num_variations = Column(Integer, default=3, comment='生成变体数量')
    
    # 图像属性
    image_width = Column(Integer, comment='原图宽度')
    image_height = Column(Integer, comment='原图高度')
    image_format = Column(String(10), comment='图像格式')
    file_size = Column(BigInteger, comment='原文件大小（字节）')
    
    # 状态信息
    status = Column(SmallInteger, default=1, comment='状态（1=成功, 0=失败）')
    error_message = Column(Text, comment='错误信息')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.now, index=True, comment='创建时间')
    
    # 关联关系
    user = relationship("User", back_populates="augmentation_records")
    results = relationship("AugmentationResult", back_populates="augmentation_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AugmentationRecord(id={self.id}, user_id={self.user_id}, type='{self.augmentation_type}')>"
    
    def to_dict(self):
        """转换为字典（不含图片数据）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'augmentation_type': self.augmentation_type,
            'methods_used': self.methods_used,
            'num_variations': self.num_variations,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'image_format': self.image_format,
            'file_size': self.file_size,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
