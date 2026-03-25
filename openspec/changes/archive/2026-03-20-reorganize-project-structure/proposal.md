## Why

当前项目根目录文件散乱，脚本、文档、配置混杂在一起，缺乏清晰的组织结构。新开发者难以快速定位文件，维护成本高。现在需要建立标准的 Python 项目结构，提升可读性和可维护性。

## What Changes

### 文档整合
- 创建 `docs/` 目录，移动所有文档文件（README.md 除外）
- 保留 `README.md` 在根目录作为项目入口文档
- 移动文件：`INFERENCE_GUIDE.md`, `INSTANCE_SEGMENTATION_GUIDE.md`, `COLOR_SCHEME_GUIDE.md`, `UNETPP_SEGMENTATION_PROMPT.md`, `optimization_expert_report.md`

### 脚本整合
- 创建 `scripts/` 目录，移动所有 Shell 脚本
- 移动文件：`quick_train.sh`, `train_and_infer.sh`
- 创建 `scripts/README.md` 说明脚本用途

### 测试整合
- 创建 `tests/` 目录，移动所有测试文件
- 移动文件：`test_model.py`, `test_system.py`
- 重命名为标准测试命名：`test_model.py` → `tests/test_model.py`, `test_system.py` → `tests/test_system.py`

### 推理脚本整合
- 创建 `src/inference/` 目录，移动推理相关脚本
- 移动文件：`inference.py`, `inference_enhanced.py`, `inference_instance.py`
- 创建 `src/inference/__init__.py`

### 训练脚本整合
- 将 `train.py` 移动到 `src/training/` 目录
- 创建 `src/training/__init__.py`

### 配置优化
- 保留 `configs/` 目录结构不变
- 保留 `requirements.txt` 在根目录

## Capabilities

### New Capabilities
- `project-structure`: 标准化的项目目录结构，遵循 Python 最佳实践

### Modified Capabilities
- `training-workflow`: 训练入口路径变更（train.py → src/training/train.py）
- `inference-workflow`: 推理脚本路径变更（inference*.py → src/inference/）

## Impact

### 文件移动清单
| 原路径 | 新路径 |
|--------|--------|
| `INFERENCE_GUIDE.md` | `docs/INFERENCE_GUIDE.md` |
| `INSTANCE_SEGMENTATION_GUIDE.md` | `docs/INSTANCE_SEGMENTATION_GUIDE.md` |
| `COLOR_SCHEME_GUIDE.md` | `docs/COLOR_SCHEME_GUIDE.md` |
| `UNETPP_SEGMENTATION_PROMPT.md` | `docs/UNETPP_SEGMENTATION_PROMPT.md` |
| `optimization_expert_report.md` | `docs/optimization_expert_report.md` |
| `quick_train.sh` | `scripts/quick_train.sh` |
| `train_and_infer.sh` | `scripts/train_and_infer.sh` |
| `test_model.py` | `tests/test_model.py` |
| `test_system.py` | `tests/test_system.py` |
| `inference.py` | `src/inference/inference.py` |
| `inference_enhanced.py` | `src/inference/inference_enhanced.py` |
| `inference_instance.py` | `src/inference/inference_instance.py` |
| `train.py` | `src/training/train.py` |

### 需要更新的文件
- `CLAUDE.md`: 更新项目结构说明
- `README.md`: 更新命令路径
- `scripts/quick_train.sh`: 更新 Python 脚本调用路径
- `scripts/train_and_infer.sh`: 更新 Python 脚本调用路径
- 各脚本内部的 import 路径

### 新建文件
- `scripts/README.md`: 脚本使用说明
- `src/inference/__init__.py`
- `src/training/__init__.py`
- `tests/__init__.py`