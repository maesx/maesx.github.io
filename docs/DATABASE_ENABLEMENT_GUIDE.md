# 图像分割数据库启用指南

## 📊 功能说明

本项目已完整实现图像分割历史记录的数据库存储功能,支持MySQL数据库和内存存储双模式运行。

### ✅ 已实现的功能

| 功能模块 | 数据库支持 | 内存后备 | 状态 |
|---------|-----------|---------|------|
| **用户注册** | ✅ | ❌ | 已启用 |
| **用户登录** | ⚠️ 演示模式 | ✅ | 已启用 |
| **模型管理** | ✅ | ✅ | 已启用 |
| **图像分割** | ✅ | ✅ | 已启用 |
| **分割历史** | ✅ | ✅ | 已启用 |
| **数据增强** | ✅ | ✅ | 已启用 |
| **结果对比** | ❌ | ✅ | 待实现 |

---

## 🚀 快速开始

### 方案一:使用MySQL数据库(推荐)

#### 1. 创建配置文件

```bash
# 复制示例配置
cp .env.mysql.example .env

# 编辑 .env 文件
nano .env
```

#### 2. 配置数据库连接

```bash
# .env 文件内容
USE_MYSQL=true

# MySQL连接配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=image_segment_platform
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_CHARSET=utf8mb4

# 连接池配置
MYSQL_POOL_SIZE=10
MYSQL_MAX_OVERFLOW=20
MYSQL_POOL_RECYCLE=3600
MYSQL_POOL_TIMEOUT=30

# 调试配置
MYSQL_ECHO=false
```

#### 3. 创建数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE image_segment_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 授予权限(如需要)
GRANT ALL PRIVILEGES ON image_segment_platform.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

# 退出
EXIT;
```

#### 4. 初始化数据表

```bash
# 运行表创建脚本
python3 scripts/create_segmentation_tables.py
```

#### 5. 重启服务

```bash
# 重启Flask服务
python start_server.py
```

### 方案二:使用内存存储(默认)

无需任何配置,系统会自动使用内存存储模式。

**特点**:
- ✅ 零配置开箱即用
- ✅ 适合开发和演示
- ⚠️ 数据不持久化
- ⚠️ 重启后历史记录丢失
- ⚠️ 仅保留最近50条记录

---

## 📋 数据表结构

### `segmentation_records` (分割记录表)

```sql
CREATE TABLE segmentation_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id BIGINT COMMENT '用户ID',
    model_id BIGINT COMMENT '模型ID',
    original_image LONGTEXT NOT NULL COMMENT '原图(Base64编码)',
    result_image LONGTEXT NOT NULL COMMENT '分割结果图(Base64编码)',
    segment_type ENUM('semantic', 'instance') NOT NULL COMMENT '分割类型',
    image_width INT COMMENT '图像宽度',
    image_height INT COMMENT '图像高度',
    image_format VARCHAR(10) COMMENT '图像格式',
    file_size BIGINT COMMENT '文件大小(字节)',
    processing_time FLOAT COMMENT '处理耗时(秒)',
    iou_score FLOAT COMMENT 'IoU得分',
    accuracy FLOAT COMMENT '准确率',
    additional_metrics JSON COMMENT '其他评估指标',
    status SMALLINT DEFAULT 1 COMMENT '状态(1=成功, 0=失败)',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_model_id (model_id),
    INDEX idx_created_at (created_at),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图像分割记录表';
```

### `users` (用户表)

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    nickname VARCHAR(100),
    role ENUM('admin', 'user') DEFAULT 'user',
    status SMALLINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### `models` (模型表)

```sql
CREATE TABLE models (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20),
    path VARCHAR(500),
    metrics JSON COMMENT '模型评估指标',
    status SMALLINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型表';
```

---

## 🔧 技术实现

### 数据库存储流程

```
图像分割请求
    ↓
执行分割处理
    ↓
生成分割结果
    ↓
保存到文件系统 (outputs/results/)
    ↓
尝试保存到MySQL数据库
    ├─ 成功 → 持久化存储 ✅
    └─ 失败 → 内存后备存储 ⚠️
