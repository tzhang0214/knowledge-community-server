@echo off
echo 正在启动ISP知识库系统...

REM 设置环境变量
set SECRET_KEY=your_secret_key_here_make_it_long_and_random_1234567890abcdef
set QWEN_API_KEY=test_key

REM 启动服务器
python main.py

pause
