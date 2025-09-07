# ISP知识库系统 - Python后端架构设计

## 📋 项目概述

ISP知识库系统后端服务，为前端React应用提供数据支持和AI智能问答功能。系统采用Python技术栈，集成QWEN大模型，提供完整的知识库管理、架构图展示和智能搜索功能。

## 🏗️ 技术架构

### 技术栈选择

- **Web框架**: FastAPI (高性能、自动API文档生成)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy (数据库操作)
- **AI模型**: QWEN (通义千问大模型)
- **缓存**: Redis (可选，用于性能优化)
- **认证**: JWT (JSON Web Token)
- **文档**: OpenAPI/Swagger (自动生成)
- **部署**: Docker + Nginx

### 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React前端     │    │   FastAPI后端    │    │   QWEN AI模型    │
│                 │◄──►│                 │◄──►│                 │
│ - 知识库展示     │    │ - RESTful API    │    │ - 智能问答       │
│ - 架构图展示     │    │ - 数据管理       │    │ - 内容生成       │
│ - AI聊天机器人   │    │ - 用户认证       │    │ - 搜索增强       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   数据库层       │
                       │                 │
                       │ - SQLite/PostgreSQL │
                       │ - Redis缓存      │
                       └─────────────────┘
```

## 🗄️ 数据库设计

### 核心数据表

#### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user', -- 'admin' | 'user'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 知识分类表 (knowledge_categories)
```sql
CREATE TABLE knowledge_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id VARCHAR(100) UNIQUE NOT NULL, -- 如 'camera-imaging'
    title VARCHAR(200) NOT NULL,               -- 如 '📷 相机成像原理'
    icon VARCHAR(50),                          -- 如 '📷'
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. 知识项表 (knowledge_items)
```sql
CREATE TABLE knowledge_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'completed', -- 'completed' | 'pending' | 'future'
    content TEXT,                            -- 详细内容
    external_link VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES knowledge_categories(category_id)
);
```

#### 4. 架构图版本表 (flow_versions)
```sql
CREATE TABLE flow_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id VARCHAR(100) UNIQUE NOT NULL, -- 如 'default', 'version1'
    title VARCHAR(200) NOT NULL,              -- 如 '标准版本'
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. 架构图模块表 (flow_modules)
```sql
CREATE TABLE flow_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id VARCHAR(100) NOT NULL,
    module_id VARCHAR(100) NOT NULL,          -- 如 'mipi-receiver'
    title VARCHAR(200) NOT NULL,               -- 如 'MIPI CSI-2接收器'
    description TEXT,
    module_type VARCHAR(50),                   -- 如 'sensor', 'processing'
    introduction TEXT,                         -- 模块简介
    principle TEXT,                           -- 实现原理
    constraints TEXT,                          -- 硬件约束
    external_link VARCHAR(500),
    position_x INTEGER,                        -- 在架构图中的X坐标
    position_y INTEGER,                        -- 在架构图中的Y坐标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES flow_versions(version_id)
);
```

#### 6. 聊天记录表 (chat_history)
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(36),
    session_id VARCHAR(100) NOT NULL,
    message_type VARCHAR(20) NOT NULL,        -- 'user' | 'assistant'
    content TEXT NOT NULL,
    response_time_ms INTEGER,                 -- 响应时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 7. 搜索记录表 (search_logs)
```sql
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(36),
    query VARCHAR(500) NOT NULL,
    result_count INTEGER,
    search_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 索引设计

```sql
-- 知识分类索引
CREATE INDEX idx_knowledge_categories_active ON knowledge_categories(is_active);
CREATE INDEX idx_knowledge_categories_sort ON knowledge_categories(sort_order);

-- 知识项索引
CREATE INDEX idx_knowledge_items_category ON knowledge_items(category_id);
CREATE INDEX idx_knowledge_items_status ON knowledge_items(status);
CREATE INDEX idx_knowledge_items_search ON knowledge_items(title, description);

-- 架构图模块索引
CREATE INDEX idx_flow_modules_version ON flow_modules(version_id);
CREATE INDEX idx_flow_modules_type ON flow_modules(module_type);

-- 聊天记录索引
CREATE INDEX idx_chat_history_session ON chat_history(session_id);
CREATE INDEX idx_chat_history_user ON chat_history(user_id);

-- 搜索记录索引
CREATE INDEX idx_search_logs_user ON search_logs(user_id);
CREATE INDEX idx_search_logs_query ON search_logs(query);
```

## 🔌 API接口设计

### 基础信息
- **基础URL**: `http://localhost:8000/api/v1`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Bearer Token

### 认证相关接口

