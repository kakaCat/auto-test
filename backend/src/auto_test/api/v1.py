"""
V1版本API路由

为了兼容前端调用，提供v1版本的API接口。
这些接口是对现有API的代理，保持向后兼容性。

遵循极简控制器编码规范：
- 控制器方法不超过5行
- 只做接收请求、调用Service、返回响应
"""

from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.stats_service import StatsService
from ..services.system_service import SystemService
from ..services.log_service import LogService
from ..utils.response import success_response

# 创建路由器
router = APIRouter()


@router.get("/stats", response_model=dict, summary="获取统计信息 (v1兼容)")
async def get_stats_v1() -> Dict[str, Any]:
    """获取统计信息 - v1版本兼容接口"""
    data = StatsService.collect_stats_data()
    return success_response(data=data, message="获取统计信息成功")


@router.get("/systems", response_model=dict, summary="获取系统列表 (v1兼容)")
async def get_systems_v1(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态筛选")
) -> Dict[str, Any]:
    """获取系统列表 - v1版本兼容接口"""
    data = SystemService.collect_systems_data(page, size, search, status)
    return success_response(data=data, message="获取系统列表成功")


@router.get("/systems/statistics", response_model=dict, summary="获取系统统计信息 (v1兼容)")
async def get_systems_statistics_v1() -> Dict[str, Any]:
    """获取系统统计信息 - v1版本兼容接口"""
    data = StatsService.collect_systems_stats_data()
    return success_response(data=data, message="获取系统统计信息成功")


@router.get("/systems/categories", response_model=dict, summary="获取系统分类 (v1兼容)")
async def get_systems_categories_v1() -> Dict[str, Any]:
    """获取系统分类 - v1版本兼容接口"""
    data = SystemService.collect_categories_data()
    return success_response(data=data, message="获取系统分类成功")


@router.get("/logs", response_model=dict, summary="获取日志列表 (v1兼容)")
async def get_logs_v1(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    level: Optional[str] = Query(None, description="日志级别筛选"),
    module: Optional[str] = Query(None, description="模块筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
) -> Dict[str, Any]:
    """获取日志列表 - v1版本兼容接口"""
    data = LogService.collect_logs_data(page, size, level, module, None, None, keyword)
    return success_response(data=data, message="获取日志列表成功")


@router.get("/logs/stats", response_model=dict, summary="获取日志统计信息 (v1兼容)")
async def get_logs_stats_v1() -> Dict[str, Any]:
    """获取日志统计信息 - v1版本兼容接口"""
    data = LogService.collect_log_stats_data()
    return success_response(data=data, message="获取日志统计信息成功")