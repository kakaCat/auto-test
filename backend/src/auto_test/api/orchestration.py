"""AI编排API接口

提供AI编排相关的HTTP接口，包括：
- 编排执行
- 计划生成和校验
- 执行监控
- WebSocket事件推送

遵循极简控制器编码规范：
- 控制器方法不超过5行代码
- 控制器不包含任何业务逻辑
- 只做接收请求、调用Service、返回响应
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field

from ..services.orchestration_service import OrchestrationService
from ..services.tracking_service import TrackingService
from ..utils.response import success_response, error_response
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["AI编排"])


# ============================================================================
# 请求/响应模型定义
# ============================================================================

class OrchestrationRequest(BaseModel):
    """编排请求模型"""
    user_input: str = Field(description="用户自然语言输入")
    context: Dict[str, Any] = Field(default_factory=dict, description="执行上下文")


class PlanGenerateRequest(BaseModel):
    """计划生成请求模型"""
    flow_id: Optional[str] = Field(default=None, description="流程ID")
    intent_text: str = Field(description="意图文本")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class PlanValidateRequest(BaseModel):
    """计划校验请求模型"""
    plan: Dict[str, Any] = Field(description="执行计划")


class ExecutionValidateInputsRequest(BaseModel):
    """执行入参校验请求模型"""
    plan: Dict[str, Any] = Field(description="执行计划")
    inputs: Dict[str, Any] = Field(description="执行入参")


# ============================================================================
# 编排执行接口
# ============================================================================

@router.post("/orchestration/v1/execute", summary="执行AI编排")
async def execute_orchestration(request: OrchestrationRequest):
    """执行AI编排任务"""
    try:
        result = await OrchestrationService.execute_orchestration(
            user_input=request.user_input,
            context=request.context
        )
        return success_response(data=result, message="编排执行成功")
    except Exception as e:
        logger.error(f"编排执行失败: {str(e)}")
        return error_response(message=f"编排执行失败: {str(e)}")


@router.get("/orchestration/v1/executions/{execution_id}", summary="获取执行状态")
async def get_execution_status(execution_id: str):
    """获取执行状态"""
    try:
        status = await OrchestrationService.get_execution_status(execution_id)
        if not status:
            raise HTTPException(status_code=404, detail="执行记录不存在")
        return success_response(data=status, message="获取状态成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取执行状态失败: {str(e)}")
        return error_response(message=f"获取状态失败: {str(e)}")


# ============================================================================
# 计划生成和校验接口
# ============================================================================

@router.post("/orchestration/plan/generate", summary="生成执行计划（Step3）")
async def generate_plan(request: PlanGenerateRequest):
    """生成执行计划"""
    try:
        result = await OrchestrationService.generate_plan(
            flow_id=request.flow_id,
            intent_text=request.intent_text,
            context=request.context
        )
        return success_response(data=result, message="计划生成成功")
    except Exception as e:
        logger.error(f"计划生成失败: {str(e)}")
        return error_response(message=f"计划生成失败: {str(e)}")


@router.post("/orchestration/plan/validate", summary="校验执行计划（Step3）")
async def validate_plan(request: PlanValidateRequest):
    """校验执行计划"""
    try:
        result = await OrchestrationService.validate_plan(request.plan)
        return success_response(data=result, message="计划校验完成")
    except Exception as e:
        logger.error(f"计划校验失败: {str(e)}")
        return error_response(message=f"计划校验失败: {str(e)}")


@router.post("/orchestration/execute/validate-inputs", summary="执行前入参校验")
async def validate_execution_inputs(request: ExecutionValidateInputsRequest):
    """执行前入参校验"""
    try:
        result = await OrchestrationService.validate_execution_inputs(
            plan=request.plan,
            inputs=request.inputs
        )
        return success_response(data=result, message="入参校验完成")
    except Exception as e:
        logger.error(f"入参校验失败: {str(e)}")
        return error_response(message=f"入参校验失败: {str(e)}")


# ============================================================================
# 流程管理接口
# ============================================================================

@router.get("/orchestration/flows", summary="获取编排流程列表")
async def get_orchestration_flows(
    page: int = 1,
    size: int = 10,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[str] = None,
    tags: Optional[str] = None,
    system_ids: Optional[str] = None,
    module_ids: Optional[str] = None
):
    """获取编排流程列表（支持跨系统/模块筛选）"""
    try:
        filters = {
            'keyword': keyword,
            'status': status,
            'created_by': created_by,
            'tags': tags.split(',') if tags else None,
            'system_ids': [int(x) for x in system_ids.split(',')] if system_ids else None,
            'module_ids': [int(x) for x in module_ids.split(',')] if module_ids else None
        }
        result = await TrackingService.get_filtered_plans(
            filters=filters, page=page, size=size
        )
        return success_response(data=result, message="获取流程列表成功")
    except Exception as e:
        logger.error(f"获取流程列表失败: {str(e)}")
        return error_response(message=f"获取流程列表失败: {str(e)}")


@router.post("/orchestration/flows", summary="创建编排流程")
async def create_orchestration_flow(flow_data: Dict[str, Any]):
    """创建编排流程"""
    try:
        result = await OrchestrationService.create_orchestration_flow(flow_data)
        return success_response(data=result, message="创建流程成功")
    except Exception as e:
        logger.error(f"创建流程失败: {str(e)}")
        return error_response(message=f"创建流程失败: {str(e)}")


@router.get("/orchestration/flows/{flow_id}", summary="获取流程详情")
async def get_orchestration_flow(flow_id: int):
    """获取流程详情"""
    try:
        result = await OrchestrationService.get_orchestration_flow(flow_id)
        if not result:
            raise HTTPException(status_code=404, detail="流程不存在")
        return success_response(data=result, message="获取流程详情成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取流程详情失败: {str(e)}")
        return error_response(message=f"获取流程详情失败: {str(e)}")


@router.put("/orchestration/flows/{flow_id}", summary="更新流程")
async def update_orchestration_flow(flow_id: int, flow_data: Dict[str, Any]):
    """更新流程"""
    try:
        result = await OrchestrationService.update_orchestration_flow(flow_id, flow_data)
        return success_response(data=result, message="更新流程成功")
    except Exception as e:
        logger.error(f"更新流程失败: {str(e)}")
        return error_response(message=f"更新流程失败: {str(e)}")


# ============================================================================
# MCP工具管理接口
# ============================================================================

@router.get("/orchestration/tools", summary="获取可用工具列表")
async def get_available_tools(tool_type: Optional[str] = None, enabled_only: bool = True):
    """获取可用工具列表"""
    try:
        result = await OrchestrationService.get_available_tools(tool_type, enabled_only)
        return success_response(data=result, message="获取工具列表成功")
    except Exception as e:
        logger.error(f"获取工具列表失败: {str(e)}")
        return error_response(message=f"获取工具列表失败: {str(e)}")


@router.get("/orchestration/tools/{tool_name}/schema", summary="获取工具Schema")
async def get_tool_schema(tool_name: str):
    """获取工具Schema定义"""
    try:
        result = await OrchestrationService.get_tool_schema(tool_name)
        if not result:
            raise HTTPException(status_code=404, detail="工具不存在")
        return success_response(data=result, message="获取工具Schema成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工具Schema失败: {str(e)}")
        return error_response(message=f"获取工具Schema失败: {str(e)}")


# ============================================================================
# 统计和监控接口
# ============================================================================

@router.get("/orchestration/stats", summary="获取编排统计信息")
async def get_orchestration_stats():
    """获取编排统计信息"""
    try:
        result = await OrchestrationService.get_orchestration_stats()
        return success_response(data=result, message="获取统计信息成功")
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return error_response(message=f"获取统计信息失败: {str(e)}")


# ============================================================================
# WebSocket实时监控
# ============================================================================

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[execution_id] = websocket
        logger.info(f"WebSocket连接建立: {execution_id}")
    
    def disconnect(self, execution_id: str):
        """断开连接"""
        if execution_id in self.active_connections:
            del self.active_connections[execution_id]
            logger.info(f"WebSocket连接断开: {execution_id}")
    
    async def send_message(self, execution_id: str, message: Dict[str, Any]):
        """发送消息"""
        if execution_id in self.active_connections:
            try:
                await self.active_connections[execution_id].send_json(message)
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {e}")
                self.disconnect(execution_id)


# 全局连接管理器
connection_manager = ConnectionManager()


@router.websocket("/orchestration/v1/monitor/{execution_id}")
async def monitor_execution(websocket: WebSocket, execution_id: str):
    """实时监控执行过程"""
    await connection_manager.connect(websocket, execution_id)
    
    try:
        # 订阅执行事件
        async for event in OrchestrationService.subscribe_execution_events(execution_id):
            event_data = {
                'event_type': event.event_type,
                'execution_id': event.execution_id,
                'step_id': event.step_id,
                'message': event.message,
                'timestamp': event.timestamp,
                'data': event.data
            }
            
            await connection_manager.send_message(execution_id, event_data)
            
            # 如果是执行完成事件，结束监控
            if event.event_type in ['execution_completed', 'execution_failed']:
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket监控异常: {e}")
        await websocket.send_json({
            'event_type': 'error',
            'message': f"监控异常: {str(e)}",
            'timestamp': datetime.now().isoformat()
        })
    finally:
        connection_manager.disconnect(execution_id)


# ============================================================================
# 跨系统/模块追踪与审计接口
# ============================================================================

@router.get("/orchestration/tracking/stats", summary="获取系统模块统计")
async def get_system_module_stats():
    """获取系统模块使用统计"""
    try:
        result = await TrackingService.get_system_module_stats()
        return success_response(data=result, message="获取统计信息成功")
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return error_response(message=f"获取统计信息失败: {str(e)}")


@router.get("/orchestration/tracking/analysis", summary="获取跨系统分析")
async def get_cross_system_analysis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取跨系统调用分析报告"""
    try:
        time_range = None
        if start_date and end_date:
            time_range = {'start': start_date, 'end': end_date}
        
        result = await TrackingService.get_cross_system_analysis(time_range)
        return success_response(data=result, message="获取分析报告成功")
    except Exception as e:
        logger.error(f"获取分析报告失败: {str(e)}")
        return error_response(message=f"获取分析报告失败: {str(e)}")


