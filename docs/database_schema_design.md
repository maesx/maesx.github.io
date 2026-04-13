# MySQL 数据库架构设计文档

> **设计原则**: 渐进式架构，不影响现有内存存储功能，提供MySQL作为持久化存储选项

## 📋 数据库信息

- **数据库类型**: MySQL 8.0+
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_unicode_ci
- **存储引擎**: InnoDB

---

## 🗃️ 数据表结构设计

### 1. 用户表 (users)

**用途**: 存储用户账户信息和认证数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希（bcrypt） |
| salt | VARCHAR(64) | NOT NULL | 密码盐值 |
| nickname | VARCHAR(50) | | 用户昵称 |
| avatar | TEXT | | 头像（Base64） |
| role | ENUM('user', 'admin') | DEFAULT 'user' | 用户角色 |
| status | TINYINT | DEFAULT 1 | 状态（1=正常, 0=禁用） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| last_login_at | DATETIME | | 最后登录时间 |
| last_login_ip | VARCHAR(45) | | 最后登录IP |

**索引**:
- `idx_username` ON (username)
- `idx_email` ON (email)
- `idx_status` ON (status)

---

### 2. 图像分割记录表 (segmentation_records)

**用途**: 存储图像分割历史记录和结果

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 记录ID |
| user_id | BIGINT | FOREIGN KEY, INDEX | 用户ID（关联users.id） |
| model_id | BIGINT | FOREIGN KEY, INDEX | 模型ID（关联models.id） |
| original_image | LONGTEXT | NOT NULL | 原图（Base64编码） |
| result_image | LONGTEXT | NOT NULL | 分割结果图（Base64编码） |
| fused_image | LONGTEXT | | 融合图像（Base64编码） |
| segment_type | ENUM('semantic', 'instance') | NOT NULL | 分割类型 |
| image_width | INT | | 图像宽度 |
| image_height | INT | | 图像高度 |
| image_format | VARCHAR(10) | | 图像格式（PNG/JPG等） |
| file_size | BIGINT | | 文件大小（字节） |
| processing_time | FLOAT | | 处理耗时（秒） |
| iou_score | FLOAT | | IoU得分 |
| accuracy | FLOAT | | 准确率 |
| class_iou | JSON | | 各类别IoU得分列表 |
| pixel_distribution | JSON | | 各类别像素占比列表 |
| instance_info | JSON | | 实例分割信息（实例数量、边界框等） |
| additional_metrics | JSON | | 其他评估指标 |
| status | TINYINT | DEFAULT 1 | 状态（1=成功, 0=失败） |
| error_message | TEXT | | 错误信息 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- `idx_user_id` ON (user_id)
- `idx_model_id` ON (model_id)
- `idx_created_at` ON (created_at)

**外键约束**:
- `fk_segment_user` FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- `fk_segment_model` FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL

---

### 3. 数据增强记录表 (augmentation_records)

**用途**: 存储数据增强历史记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 记录ID |
| user_id | BIGINT | FOREIGN KEY, INDEX | 用户ID（关联users.id） |
| original_image | LONGTEXT | NOT NULL | 原图（Base64编码） |
| augmentation_type | VARCHAR(255) | NOT NULL | 增强类型（中文描述+参数） |
| methods_used | JSON | NOT NULL | 使用的增强方法列表 |
| num_variations | INT | DEFAULT 3 | 生成变体数量 |
| image_width | INT | | 原图宽度 |
| image_height | INT | | 原图高度 |
| image_format | VARCHAR(10) | | 图像格式 |
| file_size | BIGINT | | 原文件大小（字节） |
| status | TINYINT | DEFAULT 1 | 状态（1=成功, 0=失败） |
| error_message | TEXT | | 错误信息 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- `idx_user_id` ON (user_id)
- `idx_created_at` ON (created_at)

**外键约束**:
- `fk_augment_user` FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

---

### 3.1 数据增强结果表 (augmentation_results)

