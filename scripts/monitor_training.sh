#!/bin/bash
# 训练进度监控脚本

echo "=========================================="
echo "  训练进度监控"
echo "=========================================="
echo ""

# 检查是否有训练进程在运行
if pgrep -f "train.py" > /dev/null; then
    echo "✅ 训练进程正在运行"
    echo ""
    
    # 显示最新的训练日志
    echo "📊 最新训练日志 (最后30行):"
    echo "----------------------------------------"
    logfile=$(ls -t outputs/logs/training_*.log 2>/dev/null | head -1)
    if [ -f "$logfile" ]; then
        tail -30 "$logfile"
        
        echo ""
        echo "----------------------------------------"
        echo "📈 训练指标摘要:"
        echo ""
        
        # 提取最近的验证IoU
        recent_iou=$(grep -E "Val.*IoU:" "$logfile" | tail -1 | grep -oP "IoU: \K[0-9.]+")
        if [ -n "$recent_iou" ]; then
            echo "  最新验证 IoU: $recent_iou ($(echo "$recent_iou * 100" | bc)%)"
        fi
        
        # 提取最佳IoU
        best_iou=$(grep "保存最佳模型" "$logfile" | tail -1 | grep -oP "IoU: \K[0-9.]+")
        if [ -n "$best_iou" ]; then
            echo "  当前最佳 IoU: $best_iou ($(echo "$best_iou * 100" | bc)%)"
        fi
        
        # 显示当前epoch
        current_epoch=$(grep -E "Epoch [0-9]+/[0-9]+" "$logfile" | tail -1 | grep -oP "Epoch \K[0-9]+")
        total_epochs=$(grep -E "Epoch [0-9]+/[0-9]+" "$logfile" | tail -1 | grep -oP "/\K[0-9]+")
        if [ -n "$current_epoch" ] && [ -n "$total_epochs" ]; then
            echo "  当前进度: Epoch $current_epoch / $total_epochs"
        fi
        
        # 检查是否达到目标
        if [ -n "$best_iou" ]; then
            target_iou=0.80
            current_iou_dec=$(echo "$best_iou" | awk '{printf "%.4f", $1}')
            if (( $(echo "$current_iou_dec >= $target_iou" | bc -l) )); then
                echo ""
                echo "🎉 恭喜! 已达到目标 IoU ≥ 80%"
            else
                gap=$(echo "$target_iou - $current_iou_dec" | bc)
                echo "  距离目标还差: $(echo "$gap * 100" | bc)%"
            fi
        fi
    else
        echo "未找到训练日志文件"
    fi
else
    echo "⚠️  没有检测到正在运行的训练进程"
    echo ""
    echo "如需启动训练,请运行:"
    echo "  bash scripts/train_best_model_continue.sh"
fi

echo ""
echo "=========================================="
echo "💡 其他命令:"
echo "  - 查看完整日志: tail -f outputs/logs/training_*.log"
echo "  - 查看GPU使用:  watch -n 1 nvidia-smi  # Linux"
echo "  - 查看GPU使用:  sudo powermetrics --samplers gpu_power  # macOS MPS"
echo "  - 停止训练:     pkill -f train.py"
echo "=========================================="
