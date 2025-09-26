"""
系统管理API - 使用业务层
Systems API - With Service Layer
"""

from typing import List
from fastapi import APIRouter, HTTPException
from ..models.system import System, SystemCreate, SystemUpdate
from ..services.system_service import SystemService
from ..utils.response import success_response, error_response

router = APIRouter(tags=["系统管理"])

@router.get("/systems/v1/", response_model=dict, summary="获取系统列表")
async def get_systems():
    """获取所有系统列表"""
    try:
        systems = SystemService.get_systems()
        return success_response(data=systems, message="获取系统列表成功")
    except Exception as e:
        return error_response(message=f"获取系统列表失败: {str(e)}")

@router.get("/systems/v1/enabled", response_model=dict, summary="获取启用系统列表")
async def get_enabled_systems():
    """获取启用状态的系统列表（用于API管理和页面管理页面）"""
    try:
        systems = SystemService.get_enabled_systems()
        return success_response(data=systems, message="获取启用系统列表成功")
    except Exception as e:
        return error_response(message=f"获取启用系统列表失败: {str(e)}")

@router.get("/systems/v1/enabled/{category}", response_model=dict, summary="根据分类获取启用系统列表")
async def get_enabled_systems_by_category(category: str):
    """
    根据分类获取启用状态的系统列表
    
    Args:
        category: 系统分类 ('backend' 或 'frontend')
    """
    try:
        # 验证分类参数
        if category not in ['backend', 'frontend']:
            raise HTTPException(status_code=400, detail="分类参数无效，只支持 'backend' 或 'frontend'")
            
        systems = SystemService.get_enabled_systems_by_category(category)
        return success_response(data=systems, message=f"获取分类为 '{category}' 的启用系统列表成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取分类系统列表失败: {str(e)}")

@router.get("/systems/v1/{system_id}", response_model=dict, summary="获取系统详情")
async def get_system(system_id: int):
    """根据ID获取系统详情"""
    try:
        system = SystemService.get_system_by_id(system_id)
        if not system:
            raise HTTPException(status_code=404, detail="系统不存在")
        return success_response(data=system, message="获取系统详情成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取系统详情失败: {str(e)}")

@router.post("/systems/v1/", response_model=dict, summary="创建系统")
async def create_system(system: SystemCreate):
    """创建新系统"""
    try:
        new_system = SystemService.create_system(system)
        return success_response(data=new_system, message="创建系统成功")
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f"创建系统失败: {str(e)}")

@router.put("/systems/v1/{system_id}", response_model=dict, summary="更新系统")
async def update_system(system_id: int, system: SystemUpdate):
    """更新系统信息"""
    try:
        updated_system = SystemService.update_system(system_id, system)
        if not updated_system:
            raise HTTPException(status_code=404, detail="系统不存在")
        return success_response(data=updated_system, message="更新系统成功")
    except HTTPException:
        raise
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f"更新系统失败: {str(e)}")

@router.delete("/systems/v1/{system_id}", response_model=dict, summary="删除系统")
async def delete_system(system_id: int):
    """删除系统"""
    try:
        success = SystemService.delete_system(system_id)
        if not success:
            raise HTTPException(status_code=404, detail="系统不存在")
        return success_response(message="删除系统成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"删除系统失败: {str(e)}")

@router.patch("/systems/{system_id}/status", response_model=dict, summary="切换系统启用状态")
async def toggle_system_status(system_id: int, status_data: dict):
    """切换系统启用状态"""
    try:
        enabled = status_data.get('enabled', False)
        updated_system = SystemService.toggle_enabled(system_id, enabled)
        if not updated_system:
            raise HTTPException(status_code=404, detail="系统不存在")
        return success_response(data=updated_system, message=f"系统已{'启用' if enabled else '禁用'}")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"切换系统状态失败: {str(e)}")