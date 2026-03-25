## Context

本项目是一个基于 U-Net++ 的道路车辆语义分割系统。经过代码审查发现以下问题：

1. **冗余训练脚本**：存在 4 个训练入口文件（train.py、train_light.py、run_train.py、start_training.py），其中 3 个是 train.py 的包装器或简化版
2. **测试脚本职责重叠**：5 个测试/验证脚本（test_model.py、test_system.py、test_subset.py、test_m4_performance.py、validate_model.py）功能交叉
3. **硬编码路径**：部分脚本包含绝对路径 `/Users/sux/IdeaProjects/maesx.github.io-master`
4. **过时引用**：validate_model.py 引用了不存在的 `RoadDataset` 类（应为 `RoadVehicleDataset`）
5. **缺少类型注解**：核心模块（models、data、utils）缺少类型注解，影响代码可读性和 IDE 支持

## Goals / Non-Goals

**Goals:**
- 删除冗余的训练启动脚本，保留 train.py 作为唯一训练入口
- 整合测试脚本，保留 test_model.py 和 test_system.py
- 移除硬编码的绝对路径
- 修复 validate_model.py 中的过时引用（或删除该文件）
- 为核心模块添加类型注解

**Non-Goals:**
- 不重构现有架构或模块结构
- 不添加新功能
- 不修改训练/推理的核心逻辑
- 不添加 CI/CD 配置

## Decisions

### D1: 删除 train_light.py、run_train.py、start_training.py

**理由**：
- `train_light.py` 的所有功能可通过 `python train.py --subset_ratio 0.1 --epochs 10` 实现
- `run_train.py` 仅是 subprocess 调用 train.py 的包装器，增加维护成本无实际价值
- `start_training.py` 硬编码绝对路径，且功能与 train.py 完全重复

**替代方案**：
- 保留这些文件但添加弃用警告 → 增加维护负担，用户可能继续使用过时方式
- 合并到一个脚本 → train.py 已支持所有参数，无需额外脚本

### D2: 删除 test_subset.py、test_m4_performance.py、validate_model.py

**理由**：
- `test_subset.py` 测试数据子集功能，已被 test_system.py 覆盖
- `test_m4_performance.py` 是特定硬件的性能测试，可整合到 test_system.py 作为可选功能
- `validate_model.py` 使用过时的 `RoadDataset` 类（不存在），功能与 test_model.py 重复

**替代方案**：
- 将 M4 性能测试整合到 test_system.py → 增加文件复杂度，且该测试仅对特定用户有用
- 修复 validate_model.py → test_model.py 已提供相同功能，修复成本高于删除

### D3: 删除 run_training.sh

**理由**：
- 该脚本硬编码了特定配置（IoU: 73.41%、从第9轮开始等），不适合通用使用
- `quick_train.sh` 已提供更好的交互式训练选项

### D4: 保留 quick_train.sh 和 train_and_infer.sh

**理由**：
- `quick_train.sh` 提供交互式菜单，用户体验好
- `train_and_infer.sh` 提供训练+推理一体化流程，有独特价值

### D5: 为核心模块添加类型注解

**理由**：
- 提高代码可读性和 IDE 支持
- 便于后续维护和重构
- 符合现代 Python 最佳实践

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 用户可能依赖被删除的脚本 | 在 README.md 中记录迁移路径；所有功能均可通过 train.py 参数实现 |
| 删除 M4 性能测试可能影响特定用户 | 该功能可通过 `python train.py --use_gpu True --subset_ratio 0.1` 手动测试 |
| 类型注解可能引入错误 | 仅添加注解，不修改逻辑；添加后运行现有测试验证 |