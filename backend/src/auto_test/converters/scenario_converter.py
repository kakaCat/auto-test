"""
场景数据转换器

负责场景数据的格式转换和标准化处理。
遵循静态工具类设计原则，所有方法都是静态方法。

职责：
- 场景数据格式转换
- 业务数据标准化
- 统计信息计算
- 默认值处理
"""

from typing import Dict, Any, List
from datetime import datetime


class ScenarioConverter:
    """场景数据转换器 - 静态工具类"""
    
    @staticmethod
    def to_scenario_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为场景统计数据（对齐前端期望的键）"""
        # 对齐前端 keys: total, active, success, failed
        total = data.get('total', data.get('total_scenarios', 0))
        active = data.get('active', data.get('active_scenarios', 0))
        success = data.get('success', data.get('completed_scenarios', 0))
        failed = data.get('failed', data.get('failed_scenarios', 0))
        return {
            'total': total,
            'active': active,
            'success': success,
            'failed': failed,
            'success_rate': ScenarioConverter._calculate_success_rate({
                'total_scenarios': total,
                'completed_scenarios': success
            }),
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }
    
    @staticmethod
    def to_scenarios_list(scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换为场景列表数据"""
        return [
            ScenarioConverter._transform_scenario_item(scenario)
            for scenario in scenarios
        ]
    
    @staticmethod
    def to_default_scenario_stats() -> Dict[str, Any]:
        """默认场景统计数据（对齐前端期望的键）"""
        return {
            'total': 0,
            'active': 0,
            'success': 0,
            'failed': 0,
            'success_rate': 0.0,
            'timestamp': datetime.now().isoformat()
        }
    
    # 私有辅助方法
    
    @staticmethod
    def _calculate_success_rate(data: Dict[str, Any]) -> float:
        """计算成功率"""
        total = data.get('total_scenarios', 0)
        completed = data.get('completed_scenarios', 0)
        
        if total == 0:
            return 0.0
        
        return round((completed / total) * 100, 2)
    
    @staticmethod
    def _transform_scenario_item(scenario: Dict[str, Any]) -> Dict[str, Any]:
        """转换单个场景项目"""
        return {
            'id': scenario.get('id'),
            'name': scenario.get('name', ''),
            'description': scenario.get('description', ''),
            'status': scenario.get('status', 'unknown'),
            'scenario_type': scenario.get('scenario_type', 'normal'),
            'apiCount': scenario.get('apiCount', scenario.get('api_count', 0)),
            'executionCount': scenario.get('executionCount', scenario.get('execution_count', 0)),
            'successRate': scenario.get('successRate', scenario.get('success_rate', 0)),
            'lastExecutionTime': scenario.get('lastExecutionTime', scenario.get('last_execution_time')),
            'version': scenario.get('version', '1.0.0'),
            'tags': scenario.get('tags', []),
            'is_parameters_saved': scenario.get('is_parameters_saved', False),
            'created_at': scenario.get('created_at'),
            'updated_at': scenario.get('updated_at')
        }