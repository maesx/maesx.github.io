"""
数据库初始化脚本
用于创建数据库和初始化基本数据
"""
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.web.backend.database.session import init_database, create_tables, get_db
from src.web.backend.database.models import User, Model
from src.web.backend.config.database import db_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_mysql_database():
    """初始化MySQL数据库"""
    if not db_config.use_mysql:
        logger.error("MySQL数据库未启用，请设置环境变量 USE_MYSQL=true")
        return False
    
    try:
        # 初始化数据库引擎
        logger.info("正在初始化数据库引擎...")
        init_database()
        
        # 创建所有数据表
        logger.info("正在创建数据表...")
        create_tables()
        logger.info("数据表创建成功")
        
        # 创建默认管理员账户
        logger.info("正在创建默认管理员账户...")
        create_default_admin()
        
        # 创建默认模型记录
        logger.info("正在创建默认模型记录...")
        create_default_models()
        
        logger.info("✅ MySQL数据库初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False


def create_default_admin():
    """创建默认管理员账户"""
    from hashlib import sha256
    import secrets
    
    db = get_db()
    if not db:
        logger.warning("数据库连接失败，跳过管理员账户创建")
        return
    
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == 'admin').first()
        if admin:
            logger.info("管理员账户已存在，跳过创建")
            return
        
        # 生成密码哈希
        password = 'admin123'  # 默认密码
        salt = secrets.token_hex(32)
        password_hash = sha256((password + salt).encode()).hexdigest()
        
        # 创建管理员
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=password_hash,
            salt=salt,
            nickname='系统管理员',
            role='admin',
            status=1
        )
        
        db.add(admin_user)
        db.commit()
        logger.info("✅ 默认管理员账户创建成功")
        logger.info("   用户名: admin")
        logger.info("   密码: admin123")
        logger.warning("⚠️  请及时修改默认密码！")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建管理员账户失败: {e}")
    finally:
        db.close()


def create_default_models():
    """创建默认模型记录"""
    db = get_db()
    if not db:
        logger.warning("数据库连接失败，跳过模型记录创建")
        return
    
    try:
        # 检查是否已存在模型
        model_count = db.query(Model).count()
        if model_count > 0:
            logger.info("模型记录已存在，跳过创建")
            return
        
        # 创建默认模型
        default_models = [
            {
                'model_name': 'unet_basic',
                'model_type': 'segmentation',
                'version': '1.0',
                'description': '基础U-Net分割模型',
                'input_size': '512x512',
                'num_classes': 2,
                'supported_types': {'semantic'},
                'is_active': 1,
                'is_default': 1
            },
            {
                'model_name': 'mask_rcnn',
                'model_type': 'segmentation',
                'version': '1.0',
                'description': 'Mask R-CNN实例分割模型',
                'input_size': '800x800',
                'num_classes': 80,
                'supported_types': {'instance'},
                'is_active': 1,
                'is_default': 0
            }
        ]
        
        for model_data in default_models:
            model = Model(**model_data)
            db.add(model)
        
        db.commit()
        logger.info("✅ 默认模型记录创建成功")
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建模型记录失败: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    success = init_mysql_database()
    sys.exit(0 if success else 1)
