-- =====================================================
-- 图像分割可视化平台 - 完整建表脚本
-- 生成时间: 2026-04-23
-- 说明: 基于SQLAlchemy模型自动生成
-- 数据库: MySQL 5.7+ / 8.0+
-- 字符集: utf8mb4
-- =====================================================

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 1. 用户表 (users)
-- =====================================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱地址',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `salt` VARCHAR(64) NOT NULL COMMENT '密码盐值',
    `nickname` VARCHAR(50) DEFAULT NULL COMMENT '用户昵称',
    `avatar` TEXT COMMENT '头像（Base64）',
    `role` ENUM('user', 'admin') DEFAULT 'user' COMMENT '用户角色',
    `status` SMALLINT DEFAULT 1 COMMENT '状态（1=正常, 0=禁用）',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `last_login_ip` VARCHAR(45) DEFAULT NULL COMMENT '最后登录IP',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_username` (`username`),
    UNIQUE KEY `idx_email` (`email`),
    KEY `idx_role` (`role`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =====================================================
-- 2. 模型管理表 (models)
-- =====================================================
DROP TABLE IF EXISTS `models`;
CREATE TABLE `models` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '模型ID',
    `model_name` VARCHAR(100) NOT NULL COMMENT '模型名称',
    `model_type` ENUM('segmentation', 'classification', 'detection') NOT NULL COMMENT '模型类型',
    `version` VARCHAR(20) DEFAULT NULL COMMENT '模型版本号（如"1.0.0"）',
    `parent_model_id` BIGINT DEFAULT NULL COMMENT '父模型ID（用于版本继承）',
    `changelog` TEXT COMMENT '版本变更日志',
    `description` TEXT COMMENT '模型描述',
    `model_path` VARCHAR(255) DEFAULT NULL COMMENT '模型文件路径',
    `model_size` BIGINT DEFAULT NULL COMMENT '模型文件大小（字节）',
    `input_size` VARCHAR(20) DEFAULT NULL COMMENT '输入尺寸（如"512x512"）',
    `num_classes` INT DEFAULT NULL COMMENT '类别数量',
    `supported_types` JSON DEFAULT NULL COMMENT '支持的分割类型列表',
    `performance_metrics` JSON DEFAULT NULL COMMENT '性能指标',
    `is_active` SMALLINT DEFAULT 1 COMMENT '是否启用',
    `is_default` SMALLINT DEFAULT 0 COMMENT '是否默认模型',
    `is_latest` SMALLINT DEFAULT 1 COMMENT '是否为最新版本',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_model_name` (`model_name`),
    KEY `idx_model_type` (`model_type`),
    KEY `idx_is_active` (`is_active`),
    KEY `idx_is_latest` (`is_latest`),
    KEY `idx_parent_model` (`parent_model_id`),
    CONSTRAINT `fk_model_parent` FOREIGN KEY (`parent_model_id`) REFERENCES `models` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型管理表';