```

### 代码实现位置

| 文件 | 功能 | 行数 |
|------|------|------|
| `src/web/backend/routes/segment.py` | 分割路由和数据库存储 | 695-840 |
| `src/web/backend/database/models/segmentation.py` | 分割记录模型 | 1-80 |
| `src/web/backend/database/session.py` | 数据库会话管理 | 1-199 |
| `src/web/backend/config/database.py` | 数据库配置 | 1-100 |
| `scripts/create_segmentation_tables.py` | 表创建脚本 | 1-128 |

---

## 📊 性能优化

### 数据库优化

1. **索引优化**
   - `created_at`: 时间查询优化
   - `user_id`: 用户关联查询优化
   - `model_id`: 模型关联查询优化

2. **查询优化**
   - 使用 `ORDER BY created_at DESC` 按时间倒序
   - 限制返回记录数: `LIMIT 50`
   - 避免全表扫描

3. **连接池优化**
   - 池大小: 10
   - 最大溢出: 20
   - 连接回收: 3600秒
   - 连接超时: 30秒

---

## 🐛 故障排查

### 问题1: 数据库连接失败

**症状**:
```
[WARNING] 保存到数据库失败: Can't connect to MySQL server
```

**解决方案**:
```bash
# 1. 检查MySQL是否运行
sudo systemctl status mysql

# 2. 检查配置文件
cat .env

# 3. 测试连接
mysql -h localhost -u root -p image_segment_platform
```

### 问题2: 表不存在

**症状**:
```
[WARNING] 从数据库获取历史记录失败: Table 'image_segment_platform.segmentation_records' doesn't exist
```

**解决方案**:
```bash
# 运行表创建脚本
python3 scripts/create_segmentation_tables.py
```

### 问题3: 权限问题

**症状**:
```
[WARNING] 保存到数据库失败: Access denied for user 'root'@'localhost'
```

**解决方案**:
```sql
-- 授予权限
GRANT ALL PRIVILEGES ON image_segment_platform.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

---

## 📈 数据统计

### 查询统计数据

```python
from src.web.backend.database.session import get_db_session
from src.web.backend.database.models.segmentation import SegmentationRecord
from sqlalchemy import func

with get_db_session() as session:
    if session:
        # 总记录数
        total = session.query(func.count(SegmentationRecord.id)).scalar()
        
        # 今日记录数
        from datetime import datetime, timedelta
        today = datetime.now().date()
        today_count = session.query(func.count(SegmentationRecord.id))\
            .filter(func.date(SegmentationRecord.created_at) == today)\
            .scalar()
        
        # 平均IoU
        avg_iou = session.query(func.avg(SegmentationRecord.iou_score))\
            .filter(SegmentationRecord.iou_score.isnot(None))\
            .scalar()
        
        print(f"总记录数: {total}")
        print(f"今日新增: {today_count}")
        print(f"平均IoU: {avg_iou:.4f}")
```

---

## 🎯 最佳实践

### 开发环境
- ✅ 使用内存存储,快速启动
- ✅ 无需配置MySQL
- ✅ 适合功能开发和测试

### 生产环境
- ✅ 使用MySQL数据库
- ✅ 配置连接池优化性能
- ✅ 定期备份数据库
- ✅ 监控数据库性能

### 数据迁移
```bash
# 导出数据
mysqldump -u root -p image_segment_platform > backup.sql

# 导入数据
mysql -u root -p image_segment_platform < backup.sql
```

---

## 📝 更新日志

### v1.0.0 (2026-04-30)
- ✅ 实现图像分割历史记录数据库存储
- ✅ 支持MySQL和内存双模式
- ✅ 历史记录容量从10条扩展到50条
- ✅ 添加数据库表创建脚本
- ✅ 完善错误处理和日志输出

---

## 📚 相关文档

- [数据库配置文档](./DATABASE_CONFIG.md)
- [API文档](./API_REFERENCE.md)
- [部署指南](./DEPLOYMENT.md)

---

## 💡 技术支持

如有问题,请查看:
1. 项目日志文件: `logs/`
2. 数据库日志: MySQL错误日志
3. Flask日志: 控制台输出
