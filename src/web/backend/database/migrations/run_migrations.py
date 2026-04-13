"""
数据库迁移脚本运行器
用于执行 SQL 迁移文件
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from sqlalchemy import text
from src.web.backend.database.session import get_engine, init_database
from src.web.backend.config.database import db_config

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent


def get_migration_files():
    """获取所有迁移文件（按版本号排序）"""
    migration_files = []
    for f in MIGRATIONS_DIR.glob("*.sql"):
        if f.name.startswith(("001", "002", "003", "004")):
            migration_files.append(f)
    return sorted(migration_files)


def run_migration(migration_file: Path):
    """执行单个迁移文件"""
    logger.info(f"执行迁移: {migration_file.name}")

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    engine = get_engine()
    if engine is None:
        logger.error("数据库引擎未初始化，请确保 USE_MYSQL=true")
        return False

    # 分割 SQL 语句（简单分割，以分号结尾）
    statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        # 跳过注释行
        stripped = line.strip()
        if stripped.startswith('--') or stripped.startswith('/*'):
            continue

        current_statement.append(line)

        # 如果行以分号结尾，表示语句结束
        if stripped.endswith(';'):
            statements.append('\n'.join(current_statement))
            current_statement = []

    # 执行每个语句
    with engine.connect() as conn:
        for statement in statements:
            statement = statement.strip()
            if not statement or statement == ';':
                continue

            try:
                conn.execute(text(statement))
                conn.commit()
                logger.debug(f"执行成功: {statement[:50]}...")
            except Exception as e:
                # 某些语句可能因为字段已存在而失败，这是可以接受的
                if 'Duplicate column' in str(e) or 'already exists' in str(e):
                    logger.warning(f"跳过（已存在）: {statement[:50]}...")
                else:
                    logger.error(f"执行失败: {statement[:50]}...")
                    logger.error(f"错误: {e}")
                    raise

    logger.info(f"迁移完成: {migration_file.name}")
    return True


def run_all_migrations():
    """执行所有迁移"""
    if not db_config.use_mysql:
        logger.error("MySQL 数据库未启用，请设置 USE_MYSQL=true")
        return False

    logger.info("开始执行数据库迁移...")

    # 初始化数据库连接
    init_database()

    migration_files = get_migration_files()
    logger.info(f"发现 {len(migration_files)} 个迁移文件")

    for migration_file in migration_files:
        try:
            run_migration(migration_file)
        except Exception as e:
            logger.error(f"迁移失败: {migration_file.name}")
            logger.error(f"错误: {e}")
            return False

    logger.info("所有迁移执行完成！")
    return True


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    success = run_all_migrations()
    sys.exit(0 if success else 1)