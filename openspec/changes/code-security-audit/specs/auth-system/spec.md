## ADDED Requirements

### Requirement: 用户登录认证

系统 SHALL 提供基于 JWT 的用户登录认证功能，验证用户凭据后签发有效 token。

#### Scenario: 有效凭据登录成功
- **WHEN** 用户提交有效的用户名和密码
- **THEN** 系统返回 JWT token 和用户信息

#### Scenario: 无效凭据登录失败
- **WHEN** 用户提交无效的用户名或密码
- **THEN** 系统返回 401 错误和错误信息

#### Scenario: 登录请求速率限制
- **WHEN** 同一 IP 在 1 分钟内登录失败超过 5 次
- **THEN** 系统拒绝该 IP 的登录请求 15 分钟

### Requirement: Token 验证中间件

系统 SHALL 提供 API 认证中间件，验证请求中的 JWT token 有效性。

#### Scenario: 有效 token 访问受保护 API
- **WHEN** 请求携带有效的 Authorization header (Bearer token)
- **THEN** 系统允许访问并返回正常响应

#### Scenario: 无效 token 访问受保护 API
- **WHEN** 请求携带无效或过期的 token
- **THEN** 系统返回 401 错误

#### Scenario: 缺少 token 访问受保护 API
- **WHEN** 请求未携带 Authorization header
- **THEN** 系统返回 401 错误

### Requirement: 敏感操作保护

系统 SHALL 对敏感 API 端点实施认证保护。

#### Scenario: 未认证用户删除模型
- **WHEN** 未认证用户请求 DELETE /api/models/<model_name>
- **THEN** 系统返回 401 错误，拒绝删除

#### Scenario: 已认证用户删除模型
- **WHEN** 已认证用户请求 DELETE /api/models/<model_name>
- **THEN** 系统验证权限后执行删除

#### Scenario: 公开 API 无需认证
- **WHEN** 用户访问 /api/health 或 /api/models (GET)
- **THEN** 系统无需认证即可访问

### Requirement: Token 刷新机制

系统 SHALL 提供 token 刷新机制，允许用户在 token 过期前获取新 token。

#### Scenario: 有效刷新 token
- **WHEN** 用户提交有效的刷新请求（token 未过期）
- **THEN** 系统签发新的 access token

#### Scenario: 过期 token 刷新失败
- **WHEN** 用户提交已过期的 token 进行刷新
- **THEN** 系统返回 401 错误，要求重新登录

### Requirement: 安全配置管理

系统 SHALL 通过环境变量管理敏感配置，不硬编码任何密钥。

#### Scenario: 生产环境缺少 SECRET_KEY
- **WHEN** 生产环境未设置 SECRET_KEY 环境变量
- **THEN** 系统拒绝启动并输出错误日志

#### Scenario: 开发环境使用默认 SECRET_KEY
- **WHEN** 开发环境未设置 SECRET_KEY 环境变量
- **THEN** 系统使用开发专用默认值并输出警告日志

#### Scenario: SECRET_KEY 强度验证
- **WHEN** 配置的 SECRET_KEY 少于 32 个字符
- **THEN** 系统输出警告日志提示密钥强度不足