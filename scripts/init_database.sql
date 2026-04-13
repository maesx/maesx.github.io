-- MySQL数据库初始化SQL脚本
-- 版本: 1.0
-- 创建日期: 2026-04-09

-- 创建数据库
CREATE DATABASE IF NOT EXISTS image_segment_platform
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE image_segment_platform;

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱地址',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    salt VARCHAR(64) NOT NULL COMMENT '密码盐值',
    nickname VARCHAR(50) COMMENT '用户昵称',
    avatar TEXT COMMENT '头像（Base64）',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '用户角色',
    status TINYINT DEFAULT 1 COMMENT '状态（1=正常, 0=禁用）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login_at DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(45) COMMENT '最后登录IP',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. 模型管理表
-- ============================================
CREATE TABLE IF NOT EXISTS models (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '模型ID',
    model_name VARCHAR(100) UNIQUE NOT NULL COMMENT '模型名称',
    model_type ENUM('segmentation', 'classification', 'detection') NOT NULL COMMENT '模型类型',
    version VARCHAR(20) COMMENT '模型版本',
    description TEXT COMMENT '模型描述',
    model_path VARCHAR(255) COMMENT '模型文件路径',
    model_size BIGINT COMMENT '模型文件大小（字节）',
    input_size VARCHAR(20) COMMENT '输入尺寸',
    num_classes INT COMMENT '类别数量',
    supported_types JSON COMMENT '支持的分割类型列表',
    performance_metrics JSON COMMENT '性能指标',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    is_default TINYINT DEFAULT 0 COMMENT '是否默认模型',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_model_name (model_name),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型管理表';

-- ============================================
-- 3. 图像分割记录表
-- ============================================
CREATE TABLE IF NOT EXISTS segmentation_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id BIGINT COMMENT '用户ID',
    model_id BIGINT COMMENT '模型ID',
    original_image LONGTEXT NOT NULL COMMENT '原图（Base64编码）',
    result_image LONGTEXT NOT NULL COMMENT '分割结果图（Base64编码）',
    segment_type ENUM('semantic', 'instance') NOT NULL COMMENT '分割类型',
    image_width INT COMMENT '图像宽度',
    image_height INT COMMENT '图像高度',
    image_format VARCHAR(10) COMMENT '图像格式',
    file_size BIGINT COMMENT '文件大小（字节）',
    processing_time FLOAT COMMENT '处理耗时（秒）',
    iou_score FLOAT COMMENT 'IoU得分',
    accuracy FLOAT COMMENT '准确率',
    additional_metrics JSON COMMENT '其他评估指标',
    status TINYINT DEFAULT 1 COMMENT '状态（1=成功, 0=失败）',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_model_id (model_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY fk_segment_user (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY fk_segment_model (model_id) REFERENCES models(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='图像分割记录表';

-- ============================================
-- 4. 数据增强记录表
-- ============================================
CREATE TABLE IF NOT EXISTS augmentation_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id BIGINT COMMENT '用户ID',
    original_image LONGTEXT NOT NULL COMMENT '原图（Base64编码）',
    augmentation_type VARCHAR(255) NOT NULL COMMENT '增强类型',
    methods_used JSON NOT NULL COMMENT '使用的增强方法列表',
    result_images JSON NOT NULL COMMENT '增强结果图片列表',
    num_variations INT DEFAULT 3 COMMENT '生成变体数量',
    image_width INT COMMENT '原图宽度',
    image_height INT COMMENT '原图高度',
    image_format VARCHAR(10) COMMENT '图像格式',
    file_size BIGINT COMMENT '原文件大小（字节）',
    status TINYINT DEFAULT 1 COMMENT '状态（1=成功, 0=失败）',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY fk_augment_user (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据增强记录表';

-- ============================================
-- 5. 操作日志表
-- ============================================
CREATE TABLE IF NOT EXISTS operation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id BIGINT COMMENT '操作用户ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) NOT NULL COMMENT '资源类型',
    resource_id BIGINT COMMENT '资源ID',
    operation_detail JSON COMMENT '操作详情',
    ip_address VARCHAR(45) COMMENT '操作IP地址',
    user_agent VARCHAR(255) COMMENT '用户代理',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user_id (user_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY fk_log_user (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ============================================
-- 插入默认数据
-- ============================================

-- 插入默认管理员账户（密码: admin123）
-- 密码哈希需要通过Python脚本生成，这里仅作为示例
-- INSERT INTO users (username, email, password_hash, salt, nickname, role, status)
-- VALUES ('admin', 'admin@example.com', 'hashed_password', 'salt_value', '系统管理员', 'admin', 1);

-- 插入默认模型
INSERT INTO models (model_name, model_type, version, description, input_size, num_classes, supported_types, is_active, is_default)
VALUES 
('unet_basic', 'segmentation', '1.0', '基础U-Net分割模型', '512x512', 2, '["semantic"]', 1, 1),
('mask_rcnn', 'segmentation', '1.0', 'Mask R-CNN实例分割模型', '800x800', 80, '["instance"]', 1, 0)
ON DUPLICATE KEY UPDATE model_name=model_name;

-- 完成
SELECT '✅ 数据库初始化完成' AS message;
