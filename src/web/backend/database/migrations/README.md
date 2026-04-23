# MySQL 数据库建表说明

## 📋 概述

本文档说明如何使用提供的SQL脚本创建MySQL数据库表结构。

**生成时间**: 2026-04-23  
**数据库类型**: MySQL 5.7+ / MySQL 8.0+  
**字符集**: utf8mb4  
**排序规则**: utf8mb4_unicode_ci

---

## 🗂️ 表结构总览

本项目包含 **8张核心业务表**:

| 序号 | 表名 | 说明 | 关键字段 |
|------|------|------|----------|
| 1 | `users` | 用户表 | id, username, email, role |
| 2 | `models` | 模型管理表 | id, model_name, version, is_latest |
| 3 | `segmentation_records` | 图像分割记录表 | id, user_id, model_id, segment_type |
| 4 | `augmentation_records` | 数据增强记录表 | id, user_id, methods_used |
| 5 | `augmentation_results` | 数据增强结果表 | id, record_id, variation_index |
| 6 | `datasets` | 数据集表 | id, name, dataset_type |
| 7 | `dataset_images` | 数据集图像表 | id, dataset_id, annotation_status |
| 8 | `operation_logs` | 操作日志表 | id, user_id, operation_type |

---

## 🔗 表关系图

```
users (用户)
  ├── segmentation_records (分割记录) [一对多]
  ├── augmentation_records (增强记录) [一对多]
  ├── dataset_images (数据集图像) [一对多]
  └── operation_logs (操作日志) [一对多]

models (模型)
  └── segmentation_records (分割记录) [一对多]

datasets (数据集)
  └── dataset_images (数据集图像) [一对多]

augmentation_records (增强记录)
  └── augmentation_results (增强结果) [一对多]

models (模型自关联)
  └── models (父模型) [版本继承]
```

---

## 🚀 快速开始

### 方式一：命令行执行（推荐）

```bash
# 1. 连接到MySQL服务器
mysql -u root -p

# 2. 创建数据库（如果尚未创建）
CREATE DATABASE IF NOT EXISTS image_segment_platform 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

# 3. 使用数据库
USE image_segment_platform;

# 4. 执行建表脚本
source /path/to/000_create_all_tables.sql;

# 或者直接导入
mysql -u root -p image_segment_platform < src/web/backend/database/migrations/000_create_all_tables.sql
```

### 方式二：使用客户端工具

1. 使用 Navicat / MySQL Workbench / phpMyAdmin 等工具
2. 连接到MySQL服务器
3. 打开 `000_create_all_tables.sql` 文件
4. 执行整个脚本

---

## ⚙️ 执行前提条件

### 1. MySQL配置要求

```sql
-- 查看当前字符集配置
SHOW VARIABLES LIKE 'character%';
SHOW VARIABLES LIKE 'collation%';

-- 确保以下配置正确:
-- character_set_server = utf8mb4
-- collation_server = utf8mb4_unicode_ci
```

### 2. 数据库创建

```sql
-- 创建数据库（如果尚未创建）
CREATE DATABASE IF NOT EXISTS image_segment_platform 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 授予权限（根据实际用户名修改）
GRANT ALL PRIVILEGES ON image_segment_platform.* 
TO 'your_user'@'localhost' IDENTIFIED BY 'your_password';

FLUSH PRIVILEGES;
```

### 3. 环境变量配置

在项目根目录创建 `.env` 文件（或设置环境变量）:

```bash
# .env 文件内容
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=image_segment_platform
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_CHARSET=utf8mb4
MYSQL_POOL_SIZE=10
MYSQL_MAX_OVERFLOW=20
MYSQL_POOL_RECYCLE=3600
MYSQL_POOL_TIMEOUT=30
MYSQL_ECHO=false
```

---

## ✅ 验证安装

### 1. 检查表是否创建成功

```sql
-- 查看所有表
SHOW TABLES;

-- 查看表的详细信息
SELECT 
    TABLE_NAME AS '表名',
    TABLE_COMMENT AS '表注释',
    TABLE_ROWS AS '记录数',
    CREATE_TIME AS '创建时间'
FROM 
    INFORMATION_SCHEMA.TABLES 
WHERE 
    TABLE_SCHEMA = 'image_segment_platform'
ORDER BY 
    TABLE_NAME;
```

**预期输出**:
```
+-----------------------+--------------------------+-----------+---------------------+
| 表名                   | 表注释                    | 记录数     | 创建时间             |
+-----------------------+--------------------------+-----------+---------------------+
| augmentation_records  | 数据增强记录表            | 0         | 2026-04-23 10:00:00 |
| augmentation_results  | 数据增强结果表            | 0         | 2026-04-23 10:00:00 |
| dataset_images        | 数据集图像表              | 0         | 2026-04-23 10:00:00 |
| datasets              | 数据集表                  | 0         | 2026-04-23 10:00:00 |
| models                | 模型管理表                | 1         | 2026-04-23 10:00:00 |
| operation_logs        | 操作日志表                | 0         | 2026-04-23 10:00:00 |
| segmentation_records  | 图像分割记录表            | 0         | 2026-04-23 10:00:00 |
| users                 | 用户表                    | 1         | 2026-04-23 10:00:00 |
+-----------------------+--------------------------+-----------+---------------------+
```

### 2. 检查外键约束

