"""
用户模型
存储用户账户信息和认证数据
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, Enum
from sqlalchemy.orm import relationship

from backend.database.session import Base


class User(Base):
    """用户模型类"""
    __tablename__ = 'users'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='用户ID')
    
    # 基本信息
    username = Column(String(50), unique=True, nullable=False, index=True, comment='用户名')
    email = Column(String(100), unique=True, index=True, comment='邮箱地址')
    
    # 认证信息
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    salt = Column(String(64), nullable=False, comment='密码盐值')
    
    # 个人信息
    nickname = Column(String(50), comment='用户昵称')
    avatar = Column(Text, comment='头像（Base64）')
    
    # 权限信息
    role = Column(
        Enum('user', 'admin', name='user_role_enum'),
        default='user',
        comment='用户角色'
    )
    status = Column(SmallInteger, default=1, comment='状态（1=正常, 0=禁用）')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    last_login_at = Column(DateTime, comment='最后登录时间')
    last_login_ip = Column(String(45), comment='最后登录IP')
    
    # 关联关系
    segmentation_records = relationship("SegmentationRecord", back_populates="user", cascade="all, delete-orphan")
    augmentation_records = relationship("AugmentationRecord", back_populates="user", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
