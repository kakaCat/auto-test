"""流程规划组件

负责基于意图理解结果生成可执行的API调用计划。
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..services.api_interface_service import ApiInterfaceService
from ..services.system_service import SystemService
from ..services.module_service import ModuleService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionStep(BaseModel):
    """执行步骤定义"""
    step_id: str = Field(description="步骤ID")
    step_name: str = Field(description="步骤名称")
    step_type: str = Field(description="步骤类型")
    tool_name: str = Field(description="使用的MCP工具")
    parameters: Dict[str, Any] = Field(description="步骤参数")
    dependencies: List[str] = Field(description="依赖的步骤ID", default_factory=list)
    timeout: int = Field(description="超时时间(秒)", default=30)
    retry_count: int = Field(description="重试次数", default=3)
    system_id: Optional[int] = Field(description="关联的系统ID", default=None)
    module_id: Optional[int] = Field(description="关联的模块ID", default=None)
    api_interface_id: Optional[int] = Field(description="关联的API接口ID", default=None)


class ExecutionPlan(BaseModel):
    """执行计划定义"""
    plan_id: str = Field(description="计划ID")
    plan_name: str = Field(description="计划名称")
    description: str = Field(description="计划描述")
    steps: List[ExecutionStep] = Field(description="执行步骤列表")
    metadata: Dict[str, Any] = Field(description="元数据", default_factory=dict)
    estimated_duration: int = Field(description="预估执行时间(秒)", default=0)


class FlowPlanner(BaseAgent):
    """流程规划组件
    
    负责：
    - 基于意图理解结果生成执行计划
    - 解析API接口依赖关系
    - 生成参数映射和数据传递
    - 优化执行顺序和并行度
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # 步骤类型映射
        self.step_type_mapping = {
            'api_call': 'http_request',
            'api_test': 'api_call',
            'data_validation': 'validate_response',
            'wait': 'wait_for',
            'workflow_execution': 'workflow_sequence'
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理流程规划
        
        Args:
            input_data: 包含意图理解结果的数据
            
        Returns:
            Dict[str, Any]: 执行计划
        """
        # 验证输入
        self.validate_input(input_data, ['intent_result'])
        
        intent_result = input_data['intent_result']
        context = input_data.get('context', {})
        
        logger.info(f"开始流程规划: {intent_result.get('intent')}")
        
        try:
            # 1. 分析意图和动作
            actions = intent_result.get('actions', [])
            entities = intent_result.get('entities', {})
            
            # 2. 生成基础执行步骤
            base_steps = await self._generate_base_steps(actions, entities, context)
            
            # 3. 解析API接口依赖
            enriched_steps = await self._enrich_steps_with_api_info(base_steps, entities)
            
            # 4. 优化执行顺序
            optimized_steps = await self._optimize_execution_order(enriched_steps)
            
            # 5. 生成完整执行计划
            execution_plan = await self._create_execution_plan(
                optimized_steps, intent_result, context
            )
            
            logger.info(f"流程规划完成: {len(execution_plan.steps)}个步骤")
            
            return {
                'execution_plan': execution_plan.dict(),
                'plan_summary': self._generate_plan_summary(execution_plan),
                'validation_result': await self._validate_plan(execution_plan)
            }
            
        except Exception as e:
            logger.error(f"流程规划失败: {e}")
            raise
    
    async def _generate_base_steps(self, actions: List[Dict[str, Any]], 
                                 entities: Dict[str, Any], 
                                 context: Dict[str, Any]) -> List[ExecutionStep]:
        """生成基础执行步骤
        
        Args:
            actions: 动作列表
            entities: 实体信息
            context: 上下文信息
            
        Returns:
            List[ExecutionStep]: 基础步骤列表
        """
        steps = []
        
        for i, action in enumerate(actions):
            step_id = f"step_{i+1}"
            action_type = action.get('action', 'generic_test')
            
            # 映射到MCP工具
            tool_name = self.step_type_mapping.get(action_type, 'http_request')
            
            # 构建步骤参数
            parameters = await self._build_step_parameters(action, entities, context)
            
            step = ExecutionStep(
                step_id=step_id,
                step_name=action.get('target', f'步骤{i+1}'),
                step_type=action_type,
                tool_name=tool_name,
                parameters=parameters,
                dependencies=action.get('dependencies', []),
                timeout=action.get('timeout', 30),
                retry_count=3
            )
            
            steps.append(step)
        
        return steps
    
    async def _build_step_parameters(self, action: Dict[str, Any], 
                                   entities: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """构建步骤参数
        
        Args:
            action: 动作定义
            entities: 实体信息
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 步骤参数
        """
        parameters = action.get('parameters', {}).copy()
        
        # 根据动作类型构建特定参数
        action_type = action.get('action', 'generic_test')
        
        if action_type == 'api_call':
            # API调用参数
            parameters.update({
                'method': parameters.get('method', 'GET'),
                'url': action.get('target', ''),
                'headers': parameters.get('headers', {}),
                'timeout': action.get('timeout', 30)
            })
            
        elif action_type == 'api_test':
            # API测试参数（使用api_call工具）
            api_endpoint = action.get('target', '')
            if api_endpoint in entities.get('api_endpoints', []):
                # 尝试从数据库查找API接口信息
                api_info = await self._find_api_interface(api_endpoint)
                if api_info:
                    parameters['api_id'] = api_info['id']
                else:
                    parameters['url'] = api_endpoint
                    parameters['method'] = parameters.get('method', 'GET')
            
        elif action_type == 'data_validation':
            # 数据验证参数
            parameters.update({
                'rules': entities.get('validation_rules', []),
                'strict': parameters.get('strict', False)
            })
            
        elif action_type == 'wait':
            # 等待参数
            parameters.update({
                'duration': parameters.get('duration', 5),
                'condition': parameters.get('condition', '')
            })
        
        # 添加上下文参数
        if context.get('base_url'):
            parameters['base_url'] = context['base_url']
        
        return parameters
    
    async def _enrich_steps_with_api_info(self, steps: List[ExecutionStep], 
                                        entities: Dict[str, Any]) -> List[ExecutionStep]:
        """使用API接口信息丰富步骤
        
        Args:
            steps: 基础步骤列表
            entities: 实体信息
            
        Returns:
            List[ExecutionStep]: 丰富后的步骤列表
        """
        enriched_steps = []
        
        for step in steps:
            enriched_step = step.copy()
            
            # 如果是API相关步骤，尝试关联API接口信息
            if step.step_type in ['api_call', 'api_test']:
                api_info = await self._resolve_api_interface(step, entities)
                if api_info:
                    enriched_step.system_id = api_info.get('system_id')
                    enriched_step.module_id = api_info.get('module_id')
                    enriched_step.api_interface_id = api_info.get('id')
                    
                    # 更新参数
                    if 'api_id' not in enriched_step.parameters:
                        enriched_step.parameters['api_id'] = api_info['id']
            
            enriched_steps.append(enriched_step)
        
        return enriched_steps
    
    async def _resolve_api_interface(self, step: ExecutionStep, 
                                   entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析API接口信息
        
        Args:
            step: 执行步骤
            entities: 实体信息
            
        Returns:
            Optional[Dict[str, Any]]: API接口信息
        """
        try:
            # 从参数中获取API标识
            api_id = step.parameters.get('api_id')
            if api_id:
                return ApiInterfaceService.get_api_interface_by_id(api_id)
            
            # 从URL路径匹配
            url = step.parameters.get('url', '')
            method = step.parameters.get('method', 'GET')
            
            if url:
                return await self._find_api_interface_by_path(url, method)
            
            # 从步骤名称匹配
            step_name = step.step_name
            return await self._find_api_interface_by_name(step_name)
            
        except Exception as e:
            logger.warning(f"解析API接口信息失败: {e}")
            return None
    
    async def _find_api_interface(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """根据端点查找API接口"""
        try:
            # 简单的路径匹配
            from ..models.api_interface import ApiInterfaceQueryRequest
            query = ApiInterfaceQueryRequest(
                keyword=endpoint,
                enabled_only=True
            )
            interfaces = ApiInterfaceService.search_api_interfaces(query)
            
            if interfaces:
                return interfaces[0]
            
            return None
            
        except Exception as e:
            logger.warning(f"查找API接口失败: {e}")
            return None
    
    async def _find_api_interface_by_path(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """根据路径和方法查找API接口"""
        try:
            # 这里可以实现更复杂的路径匹配逻辑
            from ..models.api_interface import ApiInterfaceQueryRequest
            query = ApiInterfaceQueryRequest(
                keyword=path,
                method=method,
                enabled_only=True
            )
            interfaces = ApiInterfaceService.search_api_interfaces(query)
            
            # 精确匹配路径
            for interface in interfaces:
                if interface['path'] == path and interface['method'] == method:
                    return interface
            
            # 模糊匹配
            if interfaces:
                return interfaces[0]
            
            return None
            
        except Exception as e:
            logger.warning(f"根据路径查找API接口失败: {e}")
            return None
    
    async def _find_api_interface_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查找API接口"""
        try:
            from ..models.api_interface import ApiInterfaceQueryRequest
            query = ApiInterfaceQueryRequest(
                keyword=name,
                enabled_only=True
            )
            interfaces = ApiInterfaceService.search_api_interfaces(query)
            
            if interfaces:
                return interfaces[0]
            
            return None
            
        except Exception as e:
            logger.warning(f"根据名称查找API接口失败: {e}")
            return None
    
    async def _optimize_execution_order(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """优化执行顺序
        
        Args:
            steps: 步骤列表
            
        Returns:
            List[ExecutionStep]: 优化后的步骤列表
        """
        # 构建依赖图
        dependency_graph = {}
        step_map = {step.step_id: step for step in steps}
        
        for step in steps:
            dependency_graph[step.step_id] = step.dependencies
        
        # 拓扑排序
        sorted_steps = self._topological_sort(dependency_graph, step_map)
        
        # 优化并行执行机会
        optimized_steps = self._optimize_parallel_execution(sorted_steps)
        
        return optimized_steps
    
    def _topological_sort(self, dependency_graph: Dict[str, List[str]], 
                         step_map: Dict[str, ExecutionStep]) -> List[ExecutionStep]:
        """拓扑排序"""
        in_degree = {step_id: 0 for step_id in dependency_graph}
        
        # 计算入度
        for step_id, deps in dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[step_id] += 1
        
        # 队列初始化
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(step_map[current])
            
            # 更新依赖此步骤的其他步骤
            for step_id, deps in dependency_graph.items():
                if current in deps:
                    in_degree[step_id] -= 1
                    if in_degree[step_id] == 0:
                        queue.append(step_id)
        
        return result
    
    def _optimize_parallel_execution(self, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        """优化并行执行"""
        # 简单实现：标记可以并行执行的步骤
        for i, step in enumerate(steps):
            # 检查是否可以与前面的步骤并行
            can_parallel = True
            for j in range(i):
                prev_step = steps[j]
                if (step.step_id in prev_step.dependencies or 
                    prev_step.step_id in step.dependencies):
                    can_parallel = False
                    break
            
            # 在参数中标记并行信息（简化处理）
            if 'metadata' not in step.parameters:
                step.parameters['metadata'] = {}
            step.parameters['metadata']['can_parallel'] = can_parallel
        
        return steps
    
    async def _create_execution_plan(self, steps: List[ExecutionStep], 
                                   intent_result: Dict[str, Any], 
                                   context: Dict[str, Any]) -> ExecutionPlan:
        """创建完整执行计划
        
        Args:
            steps: 优化后的步骤列表
            intent_result: 意图理解结果
            context: 上下文信息
            
        Returns:
            ExecutionPlan: 执行计划
        """
        plan_id = f"plan_{int(time.time() * 1000)}"
        
        # 计算预估执行时间
        estimated_duration = sum(step.timeout for step in steps)
        
        # 构建元数据
        metadata = {
            'intent': intent_result.get('intent'),
            'confidence': intent_result.get('confidence'),
            'involved_system_ids': list(set(
                step.system_id for step in steps if step.system_id
            )),
            'involved_module_ids': list(set(
                step.module_id for step in steps if step.module_id
            )),
            'total_steps': len(steps),
            'api_calls': len([s for s in steps if s.step_type in ['api_call', 'api_test']]),
            'validations': len([s for s in steps if s.step_type == 'data_validation']),
            'created_at': datetime.now().isoformat(),
            'context': context
        }
        
        return ExecutionPlan(
            plan_id=plan_id,
            plan_name=f"执行计划_{intent_result.get('intent', 'unknown')}",
            description=f"基于意图'{intent_result.get('intent')}'生成的执行计划",
            steps=steps,
            metadata=metadata,
            estimated_duration=estimated_duration
        )
    
    def _generate_plan_summary(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """生成计划摘要
        
        Args:
            plan: 执行计划
            
        Returns:
            Dict[str, Any]: 计划摘要
        """
        return {
            'plan_id': plan.plan_id,
            'total_steps': len(plan.steps),
            'estimated_duration': plan.estimated_duration,
            'step_types': {
                step_type: len([s for s in plan.steps if s.step_type == step_type])
                for step_type in set(s.step_type for s in plan.steps)
            },
            'involved_systems': len(plan.metadata.get('involved_system_ids', [])),
            'involved_modules': len(plan.metadata.get('involved_module_ids', [])),
            'parallel_opportunities': len([
                s for s in plan.steps 
                if s.parameters.get('metadata', {}).get('can_parallel', False)
            ])
        }
    
    async def _validate_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """验证执行计划
        
        Args:
            plan: 执行计划
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        issues = []
        warnings = []
        
        # 检查步骤依赖
        step_ids = {step.step_id for step in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    issues.append(f"步骤 {step.step_id} 依赖不存在的步骤 {dep}")
        
        # 检查循环依赖
        if self._has_circular_dependency(plan.steps):
            issues.append("检测到循环依赖")
        
        # 检查API接口可用性
        for step in plan.steps:
            if step.api_interface_id:
                api_info = ApiInterfaceDAO.get_by_id(step.api_interface_id)
                if not api_info or not api_info.get('enabled'):
                    warnings.append(f"步骤 {step.step_id} 关联的API接口不可用")
        
        # 检查超时设置
        total_timeout = sum(step.timeout for step in plan.steps)
        if total_timeout > 300:  # 5分钟
            warnings.append(f"总超时时间过长: {total_timeout}秒")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_timeout': total_timeout
        }
    
    def _has_circular_dependency(self, steps: List[ExecutionStep]) -> bool:
        """检查是否存在循环依赖"""
        # 构建邻接表
        graph = {step.step_id: step.dependencies for step in steps}
        
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
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return f"""你是一个专业的流程规划专家，负责将测试意图转换为可执行的API调用计划。

你的职责：
1. 分析意图理解结果，提取关键动作
2. 生成结构化的执行步骤
3. 解析API接口依赖关系
4. 优化执行顺序和并行度
5. 确保计划的可执行性和正确性

支持的步骤类型：
- api_call: API接口调用
- api_test: API接口测试
- data_validation: 数据验证
- wait: 等待延时
- workflow_execution: 工作流执行

请确保生成的执行计划：
- 步骤依赖关系正确
- 参数映射完整
- 超时设置合理
- 错误处理完善

当前时间: {datetime.now().isoformat()}
Agent ID: {self.agent_id}
"""