#### 1. 用户登录
- **接口**: `POST /auth/login`
- **请求体**:
```json
{
    "username": "admin",
    "password": "password123"
}
```
- **响应**:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "email": "admin@example.com"
    }
}
```

#### 2. 用户注册
- **接口**: `POST /auth/register`
- **请求体**:
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123"
}
```

### 知识库管理接口

#### 1. 获取所有知识分类
- **接口**: `GET /knowledge/categories`
- **权限**: 无需认证
- **响应示例**:
```json
{
    "camera-imaging": {
        "title": "📷 相机成像原理",
        "icon": "📷",
        "items": [
            {
                "title": "光学系统",
                "description": "镜头组、光圈、焦距等光学元件组成成像系统",
                "status": "completed"
            }
        ]
    }
}
```

#### 2. 获取指定分类详情
- **接口**: `GET /knowledge/category/{category_id}`
- **权限**: 无需认证
- **响应**: 返回指定分类的完整信息

#### 3. 获取指定知识项详情
- **接口**: `GET /knowledge/item/{item_id}`
- **权限**: 无需认证
- **响应**: 返回知识项的详细信息

#### 4. 创建知识分类 (管理员)
- **接口**: `POST /knowledge/categories`
- **权限**: 需要管理员权限
- **请求体**:
```json
{
    "category_id": "new-category",
    "title": "新分类",
    "icon": "🚀",
    "description": "分类描述"
}
```

#### 5. 更新知识分类 (管理员)
- **接口**: `PUT /knowledge/categories/{category_id}`
- **权限**: 需要管理员权限

#### 6. 删除知识分类 (管理员)
- **接口**: `DELETE /knowledge/categories/{category_id}`
- **权限**: 需要管理员权限

### ISP架构图接口

#### 1. 获取所有版本
- **接口**: `GET /flow/versions`
- **权限**: 无需认证
- **响应示例**:
```json
{
    "default": "标准版本",
    "version1": "版本1",
    "version2": "版本2"
}
```

#### 2. 获取指定版本架构图
- **接口**: `GET /flow/version/{version_id}`
- **权限**: 无需认证
- **响应**: 返回指定版本的完整架构图数据

#### 3. 获取指定模块详情
- **接口**: `GET /flow/module/{module_id}`
- **权限**: 无需认证
- **响应**: 返回模块的详细信息

#### 4. 创建架构图版本 (管理员)
- **接口**: `POST /flow/versions`
- **权限**: 需要管理员权限

#### 5. 更新架构图版本 (管理员)
- **接口**: `PUT /flow/versions/{version_id}`
- **权限**: 需要管理员权限

### 搜索接口

#### 1. 搜索知识库内容
- **接口**: `GET /search?q={query}&type={type}&limit={limit}`
- **权限**: 无需认证
- **参数**:
  - `q`: 搜索关键词
  - `type`: 搜索类型 (knowledge|flow|all)
  - `limit`: 结果数量限制
- **响应示例**:
```json
{
    "query": "去马赛克",
    "total": 3,
    "results": [
        {
            "type": "knowledge",
            "category": "🔬 ISP处理算法",
            "title": "去马赛克",
            "description": "Demosaic算法从Bayer阵列重建全彩图像",
            "status": "completed"
        }
    ]
}
```

### AI聊天接口

#### 1. 发送聊天消息
- **接口**: `POST /chat/message`
- **权限**: 需要用户认证
- **请求体**:
```json
{
    "message": "什么是ISP？",
    "session_id": "session_123",
    "context": "previous_messages_context"
}
```
- **响应**:
```json
{
    "response": "ISP（图像信号处理器）是...",
    "session_id": "session_123",
    "response_time_ms": 1500,
    "sources": [
        {
            "type": "knowledge",
            "title": "ISP基础概念",
            "category": "📚 基础知识"
        }
    ]
}
```

#### 2. 获取聊天历史
- **接口**: `GET /chat/history?session_id={session_id}&limit={limit}`
- **权限**: 需要用户认证
- **响应**: 返回指定会话的聊天记录

### 管理接口

#### 1. 用户管理
- **接口**: `GET /admin/users` - 获取用户列表
- **接口**: `POST /admin/users` - 创建用户
- **接口**: `PUT /admin/users/{user_id}` - 更新用户
- **接口**: `DELETE /admin/users/{user_id}` - 删除用户
- **权限**: 需要管理员权限

#### 2. 系统统计
- **接口**: `GET /admin/stats`
- **权限**: 需要管理员权限
- **响应**:
```json
{
    "total_users": 150,
    "total_knowledge_items": 45,
    "total_chat_sessions": 1200,
    "total_searches": 850,
    "active_users_today": 25
}
```

## 🤖 AI集成设计

### QWEN模型集成

#### 模型配置
```python
# AI模型配置
QWEN_CONFIG = {
    "model_name": "qwen-turbo",  # 或 qwen-plus, qwen-max
    "api_key": "your_qwen_api_key",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9
}
```

