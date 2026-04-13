"""
操作日志模型
记录关键数据变更操作日志
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.session import Base


class OperationLog(Base):
    """操作日志模型类"""
    __tablename__ = 'operation_logs'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    
    # 外键关联
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), index=True, comment='操作用户ID')
    
    # 操作信息
    operation_type = Column(String(50), nullable=False, index=True, comment='操作类型')
    resource_type = Column(String(50), nullable=False, comment='资源类型')
    resource_id = Column(BigInteger, comment='资源ID')
    operation_detail = Column(JSON, comment='操作详情')
    
    # 客户端信息
    ip_address = Column(String(45), comment='操作IP地址')
    user_agent = Column(String(255), comment='用户代理')
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.now, index=True, comment='操作时间')
    
    # 关联关系
    user = relationship("User", back_populates="operation_logs")
    
    def __repr__(self):
        return f"<OperationLog(id={self.id}, type='{self.operation_type}', resource='{self.resource_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'operation_type': self.operation_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'operation_detail': self.operation_detail,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