```sql
-- 查看外键约束
SELECT 
    TABLE_NAME AS '表名',
    CONSTRAINT_NAME AS '约束名',
    REFERENCED_TABLE_NAME AS '关联表'
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE 
    TABLE_SCHEMA = 'image_segment_platform'
    AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY 
    TABLE_NAME;
```

### 3. 检查索引

```sql
-- 查看索引
SHOW INDEX FROM segmentation_records;
SHOW INDEX FROM augmentation_records;
SHOW INDEX FROM dataset_images;
```

---

## 🔧 常见问题

### Q1: 外键约束错误

**问题**: `ERROR 1215 (HY000): Cannot add foreign key constraint`

**解决方案**:
```sql
-- 1. 确保表的创建顺序正确
-- 2. 确保被引用的表已存在
-- 3. 确保字段类型匹配（BIGINT 对 BIGINT）
-- 4. 确保字符集一致
```

### Q2: 字符集错误

**问题**: `ERROR 1071 (42000): Specified key was too long`

**解决方案**:
```sql
-- 使用 utf8mb4 字符集
ALTER DATABASE image_segment_platform 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### Q3: JSON字段不支持

**问题**: `ERROR 1064 (42000): You have an error in your SQL syntax`

**解决方案**:
```sql
-- MySQL 5.7.8+ 才支持 JSON 类型
-- 检查MySQL版本
SELECT VERSION();

-- 如果版本较低，可以将 JSON 改为 TEXT
-- 例如: supported_types JSON -> supported_types TEXT
```

### Q4: 删除表时外键约束错误

**问题**: `ERROR 1451 (23000): Cannot delete or update a parent row`

**解决方案**:
```sql
-- 临时禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- 删除所有表
DROP TABLE IF EXISTS operation_logs;
DROP TABLE IF EXISTS dataset_images;
DROP TABLE IF EXISTS datasets;
DROP TABLE IF EXISTS augmentation_results;
DROP TABLE IF EXISTS augmentation_records;
DROP TABLE IF EXISTS segmentation_records;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS users;

-- 重新启用水键检查
SET FOREIGN_KEY_CHECKS = 1;
```

---

## 🔐 默认账户信息

**默认管理员账户** (需修改密码):

```sql
-- 用户名: admin
-- 初始密码: admin123 (示例，实际需要生成哈希)
-- 角色: admin
```

**修改密码步骤**:

```python
# 在Python中生成密码哈希
import hashlib
import secrets

# 生成随机盐值
salt = secrets.token_hex(32)

# 生成密码哈希 (实际项目应使用 bcrypt 或 werkzeug.security)
password = "your_new_password"
password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)

# 更新数据库
UPDATE users 
SET password_hash = '<new_hash>', salt = '<new_salt>' 
WHERE username = 'admin';
```

---

## 📊 性能优化建议

### 1. 索引优化

```sql
-- 为常用查询添加复合索引
CREATE INDEX idx_user_created ON segmentation_records(user_id, created_at);
CREATE INDEX idx_model_created ON segmentation_records(model_id, created_at);
CREATE INDEX idx_dataset_status ON dataset_images(dataset_id, annotation_status);
```

### 2. 分区策略（大数据量）

```sql
-- 按时间分区（适用于日志表）
ALTER TABLE operation_logs 
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);
```

### 3. 字段优化建议

对于存储大量Base64图片的LONGTEXT字段:
- 考虑使用文件存储（OSS/NFS）+ 数据库存储路径
- 或考虑使用压缩算法减少存储空间

---

## 🔄 数据迁移

如果已有数据需要迁移，请参考:

1. `001_add_segmentation_fields.sql` - 为分割记录表添加字段
2. `002_create_augmentation_results.sql` - 创建增强结果表
3. `003_add_model_version_fields.sql` - 为模型表添加版本字段
4. `004_create_dataset_tables.sql` - 创建数据集相关表

执行迁移前请务必备份数据！

---

## 📝 SQL脚本文件说明

```
src/web/backend/database/migrations/
├── 000_create_all_tables.sql         # 完整建表脚本（本文件）
├── 001_add_segmentation_fields.sql   # 迁移脚本:添加分割字段
├── 002_create_augmentation_results.sql # 迁移脚本:创建增强结果表
├── 003_add_model_version_fields.sql  # 迁移脚本:添加版本字段
└── 004_create_dataset_tables.sql     # 迁移脚本:创建数据集表
```

---

## 🛠️ 维护命令

```sql
-- 查看表大小
SELECT 
    TABLE_NAME AS '表名',
    ROUND(DATA_LENGTH/1024/1024, 2) AS '数据大小(MB)',
    ROUND(INDEX_LENGTH/1024/1024, 2) AS '索引大小(MB)',
    TABLE_ROWS AS '记录数'
FROM 
    INFORMATION_SCHEMA.TABLES
WHERE 
    TABLE_SCHEMA = 'image_segment_platform'
ORDER BY 
    DATA_LENGTH DESC;

-- 优化表
OPTIMIZE TABLE segmentation_records;
OPTIMIZE TABLE augmentation_records;

-- 分析表
ANALYZE TABLE segmentation_records;

-- 检查表
CHECK TABLE segmentation_records;
```

---

## 📖 参考资料

- [MySQL 8.0 参考手册](https://dev.mysql.com/doc/refman/8.0/en/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- 项目数据库设计文档: `openspec/changes/database-schema-review/design.md`

---

## ✉️ 联系支持

如有问题，请联系开发团队或提交Issue。

**生成时间**: 2026-04-23  
**版本**: v1.0.0
