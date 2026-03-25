## ADDED Requirements

### Requirement: 自定义异常类层次

系统 SHALL 提供统一的异常类层次结构，用于处理各类错误情况。

#### Scenario: 模型加载失败
- **WHEN** 模型文件不存在或格式错误
- **THEN** 系统 SHALL 抛出 `ModelLoadError` 异常，包含详细的错误信息

#### Scenario: 数据加载失败
- **WHEN** 数据目录不存在或数据格式错误
- **THEN** 系统 SHALL 抛出 `DataLoadError` 异常，包含详细的错误信息

#### Scenario: 配置验证失败
- **WHEN** 配置参数无效
- **THEN** 系统 SHALL 抛出 `ConfigError` 异常，包含详细的错误信息

### Requirement: 日志记录功能

系统 SHALL 提供统一的日志记录功能，支持不同日志级别。

#### Scenario: 训练日志记录
- **WHEN** 训练过程中发生事件
- **THEN** 系统 SHALL 记录到 `outputs/logs/training.log` 文件

#### Scenario: 推理日志记录
- **WHEN** 推理过程中发生事件
- **THEN** 系统 SHALL 记录到 `outputs/logs/inference.log` 文件

#### Scenario: 日志级别控制
- **WHEN** 用户设置日志级别
- **THEN** 系统 SHALL 只记录该级别及以上级别的日志