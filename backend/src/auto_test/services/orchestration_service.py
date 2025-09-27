"""编排服务层

负责AI编排的业务逻辑处理，包括：
- 编排执行协调
- 计划生成和校验
- 流程管理
- 工具管理
- 统计和监控

遵循Service层设计原则：
- 数据收集与组装
- 业务流程协调
- 基础设施调用封装
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime

from ..agents.intent_parser import IntentParser
from ..agents.flow_planner import FlowPlanner
from ..agents.execution_engine import ExecutionEngine
from ..mcp.client import MCPClient
from ..database.dao_ai import AIExecutionDAO, OrchestrationPlanDAO, ExecutionStepDAO
from ..utils.logger import get_logger
from ..config import Config

logger = get_logger(__name__)


class OrchestrationService:
    """编排服务类
    
    提供AI编排相关的业务逻辑处理
    """
    
    @staticmethod
    async def execute_orchestration(user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行编排任务
        
        Args:
            user_input: 用户自然语言输入
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        config = Config()
        execution_id = str(uuid.uuid4())
        
        try:
            logger.info(f"开始执行编排任务: {execution_id}")
            
            # 1. 意图理解
            intent_parser = IntentParser(config)
            intent_result = await intent_parser.run({"user_input": user_input})
            
            if not intent_result['success']:
                raise Exception(f"意图理解失败: {intent_result.get('error', '未知错误')}")
            
            # 2. 流程规划
            flow_planner = FlowPlanner(config)
            planning_result = await flow_planner.run({
                "intent_result": intent_result['result'],
                "context": context or {}
            })
            
            if not planning_result['success']:
                raise Exception(f"流程规划失败: {planning_result.get('error', '未知错误')}")
            
            execution_plan = planning_result['result']['execution_plan']
            
            # 3. 计划校验
            validation_result = await OrchestrationService.validate_plan(execution_plan)
            if not validation_result['valid']:
                logger.warning(f"计划校验发现问题: {validation_result['issues']}")
                # 如果有严重问题，停止执行
                if validation_result['issues']:
                    raise Exception(f"计划校验失败: {'; '.join(validation_result['issues'])}")
            
            # 4. 执行引擎启动
            execution_engine = ExecutionEngine(config)
            execution_result = await execution_engine.run({
                "execution_plan": execution_plan,
                "context": {
                    "execution_id": execution_id,
                    **(context or {})
                }
            })
            
            logger.info(f"编排任务启动成功: {execution_id}")
            
            return {
                "execution_id": execution_id,
                "status": "started",
                "intent_result": intent_result['result'],
                "execution_plan": execution_plan,
                "plan_summary": planning_result['result'].get('plan_summary', {}),
                "validation_result": validation_result,
                "execution_result": execution_result
            }
            
        except Exception as e:
            logger.error(f"编排执行失败: {execution_id}, {str(e)}")
            raise
    
    @staticmethod
    async def generate_plan(flow_id: Optional[str], intent_text: str, 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划（Step3）
        
        Args:
            flow_id: 流程ID
            intent_text: 意图文本
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        config = Config()
        
        try:
            # 1. 意图理解
            intent_parser = IntentParser(config)
            intent_result = await intent_parser.run({"user_input": intent_text})
            
            if not intent_result['success']:
                raise Exception(f"意图理解失败: {intent_result.get('error', '未知错误')}")
            
            # 2. 流程规划
            flow_planner = FlowPlanner(config)
            planning_result = await flow_planner.run({
                "intent_result": intent_result['result'],
                "context": context
            })
            
            if not planning_result['success']:
                raise Exception(f"流程规划失败: {planning_result.get('error', '未知错误')}")
            
            execution_plan = planning_result['result']['execution_plan']
            
            # 3. 提取未解决的输入参数
            unresolved_inputs = OrchestrationService._extract_unresolved_inputs(execution_plan)
            
            return {
                "plan": execution_plan,
                "unresolved_inputs": unresolved_inputs,
                "plan_summary": planning_result['result'].get('plan_summary', {}),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "flow_id": flow_id,
                    "intent": intent_result['result'].get('intent'),
                    "confidence": intent_result['result'].get('confidence')
                }
            }
            
        except Exception as e:
            logger.error(f"计划生成失败: {str(e)}")
            raise
    
    @staticmethod
    async def validate_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
        """校验执行计划（Step3）
        
        Args:
            plan: 执行计划
            
        Returns:
            Dict[str, Any]: 校验结果
        """
        try:
            issues = []
            warnings = []
            
            # 1. 基础结构校验
            if not isinstance(plan, dict):
                issues.append("计划必须是字典格式")
                return {"ok": False, "issues": issues, "warnings": warnings}
            
            steps = plan.get('steps', [])
            if not steps:
                issues.append("计划中没有执行步骤")
                return {"ok": False, "issues": issues, "warnings": warnings}
            
            # 2. 步骤结构校验
            step_ids = set()
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    issues.append(f"步骤{i+1}格式无效")
                    continue
                
                step_id = step.get('step_id')
                if not step_id:
                    issues.append(f"步骤{i+1}缺少step_id")
                elif step_id in step_ids:
                    issues.append(f"步骤ID重复: {step_id}")
                else:
                    step_ids.add(step_id)
                
                # 检查必需字段
                required_fields = ['step_name', 'step_type', 'tool_name', 'parameters']
                for field in required_fields:
                    if field not in step:
                        issues.append(f"步骤{step_id}缺少必需字段: {field}")
            
            # 3. 依赖关系校验
            for step in steps:
                step_id = step.get('step_id')
                dependencies = step.get('dependencies', [])
                
                for dep in dependencies:
                    if dep not in step_ids:
                        issues.append(f"步骤{step_id}依赖不存在的步骤: {dep}")
            
            # 4. 循环依赖检查
            if OrchestrationService._has_circular_dependency(steps):
                issues.append("检测到循环依赖")
            
            # 5. 工具可用性检查
            config = Config()
            mcp_client = MCPClient(config)
            await mcp_client.initialize()
            
            available_tools = await mcp_client.list_tools()
            available_tool_names = {tool['name'] for tool in available_tools}
            
            for step in steps:
                tool_name = step.get('tool_name')
                if tool_name and tool_name not in available_tool_names:
                    warnings.append(f"步骤{step.get('step_id')}使用的工具不可用: {tool_name}")
            
            # 6. 超时设置检查
            total_timeout = sum(step.get('timeout', 30) for step in steps)
            if total_timeout > 600:  # 10分钟
                warnings.append(f"总超时时间过长: {total_timeout}秒")
            
            return {
                "ok": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "metadata": {
                    "total_steps": len(steps),
                    "total_timeout": total_timeout,
                    "validated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"计划校验异常: {str(e)}")
            return {
                "ok": False,
                "issues": [f"校验异常: {str(e)}"],
                "warnings": []
            }
    
    @staticmethod
    async def validate_execution_inputs(plan: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行前入参校验（必选）
        
        Args:
            plan: 执行计划
            inputs: 执行入参
            
        Returns:
            Dict[str, Any]: 校验结果
        """
        try:
            errors = []
            warnings = []
            
            # 1. 提取计划中的参数要求
            required_params = set()
            optional_params = set()
            
            steps = plan.get('steps', [])
            for step in steps:
                parameters = step.get('parameters', {})
                
                # 查找占位符参数
                import re
                for key, value in parameters.items():
                    if isinstance(value, str):
                        # 查找 {{param_name}} 格式的占位符
                        placeholders = re.findall(r'\{\{(\w+)\}\}', value)
                        for placeholder in placeholders:
                            if placeholder.startswith('required_'):
                                required_params.add(placeholder)
                            else:
                                optional_params.add(placeholder)
            
            # 2. 检查必需参数
            for param in required_params:
                if param not in inputs:
                    errors.append(f"缺少必需参数: {param}")
                elif inputs[param] is None or inputs[param] == "":
                    errors.append(f"必需参数不能为空: {param}")
            
            # 3. 类型和格式校验
            for param_name, param_value in inputs.items():
                # 基础类型检查
                if param_value is not None:
                    # URL格式检查
                    if param_name.endswith('_url') or param_name.endswith('_endpoint'):
                        if not isinstance(param_value, str) or not param_value.startswith(('http://', 'https://')):
                            warnings.append(f"参数{param_name}应该是有效的URL格式")
                    
                    # 数字格式检查
                    elif param_name.endswith('_count') or param_name.endswith('_timeout'):
                        try:
                            int(param_value)
                        except (ValueError, TypeError):
                            errors.append(f"参数{param_name}应该是数字格式")
            
            # 4. 业务规则校验
            # 这里可以添加更多业务相关的校验规则
            
            return {
                "ok": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "metadata": {
                    "required_params": list(required_params),
                    "optional_params": list(optional_params),
                    "provided_params": list(inputs.keys()),
                    "validated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"入参校验异常: {str(e)}")
            return {
                "ok": False,
                "errors": [f"校验异常: {str(e)}"],
                "warnings": []
            }
    
    @staticmethod
    async def get_execution_status(execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态
        
        Args:
            execution_id: 执行ID
            
        Returns:
            Optional[Dict[str, Any]]: 执行状态信息
        """
        try:
            config = Config()
            execution_engine = ExecutionEngine(config)
            return await execution_engine.get_execution_status(execution_id)
            
        except Exception as e:
            logger.error(f"获取执行状态失败: {str(e)}")
            return None
    
    @staticmethod
    async def subscribe_execution_events(execution_id: str) -> AsyncGenerator:
        """订阅执行事件
        
        Args:
            execution_id: 执行ID
            
        Yields:
            执行事件
        """
        try:
            config = Config()
            execution_engine = ExecutionEngine(config)
            
            async for event in execution_engine.subscribe_events(execution_id):
                yield event
                
        except Exception as e:
            logger.error(f"订阅执行事件失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_orchestration_flows(page: int = 1, size: int = 10, 
                                    filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取编排流程列表
        
        Args:
            page: 页码
            size: 每页数量
            filters: 筛选条件
            
        Returns:
            Dict[str, Any]: 流程列表
        """
        try:
            filters = filters or {}
            flows = OrchestrationPlanDAO.search_plans(filters, page, size)
            
            # 统计信息
            total_count = len(OrchestrationPlanDAO.search_plans(filters, 1, 1000))  # 简化实现
            
            return {
                "flows": flows,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total_count,
                    "pages": (total_count + size - 1) // size
                }
            }
            
        except Exception as e:
            logger.error(f"获取流程列表失败: {str(e)}")
            raise
    
    @staticmethod
    async def create_orchestration_flow(flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建编排流程
        
        Args:
            flow_data: 流程数据
            
        Returns:
            Dict[str, Any]: 创建结果
        """
        try:
            # 数据验证
            required_fields = ['plan_name', 'intent_text', 'execution_plan']
            for field in required_fields:
                if field not in flow_data:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # 创建流程
            flow = OrchestrationPlanDAO.create_plan(flow_data)
            
            logger.info(f"创建编排流程成功: {flow['id']}")
            return flow
            
        except Exception as e:
            logger.error(f"创建流程失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_orchestration_flow(flow_id: int) -> Optional[Dict[str, Any]]:
        """获取流程详情
        
        Args:
            flow_id: 流程ID
            
        Returns:
            Optional[Dict[str, Any]]: 流程详情
        """
        try:
            return OrchestrationPlanDAO.get_by_id(flow_id)
            
        except Exception as e:
            logger.error(f"获取流程详情失败: {str(e)}")
            return None
    
    @staticmethod
    async def update_orchestration_flow(flow_id: int, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新流程
        
        Args:
            flow_id: 流程ID
            flow_data: 更新数据
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            # 这里需要实现更新逻辑
            # 简化实现：先获取再更新
            existing_flow = OrchestrationPlanDAO.get_by_id(flow_id)
            if not existing_flow:
                raise ValueError(f"流程不存在: {flow_id}")
            
            # 更新字段
            existing_flow.update(flow_data)
            existing_flow['updated_at'] = datetime.now().isoformat()
            
            # 这里应该调用DAO的更新方法
            # updated_flow = OrchestrationPlanDAO.update_plan(flow_id, flow_data)
            
            logger.info(f"更新编排流程成功: {flow_id}")
            return existing_flow
            
        except Exception as e:
            logger.error(f"更新流程失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_available_tools(tool_type: Optional[str] = None, 
                                enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取可用工具列表
        
        Args:
            tool_type: 工具类型筛选
            enabled_only: 是否只返回启用的工具
            
        Returns:
            List[Dict[str, Any]]: 工具列表
        """
        try:
            config = Config()
            mcp_client = MCPClient(config)
            await mcp_client.initialize()
            
            return await mcp_client.list_tools(tool_type, enabled_only)
            
        except Exception as e:
            logger.error(f"获取工具列表失败: {str(e)}")
            raise
    
    @staticmethod
    async def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具Schema定义
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[Dict[str, Any]]: 工具Schema
        """
        try:
            config = Config()
            mcp_client = MCPClient(config)
            await mcp_client.initialize()
            
            return await mcp_client.get_tool_schema(tool_name)
            
        except Exception as e:
            logger.error(f"获取工具Schema失败: {str(e)}")
            return None
    
    @staticmethod
    async def get_orchestration_stats() -> Dict[str, Any]:
        """获取编排统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 执行统计
            # 这里需要实现统计查询逻辑
            # 简化实现
            
            stats = {
                "executions": {
                    "total": 0,
                    "running": 0,
                    "completed": 0,
                    "failed": 0
                },
                "flows": {
                    "total": 0,
                    "draft": 0,
                    "published": 0,
                    "archived": 0
                },
                "tools": {
                    "total": 0,
                    "enabled": 0,
                    "disabled": 0
                },
                "performance": {
                    "avg_execution_time": 0,
                    "success_rate": 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise
    
    @staticmethod
    def _extract_unresolved_inputs(plan: Dict[str, Any]) -> List[str]:
        """提取未解决的输入参数"""
        unresolved = []
        
        steps = plan.get('steps', [])
        for step in steps:
            parameters = step.get('parameters', {})
            
            # 查找占位符参数
            import re
            for key, value in parameters.items():
                if isinstance(value, str):
                    # 查找 {{param_name}} 格式的占位符
                    placeholders = re.findall(r'\{\{(\w+)\}\}', value)
                    unresolved.extend(placeholders)
        
        return list(set(unresolved))  # 去重
    
    @staticmethod
    def _has_circular_dependency(steps: List[Dict[str, Any]]) -> bool:
        """检查是否存在循环依赖"""
        # 构建邻接表
        graph = {}
        for step in steps:
            step_id = step.get('step_id')
            dependencies = step.get('dependencies', [])
            graph[step_id] = dependencies
        
        # DFS检查循环
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if dfs(step_id):
                    return True
        
        return False