@router.get("/orchestration/tracking/executions/{execution_id}", summary="获取执行追踪数据")
async def get_execution_tracking(execution_id: str):
    """获取执行的追踪数据"""
    try:
        result = await TrackingService.get_execution_tracking_data(execution_id)
        return success_response(data=result, message="获取追踪数据成功")
    except Exception as e:
        logger.error(f"获取追踪数据失败: {str(e)}")
        return error_response(message=f"获取追踪数据失败: {str(e)}")


@router.post("/orchestration/tracking/export", summary="导出审计报告")
async def export_audit_report(
    filters: Dict[str, Any],
    format: str = "json"
):
    """导出审计报告"""
    try:
        result = await TrackingService.export_audit_report(filters, format)
        return success_response(data=result, message="导出报告成功")
    except Exception as e:
        logger.error(f"导出报告失败: {str(e)}")
        return error_response(message=f"导出报告失败: {str(e)}")


# ============================================================================
# 兼容性路由（支持前端调用）
# ============================================================================

@router.post("/orchestration/execute", summary="执行AI编排（兼容路由）")
async def execute_orchestration_compat(request: OrchestrationRequest):
    """执行AI编排任务 - 兼容路由"""
    return await execute_orchestration(request)


@router.get("/orchestration/executions/{execution_id}/status", summary="获取执行状态（兼容路由）")
async def get_execution_status_compat(execution_id: str):
    """获取执行状态 - 兼容路由"""
    return await get_execution_status(execution_id)