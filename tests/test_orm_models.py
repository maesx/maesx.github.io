"""
ORM 模型单元测试
测试数据库模型的字段、关系和方法
"""
import pytest
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSegmentationRecord:
    """SegmentationRecord 模型测试"""

    def test_model_creation(self):
        """测试模型创建"""
        from src.web.backend.database.models.segmentation import SegmentationRecord

        record = SegmentationRecord(
            user_id=1,
            model_id=1,
            original_image='base64_original',
            result_image='base64_result',
            fused_image='base64_fused',
            segment_type='semantic',
            image_width=512,
            image_height=512,
            image_format='PNG',
            file_size=1024,
            processing_time=0.5,
            iou_score=0.85,
            accuracy=0.92,
            class_iou=[0.9, 0.8, 0.85, 0.75],
            pixel_distribution=[60.0, 20.0, 15.0, 5.0],
            instance_info=None,
            status=1
        )

        assert record.segment_type == 'semantic'
        assert record.image_width == 512
        assert record.iou_score == 0.85
        assert len(record.class_iou) == 4

    def test_to_dict_method(self):
        """测试 to_dict 方法"""
        from src.web.backend.database.models.segmentation import SegmentationRecord

        record = SegmentationRecord(
            user_id=1,
            model_id=1,
            original_image='base64_original',
            result_image='base64_result',
            segment_type='instance',
            class_iou=[0.9, 0.8],
            pixel_distribution=[50.0, 50.0],
            instance_info=[{'id': 1, 'class_name': 'car'}]
        )

        result = record.to_dict()
        assert 'original_image' not in result  # to_dict 不应包含图片数据
        assert 'class_iou' in result
        assert 'pixel_distribution' in result
        assert 'instance_info' in result


class TestAugmentationRecord:
    """AugmentationRecord 模型测试"""

    def test_model_creation(self):
        """测试模型创建"""
        from src.web.backend.database.models.augmentation import AugmentationRecord

        record = AugmentationRecord(
            user_id=None,  # 可为空
            original_image='base64_original',
            augmentation_type='水平翻转 + 亮度调整',
            methods_used=['horizontal_flip', 'brightness'],
            num_variations=3,
            image_width=640,
            image_height=480,
            status=1
        )

        assert record.user_id is None
        assert record.num_variations == 3
        assert 'horizontal_flip' in record.methods_used


class TestAugmentationResult:
    """AugmentationResult 模型测试"""

    def test_model_creation(self):
        """测试模型创建"""
        from src.web.backend.database.models.augmentation_result import AugmentationResult

        result = AugmentationResult(
            record_id=1,
            result_image='base64_result',
            variation_index=0,
            image_width=640,
            image_height=480,
            image_format='PNG'
        )

        assert result.record_id == 1
        assert result.variation_index == 0


class TestModel:
    """Model 模型测试"""

    def test_model_creation_with_version(self):
        """测试模型创建（包含版本信息）"""
        from src.web.backend.database.models.model import Model

        model = Model(
            model_name='unet_plusplus_v2',
            model_type='segmentation',
            version='1.1.0',
            parent_model_id=1,
            changelog='增加深度监督，提升IoU',
            description='U-Net++ 改进版',
            num_classes=4,
            is_active=1,
            is_default=0,
            is_latest=1
        )

        assert model.version == '1.1.0'
        assert model.parent_model_id == 1
        assert model.is_latest == 1

    def test_to_dict_includes_version_fields(self):
        """测试 to_dict 包含版本字段"""
        from src.web.backend.database.models.model import Model

        model = Model(
            model_name='test_model',
            model_type='segmentation',
            version='1.0.0',
            parent_model_id=None,
            changelog='初始版本',
            is_latest=1
        )

        result = model.to_dict()
        assert 'version' in result
        assert 'parent_model_id' in result
        assert 'changelog' in result
        assert 'is_latest' in result


class TestDataset:
    """Dataset 模型测试"""

    def test_model_creation(self):
        """测试模型创建"""
        from src.web.backend.database.models.dataset import Dataset

        dataset = Dataset(
            name='training_set_v1',
            description='训练数据集',
            dataset_type='training',
            image_count=100,
            annotation_count=80,
            total_size=1024000,
            is_public=0
        )

        assert dataset.name == 'training_set_v1'
        assert dataset.image_count == 100
        assert dataset.annotation_count == 80

    def test_default_values(self):
        """测试默认值"""
        from src.web.backend.database.models.dataset import Dataset

        dataset = Dataset(name='test_dataset')

        assert dataset.image_count == 0
        assert dataset.annotation_count == 0
        assert dataset.total_size == 0
        assert dataset.is_public == 0
        assert dataset.dataset_type == 'custom'


class TestDatasetImage:
    """DatasetImage 模型测试"""

    def test_model_creation(self):
        """测试模型创建"""
        from src.web.backend.database.models.dataset_image import DatasetImage

        image = DatasetImage(
            dataset_id=1,
            filename='image_001.jpg',
            file_path='/data/images/image_001.jpg',
            image_width=640,
            image_height=480,
            image_format='JPEG',
            file_size=102400,
            annotation_data={'boxes': [[10, 20, 100, 200]]},
            annotation_status='annotated',
            uploaded_by=1
        )

        assert image.filename == 'image_001.jpg'
        assert image.annotation_status == 'annotated'
        assert 'boxes' in image.annotation_data

    def test_default_annotation_status(self):
        """测试默认标注状态"""
        from src.web.backend.database.models.dataset_image import DatasetImage

        image = DatasetImage(
            dataset_id=1,
            filename='test.jpg'
        )

        assert image.annotation_status == 'pending'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])