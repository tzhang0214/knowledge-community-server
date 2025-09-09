#!/bin/bash
echo "正在启动ISP知识库系统..."

# 设置环境变量
export SECRET_KEY="your_secret_key_here_make_it_long_and_random_1234567890abcdef"
export QWEN_API_KEY="test_key"

# 启动服务器（生产模式，无reload）
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning
