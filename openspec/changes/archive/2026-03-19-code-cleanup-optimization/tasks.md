## 1. 删除冗余训练脚本

- [x] 1.1 删除 `train_light.py` 文件
- [x] 1.2 删除 `run_train.py` 文件
- [x] 1.3 删除 `start_training.py` 文件

## 2. 删除冗余测试脚本

- [x] 2.1 删除 `test_subset.py` 文件
- [x] 2.2 删除 `test_m4_performance.py` 文件
- [x] 2.3 删除 `validate_model.py` 文件

## 3. 删除冗余 Shell 脚本

- [x] 3.1 删除 `run_training.sh` 文件

## 4. 核心模块添加类型注解

- [x] 4.1 为 `src/models/unet_plusplus.py` 添加类型注解
- [x] 4.2 为 `src/data/dataset.py` 添加类型注解
- [x] 4.3 为 `src/utils/losses.py` 添加类型注解

## 5. 统一推理脚本模型加载逻辑

- [x] 5.1 更新 `inference.py` 中的模型加载逻辑，处理无 args 的 checkpoint
- [x] 5.2 更新 `inference_enhanced.py` 中的模型加载逻辑，处理无 args 的 checkpoint
- [x] 5.3 验证 `inference_instance.py` 已正确处理无 args 的 checkpoint

## 6. 验证与测试

- [x] 6.1 运行 `python test_system.py` 验证系统完整性
- [x] 6.2 运行 `python test_model.py --split val` 验证模型测试功能
- [x] 6.3 运行 `python inference.py --split val --num_samples 5` 验证推理功能
- [x] 6.4 运行 `python train.py --subset_ratio 0.01 --epochs 1` 验证训练入口

## 7. 文档更新

- [x] 7.1 更新 `CLAUDE.md` 移除已删除脚本的引用
- [x] 7.2 检查 `README.md` 是否需要更新（如有引用已删除脚本）