"""执行引擎组件

负责协调MCP工具执行计划，监控执行过程，处理异常和重试。
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from enum import Enum

from .base_agent import BaseAgent
from ..mcp.client import MCPClient
from ..database.dao_ai import AIExecutionDAO, ExecutionStepDAO
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionEvent:
    """执行事件"""
    def __init__(self, event_type: str, execution_id: str, step_id: Optional[str] = None, 
                 message: str = "", data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.execution_id = execution_id
        self.step_id = step_id
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now().isoformat()


class ExecutionEngine(BaseAgent):
    """执行引擎组件
    
    负责：
    - 协调MCP工具执行计划
    - 监控执行过程和状态
    - 处理步骤间数据传递
    - 异常处理和重试机制
    - 实时事件推送
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        self.mcp_client = MCPClient(config)
        self.active_executions = {}  # 活跃的执行实例
        self.event_subscribers = {}  # 事件订阅者
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理执行请求
        
        Args:
            input_data: 包含执行计划的数据
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 验证输入
        self.validate_input(input_data, ['execution_plan'])
        
        execution_plan = input_data['execution_plan']
        context = input_data.get('context', {})
        
        # 生成执行ID
        execution_id = str(uuid.uuid4())
        
        logger.info(f"开始执行计划: {execution_id}")
        
        try:
            # 初始化MCP客户端
            await self.mcp_client.initialize()
            
            # 创建执行记录
            await self._create_execution_record(execution_id, execution_plan, context)
            
            # 异步执行计划
            asyncio.create_task(self._execute_plan_async(execution_id, execution_plan, context))
            
            return {
                'execution_id': execution_id,
                'status': ExecutionStatus.RUNNING.value,
                'message': '执行已启动',
                'plan_summary': {
                    'total_steps': len(execution_plan.get('steps', [])),
                    'estimated_duration': execution_plan.get('estimated_duration', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"启动执行失败: {e}")
            raise
    
    async def _create_execution_record(self, execution_id: str, execution_plan: Dict[str, Any], 
                                     context: Dict[str, Any]) -> None:
        """创建执行记录"""
        try:
            execution_data = {
                'execution_id': execution_id,
                'agent_type': 'execution_engine',
                'input_data': {
                    'execution_plan': execution_plan,
                    'context': context
                },
                'status': ExecutionStatus.PENDING.value
            }
            
            AIExecutionDAO.create_execution(execution_data)
            logger.info(f"执行记录已创建: {execution_id}")
            
        except Exception as e:
            logger.error(f"创建执行记录失败: {e}")
            raise
    
    async def _execute_plan_async(self, execution_id: str, execution_plan: Dict[str, Any], 
                                context: Dict[str, Any]) -> None:
        """异步执行计划"""
        try:
            # 更新执行状态
            await self._update_execution_status(execution_id, ExecutionStatus.RUNNING)
            
            # 发送执行开始事件
            await self._emit_event(ExecutionEvent(
                'execution_started', execution_id, 
                message=f"开始执行计划: {execution_plan.get('plan_name', 'Unknown')}"
            ))
            
            # 执行步骤
            steps = execution_plan.get('steps', [])
            execution_context = {
                'execution_id': execution_id,
                'variables': {},  # 步骤间共享变量
                **context
            }
            
            success_count = 0
            failed_count = 0
            
            for step in steps:
                try:
                    # 检查依赖
                    if not await self._check_step_dependencies(step, execution_context):
                        logger.warning(f"步骤依赖未满足，跳过: {step['step_id']}")
                        await self._update_step_status(execution_id, step['step_id'], StepStatus.SKIPPED)
                        continue
                    
                    # 执行步骤
                    step_result = await self._execute_step(execution_id, step, execution_context)
                    
                    if step_result['success']:
                        success_count += 1
                        # 更新共享变量
                        if 'output_variables' in step_result:
                            execution_context['variables'].update(step_result['output_variables'])
                    else:
                        failed_count += 1
                        
                        # 检查是否需要停止执行
                        if step.get('critical', True):
                            logger.error(f"关键步骤失败，停止执行: {step['step_id']}")
                            break
                
                except Exception as e:
                    failed_count += 1
                    logger.error(f"步骤执行异常: {step['step_id']}, {e}")
                    
                    await self._emit_event(ExecutionEvent(
                        'step_failed', execution_id, step['step_id'],
                        f"步骤执行异常: {str(e)}"
                    ))
                    
                    # 检查是否需要停止执行
                    if step.get('critical', True):
                        break
            
            # 确定最终状态
            final_status = ExecutionStatus.COMPLETED if failed_count == 0 else ExecutionStatus.FAILED
            
            # 更新执行状态
            await self._update_execution_status(execution_id, final_status, {
                'success_count': success_count,
                'failed_count': failed_count,
                'total_steps': len(steps)
            })
            
            # 发送执行完成事件
            await self._emit_event(ExecutionEvent(
                'execution_completed', execution_id,
                message=f"执行完成: 成功{success_count}个，失败{failed_count}个"
            ))
            
        except Exception as e:
            logger.error(f"执行计划异常: {execution_id}, {e}")
            
            # 更新为失败状态
            await self._update_execution_status(execution_id, ExecutionStatus.FAILED, {
                'error': str(e)
            })
            
            # 发送执行失败事件
            await self._emit_event(ExecutionEvent(
                'execution_failed', execution_id,
                message=f"执行失败: {str(e)}"
            ))
        
        finally:
            # 清理活跃执行
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _execute_step(self, execution_id: str, step: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤
        
        Args:
            execution_id: 执行ID
            step: 步骤定义
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 步骤执行结果
        """
        step_id = step['step_id']
        step_name = step.get('step_name', step_id)
        tool_name = step.get('tool_name', 'http_request')
        
        logger.info(f"开始执行步骤: {step_id} ({step_name})")
        
        try:
            # 创建步骤记录
            await self._create_step_record(execution_id, step)
            
            # 更新步骤状态为运行中
            await self._update_step_status(execution_id, step_id, StepStatus.RUNNING)
            
            # 发送步骤开始事件
            await self._emit_event(ExecutionEvent(
                'step_started', execution_id, step_id,
                f"开始执行步骤: {step_name}"
            ))
            
            # 准备步骤参数
            step_parameters = await self._prepare_step_parameters(step, context)
            
            # 调用MCP工具
            tool_result = await self.mcp_client.call_tool(
                tool_name=tool_name,
                parameters=step_parameters,
                context=context
            )
            
            # 处理工具结果
            if tool_result['success']:
                # 提取输出变量
                output_variables = self._extract_output_variables(step, tool_result['result'])
                
                # 更新步骤状态为完成
                await self._update_step_status(execution_id, step_id, StepStatus.COMPLETED, {
                    'output_data': tool_result['result'],
                    'output_variables': output_variables
                })
                
                # 发送步骤成功事件
                await self._emit_event(ExecutionEvent(
                    'step_succeeded', execution_id, step_id,
                    f"步骤执行成功: {step_name}",
                    {'result': tool_result['result']}
                ))
                
                logger.info(f"步骤执行成功: {step_id}")
                
                return {
                    'success': True,
                    'result': tool_result['result'],
                    'output_variables': output_variables
                }
            
            else:
                # 工具执行失败
                error_message = tool_result.get('error', '未知错误')
                
                # 更新步骤状态为失败
                await self._update_step_status(execution_id, step_id, StepStatus.FAILED, {
                    'error_message': error_message
                })
                
                # 发送步骤失败事件
                await self._emit_event(ExecutionEvent(
                    'step_failed', execution_id, step_id,
                    f"步骤执行失败: {error_message}"
                ))
                
                logger.error(f"步骤执行失败: {step_id}, {error_message}")
                
                return {
                    'success': False,
                    'error': error_message
                }
        
        except Exception as e:
            error_message = str(e)
            
            # 更新步骤状态为失败
            await self._update_step_status(execution_id, step_id, StepStatus.FAILED, {
                'error_message': error_message
            })
            
            # 发送步骤失败事件
            await self._emit_event(ExecutionEvent(
                'step_failed', execution_id, step_id,
                f"步骤执行异常: {error_message}"
            ))
            
            logger.error(f"步骤执行异常: {step_id}, {e}")
            
            return {
                'success': False,
                'error': error_message
            }
    
    async def _prepare_step_parameters(self, step: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """准备步骤参数"""
        parameters = step.get('parameters', {}).copy()
        variables = context.get('variables', {})
        
        # 替换参数中的变量引用
        def replace_variables(obj):
            if isinstance(obj, str):
                # 替换 {{variable_name}} 格式的变量
                import re
                pattern = r'\{\{(\w+)\}\}'
                
                def replacer(match):
                    var_name = match.group(1)
                    return str(variables.get(var_name, match.group(0)))
                
                return re.sub(pattern, replacer, obj)
            
            elif isinstance(obj, dict):
                return {k: replace_variables(v) for k, v in obj.items()}
            
            elif isinstance(obj, list):
                return [replace_variables(item) for item in obj]
            
            else:
                return obj
        
        return replace_variables(parameters)
    
    def _extract_output_variables(self, step: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """从步骤结果中提取输出变量"""
        output_variables = {}
        
        # 获取变量提取规则
        variable_extractions = step.get('variable_extractions', {})
        
        for var_name, extraction_rule in variable_extractions.items():
            try:
                if isinstance(extraction_rule, str):
                    # 简单的JSONPath提取
                    if extraction_rule.startswith('$.'):
                        # 这里可以使用jsonpath库进行提取
                        # 简化实现：直接从result中获取
                        if isinstance(result, dict):
                            keys = extraction_rule[2:].split('.')
                            value = result
                            for key in keys:
                                if isinstance(value, dict) and key in value:
                                    value = value[key]
                                else:
                                    value = None
                                    break
                            if value is not None:
                                output_variables[var_name] = value
                    else:
                        # 直接赋值
                        output_variables[var_name] = extraction_rule
                
                elif isinstance(extraction_rule, dict):
                    # 复杂提取规则
                    if extraction_rule.get('type') == 'jsonpath':
                        # JSONPath提取
                        path = extraction_rule.get('path', '')
                        # 实现JSONPath提取逻辑
                        pass
                    elif extraction_rule.get('type') == 'regex':
                        # 正则表达式提取
                        import re
                        pattern = extraction_rule.get('pattern', '')
                        text = str(result)
                        match = re.search(pattern, text)
                        if match:
                            output_variables[var_name] = match.group(1) if match.groups() else match.group(0)
            
            except Exception as e:
                logger.warning(f"提取变量失败: {var_name}, {e}")
        
        # 默认提取一些常用变量
        if isinstance(result, dict):
            # HTTP响应的常用字段
            if 'status_code' in result:
                output_variables['last_status_code'] = result['status_code']
            if 'body' in result and isinstance(result['body'], dict):
                # 提取响应体中的id字段
                if 'id' in result['body']:
                    output_variables['last_response_id'] = result['body']['id']
        
        return output_variables
    
    async def _check_step_dependencies(self, step: Dict[str, Any], 
                                     context: Dict[str, Any]) -> bool:
        """检查步骤依赖"""
        dependencies = step.get('dependencies', [])
        
        if not dependencies:
            return True
        
        # 检查依赖步骤是否都已完成
        execution_id = context['execution_id']
        
        for dep_step_id in dependencies:
            # 查询依赖步骤的状态
            steps = ExecutionStepDAO.get_steps_by_execution(execution_id)
            dep_step = next((s for s in steps if s['step_id'] == dep_step_id), None)
            
            if not dep_step or dep_step['status'] != StepStatus.COMPLETED.value:
                return False
        
        return True
    
    async def _create_step_record(self, execution_id: str, step: Dict[str, Any]) -> None:
        """创建步骤记录"""
        try:
            step_data = {
                'execution_id': execution_id,
                'step_id': step['step_id'],
                'step_name': step.get('step_name', step['step_id']),
                'step_type': step.get('step_type', 'unknown'),
                'status': StepStatus.PENDING.value,
                'input_data': step.get('parameters', {}),
                'system_id': step.get('system_id'),
                'module_id': step.get('module_id'),
                'api_interface_id': step.get('api_interface_id')
            }
            
            ExecutionStepDAO.create_step(step_data)
            
        except Exception as e:
            logger.error(f"创建步骤记录失败: {e}")
            raise
    
    async def _update_execution_status(self, execution_id: str, status: ExecutionStatus, 
                                     data: Optional[Dict[str, Any]] = None) -> None:
        """更新执行状态"""
        try:
            update_data = {'status': status.value}
            
            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                update_data['end_time'] = True
            
            if data:
                update_data['output_data'] = data
            
            AIExecutionDAO.update_execution(execution_id, update_data)
            
        except Exception as e:
            logger.error(f"更新执行状态失败: {e}")
    
    async def _update_step_status(self, execution_id: str, step_id: str, status: StepStatus, 
                                data: Optional[Dict[str, Any]] = None) -> None:
        """更新步骤状态"""
        try:
            update_data = {'status': status.value}
            
            if status == StepStatus.RUNNING:
                update_data['start_time'] = True
            elif status in [StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED]:
                update_data['end_time'] = True
            
            if data:
                update_data.update(data)
            
            ExecutionStepDAO.update_step(step_id, update_data)
            
        except Exception as e:
            logger.error(f"更新步骤状态失败: {e}")
    
    async def _emit_event(self, event: ExecutionEvent) -> None:
        """发送执行事件"""
        try:
            # 记录事件日志
            logger.info(f"执行事件: {event.event_type} - {event.message}")
            
            # 通知订阅者
            subscribers = self.event_subscribers.get(event.execution_id, [])
            for subscriber in subscribers:
                try:
                    await subscriber(event)
                except Exception as e:
                    logger.error(f"事件通知失败: {e}")
        
        except Exception as e:
            logger.error(f"发送事件失败: {e}")
    
    async def subscribe_events(self, execution_id: str) -> AsyncGenerator[ExecutionEvent, None]:
        """订阅执行事件
        
        Args:
            execution_id: 执行ID
            
        Yields:
            ExecutionEvent: 执行事件
        """
        event_queue = asyncio.Queue()
        
        async def event_handler(event: ExecutionEvent):
            await event_queue.put(event)
        
        # 添加订阅者
        if execution_id not in self.event_subscribers:
            self.event_subscribers[execution_id] = []
        self.event_subscribers[execution_id].append(event_handler)
        
        try:
            while True:
                event = await event_queue.get()
                yield event
                
                # 如果是执行完成事件，结束订阅
                if event.event_type in ['execution_completed', 'execution_failed']:
                    break
        
        finally:
            # 移除订阅者
            if execution_id in self.event_subscribers:
                self.event_subscribers[execution_id].remove(event_handler)
                if not self.event_subscribers[execution_id]:
                    del self.event_subscribers[execution_id]
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态
        
        Args:
            execution_id: 执行ID
            
        Returns:
            Optional[Dict[str, Any]]: 执行状态信息
        """
        try:
            # 获取执行记录
            execution = AIExecutionDAO.get_by_execution_id(execution_id)
            if not execution:
                return None
            
            # 获取步骤信息
            steps = ExecutionStepDAO.get_steps_by_execution(execution_id)
            
            # 统计信息
            total_steps = len(steps)
            completed_steps = len([s for s in steps if s['status'] == StepStatus.COMPLETED.value])
            failed_steps = len([s for s in steps if s['status'] == StepStatus.FAILED.value])
            running_steps = len([s for s in steps if s['status'] == StepStatus.RUNNING.value])
            
            return {
                'execution_id': execution_id,
                'status': execution['status'],
                'start_time': execution['start_time'],
                'end_time': execution.get('end_time'),
                'steps': {
                    'total': total_steps,
                    'completed': completed_steps,
                    'failed': failed_steps,
                    'running': running_steps,
                    'pending': total_steps - completed_steps - failed_steps - running_steps
                },
                'progress': completed_steps / total_steps if total_steps > 0 else 0,
                'step_details': steps
            }
        
        except Exception as e:
            logger.error(f"获取执行状态失败: {e}")
            return None
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return f"""你是一个专业的执行引擎，负责协调和监控API测试计划的执行。

你的职责：
1. 协调MCP工具执行测试步骤
2. 监控执行过程和状态变化
3. 处理步骤间的数据传递
4. 管理异常情况和重试机制
5. 提供实时的执行事件推送

执行原则：
- 严格按照依赖关系执行步骤
- 及时处理异常和错误
- 确保数据传递的正确性
- 提供详细的执行日志
- 支持并行执行优化

当前时间: {datetime.now().isoformat()}
Agent ID: {self.agent_id}
"""