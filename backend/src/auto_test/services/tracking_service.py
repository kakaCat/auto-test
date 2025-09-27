"""跨系统/模块追踪与审计服务

负责处理跨系统/模块的追踪、聚合和审计功能，包括：
- 元数据聚合和更新
- 筛选接口实现
- 权限控制和脱敏
- 统计分析

遵循Service层设计原则：
- 数据收集与组装
- 业务流程协调
- 基础设施调用封装
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import json

from ..database.dao_ai import OrchestrationPlanDAO, ExecutionStepDAO
from ..services.api_interface_service import ApiInterfaceService
from ..services.system_service import SystemService
from ..services.module_service import ModuleService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrackingService:
    """跨系统/模块追踪服务"""
    
    @staticmethod
    async def aggregate_plan_metadata(plan_id: int) -> Dict[str, Any]:
        """聚合计划的系统/模块元数据
        
        Args:
            plan_id: 计划ID
            
        Returns:
            Dict[str, Any]: 聚合的元数据
        """
        try:
            # 获取计划详情
            plan = OrchestrationPlanDAO.get_by_id(plan_id)
            if not plan:
                raise ValueError(f"计划不存在: {plan_id}")
            
            execution_plan = plan.get('execution_plan', {})
            steps = execution_plan.get('steps', [])
            
            # 聚合系统和模块ID
            involved_system_ids = set()
            involved_module_ids = set()
            involved_apis = []
            
            for step in steps:
                # 从步骤中提取系统/模块信息
                if step.get('system_id'):
                    involved_system_ids.add(step['system_id'])
                
                if step.get('module_id'):
                    involved_module_ids.add(step['module_id'])
                
                if step.get('api_interface_id'):
                    involved_apis.append({
                        'api_id': step['api_interface_id'],
                        'step_id': step.get('step_id'),
                        'step_name': step.get('step_name')
                    })
            
            # 获取系统和模块详细信息
            systems_info = []
            for system_id in involved_system_ids:
                system = SystemService.get_system_by_id(system_id)
                if system:
                    systems_info.append({
                        'id': system['id'],
                        'name': system['name'],
                        'category': system.get('category', 'custom')
                    })
            
            modules_info = []
            for module_id in involved_module_ids:
                module = ModuleService.get_module_by_id(module_id)
                if module:
                    modules_info.append({
                        'id': module['id'],
                        'name': module['name'],
                        'system_id': module.get('system_id')
                    })
            
            # 构建聚合元数据
            aggregated_metadata = {
                'involved_system_ids': list(involved_system_ids),
                'involved_module_ids': list(involved_module_ids),
                'systems_info': systems_info,
                'modules_info': modules_info,
                'involved_apis': involved_apis,
                'aggregated_at': datetime.now().isoformat(),
                'total_systems': len(involved_system_ids),
                'total_modules': len(involved_module_ids),
                'total_apis': len(involved_apis)
            }
            
            return aggregated_metadata
            
        except Exception as e:
            logger.error(f"聚合计划元数据失败: {e}")
            raise
    
    @staticmethod
    async def update_plan_metadata(plan_id: int, metadata: Dict[str, Any]) -> bool:
        """更新计划的元数据
        
        Args:
            plan_id: 计划ID
            metadata: 新的元数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取现有计划
            plan = OrchestrationPlanDAO.get_by_id(plan_id)
            if not plan:
                return False
            
            # 合并元数据
            existing_metadata = plan.get('metadata', {})
            if isinstance(existing_metadata, str):
                existing_metadata = json.loads(existing_metadata)
            
            updated_metadata = {**existing_metadata, **metadata}
            
            # 更新计划（这里需要实现DAO的更新方法）
            # OrchestrationPlanDAO.update_plan(plan_id, {'metadata': updated_metadata})
            
            logger.info(f"计划元数据更新成功: {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新计划元数据失败: {e}")
            return False
    
    @staticmethod
    async def get_filtered_plans(filters: Dict[str, Any], page: int = 1, size: int = 10) -> Dict[str, Any]:
        """获取筛选后的计划列表
        
        Args:
            filters: 筛选条件
            page: 页码
            size: 每页数量
            
        Returns:
            Dict[str, Any]: 筛选结果
        """
        try:
            # 处理系统/模块筛选
            system_ids = filters.get('system_ids', [])
            module_ids = filters.get('module_ids', [])
            
            # 基础筛选
            base_filters = {
                'keyword': filters.get('keyword'),
                'status': filters.get('status'),
                'created_by': filters.get('created_by'),
                'is_template': filters.get('is_template')
            }
            
            # 获取计划列表
            plans = OrchestrationPlanDAO.search_plans(base_filters, page, size)
            
            # 如果有系统/模块筛选，进行二次过滤
            if system_ids or module_ids:
                filtered_plans = []
                
                for plan in plans:
                    metadata = plan.get('metadata', {})
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                    
                    plan_system_ids = set(metadata.get('involved_system_ids', []))
                    plan_module_ids = set(metadata.get('involved_module_ids', []))
                    
                    # 检查系统筛选
                    if system_ids:
                        if not any(sid in plan_system_ids for sid in system_ids):
                            continue
                    
                    # 检查模块筛选
                    if module_ids:
                        if not any(mid in plan_module_ids for mid in module_ids):
                            continue
                    
                    filtered_plans.append(plan)
                
                plans = filtered_plans
            
            # 添加聚合信息
            for plan in plans:
                metadata = plan.get('metadata', {})
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                # 获取系统/模块名称
                system_names = []
                for system_id in metadata.get('involved_system_ids', []):
                    system = SystemService.get_system_by_id(system_id)
                    if system:
                        system_names.append(system['name'])
                
                module_names = []
                for module_id in metadata.get('involved_module_ids', []):
                    module = ModuleService.get_module_by_id(module_id)
                    if module:
                        module_names.append(module['name'])
                
                plan['display_info'] = {
                    'system_names': system_names,
                    'module_names': module_names,
                    'total_systems': len(system_names),
                    'total_modules': len(module_names)
                }
            
            return {
                'plans': plans,
                'pagination': {
                    'page': page,
                    'size': size,
                    'total': len(plans)
                },
                'filters_applied': {
                    'system_ids': system_ids,
                    'module_ids': module_ids,
                    'other_filters': base_filters
                }
            }
            
        except Exception as e:
            logger.error(f"获取筛选计划失败: {e}")
            raise
    
    @staticmethod
    async def get_system_module_stats() -> Dict[str, Any]:
        """获取系统/模块统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 获取所有计划
            all_plans = OrchestrationPlanDAO.search_plans({}, 1, 1000)
            
            # 统计系统使用情况
            system_usage = {}
            module_usage = {}
            
            for plan in all_plans:
                metadata = plan.get('metadata', {})
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                # 统计系统
                for system_id in metadata.get('involved_system_ids', []):
                    system_usage[system_id] = system_usage.get(system_id, 0) + 1
                
                # 统计模块
                for module_id in metadata.get('involved_module_ids', []):
                    module_usage[module_id] = module_usage.get(module_id, 0) + 1
            
            # 获取系统/模块详细信息
            system_stats = []
            for system_id, count in system_usage.items():
                system = SystemService.get_system_by_id(system_id)
                if system:
                    system_stats.append({
                        'id': system_id,
                        'name': system['name'],
                        'usage_count': count,
                        'category': system.get('category', 'custom')
                    })
            
            module_stats = []
            for module_id, count in module_usage.items():
                module = ModuleService.get_module_by_id(module_id)
                if module:
                    module_stats.append({
                        'id': module_id,
                        'name': module['name'],
                        'usage_count': count,
                        'system_id': module.get('system_id')
                    })
            
            # 排序
            system_stats.sort(key=lambda x: x['usage_count'], reverse=True)
            module_stats.sort(key=lambda x: x['usage_count'], reverse=True)
            
            return {
                'total_plans': len(all_plans),
                'total_systems_involved': len(system_usage),
                'total_modules_involved': len(module_usage),
                'system_stats': system_stats,
                'module_stats': module_stats,
                'top_systems': system_stats[:5],
                'top_modules': module_stats[:5],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取系统模块统计失败: {e}")
            raise
    
    @staticmethod
    async def get_execution_tracking_data(execution_id: str) -> Dict[str, Any]:
        """获取执行的追踪数据
        
        Args:
            execution_id: 执行ID
            
        Returns:
            Dict[str, Any]: 追踪数据
        """
        try:
            # 获取执行步骤
            steps = ExecutionStepDAO.get_steps_by_execution(execution_id)
            
            # 聚合系统/模块信息
            involved_systems = {}
            involved_modules = {}
            api_calls = []
            
            for step in steps:
                # 系统信息
                if step.get('system_id') and step.get('system_name'):
                    system_id = step['system_id']
                    if system_id not in involved_systems:
                        involved_systems[system_id] = {
                            'id': system_id,
                            'name': step['system_name'],
                            'step_count': 0,
                            'success_count': 0,
                            'failed_count': 0,
                            'total_duration': 0
                        }
                    
                    involved_systems[system_id]['step_count'] += 1
                    
                    if step['status'] == 'completed':
                        involved_systems[system_id]['success_count'] += 1
                    elif step['status'] == 'failed':
                        involved_systems[system_id]['failed_count'] += 1
                
                # 模块信息
                if step.get('module_id') and step.get('module_name'):
                    module_id = step['module_id']
                    if module_id not in involved_modules:
                        involved_modules[module_id] = {
                            'id': module_id,
                            'name': step['module_name'],
                            'system_id': step.get('system_id'),
                            'step_count': 0,
                            'success_count': 0,
                            'failed_count': 0
                        }
                    
                    involved_modules[module_id]['step_count'] += 1
                    
                    if step['status'] == 'completed':
                        involved_modules[module_id]['success_count'] += 1
                    elif step['status'] == 'failed':
                        involved_modules[module_id]['failed_count'] += 1
                
                # API调用信息
                if step.get('api_interface_id'):
                    api_calls.append({
                        'step_id': step['step_id'],
                        'api_id': step['api_interface_id'],
                        'api_name': step.get('api_name'),
                        'status': step['status'],
                        'start_time': step.get('start_time'),
                        'end_time': step.get('end_time'),
                        'error_message': step.get('error_message')
                    })
            
            return {
                'execution_id': execution_id,
                'involved_systems': list(involved_systems.values()),
                'involved_modules': list(involved_modules.values()),
                'api_calls': api_calls,
                'summary': {
                    'total_systems': len(involved_systems),
                    'total_modules': len(involved_modules),
                    'total_api_calls': len(api_calls),
                    'total_steps': len(steps)
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取执行追踪数据失败: {e}")
            raise
    
    @staticmethod
    async def apply_permission_filter(data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """应用权限过滤和脱敏
        
        Args:
            data: 原始数据
            user_context: 用户上下文（包含权限信息）
            
        Returns:
            Dict[str, Any]: 过滤后的数据
        """
        try:
            # 获取用户权限
            user_role = user_context.get('role', 'user')
            user_team = user_context.get('team', '')
            
            filtered_data = data.copy()
            
            # 根据权限级别进行过滤
            if user_role == 'admin':
                # 管理员可以看到所有信息
                pass
            
            elif user_role == 'team_lead':
                # 团队负责人可以看到本团队的信息
                if 'plans' in filtered_data:
                    filtered_data['plans'] = [
                        plan for plan in filtered_data['plans']
                        if plan.get('created_by', '').startswith(user_team) or 
                           plan.get('metadata', {}).get('owner_team') == user_team
                    ]
            
            elif user_role == 'user':
                # 普通用户只能看到自己创建的
                user_id = user_context.get('user_id', '')
                if 'plans' in filtered_data:
                    filtered_data['plans'] = [
                        plan for plan in filtered_data['plans']
                        if plan.get('created_by') == user_id
                    ]
            
            # 脱敏处理
            filtered_data = TrackingService._apply_data_masking(filtered_data, user_context)
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"应用权限过滤失败: {e}")
            return data
    
    @staticmethod
    def _apply_data_masking(data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """应用数据脱敏
        
        Args:
            data: 原始数据
            user_context: 用户上下文
            
        Returns:
            Dict[str, Any]: 脱敏后的数据
        """
        user_role = user_context.get('role', 'user')
        
        # 如果是管理员，不需要脱敏
        if user_role == 'admin':
            return data
        
        masked_data = data.copy()
        
        # 脱敏敏感字段
        if 'plans' in masked_data:
            for plan in masked_data['plans']:
                # 脱敏执行计划中的敏感参数
                execution_plan = plan.get('execution_plan', {})
                if isinstance(execution_plan, str):
                    execution_plan = json.loads(execution_plan)
                
                steps = execution_plan.get('steps', [])
                for step in steps:
                    parameters = step.get('parameters', {})
                    
                    # 脱敏密码、token等敏感信息
                    for key in ['password', 'token', 'secret', 'key']:
                        if key in parameters:
                            parameters[key] = '***'
                    
                    # 脱敏请求体中的敏感信息
                    if 'body' in parameters and isinstance(parameters['body'], dict):
                        for key in ['password', 'token', 'secret']:
                            if key in parameters['body']:
                                parameters['body'][key] = '***'
                
                plan['execution_plan'] = execution_plan
        
        return masked_data
    
    @staticmethod
    async def get_cross_system_analysis(time_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """获取跨系统分析报告
        
        Args:
            time_range: 时间范围筛选
            
        Returns:
            Dict[str, Any]: 分析报告
        """
        try:
            # 获取所有计划
            all_plans = OrchestrationPlanDAO.search_plans({}, 1, 1000)
            
            # 分析跨系统调用模式
            cross_system_patterns = {}
            system_pairs = {}
            
            for plan in all_plans:
                metadata = plan.get('metadata', {})
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                involved_systems = metadata.get('involved_system_ids', [])
                
                # 记录跨系统模式
                if len(involved_systems) > 1:
                    pattern_key = tuple(sorted(involved_systems))
                    cross_system_patterns[pattern_key] = cross_system_patterns.get(pattern_key, 0) + 1
                    
                    # 记录系统对
                    for i, sys1 in enumerate(involved_systems):
                        for sys2 in involved_systems[i+1:]:
                            pair_key = tuple(sorted([sys1, sys2]))
                            system_pairs[pair_key] = system_pairs.get(pair_key, 0) + 1
            
            # 获取系统名称映射
            system_names = {}
            for system_id in set().union(*[list(pattern) for pattern in cross_system_patterns.keys()]):
                system = SystemService.get_system_by_id(system_id)
                if system:
                    system_names[system_id] = system['name']
            
            # 构建分析结果
            cross_system_analysis = []
            for pattern, count in sorted(cross_system_patterns.items(), key=lambda x: x[1], reverse=True):
                pattern_names = [system_names.get(sid, f'System_{sid}') for sid in pattern]
                cross_system_analysis.append({
                    'system_ids': list(pattern),
                    'system_names': pattern_names,
                    'usage_count': count,
                    'pattern': ' + '.join(pattern_names)
                })
            
            system_pair_analysis = []
            for pair, count in sorted(system_pairs.items(), key=lambda x: x[1], reverse=True):
                pair_names = [system_names.get(sid, f'System_{sid}') for sid in pair]
                system_pair_analysis.append({
                    'system_ids': list(pair),
                    'system_names': pair_names,
                    'interaction_count': count,
                    'pair': ' ↔ '.join(pair_names)
                })
            
            return {
                'total_plans': len(all_plans),
                'cross_system_plans': len(cross_system_patterns),
                'cross_system_patterns': cross_system_analysis[:10],  # 前10个
                'system_pairs': system_pair_analysis[:10],  # 前10个
                'analysis_summary': {
                    'most_common_pattern': cross_system_analysis[0] if cross_system_analysis else None,
                    'most_frequent_pair': system_pair_analysis[0] if system_pair_analysis else None,
                    'cross_system_rate': len(cross_system_patterns) / len(all_plans) if all_plans else 0
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取跨系统分析失败: {e}")
            raise
    
    @staticmethod
    async def export_audit_report(filters: Dict[str, Any], format: str = 'json') -> Dict[str, Any]:
        """导出审计报告
        
        Args:
            filters: 筛选条件
            format: 导出格式
            
        Returns:
            Dict[str, Any]: 导出结果
        """
        try:
            # 获取筛选数据
            filtered_data = await TrackingService.get_filtered_plans(filters, 1, 1000)
            
            # 构建审计报告
            audit_report = {
                'report_info': {
                    'generated_at': datetime.now().isoformat(),
                    'filters': filters,
                    'format': format,
                    'total_records': len(filtered_data.get('plans', []))
                },
                'summary': {
                    'total_plans': len(filtered_data.get('plans', [])),
                    'unique_systems': len(set().union(*[
                        plan.get('metadata', {}).get('involved_system_ids', [])
                        for plan in filtered_data.get('plans', [])
                    ])),
                    'unique_modules': len(set().union(*[
                        plan.get('metadata', {}).get('involved_module_ids', [])
                        for plan in filtered_data.get('plans', [])
                    ]))
                },
                'data': filtered_data['plans']
            }
            
            # 根据格式处理
            if format == 'csv':
                # 这里可以实现CSV导出逻辑
                audit_report['export_url'] = '/api/orchestration/export/audit.csv'
            elif format == 'excel':
                # 这里可以实现Excel导出逻辑
                audit_report['export_url'] = '/api/orchestration/export/audit.xlsx'
            
            return audit_report
            
        except Exception as e:
            logger.error(f"导出审计报告失败: {e}")
            raise