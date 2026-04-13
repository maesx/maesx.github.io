"""
数据增强结果模型
存储数据增强生成的结果图片
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT as LongText
from sqlalchemy.orm import relationship

from backend.database.session import Base


class AugmentationResult(Base):
    """数据增强结果模型类"""
    __tablename__ = 'augmentation_results'

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='结果ID')

    # 外键关联
    record_id = Column(BigInteger, ForeignKey('augmentation_records.id', ondelete='CASCADE'), index=True, comment='增强记录ID')

    # 图像数据
    result_image = Column(LongText, nullable=False, comment='增强结果图片（Base64编码）')
    variation_index = Column(Integer, nullable=False, comment='变体序号（从0开始）')

    # 图像属性
    image_width = Column(Integer, comment='图像宽度')
    image_height = Column(Integer, comment='图像高度')
    image_format = Column(String(10), comment='图像格式')

    # 关联关系
    augmentation_record = relationship("AugmentationRecord", back_populates="results")

    def __repr__(self):
        return f"<AugmentationResult(id={self.id}, record_id={self.record_id}, index={self.variation_index})>"

    def to_dict(self):
        """转换为字典（不含图片数据）"""
        return {
            'id': self.id,
            'record_id': self.record_id,
            'variation_index': self.variation_index,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'image_format': self.image_format
        }