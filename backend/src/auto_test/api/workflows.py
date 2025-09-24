"""工作流API路由

负责工作流相关的HTTP接口处理。
遵循极简控制器编码规范，只做接收请求、调用服务、返回响应。

职责：
- 接收HTTP请求
- 调用Service层
- 返回标准响应
"""

from fastapi import APIRouter
from typing import Dict, Any

from ..services.workflow_service import WorkflowService

router = APIRouter()


@router.get("/workflows/v1/stats")
async def get_workflow_stats() -> Dict[str, Any]:
    """获取工作流统计信息"""
    stats_data = WorkflowService.collect_workflow_stats_data()
    return stats_data


@router.get("/workflows/v1/")
async def get_workflows() -> Dict[str, Any]:
    """获取工作流列表（预留接口）"""
    workflows_data = WorkflowService.collect_workflows_data()
    return {
        "workflows": workflows_data,
        "total": len(workflows_data)
    }