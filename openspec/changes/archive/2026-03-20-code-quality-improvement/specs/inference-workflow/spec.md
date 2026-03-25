## MODIFIED Requirements

### Requirement: 推理脚本模块化

推理脚本 SHALL 位于 `src/inference/` 目录，并在根目录提供兼容入口。所有函数 SHALL 具有完整的类型注解。

#### Scenario: 基础推理
- **WHEN** 用户运行 `python src/inference/inference.py --split val --num_samples 20`
- **THEN** 系统 SHALL 对验证集进行推理并保存可视化结果

#### Scenario: 根目录兼容入口
- **WHEN** 用户运行 `python inference.py --split val --num_samples 20`
- **THEN** 系统 SHALL 正确执行推理流程（通过代理脚本）

#### Scenario: 增强推理
- **WHEN** 用户运行 `python src/inference/inference_enhanced.py --color_scheme bright --alpha 0.6`
- **THEN** 系统 SHALL 使用指定颜色方案进行可视化

#### Scenario: 实例分割
- **WHEN** 用户运行 `python src/inference/inference_instance.py --split val --num_samples 20`
- **THEN** 系统 SHALL 对每个车辆实例进行编号和着色

#### Scenario: 模型加载失败处理
- **WHEN** 推理时模型文件不存在或格式错误
- **THEN** 系统 SHALL 抛出 `ModelLoadError` 异常并记录日志

#### Scenario: 图像加载失败处理
- **WHEN** 推理时图像文件不存在或格式错误
- **THEN** 系统 SHALL 抛出 `DataLoadError` 异常并记录日志