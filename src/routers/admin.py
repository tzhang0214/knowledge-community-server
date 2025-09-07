"""
管理员相关路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from src.database import get_db
from src.models import User, KnowledgeItem, ChatHistory
from src.schemas import UserCreate, UserResponse, SystemStats
from src.auth import get_current_admin_user, get_password_hash
from src.cache import clear_all_cache

router = APIRouter(prefix="/admin", tags=["管理"])


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(default=0, ge=0, description="跳过数量"),
    limit: int = Query(default=100, ge=1, le=1000, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（管理员）"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建用户（管理员）"""
    # 检查工号是否已存在
    existing_id = db.query(User).filter(User.id == user_data.id).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工号已存在"
        )
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        id=user_data.id,
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role="user"
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新字段
    for field, value in user_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除用户（管理员）"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取系统统计信息（管理员）"""
    # 总用户数
    total_users = db.query(User).count()
    
    # 总知识项数
    total_knowledge_items = db.query(KnowledgeItem).count()
    
    # 总聊天会话数
    total_chat_sessions = db.query(ChatHistory.session_id).distinct().count()
    
    # 总搜索次数（SearchLog已删除，设为0）
    total_searches = 0
    
    # 今日活跃用户数
    today = datetime.utcnow().date()
    active_users_today = db.query(ChatHistory.user_id).filter(
        func.date(ChatHistory.created_at) == today
    ).distinct().count()
    
    return SystemStats(
        total_users=total_users,
        total_knowledge_items=total_knowledge_items,
        total_chat_sessions=total_chat_sessions,
        total_searches=total_searches,
        active_users_today=active_users_today
    )


@router.get("/stats/daily")
async def get_daily_stats(
    days: int = Query(default=7, ge=1, le=30, description="天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取每日统计信息（管理员）"""
    stats = []
    
    for i in range(days):
        date = datetime.utcnow().date() - timedelta(days=i)
        
        # 当日新增用户
        new_users = db.query(User).filter(
            func.date(User.created_at) == date
        ).count()
        
        # 当日聊天消息数
        chat_messages = db.query(ChatHistory).filter(
            func.date(ChatHistory.created_at) == date
        ).count()
        
        # 当日搜索次数（SearchLog已删除，设为0）
        searches = 0
        
        stats.append({
            "date": date.isoformat(),
            "new_users": new_users,
            "chat_messages": chat_messages,
            "searches": searches
        })
    
    return {"daily_stats": stats}


@router.post("/cache/clear")
async def clear_cache(
    cache_type: str = Query(..., pattern="^(knowledge|flow|search|chat|all)$", description="缓存类型"),
    current_user: User = Depends(get_current_admin_user)
):
    """清除缓存（管理员）"""
    if cache_type == "all":
        clear_all_cache()
        message = "所有缓存已清除"
    elif cache_type == "knowledge":
        from src.cache import clear_knowledge_cache
        clear_knowledge_cache()
        message = "知识库缓存已清除"
    elif cache_type == "flow":
        from src.cache import clear_flow_cache
        clear_flow_cache()
        message = "架构图缓存已清除"
    elif cache_type == "search":
        from src.cache import clear_search_cache
        clear_search_cache()
        message = "搜索缓存已清除"
    elif cache_type == "chat":
        from src.cache import clear_chat_cache
        clear_chat_cache()
        message = "聊天缓存已清除"
    
    return {"message": message}


@router.get("/logs/chat")
async def get_chat_logs(
    skip: int = Query(default=0, ge=0, description="跳过数量"),
    limit: int = Query(default=100, ge=1, le=1000, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取聊天日志（管理员）"""
    logs = db.query(ChatHistory).join(User).order_by(
        ChatHistory.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "user": log.user.username if log.user else None,
                "session_id": log.session_id,
                "message_type": log.message_type,
                "content": log.content[:100] + "..." if len(log.content) > 100 else log.content,
                "response_time_ms": log.response_time_ms,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }
