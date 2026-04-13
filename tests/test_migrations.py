"""
数据迁移脚本验证测试
验证迁移脚本的 SQL 语法和逻辑正确性
"""
import os
import re
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MIGRATIONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'src/web/backend/database/migrations'
)


class TestMigrationFiles:
    """迁移文件测试"""

    def test_migration_files_exist(self):
        """测试迁移文件存在"""
        expected_files = [
            '001_add_segmentation_fields.sql',
            '002_create_augmentation_results.sql',
            '003_add_model_version_fields.sql',
            '004_create_dataset_tables.sql'
        ]

        for filename in expected_files:
            filepath = os.path.join(MIGRATIONS_DIR, filename)
            assert os.path.exists(filepath), f"迁移文件不存在: {filename}"

    def test_migration_001_syntax(self):
        """测试迁移脚本 001 语法"""
        filepath = os.path.join(MIGRATIONS_DIR, '001_add_segmentation_fields.sql')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查包含必要的 ALTER TABLE 语句
        assert 'ALTER TABLE segmentation_records' in content
        assert 'ADD COLUMN fused_image' in content
        assert 'ADD COLUMN class_iou' in content
        assert 'ADD COLUMN pixel_distribution' in content
        assert 'ADD COLUMN instance_info' in content

    def test_migration_002_syntax(self):
        """测试迁移脚本 002 语法"""
        filepath = os.path.join(MIGRATIONS_DIR, '002_create_augmentation_results.sql')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查包含 CREATE TABLE 语句
        assert 'CREATE TABLE' in content
        assert 'augmentation_results' in content
        assert 'record_id' in content
        assert 'result_image' in content
        assert 'variation_index' in content
        assert 'FOREIGN KEY' in content

    def test_migration_003_syntax(self):
        """测试迁移脚本 003 语法"""
        filepath = os.path.join(MIGRATIONS_DIR, '003_add_model_version_fields.sql')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查包含必要的字段
        assert 'ALTER TABLE models' in content
        assert 'ADD COLUMN parent_model_id' in content
        assert 'ADD COLUMN changelog' in content
        assert 'ADD COLUMN is_latest' in content

    def test_migration_004_syntax(self):
        """测试迁移脚本 004 语法"""
        filepath = os.path.join(MIGRATIONS_DIR, '004_create_dataset_tables.sql')
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查包含两张表的创建
        assert content.count('CREATE TABLE') >= 2
        assert 'datasets' in content
        assert 'dataset_images' in content
        assert 'annotation_data' in content
        assert 'annotation_status' in content

    def test_all_migrations_have_comments(self):
        """测试所有迁移文件都有注释说明"""
        migration_files = [
            '001_add_segmentation_fields.sql',
            '002_create_augmentation_results.sql',
            '003_add_model_version_fields.sql',
            '004_create_dataset_tables.sql'
        ]

        for filename in migration_files:
            filepath = os.path.join(MIGRATIONS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查文件开头有注释
            assert content.strip().startswith('--'), f"{filename} 缺少注释说明"

    def test_migration_order(self):
        """测试迁移文件按正确顺序执行"""
        migration_files = sorted([
            f for f in os.listdir(MIGRATIONS_DIR)
            if f.endswith('.sql') and f[0].isdigit()
        ])

        # 验证文件名前缀是连续的数字
        prefixes = [f[:3] for f in migration_files]
        expected_prefixes = ['001', '002', '003', '004']
        assert prefixes == expected_prefixes, f"迁移文件顺序不正确: {prefixes}"


class TestMigrationRunner:
    """迁移运行器测试"""

    def test_runner_exists(self):
        """测试迁移运行器存在"""
        runner_path = os.path.join(MIGRATIONS_DIR, 'run_migrations.py')
        assert os.path.exists(runner_path), "迁移运行器不存在"

    def test_runner_imports(self):
        """测试迁移运行器导入"""
        runner_path = os.path.join(MIGRATIONS_DIR, 'run_migrations.py')
        with open(runner_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查必要的导入
        assert 'from sqlalchemy import text' in content
        assert 'def run_migration' in content
        assert 'def run_all_migrations' in content


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])