**用途**: 存储数据增强生成的结果图片（拆分自augmentation_records）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 结果ID |
| record_id | BIGINT | FOREIGN KEY, INDEX | 增强记录ID（关联augmentation_records.id） |
| result_image | LONGTEXT | NOT NULL | 增强结果图片（Base64编码） |
| variation_index | INT | NOT NULL | 变体序号（从0开始） |
| image_width | INT | | 图像宽度 |
| image_height | INT | | 图像高度 |
| image_format | VARCHAR(10) | | 图像格式 |

**索引**:
- `idx_record_id` ON (record_id)

**外键约束**:
- `fk_augment_result_record` FOREIGN KEY (record_id) REFERENCES augmentation_records(id) ON DELETE CASCADE

---

### 4. 模型管理表 (models)

**用途**: 存储AI模型元数据和管理信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 模型ID |
| model_name | VARCHAR(100) | UNIQUE, NOT NULL | 模型名称 |
| model_type | ENUM('segmentation', 'classification', 'detection') | NOT NULL | 模型类型 |
| version | VARCHAR(20) | | 模型版本号（如"1.0.0"） |
| parent_model_id | BIGINT | FOREIGN KEY | 父模型ID（用于版本继承） |
| changelog | TEXT | | 版本变更日志 |
| description | TEXT | | 模型描述 |
| model_path | VARCHAR(255) | | 模型文件路径 |
| model_size | BIGINT | | 模型文件大小（字节） |
| input_size | VARCHAR(20) | | 输入尺寸（如"512x512"） |
| num_classes | INT | | 类别数量 |
| supported_types | JSON | | 支持的分割类型列表 |
| performance_metrics | JSON | | 性能指标 |
| is_active | TINYINT | DEFAULT 1 | 是否启用 |
| is_default | TINYINT | DEFAULT 0 | 是否默认模型 |
| is_latest | TINYINT | DEFAULT 1 | 是否为最新版本 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- `idx_model_name` ON (model_name)
- `idx_is_active` ON (is_active)
- `idx_is_latest` ON (is_latest)

**外键约束**:
- `fk_model_parent` FOREIGN KEY (parent_model_id) REFERENCES models(id) ON DELETE SET NULL

---

### 5. 数据集表 (datasets)

**用途**: 存储数据集元数据和管理信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 数据集ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | 数据集名称 |
| description | TEXT | | 数据集描述 |
| dataset_type | ENUM('training', 'validation', 'test', 'custom') | DEFAULT 'custom' | 数据集类型 |
| image_count | INT | DEFAULT 0 | 图像数量 |
| annotation_count | INT | DEFAULT 0 | 已标注数量 |
| total_size | BIGINT | DEFAULT 0 | 总大小（字节） |
| is_public | TINYINT | DEFAULT 0, INDEX | 是否公开（0=私密, 1=公开） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

**索引**:
- `idx_name` ON (name)
- `idx_is_public` ON (is_public)

---

### 6. 数据集图像表 (dataset_images)

**用途**: 存储数据集中的图像和标注信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 图像ID |
| dataset_id | BIGINT | FOREIGN KEY, INDEX | 数据集ID（关联datasets.id） |
| filename | VARCHAR(255) | NOT NULL | 文件名 |
| file_path | VARCHAR(500) | | 文件存储路径 |
| image_width | INT | | 图像宽度 |
| image_height | INT | | 图像高度 |
| image_format | VARCHAR(10) | | 图像格式 |
| file_size | BIGINT | | 文件大小（字节） |
| annotation_data | JSON | | 标注数据（支持多种格式） |
| annotation_status | ENUM('pending', 'annotated', 'reviewed') | DEFAULT 'pending', INDEX | 标注状态 |
| uploaded_by | BIGINT | FOREIGN KEY | 上传用户ID |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**:
- `idx_dataset_id` ON (dataset_id)
- `idx_annotation_status` ON (annotation_status)

