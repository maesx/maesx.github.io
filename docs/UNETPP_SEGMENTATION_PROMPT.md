# U-Net++ 图像分割系统快速搭建 Prompt

## 📋 使用说明

这是一个完整的、可直接使用的 AI Prompt，用于快速搭建基于 U-Net++ 的图像分割系统。您可以将此 Prompt 提供给 ChatGPT、Claude 等 AI 助手快速生成完整代码。

---

## 🎯 完整 Prompt

### Prompt 正文（复制以下内容）

---

我需要搭建一个基于 U-Net++ 的语义图像分割系统，用于分割道路场景中的车辆目标。请帮我生成完整可运行的代码，包括以下模块：

### 1. 数据格式转换模块（YOLO -> 分割掩码）

**背景**：我有 YOLO 格式的目标检测数据集，包含边界框标注（bounding box），需要转换为语义分割掩码。

**数据格式**：
- 图像：`images/{train,val,test}/*.jpg`
- 标注：`labels/{train,val,test}/*.txt`（YOLO格式：class_id x_center y_center width height）
- 类别文件：`classes.txt`，每行一个类别名称

**转换要求**：
- 读取YOLO边界框标注
- 将边界框区域填充为对应的类别标签值
- 背景为0，目标类别从1开始编号
- 输出PNG格式的分割掩码

**目标类别**：car, truck, bus（共3类车辆 + 1类背景 = 4类）

