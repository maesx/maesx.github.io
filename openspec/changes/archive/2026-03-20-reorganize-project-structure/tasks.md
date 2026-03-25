## 1. 创建新目录结构

- [x] 1.1 创建 `docs/` 目录
- [x] 1.2 创建 `scripts/` 目录
- [x] 1.3 创建 `tests/` 目录
- [x] 1.4 创建 `src/inference/` 目录
- [x] 1.5 创建 `src/training/` 目录

## 2. 移动文档文件

- [x] 2.1 移动 `INFERENCE_GUIDE.md` 到 `docs/`
- [x] 2.2 移动 `INSTANCE_SEGMENTATION_GUIDE.md` 到 `docs/`
- [x] 2.3 移动 `COLOR_SCHEME_GUIDE.md` 到 `docs/`
- [x] 2.4 移动 `UNETPP_SEGMENTATION_PROMPT.md` 到 `docs/`
- [x] 2.5 移动 `optimization_expert_report.md` 到 `docs/`

## 3. 移动脚本文件

- [x] 3.1 移动 `quick_train.sh` 到 `scripts/`
- [x] 3.2 移动 `train_and_infer.sh` 到 `scripts/`
- [x] 3.3 创建 `scripts/README.md` 说明脚本用途

## 4. 移动测试文件

- [x] 4.1 移动 `test_model.py` 到 `tests/`
- [x] 4.2 移动 `test_system.py` 到 `tests/`
- [x] 4.3 创建 `tests/__init__.py`

## 5. 移动推理脚本

- [x] 5.1 移动 `inference.py` 到 `src/inference/`
- [x] 5.2 移动 `inference_enhanced.py` 到 `src/inference/`
- [x] 5.3 移动 `inference_instance.py` 到 `src/inference/`
- [x] 5.4 创建 `src/inference/__init__.py`

## 6. 移动训练脚本

- [x] 6.1 移动 `train.py` 到 `src/training/`
- [x] 6.2 创建 `src/training/__init__.py`

## 7. 更新 import 路径

- [x] 7.1 更新 `src/training/train.py` 中的 import 路径
- [x] 7.2 更新 `src/inference/inference.py` 中的 import 路径
- [x] 7.3 更新 `src/inference/inference_enhanced.py` 中的 import 路径
- [x] 7.4 更新 `src/inference/inference_instance.py` 中的 import 路径
- [x] 7.5 更新 `tests/test_model.py` 中的 import 路径
- [x] 7.6 更新 `tests/test_system.py` 中的 import 路径

## 8. 创建根目录代理脚本

- [x] 8.1 创建根目录 `train.py` 代理脚本
- [x] 8.2 创建根目录 `inference.py` 代理脚本

## 9. 更新 Shell 脚本路径

- [x] 9.1 更新 `scripts/quick_train.sh` 中的脚本路径
- [x] 9.2 更新 `scripts/train_and_infer.sh` 中的脚本路径

## 10. 更新文档

- [x] 10.1 更新 `README.md` 中的路径引用
- [x] 10.2 更新 `CLAUDE.md` 中的项目结构说明

## 11. 验证

- [x] 11.1 运行 `python tests/test_system.py` 验证系统测试
- [x] 11.2 运行 `python train.py --help` 验证训练入口
- [x] 11.3 运行 `python inference.py --help` 验证推理入口