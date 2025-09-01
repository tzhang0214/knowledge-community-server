"""
数据库模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from src.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # 'admin' | 'user'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class KnowledgeCategory(Base):
    """知识分类表"""
    __tablename__ = "knowledge_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    icon = Column(String(50))
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class KnowledgeItem(Base):
    """知识项表"""
    __tablename__ = "knowledge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(String(100), ForeignKey("knowledge_categories.category_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="completed")  # 'completed' | 'pending' | 'future'
    content = Column(Text)
    external_link = Column(String(500))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowVersion(Base):
    """架构图版本表"""
    __tablename__ = "flow_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowModule(Base):
    """架构图模块表"""
    __tablename__ = "flow_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(100), ForeignKey("flow_versions.version_id"), nullable=False)
    module_id = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    module_type = Column(String(50))  # 'sensor', 'processing', etc.
    introduction = Column(Text)
    principle = Column(Text)
    constraints = Column(Text)
    external_link = Column(String(500))
    position_x = Column(Integer)
    position_y = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowArchitecture(Base):
    """架构图结构表"""
    __tablename__ = "flow_architectures"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), nullable=False)  # 'sensor', 'raw', 'rgb', 'yuv', 'output', 'memory'
    title = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FlowArchitectureItem(Base):
    """架构图模块项表"""
    __tablename__ = "flow_architecture_items"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), ForeignKey("flow_architectures.domain"), nullable=False)
    item_id = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    item_type = Column(String(50), nullable=False)  # 'sensor', 'raw', 'rgb', 'yuv', 'output', 'memory'
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatHistory(Base):
    """聊天记录表"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(100), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SearchLog(Base):
    """搜索记录表"""
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String(500), nullable=False)
    result_count = Column(Integer)
    search_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 创建索引
Index("idx_knowledge_categories_active", KnowledgeCategory.is_active)
Index("idx_knowledge_categories_sort", KnowledgeCategory.sort_order)
Index("idx_knowledge_items_category", KnowledgeItem.category_id)
Index("idx_knowledge_items_status", KnowledgeItem.status)
Index("idx_knowledge_items_search", KnowledgeItem.title, KnowledgeItem.description)
Index("idx_flow_modules_version", FlowModule.version_id)
Index("idx_flow_modules_type", FlowModule.module_type)
Index("idx_chat_history_session", ChatHistory.session_id)
Index("idx_chat_history_user", ChatHistory.user_id)
Index("idx_search_logs_user", SearchLog.user_id)
Index("idx_search_logs_query", SearchLog.query)
