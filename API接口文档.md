# 知识社区服务器 API 接口文档

## 概述

本文档描述了知识社区服务器的RESTful API接口，为前端开发提供完整的接口规范。

**基础URL**: `http://localhost:8000`  
**API版本**: v1  
**认证方式**: Bearer Token (JWT)

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": { ... }
}
```

## 认证接口

### 1. 用户注册
**POST** `/auth/register`

**请求体**:
```json
{
  "id": "user001",
  "username": "张三",
  "email": "zhangsan@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user001",
    "username": "张三",
    "email": "zhangsan@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2. 用户登录
**POST** `/auth/login`

**请求体**:
```json
{
  "id": "user001",
  "password": "password123"
}
```

**响应**: 同注册接口

### 3. 获取当前用户信息
**GET** `/auth/me`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": "user001",
  "username": "张三",
  "email": "zhangsan@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 知识库接口

### 1. 获取知识分类列表
**GET** `/knowledge/categories`

**响应**:
```json
{
  "camera-imaging": {
    "title": "📷 相机成像原理",
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "光学系统",
        "description": "镜头组、光圈、焦距等光学元件组成成像系统",
        "status": "completed"
      }
    ]
  },
  "isp-algorithms": {
    "title": "🔬 ISP处理算法",
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "title": "去马赛克",
        "description": "Demosaic算法从Bayer阵列重建全彩图像",
        "status": "completed"
      }
    ]
  }
}
```

### 2. 获取知识项详情
**GET** `/knowledge/item/{item_id}`

**路径参数**:
- `item_id`: 知识项ID (UUID格式)

**响应**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "category_id": "camera-imaging",
  "title": "光学系统",
  "description": "镜头组、光圈、焦距等光学元件组成成像系统",
  "status": "completed",
  "content": "详细的光学系统说明...",
  "sort_order": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 3. 创建知识项
**POST** `/knowledge/item`

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "category_id": "camera-imaging",
  "title": "新的知识项",
  "description": "知识项描述",
  "status": "completed",
  "content": "详细内容",
  "sort_order": 0
}
```

**响应**:
```json
{
  "message": "知识项创建成功",
  "item_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 4. 更新知识项
**PUT** `/knowledge/item/{item_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "status": "pending"
}
```

**响应**:
```json
{
  "message": "知识项更新成功"
}
```

### 5. 删除知识项
**DELETE** `/knowledge/item/{item_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "message": "知识项删除成功"
}
```

### 6. 搜索知识项
**GET** `/knowledge/search`

**查询参数**:
- `q`: 搜索关键词 (必需)
- `category_id`: 分类ID (可选)
- `status`: 状态筛选 (可选: completed, pending, future)

**响应**:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "category_id": "camera-imaging",
      "title": "光学系统",
      "description": "镜头组、光圈、焦距等光学元件组成成像系统",
      "status": "completed",
      "sort_order": 0
    }
  ],
  "total": 1
}
```

## 知识项详情接口

### 1. 获取知识项详情列表
**GET** `/knowledge/item/{item_id}/details`

**路径参数**:
- `item_id`: 知识项ID (UUID格式)

**响应**:
```json
[
  {
    "id": "detail-550e8400-e29b-41d4-a716-446655440001-001",
    "knowledge_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "镜头组",
    "description": "由多个透镜组成的光学系统，用于聚焦光线到传感器上",
    "external_link": "https://en.wikipedia.org/wiki/Camera_lens",
    "sort_order": 0,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 2. 创建知识项详情
**POST** `/knowledge/item/{item_id}/details`

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "新的详情项",
  "description": "详情描述",
  "external_link": "https://example.com",
  "sort_order": 0
}
```

**响应**:
```json
{
  "id": "detail-550e8400-e29b-41d4-a716-446655440001-002",
  "knowledge_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "新的详情项",
  "description": "详情描述",
  "external_link": "https://example.com",
  "sort_order": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 3. 更新知识项详情
**PUT** `/knowledge/detail/{detail_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "更新后的标题",
  "description": "更新后的描述"
}
```

**响应**:
```json
{
  "id": "detail-550e8400-e29b-41d4-a716-446655440001-001",
  "knowledge_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "更新后的标题",
  "description": "更新后的描述",
  "external_link": "https://en.wikipedia.org/wiki/Camera_lens",
  "sort_order": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. 删除知识项详情
**DELETE** `/knowledge/detail/{detail_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "message": "知识项详情删除成功"
}
```

### 5. 获取单个知识项详情
**GET** `/knowledge/detail/{detail_id}`

**路径参数**:
- `detail_id`: 详情ID (UUID格式)

**响应**:
```json
{
  "id": "detail-550e8400-e29b-41d4-a716-446655440001-001",
  "knowledge_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "镜头组",
  "description": "由多个透镜组成的光学系统，用于聚焦光线到传感器上",
  "external_link": "https://en.wikipedia.org/wiki/Camera_lens",
  "sort_order": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 聊天接口

### 1. 发送聊天消息
**POST** `/chat/message`

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "message": "什么是相机成像原理？",
  "session_id": "session-123",
  "context": "用户上下文信息"
}
```

**响应**:
```json
{
  "response": "相机成像原理是指光线通过镜头系统聚焦到感光元件上...",
  "session_id": "session-123",
  "response_time_ms": 1500,
  "sources": [
    {
      "type": "knowledge",
      "title": "光学系统",
      "category": "📷 相机成像原理",
      "external_link": "https://en.wikipedia.org/wiki/Camera_lens"
    }
  ]
}
```

### 2. 获取聊天历史
**GET** `/chat/history`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `session_id`: 会话ID (可选)
- `limit`: 消息数量限制 (默认50, 最大200)

**响应**:
```json
[
  {
    "id": "chat-001",
    "user_id": "user001",
    "session_id": "session-123",
    "message_type": "user",
    "content": "什么是相机成像原理？",
    "response_time_ms": null,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": "chat-002",
    "user_id": "user001",
    "session_id": "session-123",
    "message_type": "assistant",
    "content": "相机成像原理是指光线通过镜头系统聚焦到感光元件上...",
    "response_time_ms": 1500,
    "created_at": "2024-01-01T00:00:01Z"
  }
]
```

### 3. 获取聊天会话列表
**GET** `/chat/sessions`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `limit`: 会话数量限制 (默认20, 最大100)

**响应**:
```json
{
  "sessions": [
    {
      "session_id": "session-123",
      "last_message": "什么是相机成像原理？",
      "last_message_type": "user",
      "last_message_time": "2024-01-01T00:00:00Z",
      "message_count": 10
    }
  ]
}
```

### 4. 删除聊天会话
**DELETE** `/chat/session/{session_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "message": "删除了 10 条消息"
}
```

### 5. 流式聊天消息
**POST** `/chat/stream`

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**: 同发送聊天消息

**响应**: 同发送聊天消息 (目前返回普通响应，未来可扩展为WebSocket流式响应)

## 搜索接口

### 1. 全局搜索
**GET** `/search`

**查询参数**:
- `q`: 搜索关键词 (必需)
- `type`: 搜索类型 (可选: knowledge, flow, all, 默认all)
- `limit`: 结果数量限制 (默认10, 最大100)

**响应**:
```json
{
  "query": "相机成像",
  "total": 5,
  "results": [
    {
      "type": "knowledge",
      "category": "📷 相机成像原理",
      "title": "光学系统",
      "description": "镜头组、光圈、焦距等光学元件组成成像系统",
      "status": "completed",
      "external_link": "https://en.wikipedia.org/wiki/Camera_lens"
    }
  ]
}
```

## 管理接口

### 1. 获取系统统计
**GET** `/admin/stats`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "total_users": 100,
  "total_knowledge_items": 500,
  "total_chat_sessions": 1000,
  "total_searches": 5000,
  "active_users_today": 50
}
```

## 错误码说明

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| INVALID_TOKEN | 401 | 无效的访问令牌 |
| TOKEN_EXPIRED | 401 | 访问令牌已过期 |
| USER_NOT_FOUND | 404 | 用户不存在 |
| KNOWLEDGE_ITEM_NOT_FOUND | 404 | 知识项不存在 |
| KNOWLEDGE_DETAIL_NOT_FOUND | 404 | 知识项详情不存在 |
| CATEGORY_NOT_FOUND | 404 | 分类不存在 |
| PERMISSION_DENIED | 403 | 权限不足 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## 数据模型

### 用户模型 (User)
```json
{
  "id": "string (UUID)",
  "username": "string (3-50字符)",
  "email": "string (可选, 最大100字符)",
  "password_hash": "string (内部使用)",
  "role": "string (user|admin)",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 知识分类模型 (KnowledgeCategory)
```json
{
  "id": "string (UUID)",
  "category_id": "string (唯一标识符)",
  "title": "string (最大200字符)",
  "icon": "string (可选, 最大50字符)",
  "description": "string (可选)",
  "sort_order": "integer",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 知识项模型 (KnowledgeItem)
```json
{
  "id": "string (UUID)",
  "category_id": "string (外键)",
  "title": "string (最大200字符)",
  "description": "string (可选)",
  "status": "string (completed|pending|future)",
  "content": "string (可选)",
  "sort_order": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 知识项详情模型 (KnowledgeDetail)
```json
{
  "id": "string (UUID)",
  "knowledge_id": "string (外键)",
  "title": "string (最大200字符)",
  "description": "string (可选)",
  "external_link": "string (可选, 最大500字符)",
  "sort_order": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 聊天记录模型 (ChatHistory)
```json
{
  "id": "string (UUID)",
  "user_id": "string (外键, 可选)",
  "session_id": "string (最大100字符)",
  "message_type": "string (user|assistant)",
  "content": "string",
  "response_time_ms": "integer (可选)",
  "created_at": "datetime"
}
```

## 使用示例

### JavaScript/TypeScript 示例

```typescript
// 用户登录
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    id: 'user001',
    password: 'password123'
  })
});

const { access_token } = await loginResponse.json();

// 获取知识分类
const categoriesResponse = await fetch('/knowledge/categories', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const categories = await categoriesResponse.json();

// 发送聊天消息
const chatResponse = await fetch('/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    message: '什么是相机成像原理？',
    session_id: 'session-123'
  })
});

const chatResult = await chatResponse.json();
```

### Python 示例

```python
import requests

# 用户登录
login_data = {
    "id": "user001",
    "password": "password123"
}
response = requests.post('http://localhost:8000/auth/login', json=login_data)
access_token = response.json()['access_token']

# 获取知识分类
headers = {'Authorization': f'Bearer {access_token}'}
categories = requests.get('http://localhost:8000/knowledge/categories', headers=headers)

# 发送聊天消息
chat_data = {
    "message": "什么是相机成像原理？",
    "session_id": "session-123"
}
chat_response = requests.post(
    'http://localhost:8000/chat/message', 
    json=chat_data, 
    headers=headers
)
```

## 注意事项

1. **认证**: 除了登录和注册接口外，所有接口都需要在请求头中携带有效的JWT token
2. **UUID格式**: 所有ID字段都使用UUID格式 (36字符)
3. **时间格式**: 所有时间字段都使用ISO 8601格式 (UTC时间)
4. **分页**: 搜索和列表接口支持limit参数控制返回数量
5. **缓存**: 知识库相关接口使用了缓存机制，数据更新后会自动清除相关缓存
6. **错误处理**: 所有接口都返回统一的错误格式，前端需要根据错误码进行相应处理

## 更新日志

- **v1.0.0** (2024-01-01): 初始版本，包含基础的知识库和聊天功能
- **v1.1.0** (2024-01-15): 添加知识项详情管理功能
- **v1.2.0** (2024-02-01): 优化搜索功能，添加全局搜索接口
