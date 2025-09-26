"""
页面分步保存权限包装器
Page Step Save Permission Wrapper

负责权限控制和数据包装：
- 权限控制
- 敏感信息过滤
- 缓存友好处理
- 静态方法实现
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ..models.page_step import (
    PageProgress, PageStepSaveResponse, PageCompleteResponse
)


class PageStepWrapper:
    """页面分步保存权限包装器"""

    @staticmethod
    def wrap_step_save_response(page_id: int, step: str, status: str, saved_at: datetime) -> PageStepSaveResponse:
        """包装步骤保存响应"""
        return PageStepSaveResponse(
            page_id=page_id,
            step=step,
            status=status,
            saved_at=saved_at
        )

    @staticmethod
    def wrap_progress(progress: PageProgress) -> PageProgress:
        """包装配置进度"""
        # 这里可以根据用户权限过滤敏感信息
        return progress

    @staticmethod
    def wrap_complete_response(page_id: int, completed_at: datetime, status: str) -> PageCompleteResponse:
        """包装完成配置响应"""
        return PageCompleteResponse(
            page_id=page_id,
            completed_at=completed_at,
            status=status
        )

    @staticmethod
    def wrap_all_step_data(all_data: Dict[str, Any]) -> Dict[str, Any]:
        """包装所有步骤数据"""
        # 移除敏感信息，保持缓存友好
        wrapped_data = {}
        
        for step, data in all_data.items():
            wrapped_data[step] = PageStepWrapper._filter_sensitive_data(step, data)
        
        return wrapped_data

    @staticmethod
    def wrap_step_data_with_permissions(step: str, data: Dict[str, Any], user_permissions: Optional[list] = None) -> Dict[str, Any]:
        """根据用户权限包装步骤数据"""
        if not user_permissions:
            user_permissions = []
        
        # 根据权限过滤数据
        if step == 'basic':
            return PageStepWrapper._wrap_basic_info_data(data, user_permissions)
        elif step == 'layout':
            return PageStepWrapper._wrap_layout_data(data, user_permissions)
        elif step == 'api':
            return PageStepWrapper._wrap_api_config_data(data, user_permissions)
        elif step == 'interaction':
            return PageStepWrapper._wrap_interaction_data(data, user_permissions)
        
        return data

    @staticmethod
    def wrap_progress_with_permissions(progress: Dict[str, Any], user_permissions: Optional[list] = None) -> Dict[str, Any]:
        """根据用户权限包装进度数据"""
        if not user_permissions:
            user_permissions = []
        
        wrapped_progress = progress.copy()
        
        # 如果用户没有管理权限，隐藏某些敏感信息
        if 'admin' not in user_permissions:
            # 移除详细的步骤状态信息
            if 'step_status' in wrapped_progress:
                wrapped_progress['step_status'] = PageStepWrapper._simplify_step_status(
                    wrapped_progress['step_status']
                )
        
        return wrapped_progress

    @staticmethod
    def wrap_statistics_with_permissions(stats: Dict[str, Any], user_permissions: Optional[list] = None) -> Dict[str, Any]:
        """根据用户权限包装统计数据"""
        if not user_permissions:
            user_permissions = []
        
        wrapped_stats = stats.copy()
        
        # 如果用户没有统计权限，限制数据访问
        if 'stats:view' not in user_permissions and 'admin' not in user_permissions:
            # 只返回基本统计信息
            wrapped_stats = {
                'total_pages': stats.get('total_pages', 0),
                'completed_pages': stats.get('completed_pages', 0)
            }
        
        return wrapped_stats

    @staticmethod
    def _filter_sensitive_data(step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤敏感数据"""
        if not data:
            return data
        
        filtered_data = data.copy()
        
        # 移除时间戳等动态数据，保持缓存友好
        dynamic_fields = ['created_at', 'updated_at', 'last_modified']
        for field in dynamic_fields:
            filtered_data.pop(field, None)
        
        # 根据步骤类型过滤特定敏感信息
        if step == 'api':
            # 移除API密钥等敏感信息
            if 'apis' in filtered_data:
                for api in filtered_data['apis']:
                    if isinstance(api, dict):
                        api.pop('api_key', None)
                        api.pop('secret', None)
                        api.pop('token', None)
        
        elif step == 'interaction':
            # 移除敏感的交互配置
            if 'events' in filtered_data:
                for event in filtered_data['events']:
                    if isinstance(event, dict) and 'actions' in event:
                        for action in event['actions']:
                            if isinstance(action, dict):
                                action.pop('credentials', None)
                                action.pop('private_key', None)
        
        return filtered_data

    @staticmethod
    def _wrap_basic_info_data(data: Dict[str, Any], permissions: list) -> Dict[str, Any]:
        """包装基本信息数据"""
        wrapped_data = data.copy()
        
        # 如果没有编辑权限，移除某些字段
        if 'page:edit' not in permissions and 'admin' not in permissions:
            sensitive_fields = ['permissions', 'system_id', 'module_id']
            for field in sensitive_fields:
                wrapped_data.pop(field, None)
        
        return wrapped_data

    @staticmethod
    def _wrap_layout_data(data: Dict[str, Any], permissions: list) -> Dict[str, Any]:
        """包装布局数据"""
        wrapped_data = data.copy()
        
        # 如果没有设计权限，简化组件信息
        if 'design:edit' not in permissions and 'admin' not in permissions:
            if 'components' in wrapped_data:
                simplified_components = []
                for component in wrapped_data['components']:
                    if isinstance(component, dict):
                        simplified_components.append({
                            'id': component.get('id'),
                            'type': component.get('type'),
                            'position': component.get('position')
                        })
                wrapped_data['components'] = simplified_components
        
        return wrapped_data

    @staticmethod
    def _wrap_api_config_data(data: Dict[str, Any], permissions: list) -> Dict[str, Any]:
        """包装API配置数据"""
        wrapped_data = data.copy()
        
        # 如果没有API权限，移除敏感配置
        if 'api:config' not in permissions and 'admin' not in permissions:
            if 'apis' in wrapped_data:
                public_apis = []
                for api in wrapped_data['apis']:
                    if isinstance(api, dict):
                        public_apis.append({
                            'api_id': api.get('api_id'),
                            'execution_type': api.get('execution_type'),
                            'order': api.get('order'),
                            'enabled': api.get('enabled')
                        })
                wrapped_data['apis'] = public_apis
        
        return wrapped_data

    @staticmethod
    def _wrap_interaction_data(data: Dict[str, Any], permissions: list) -> Dict[str, Any]:
        """包装交互数据"""
        wrapped_data = data.copy()
        
        # 如果没有交互权限，简化事件信息
        if 'interaction:edit' not in permissions and 'admin' not in permissions:
            if 'events' in wrapped_data:
                public_events = []
                for event in wrapped_data['events']:
                    if isinstance(event, dict):
                        public_events.append({
                            'id': event.get('id'),
                            'enabled': event.get('enabled')
                        })
                wrapped_data['events'] = public_events
            
            if 'workflows' in wrapped_data:
                public_workflows = []
                for workflow in wrapped_data['workflows']:
                    if isinstance(workflow, dict):
                        public_workflows.append({
                            'id': workflow.get('id'),
                            'name': workflow.get('name'),
                            'enabled': workflow.get('enabled')
                        })
                wrapped_data['workflows'] = public_workflows
        
        return wrapped_data

    @staticmethod
    def _simplify_step_status(step_status: Dict[str, str]) -> Dict[str, str]:
        """简化步骤状态"""
        simplified = {}
        for step, status in step_status.items():
            # 只显示是否完成，不显示详细状态
            simplified[step] = 'completed' if status == 'completed' else 'pending'
        return simplified

    @staticmethod
    def add_cache_headers(data: Dict[str, Any]) -> Dict[str, Any]:
        """添加缓存友好的头信息"""
        if not isinstance(data, dict):
            return data
        
        # 添加缓存标识
        data['_cache_friendly'] = True
        data['_cache_version'] = '1.0'
        
        return data

    @staticmethod
    def remove_dynamic_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """移除动态字段，使数据更适合缓存"""
        if not isinstance(data, dict):
            return data
        
        cleaned_data = data.copy()
        
        # 移除时间相关的动态字段
        dynamic_fields = [
            'last_saved_at', 'created_at', 'updated_at', 
            'last_modified', 'timestamp', 'current_time'
        ]
        
        for field in dynamic_fields:
            cleaned_data.pop(field, None)
        
        return cleaned_data