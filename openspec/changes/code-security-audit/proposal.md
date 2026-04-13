## Why

项目当前存在多个安全漏洞，包括无效的认证系统、不安全的模型文件加载、敏感信息泄露等问题。这些漏洞在生产环境中可能导致远程代码执行、数据泄露、拒绝服务等严重安全事件。在项目正式部署前进行全面的安全审查和修复是必要的。

## What Changes

- **[严重]** 实现真正的认证系统，替换当前的虚假认证
- **[严重]** 添加 API 认证中间件，保护所有敏感端点
- **[高危]** 修复 PyTorch 模型文件不安全加载问题（远程代码执行风险）
- **[高危]** 设置安全的 SECRET_KEY，移除硬编码默认值
- **[高危]** 限制 CORS 配置，仅允许可信来源
- **[高危]** 为模型删除接口添加认证保护
- **[中危]** 增强文件上传验证（Magic number 检查）
- **[中危]** 实现 API 速率限制防止滥用
- **[中危]** 移除 API 响应中的敏感路径信息
- **[中危]** 生产环境默认关闭 DEBUG 模式
- **[中危]** 更新存在已知漏洞的依赖版本
- **[中危]** 添加文件上传大小和数量限制
- **[低危]** 添加安全响应头
- **[低危]** 移除调试打印语句

## Capabilities

### New Capabilities

- `auth-system`: JWT 认证系统实现，包括用户登录、token 验证、API 保护中间件
- `file-upload-security`: 文件上传安全增强，包括 Magic number 验证、文件大小限制、唯一命名
- `api-security`: API 安全加固，包括速率限制、输入验证、错误处理优化
- `model-security`: 模型文件安全加载机制，使用 safetensors 或 weights_only=True

### Modified Capabilities

无现有 specs 需要修改。

## Impact

- **后端代码**：`src/web/backend/` 下所有路由和服务文件
- **配置文件**：`src/web/backend/config.py` 安全配置更新
- **依赖文件**：`src/web/requirements.txt` 版本更新
- **推理模块**：`src/inference/inference.py` 模型加载方式
- **训练模块**：`src/training/train.py` 模型加载方式
- **前端 API**：`src/web/frontend/src/api/index.js` 认证集成