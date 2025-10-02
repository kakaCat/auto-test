"""场景API路由

负责场景相关的HTTP接口处理。
遵循极简控制器编码规范，只做接收请求、调用服务、返回响应。

职责：
- 接收HTTP请求
- 调用Service层
- 返回标准响应
"""

from fastapi import APIRouter, Query
from typing import Dict, Any, Optional

from ..services.scenario_service import ScenarioService
from ..utils.response import success_response, error_response

router = APIRouter()


@router.get("/scenarios/v1/stats", response_model=dict, summary="获取场景统计")
async def get_scenario_stats() -> Dict[str, Any]:
    """获取场景统计信息 - 极简控制器"""
    try:
        stats_data = ScenarioService.collect_scenario_stats_data()
        return success_response(data=stats_data, message="获取场景统计信息成功")
    except Exception as e:
        return error_response(message=f"获取场景统计信息失败: {str(e)}")


@router.get("/scenarios/v1/", response_model=dict, summary="获取场景列表")
async def get_scenarios(
    api_id: Optional[int] = Query(None, description="API ID过滤"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态"),
    tags: Optional[str] = Query(None, description="标签，逗号分隔或多值"),
    created_by: Optional[str] = Query(None, description="创建人"),
    created_time_range: Optional[list[str]] = Query(None, description="创建时间范围"),
    is_parameters_saved: Optional[bool] = Query(None, description="是否保存过参数")
) -> Dict[str, Any]:
    """获取场景列表（无分页）"""
    try:
        filters = {
            'api_id': api_id,
            'keyword': keyword,
            'status': status,
            'tags': tags,
            'created_by': created_by,
            'created_time_range': created_time_range,
            'is_parameters_saved': is_parameters_saved
        }
        scenarios_data = ScenarioService.collect_scenarios_data(filters)
        return success_response(data=scenarios_data, message="获取场景列表成功")
    except Exception as e:
        return error_response(message=f"获取场景列表失败: {str(e)}")


@router.get("/scenarios/v1/creators", response_model=dict, summary="获取场景创建人列表")
async def get_creators(keyword: Optional[str] = Query(None, description="搜索关键词")) -> Dict[str, Any]:
    """获取场景创建人选项列表"""
    try:
        creators = ScenarioService.get_creators(keyword)
        return success_response(data=creators, message="获取创建人列表成功")
    except Exception as e:
        return error_response(message=f"获取创建人列表失败: {str(e)}")


@router.get("/scenario-tags", response_model=dict, summary="获取场景标签列表")
async def get_scenario_tags() -> Dict[str, Any]:
    """提供场景标签选项（示例数据）"""
    try:
        tags = [
            { 'label': 'auth', 'value': 'auth', 'color': '#409EFF', 'group': '功能' },
            { 'label': 'smoke', 'value': 'smoke', 'color': '#67C23A', 'group': '级别' },
            { 'label': 'rate-limit', 'value': 'rate-limit', 'color': '#E6A23C', 'group': '稳定性' }
        ]
        return success_response(data=tags, message="获取场景标签列表成功")
    except Exception as e:
        return error_response(message=f"获取场景标签列表失败: {str(e)}")