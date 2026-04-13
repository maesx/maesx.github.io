## ADDED Requirements

### Requirement: CORS 配置限制

系统 SHALL 限制 CORS 配置，仅允许可信来源访问 API。

#### Scenario: 允许的来源访问
- **WHEN** 请求来自配置的允许来源（如 https://example.com）
- **THEN** 系统正常处理请求并返回正确的 CORS 头

#### Scenario: 未授权来源访问
- **WHEN** 请求来自未配置的来源
- **THEN** 系统拒绝请求或返回空 CORS 头

#### Scenario: 开发环境宽松 CORS
- **WHEN** 系统运行在开发环境（DEBUG=True）
- **THEN** 允许 localhost 来源访问

#### Scenario: 生产环境严格 CORS
- **WHEN** 系统运行在生产环境
- **THEN** 仅允许 CORS_ALLOWED_ORIGINS 配置的来源

### Requirement: API 速率限制

系统 SHALL 实现全局和端点级别的 API 速率限制。

#### Scenario: 全局速率限制
- **WHEN** 同一 IP 在 1 分钟内请求超过 100 次
- **THEN** 系统返回 429 错误并提示稍后重试

#### Scenario: 敏感端点速率限制
- **WHEN** 同一 IP 在 1 分钟内调用 /api/segment 超过 20 次
- **THEN** 系统返回 429 错误

#### Scenario: 登录端点严格限制
- **WHEN** 同一 IP 在 1 分钟内登录失败超过 5 次
- **THEN** 系统拒绝该 IP 的登录请求 15 分钟

#### Scenario: 速率限制响应头
- **WHEN** 系统返回速率限制错误
- **THEN** 响应头包含 X-RateLimit-Limit 和 X-RateLimit-Remaining

### Requirement: 输入验证

系统 SHALL 对所有 API 输入参数进行验证。

#### Scenario: 模型名称参数验证
- **WHEN** 请求包含包含路径遍历字符的 model_name 参数（如 ../config）
- **THEN** 系统拒绝请求并返回 400 错误

#### Scenario: 必填参数缺失
- **WHEN** 请求缺少必填参数（如上传文件时缺少 file）
- **THEN** 系统返回 400 错误和参数缺失提示

#### Scenario: 参数类型验证
- **WHEN** 请求参数类型不正确（如 num_samples 应为整数但传入字符串）
- **THEN** 系统返回 400 错误和类型错误提示

### Requirement: 错误响应安全

系统 SHALL 在错误响应中隐藏敏感信息。

#### Scenario: 生产环境错误响应
- **WHEN** 生产环境发生内部错误
- **THEN** 系统返回通用错误信息，不包含堆栈跟踪和路径

#### Scenario: 开发环境错误响应
- **WHEN** 开发环境发生内部错误
- **THEN** 系统返回详细错误信息便于调试

#### Scenario: 错误日志记录
- **WHEN** 系统发生错误
- **THEN** 详细错误信息记录到日志文件，不返回给客户端

### Requirement: 安全响应头

系统 SHALL 为所有响应添加安全相关的 HTTP 头。

#### Scenario: X-Content-Type-Options 头
- **WHEN** 系统返回任何响应
- **THEN** 响应头包含 X-Content-Type-Options: nosniff

#### Scenario: X-Frame-Options 头
- **WHEN** 系统返回任何响应
- **THEN** 响应头包含 X-Frame-Options: DENY

#### Scenario: Content-Security-Policy 头
- **WHEN** 系统返回 HTML 响应
- **THEN** 响应头包含适当的 Content-Security-Policy

### Requirement: DEBUG 模式控制

系统 SHALL 根据环境自动控制 DEBUG 模式。

#### Scenario: 生产环境 DEBUG 关闭
- **WHEN** FLASK_ENV=production 或 FLASK_DEBUG=False
- **THEN** 系统禁用 DEBUG 模式

#### Scenario: DEBUG 模式警告
- **WHEN** 生产环境启用 DEBUG 模式
- **THEN** 系统输出严重警告日志