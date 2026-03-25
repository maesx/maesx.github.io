# 道路车辆分割 - 颜色方案说明

## 🎨 可视化颜色方案

### 方案1: Standard (标准) ⭐推荐
**适用场景:** 日常使用、科研论文
```
- Background (背景):  黑色 RGB(0, 0, 0)
- Car (轿车):         红色 RGB(255, 0, 0)
- Truck (卡车):       绿色 RGB(0, 255, 0)
- Bus (公交车):       蓝色 RGB(0, 0, 255)
```

### 方案2: Bright (鲜艳)
**适用场景:** 演示展示、教学用途
```
- Background (背景):  黑色 RGB(0, 0, 0)
- Car (轿车):         黄色   RGB(255, 255, 0)
- Truck (卡车):       紫红色 RGB(255, 0, 255)
- Bus (公交车):       青色   RGB(0, 255, 255)
```

### 方案3: Contrast (高对比度) ⭐演示推荐
**适用场景:** 演讲、演示、低质量图像
```
- Background (背景):  深灰 RGB(50, 50, 50)
- Car (轿车):         亮黄 RGB(255, 255, 61)
- Truck (卡车):       橙色 RGB(30, 144, 255)
- Bus (公交车):       粉色 RGB(255, 105, 180)
```

### 方案4: Pastel (柔和)
**适用场景:** 报告、文档
```
- Background (背景):  深灰   RGB(30, 30, 30)
- Car (轿车):         淡紫色 RGB(200, 150, 255)
- Truck (卡车):       淡绿色 RGB(150, 255, 200)
- Bus (公交车):       淡橙色 RGB(255, 200, 150)
```

### 方案5: Dark (深色)
**适用场景:** 深色背景 Presentation
```
- Background (背景):  黑色   RGB(0, 0, 0)
- Car (轿车):         深红色 RGB(0, 0, 180)
- Truck (卡车):       深绿色 RGB(0, 180, 0)
- Bus (公交车):       深蓝色 RGB(180, 0, 0)
```

### 方案6: Traffic (交通标志色)
**适用场景:** 交通场景分析
```
- Background (背景):  黑色     RGB(0, 0, 0)
- Car (轿车):         橙色     RGB(0, 204, 255)
- Truck (卡车):       巧克力色 RGB(210, 105, 30)
- Bus (公交车):       蓝色     RGB(255, 255, 0)
```

---

## 📖 使用方法

### 基本用法
```bash
# 使用标准颜色方案
python3 inference_enhanced.py \
    --model_path outputs/checkpoints/best_model.pth \
    --split val \
    --num_samples 20 \
    --color_scheme standard

# 使用高对比度颜色方案
python3 inference_enhanced.py \
    --model_path outputs/checkpoints/best_model.pth \
    --split val \
    --num_samples 20 \
    --color_scheme contrast
```

### 高级选项
```bash
# 调整叠加透明度
python3 inference_enhanced.py \
    --color_scheme bright \
    --alpha 0.7  # 0.0-1.0, 值越大分割区域越明显
```

---

## 🖼️ 可视化结果说明

每张可视化图片包含：

```
┌─────────────────────────────────────────────────────────┐
│  Original  │   Overlay    │ Segmentation │   Legend     │
│   (原图)    │  (叠加效果)  │   (纯掩码)    │   (图例)     │
└─────────────────────────────────────────────────────────┘
```

- **Original**: 原始输入图像
- **Overlay**: 原图与分割掩码叠加效果
- **Segmentation**: 纯分割掩码（没有原图）
- **Legend**: 
  - 类别颜色图例
  - 各类别像素占比统计

---

## 📊 当前模型性能

- **最佳IoU**: 74.11%
- **训练数据**: 800张图像 (10%子集)
- **验证数据**: 100张图像
- **模型**: U-Net++ + VGG19

---

## 🎯 快速对比不同颜色方案

您可以打开以下目录对比效果：

1. **outputs/visualizations/standard/val/** - 标准颜色
2. **outputs/visualizations/bright/val/** - 鲜艳颜色
3. **outputs/visualizations/contrast/val/** - 高对比度

---

## 💡 提示

- 如果效果不明显，尝试调整 `--alpha` 参数 (默认0.5)
- 对于演示，推荐使用 **contrast** 或 **bright** 方案
- 对于论文，推荐使用 **standard** 方案
- 统计信息显示在图例右侧，包含各车辆类别的占比

---

## 🔧 自定义颜色

如需自定义颜色，可编辑 `inference_enhanced.py` 中的颜色方案：

```python
# 在 self.color_schemes 字典中添加
'custom': [
    [0, 0, 0],      # Background - BGR格式
    [XXX, XXX, XXX],  # Car
    [XXX, XXX, XXX],  # Truck
    [XXX, XXX, XXX]   # Bus
]
```
