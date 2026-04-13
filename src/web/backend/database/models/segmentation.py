"""
图像分割记录模型
存储图像分割历史记录和结果
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, Float, SmallInteger, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.session import Base


class SegmentationRecord(Base):
    """图像分割记录模型类"""
    __tablename__ = 'segmentation_records'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='记录ID')
    
    # 外键关联
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), index=True, comment='用户ID')
    model_id = Column(BigInteger, ForeignKey('models.id', ondelete='SET NULL'), index=True, comment='模型ID')
    
    # 图像数据（Base64编码）
    original_image = Column(LongText, nullable=False, comment='原图（Base64编码）')
    result_image = Column(LongText, nullable=False, comment='分割结果图（Base64编码）')
    fused_image = Column(LongText, comment='融合图像（Base64编码）')
    
    # 分割参数
    segment_type = Column(
        Enum('semantic', 'instance', name='segment_type_enum'),
        nullable=False,
        comment='分割类型'
    )
    
    # 图像属性
    image_width = Column(Integer, comment='图像宽度')
    image_height = Column(Integer, comment='图像高度')
    image_format = Column(String(10), comment='图像格式（PNG/JPG等）')
    file_size = Column(BigInteger, comment='文件大小（字节）')
    
    # 处理结果
    processing_time = Column(Float, comment='处理耗时（秒）')
    iou_score = Column(Float, comment='IoU得分')
    accuracy = Column(Float, comment='准确率')
    class_iou = Column(JSON, comment='各类别IoU得分列表')
    pixel_distribution = Column(JSON, comment='各类别像素占比列表')
    instance_info = Column(JSON, comment='实例分割信息（实例数量、边界框等）')
    additional_metrics = Column(JSON, comment='其他评估指标')
    
    # 状态信息
    status = Column(SmallInteger, default=1, comment='状态（1=成功, 0=失败）')
    error_message = Column(Text, comment='错误信息')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.now, index=True, comment='创建时间')
    
    # 关联关系
    user = relationship("User", back_populates="segmentation_records")
    model = relationship("Model", back_populates="segmentation_records")
    
    def __repr__(self):
        return f"<SegmentationRecord(id={self.id}, user_id={self.user_id}, type='{self.segment_type}')>"
    
    def to_dict(self):
        """转换为字典（不含图片数据）"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'segment_type': self.segment_type,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'image_format': self.image_format,
            'file_size': self.file_size,
            'processing_time': self.processing_time,
            'iou_score': self.iou_score,
            'accuracy': self.accuracy,
            'class_iou': self.class_iou,
            'pixel_distribution': self.pixel_distribution,
            'instance_info': self.instance_info,
            'additional_metrics': self.additional_metrics,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 导入LongText类型
from sqlalchemy.dialects.mysql import LONGTEXT as LongText
