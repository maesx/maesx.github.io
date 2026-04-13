## Why

当前 `database_schema_design.md` 文档中的表结构与实际内存存储的数据结构存在差异，导致部分关键数据无法持久化到数据库。同时，数据增强记录表的 JSON 存储方式存在性能隐患，且缺乏后续扩展（模型版本管理、数据集管理）所需的表结构设计。现在需要审查并优化数据库架构，确保数据完整性和可扩展性。

## What Changes

- **segmentation_records 表增加字段**：添加 `fused_image`（融合图）、`class_iou`（各类别IoU）、`pixel_distribution`（像素分布）、`instance_info`（实例信息）字段
- **augmentation_records 表重构**：将 JSON 存储的多个增强结果图片拆分为独立记录，每张图片一条记录
- **models 表增强**：添加模型版本管理相关字段，支持多版本模型共存
- **新增 datasets 表**：支持训练数据集的管理和标注
- **新增 dataset_images 表**：存储数据集中的图像和标注信息
- **更新 ORM 模型**：同步更新 Python ORM 模型类

## Capabilities

### New Capabilities
- `dataset-management`: 数据集管理功能，支持数据集的创建、图像上传、标注管理等
- `model-versioning`: 模型版本管理功能，支持多版本模型共存和版本切换

### Modified Capabilities
- `segmentation-storage`: 分割记录存储需求变更，需要存储更多关键数据字段
- `augmentation-storage`: 数据增强记录存储需求变更，从 JSON 存储改为独立记录存储

## Impact

- **受影响代码**：
  - `src/web/backend/database/models/segmentation.py` - SegmentationRecord 模型
  - `src/web/backend/database/models/augmentation.py` - AugmentationRecord 模型
  - `src/web/backend/database/models/model.py` - Model 模型
  - `src/web/backend/services/storage_service.py` - 存储服务
  - `docs/database_schema_design.md` - 数据库设计文档

- **数据库迁移**：需要执行数据���迁移脚本添加新字段和表

- **向后兼容性**：新增字段均有默认值，不影响现有数据