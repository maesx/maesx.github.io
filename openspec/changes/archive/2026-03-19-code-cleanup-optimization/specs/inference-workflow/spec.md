## MODIFIED Requirements

### Requirement: 推理脚本模型加载健壮性

推理脚本 SHALL 能够处理不包含 `args` 字段的旧版 checkpoint 文件。

#### Scenario: 加载标准 checkpoint
- **WHEN** checkpoint 包含 `args` 字段
- **THEN** 系统 SHALL 从 `args` 读取模型配置（num_classes, encoder, deep_supervision, img_size）

#### Scenario: 加载旧版 checkpoint
- **WHEN** checkpoint 不包含 `args` 字段
- **THEN** 系统 SHALL 使用默认配置（num_classes=4, encoder='vgg19', deep_supervision=True, img_size=[512, 512]）

### Requirement: 推理脚本统一

系统 SHALL 提供三个推理脚本，职责明确：
- `inference.py`: 基础推理和可视化
- `inference_enhanced.py`: 增强推理，支持多种颜色方案
- `inference_instance.py`: 实例分割推理

#### Scenario: 基础推理
- **WHEN** 用户运行 `python inference.py --split val --num_samples 20`
- **THEN** 系统 SHALL 对验证集进行推理并保存可视化结果

#### Scenario: 增强推理
- **WHEN** 用户运行 `python inference_enhanced.py --color_scheme bright --alpha 0.6`
- **THEN** 系统 SHALL 使用指定颜色方案进行可视化

#### Scenario: 实例分割
- **WHEN** 用户运行 `python inference_instance.py --split val --num_samples 20`
- **THEN** 系统 SHALL 对每个车辆实例进行编号和着色