"""
架构图管理路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import FlowVersion, FlowModule, User, FlowArchitecture, FlowArchitectureItem
from src.schemas import (
    FlowVersionCreate, FlowVersionUpdate, FlowVersionResponse,
    FlowModuleCreate, FlowModuleUpdate, FlowModuleResponse
)
from src.auth import get_current_admin_user
from src.cache import (
    get_cached_flow_version, set_cached_flow_version,
    get_cached_flow_module, set_cached_flow_module,
    clear_flow_cache
)

router = APIRouter(prefix="/flow", tags=["架构图"])


@router.get("/versions", response_model=Dict[str, Any])
async def get_flow_versions(db: Session = Depends(get_db)):
    """获取架构图版本信息"""
    # 从数据库查询架构图结构
    architectures = db.query(FlowArchitecture).filter(
        FlowArchitecture.is_active == True
    ).order_by(FlowArchitecture.sort_order).all()
    
    result = {}
    
    for architecture in architectures:
        # 查询该域下的所有模块项
        items = db.query(FlowArchitectureItem).filter(
            FlowArchitectureItem.domain == architecture.domain,
            FlowArchitectureItem.is_active == True
        ).order_by(FlowArchitectureItem.sort_order).all()
        
        result[architecture.domain] = {
            "title": architecture.title,
            "items": [
                {
                    "id": item.item_id,
                    "title": item.title,
                    "description": item.description,
                    "type": item.item_type
                }
                for item in items
            ]
        }
    
    return result


@router.get("/version/{version_id}", response_model=Dict[str, Any])
async def get_flow_version(version_id: str, db: Session = Depends(get_db)):
    """获取指定版本架构图"""
    # 尝试从缓存获取
    cached_data = get_cached_flow_version(version_id)
    if cached_data:
        return cached_data
    
    version = db.query(FlowVersion).filter(
        FlowVersion.version_id == version_id,
        FlowVersion.is_active == True
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 获取版本下的模块
    modules = db.query(FlowModule).filter(
        FlowModule.version_id == version_id
    ).all()
    
    result = {
        "version": {
            "version_id": version.version_id,
            "title": version.title,
            "description": version.description,
            "is_default": version.is_default
        },
        "modules": [
            {
                "module_id": module.module_id,
                "title": module.title,
                "description": module.description,
                "module_type": module.module_type,
                "position_x": module.position_x,
                "position_y": module.position_y
            }
            for module in modules
        ]
    }
    
    # 缓存结果
    set_cached_flow_version(version_id, result)
    
    return result


@router.get("/module/{module_id}", response_model=FlowModuleResponse)
async def get_flow_module(module_id: str, db: Session = Depends(get_db)):
    """获取指定模块详情"""
    # 尝试从缓存获取
    cached_data = get_cached_flow_module(module_id)
    if cached_data:
        return cached_data
    
    module = db.query(FlowModule).filter(FlowModule.module_id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模块不存在"
        )
    
    result = FlowModuleResponse.from_orm(module)
    
    # 缓存结果
    set_cached_flow_module(module_id, result.dict())
    
    return result


@router.post("/versions", response_model=FlowVersionResponse)
async def create_flow_version(
    version_data: FlowVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建架构图版本（管理员）"""
    # 检查版本ID是否已存在
    existing_version = db.query(FlowVersion).filter(
        FlowVersion.version_id == version_data.version_id
    ).first()
    
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本ID已存在"
        )
    
    # 如果设置为默认版本，先取消其他默认版本
    if version_data.is_default:
        db.query(FlowVersion).filter(FlowVersion.is_default == True).update({"is_default": False})
    
    db_version = FlowVersion(**version_data.dict())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    # 清除缓存
    clear_flow_cache()
    
    return FlowVersionResponse.from_orm(db_version)


@router.put("/versions/{version_id}", response_model=FlowVersionResponse)
async def update_flow_version(
    version_id: str,
    version_data: FlowVersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新架构图版本（管理员）"""
    version = db.query(FlowVersion).filter(FlowVersion.version_id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 如果设置为默认版本，先取消其他默认版本
    if version_data.is_default:
        db.query(FlowVersion).filter(FlowVersion.is_default == True).update({"is_default": False})
    
    # 更新字段
    update_data = version_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(version, field, value)
    
    db.commit()
    db.refresh(version)
    
    # 清除缓存
    clear_flow_cache()
    
    return FlowVersionResponse.from_orm(version)


@router.delete("/versions/{version_id}")
async def delete_flow_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除架构图版本（管理员）"""
    version = db.query(FlowVersion).filter(FlowVersion.version_id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    
    # 检查是否有模块
    modules_count = db.query(FlowModule).filter(FlowModule.version_id == version_id).count()
    
    if modules_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本下还有模块，无法删除"
        )
    
    db.delete(version)
    db.commit()
    
    # 清除缓存
    clear_flow_cache()
    
    return {"message": "版本删除成功"}


@router.post("/modules", response_model=FlowModuleResponse)
async def create_flow_module(
    module_data: FlowModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建架构图模块（管理员）"""
    # 检查版本是否存在
    version = db.query(FlowVersion).filter(
        FlowVersion.version_id == module_data.version_id,
        FlowVersion.is_active == True
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本不存在"
        )
    
    # 检查模块ID是否已存在
    existing_module = db.query(FlowModule).filter(
        FlowModule.module_id == module_data.module_id
    ).first()
    
    if existing_module:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="模块ID已存在"
        )
    
    db_module = FlowModule(**module_data.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    
    # 清除缓存
    clear_flow_cache()
    
    return FlowModuleResponse.from_orm(db_module)


@router.put("/modules/{module_id}", response_model=FlowModuleResponse)
async def update_flow_module(
    module_id: str,
    module_data: FlowModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新架构图模块（管理员）"""
    module = db.query(FlowModule).filter(FlowModule.module_id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模块不存在"
        )
    
    # 更新字段
    update_data = module_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    
    # 清除缓存
    clear_flow_cache()
    
    return FlowModuleResponse.from_orm(module)


@router.delete("/modules/{module_id}")
async def delete_flow_module(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除架构图模块（管理员）"""
    module = db.query(FlowModule).filter(FlowModule.module_id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模块不存在"
        )
    
    db.delete(module)
    db.commit()
    
    # 清除缓存
    clear_flow_cache()
    
    return {"message": "模块删除成功"}