-- =====================================================
-- 3. 图像分割记录表 (segmentation_records)
-- =====================================================
DROP TABLE IF EXISTS `segmentation_records`;
CREATE TABLE `segmentation_records` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `user_id` BIGINT DEFAULT NULL COMMENT '用户ID',
    `model_id` BIGINT DEFAULT NULL COMMENT '模型ID',
    `original_image` LONGTEXT NOT NULL COMMENT '原图（Base64编码）',
    `result_image` LONGTEXT NOT NULL COMMENT '分割结果图（Base64编码）',
    `fused_image` LONGTEXT COMMENT '融合图像（Base64编码）',
    `segment_type` ENUM('semantic', 'instance') NOT NULL COMMENT '分割类型',
    `image_width` INT DEFAULT NULL COMMENT '图像宽度',
    `image_height` INT DEFAULT NULL COMMENT '图像高度',
    `image_format` VARCHAR(10) DEFAULT NULL COMMENT '图像格式（PNG/JPG等）',
    `file_size` BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
    `processing_time` FLOAT DEFAULT NULL COMMENT '处理耗时（秒）',
    `iou_score` FLOAT DEFAULT NULL COMMENT 'IoU得分',
    `accuracy` FLOAT DEFAULT NULL COMMENT '准确率',
    `class_iou` JSON DEFAULT NULL COMMENT '各类别IoU得分列表',
    `pixel_distribution` JSON DEFAULT NULL COMMENT '各类别像素占比列表',
    `instance_info` JSON DEFAULT NULL COMMENT '实例分割信息（实例数量、边界框等）',
    `additional_metrics` JSON DEFAULT NULL COMMENT '其他评估指标',
    `status` SMALLINT DEFAULT 1 COMMENT '状态（1=成功, 0=失败）',
    `error_message` TEXT COMMENT '错误信息',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_model_id` (`model_id`),
    KEY `idx_created_at` (`created_at`),
    KEY `idx_status` (`status`),
    KEY `idx_segment_type` (`segment_type`),
    CONSTRAINT `fk_segmentation_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_segmentation_model` FOREIGN KEY (`model_id`) REFERENCES `models` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图像分割记录表';

-- =====================================================
-- 4. 数据增强记录表 (augmentation_records)
-- =====================================================
DROP TABLE IF EXISTS `augmentation_records`;
CREATE TABLE `augmentation_records` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `user_id` BIGINT DEFAULT NULL COMMENT '用户ID（可为空）',
    `original_image` LONGTEXT NOT NULL COMMENT '原图（Base64编码）',
    `augmentation_type` VARCHAR(255) NOT NULL COMMENT '增强类型（中文描述+参数）',
    `methods_used` JSON NOT NULL COMMENT '使用的增强方法列表',
    `num_variations` INT DEFAULT 3 COMMENT '生成变体数量',
    `image_width` INT DEFAULT NULL COMMENT '原图宽度',
    `image_height` INT DEFAULT NULL COMMENT '原图高度',
    `image_format` VARCHAR(10) DEFAULT NULL COMMENT '图像格式',
    `file_size` BIGINT DEFAULT NULL COMMENT '原文件大小（字节）',
    `status` SMALLINT DEFAULT 1 COMMENT '状态（1=成功, 0=失败）',
    `error_message` TEXT COMMENT '错误信息',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_created_at` (`created_at`),
    KEY `idx_status` (`status`),
    CONSTRAINT `fk_augmentation_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据增强记录表';

-- =====================================================
-- 5. 数据增强结果表 (augmentation_results)
-- =====================================================
DROP TABLE IF EXISTS `augmentation_results`;
CREATE TABLE `augmentation_results` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '结果ID',
    `record_id` BIGINT NOT NULL COMMENT '增强记录ID',
    `result_image` LONGTEXT NOT NULL COMMENT '增强结果图片（Base64编码）',
    `variation_index` INT NOT NULL COMMENT '变体序号（从0开始）',
    `image_width` INT DEFAULT NULL COMMENT '图像宽度',
    `image_height` INT DEFAULT NULL COMMENT '图像高度',
    `image_format` VARCHAR(10) DEFAULT NULL COMMENT '图像格式',
    PRIMARY KEY (`id`),
    KEY `idx_record_id` (`record_id`),
    KEY `idx_variation_index` (`variation_index`),
    CONSTRAINT `fk_augment_result_record` FOREIGN KEY (`record_id`) REFERENCES `augmentation_records` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据增强结果表';

-- =====================================================
-- 6. 数据集表 (datasets)
-- =====================================================
DROP TABLE IF EXISTS `datasets`;
CREATE TABLE `datasets` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '数据集ID',
    `name` VARCHAR(100) NOT NULL COMMENT '数据集名称',
    `description` TEXT COMMENT '数据集描述',
    `dataset_type` ENUM('training', 'validation', 'test', 'custom') DEFAULT 'custom' COMMENT '数据集类型',
    `image_count` INT DEFAULT 0 COMMENT '图像数量',
    `annotation_count` INT DEFAULT 0 COMMENT '已标注数量',
    `total_size` BIGINT DEFAULT 0 COMMENT '总大小（字节）',
    `is_public` SMALLINT DEFAULT 0 COMMENT '是否公开（0=私密, 1=公开）',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_name` (`name`),
    KEY `idx_dataset_type` (`dataset_type`),
    KEY `idx_is_public` (`is_public`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据集表';

-- =====================================================
-- 7. 数据集图像表 (dataset_images)
-- =====================================================
DROP TABLE IF EXISTS `dataset_images`;
CREATE TABLE `dataset_images` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '图像ID',
    `dataset_id` BIGINT NOT NULL COMMENT '数据集ID',
    `uploaded_by` BIGINT DEFAULT NULL COMMENT '上传用户ID',
    `filename` VARCHAR(255) NOT NULL COMMENT '文件名',
    `file_path` VARCHAR(500) DEFAULT NULL COMMENT '文件存储路径',
    `image_width` INT DEFAULT NULL COMMENT '图像宽度',
    `image_height` INT DEFAULT NULL COMMENT '图像高度',
    `image_format` VARCHAR(10) DEFAULT NULL COMMENT '图像格式',
    `file_size` BIGINT DEFAULT NULL COMMENT '文件大小（字节）',
    `annotation_data` JSON DEFAULT NULL COMMENT '标注数据（支持多种格式）',
    `annotation_status` ENUM('pending', 'annotated', 'reviewed') DEFAULT 'pending' COMMENT '标注状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_dataset_id` (`dataset_id`),
    KEY `idx_uploaded_by` (`uploaded_by`),
    KEY `idx_annotation_status` (`annotation_status`),
    KEY `idx_filename` (`filename`),
    CONSTRAINT `fk_dataset_image_dataset` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dataset_image_user` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据集图像表';

-- =====================================================
-- 8. 操作日志表 (operation_logs)
-- =====================================================
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `user_id` BIGINT DEFAULT NULL COMMENT '操作用户ID',
    `operation_type` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `resource_type` VARCHAR(50) NOT NULL COMMENT '资源类型',
    `resource_id` BIGINT DEFAULT NULL COMMENT '资源ID',
    `operation_detail` JSON DEFAULT NULL COMMENT '操作详情',
    `ip_address` VARCHAR(45) DEFAULT NULL COMMENT '操作IP地址',
    `user_agent` VARCHAR(255) DEFAULT NULL COMMENT '用户代理',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_operation_type` (`operation_type`),
    KEY `idx_resource_type` (`resource_type`),
    KEY `idx_created_at` (`created_at`),
    CONSTRAINT `fk_operation_log_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- =====================================================
-- 9. 创建枚举类型视图（可选，用于文档说明）
-- =====================================================

-- 用户角色枚举: user, admin
-- 模型类型枚举: segmentation, classification, detection
-- 分割类型枚举: semantic, instance
-- 数据集类型枚举: training, validation, test, custom
-- 标注状态枚举: pending, annotated, reviewed

-- =====================================================
-- 10. 插入默认管理员用户（可选）
-- =====================================================

-- 默认管理员账户
-- 用户名: admin
-- 密码: admin123 (实际使用时需替换为正确的哈希值)
-- 密码哈希和盐值需要通过实际的加密算法生成

INSERT INTO `users` (`username`, `email`, `password_hash`, `salt`, `nickname`, `role`, `status`)
VALUES 
('admin', 'admin@example.com', 'REPLACE_WITH_ACTUAL_HASH', 'REPLACE_WITH_ACTUAL_SALT', '系统管理员', 'admin', 1);

-- =====================================================
-- 11. 插入默认模型记录（可选）
-- =====================================================

-- 默认分割模型
INSERT INTO `models` (`model_name`, `model_type`, `version`, `description`, `model_path`, `input_size`, `num_classes`, `is_active`, `is_default`, `is_latest`)
VALUES 
('best_model', 'segmentation', '1.0.0', '最佳分割模型', 'outputs/checkpoints/best_model.pth', '512x512', 4, 1, 1, 1);

-- =====================================================
-- 完成
-- =====================================================

SET FOREIGN_KEY_CHECKS = 1;

-- 验证表创建
SELECT 
    TABLE_NAME AS '表名',
    TABLE_COMMENT AS '表注释',
    TABLE_ROWS AS '记录数',
    CREATE_TIME AS '创建时间'
FROM 
    INFORMATION_SCHEMA.TABLES 
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('users', 'models', 'segmentation_records', 'augmentation_records', 'augmentation_results', 'datasets', 'dataset_images', 'operation_logs')
ORDER BY 
    TABLE_NAME;

-- 显示表结构统计
SELECT 
    '数据库表创建完成' AS '状态',
    COUNT(*) AS '表数量'
FROM 
    INFORMATION_SCHEMA.TABLES 
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('users', 'models', 'segmentation_records', 'augmentation_records', 'augmentation_results', 'datasets', 'dataset_images', 'operation_logs');
