"""
API接口管理API - 使用业务层
API Interfaces Management API - With Service Layer

遵循极简控制器编码规范：
- 控制器方法不超过5行代码
- 控制器不包含任何业务逻辑
- 只做接收请求、调用Service、返回响应
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from ..models.api_interface import (
    ApiInterface, ApiInterfaceCreate, ApiInterfaceUpdate, 
    ApiInterfaceQueryRequest, ApiInterfaceResponse,
    ApiInterfaceBatchRequest
)
from ..services.api_interface_service import ApiInterfaceService
from ..utils.response import success_response, error_response

router = APIRouter(tags=["API接口管理"])

@router.get("/", response_model=dict, summary="获取API接口列表")
async def get_api_interfaces():
    """获取所有API接口列表"""
    try:
        apis = ApiInterfaceService.get_api_interfaces()
        return success_response(data=apis, message="获取API接口列表成功")
    except Exception as e:
        return error_response(message=f"获取API接口列表失败: {str(e)}")

@router.get("/{api_id}", response_model=dict, summary="获取API接口详情")
async def get_api_interface(api_id: int):
    """根据ID获取API接口详情"""
    try:
        api = ApiInterfaceService.get_api_interface_by_id(api_id)
        if not api:
            raise HTTPException(status_code=404, detail="API接口不存在")
        return success_response(data=api, message="获取API接口详情成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取API接口详情失败: {str(e)}")

@router.post("/", response_model=dict, summary="创建API接口")
async def create_api_interface(api: ApiInterfaceCreate):
    """创建新API接口"""
    try:
        new_api = ApiInterfaceService.create_api_interface(api)
        return success_response(data=new_api, message="创建API接口成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"创建API接口失败: {str(e)}")

@router.put("/{api_id}", response_model=dict, summary="更新API接口")
async def update_api_interface(api_id: int, api: ApiInterfaceUpdate):
    """更新API接口信息"""
    try:
        updated_api = ApiInterfaceService.update_api_interface(api_id, api)
        if not updated_api:
            raise HTTPException(status_code=404, detail="API接口不存在")
        return success_response(data=updated_api, message="更新API接口成功")
    except HTTPException:
        raise
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"更新API接口失败: {str(e)}")

@router.delete("/{api_id}", response_model=dict, summary="删除API接口")
async def delete_api_interface(api_id: int):
    """删除API接口"""
    try:
        success = ApiInterfaceService.delete_api_interface(api_id)
        if not success:
            raise HTTPException(status_code=404, detail="API接口不存在")
        return success_response(message="删除API接口成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"删除API接口失败: {str(e)}")

@router.post("/search", response_model=dict, summary="搜索API接口")
async def search_api_interfaces(query: ApiInterfaceQueryRequest):
    """搜索API接口"""
    try:
        apis = ApiInterfaceService.search_api_interfaces(query)
        return success_response(data=apis, message="搜索API接口成功")
    except Exception as e:
        return error_response(message=f"搜索API接口失败: {str(e)}")

@router.get("/search/simple", response_model=dict, summary="简单搜索API接口")
async def search_api_interfaces_simple(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    system_id: Optional[int] = Query(None, description="系统ID"),
    module_id: Optional[int] = Query(None, description="模块ID"),
    method: Optional[str] = Query(None, description="HTTP方法"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页数量")
):
    """简单搜索API接口（GET方式）"""
    try:
        query_request = ApiInterfaceQueryRequest(
            keyword=keyword,
            system_id=system_id,
            module_id=module_id,
            method=method,
            status=status,
            page=page,
            size=size
        )
        apis = ApiInterfaceService.search_api_interfaces(query_request)
        return success_response(data=apis, message="搜索API接口成功")
    except Exception as e:
        return error_response(message=f"搜索API接口失败: {str(e)}")

@router.get("/system/{system_id}", response_model=dict, summary="获取系统的API接口")
async def get_api_interfaces_by_system(system_id: int):
    """根据系统ID获取API接口列表"""
    try:
        apis = ApiInterfaceService.get_api_interfaces_by_system(system_id)
        return success_response(data=apis, message="获取系统API接口列表成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"获取系统API接口列表失败: {str(e)}")

@router.get("/module/{module_id}", response_model=dict, summary="获取模块的API接口")
async def get_api_interfaces_by_module(module_id: int):
    """根据模块ID获取API接口列表"""
    try:
        apis = ApiInterfaceService.get_api_interfaces_by_module(module_id)
        return success_response(data=apis, message="获取模块API接口列表成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"获取模块API接口列表失败: {str(e)}")

@router.get("/stats/summary", response_model=dict, summary="获取API接口统计")
async def get_api_interface_stats():
    """获取API接口统计信息"""
    try:
        stats = ApiInterfaceService.get_api_interface_stats()
        return success_response(data=stats, message="获取统计信息成功")
    except Exception as e:
        return error_response(message=f"获取统计信息失败: {str(e)}")

@router.post("/batch/status", response_model=dict, summary="批量更新状态")
async def batch_update_status(batch_request: ApiInterfaceBatchRequest):
    """批量更新API接口状态"""
    try:
        result = ApiInterfaceService.batch_update_status(batch_request)
        return success_response(data=result, message="批量更新状态成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"批量更新状态失败: {str(e)}")

@router.post("/batch/delete", response_model=dict, summary="批量删除API接口")
async def batch_delete_api_interfaces(api_ids: List[int] = Body(..., description="API接口ID列表")):
    """批量删除API接口"""
    try:
        result = ApiInterfaceService.batch_delete(api_ids)
        return success_response(data=result, message="批量删除成功")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"批量删除失败: {str(e)}")

@router.get("/export/data", response_model=dict, summary="导出API接口数据")
async def export_api_interfaces(
    system_id: Optional[int] = Query(None, description="系统ID"),
    status: Optional[str] = Query(None, description="状态筛选")
):
    """导出API接口数据"""
    try:
        # 构建查询条件
        query_request = ApiInterfaceQueryRequest(
            system_id=system_id,
            status=status,
            page=1,
            size=1000  # 导出时获取更多数据
        )
        apis = ApiInterfaceService.search_api_interfaces(query_request)
        
        # 构建导出数据
        export_data = {
            'apis': apis,
            'total': len(apis),
            'export_time': ApiInterfaceService._get_current_timestamp(),
            'filters': {
                'system_id': system_id,
                'status': status
            }
        }
        
        return success_response(data=export_data, message="导出数据成功")
    except Exception as e:
        return error_response(message=f"导出数据失败: {str(e)}")

@router.post("/import/data", response_model=dict, summary="导入API接口数据")
async def import_api_interfaces(apis_data: List[ApiInterfaceCreate]):
    """批量导入API接口数据"""
    try:
        results = []
        success_count = 0
        error_count = 0
        
        for api_data in apis_data:
            try:
                new_api = ApiInterfaceService.create_api_interface(api_data)
                results.append({
                    'name': api_data.name,
                    'status': 'success',
                    'id': new_api.get('id')
                })
                success_count += 1
            except Exception as e:
                results.append({
                    'name': api_data.name,
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
        
        import_result = {
            'total': len(apis_data),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        }
        
        return success_response(data=import_result, message="导入数据完成")
    except Exception as e:
        return error_response(message=f"导入数据失败: {str(e)}")

@router.get("/methods/list", response_model=dict, summary="获取HTTP方法列表")
async def get_http_methods():
    """获取支持的HTTP方法列表"""
    try:
        methods = [
            {'value': 'GET', 'label': 'GET', 'color': 'success'},
            {'value': 'POST', 'label': 'POST', 'color': 'primary'},
            {'value': 'PUT', 'label': 'PUT', 'color': 'warning'},
            {'value': 'DELETE', 'label': 'DELETE', 'color': 'danger'},
            {'value': 'PATCH', 'label': 'PATCH', 'color': 'info'},
            {'value': 'HEAD', 'label': 'HEAD', 'color': 'default'},
            {'value': 'OPTIONS', 'label': 'OPTIONS', 'color': 'default'}
        ]
        return success_response(data=methods, message="获取HTTP方法列表成功")
    except Exception as e:
        return error_response(message=f"获取HTTP方法列表失败: {str(e)}")

@router.get("/statuses/list", response_model=dict, summary="获取状态列表")
async def get_api_statuses():
    """获取API接口状态列表"""
    try:
        statuses = [
            {'value': 'active', 'label': '启用', 'color': 'success'},
            {'value': 'inactive', 'label': '禁用', 'color': 'info'},
            {'value': 'deprecated', 'label': '已废弃', 'color': 'warning'},
            {'value': 'testing', 'label': '测试中', 'color': 'primary'}
        ]
        return success_response(data=statuses, message="获取状态列表成功")
    except Exception as e:
        return error_response(message=f"获取状态列表失败: {str(e)}")