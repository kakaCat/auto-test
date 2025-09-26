"""
页面分步保存数据转换器
Page Step Save Data Converter

负责数据转换和格式标准化：
- 业务数据转换
- 格式标准化
- 调用Rule验证
- 静态方法实现
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ..models.page_step import (
    PageBasicInfo, PageLayout, PageApiConfig, PageInteraction, PageProgress,
    PageStepSaveResponse, PageCompleteResponse
)
from ..rules.page_step_rule import PageStepRule


class PageStepConverter:
    """页面分步保存数据转换器"""

    @staticmethod
    def basic_info_to_data(basic_info: PageBasicInfo) -> Dict[str, Any]:
        """将基本信息模型转换为数据字典"""
        PageStepRule.validate_basic_info(basic_info)
        
        return {
            'name': basic_info.name,
            'description': basic_info.description,
            'route_path': basic_info.route_path,
            'page_type': basic_info.page_type,
            'system_id': basic_info.system_id,
            'module_id': basic_info.module_id,
            'enabled': basic_info.enabled,
            'icon': basic_info.icon,
            'permissions': basic_info.permissions
        }

    @staticmethod
    def layout_to_data(layout: PageLayout) -> Dict[str, Any]:
        """将布局模型转换为数据字典"""
        PageStepRule.validate_layout(layout)
        
        return {
            'components': [component.dict() for component in layout.components],
            'layout_type': layout.layout_type,
            'responsive': layout.responsive,
            'grid_config': layout.grid_config.dict() if layout.grid_config else None,
            'theme': layout.theme.dict() if layout.theme else None
        }

    @staticmethod
    def api_config_to_data(api_config: PageApiConfig) -> Dict[str, Any]:
        """将API配置模型转换为数据字典"""
        PageStepRule.validate_api_config(api_config)
        
        return {
            'system_id': api_config.system_id,
            'module_id': api_config.module_id,
            'apis': [api.dict() for api in api_config.apis]
        }

    @staticmethod
    def interaction_to_data(interaction: PageInteraction) -> Dict[str, Any]:
        """将交互模型转换为数据字典"""
        PageStepRule.validate_interaction(interaction)
        
        return {
            'events': [event.dict() for event in interaction.events],
            'workflows': [workflow.dict() for workflow in interaction.workflows]
        }

    @staticmethod
    def data_to_basic_info(data: Dict[str, Any]) -> PageBasicInfo:
        """将数据字典转换为基本信息模型"""
        return PageBasicInfo(
            name=data.get('name', ''),
            description=data.get('description'),
            route_path=data.get('route_path'),
            page_type=data.get('page_type', 'page'),
            system_id=data.get('system_id', 0),
            module_id=data.get('module_id'),
            enabled=data.get('enabled', True),
            icon=data.get('icon'),
            permissions=data.get('permissions')
        )

    @staticmethod
    def data_to_layout(data: Dict[str, Any]) -> PageLayout:
        """将数据字典转换为布局模型"""
        from ..models.page_step import ComponentConfig, GridConfig, ThemeConfig
        
        components = []
        for comp_data in data.get('components', []):
            components.append(ComponentConfig(**comp_data))
        
        grid_config = None
        if data.get('grid_config'):
            grid_config = GridConfig(**data['grid_config'])
        
        theme = None
        if data.get('theme'):
            theme = ThemeConfig(**data['theme'])
        
        return PageLayout(
            components=components,
            layout_type=data.get('layout_type', 'grid'),
            responsive=data.get('responsive', True),
            grid_config=grid_config,
            theme=theme
        )

    @staticmethod
    def data_to_api_config(data: Dict[str, Any]) -> PageApiConfig:
        """将数据字典转换为API配置模型"""
        from ..models.page_step import ApiConfigItem
        
        apis = []
        for api_data in data.get('apis', []):
            apis.append(ApiConfigItem(**api_data))
        
        return PageApiConfig(
            system_id=data.get('system_id', 0),
            module_id=data.get('module_id', 0),
            apis=apis
        )

    @staticmethod
    def data_to_interaction(data: Dict[str, Any]) -> PageInteraction:
        """将数据字典转换为交互模型"""
        from ..models.page_step import InteractionEvent, WorkflowConfig
        
        events = []
        for event_data in data.get('events', []):
            events.append(InteractionEvent(**event_data))
        
        workflows = []
        for workflow_data in data.get('workflows', []):
            workflows.append(WorkflowConfig(**workflow_data))
        
        return PageInteraction(
            events=events,
            workflows=workflows
        )

    @staticmethod
    def data_to_progress(progress_data: Dict[str, Any]) -> PageProgress:
        """将数据字典转换为进度模型"""
        return PageProgress(
            page_id=progress_data.get('page_id', 0),
            current_step=progress_data.get('current_step', 0),
            completed_steps=progress_data.get('completed_steps', []),
            step_status=progress_data.get('step_status', {
                'basic': 'pending',
                'layout': 'pending',
                'api': 'pending',
                'interaction': 'pending'
            }),
            last_saved_at=progress_data.get('last_saved_at', datetime.now()),
            is_completed=progress_data.get('is_completed', False)
        )

    @staticmethod
    def data_to_step_model(step: str, data: Dict[str, Any]) -> Any:
        """根据步骤类型将数据转换为对应的模型"""
        step_data = data.get('data', {})
        
        if step == 'basic':
            return PageStepConverter.data_to_basic_info(step_data)
        elif step == 'layout':
            return PageStepConverter.data_to_layout(step_data)
        elif step == 'api':
            return PageStepConverter.data_to_api_config(step_data)
        elif step == 'interaction':
            return PageStepConverter.data_to_interaction(step_data)
        else:
            raise ValueError(f"未知的步骤类型: {step}")

    @staticmethod
    def progress_to_response(progress: PageProgress) -> Dict[str, Any]:
        """将进度模型转换为响应数据"""
        return {
            'page_id': progress.page_id,
            'current_step': progress.current_step,
            'completed_steps': progress.completed_steps,
            'step_status': progress.step_status,
            'last_saved_at': progress.last_saved_at.isoformat(),
            'is_completed': progress.is_completed
        }

    @staticmethod
    def step_save_to_response(page_id: int, step: str, status: str, saved_at: datetime) -> PageStepSaveResponse:
        """创建步骤保存响应"""
        return PageStepSaveResponse(
            page_id=page_id,
            step=step,
            status=status,
            saved_at=saved_at
        )

    @staticmethod
    def complete_to_response(page_id: int, completed_at: datetime, status: str) -> PageCompleteResponse:
        """创建完成配置响应"""
        return PageCompleteResponse(
            page_id=page_id,
            completed_at=completed_at,
            status=status
        )

    @staticmethod
    def all_step_data_to_response(all_data: Dict[str, Any]) -> Dict[str, Any]:
        """将所有步骤数据转换为响应格式"""
        response = {}
        
        for step, step_data in all_data.items():
            if step_data:
                try:
                    model = PageStepConverter.data_to_step_model(step, step_data)
                    response[step] = model.dict() if hasattr(model, 'dict') else model
                except Exception as e:
                    # 如果转换失败，返回原始数据
                    response[step] = step_data.get('data', {})
        
        return response

    @staticmethod
    def statistics_to_response(stats: Dict[str, Any]) -> Dict[str, Any]:
        """将统计数据转换为响应格式"""
        return {
            'total_pages': stats.get('total_pages', 0),
            'completed_pages': stats.get('completed_pages', 0),
            'incomplete_pages': stats.get('incomplete_pages', 0),
            'completion_rate': (
                stats.get('completed_pages', 0) / stats.get('total_pages', 1) * 100
                if stats.get('total_pages', 0) > 0 else 0
            ),
            'step_completion_rate': stats.get('step_completion_rate', {})
        }