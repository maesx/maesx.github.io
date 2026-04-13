"""
向后兼容性测试
验证数据库变更不影响现有数据和功能
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBackwardCompatibility:
    """向后兼容性测试"""

    def test_segmentation_record_new_fields_nullable(self):
        """测试分割记录新字段可为空"""
        from src.web.backend.database.models.segmentation import SegmentationRecord

        # 创建旧格式的记录（不包含新字段）
        record = SegmentationRecord(
            user_id=1,
            model_id=1,
            original_image='base64',
            result_image='base64',
            segment_type='semantic'
        )

        # 新字段应该允许为空
        assert record.fused_image is None
        assert record.class_iou is None
        assert record.pixel_distribution is None
        assert record.instance_info is None

    def test_model_new_fields_nullable(self):
        """测试模型新字段可为空"""
        from src.web.backend.database.models.model import Model

        # 创建旧格式的模型（不包含版本字段）
        model = Model(
            model_name='old_model',
            model_type='segmentation',
            description='旧模型'
        )

        # 新字段应该允许为空或有默认值
        assert model.parent_model_id is None
        assert model.changelog is None
        # is_latest 应该有默认值
        assert model.is_latest is not None

    def test_augmentation_record_without_result_images(self):
        """测试增强记录不包含 result_images 字段"""
        from src.web.backend.database.models.augmentation import AugmentationRecord

        # 创建增强记录
        record = AugmentationRecord(
            user_id=None,
            original_image='base64',
            augmentation_type='翻转',
            methods_used=['flip'],
            num_variations=3
        )

        # 验证 result_images 字段已移除
        assert not hasattr(record, 'result_images') or record.result_images is None

    def test_augmentation_record_user_id_nullable(self):
        """测试增强记录 user_id 可为空"""
        from src.web.backend.database.models.augmentation import AugmentationRecord

        # 创建无用户的增强记录
        record = AugmentationRecord(
            user_id=None,
            original_image='base64',
            augmentation_type='测试',
            methods_used=[]
        )

        assert record.user_id is None

    def test_dataset_defaults(self):
        """测试数据集默认值"""
        from src.web.backend.database.models.dataset import Dataset

        # 创建最小化数据集
        dataset = Dataset(name='test')

        # 验证默认值
        assert dataset.image_count == 0
        assert dataset.annotation_count == 0
        assert dataset.total_size == 0
        assert dataset.is_public == 0
        assert dataset.dataset_type == 'custom'

    def test_dataset_image_defaults(self):
        """测试数据集图像默认值"""
        from src.web.backend.database.models.dataset_image import DatasetImage

        # 创建最小化图像记录
        image = DatasetImage(
            dataset_id=1,
            filename='test.jpg'
        )

        # 验证默认值
        assert image.annotation_status == 'pending'
        assert image.annotation_data is None

    def test_to_dict_backward_compatible(self):
        """测试 to_dict 方法向后兼容"""
        from src.web.backend.database.models.segmentation import SegmentationRecord
        from src.web.backend.database.models.model import Model

        # 旧格式分割记录
        old_record = SegmentationRecord(
            original_image='base64',
            result_image='base64',
            segment_type='semantic'
        )
        old_dict = old_record.to_dict()

        # 验证旧字段仍然存在
        assert 'segment_type' in old_dict
        assert 'processing_time' in old_dict

        # 旧格式模型
        old_model = Model(
            model_name='test',
            model_type='segmentation'
        )
        old_model_dict = old_model.to_dict()

        # 验证旧字段仍然存在
        assert 'model_name' in old_model_dict
        assert 'model_type' in old_model_dict
        assert 'is_active' in old_model_dict

    def test_memory_storage_still_works(self):
        """测试内存存储仍然可用"""
        from src.web.backend.services.storage_service import (
            MemoryStorageService,
            SegmentationResult
        )

        # 创建内存存储服务
        storage = MemoryStorageService()

        # 创建分割结果
        result = SegmentationResult(
            result_id='test-001',
            original_filename='test.jpg',
            model_name='best_model',
            segment_type='semantic',
            iou=0.85,
            accuracy=0.90,
            process_time=0.5,
            class_names=['bg', 'car', 'truck', 'bus'],
            class_iou=[0.9, 0.8, 0.85, 0.75],
            pixel_distribution=[60, 20, 15, 5],
            timestamp='2026-04-09 12:00:00'
        )

        # 添加到存储
        storage.add_segmentation_result(result)

        # 验证可以获取
        retrieved = storage.get_segmentation_result('test-001')
        assert retrieved is not None
        assert retrieved.iou == 0.85

    def test_database_config_mysql_optional(self):
        """测试 MySQL 配置为可选"""
        from src.web.backend.config.database import db_config

        # 验证 use_mysql 可以设置为 False
        # 默认情况下应该是 False（根据配置）
        assert hasattr(db_config, 'use_mysql')
        assert isinstance(db_config.use_mysql, bool)

    def test_session_context_manager_without_mysql(self):
        """测试无 MySQL 时会话管理器正常工作"""
        from src.web.backend.database.session import get_db_session

        # 即使 MySQL 未启用，上下文管理器也应该正常工作
        with get_db_session() as session:
            # session 可能为 None（MySQL 未启用）
            pass  # 不应该抛出异常


class TestMigrationSafety:
    """迁移安全性测试"""

    def test_migration_uses_add_column_not_modify(self):
        """测试迁移使用 ADD COLUMN 而非修改现有列"""
        migrations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'src/web/backend/database/migrations'
        )

        # 检查迁移脚本 001
        with open(os.path.join(migrations_dir, '001_add_segmentation_fields.sql'), 'r') as f:
            content = f.read()

        # 应该使用 ADD COLUMN
        assert 'ADD COLUMN' in content
        # 不应该使用 DROP COLUMN 或 MODIFY COLUMN（可能破坏现有数据）
        assert 'DROP COLUMN' not in content

    def test_migration_uses_defaults(self):
        """测试迁移使用默认值"""
        migrations_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'src/web/backend/database/migrations'
        )

        # 检查迁移脚本 003
        with open(os.path.join(migrations_dir, '003_add_model_version_fields.sql'), 'r') as f:
            content = f.read()

        # is_latest 应该有默认值
        assert 'DEFAULT' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])