**输出结构**：

    outputs/masks/
      ├── train/*.png
      ├── val/*.png
      └── test/*.png

请生成完整的转换脚本 `yolo_to_mask.py`

---

### 2. 数据加载与增强模块

**要求**：

#### 数据集类 `RoadVehicleDataset`:
- 继承 `torch.utils.data.Dataset`
- 支持读取图像和对应的分割掩码
- 支持数据子集比例选择（用于快速实验）
- 图像尺寸：512x512

#### 数据增强策略：

**训练集增强**：
- 随机水平翻转 (p=0.5)
- 随机垂直翻转 (p=0.2)
- 随机旋转90度 (p=0.5)
- 亮度对比度调整 (brightness_limit=0.2, contrast_limit=0.2, p=0.5)
- 高斯模糊 (blur_limit=7, p=0.3)
- 高斯噪声 (p=0.3)
- 弹性形变 ElasticTransform (p=0.3)
- 网格畸变 GridDistortion (p=0.3)
- 标准化：mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)

**验证/测试集增强**：
- 仅Resize + Normalize

#### 数据加载器：
- 使用 albumentations 库进行数据增强
- 提供 `get_dataloader()` 函数返回 DataLoader
- 支持批次大小、并行加载等参数配置

请生成完整的数据处理脚本 `dataset.py`

---

### 3. U-Net++ 模型架构

**要求**：

#### 网络结构：
- 编码器：使用预训练的 VGG19 作为 backbone
- 解码器：实现 U-Net++ 的嵌套跳跃连接结构
- 深度监督：在多个解码器层级输出辅助预测
- 输出类别数：4（背景 + 3类车辆）

#### 关键特性：
- 实现密集跳跃连接（dense skip connections）
- 支持 deep supervision 模式（训练时返回多个尺度输出）
- 初始化：使用 ImageNet 预训练权重

请生成完整的模型文件 `unet_plusplus.py`

---

### 4. 训练模块

**训练配置**：
- 损失函数：CrossEntropyLoss + Dice Loss 组合
- 优化器：Adam，初始学习率 1e-4
- 学习率调度：ReduceLROnPlateau（耐心=5，降低因子=0.5）
- 早停策略：耐心=10轮
- 批次大小：根据GPU/CPU自动调整（GPU: 8-16, CPU: 4）
- 训练轮数：50-100 epochs

**训练过程**：
- 每个epoch记录训练和验证的 Loss、IoU、Pixel Accuracy
- 保存最佳模型（基于验证集 IoU）
- 支持从检查点恢复训练
- 打印详细的训练日志

**目标性能**：
- 验证集 mIoU ≥ 70%

请生成完整的训练脚本 `train.py`

---

### 5. 可视化推理模块

**要求**：
生成一个推理脚本，实现以下功能：

#### 5.1 基础可视化：
- 加载训练好的模型
- 对验证集图像进行分割预测
- 生成 **原图 vs 标注掩码 vs 预测掩码** 的对比图
- 使用彩色掩码显示不同类别（背景=黑色，car=红色，truck=绿色，bus=蓝色）

#### 5.2 实例分割可视化：
- 对预测的语义分割结果，使用连通区域分析分离不同实例
- 为 **同一类型的每个实例分配不同颜色**
- 在每个实例上标注实例ID和类型

#### 5.3 输出格式：
- 每张图像生成一张可视化结果图
- 图像排列：原图 | 分割结果 | 彩色掩码叠加 | 实例分割
- 保存为高质量 JPG 图片
- 输出目录：`outputs/visualizations/val/`

#### 5.4 性能统计：
- 计算并打印整体 mIoU
- 计算并打印各类别 IoU
- 生成简短的推理报告

请生成完整的推理脚本 `inference.py`

---

### 6. 项目文件结构

请按以下结构组织生成的代码：

    project/
    ├── src/
    │   ├── data/
    │   │   ├── yolo_to_mask.py    # 数据格式转换
    │   │   └── dataset.py          # 数据加载和增强
    │   ├── models/
    │   │   └── unet_plusplus.py   # U-Net++ 模型
    │   └── utils/
    │       └── losses.py           # 损失函数和评估指标
    ├── train.py                    # 训练脚本
    ├── inference.py                # 推理和可视化脚本
    ├── requirements.txt            # 依赖包
    └── README.md                   # 使用说明

---

### 7. 代码要求

- 使用 PyTorch 框架
- 代码需要完整可运行，不要省略关键部分
- 包含必要的注释和文档字符串
- 支持命令行参数配置
- 提供使用示例
- 考虑 GPU/CPU 兼容性
- 添加异常处理

---

### 8. 输出要求

请为每个模块生成完整的、可直接运行的 Python 代码，并简要说明：
1. 主要功能和设计思路
2. 关键参数和配置
3. 使用方法和示例命令
4. 注意事项

---

**开始生成代码，从数据格式转换模块开始。**

---

## 📝 使用方法

### 步骤 1：准备数据
确保您的数据集符合以下结构：

    road_vehicle_pedestrian_det_datasets/
    ├── images/
    │   ├── train/*.jpg
    │   ├── val/*.jpg
    │   └── test/*.jpg
    ├── labels/
    │   ├── train/*.txt
    │   ├── val/*.txt
    │   └── test/*.txt
    └── classes.txt

### 步骤 2：使用 Prompt
1. 复制上面的完整 Prompt
2. 粘贴到 ChatGPT、Claude 等 AI 助手
3. AI 将为您生成完整的代码
4. 根据实际情况调整参数和配置

### 步骤 3：运行代码
按照 AI 生成的说明文档依次运行：
1. 数据转换脚本
2. 训练脚本
3. 推理可视化脚本

---

## ⚙️ 可定制参数

以下参数可根据实际需求在 Prompt 中修改：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **目标类别** | car, truck, bus | 根据您的数据集调整 |
| **图像尺寸** | 512x512 | 可改为 256x256 或 1024x1024 |
| **编码器** | VGG19 | 可改为 ResNet50, EfficientNet 等 |
| **批次大小** | GPU:8, CPU:4 | 根据显存调整 |
| **训练轮数** | 50-100 | 根据数据量和收敛情况调整 |
| **学习率** | 1e-4 | 默认值，可微调 |
| **目标 IoU** | 70% | 可设为 80% 或更高 |

---

## 💡 优化建议

### Prompt 改进技巧：

**1. 更详细的增强策略**：

    在训练集增强中添加：
    - 随机裁剪：RandomCrop(height=512, width=512, p=0.5)
    - 颜色抖动：ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1)
    - 课程学习：前10轮使用轻度增强，后面逐渐加强

**2. 更复杂损失函数**：

    使用 Focal Loss 替代 CrossEntropy：
    - alpha = [0.1, 0.3, 0.3, 0.3]  # 类别权重
    - gamma = 2.0  # 聚焦参数

**3. 添加评估指标**：

    除了 IoU，还计算：
    - 类别平均精度 (Class-wise Accuracy)
    - Dice Coefficient
    - 边界 F1 分数 (Boundary F1)

**4. 实例分割增强**：

    在实例分割中添加：
    - 基于形态学操作的实例分离
    - 小目标过滤（面积 < 100 像素）
    - 边界框输出和 JSON 标注生成

---

## 🎯 预期结果

使用此 Prompt 生成的系统，预期可以达到：

### 性能指标：
- **整体 mIoU**: 70-80%（取决于数据量）
- **各类别 IoU**:
  - Background: 90%+
  - Bus: 85%+（大目标）
  - Truck: 70%+（中等目标）
  - Car: 60%+（小目标）

### 功能实现：
- ✅ 完整的数据转换流水线
- ✅ 丰富的数据增强策略
- ✅ 稳定的训练过程
- ✅ 详细的可视化输出
- ✅ 实例级分割能力

---

## 🔧 常见问题

### Q1: 生成的代码无法运行？
**A**: 检查以下几点：
- Python 版本是否 ≥ 3.7
- PyTorch 版本是否匹配
- 依赖包是否完整安装
- 文件路径是否正确

### Q2: 训练时显存不足？
**A**: 在 Prompt 中添加：

    请添加梯度累积 (gradient accumulation) 功能：
    - accumulation_steps = 4
    - 等效批次大小 = batch_size × accumulation_steps

### Q3: 想要更换 backbone？
**A**: 修改 Prompt 中的编码器部分：

    编码器改为：ResNet50 或 EfficientNet-B4
    确保使用 ImageNet 预训练权重

### Q4: 需要更快的训练速度？
**A**: 在 Prompt 中添加：

    添加混合精度训练 (AMP)：
    - 使用 torch.cuda.amp
    - 减少显存占用，加速 2-3 倍

---

## 📚 扩展方向

如果需要进一步增强系统，可以在 Prompt 中添加：

### 1. 半监督学习

    添加以下功能：
    - 使用伪标签 (pseudo-labeling)
    - 实现一致性正则化
    - 支持 MixMatch 或 FixMatch 方法

### 2. 实时推理

    添加模型优化：
    - ONNX 导出
    - TensorRT 加速
    - 模型量化 (int8/fp16)
    - 推理速度优化到 30+ FPS

### 3. 多尺度训练

    支持多尺度输入：
    - 训练时随机尺度 [0.5, 1.0, 1.5]
    - 测试时多尺度融合 (TTA)

---

## ✅ 检查清单

使用此 Prompt 前，请确认：

- [ ] 数据集格式符合要求
- [ ] 了解目标类别数量
- [ ] 确定目标性能指标
- [ ] 准备好依赖环境
- [ ] 有足够的训练资源（GPU 推荐）

---

## 📞 反馈与改进

如果您在使用此 Prompt 时遇到问题或有改进建议，可以：

1. 直接在 Prompt 中补充具体需求
2. 调整参数配置
3. 增加额外功能模块

---

**祝您快速搭建成功！** 🚀