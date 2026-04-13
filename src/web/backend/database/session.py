"""
数据库引擎和会话管理
基于SQLAlchemy实现的数据库连接池管理
"""
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
import logging

from src.web.backend.config.database import db_config

logger = logging.getLogger(__name__)

# 声明基类
Base = declarative_base()

# 全局引擎和会话工厂
_engine = None
_SessionLocal = None


def init_database():
    """
    初始化数据库引擎和连接池
    
    注意：仅在USE_MYSQL=true时才会初始化MySQL连接
    """
    global _engine, _SessionLocal
    
    if not db_config.use_mysql:
        logger.info("MySQL数据库未启用，使用内存存储")
        return
    
    if _engine is not None:
        logger.warning("数据库引擎已经初始化")
        return
    
    config = db_config.mysql_config
    
    try:
        # 创建数据库引擎
        _engine = create_engine(
            config.database_url,
            poolclass=QueuePool,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_recycle=config.pool_recycle,
            pool_timeout=config.pool_timeout,
            echo=config.echo,
            pool_pre_ping=True  # 连接前检查连接是否有效
        )
        
        # 创建会话工厂
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )
        
        # 注册连接池事件监听器
        @event.listens_for(_engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.debug(f"数据库连接创建: {connection_record}")
        
        @event.listens_for(_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug(f"连接从池中取出: {id(dbapi_connection)}")
        
        @event.listens_for(_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            logger.debug(f"连接归还到池中: {id(dbapi_connection)}")
        
        logger.info(
            f"MySQL数据库引擎初始化成功 - "
            f"Host: {config.host}:{config.port}, "
            f"Database: {config.database}, "
            f"Pool Size: {config.pool_size}"
        )
        
    except Exception as e:
        logger.error(f"数据库引擎初始化失败: {e}")
        raise


def get_engine():
    """获取数据库引擎"""
    if _engine is None:
        init_database()
    return _engine


def get_session_maker():
    """获取会话工厂"""
    if _SessionLocal is None:
        init_database()
    return _SessionLocal


def get_db() -> Optional[Session]:
    """
    获取数据库会话
    
    Returns:
        Session: 数据库会话对象，如果MySQL未启用则返回None
    """
    if not db_config.use_mysql:
        return None
    
    SessionLocal = get_session_maker()
    if SessionLocal is None:
        return None
    
    return SessionLocal()


@contextmanager
def get_db_session():
    """
    获取数据库会话的上下文管理器
    
    用法:
        with get_db_session() as session:
            user = session.query(User).first()
    
    Yields:
        Session: 数据库会话对象
    """
    session = get_db()
    try:
        yield session
        if session:
            session.commit()
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise
    finally:
        if session:
            session.close()


def close_database():
    """关闭数据库连接池"""
    global _engine, _SessionLocal
    
    if _engine:
        _engine.dispose()
        logger.info("数据库连接池已关闭")
    
    _engine = None
    _SessionLocal = None


def create_tables():
    """
    创建所有数据表
    
    注意：仅在USE_MYSQL=true时才会创建表
    """
    if not db_config.use_mysql:
        logger.info("MySQL数据库未启用，跳过表创建")
        return
    
    engine = get_engine()
    if engine:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")


def drop_tables():
    """
    删除所有数据表
    
    警告：此操作不可逆，仅用于开发和测试
    """
    if not db_config.use_mysql:
        logger.info("MySQL数据库未启用，跳过表删除")
        return
    
    engine = get_engine()
    if engine:
        Base.metadata.drop_all(bind=engine)
        logger.warning("所有数据库表已删除")


# 导出Base类供模型使用
__all__ = [
    'Base',
    'init_database',
    'get_db',
    'get_db_session',
    'close_database',
    'create_tables',
    'drop_tables'
]
