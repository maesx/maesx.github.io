"""
CRUD 操作测试
测试新表结构的增删改查操作
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSegmentationRecordCRUD:
    """SegmentationRecord CRUD 测试"""

    def test_create_segmentation_record(self):
        """测试创建分割记录"""
        from src.web.backend.database.models.segmentation import SegmentationRecord

        record = SegmentationRecord(
            user_id=1,
            model_id=1,
            original_image='base64_data',
            result_image='base64_result',
            fused_image='base64_fused',
            segment_type='semantic',
            class_iou=[0.9, 0.8, 0.85, 0.75],
            pixel_distribution=[60.0, 20.0, 15.0, 5.0],
            instance_info=None
        )

        # 验证字段设置正确
        assert record.fused_image == 'base64_fused'
        assert record.class_iou == [0.9, 0.8, 0.85, 0.75]
        assert record.pixel_distribution == [60.0, 20.0, 15.0, 5.0]

    def test_update_segmentation_record(self):
        """测试更新分割记录"""
        from src.web.backend.database.models.segmentation import SegmentationRecord

        record = SegmentationRecord(
            original_image='base64',
            result_image='base64',
            segment_type='semantic'
        )

        # 更新字段
        record.class_iou = [0.95, 0.85, 0.90, 0.80]
        record.pixel_distribution = [55.0, 25.0, 15.0, 5.0]
        record.instance_info = [{'id': 1, 'class_name': 'car'}]

        assert record.class_iou[0] == 0.95
        assert len(record.instance_info) == 1


class TestAugmentationResultCRUD:
    """AugmentationResult CRUD 测试"""

    def test_create_augmentation_result(self):
        """测试创建增强结果"""
        from src.web.backend.database.models.augmentation_result import AugmentationResult

        result = AugmentationResult(
            record_id=1,
            result_image='base64_image',
            variation_index=0,
            image_width=640,
            image_height=480
        )

        assert result.record_id == 1
        assert result.variation_index == 0

    def test_multiple_results_for_one_record(self):
        """测试一个记录对应多个结果"""
        from src.web.backend.database.models.augmentation_result import AugmentationResult

        results = []
        for i in range(3):
            result = AugmentationResult(
                record_id=1,
                result_image=f'base64_image_{i}',
                variation_index=i
            )
            results.append(result)

        assert len(results) == 3
        assert results[0].variation_index == 0
        assert results[1].variation_index == 1
        assert results[2].variation_index == 2


class TestModelVersionCRUD:
    """Model 版本管理 CRUD 测试"""

    def test_create_model_with_version(self):
        """测试创建带版本的模型"""
        from src.web.backend.database.models.model import Model

        model = Model(
            model_name='unet_plusplus',
            model_type='segmentation',
            version='1.0.0',
            is_latest=1
        )

        assert model.version == '1.0.0'
        assert model.is_latest == 1

    def test_create_new_version(self):
        """测试创建新版本"""
        from src.web.backend.database.models.model import Model

        # 父模型
        parent = Model(
            model_name='unet_plusplus',
            model_type='segmentation',
            version='1.0.0',
            is_latest=0  # 不再是最新
        )

        # 新版本
        new_version = Model(
            model_name='unet_plusplus',
            model_type='segmentation',
            version='1.1.0',
            parent_model_id=1,  # 引用父模型
            changelog='增加深度监督',
            is_latest=1
        )

        assert new_version.version == '1.1.0'
        assert new_version.parent_model_id == 1
        assert new_version.is_latest == 1


class TestDatasetCRUD:
    """Dataset CRUD 测试"""

    def test_create_dataset(self):
        """测试创建数据集"""
        from src.web.backend.database.models.dataset import Dataset

        dataset = Dataset(
            name='training_set',
            description='训练数据集',
            dataset_type='training',
            image_count=0,
            annotation_count=0
        )

        assert dataset.name == 'training_set'
        assert dataset.image_count == 0

    def test_update_dataset_stats(self):
        """测试更新数据集统计"""
        from src.web.backend.database.models.dataset import Dataset

        dataset = Dataset(name='test')

        # 模拟添加图片
        dataset.image_count = 10
        dataset.annotation_count = 5
        dataset.total_size = 1024000

        assert dataset.image_count == 10
        assert dataset.annotation_count == 5


class TestDatasetImageCRUD:
    """DatasetImage CRUD 测试"""

    def test_create_dataset_image(self):
        """测试创建数据集图像"""
        from src.web.backend.database.models.dataset_image import DatasetImage

        image = DatasetImage(
            dataset_id=1,
            filename='image_001.jpg',
            image_width=640,
            image_height=480,
            annotation_status='pending'
        )

        assert image.dataset_id == 1
        assert image.annotation_status == 'pending'

    def test_update_annotation(self):
        """测试更新标注"""
        from src.web.backend.database.models.dataset_image import DatasetImage

        image = DatasetImage(
            dataset_id=1,
            filename='test.jpg',
            annotation_status='pending'
        )

        # 添加标注
        image.annotation_data = {
            'boxes': [[10, 20, 100, 200]],
            'labels': ['car']
        }
        image.annotation_status = 'annotated'

        assert image.annotation_status == 'annotated'
        assert len(image.annotation_data['boxes']) == 1


class TestRelationships:
    """关系测试"""

    def test_augmentation_record_results_relationship(self):
        """测试增强记录与结果的关系"""
        from src.web.backend.database.models.augmentation import AugmentationRecord
        from src.web.backend.database.models.augmentation_result import AugmentationResult

        # 验证关系定义存在
        assert hasattr(AugmentationRecord, 'results')
        assert hasattr(AugmentationResult, 'augmentation_record')

    def test_dataset_images_relationship(self):
        """测试数据集与图像的关系"""
        from src.web.backend.database.models.dataset import Dataset
        from src.web.backend.database.models.dataset_image import DatasetImage

        # 验证关系定义存在
        assert hasattr(Dataset, 'images')
        assert hasattr(DatasetImage, 'dataset')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])