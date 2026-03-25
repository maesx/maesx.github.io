## MODIFIED Requirements

### Requirement: 单一训练入口

系统 SHALL 通过 `train.py` 作为唯一的训练入口脚本，支持所有训练配置。

#### Scenario: 标准训练
- **WHEN** 用户运行 `python train.py --batch_size 8 --epochs 50 --use_gpu True`
- **THEN** 系统 SHALL 使用完整数据集进行训练

#### Scenario: 轻量级训练
- **WHEN** 用户运行 `python train.py --subset_ratio 0.1 --epochs 10`
- **THEN** 系统 SHALL 使用 10% 数据集进行快速训练

#### Scenario: 恢复训练
- **WHEN** 用户运行 `python train.py --resume outputs/checkpoints/best_model.pth`
- **THEN** 系统 SHALL 从指定检查点恢复训练

#### Scenario: 学习率预热
- **WHEN** 用户运行 `python train.py --warmup_epochs 3`
- **THEN** 系统 SHALL 在前 3 个 epoch 进行学习率预热

## REMOVED Requirements

### Requirement: train_light.py 轻量级训练入口

**Reason**: 功能已被 `train.py --subset_ratio 0.1 --epochs 10` 完全覆盖

**Migration**: 使用 `python train.py --subset_ratio 0.1 --epochs 10 --batch_size 4` 替代 `python train_light.py`

### Requirement: run_train.py subprocess 训练包装器

**Reason**: 仅是 subprocess 调用 train.py 的包装器，无额外价值

**Migration**: 直接使用 `python train.py` 及相应参数

### Requirement: start_training.py 硬编码训练启动器

**Reason**: 硬编码绝对路径且功能与 train.py 重复

**Migration**: 使用 `python train.py --resume outputs/checkpoints/best_model.pth --warmup_epochs 3` 替代