**外键约束**:
- `fk_dataset_image_dataset` FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
- `fk_dataset_image_user` FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL

---

### 7. 操作日志表 (operation_logs)

**用途**: 记录关键数据变更操作日志

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 日志ID |
| user_id | BIGINT | FOREIGN KEY, INDEX | 操作用户ID |
| operation_type | VARCHAR(50) | NOT NULL | 操作类型 |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型（user/segment/augment/model） |
| resource_id | BIGINT | | 资源ID |
| operation_detail | JSON | | 操作详情 |
| ip_address | VARCHAR(45) | | 操作IP地址 |
| user_agent | VARCHAR(255) | | 用户代理 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 操作时间 |

**索引**:
- `idx_user_id` ON (user_id)
- `idx_operation_type` ON (operation_type)
- `idx_resource` ON (resource_type, resource_id)
- `idx_created_at` ON (created_at)

**外键约束**:
- `fk_log_user` FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL

---

## 🔧 技术选型

### ORM框架
- **SQLAlchemy 2.0+**: Python最成熟的ORM框架，支持连接池、事务管理
- **PyMySQL**: MySQL驱动程序

### 连接池配置
```python
# 推荐配置
pool_size = 10  # 连接池大小
max_overflow = 20  # 最大溢出连接数
pool_recycle = 3600  # 连接回收时间（1小时）
pool_timeout = 30  # 获取连接超时时间
```

### Base64存储优化
- 图片压缩：存储前使用PIL进行质量压缩
- 分离存储：超大图片可考虑分表存储
- 索引优化：避免在Base64字段上建立索引

---

## 📊 数据流转设计

### 写入流程
```
用户操作 → API接口 → Service层 → ORM模型 → MySQL数据库
                                    ↓
                              日志记录 → operation_logs表
```

### 读取流程
```
用户查询 → API接口 → Service层 → ORM模型 → MySQL数据库
                                    ↓
                              缓存优化（可选）
```

---

## 🔐 数据库配置管理

### 环境变量设计
```bash
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=image_segment_platform
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_CHARSET=utf8mb4

# 连接池配置
MYSQL_POOL_SIZE=10
MYSQL_MAX_OVERFLOW=20
MYSQL_POOL_RECYCLE=3600
MYSQL_POOL_TIMEOUT=30
```

### 配置优先级
1. 环境变量（生产环境）
2. 配置文件（开发环境）
3. 默认值（兜底配置）

---

## ⚙️ 初始化脚本设计

### 1. 数据库创建脚本
```sql
CREATE DATABASE IF NOT EXISTS image_segment_platform
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 2. 表结构创建脚本
- 按依赖顺序创建表（users → models → 其他）
- 自动创建索引和外键约束
- 支持幂等性（可重复执行）

### 3. 初始数据插入
- 默认管理员账户
- 默认模型记录
- 系统配置项

---

## 🚀 渐进式接入方案

### 阶段1: 准备阶段（当前）
- ✅ 设计数据库Schema
- ✅ 创建ORM模型类
- ✅ 实现数据库服务层
- ✅ 编写配置文件
- ⚠️ 不影响现有系统运行

### 阶段2: 接入阶段（明天）
- 启用MySQL数据库
- 执行初始化脚本
- 切换数据存储方式
- 测试验证

### 阶段3: 优化阶段
- 添加缓存层（Redis）
- 性能优化
- 监控告警

---

## 📝 注意事项

1. **Base64存储限制**: MySQL LONGTEXT最大支持4GB，足够存储图片
2. **内存管理**: 大文件读取时考虑流式处理，避免内存溢出
3. **事务处理**: 关键操作使用事务确保数据一致性
4. **错误处理**: 数据库操作失败时优雅降级到内存存储
5. **性能监控**: 记录慢查询日志，优化查询性能

---

## 📚 后续扩展

- 支持图片OSS存储（MySQL只存URL）
- 数据备份与恢复方案
- 数据迁移工具
- API文档生成
- 性能压测报告
