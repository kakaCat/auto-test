"""
统计数据转换器

负责统计数据的格式转换和标准化处理。
遵循静态工具类设计原则，所有方法都是静态方法。

职责：
- 数据格式转换
- 业务数据标准化
- 统计信息计算
- 默认值处理
"""

from typing import Dict, Any, List
from datetime import datetime


class StatsConverter:
    """统计数据转换器 - 静态工具类"""
    
    @staticmethod
    def to_comprehensive_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为综合统计数据"""
        systems = data.get('systems', [])
        modules = data.get('modules', [])
        
        return {
            'api_stats': {
                'total_apis': len(modules),
                'enabled_apis': len([m for m in modules if m.get('status') == 'active']),
                'disabled_apis': len([m for m in modules if m.get('status') != 'active']),
                'apis_by_method': StatsConverter._count_by_method(modules),
                'apis_by_system': StatsConverter._count_by_system(modules)
            },
            'system_stats': {
                'total_systems': len(systems),
                'active_systems': len([s for s in systems if s.get('status') == 'active']),
                'systems_by_status': StatsConverter._count_by_status(systems)
            },
            'workflow_stats': {
                'total_workflows': 0,
                'active_workflows': 0,
                'completed_workflows': 0
            },
            'scenario_stats': {
                'total_scenarios': 0,
                'active_scenarios': 0,
                'completed_scenarios': 0
            },
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }
    
    @staticmethod
    def to_systems_stats(systems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """转换为系统统计数据"""
        return {
            'total': len(systems),
            'by_status': StatsConverter._count_by_status(systems),
            'by_category': StatsConverter._count_by_category(systems),
            'recent_count': len([s for s in systems if StatsConverter._is_recent(s)])
        }
    
    @staticmethod
    def to_modules_stats(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """转换为模块统计数据"""
        return {
            'total': len(modules),
            'by_status': StatsConverter._count_by_status(modules),
            'by_system': StatsConverter._count_by_system(modules),
            'by_method': StatsConverter._count_by_method(modules),
            'recent_count': len([m for m in modules if StatsConverter._is_recent(m)])
        }
    
    @staticmethod
    def to_workflows_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为工作流统计数据"""
        return {
            'total_workflows': 0,
            'active_workflows': 0,
            'completed_workflows': 0,
            'failed_workflows': 0,
            'success_rate': 0.0
        }
    
    @staticmethod
    def to_scenarios_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为场景统计数据"""
        return {
            'total_scenarios': 0,
            'active_scenarios': 0,
            'completed_scenarios': 0,
            'failed_scenarios': 0,
            'success_rate': 0.0
        }
    
    @staticmethod
    def to_default_stats() -> Dict[str, Any]:
        """默认综合统计数据"""
        return {
            'api_stats': {
                'total_apis': 0,
                'enabled_apis': 0,
                'disabled_apis': 0,
                'apis_by_method': {},
                'apis_by_system': {}
            },
            'system_stats': {
                'total_systems': 0,
                'active_systems': 0,
                'systems_by_status': {}
            },
            'workflow_stats': {
                'total_workflows': 0,
                'active_workflows': 0,
                'completed_workflows': 0
            },
            'scenario_stats': {
                'total_scenarios': 0,
                'active_scenarios': 0,
                'completed_scenarios': 0
            },
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def to_default_systems_stats() -> Dict[str, Any]:
        """默认系统统计数据"""
        return {
            'total': 0,
            'by_status': {},
            'by_category': {},
            'recent_count': 0
        }
    
    @staticmethod
    def to_default_modules_stats() -> Dict[str, Any]:
        """默认模块统计数据"""
        return {
            'total': 0,
            'by_status': {},
            'by_system': {},
            'by_method': {},
            'recent_count': 0
        }
    
    @staticmethod
    def to_default_workflows_stats() -> Dict[str, Any]:
        """默认工作流统计数据"""
        return {
            'total_workflows': 0,
            'active_workflows': 0,
            'completed_workflows': 0,
            'failed_workflows': 0,
            'success_rate': 0.0
        }
    
    @staticmethod
    def to_default_scenarios_stats() -> Dict[str, Any]:
        """默认场景统计数据"""
        return {
            'total_scenarios': 0,
            'active_scenarios': 0,
            'completed_scenarios': 0,
            'failed_scenarios': 0,
            'success_rate': 0.0
        }
    
    # 私有辅助方法
    
    @staticmethod
    def _count_by_status(items: List[Dict[str, Any]]) -> Dict[str, int]:
        """按状态统计"""
        status_count = {}
        for item in items:
            status = item.get('status', 'unknown')
            status_count[status] = status_count.get(status, 0) + 1
        return status_count
    
    @staticmethod
    def _count_by_system(modules: List[Dict[str, Any]]) -> Dict[str, int]:
        """按系统统计模块"""
        system_count = {}
        for module in modules:
            system_name = module.get('system_name', 'unknown')
            system_count[system_name] = system_count.get(system_name, 0) + 1
        return system_count
    
    @staticmethod
    def _count_by_method(modules: List[Dict[str, Any]]) -> Dict[str, int]:
        """按方法统计模块"""
        method_count = {}
        for module in modules:
            method = module.get('method', 'unknown')
            method_count[method] = method_count.get(method, 0) + 1
        return method_count
    
    @staticmethod
    def _count_by_category(systems: List[Dict[str, Any]]) -> Dict[str, int]:
        """按分类统计系统"""
        category_count = {}
        for system in systems:
            category = system.get('category', 'unknown')
            category_count[category] = category_count.get(category, 0) + 1
        return category_count
    
    @staticmethod
    def _is_recent(item: Dict[str, Any]) -> bool:
        """判断是否为最近创建的项目"""
        # 简单实现，可根据需要扩展
        return True