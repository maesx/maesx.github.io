## Context

当前项目是一个基于 U-Net++ 的道路车辆语义分割系统。经过代码审查发现：

1. **类型注解不完整**：
   - `src/models/unet_plusplus.py`、`src/data/dataset.py`、`src/utils/losses.py` 已添加类型注解
   - `src/training/train.py` 缺少类型注解
   - `src/inference/` 目录下的推理脚本缺少类型注解
   - `src/data/yolo_to_mask.py` 缺少类型注解

2. **错误处理不足**：
   - 模型加载失败时缺乏友好的错误提示
   - 数据加载失败时程序直接崩溃
   - 配置参数缺乏验证
   - 缺少日志记录机制

## Goals / Non-Goals

**Goals:**
- 为所有核心模块添加完整的类型注解
- 建立统一的错误处理机制
- 添加日志记录功能
- 提高代码可读性和 IDE 支持

**Non-Goals:**
- 不修改现有 API 行为
- 不添加新功能
- 不重构代码结构
- 不添加单元测试（可在后续变更中处理）

## Decisions

### D1: 类型注解风格

**决定**: 使用 Python 3.9+ 风格的类型注解

**理由**:
- 项目已使用 Python 3.9+
- 使用内置类型（如 `list[int]` 而非 `List[int]`）更简洁
- 与现有代码风格一致

**实现**:
- 函数参数和返回值添加类型注解
- 类属性添加类型注解
- 使用 `Optional[T]` 表示可选参数
- 使用 `Union[T1, T2]` 表示多种类型

### D2: 错误处理策略

**决定**: 创建自定义异常类层次结构

**理由**:
- 提供更具体的错误信息
- 便于调用者捕获特定异常
- 与 Python 最佳实践一致

**异常类设计**:
```python
class SegmentationError(Exception):
    """基础异常类"""
    pass

class ModelLoadError(SegmentationError):
    """模型加载失败"""
    pass

class DataLoadError(SegmentationError):
    """数据加载失败"""
    pass

class ConfigError(SegmentationError):
    """配置错误"""
    pass
```

### D3: 日志记录策略

**决定**: 使用 Python 标准库 `logging` 模块

**理由**:
- 无需额外依赖
- 与 TensorBoard 日志分离
- 支持不同日志级别

**实现**:
- 创建 `src/utils/logging_config.py` 统一配置日志
- 支持控制台和文件输出
- 训练和推理使用不同的日志文件

### D4: 配置验证

**决定**: 在关键入口点添加配置验证

**理由**:
- 尽早发现配置错误
- 提供清晰的错误信息
- 不影响运行时性能

**验证点**:
- 训练脚本启动时验证训练参数
- 推理脚本启动时验证模型路径
- 数据加载时验证数据目录

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 类型注解可能引入错误 | 仅添加注解，不修改逻辑；添加后运行现有测试验证 |
| 错误处理可能改变程序行为 | 保持向后兼容，异常仍向上传播 |
| 日志文件可能占用磁盘空间 | 设置日志轮转，限制文件大小 |
| 增加代码复杂度 | 保持错误处理代码简洁，避免过度设计 |