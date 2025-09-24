"""
统计信息API模块

提供系统级别的统计信息聚合服务，包括：
- 系统统计信息
- 模块统计信息  
- 工作流统计信息
- 场景统计信息
- 综合统计信息

遵循极简控制器编码规范：
- 控制器方法不超过5行
- 只做接收请求、调用Service、返回响应
- 使用Service层进行数据收集和组装
"""

from fastapi import APIRouter
from typing import Dict, Any

from ..services.stats_service import StatsService
from ..utils.response import success_response

# 创建路由器
router = APIRouter()


@router.get("/", response_model=dict, summary="获取综合统计信息")
async def get_stats() -> Dict[str, Any]:
    """获取综合统计信息 - 极简控制器"""
    data = StatsService.collect_stats_data()
    return success_response(data=data, message="获取统计信息成功")


@router.get("/systems", response_model=dict, summary="获取系统统计信息")
async def get_systems_stats() -> Dict[str, Any]:
    """获取系统统计信息 - 极简控制器"""
    data = StatsService.collect_systems_stats_data()
    return success_response(data=data, message="获取系统统计信息成功")


@router.get("/modules", response_model=dict, summary="获取模块统计信息")
async def get_modules_stats() -> Dict[str, Any]:
    """获取模块统计信息 - 极简控制器"""
    data = StatsService.collect_modules_stats_data()
    return success_response(data=data, message="获取模块统计信息成功")


@router.get("/workflows", response_model=dict, summary="获取工作流统计信息")
async def get_workflows_stats() -> Dict[str, Any]:
    """获取工作流统计信息 - 极简控制器"""
    data = StatsService.collect_workflows_stats_data()
    return success_response(data=data, message="获取工作流统计信息成功")


@router.get("/scenarios", response_model=dict, summary="获取场景统计信息")
async def get_scenarios_stats() -> Dict[str, Any]:
    """获取场景统计信息 - 极简控制器"""
    data = StatsService.collect_scenarios_stats_data()
    return success_response(data=data, message="获取场景统计信息成功")