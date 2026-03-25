## Why

项目存在明显的代码冗余和重复问题：多个功能相似的训练启动脚本（train_light.py、run_train.py、start_training.py）、多个测试脚本职责重叠（test_model.py、test_system.py、test_subset.py、test_m4_performance.py、validate_model.py）、以及硬编码的绝对路径。这些问题导致维护成本增加、代码一致性差，且容易引入bug。

## What Changes

### 删除冗余文件

**训练相关脚本（保留 train.py）：**
- **BREAKING** 删除 `train_light.py` - 功能已被 `train.py --subset_ratio 0.1` 完全覆盖
- **BREAKING** 删除 `run_train.py` - 仅是 subprocess 调用 train.py 的包装器，无额外价值
- **BREAKING** 删除 `start_training.py` - 硬编码绝对路径，功能与 train.py 重复

**测试脚本整合：**
- **BREAKING** 删除 `test_subset.py` - 功能已被 test_system.py 覆盖
- **BREAKING** 删除 `test_m4_performance.py` - 特定硬件测试，可整合到 test_system.py
- **BREAKING** 删除 `validate_model.py` - 使用过时的 RoadDataset 类，功能与 test_model.py 重复

**Shell脚本整合：**
- **BREAKING** 删除 `run_training.sh` - 硬编码配置，功能与 quick_train.sh 重复

### 代码质量优化

- 移除 `validate_model.py` 中对不存在的 `RoadDataset` 类的引用
- 统一推理脚本中的模型加载逻辑（处理无 args 的 checkpoint 情况）
- 添加类型注解到核心模块（models、data、utils）
- 统一配置管理，移除硬编码路径

## Capabilities

### New Capabilities
- `unified-testing`: 统一的测试入口，整合系统测试、模型验证、性能基准测试功能

### Modified Capabilities
- `training-workflow`: 简化训练入口，移除冗余脚本，保留 train.py 作为唯一训练入口
- `inference-workflow`: 统一推理脚本中的模型加载逻辑，增强健壮性

## Impact

### 受影响的文件
- **删除**: train_light.py, run_train.py, start_training.py, test_subset.py, test_m4_performance.py, validate_model.py, run_training.sh
- **保留**: train.py, test_model.py, test_system.py, inference.py, inference_enhanced.py, inference_instance.py, quick_train.sh, train_and_infer.sh

### 代码变更
- `src/models/unet_plusplus.py`: 添加类型注解
- `src/data/dataset.py`: 添加类型注解
- `src/utils/losses.py`: 添加类型注解
- `inference*.py`: 统一模型加载逻辑

### 向后兼容性
- 所有删除的脚本功能均可通过保留的脚本 + 参数实现
- 用户需要更新调用方式（如使用 `python train.py --subset_ratio 0.1` 替代 `python train_light.py`）