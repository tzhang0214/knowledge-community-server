"""
Pydantic数据模型和API响应模式
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# 基础响应模型
class ResponseBase(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None


# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """用户创建模型"""
    id: str = Field(..., min_length=1, max_length=36, description="用户工号")
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应模型"""
    id: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 知识分类相关模型
class KnowledgeCategoryBase(BaseModel):
    """知识分类基础模型"""
    category_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., max_length=200)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    sort_order: int = 0


class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    """知识分类创建模型"""
    pass


class KnowledgeCategoryUpdate(BaseModel):
    """知识分类更新模型"""
    title: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class KnowledgeCategoryResponse(KnowledgeCategoryBase):
    """知识分类响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 知识项相关模型
class KnowledgeItemBase(BaseModel):
    """知识项基础模型"""
    category_id: str = Field(..., max_length=100)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: str = Field(default="completed", pattern="^(completed|pending|future)$")
    content: Optional[str] = None
    external_link: Optional[str] = Field(None, max_length=500)
    sort_order: int = 0


class KnowledgeItemCreate(KnowledgeItemBase):
    """知识项创建模型"""
    pass


class KnowledgeItemUpdate(BaseModel):
    """知识项更新模型"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(completed|pending|future)$")
    content: Optional[str] = None
    external_link: Optional[str] = Field(None, max_length=500)
    sort_order: Optional[int] = None


class KnowledgeItemResponse(KnowledgeItemBase):
    """知识项响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 聊天相关模型
class ChatMessage(BaseModel):
    """聊天消息模型"""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    session_id: str
    response_time_ms: int
    sources: Optional[List[Dict[str, Any]]] = None


class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    id: int
    user_id: Optional[str] = None
    session_id: str
    message_type: str
    content: str
    response_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 搜索相关模型
class SearchRequest(BaseModel):
    """搜索请求模型"""
    q: str = Field(..., min_length=1, description="搜索关键词")
    type: str = Field(default="all", pattern="^(knowledge|flow|all)$", description="搜索类型")
    limit: int = Field(default=10, ge=1, le=100, description="结果数量限制")


class SearchResult(BaseModel):
    """搜索结果模型"""
    type: str
    category: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    external_link: Optional[str] = None


class SearchResponse(BaseModel):
    """搜索响应模型"""
    query: str
    total: int
    results: List[SearchResult]


# 管理相关模型
class SystemStats(BaseModel):
    """系统统计模型"""
    total_users: int
    total_knowledge_items: int
    total_chat_sessions: int
    total_searches: int
    active_users_today: int


# 错误响应模型
class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
