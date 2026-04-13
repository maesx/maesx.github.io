## ADDED Requirements

### Requirement: 文件类型验证

系统 SHALL 通过 Magic number 验证上传文件的真实类型，而非仅依赖扩展名。

#### Scenario: 有效图片文件上传
- **WHEN** 用户上传扩展名为 .jpg 且 Magic number 为 JPEG 的文件
- **THEN** 系统接受上传并保存文件

#### Scenario: 伪造扩展名文件上传
- **WHEN** 用户上传扩展名为 .jpg 但 Magic number 为 PNG 的文件
- **THEN** 系统拒绝上传并返回错误信息

#### Scenario: 恶意脚本伪装上传
- **WHEN** 用户上传扩展名为 .jpg 但 Magic number 为 PHP/Python 脚本的文件
- **THEN** 系统拒绝上传并返回错误信息

#### Scenario: 不支持的文件类型
- **WHEN** 用户上传 .exe 或 .sh 等不支持类型的文件
- **THEN** 系统拒绝上传并返回错误信息

### Requirement: 文件大小限制

系统 SHALL 限制上传文件的大小，防止存储耗尽攻击。

#### Scenario: 文件大小在限制内
- **WHEN** 用户上传小于 50MB 的图片文件
- **THEN** 系统正常处理上传

#### Scenario: 文件超过大小限制
- **WHEN** 用户上传超过 50MB 的文件
- **THEN** 系统拒绝上传并返回 413 错误

#### Scenario: 模型文件大小限制
- **WHEN** 用户上传小于 500MB 的模型文件
- **THEN** 系统正常处理上传

### Requirement: 文件名安全处理

系统 SHALL 使用 UUID 重命名上传文件，防止路径遍历和文件覆盖攻击。

#### Scenario: 文件名包含路径遍历字符
- **WHEN** 用户上传文件名为 ../../../etc/passwd 的文件
- **THEN** 系统使用 UUID 重命名并保存到正确目录

#### Scenario: 多用户上传同名文件
- **WHEN** 两个用户分别上传名为 image.jpg 的文件
- **THEN** 系统为两个文件分配不同的 UUID 文件名，互不覆盖

#### Scenario: 保留原始文件名记录
- **WHEN** 系统保存上传文件
- **THEN** 系统在数据库或元数据中记录原始文件名

### Requirement: 上传目录安全

系统 SHALL 配置上传目录的安全权限，防止直接执行上传的文件。

#### Scenario: 上传目录禁止执行
- **WHEN** 攻击者尝试直接访问上传目录中的脚本文件
- **THEN** Web 服务器拒绝执行，仅返回文件内容或 403 错误

#### Scenario: 上传目录隔离
- **WHEN** 用户上传文件
- **THEN** 文件保存在独立的 uploads 目录，不与应用代码目录混合

### Requirement: 上传数量限制

系统 SHALL 限制单用户上传文件数量，防止存储滥用。

#### Scenario: 单次批量上传限制
- **WHEN** 用户单次上传超过 10 个文件
- **THEN** 系统拒绝上传并返回错误信息

#### Scenario: 用户总上传量限制
- **WHEN** 用户上传的文件总大小超过配额
- **THEN** 系统拒绝上传并提示清理旧文件