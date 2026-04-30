#!/usr/bin/env python3
"""
创建图像分割相关数据表
用于存储图像分割历史记录
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.backend.database.session import Base, init_database, create_tables, get_engine
from src.web.backend.database.models.segmentation import SegmentationRecord
from src.web.backend.database.models.user import User
from src.web.backend.database.models.model import Model


def create_segmentation_tables():
    """创建分割记录相关数据表"""
    print("=" * 80)
    print("开始创建数据库表...")
    print("=" * 80)
    
    try:
        # 初始化数据库
        init_database()
        
        # 创建所有表
        create_tables()
        
        print("\n✅ 数据库表创建成功!")
        print("\n创建的表:")
        print("  - users (用户表)")
        print("  - models (模型表)")
        print("  - segmentation_records (分割记录表)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 创建数据库表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_tables():
    """检查数据表是否存在"""
    print("\n" + "=" * 80)
    print("检查数据库表...")
    print("=" * 80)
    
    try:
        from sqlalchemy import inspect
        engine = get_engine()
        
        if engine is None:
            print("\n⚠️  数据库引擎未初始化，MySQL可能未启用")
            return False
        
        inspector = inspect(engine)
        
        # 获取所有表名
        table_names = inspector.get_table_names()
        
        print(f"\n数据库中的表 (共 {len(table_names)} 个):")
        for table in sorted(table_names):
            print(f"  - {table}")
        
        # 检查分割记录表是否存在
        if 'segmentation_records' in table_names:
            print("\n✅ segmentation_records 表已存在")
            
            # 获取表的列信息
            columns = inspector.get_columns('segmentation_records')
            print(f"\n  表结构 (共 {len(columns)} 列):")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f", 默认值: {col.get('default')}" if col.get('default') else ""
                print(f"    - {col['name']}: {col['type']} {nullable}{default}")
        else:
            print("\n❌ segmentation_records 表不存在，需要创建")
        
        return 'segmentation_records' in table_names
        
    except Exception as e:
        print(f"\n❌ 检查数据库表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("图像分割数据库表创建工具")
    print("=" * 80)
    
    # 检查是否配置了MySQL
    from src.web.backend.config.database import db_config
    
    if not db_config.use_mysql:
        print("\n⚠️  MySQL数据库未启用 (USE_MYSQL=false)")
        print("图像分割功能将使用内存存储")
        print("\n如需启用MySQL数据库，请:")
        print("  1. 创建 .env 文件")
        print("  2. 设置 USE_MYSQL=true")
        print("  3. 配置数据库连接信息")
        print("  4. 重新运行此脚本")
        return False
    
    # 先检查表是否存在
    tables_ok = check_tables()
    
    # 如果表不存在，创建表
    if not tables_ok:
        print("\n开始创建数据库表...")
        if create_segmentation_tables():
            # 再次检查确认
            print("\n" + "=" * 80)
            check_tables()
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
