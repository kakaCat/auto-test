"""
工作流数据转换器

负责工作流数据的格式转换和标准化处理。
遵循静态工具类设计原则，所有方法都是静态方法。

职责：
- 工作流数据格式转换
- 业务数据标准化
- 统计信息计算
- 默认值处理
"""

from typing import Dict, Any, List
from datetime import datetime


class WorkflowConverter:
    """工作流数据转换器 - 静态工具类"""
    
    @staticmethod
    def to_workflow_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """转换为工作流统计数据"""
        return {
            'total_workflows': data.get('total_workflows', 0),
            'active_workflows': data.get('active_workflows', 0),
            'completed_workflows': data.get('completed_workflows', 0),
            'failed_workflows': data.get('failed_workflows', 0),
            'success_rate': WorkflowConverter._calculate_success_rate(data),
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }
    
    @staticmethod
    def to_workflows_list(workflows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """转换为工作流列表数据"""
        return [
            WorkflowConverter._transform_workflow_item(workflow)
            for workflow in workflows
        ]
    
    @staticmethod
    def to_default_workflow_stats() -> Dict[str, Any]:
        """默认工作流统计数据"""
        return {
            'total_workflows': 0,
            'active_workflows': 0,
            'completed_workflows': 0,
            'failed_workflows': 0,
            'success_rate': 0.0,
            'timestamp': datetime.now().isoformat()
        }
    
    # 私有辅助方法
    
    @staticmethod
    def _calculate_success_rate(data: Dict[str, Any]) -> float:
        """计算成功率"""
        total = data.get('total_workflows', 0)
        completed = data.get('completed_workflows', 0)
        
        if total == 0:
            return 0.0
        
        return round((completed / total) * 100, 2)
    
    @staticmethod
    def _transform_workflow_item(workflow: Dict[str, Any]) -> Dict[str, Any]:
        """转换单个工作流项目"""
        return {
            'id': workflow.get('id'),
            'name': workflow.get('name', ''),
            'description': workflow.get('description', ''),
            'status': workflow.get('status', 'unknown'),
            'created_at': workflow.get('created_at'),
            'updated_at': workflow.get('updated_at')
        }