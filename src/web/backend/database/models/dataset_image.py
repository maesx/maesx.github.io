"""
数据集图像模型
存储数据集中的图像和标注信息
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.session import Base


class DatasetImage(Base):
    """数据集图像模型类"""
    __tablename__ = 'dataset_images'

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='图像ID')

    # 外键关联
    dataset_id = Column(BigInteger, ForeignKey('datasets.id', ondelete='CASCADE'), index=True, comment='数据集ID')
    uploaded_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), comment='上传用户ID')

    # 文件信息
    filename = Column(String(255), nullable=False, comment='文件名')
    file_path = Column(String(500), comment='文件存储路径')

    # 图像属性
    image_width = Column(Integer, comment='图像宽度')
    image_height = Column(Integer, comment='图像高度')
    image_format = Column(String(10), comment='图像格式')
    file_size = Column(BigInteger, comment='文件大小（字节）')

    # 标注信息
    annotation_data = Column(JSON, comment='标注数据（支持多种格式）')
    annotation_status = Column(
        Enum('pending', 'annotated', 'reviewed', name='annotation_status_enum'),
        default='pending',
        index=True,
        comment='标注状态'
    )

    # 时间信息
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关联关系
    dataset = relationship("Dataset", back_populates="images")
    uploader = relationship("User")

    def __repr__(self):
        return f"<DatasetImage(id={self.id}, filename='{self.filename}', status='{self.annotation_status}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'image_format': self.image_format,
            'file_size': self.file_size,
            'annotation_status': self.annotation_status,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }