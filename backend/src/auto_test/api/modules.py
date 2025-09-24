"""
模块管理API - 使用业务层
Modules API - With Service Layer
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from ..models.module import Module, ModuleCreate, ModuleUpdate
from ..services.module_service import ModuleService
from ..utils.response import success_response, error_response

router = APIRouter(tags=["模块管理"])

@router.get("/modules/v1/", response_model=dict, summary="获取模块列表")
async def get_modules(system_id: int = Query(None, description="系统ID，可选")):
    """获取模块列表，可按系统ID筛选"""
    try:
        modules = ModuleService.get_modules(system_id)
        return success_response(data=modules, message="获取模块列表成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"获取模块列表失败: {str(e)}")

@router.get("/modules/v1/by-system/{system_id}", response_model=dict, summary="根据系统ID获取模块列表")
async def get_modules_by_system(system_id: int):
    """根据系统ID获取模块列表"""
    try:
        modules = ModuleService.get_modules(system_id)
        return success_response(data=modules, message="获取模块列表成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"获取模块列表失败: {str(e)}")

@router.get("/modules/v1/enabled", response_model=dict, summary="获取启用模块列表")
async def get_enabled_modules(system_id: int = Query(None, description="系统ID，可选")):
    """获取启用状态的模块列表（用于API管理和页面管理页面）"""
    try:
        modules = ModuleService.get_enabled_modules(system_id)
        return success_response(data=modules, message="获取启用模块列表成功")
    except Exception as e:
        return error_response(message=f"获取启用模块列表失败: {str(e)}")

@router.get("/modules/v1/enabled/by-system/{system_id}", response_model=dict, summary="根据系统ID获取启用模块列表")
async def get_enabled_modules_by_system(system_id: int):
    """根据系统ID获取启用状态的模块列表"""
    try:
        modules = ModuleService.get_enabled_modules(system_id)
        return success_response(data=modules, message="获取启用模块列表成功")
    except Exception as e:
        return error_response(message=f"获取启用模块列表失败: {str(e)}")

@router.get("/modules/v1/{module_id}", response_model=dict, summary="获取模块详情")
async def get_module(module_id: int):
    """根据ID获取模块详情"""
    try:
        module = ModuleService.get_module_by_id(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="模块不存在")
        return success_response(data=module, message="获取模块详情成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取模块详情失败: {str(e)}")

@router.post("/modules/v1/", response_model=dict, summary="创建模块")
async def create_module(module: ModuleCreate):
    """创建新模块"""
    try:
        new_module = ModuleService.create_module(module)
        return success_response(data=new_module, message="创建模块成功")
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        return error_response(message=f"创建模块失败: {str(e)}")

@router.put("/modules/v1/{module_id}", response_model=dict, summary="更新模块")
async def update_module(module_id: int, module: ModuleUpdate):
    """更新模块信息"""
    try:
        updated_module = ModuleService.update_module(module_id, module)
        if not updated_module:
            raise HTTPException(status_code=404, detail="模块不存在")
        return success_response(data=updated_module, message="更新模块成功")
    except HTTPException:
        raise
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"更新模块失败: {str(e)}")

@router.delete("/modules/v1/{module_id}", response_model=dict, summary="删除模块")
async def delete_module(module_id: int):
    """删除模块"""
    try:
        success = ModuleService.delete_module(module_id)
        if not success:
            raise HTTPException(status_code=404, detail="模块不存在")
        return success_response(message="删除模块成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"删除模块失败: {str(e)}")

@router.get("/modules/v1/tags/list", response_model=dict, summary="获取标签列表")
async def get_tags():
    """获取所有模块标签"""
    try:
        tags = ModuleService.get_all_tags()
        return success_response(data=tags, message="获取标签列表成功")
    except Exception as e:
        return error_response(message=f"获取标签列表失败: {str(e)}")

@router.get("/modules/v1/stats/summary", response_model=dict, summary="获取模块统计")
async def get_module_stats():
    """获取模块统计信息"""
    try:
        stats = ModuleService.get_module_statistics()
        return success_response(data=stats, message="获取统计信息成功")
    except Exception as e:
        return error_response(message=f"获取统计信息失败: {str(e)}")

@router.patch("/modules/{module_id}/status", response_model=dict, summary="切换模块启用状态")
async def toggle_module_status(module_id: int, status_data: dict):
    """切换模块启用状态"""
    try:
        enabled = status_data.get('enabled', False)
        updated_module = ModuleService.toggle_enabled(module_id, enabled)
        if not updated_module:
            raise HTTPException(status_code=404, detail="模块不存在")
        return success_response(data=updated_module, message=f"模块已{'启用' if enabled else '禁用'}")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"切换模块状态失败: {str(e)}")