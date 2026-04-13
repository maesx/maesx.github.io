# MySQL数据库接入指南

> 本文档介绍如何将图像分割平台从内存存储迁移到MySQL数据库存储

## 📋 目录

- [准备工作](#准备工作)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [初始化数据库](#初始化数据库)
- [数据迁移](#数据迁移)
- [验证测试](#验证测试)
- [常见问题](#常见问题)

---

## 准备工作

### 1. 环境要求

- Python 3.8+
- MySQL 8.0+
- 已安装的Python包:
  - `pymysql`
  - `sqlalchemy`

### 2. 安装依赖

```bash
pip install pymysql sqlalchemy
```

### 3. 准备MySQL数据库

确保MySQL服务正在运行，并且您有创建数据库的权限。

---

## 快速开始

### 1. 复制配置文件

```bash
cp .env.mysql.example .env
```

### 2. 修改配置

编辑 `.env` 文件，修改MySQL连接信息：

```bash
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=image_segment_platform
MYSQL_USER=root
MYSQL_PASSWORD=your_password
```

### 3. 初始化数据库

**方法A: 使用Python脚本（推荐）**

```bash
python scripts/init_database.py
```

**方法B: 使用SQL脚本**

```bash
mysql -u root -p < scripts/init_database.sql
```

### 4. 重启应用

```bash
python src/web/backend/app.py
```

---

## 配置说明

### 环境变量详解

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `USE_MYSQL` | 是否启用MySQL | `false` | 是 |
| `MYSQL_HOST` | MySQL服务器地址 | `localhost` | 是 |
| `MYSQL_PORT` | MySQL服务器端口 | `3306` | 是 |
| `MYSQL_DATABASE` | 数据库名称 | `image_segment_platform` | 是 |
| `MYSQL_USER` | 数据库用户名 | `root` | 是 |
| `MYSQL_PASSWORD` | 数据库密码 | - | 是 |
| `MYSQL_CHARSET` | 字符集 | `utf8mb4` | 否 |
| `MYSQL_POOL_SIZE` | 连接池大小 | `10` | 否 |
| `MYSQL_MAX_OVERFLOW` | 最大溢出连接数 | `20` | 否 |
| `MYSQL_POOL_RECYCLE` | 连接回收时间(秒) | `3600` | 否 |
| `MYSQL_POOL_TIMEOUT` | 获取连接超时(秒) | `30` | 否 |
| `MYSQL_ECHO` | 是否打印SQL语句 | `false` | 否 |

### 连接池配置建议

| 场景 | Pool Size | Max Overflow | 说明 |
|------|-----------|--------------|------|
| 开发环境 | 5 | 10 | 低并发 |
| 测试环境 | 10 | 20 | 中等并发 |
| 生产环境（小规模） | 20 | 40 | 100用户以下 |
| 生产环境（大规模） | 50 | 100 | 100用户以上 |

---

## 初始化数据库

### 使用Python脚本初始化（推荐）

```bash
python scripts/init_database.py
```

**脚本功能**:
- ✅ 创建数据库引擎和连接池
- ✅ 创建所有数据表
- ✅ 插入默认管理员账户（用户名: `admin`, 密码: `admin123`）
- ✅ 插入默认模型记录
- ✅ 验证数据表创建成功

**输出示例**:
```
INFO: 正在初始化数据库引擎...
INFO: MySQL数据库引擎初始化成功 - Host: localhost:3306, Database: image_segment_platform, Pool Size: 10
INFO: 正在创建数据表...
INFO: 数据表创建成功
INFO: 正在创建默认管理员账户...
INFO: ✅ 默认管理员账户创建成功
INFO:    用户名: admin
INFO:    密码: admin123
INFO: ⚠️  请及时修改默认密码！
INFO: ✅ MySQL数据库初始化完成
```

### 使用SQL脚本初始化

```bash
# 方式1: 直接执行SQL文件
mysql -u root -p < scripts/init_database.sql

# 方式2: 登录MySQL后执行
mysql -u root -p
mysql> source scripts/init_database.sql;
```

---

## 数据迁移

### 导出现有数据

如果系统中已有数据，可以使用导出工具：

```bash
python scripts/database_tool.py --export --output ./backups
```

**输出内容**:
- `users.json` - 用户数据
- `models.json` - 模型数据
- `segmentation_records.json` - 分割记录（不含图片）
- `augmentation_records.json` - 增强记录（不含图片）
- `operation_logs.json` - 操作日志

### 导入数据（开发中）

```bash
python scripts/database_tool.py --import ./backups/backup_xxx/users.json
```

---

## 验证测试

### 1. 检查数据库连接

```python
from backend.database.session import get_db, init_database
from backend.config.database import db_config

# 初始化数据库
init_database()

# 测试连接
db = get_db()
print("数据库连接成功" if db else "数据库连接失败")
```

### 2. 查询数据

```python
from backend.database.session import get_db_session
from backend.database.models import User

with get_db_session() as db:
    if db:
        users = db.query(User).all()
        print(f"用户数量: {len(users)}")
```

### 3. 插入测试数据

```python
from backend.database.session import get_db_session
from backend.database.models import User
from hashlib import sha256
import secrets

with get_db_session() as db:
    if db:
        # 创建测试用户
        password = 'test123'
        salt = secrets.token_hex(32)
        password_hash = sha256((password + salt).encode()).hexdigest()
        
        user = User(
            username='test_user',
            email='test@example.com',
            password_hash=password_hash,
            salt=salt
        )
        
        db.add(user)
        print("用户创建成功")
```

---

## 常见问题

### Q1: 连接失败 "Can't connect to MySQL server"

**原因**: MySQL服务未启动或连接配置错误

**解决方案**:
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 启动MySQL服务
sudo systemctl start mysql

# 验证连接配置
mysql -h localhost -P 3306 -u root -p
```

### Q2: 数据库不存在

**原因**: 数据库未创建

**解决方案**:
```bash
# 手动创建数据库
mysql -u root -p -e "CREATE DATABASE image_segment_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 或运行初始化脚本
python scripts/init_database.py
```

### Q3: 字符集错误

**原因**: 数据库或表字符集配置错误

**解决方案**:
```sql
-- 修改数据库字符集
ALTER DATABASE image_segment_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改表字符集
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Q4: 内存存储和MySQL存储冲突

**原因**: 系统同时启用了两种存储方式

**解决方案**:
- 系统设计为**互斥模式**
- 当 `USE_MYSQL=true` 时，自动使用MySQL
- 当 `USE_MYSQL=false` 时，自动使用内存存储
- 不会产生冲突

### Q5: 图片存储过大导致性能问题

**原因**: Base64编码会增大约33%的体积

**解决方案**:
1. **短期**: 使用连接池优化查询性能
2. **长期**: 考虑使用OSS存储图片，MySQL只存URL

### Q6: 忘记管理员密码

**解决方案**:
```bash
# 重新运行初始化脚本（会重置所有数据）
python scripts/init_database.py

# 或手动重置密码（需要Python代码）
from backend.database.session import get_db_session
from backend.database.models import User
from hashlib import sha256
import secrets

with get_db_session() as db:
    if db:
        admin = db.query(User).filter(User.username == 'admin').first()
        if admin:
            new_password = 'new_password'
            admin.salt = secrets.token_hex(32)
            admin.password_hash = sha256((new_password + admin.salt).encode()).hexdigest()
            print("密码重置成功")
```

---

## 性能优化建议

### 1. 连接池优化

根据实际并发量调整连接池参数：

```bash
MYSQL_POOL_SIZE=20
MYSQL_MAX_OVERFLOW=40
MYSQL_POOL_RECYCLE=3600
```

### 2. 查询优化

- 使用索引字段查询
- 避免全表扫描
- 分页查询大数据集

### 3. 图片存储优化

对于大量图片数据：
- 考虑压缩图片后再存储
- 使用CDN加速图片加载
- 定期清理历史数据

---

## 安全建议

1. **修改默认密码**: 首次登录后立即修改admin密码
2. **使用强密码**: 数据库密码至少12位，包含大小写字母、数字、特殊字符
3. **限制数据库访问**: 只允许应用服务器访问数据库
4. **定期备份**: 使用 `database_tool.py --export` 定期备份数据
5. **监控日志**: 关注 `operation_logs` 表中的异常操作

---

## 下一步

- [ ] 启用MySQL数据库（设置 `USE_MYSQL=true`）
- [ ] 运行初始化脚本
- [ ] 修改默认管理员密码
- [ ] 配置定期备份
- [ ] 监控系统性能

---

## 技术支持

如有问题，请检查：
1. MySQL服务状态
2. 配置文件 `.env` 是否正确
3. 网络连接是否正常
4. 日志文件中的错误信息

---

**祝您使用愉快！** 🎉
