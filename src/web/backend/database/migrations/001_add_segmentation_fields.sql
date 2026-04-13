-- 迁移脚本: 为 segmentation_records 表添加新字段
-- 版本: 001
-- 日期: 2026-04-09
-- 说明: 添加 fused_image, class_iou, pixel_distribution, instance_info 字段

-- 添加 fused_image 字段
ALTER TABLE segmentation_records
ADD COLUMN fused_image LONGTEXT COMMENT '融合图像（Base64编码）' AFTER result_image;

-- 添加 class_iou 字段
ALTER TABLE segmentation_records
ADD COLUMN class_iou JSON COMMENT '各类别IoU得分列表' AFTER accuracy;

-- 添加 pixel_distribution 字段
ALTER TABLE segmentation_records
ADD COLUMN pixel_distribution JSON COMMENT '各类别像素占比列表' AFTER class_iou;

-- 添加 instance_info 字段
ALTER TABLE segmentation_records
ADD COLUMN instance_info JSON COMMENT '实例分割信息（实例数量、边界框等）' AFTER pixel_distribution;

-- 验证字段添加成功
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'segmentation_records'
AND COLUMN_NAME IN ('fused_image', 'class_iou', 'pixel_distribution', 'instance_info');