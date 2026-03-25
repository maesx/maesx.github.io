# 道路车辆分割系统 - 推理可视化说明

## 训练完成后查看验证集分割结果

### 方式1: 使用自动流程脚本（推荐）

训练完成后自动进行推理:

```bash
./train_and_infer.sh
```

这个脚本会:
1. 检查是否有训练好的模型
2. 如果没有，提供训练选项
3. 训练完成后自动对验证集进行推理
4. 生成可视化结果

### 方式2: 手动推理验证集

训练完成后，单独运行推理:

```bash
# 对验证集推理（默认20张样本）
python3 inference.py --model_path outputs/checkpoints/best_model.pth --split val

# 指定样本数量
python3 inference.py --model_path outputs/checkpoints/best_model.pth --split val --num_samples 50

# 对测试集推理
python3 inference.py --split test --num_samples 30

# 对训练集推理
python3 inference.py --split train --num_samples 10
```

### 方式3: 推理单张图像

```bash
python3 inference.py --image_path road_vehicle_pedestrian_det_datasets/images/val/xxx.jpg
```

### 可视化结果说明

结果保存在: `outputs/visualizations/val/`

每个图像包含三个部分:
1. **左侧**: 原始图像
2. **中间**: 原始图像 + 分割结果叠加
3. **右侧**: 纯分割掩码

颜色映射:
- **黑色**: 背景
- **红色**: Car (小汽车)
- **绿色**: Truck (卡车)
- **蓝色**: Bus (公共汽车)

### 参数说明

```bash
python3 inference.py [参数]

必需参数:
  --model_path    模型权重路径 (默认: outputs/checkpoints/best_model.pth)

可选参数:
  --split         数据集划分: train/val/test (默认: val)
  --num_samples   可视化样本数量 (默认: 10)
  --device        设备: cpu/cuda/mps (默认: 自动检测)
  --image_path    单张图像路径 (指定后忽略split)
  --images_dir    批量推理目录
  --output_dir    输出目录 (默认: outputs/visualizations)
```

### 示例

```bash
# 示例1: 训练完成后快速查看验证集效果
python3 inference.py --split val --num_samples 20

# 示例2: 使用M4 GPU推理测试集
python3 inference.py --split test --num_samples 50 --device mps

# 示例3: 批量推理整个文件夹
python3 inference.py --images_dir path/to/images --output_dir results

# 示例4: 推理单张图像并指定输出路径
python3 inference.py --image_path test.jpg --output_dir my_results
```

### 监控训练过程

```bash
# 启动TensorBoard
tensorboard --logdir outputs/logs

# 浏览器打开
# http://localhost:6006
```

可以查看:
- Loss变化曲线
- IoU变化曲线
- Pixel Accuracy变化曲线

### 常见问题

**Q: 训练完成后找不到模型文件？**
A: 模型保存在 `outputs/checkpoints/best_model.pth`

**Q: 推理速度慢？**
A: 使用 `--device mps` 启用M4 GPU加速

**Q: 想看更多样本？**
A: 使用 `--num_samples` 参数，例如 `--num_samples 100`

**Q: 想看所有样本？**
A: 省略 `--num_samples` 参数，或设置很大的值
