"""
聊天相关路由
"""
import time
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import ChatHistory, User, KnowledgeItem, KnowledgeCategory
from src.schemas import ChatMessage, ChatResponse, ChatHistoryResponse
from src.ai_service import ai_service
from src.cache import get_cached_chat_session, set_cached_chat_session

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    message_data: ChatMessage,
    request: Request,
    db: Session = Depends(get_db)
):
    """发送聊天消息"""
    # 从中间件获取用户信息
    user_info = request.state.user
    current_user_id = user_info['id']
    
    start_time = time.time()
    
    # 生成或使用会话ID
    session_id = message_data.session_id or str(uuid.uuid4())
    
    # 获取聊天历史
    chat_history = get_chat_history_for_session(db, session_id, current_user_id)
    
    # 构建知识上下文
    knowledge_context = build_knowledge_context(db, message_data.message)
    
    # 调用AI服务生成回答
    ai_response = await ai_service.generate_answer(
        question=message_data.message,
        knowledge_context=knowledge_context,
        chat_history=chat_history
    )
    
    if not ai_response.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"AI服务错误: {ai_response.get('error', '未知错误')}"
        )
    
    # 保存用户消息
    user_message = ChatHistory(
        user_id=current_user_id,
        session_id=session_id,
        message_type="user",
        content=message_data.message
    )
    db.add(user_message)
    
    # 保存AI回复
    ai_message = ChatHistory(
        user_id=current_user_id,
        session_id=session_id,
        message_type="assistant",
        content=ai_response["response"],
        response_time_ms=ai_response["response_time_ms"]
    )
    db.add(ai_message)
    
    db.commit()
    
    # 构建响应
    response = ChatResponse(
        response=ai_response["response"],
        session_id=session_id,
        response_time_ms=ai_response["response_time_ms"],
        sources=get_knowledge_sources(db, knowledge_context)
    )
    
    # 缓存会话
    set_cached_chat_session(session_id, {
        "user_id": current_user_id,
        "last_message": message_data.message,
        "last_response": ai_response["response"]
    })
    
    return response


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    request: Request,
    session_id: Optional[str] = Query(None, description="会话ID"),
    limit: int = Query(default=50, ge=1, le=200, description="消息数量限制"),
    db: Session = Depends(get_db)
):
    """获取聊天历史"""
    # 从中间件获取用户信息
    user_info = request.state.user
    current_user_id = user_info['id']
    
    query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user_id)
    
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)
    
    messages = query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    # 按时间正序返回
    messages.reverse()
    
    return [ChatHistoryResponse.from_orm(msg) for msg in messages]


@router.get("/sessions")
async def get_chat_sessions(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100, description="会话数量限制"),
    db: Session = Depends(get_db)
):
    """获取聊天会话列表"""
    # 从中间件获取用户信息
    user_info = request.state.user
    current_user_id = user_info['id']
    
    # 获取用户的会话列表
    sessions = db.query(ChatHistory.session_id).filter(
        ChatHistory.user_id == current_user_id
    ).distinct().limit(limit).all()
    
    session_list = []
    for session in sessions:
        session_id = session.session_id
        
        # 获取会话的最后一条消息
        last_message = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id,
            ChatHistory.user_id == current_user_id
        ).order_by(ChatHistory.created_at.desc()).first()
        
        if last_message:
            session_list.append({
                "session_id": session_id,
                "last_message": last_message.content,
                "last_message_type": last_message.message_type,
                "last_message_time": last_message.created_at,
                "message_count": db.query(ChatHistory).filter(
                    ChatHistory.session_id == session_id,
                    ChatHistory.user_id == current_user_id
                ).count()
            })
    
    return {"sessions": session_list}


@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    # 从中间件获取用户信息
    user_info = request.state.user
    current_user_id = user_info['id']
    
    # 删除会话中的所有消息
    deleted_count = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id,
        ChatHistory.user_id == current_user_id
    ).delete()
    
    db.commit()
    
    return {"message": f"删除了 {deleted_count} 条消息"}


def get_chat_history_for_session(db: Session, session_id: str, user_id: str) -> List[dict]:
    """获取会话的聊天历史"""
    messages = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id,
        ChatHistory.user_id == user_id
    ).order_by(ChatHistory.created_at).limit(10).all()  # 限制历史消息数量
    
    return [
        {
            "role": "user" if msg.message_type == "user" else "assistant",
            "content": msg.content
        }
        for msg in messages
    ]


def build_knowledge_context(db: Session, question: str) -> str:
    """构建知识上下文"""
    # 简单的关键词匹配来查找相关知识
    keywords = ai_service.extract_keywords(question)
    
    context_parts = []
    
    for keyword in keywords[:3]:  # 限制关键词数量
        # 搜索知识项
        items = db.query(KnowledgeItem).join(KnowledgeCategory).filter(
            KnowledgeItem.title.contains(keyword),
            KnowledgeCategory.is_active == True
        ).limit(2).all()
        
        for item in items:
            context_parts.append(f"知识项: {item.title}\n{item.description or ''}")
    
    return "\n\n".join(context_parts) if context_parts else ""


def get_knowledge_sources(db: Session, knowledge_context: str) -> List[dict]:
    """获取知识来源"""
    sources = []
    
    if not knowledge_context:
        return sources
    
    # 从上下文中提取知识项标题
    lines = knowledge_context.split('\n')
    for line in lines:
        if line.startswith("知识项: "):
            title = line.replace("知识项: ", "").strip()
            
            # 查找对应的知识项
            item = db.query(KnowledgeItem).join(KnowledgeCategory).filter(
                KnowledgeItem.title == title
            ).first()
            
            if item:
                sources.append({
                    "type": "knowledge",
                    "title": item.title,
                    "category": item.category.title if item.category else None,
                    "external_link": item.external_link
                })
    
    return sources


@router.post("/stream")
async def stream_chat_message(
    message_data: ChatMessage,
    request: Request,
    db: Session = Depends(get_db)
):
    """流式聊天消息（WebSocket实现的基础）"""
    # 这里可以实现WebSocket流式响应
    # 目前返回普通响应
    return await send_chat_message(message_data, request, db)
