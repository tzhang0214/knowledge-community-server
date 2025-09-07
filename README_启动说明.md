# ISP知识库系统启动脚本

## Windows (start_server.bat)
双击运行 `start_server.bat` 文件即可启动服务器

## Linux/Mac (start_server.sh)
```bash
chmod +x start_server.sh
./start_server.sh
```

## 环境变量说明
- `SECRET_KEY`: JWT签名密钥，用于token验证
- `QWEN_API_KEY`: 通义千问API密钥

## 使用说明
1. 确保已安装Python依赖：`pip install -r requirements.txt`
2. 运行对应的启动脚本
3. 服务器将在 http://localhost:8000 启动
4. API文档地址：http://localhost:8000/docs

## 测试认证
在Swagger UI中：
1. 访问 http://localhost:8000/docs
2. 点击 Authorize 按钮（🔒图标）
3. 输入测试token：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImV4cCI6MTc1NzMzMDcwNX0.JmC1jCKSu8a6OvGijYjcF2PmOV1Nv4ikCLDUhTZXczI`
4. 点击 Authorize 完成认证
