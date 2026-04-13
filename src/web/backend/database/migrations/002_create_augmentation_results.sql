-- 迁移脚本: 创建 augmentation_results 表并迁移数据
-- 版本: 002
-- 日期: 2026-04-09
-- 说明: 创建 augmentation_results 表，从 augmentation_records.result_images 迁移数据

-- 1. 创建 augmentation_results 表
CREATE TABLE IF NOT EXISTS augmentation_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '结果ID',
    record_id BIGINT NOT NULL COMMENT '增强记录ID',
    result_image LONGTEXT NOT NULL COMMENT '增强结果图片（Base64编码）',
    variation_index INT NOT NULL COMMENT '变体序号（从0开始）',
    image_width INT COMMENT '图像宽度',
    image_height INT COMMENT '图像高度',
    image_format VARCHAR(10) COMMENT '图像格式',
    INDEX idx_record_id (record_id),
    CONSTRAINT fk_augment_result_record
        FOREIGN KEY (record_id)
        REFERENCES augmentation_records(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据增强结果表';

-- 2. 迁移现有数据（从 JSON 数组拆分为独立记录）
-- 注意：此步骤需要在 Python 中执行，因为 MySQL 不支持直接解析 JSON 数组
-- 以下是 Python 迁移脚本的 SQL 逻辑说明：
--
-- Python 迁移代码示例：
-- import json
-- for record in session.query(AugmentationRecord).all():
--     if record.result_images:
--         images = json.loads(record.result_images) if isinstance(record.result_images, str) else record.result_images
--         for idx, img in enumerate(images):
--             result = AugmentationResult(
--                 record_id=record.id,
--                 result_image=img,
--                 variation_index=idx
--             )
--             session.add(result)
-- session.commit()

-- 3. 数据迁移完成后，删除 result_images 字段（可选，建议保留一段时间作为备份）
-- ALTER TABLE augmentation_records DROP COLUMN result_images;

-- 验证表创建成功
SHOW CREATE TABLE augmentation_results;