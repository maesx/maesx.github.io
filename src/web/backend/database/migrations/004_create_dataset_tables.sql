-- 迁移脚本: 创建 datasets 和 dataset_images 表
-- 版本: 004
-- 日期: 2026-04-09
-- 说明: 创建数据集管理相关的两张表

-- 1. 创建 datasets 表
CREATE TABLE IF NOT EXISTS datasets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '数据集ID',
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '数据集名称',
    description TEXT COMMENT '数据集描述',
    dataset_type ENUM('training', 'validation', 'test', 'custom') DEFAULT 'custom' COMMENT '数据集类型',
    image_count INT DEFAULT 0 COMMENT '图像数量',
    annotation_count INT DEFAULT 0 COMMENT '已标注数量',
    total_size BIGINT DEFAULT 0 COMMENT '总大小（字节）',
    is_public TINYINT DEFAULT 0 COMMENT '是否公开（0=私密, 1=公开）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_is_public (is_public)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据集表';

-- 2. 创建 dataset_images 表
CREATE TABLE IF NOT EXISTS dataset_images (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '图像ID',
    dataset_id BIGINT NOT NULL COMMENT '数据集ID',
    filename VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) COMMENT '文件存储路径',
    image_width INT COMMENT '图像宽度',
    image_height INT COMMENT '图像高度',
    image_format VARCHAR(10) COMMENT '图像格式',
    file_size BIGINT COMMENT '文件大小（字节）',
    annotation_data JSON COMMENT '标注数据（支持多种格式）',
    annotation_status ENUM('pending', 'annotated', 'reviewed') DEFAULT 'pending' COMMENT '标注状态',
    uploaded_by BIGINT COMMENT '上传用户ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_dataset_id (dataset_id),
    INDEX idx_annotation_status (annotation_status),
    CONSTRAINT fk_dataset_image_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES datasets(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_dataset_image_user
        FOREIGN KEY (uploaded_by)
        REFERENCES users(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据集图像表';

-- 验证表创建成功
SHOW CREATE TABLE datasets;
SHOW CREATE TABLE dataset_images;