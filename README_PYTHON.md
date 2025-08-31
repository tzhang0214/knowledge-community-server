# ISP知识库系统 - Python后端实现

这是基于FastAPI和QWEN大模型的ISP知识库系统后端服务，提供完整的知识库管理、架构图展示和AI智能问答功能。

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd knowledge-community-server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp env.example .env

# 编辑 .env 文件，配置以下参数：
# - QWEN_API_KEY: 你的QWEN API密钥
# - SECRET_KEY: JWT密钥（建议使用长随机字符串）
# - DATABASE_URL: 数据库连接URL
# - REDIS_URL: Redis连接URL（可选）
```

### 3. 初始化数据库

```bash
# 使用启动脚本初始化
python start.py --init-db

# 或直接运行初始化脚本
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 使用启动脚本
python start.py

# 或直接使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问服务

- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 📁 项目结构

```
knowledge-community-server/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── models.py          # 数据模型
│   ├── schemas.py         # Pydantic模式
│   ├── auth.py            # 认证授权
│   ├── ai_service.py      # AI服务
│   ├── cache.py           # 缓存管理
│   └── routers/           # API路由
│       ├── auth.py        # 认证路由
│       ├── knowledge.py   # 知识库路由
│       ├── flow.py        # 架构图路由
│       ├── search.py      # 搜索路由
│       ├── chat.py        # 聊天路由
│       └── admin.py       # 管理路由
├── scripts/               # 脚本工具
│   └── init_db.py         # 数据库初始化
├── tests/                 # 测试文件
│   └── test_auth.py       # 认证测试
├── main.py               # 主应用
├── start.py              # 启动脚本
├── requirements.txt      # 依赖列表
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose
└── README_PYTHON.md      # 本文档
```

## 🔧 核心功能

### 1. 用户认证
- JWT Token认证
- 用户注册/登录
- 角色权限管理（admin/user）

### 2. 知识库管理
- 知识分类CRUD操作
- 知识项CRUD操作
- 分类层级管理
- 状态管理（completed/pending/future）

### 3. 架构图管理
- 架构图版本管理
- 模块CRUD操作
- 位置坐标管理
- 模块类型分类

### 4. 智能搜索
- 关键词搜索
- 语义搜索增强
- 搜索建议
- 热门搜索统计

### 5. AI聊天
- 基于QWEN的智能问答
- 聊天历史管理
- 会话管理
- 知识上下文集成

### 6. 系统管理
- 用户管理
- 系统统计
- 日志查看
- 缓存管理

## 🗄️ 数据库设计

### 核心表结构
- `users`: 用户表
- `knowledge_categories`: 知识分类表
- `knowledge_items`: 知识项表
- `flow_versions`: 架构图版本表
- `flow_modules`: 架构图模块表
- `chat_history`: 聊天记录表
- `search_logs`: 搜索记录表

## 🔌 API接口

### 基础信息
- 基础URL: `http://localhost:8000/api/v1`
- 认证方式: JWT Bearer Token
- 数据格式: JSON

### 主要接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /knowledge/categories` - 获取知识分类
- `GET /flow/versions` - 获取架构图版本
- `GET /search` - 搜索内容
- `POST /chat/message` - 发送聊天消息
- `GET /admin/stats` - 系统统计

## 🤖 AI集成

### QWEN模型配置
```python
QWEN_CONFIG = {
    "model_name": "qwen-turbo",
    "api_key": "your_qwen_api_key",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9
}
```

### 功能特性
- 智能问答
- 搜索增强
- 关键词提取
- 文本相似度计算

## 🚀 部署方案

### 开发环境
```bash
# 直接运行
python start.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker部署
```bash
# 构建镜像
docker build -t isp-knowledge-server .

# 运行容器
docker run -p 8000:8000 isp-knowledge-server

# 或使用Docker Compose
docker-compose up -d
```

### 生产环境
```bash
# 使用gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用uvicorn生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🧪 测试

```bash
# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_auth.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 📊 监控日志

### 日志配置
- 日志级别: INFO
- 日志文件: logs/app.log
- 日志轮转: 10MB/5个备份

### 监控指标
- API响应时间
- 数据库查询性能
- AI模型响应时间
- 系统资源使用率

## 🔒 安全特性

### 认证授权
- JWT Token认证
- 密码bcrypt加密
- 角色权限控制
- API访问限流

### 数据安全
- SQL注入防护
- XSS防护
- 输入验证
- 输出编码

## 📈 性能优化

### 缓存策略
- Redis缓存热点数据
- 内存缓存装饰器
- 缓存键设计优化
- TTL过期管理

### 数据库优化
- 索引优化
- 查询优化
- 连接池管理
- 分页查询

## 🛠️ 开发工具

### 代码规范
- PEP 8代码风格
- 类型注解
- 文档字符串
- 错误处理

### 调试工具
- FastAPI自动文档
- 日志调试
- 数据库调试
- API测试

## 📝 默认用户

初始化数据库后会创建以下默认用户：

- **管理员**: admin / admin123
- **测试用户**: testuser / test123

## 🔧 配置说明

### 环境变量
```env
# 数据库配置
DATABASE_URL=sqlite:///./isp_knowledge.db

# QWEN API配置
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# JWT配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis配置
REDIS_URL=redis://localhost:6379

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 📚 相关文档

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [QWEN API文档](https://help.aliyun.com/zh/dashscope/)
- [Redis文档](https://redis.io/documentation)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。

---

## 🎯 总结

这个Python实现提供了完整的ISP知识库系统后端服务，具有以下特点：

- ✅ 完整的RESTful API
- ✅ 基于QWEN的AI智能问答
- ✅ 高性能缓存系统
- ✅ 完整的用户权限管理
- ✅ 生产级部署方案
- ✅ 完整的测试覆盖
- ✅ 详细的文档说明

项目采用现代化的Python技术栈，具有良好的可扩展性、安全性和性能，适合从开发到生产的完整部署流程。
