"""
搜索相关路由
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.database import get_db
from src.models import KnowledgeItem, KnowledgeCategory, FlowModule, FlowVersion, SearchLog
from src.schemas import SearchRequest, SearchResponse, SearchResult
from src.auth import get_current_user, get_current_active_user
from src.cache import get_cached_search_result, set_cached_search_result
from src.ai_service import ai_service

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    type: str = Query(default="all", pattern="^(knowledge|flow|all)$", description="搜索类型"),
    limit: int = Query(default=10, ge=1, le=100, description="结果数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """搜索知识库内容"""
    start_time = time.time()
    
    # 尝试从缓存获取
    cache_key = f"{q}_{type}_{limit}"
    cached_result = get_cached_search_result(cache_key)
    if cached_result:
        return SearchResponse(**cached_result)
    
    results = []
    
    # 搜索知识项
    if type in ["knowledge", "all"]:
        knowledge_results = search_knowledge(db, q, limit)
        results.extend(knowledge_results)
    
    # 搜索架构图模块
    if type in ["flow", "all"]:
        flow_results = search_flow(db, q, limit)
        results.extend(flow_results)
    
    # 按相关性排序（简单实现）
    results = sorted(results, key=lambda x: x.get("relevance", 0), reverse=True)
    
    # 限制结果数量
    results = results[:limit]
    
    # 记录搜索日志
    search_time = int((time.time() - start_time) * 1000)
    search_log = SearchLog(
        user_id=current_user.id,
        query=q,
        result_count=len(results),
        search_time_ms=search_time
    )
    db.add(search_log)
    db.commit()
    
    # 缓存结果
    result_data = {
        "query": q,
        "total": len(results),
        "results": results
    }
    set_cached_search_result(cache_key, result_data)
    
    return SearchResponse(
        query=q,
        total=len(results),
        results=results
    )


def search_knowledge(db: Session, query: str, limit: int) -> List[SearchResult]:
    """搜索知识项"""
    results = []
    
    # 构建搜索条件
    search_conditions = or_(
        KnowledgeItem.title.contains(query),
        KnowledgeItem.description.contains(query),
        KnowledgeItem.content.contains(query)
    )
    
    # 执行搜索
    items = db.query(KnowledgeItem).join(KnowledgeCategory).filter(
        search_conditions,
        KnowledgeCategory.is_active == True
    ).limit(limit).all()
    
    for item in items:
        # 计算相关性分数（简单实现）
        relevance = calculate_relevance(item, query)
        
        results.append(SearchResult(
            type="knowledge",
            category=item.category.title if item.category else None,
            title=item.title,
            description=item.description,
            status=item.status,
            external_link=item.external_link,
            relevance=relevance
        ))
    
    return results


def search_flow(db: Session, query: str, limit: int) -> List[SearchResult]:
    """搜索架构图模块"""
    results = []
    
    # 构建搜索条件
    search_conditions = or_(
        FlowModule.title.contains(query),
        FlowModule.description.contains(query),
        FlowModule.introduction.contains(query),
        FlowModule.principle.contains(query)
    )
    
    # 执行搜索
    modules = db.query(FlowModule).join(FlowVersion).filter(
        search_conditions,
        FlowVersion.is_active == True
    ).limit(limit).all()
    
    for module in modules:
        # 计算相关性分数
        relevance = calculate_relevance(module, query)
        
        results.append(SearchResult(
            type="flow",
            category=module.version.title if module.version else None,
            title=module.title,
            description=module.description,
            external_link=module.external_link,
            relevance=relevance
        ))
    
    return results


def calculate_relevance(item, query: str) -> float:
    """计算相关性分数"""
    # 简单的相关性计算
    query_lower = query.lower()
    title_score = 0
    desc_score = 0
    
    # 标题匹配权重更高
    if hasattr(item, 'title') and item.title:
        if query_lower in item.title.lower():
            title_score = 1.0
        elif any(word in item.title.lower() for word in query_lower.split()):
            title_score = 0.5
    
    # 描述匹配
    if hasattr(item, 'description') and item.description:
        if query_lower in item.description.lower():
            desc_score = 0.8
        elif any(word in item.description.lower() for word in query_lower.split()):
            desc_score = 0.3
    
    # 内容匹配
    content_score = 0
    if hasattr(item, 'content') and item.content:
        if query_lower in item.content.lower():
            content_score = 0.6
        elif any(word in item.content.lower() for word in query_lower.split()):
            content_score = 0.2
    
    return title_score + desc_score + content_score


@router.get("/enhanced", response_model=SearchResponse)
async def enhanced_search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    type: str = Query(default="all", pattern="^(knowledge|flow|all)$", description="搜索类型"),
    limit: int = Query(default=10, ge=1, le=100, description="结果数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI增强搜索"""
    # 先执行基础搜索
    basic_results = await search(q, type, limit, db, current_user)
    
    # 使用AI增强搜索结果
    if basic_results.results:
        enhanced_response = await ai_service.search_enhancement(q, basic_results.results)
        
        if enhanced_response.get("success"):
            # 添加AI增强的解释
            enhanced_explanation = enhanced_response.get("response", "")
            basic_results.ai_enhancement = enhanced_explanation
    
    return basic_results


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取搜索建议"""
    suggestions = []
    
    # 从知识项标题中获取建议
    knowledge_suggestions = db.query(KnowledgeItem.title).filter(
        KnowledgeItem.title.contains(q)
    ).limit(5).all()
    
    for suggestion in knowledge_suggestions:
        suggestions.append(suggestion[0])
    
    # 从架构图模块标题中获取建议
    flow_suggestions = db.query(FlowModule.title).filter(
        FlowModule.title.contains(q)
    ).limit(5).all()
    
    for suggestion in flow_suggestions:
        suggestions.append(suggestion[0])
    
    # 去重并限制数量
    suggestions = list(set(suggestions))[:10]
    
    return {"suggestions": suggestions}


@router.get("/popular")
async def get_popular_searches(
    limit: int = Query(default=10, ge=1, le=50, description="结果数量限制"),
    db: Session = Depends(get_db)
):
    """获取热门搜索"""
    # 统计搜索频率
    popular_searches = db.query(
        SearchLog.query,
        db.func.count(SearchLog.id).label('count')
    ).group_by(SearchLog.query).order_by(
        db.func.count(SearchLog.id).desc()
    ).limit(limit).all()
    
    return {
        "popular_searches": [
            {"query": item.query, "count": item.count}
            for item in popular_searches
        ]
    }
