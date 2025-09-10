"""
知识库相关路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database import get_db
from src.models import KnowledgeCategory, KnowledgeItem, KnowledgeDetail, User
from src.schemas import KnowledgeItemCreate, KnowledgeItemUpdate, KnowledgeDetailCreate, KnowledgeDetailUpdate, KnowledgeDetailResponse
from src.cache import (
    get_cached_knowledge_categories, set_cached_knowledge_categories,
    get_cached_knowledge_item, set_cached_knowledge_item,
    clear_knowledge_cache
)

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/categories")
async def get_knowledge_categories(
    db: Session = Depends(get_db)
):
    """获取知识分类列表"""
    # 尝试从缓存获取
    cached_data = get_cached_knowledge_categories()
    if cached_data:
        return cached_data
    
    try:
        # 查询所有活跃的分类
        categories = db.query(KnowledgeCategory).filter(
            KnowledgeCategory.is_active == True
        ).order_by(KnowledgeCategory.sort_order).all()
        
        # 构建返回数据结构
        result = {}
        for category in categories:
            # 查询该分类下的知识项
            items = db.query(KnowledgeItem).filter(
                KnowledgeItem.category_id == category.id
            ).order_by(KnowledgeItem.sort_order).all()
            
            # 构建知识项列表
            item_list = []
            for item in items:
                item_list.append({
                    "id": item.id,  # 使用UUID格式的id
                    "title": item.title,
                    "description": item.description,
                    "status": item.status
                })
            
            result[category.id] = {
                "title": category.title,
                "items": item_list
            }
        
        # 设置缓存
        set_cached_knowledge_categories(result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识分类失败: {str(e)}")


@router.get("/item/{item_id}")
async def get_knowledge_item(
    item_id: str, 
    db: Session = Depends(get_db)
):
    """根据ID获取知识项详情"""
    # 尝试从缓存获取
    cached_data = get_cached_knowledge_item(item_id)
    if cached_data:
        return cached_data
    
    try:
        # 查询知识项
        item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="知识项不存在")
        
        # 构建返回数据
        result = {
            "category_id": item.category_id,
            "title": item.title,
            "description": item.description,
            "status": item.status,
            "content": item.content,
            "sort_order": item.sort_order,
            "id": item.id,  # 使用UUID格式的id
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None
        }
        
        # 设置缓存
        set_cached_knowledge_item(item_id, result)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识项失败: {str(e)}")


@router.post("/item")
async def create_knowledge_item(
    item: KnowledgeItemCreate, 
    db: Session = Depends(get_db)
):
    """创建知识项"""
    try:
        # 验证分类是否存在
        category = db.query(KnowledgeCategory).filter(
            KnowledgeCategory.id == item.category_id
        ).first()
        if not category:
            raise HTTPException(status_code=400, detail="指定的分类不存在")
        
        # 创建知识项
        db_item = KnowledgeItem(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # 清除相关缓存
        clear_knowledge_cache()
        
        return {
            "message": "知识项创建成功",
            "item_id": db_item.id  # 返回UUID格式的id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建知识项失败: {str(e)}")


@router.put("/item/{item_id}")
async def update_knowledge_item(
    item_id: str,
    item: KnowledgeItemUpdate, 
    db: Session = Depends(get_db)
):
    """更新知识项"""
    try:
        # 查询知识项
        db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="知识项不存在")
        
        # 更新字段
        update_data = item.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        
        # 清除相关缓存
        clear_knowledge_cache()
        
        return {"message": "知识项更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新知识项失败: {str(e)}")


@router.delete("/item/{item_id}")
async def delete_knowledge_item(
    item_id: str, 
    db: Session = Depends(get_db)
):
    """删除知识项"""
    try:
        # 查询知识项
        db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="知识项不存在")
        
        # 删除知识项
        db.delete(db_item)
        db.commit()
        
        # 清除相关缓存
        clear_knowledge_cache()
        
        return {"message": "知识项删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除知识项失败: {str(e)}")


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., description="搜索关键词"),
    category_id: str = Query(None, description="分类ID"),
    status: str = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """搜索知识项"""
    try:
        # 构建查询条件
        query = db.query(KnowledgeItem)
        
        # 关键词搜索
        if q:
            query = query.filter(
                and_(
                    KnowledgeItem.title.contains(q),
                    KnowledgeItem.description.contains(q)
                )
            )
        
        # 分类筛选
        if category_id:
            query = query.filter(KnowledgeItem.category_id == category_id)
        
        # 状态筛选
        if status:
            query = query.filter(KnowledgeItem.status == status)
        
        # 执行查询
        items = query.order_by(KnowledgeItem.sort_order).all()
        
        # 构建返回数据
        result = []
        for item in items:
            result.append({
                "id": item.id,  # 使用UUID格式的id
                "category_id": item.category_id,
                "title": item.title,
                "description": item.description,
                "status": item.status,
                "sort_order": item.sort_order
            })
        
        return {"items": result, "total": len(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


# KnowledgeDetail相关接口
@router.get("/item/{item_id}/details", response_model=List[KnowledgeDetailResponse])
async def get_knowledge_item_details(
    item_id: str,
    db: Session = Depends(get_db)
):
    """获取知识项的详情列表"""
    try:
        # 验证知识项是否存在
        item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="知识项不存在")
        
        # 查询详情列表
        details = db.query(KnowledgeDetail).filter(
            KnowledgeDetail.knowledge_id == item_id
        ).order_by(KnowledgeDetail.sort_order).all()
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识项详情失败: {str(e)}")


@router.post("/item/{item_id}/details", response_model=KnowledgeDetailResponse)
async def create_knowledge_item_detail(
    item_id: str,
    detail: KnowledgeDetailCreate,
    db: Session = Depends(get_db)
):
    """为知识项创建详情"""
    try:
        # 验证知识项是否存在
        item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="知识项不存在")
        
        # 创建详情
        db_detail = KnowledgeDetail(
            knowledge_id=item_id,
            **detail.dict()
        )
        db.add(db_detail)
        db.commit()
        db.refresh(db_detail)
        
        # 清除相关缓存
        clear_knowledge_cache()
        
        return db_detail
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建知识项详情失败: {str(e)}")


@router.put("/detail/{detail_id}", response_model=KnowledgeDetailResponse)
async def update_knowledge_item_detail(
    detail_id: str,
    detail: KnowledgeDetailUpdate,
    db: Session = Depends(get_db)
):
    """更新知识项详情"""
    try:
        # 查询详情
        db_detail = db.query(KnowledgeDetail).filter(KnowledgeDetail.id == detail_id).first()
        if not db_detail:
            raise HTTPException(status_code=404, detail="知识项详情不存在")
        
        # 更新字段
        update_data = detail.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_detail, field, value)
        
        db.commit()
        db.refresh(db_detail)
        
        # 清除相关缓存
        clear_knowledge_cache()
        
        return db_detail
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新知识项详情失败: {str(e)}")


@router.delete("/detail/{detail_id}")
async def delete_knowledge_item_detail(
    detail_id: str,
    db: Session = Depends(get_db)
):
    """删除知识项详情"""
    try:
        # 查询详情
        db_detail = db.query(KnowledgeDetail).filter(KnowledgeDetail.id == detail_id).first()
        if not db_detail:
            raise HTTPException(status_code=404, detail="知识项详情不存在")
        
        # 删除详情
        db.delete(db_detail)
        db.commit()
        
        # 清除相关缓存
        clear_knowledge_cache()
        
        return {"message": "知识项详情删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除知识项详情失败: {str(e)}")


@router.get("/detail/{detail_id}", response_model=KnowledgeDetailResponse)
async def get_knowledge_item_detail(
    detail_id: str,
    db: Session = Depends(get_db)
):
    """根据ID获取知识项详情"""
    try:
        # 查询详情
        detail = db.query(KnowledgeDetail).filter(KnowledgeDetail.id == detail_id).first()
        if not detail:
            raise HTTPException(status_code=404, detail="知识项详情不存在")
        
        return detail
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识项详情失败: {str(e)}")
