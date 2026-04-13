## 1. 紧急安全修复

- [x] 1.1 修复 `torch.load` 的 `weights_only=False` 问题
  - `src/web/backend/routes/models.py:160`
  - `src/web/backend/services/model_service.py:67,133`
  - `src/inference/inference.py:51`
  - `src/training/train.py:208`
- [x] 1.2 设置安全的 SECRET_KEY 配置检查
  - 修改 `src/web/backend/config.py`
  - 生产环境强制要求环境变量
- [x] 1.3 关闭生产环境 DEBUG 模式默认值
  - 修改 `src/web/backend/config.py`

## 2. JWT 认证系统实现

- [ ] 2.1 添加认证相关依赖
  - 更新 `src/web/requirements.txt`：PyJWT、Flask-JWT-Extended
- [ ] 2.2 创建认证模块 `src/web/backend/auth/`
  - `auth/jwt_handler.py`：JWT 签发和验证
  - `auth/decorators.py`：认证装饰器
- [ ] 2.3 实现用户登录接口
  - 修改 `src/web/backend/routes/auth.py`
  - 实现真实的凭据验证
  - 返回有效的 JWT token
- [ ] 2.4 实现 Token 验证中间件
  - 创建 `src/web/backend/middleware/auth_middleware.py`
  - 实现 `@require_auth` 装饰器
- [ ] 2.5 保护敏感 API 端点
  - 修改 `src/web/backend/routes/models.py`：保护 DELETE 端点
  - 修改 `src/web/backend/routes/segment.py`：保护上传端点（可选）
- [ ] 2.6 实现 Token 刷新机制
  - 添加 `/api/auth/refresh` 端点

## 3. API 安全加固

- [ ] 3.1 配置 CORS 白名单
  - 修改 `src/web/backend/app.py`
  - 添加 `CORS_ALLOWED_ORIGINS` 配置项
  - 开发/生产环境区分配置
- [ ] 3.2 实现速率限制
  - 添加 Flask-Limiter 依赖
  - 配置全局速率限制（100次/分钟）
  - 配置敏感端点限制（/api/segment: 20次/分钟）
  - 配置登录端点限制（5次失败/分钟）
- [ ] 3.3 增强输入验证
  - 创建 `src/web/backend/utils/validators.py`
  - 实现模型名称验证（防止路径遍历）
  - 实现参数类型验证
- [ ] 3.4 优化错误响应
  - 创建 `src/web/backend/utils/error_handler.py`
  - 生产环境隐藏敏感信息
  - 统一错误响应格式
- [ ] 3.5 添加安全响应头
  - 添加 X-Content-Type-Options
  - 添加 X-Frame-Options
  - 添加 Content-Security-Policy

## 4. 文件上传安全增强

- [ ] 4.1 添加文件验证依赖
  - 更新 `src/web/requirements.txt`：python-magic
- [ ] 4.2 实现 Magic number 验证
  - 创建 `src/web/backend/utils/file_validator.py`
  - 验证图片文件真实类型
  - 验证模型文件类型
- [ ] 4.3 实现文件名安全处理
  - 使用 UUID 重命名上传文件
  - 记录原始文件名
- [ ] 4.4 添加文件大小限制
  - 图片文件：50MB
  - 模型文件：500MB
- [ ] 4.5 配置上传目录安全
  - 设置目录权限
  - 禁止脚本执行
- [ ] 4.6 更新文件上传接口
  - 修改 `src/web/backend/routes/segment.py`
  - 修改 `src/web/backend/routes/models.py`

## 5. 敏感信息清理

- [ ] 5.1 移除 API 响应中的敏感路径
  - 修改 `src/web/backend/routes/models.py`：移除 path 字段
  - 修改 `src/web/backend/routes/segment.py`：移除 save_path 字段
- [ ] 5.2 移除调试打印语句
  - 清理 `src/web/backend/routes/segment.py` 中的 print 语句
- [ ] 5.3 配置日志脱敏
  - 创建 `src/web/backend/utils/log_filter.py`
  - 过滤敏感信息

## 6. 依赖更新

- [ ] 6.1 更新存在漏洞的依赖
  - Flask >= 2.3.3 → 最新安全版本
  - Pillow >= 10.0.0 → 最新安全版本
  - werkzeug >= 2.3.7 → 最新安全版本
- [ ] 6.2 测试兼容性
  - 运行现有测试套件
  - 手动测试关键功能

## 7. 文档更新

- [ ] 7.1 创建安全审查报告文档
  - 创建 `docs/security_audit_report.md`
  - 记录所有发现的漏洞
  - 记录修复措施
- [ ] 7.2 更新部署文档
  - 添加环境变量配置说明
  - 添加安全配置检查清单
- [ ] 7.3 更新 API 文档
  - 添加认证相关接口说明
  - 添加错误码说明

## 8. 测试验证

- [ ] 8.1 编写安全测试用例
  - 认证测试
  - 文件上传测试
  - API 安全测试
- [ ] 8.2 执行渗透测试
  - 使用安全工具扫描
  - 手动测试关键漏洞点
- [ ] 8.3 验证修复效果
  - 确认所有漏洞已修复
  - 确认功能正常