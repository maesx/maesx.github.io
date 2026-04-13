## Context

当前项目使用 SQLAlchemy ORM + MySQL 作为持久化存储方案，同时保留内存存储作为备选。现有 `database_schema_design.md` 定义了 5 张核心表，但与实际业务数据结构存在差异：

- `segmentation_records` 表缺少关键字段（融合图、类别IoU、像素分布、实例信息）
- `augmentation_records` 表使用 JSON 存储多张图片，查询和存储效率低
- 缺乏模型版本管理和数据集管理所需的表结构

## Goals / Non-Goals

**Goals:**
- 补全 `segmentation_records` 表的关键字段，确保分割结果数据完整持久化
- 重构 `augmentation_records` 表，提升查询性能和存储效率
- 添加模型版本管理能力，支持多版本模型共存
- 添加数据集管理表结构，为后续数据集功能预留扩展

**Non-Goals:**
- 不实现用户认证功能（保留 users 表设计，暂不启用）
- 不持久化批量任务和对比列表（保持内存存储）
- 不修改现有 API 接口签名

## Decisions

### 1. segmentation_records 表字段扩展

**决策**: 添加 4 个新字段存储关键分割数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| fused_image | LONGTEXT | 融合图像（Base64） |
| class_iou | JSON | 各类别IoU得分列表 |
| pixel_distribution | JSON | 各类别像素占比列表 |
| instance_info | JSON | 实例分割信息（实例数量、边界框等） |

**理由**: 这些字段是分割结果的核心数据，缺失会导致历史记录无法完整复现分析结果。

**备选方案**: 将所有额外数据合并到 `additional_metrics` JSON 字段
- 优点: 表结构简单
- 缺点: 查询不便，语义不清晰

### 2. augmentation_records 表重构

**决策**: 拆分为 `augmentation_records`（主记录）+ `augmentation_results`（结果图片）两张表

```
augmentation_records (主记录)
├── id, user_id, original_image, augmentation_type, methods_used
├── num_variations, image_width, image_height, image_format
├── file_size, status, error_message, created_at
└── [索引] user_id, created_at

augmentation_results (结果图片)
├── id, record_id (FK), result_image, variation_index
├── image_width, image_height, image_format
└── [索引] record_id
```

**理由**: 
- 每张增强结果图片独立存储，支持单独查询
- 避免 JSON 字段过大导致的性能问题
- 便于后续扩展（如单独删除某张结果图）

**备选方案**: 保持 JSON 存储，添加压缩
- 优点: 改动最小
- 缺点: 无法单独查询某张图片，JSON 解析开销

### 3. 模型版本管理设计

**决策**: 在 `models` 表添加版本相关字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| version | VARCHAR(20) | 模型版本号（如 "1.0.0"） |
| parent_model_id | BIGINT | 父模型ID（用于版本继承） |
| changelog | TEXT | 版本变更日志 |
| is_latest | TINYINT | 是否为最新版本 |

**理由**: 支持同一模型的多个版本共存，便于模型迭代和回滚。

### 4. 数据集管理表设计

**决策**: 新增 `datasets` 和 `dataset_images` 两张表

```
datasets (数据集)
├── id, name, description, dataset_type
├── image_count, annotation_count, total_size
├── is_public, created_at, updated_at
└── [索引] name, is_public

dataset_images (数据集图像)
├── id, dataset_id (FK), filename, file_path
├── image_width, image_height, image_format, file_size
├── annotation_data (JSON), annotation_status
├── uploaded_by, created_at
└── [索引] dataset_id, annotation_status
```

**理由**: 为后续数据集管理功能预留表结构，支持图像上传、标注存储和统计。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 数据迁移可能导致服务中断 | 使用在线 DDL 或低峰期迁移，添加默认值确保兼容性 |
| LONGTEXT 字段存储大量 Base64 图片可能影响性能 | 后续考虑迁移到 OSS 文件存储，数据库只存路径 |
| 新表增加系统复杂度 | 保持表结构简洁，避免过度设计 |

## Migration Plan

1. **备份现有数据库**
2. **执行 DDL 迁移脚本**：
   - 为 `segmentation_records` 添加新字段（带默认值）
   - 创建 `augmentation_results` 表
   - 迁移现有 `augmentation_records.result_images` 数据到新表
   - 为 `models` 表添加版本管理字段
   - 创建 `datasets` 和 `dataset_images` 表
3. **更新 ORM 模型代码**
4. **验证数据完整性**
5. **回滚策略**: 保留原表结构 30 天，可随时回退

## Open Questions

1. 数据集的标注数据格式是否需要支持 COCO/VOC 等标准格式？
2. 模型版本是否需要支持灰度发布（部分用户使用新版本）？