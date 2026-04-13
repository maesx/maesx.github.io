## 1. 数据库表结构更新

- [x] 1.1 更新 database_schema_design.md 文档，添加新字段和表定义
- [x] 1.2 为 segmentation_records 表添加 fused_image、class_iou、pixel_distribution、instance_info 字段
- [x] 1.3 创建 augmentation_results 表（拆分自 augmentation_records.result_images）
- [x] 1.4 为 models 表添加 version、parent_model_id、changelog、is_latest 字段
- [x] 1.5 创建 datasets 表
- [x] 1.6 创建 dataset_images 表

## 2. ORM 模型更新

- [x] 2.1 更新 SegmentationRecord 模型，添加新字段映射
- [x] 2.2 创建 AugmentationResult 模型类
- [x] 2.3 更新 AugmentationRecord 模型，添加与 AugmentationResult 的关联关系
- [x] 2.4 更新 Model 模型，添加版本管理字段
- [x] 2.5 创建 Dataset 模型类
- [x] 2.6 创建 DatasetImage 模型类
- [x] 2.7 更新 models/__init__.py 导出新模型

## 3. 数据迁移脚本

- [x] 3.1 创建迁移脚本：为 segmentation_records 添加新字段
- [x] 3.2 创建迁移脚本：将现有 augmentation_records.result_images 数据迁移到 augmentation_results 表
- [x] 3.3 创建迁移脚本：为 models 表添加版本管理字段
- [x] 3.4 创建 datasets 和 dataset_images 表的初始化脚本

## 4. 存储服务更新

- [x] 4.1 更新 storage_service.py 支持新的数据结构
- [x] 4.2 更新分割结果保存逻辑，填充新字段
- [x] 4.3 更新数据增强结果保存逻辑，使用新的表结构

## 5. 测试验证

- [x] 5.1 编写 ORM 模型单元测试
- [x] 5.2 验证数据迁移脚本正确性
- [x] 5.3 测试新表结构的 CRUD 操作
- [x] 5.4 验证向后兼容性（现有数据不受影响）