## ADDED Requirements

### Requirement: 标准化项目目录结构

项目 SHALL 遵循标准 Python 项目目录结构，文件按功能分类组织。

#### Scenario: 文档目录结构
- **WHEN** 用户查看项目根目录
- **THEN** 系统 SHALL 仅显示 README.md 作为入口文档
- **AND** 所有其他文档 SHALL 位于 docs/ 目录

#### Scenario: 脚本目录结构
- **WHEN** 用户需要查找辅助脚本
- **THEN** 系统 SHALL 在 scripts/ 目录提供所有 Shell 脚本

#### Scenario: 测试目录结构
- **WHEN** 用户运行测试
- **THEN** 系统 SHALL 从 tests/ 目录加载测试文件

#### Scenario: 源码目录结构
- **WHEN** 用户查看 src/ 目录
- **THEN** 系统 SHALL 包含以下子目录：
  - `src/data/`: 数据处理模块
  - `src/models/`: 模型定义
  - `src/utils/`: 工具函数
  - `src/inference/`: 推理脚本
  - `src/training/`: 训练脚本

### Requirement: 向后兼容入口点

项目 SHALL 在根目录提供向后兼容的入口点脚本。

#### Scenario: 训练入口点
- **WHEN** 用户运行 `python train.py`
- **THEN** 系统 SHALL 正确执行训练流程

#### Scenario: 推理入口点
- **WHEN** 用户运行 `python inference.py`
- **THEN** 系统 SHALL 正确执行推理流程