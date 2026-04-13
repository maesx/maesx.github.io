"""
数据库配置管理模块
支持环境变量和配置文件的灵活配置
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class MySQLConfig:
    """MySQL数据库配置"""
    # 基础配置
    host: str = "localhost"
    port: int = 3306
    database: str = "image_segment_platform"
    user: str = "root"
    password: str = ""
    charset: str = "utf8mb4"
    
    # 连接池配置
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    pool_timeout: int = 30
    
    # Echo SQL语句（调试用）
    echo: bool = False
    
    @property
    def database_url(self) -> str:
        """生成数据库连接URL"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )
    
    @classmethod
    def from_env(cls) -> 'MySQLConfig':
        """从环境变量加载配置"""
        return cls(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            database=os.getenv('MYSQL_DATABASE', 'image_segment_platform'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            charset=os.getenv('MYSQL_CHARSET', 'utf8mb4'),
            pool_size=int(os.getenv('MYSQL_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('MYSQL_MAX_OVERFLOW', '20')),
            pool_recycle=int(os.getenv('MYSQL_POOL_RECYCLE', '3600')),
            pool_timeout=int(os.getenv('MYSQL_POOL_TIMEOUT', '30')),
            echo=os.getenv('MYSQL_ECHO', 'false').lower() == 'true'
        )


class DatabaseConfig:
    """数据库配置管理器"""
    
    def __init__(self, use_mysql: bool = False, mysql_config: Optional[MySQLConfig] = None):
        """
        初始化数据库配置
        
        Args:
            use_mysql: 是否使用MySQL数据库
            mysql_config: MySQL配置对象，如果为None则从环境变量加载
        """
        self.use_mysql = use_mysql
        self.mysql_config = mysql_config or MySQLConfig.from_env()
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量加载所有配置"""
        use_mysql = os.getenv('USE_MYSQL', 'false').lower() == 'true'
        return cls(use_mysql=use_mysql)
    
    def get_database_url(self) -> Optional[str]:
        """获取数据库连接URL"""
        if self.use_mysql:
            return self.mysql_config.database_url
        return None


# 全局配置实例
# 默认不启用MySQL，需要通过环境变量USE_MYSQL=true启用
db_config = DatabaseConfig.from_env()