#### 智能问答功能
1. **问题理解**: 分析用户问题类型和意图
2. **知识检索**: 从知识库中检索相关内容
3. **答案生成**: 基于检索结果生成回答
4. **来源引用**: 提供知识来源和参考链接

#### 搜索增强
1. **语义搜索**: 使用向量相似度搜索
2. **关键词匹配**: 传统关键词搜索
3. **混合排序**: 结合多种搜索策略

### 缓存策略

#### Redis缓存设计
```python
# 缓存键设计
CACHE_KEYS = {
    "knowledge_categories": "knowledge:categories",
    "knowledge_item": "knowledge:item:{item_id}",
    "flow_version": "flow:version:{version_id}",
    "flow_module": "flow:module:{module_id}",
    "search_result": "search:result:{query_hash}",
    "chat_session": "chat:session:{session_id}"
}

# 缓存过期时间
CACHE_TTL = {
    "knowledge": 3600,      # 1小时
    "flow": 1800,          # 30分钟
    "search": 300,         # 5分钟
    "chat": 1800          # 30分钟
}
```

## 🚀 部署方案

### 开发环境

#### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置文件
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=sqlite:///./isp_knowledge.db
# 或 PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/isp_knowledge

# QWEN API配置
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# JWT配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis配置 (可选)
REDIS_URL=redis://localhost:6379

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 3. 启动服务
```bash
# 初始化数据库
python scripts/init_db.py

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境

#### 1. Docker部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/isp_knowledge
      - QWEN_API_KEY=${QWEN_API_KEY}
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=isp_knowledge
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 3. Nginx配置
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
}
```

## 📊 性能优化

### 数据库优化
1. **索引优化**: 为常用查询字段创建索引
2. **查询优化**: 使用分页和限制结果数量
3. **连接池**: 使用数据库连接池管理连接

### 缓存优化
1. **Redis缓存**: 缓存热点数据
2. **内存缓存**: 使用Python内置缓存
3. **CDN**: 静态资源使用CDN加速

### API优化
1. **异步处理**: 使用FastAPI的异步特性
2. **批量操作**: 支持批量查询和更新
3. **压缩**: 启用Gzip压缩

## 🔒 安全设计

### 认证授权
1. **JWT认证**: 使用JWT进行用户认证
2. **角色权限**: 基于角色的访问控制
3. **API限流**: 防止API滥用

### 数据安全
1. **密码加密**: 使用bcrypt加密用户密码
2. **SQL注入防护**: 使用ORM防止SQL注入
3. **XSS防护**: 输入验证和输出编码

### 网络安全
1. **HTTPS**: 生产环境使用HTTPS
2. **CORS配置**: 正确配置跨域访问
3. **防火墙**: 配置网络防火墙规则

## 📈 监控日志

### 日志系统
```python
# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}
```

### 监控指标
1. **API性能**: 响应时间、吞吐量
2. **数据库性能**: 查询时间、连接数
3. **AI模型性能**: 响应时间、准确率
4. **系统资源**: CPU、内存、磁盘使用率

## 🧪 测试策略

### 单元测试
```python
# 使用pytest进行单元测试
pytest tests/unit/ -v
```

### 集成测试
```python
# 测试API接口
pytest tests/integration/ -v
```

### 性能测试
```python
# 使用locust进行压力测试
locust -f tests/performance/locustfile.py
```

## 📚 开发规范

### 代码规范
1. **PEP 8**: 遵循Python代码规范
2. **类型注解**: 使用类型提示
3. **文档字符串**: 为函数和类添加文档

### API规范
1. **RESTful设计**: 遵循REST API设计原则
2. **错误处理**: 统一的错误响应格式
3. **版本控制**: API版本管理策略

### 数据库规范
1. **命名规范**: 表名和字段名规范
2. **约束设计**: 合理的数据约束
3. **迁移管理**: 数据库版本管理

---

## 🎯 总结

本后端架构设计基于FastAPI和QWEN大模型，提供了完整的ISP知识库管理功能。系统具有良好的可扩展性、安全性和性能，支持从开发到生产的完整部署流程。

### 核心特性
- ✅ 完整的知识库CRUD操作
- ✅ ISP架构图版本管理
- ✅ 基于QWEN的智能问答
- ✅ 高性能搜索功能
- ✅ 用户权限管理
- ✅ 完整的API文档
- ✅ 生产级部署方案

### 技术亮点
- 🚀 FastAPI高性能异步框架
- 🤖 QWEN大模型智能集成
- 🔒 JWT认证和权限控制
- 📊 Redis缓存优化
- 🐳 Docker容器化部署
- 📈 完整的监控日志系统
