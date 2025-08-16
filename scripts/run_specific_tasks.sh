#!/bin/bash

# 简单的任务运行脚本
# 使用方法: ./run_specific_tasks.sh 0,1,2 (按数组索引)

TASK_INDICES=$1

if [ -z "$TASK_INDICES" ]; then
    echo "使用方法: $0 <task_indices>"
    echo "示例: $0 0,1,2    # 运行数组中前3个任务"
    echo "      $0 5,10,15  # 运行数组中第6、11、16个任务"
    echo "注意: 索引从0开始"
    exit 1
fi

cd evaluate

echo "运行任务索引: $TASK_INDICES"

python evaluate.py \
    --input_path ../data/test_809.json \
    --model_name "gpt-4o-mini" \
    --total_count 1 \
    --cur_count 1 \
    --task_ids "$TASK_INDICES"

cd ..