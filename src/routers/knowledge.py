"""
知识库管理路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import KnowledgeCategory, KnowledgeItem, User
from src.schemas import (
    KnowledgeCategoryCreate, KnowledgeCategoryUpdate, KnowledgeCategoryResponse,
    KnowledgeItemCreate, KnowledgeItemUpdate, KnowledgeItemResponse
)
from src.auth import get_current_admin_user, get_current_user
from src.cache import (
    get_cached_knowledge_categories, set_cached_knowledge_categories,
    get_cached_knowledge_item, set_cached_knowledge_item,
    clear_knowledge_cache
)

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/categories", response_model=Dict[str, Any])
async def get_knowledge_categories(db: Session = Depends(get_db)):
    """获取所有知识分类"""
    # 尝试从缓存获取
    cached_data = get_cached_knowledge_categories()
    if cached_data:
        return cached_data
    
    # 从数据库获取
    categories = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.is_active == True
    ).order_by(KnowledgeCategory.sort_order).all()
    
    result = {}
    for category in categories:
        # 获取分类下的知识项
        items = db.query(KnowledgeItem).filter(
            KnowledgeItem.category_id == category.category_id
        ).order_by(KnowledgeItem.sort_order).all()
        
        result[category.category_id] = {
            "title": category.title,
            "items": [
                {
                    "title": item.title,
                    "description": item.description,
                    "status": item.status
                }
                for item in items
            ]
        }
    
    # 缓存结果
    set_cached_knowledge_categories(result)
    
    return result


@router.get("/category/{category_id}", response_model=KnowledgeCategoryResponse)
async def get_knowledge_category(category_id: str, db: Session = Depends(get_db)):
    """获取指定分类详情"""
    category = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.category_id == category_id,
        KnowledgeCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    return KnowledgeCategoryResponse.from_orm(category)


@router.get("/item/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(item_id: int, db: Session = Depends(get_db)):
    """获取指定知识项详情"""
    # 尝试从缓存获取
    cached_data = get_cached_knowledge_item(item_id)
    if cached_data:
        return cached_data
    
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识项不存在"
        )
    
    result = KnowledgeItemResponse.from_orm(item)
    
    # 缓存结果
    set_cached_knowledge_item(item_id, result.dict())
    
    return result


@router.post("/categories", response_model=KnowledgeCategoryResponse)
async def create_knowledge_category(
    category_data: KnowledgeCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建知识分类（管理员）"""
    # 检查分类ID是否已存在
    existing_category = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.category_id == category_data.category_id
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类ID已存在"
        )
    
    db_category = KnowledgeCategory(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # 清除缓存
    clear_knowledge_cache()
    
    return KnowledgeCategoryResponse.from_orm(db_category)


@router.put("/categories/{category_id}", response_model=KnowledgeCategoryResponse)
async def update_knowledge_category(
    category_id: str,
    category_data: KnowledgeCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新知识分类（管理员）"""
    category = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.category_id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 更新字段
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    # 清除缓存
    clear_knowledge_cache()
    
    return KnowledgeCategoryResponse.from_orm(category)


@router.delete("/categories/{category_id}")
async def delete_knowledge_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除知识分类（管理员）"""
    category = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.category_id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 检查是否有知识项
    items_count = db.query(KnowledgeItem).filter(
        KnowledgeItem.category_id == category_id
    ).count()
    
    if items_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类下还有知识项，无法删除"
        )
    
    db.delete(category)
    db.commit()
    
    # 清除缓存
    clear_knowledge_cache()
    
    return {"message": "分类删除成功"}


@router.post("/items", response_model=KnowledgeItemResponse)
async def create_knowledge_item(
    item_data: KnowledgeItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建知识项（管理员）"""
    # 检查分类是否存在
    category = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.category_id == item_data.category_id,
        KnowledgeCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类不存在"
        )
    
    db_item = KnowledgeItem(**item_data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 清除缓存
    clear_knowledge_cache()
    
    return KnowledgeItemResponse.from_orm(db_item)


@router.put("/items/{item_id}", response_model=KnowledgeItemResponse)
async def update_knowledge_item(
    item_id: int,
    item_data: KnowledgeItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新知识项（管理员）"""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识项不存在"
        )
    
    # 更新字段
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # 清除缓存
    clear_knowledge_cache()
    
    return KnowledgeItemResponse.from_orm(item)


@router.delete("/items/{item_id}")
async def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除知识项（管理员）"""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识项不存在"
        )
    
    db.delete(item)
    db.commit()
    
    # 清除缓存
    clear_knowledge_cache()
    
    return {"message": "知识项删除成功"}
