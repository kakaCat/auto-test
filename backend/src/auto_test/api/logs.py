"""
日志管理API - 使用业务层
Logs API - With Service Layer

遵循极简控制器编码规范：
- 控制器方法不超过5行代码
- 控制器不包含任何业务逻辑
- 只做接收请求、调用Service、返回响应
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Query
from ..services.log_service import LogService
from ..utils.response import success_response, error_response

router = APIRouter(tags=["日志管理"])


@router.get("/logs/v1", response_model=dict, summary="获取日志列表")
async def get_logs(
    level: Optional[str] = Query(None, description="日志级别过滤"),
    page: Optional[int] = Query(1, description="页码"),
    size: Optional[int] = Query(10, description="每页数量"),
    module: Optional[str] = Query(None, description="模块筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
) -> Dict[str, Any]:
    """获取日志列表 - 极简控制器"""
    try:
        logs_data = LogService.collect_logs_data(
            page=page, 
            size=size, 
            level=level, 
            module=module, 
            keyword=keyword
        )
        stats_data = LogService.collect_log_stats_data()
        
        return success_response(
            data={
                "logs": logs_data.get("logs", []),
                "stats": stats_data,
                "total": logs_data.get("total", 0),
                "page": page,
                "size": size
            },
            message="获取日志列表成功"
        )
    except Exception as e:
        return error_response(message=f"获取日志列表失败: {str(e)}")


@router.get("/logs/v1/stats", response_model=dict, summary="获取日志统计信息")
async def get_log_stats() -> Dict[str, Any]:
    """获取日志统计信息 - 极简控制器"""
    try:
        stats_data = LogService.collect_log_stats_data()
        return success_response(data=stats_data, message="获取日志统计信息成功")
    except Exception as e:
        return error_response(message=f"获取日志统计信息失败: {str(e)}")


@router.get("/logs/v1/levels", response_model=dict, summary="获取日志级别列表")
async def get_log_levels() -> Dict[str, Any]:
    """获取支持的日志级别列表 - 极简控制器"""
    try:
        levels = [
            {"value": "DEBUG", "label": "调试", "color": "info"},
            {"value": "INFO", "label": "信息", "color": "success"},
            {"value": "WARNING", "label": "警告", "color": "warning"},
            {"value": "ERROR", "label": "错误", "color": "danger"},
            {"value": "CRITICAL", "label": "严重", "color": "danger"}
        ]
        return success_response(data=levels, message="获取日志级别列表成功")
    except Exception as e:
        return error_response(message=f"获取日志级别列表失败: {str(e)}")