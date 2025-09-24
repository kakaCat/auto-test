"""场景API路由

负责场景相关的HTTP接口处理。
遵循极简控制器编码规范，只做接收请求、调用服务、返回响应。

职责：
- 接收HTTP请求
- 调用Service层
- 返回标准响应
"""

from fastapi import APIRouter
from typing import Dict, Any

from ..services.scenario_service import ScenarioService

router = APIRouter()


@router.get("/stats")
async def get_scenario_stats() -> Dict[str, Any]:
    """获取场景统计信息"""
    stats_data = ScenarioService.collect_scenario_stats_data()
    return stats_data


@router.get("/")
async def get_scenarios() -> Dict[str, Any]:
    """获取场景列表（预留接口）"""
    scenarios_data = ScenarioService.collect_scenarios_data()
    return {
        "scenarios": scenarios_data,
        "total": len(scenarios_data)
    }