#!/bin/bash
# 训练完成后自动推理验证集的完整流程

# 切换到项目根目录
cd "$(dirname "$0")/.."

echo "========================================"
echo "道路车辆分割系统 - 训练+推理流程"
echo "========================================"
echo ""

# 检查模型是否存在
if [ ! -f "outputs/checkpoints/best_model.pth" ]; then
    echo "未找到训练好的模型，开始训练..."
    echo ""

    # 训练选项
    echo "请选择训练模式:"
    echo "1) 快速训练 (~2小时) - 推荐"
    echo "2) 标准训练 (~3小时)"
    echo "3) 完整训练 (~60小时)"
    read -p "请输入选项 (1-3): " train_choice

    case $train_choice in
        1)
            python3 train.py \
                --batch_size 8 \
                --epochs 20 \
                --use_gpu True \
                --subset_ratio 0.1125 \
                --save_interval 5 \
                --num_workers 0
            ;;
        2)
            python3 train.py \
                --batch_size 8 \
                --epochs 30 \
                --use_gpu True \
                --subset_ratio 0.2 \
                --save_interval 10 \
                --num_workers 0
            ;;
        3)
            python3 train.py \
                --batch_size 8 \
                --epochs 50 \
                --use_gpu True \
                --subset_ratio 1.0 \
                --save_interval 10 \
                --num_workers 0
            ;;
        *)
            echo "无效选项，退出"
            exit 1
            ;;
    esac

    echo ""
    echo "✓ 训练完成!"
fi

echo ""
echo "========================================"
echo "开始推理验证集"
echo "========================================"
echo ""

# 推理验证集
read -p "可视化样本数量 (默认20): " num_samples
num_samples=${num_samples:-20}

echo ""
echo "对验证集进行推理..."
python3 inference.py \
    --model_path outputs/checkpoints/best_model.pth \
    --split val \
    --num_samples $num_samples \
    --device mps

echo ""
echo "========================================"
echo "✓ 流程完成!"
echo "========================================"
echo ""
echo "结果查看:"
echo "  可视化结果: outputs/visualizations/val/"
echo "  训练日志: tensorboard --logdir outputs/logs"
echo ""
echo "其他操作:"
echo "  推理测试集: python3 inference.py --split test"
echo "  查看单张图: python3 inference.py --image_path <路径>"
