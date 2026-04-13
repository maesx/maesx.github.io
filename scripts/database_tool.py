"""
数据库管理工具
提供数据库备份、恢复、迁移等功能
"""
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

import logging
from src.web.backend.database.session import get_db, get_db_session
from src.web.backend.database.models import User, Model, SegmentationRecord, AugmentationRecord, OperationLog
from src.web.backend.config.database import db_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_data(output_dir: str = './backups'):
    """
    导出数据库数据到JSON文件
    
    Args:
        output_dir: 输出目录
    """
    if not db_config.use_mysql:
        logger.error("MySQL数据库未启用")
        return False
    
    try:
        # 创建输出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(output_dir, f'backup_{timestamp}')
        os.makedirs(backup_dir, exist_ok=True)
        
        with get_db_session() as db:
            if not db:
                logger.error("数据库连接失败")
                return False
            
            # 导出用户
            users = db.query(User).all()
            user_data = [user.to_dict() for user in users]
            save_json(user_data, os.path.join(backup_dir, 'users.json'))
            logger.info(f"✅ 导出用户数据: {len(users)} 条")
            
            # 导出模型
            models = db.query(Model).all()
            model_data = [model.to_dict() for model in models]
            save_json(model_data, os.path.join(backup_dir, 'models.json'))
            logger.info(f"✅ 导出模型数据: {len(models)} 条")
            
            # 导出分割记录（不含图片）
            segments = db.query(SegmentationRecord).all()
            segment_data = [seg.to_dict() for seg in segments]
            save_json(segment_data, os.path.join(backup_dir, 'segmentation_records.json'))
            logger.info(f"✅ 导出分割记录: {len(segments)} 条")
            
            # 导出增强记录（不含图片）
            augments = db.query(AugmentationRecord).all()
            augment_data = [aug.to_dict() for aug in augments]
            save_json(augment_data, os.path.join(backup_dir, 'augmentation_records.json'))
            logger.info(f"✅ 导出增强记录: {len(augments)} 条")
            
            # 导出操作日志
            logs = db.query(OperationLog).all()
            log_data = [log.to_dict() for log in logs]
            save_json(log_data, os.path.join(backup_dir, 'operation_logs.json'))
            logger.info(f"✅ 导出操作日志: {len(logs)} 条")
        
        logger.info(f"✅ 数据导出完成: {backup_dir}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据导出失败: {e}")
        return False


def import_data(input_file: str):
    """
    从JSON文件导入数据
    
    Args:
        input_file: JSON文件路径
    """
    if not db_config.use_mysql:
        logger.error("MySQL数据库未启用")
        return False
    
    logger.warning("⚠️  数据导入功能尚未实现，敬请期待")
    return False


def save_json(data: list, file_path: str):
    """保存数据到JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: str):
    """从JSON文件加载数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库管理工具')
    parser.add_argument('--export', action='store_true', help='导出数据')
    parser.add_argument('--import', dest='import_file', help='导入数据文件路径')
    parser.add_argument('--output', default='./backups', help='导出输出目录')
    
    args = parser.parse_args()
    
    if args.export:
        export_data(args.output)
    elif args.import_file:
        import_data(args.import_file)
    else:
        parser.print_help()
