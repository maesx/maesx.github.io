## ADDED Requirements

### Requirement: 安全模型加载

系统 SHALL 使用安全的模型文件加载方式，防止恶意代码执行。

#### Scenario: 使用 weights_only=True 加载模型
- **WHEN** 系统加载 .pth 模型文件
- **THEN** 使用 torch.load(..., weights_only=True) 参数

#### Scenario: 拒绝不安全加载方式
- **WHEN** 代码尝试使用 weights_only=False 加载模型
- **THEN** 系统抛出安全警告或拒绝加载

#### Scenario: 加载失败处理
- **WHEN** 模型文件加载失败（格式不兼容或损坏）
- **THEN** 系统返回友好错误信息，不暴露内部路径

### Requirement: 模型文件验证

系统 SHALL 在加载前验证模型文件的完整性。

#### Scenario: 模型文件签名验证
- **WHEN** 加载受信任的模型文件
- **THEN** 系统验证文件签名或哈希值

#### Scenario: 未验证模型警告
- **WHEN** 加载未签名的模型文件
- **THEN** 系统输出警告日志

#### Scenario: 模型文件大小检查
- **WHEN** 模型文件大小异常（过大或过小）
- **THEN** 系统拒绝加载并输出警告

### Requirement: 模型上传安全

系统 SHALL 对用户上传的模型文件实施安全检查。

#### Scenario: 模型文件类型验证
- **WHEN** 用户上传模型文件
- **THEN** 系统验证文件扩展名为 .pth 或 .pt

#### Scenario: 恶意模型文件检测
- **WHEN** 用户上传包含可疑代码的模型文件
- **THEN** weights_only=True 加载方式阻止代码执行

#### Scenario: 模型上传认证
- **WHEN** 用户上传模型文件
- **THEN** 系统要求用户已认证

### Requirement: 模型存储安全

系统 SHALL 安全存储模型文件，防止未授权访问。

#### Scenario: 模型目录权限
- **WHEN** 系统创建模型存储目录
- **THEN** 目录权限设置为仅应用用户可读写

#### Scenario: 模型文件访问控制
- **WHEN** 请求访问模型文件
- **THEN** 通过 API 端点控制访问，不直接暴露文件路径

#### Scenario: 模型删除保护
- **WHEN** 请求删除模型文件
- **THEN** 系统验证用户权限后才执行删除

### Requirement: 模型加载路径安全

系统 SHALL 验证模型加载路径，防止路径遍历攻击。

#### Scenario: 路径遍历检测
- **WHEN** 模型名称包含 .. 或 / 等路径遍历字符
- **THEN** 系统拒绝加载并返回错误

#### Scenario: 模型名称白名单
- **WHEN** 加载模型
- **THEN** 系统仅从配置的模型目录中查找

#### Scenario: 模型名称规范化
- **WHEN** 模型名称包含特殊字符
- **THEN** 系统规范化处理后验证