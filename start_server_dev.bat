@echo off
echo 正在启动ISP知识库系统...

REM 设置环境变量
set DATABASE_URL=sqlite:///./isp_knowledge.db
set QWEN_API_KEY=dummy_key_for_testing
set SECRET_KEY=your_secret_key_here_must_be_very_long_and_random_string_for_jwt_token_generation
set ALGORITHM=HS256
set ACCESS_TOKEN_EXPIRE_MINUTES=30
set HOST=0.0.0.0
set PORT=8000
set DEBUG=true
set LOG_LEVEL=INFO
set LOG_FILE=logs/app.log

REM 创建日志目录
if not exist logs mkdir logs

REM 启动服务
python main.py

pause
