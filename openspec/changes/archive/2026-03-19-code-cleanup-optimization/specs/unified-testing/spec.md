## ADDED Requirements

### Requirement: 统一测试入口

系统 SHALL 提供统一的测试入口脚本 `test_model.py` 和 `test_system.py`，覆盖所有测试场景。

#### Scenario: 模型性能测试
- **WHEN** 用户运行 `python test_model.py --model_path <path> --split test`
- **THEN** 系统 SHALL 加载模型并在指定数据集上计算 IoU、准确率等指标

#### Scenario: 系统完整性测试
- **WHEN** 用户运行 `python test_system.py`
- **THEN** 系统 SHALL 验证数据加载、模型构建、前向传播、损失计算等核心功能

#### Scenario: 数据子集测试
- **WHEN** 用户需要测试数据子集功能
- **THEN** 系统 SHALL 通过 `python train.py --subset_ratio <ratio>` 进行验证，无需单独测试脚本

### Requirement: 测试脚本职责明确

系统 SHALL 确保每个测试脚本有明确的职责边界。

#### Scenario: test_model.py 职责
- **WHEN** 用户需要评估模型性能
- **THEN** 系统 SHALL 通过 `test_model.py` 提供模型加载、推理、指标计算功能

#### Scenario: test_system.py 职责
- **WHEN** 用户需要验证系统完整性
- **THEN** 系统 SHALL 通过 `test_system.py` 提供数据加载、模型构建、前向传播验证功能