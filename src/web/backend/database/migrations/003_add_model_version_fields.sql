-- 迁移脚本: 为 models 表添加版本管理字段
-- 版本: 003
-- 日期: 2026-04-09
-- 说明: 添加 parent_model_id, changelog, is_latest 字段

-- 添加 parent_model_id 字段（自引用外键）
ALTER TABLE models
ADD COLUMN parent_model_id BIGINT COMMENT '父模型ID（用于版本继承）' AFTER version;

-- 添加外键约束（自引用）
ALTER TABLE models
ADD CONSTRAINT fk_model_parent
FOREIGN KEY (parent_model_id) REFERENCES models(id) ON DELETE SET NULL;

-- 添加 changelog 字段
ALTER TABLE models
ADD COLUMN changelog TEXT COMMENT '版本变更日志' AFTER parent_model_id;

-- 添加 is_latest 字段
ALTER TABLE models
ADD COLUMN is_latest TINYINT DEFAULT 1 COMMENT '是否为最新版本' AFTER is_default;

-- 添加索引
ALTER TABLE models
ADD INDEX idx_is_latest (is_latest);

-- 为现有数据设置默认值（所有现有模型默认为最新版本）
UPDATE models SET is_latest = 1 WHERE is_latest IS NULL;

-- 验证字段添加成功
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'models'
AND COLUMN_NAME IN ('parent_model_id', 'changelog', 'is_latest');