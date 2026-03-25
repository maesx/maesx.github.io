## MODIFIED Requirements

### Requirement: 单一训练入口

系统 SHALL 通过 `src/training/train.py` 作为主要训练入口，并在根目录提供兼容入口。所有函数 SHALL 具有完整的类型注解。

#### Scenario: 标准训练
- **WHEN** 用户运行 `python src/training/train.py --batch_size 8 --epochs 50 --use_gpu True`
- **THEN** 系统 SHALL 使用完整数据集进行训练

#### Scenario: 根目录兼容入口
- **WHEN** 用户运行 `python train.py --subset_ratio 0.1 --epochs 10`
- **THEN** 系统 SHALL 正确执行训练流程（通过代理脚本）

#### Scenario: 恢复训练
- **WHEN** 用户运行 `python train.py --resume outputs/checkpoints/best_model.pth`
- **THEN** 系统 SHALL 从指定检查点恢复训练

#### Scenario: 模型加载失败处理
- **WHEN** 指定的恢复模型文件不存在
- **THEN** 系统 SHALL 抛出 `ModelLoadError` 异常并记录日志

#### Scenario: 数据目录验证
- **WHEN** 训练启动时数据目录不存在
- **THEN** 系统 SHALL 抛出 `DataLoadError` 异常并记录日志