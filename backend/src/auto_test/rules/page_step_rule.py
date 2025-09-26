"""
页面分步保存业务规则验证器
Page Step Save Business Rule Validator

负责业务规则验证：
- 快速失败验证
- 跨层复用规则
- 统一验证逻辑
- 静态方法实现
"""

from typing import Dict, Any, List
from ..models.page_step import (
    PageBasicInfo, PageLayout, PageApiConfig, PageInteraction, StepStatus
)


class PageStepRule:
    """页面分步保存业务规则"""

    @staticmethod
    def validate_page_id(page_id: int) -> None:
        """验证页面ID"""
        if not page_id or page_id <= 0:
            raise ValueError("页面ID必须是正整数")

    @staticmethod
    def validate_step_name(step: str) -> None:
        """验证步骤名称"""
        valid_steps = ['basic', 'layout', 'api', 'interaction']
        if step not in valid_steps:
            raise ValueError(f"无效的步骤名称: {step}，有效值: {valid_steps}")

    @staticmethod
    def validate_basic_info(basic_info: PageBasicInfo) -> None:
        """验证页面基本信息"""
        if not basic_info:
            raise ValueError("页面基本信息不能为空")
        
        if not basic_info.name or not basic_info.name.strip():
            raise ValueError("页面名称不能为空")
        
        if len(basic_info.name) > 100:
            raise ValueError("页面名称长度不能超过100个字符")
        
        if basic_info.system_id <= 0:
            raise ValueError("系统ID必须是正整数")
        
        if basic_info.route_path and len(basic_info.route_path) > 200:
            raise ValueError("路由路径长度不能超过200个字符")
        
        # 验证页面类型
        valid_page_types = ['page', 'modal', 'drawer', 'popup']
        if basic_info.page_type not in valid_page_types:
            raise ValueError(f"无效的页面类型: {basic_info.page_type}，有效值: {valid_page_types}")

    @staticmethod
    def validate_layout(layout: PageLayout) -> None:
        """验证页面布局"""
        if not layout:
            raise ValueError("页面布局不能为空")
        
        # 验证布局类型
        valid_layout_types = ['grid', 'flex', 'absolute', 'flow']
        if layout.layout_type not in valid_layout_types:
            raise ValueError(f"无效的布局类型: {layout.layout_type}，有效值: {valid_layout_types}")
        
        # 验证组件配置
        if layout.components:
            PageStepRule._validate_components(layout.components)
        
        # 验证网格配置
        if layout.grid_config:
            PageStepRule._validate_grid_config(layout.grid_config)

    @staticmethod
    def validate_api_config(api_config: PageApiConfig) -> None:
        """验证API配置"""
        if not api_config:
            raise ValueError("API配置不能为空")
        
        if api_config.system_id <= 0:
            raise ValueError("系统ID必须是正整数")
        
        if api_config.module_id <= 0:
            raise ValueError("模块ID必须是正整数")
        
        # 验证API配置项
        if api_config.apis:
            PageStepRule._validate_api_config_items(api_config.apis)

    @staticmethod
    def validate_interaction(interaction: PageInteraction) -> None:
        """验证页面交互"""
        if not interaction:
            raise ValueError("页面交互配置不能为空")
        
        # 验证交互事件
        if interaction.events:
            PageStepRule._validate_interaction_events(interaction.events)
        
        # 验证工作流配置
        if interaction.workflows:
            PageStepRule._validate_workflow_configs(interaction.workflows)

    @staticmethod
    def validate_all_steps_completed(progress: Dict[str, Any]) -> None:
        """验证所有步骤是否完成"""
        if not progress:
            raise ValueError("配置进度不存在")
        
        step_status = progress.get('step_status', {})
        required_steps = ['basic', 'layout', 'api', 'interaction']
        
        for step in required_steps:
            if step_status.get(step) != 'completed':
                raise ValueError(f"步骤 {step} 尚未完成，无法完成页面配置")

    @staticmethod
    def validate_step_status(status: StepStatus) -> None:
        """验证步骤状态"""
        valid_statuses = ['pending', 'draft', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"无效的步骤状态: {status}，有效值: {valid_statuses}")

    @staticmethod
    def _validate_components(components: List[Any]) -> None:
        """验证组件配置"""
        for i, component in enumerate(components):
            if not hasattr(component, 'id') or not component.id:
                raise ValueError(f"组件 {i} 缺少ID")
            
            if not hasattr(component, 'type') or not component.type:
                raise ValueError(f"组件 {i} 缺少类型")
            
            # 验证组件类型
            valid_component_types = [
                'input', 'button', 'table', 'form', 'card', 'list',
                'chart', 'image', 'text', 'divider', 'container'
            ]
            if component.type not in valid_component_types:
                raise ValueError(f"组件 {i} 类型无效: {component.type}")

    @staticmethod
    def _validate_grid_config(grid_config: Any) -> None:
        """验证网格配置"""
        if hasattr(grid_config, 'columns'):
            if grid_config.columns <= 0 or grid_config.columns > 24:
                raise ValueError("网格列数必须在1-24之间")
        
        if hasattr(grid_config, 'gap'):
            if grid_config.gap < 0 or grid_config.gap > 100:
                raise ValueError("网格间距必须在0-100之间")

    @staticmethod
    def _validate_api_config_items(apis: List[Any]) -> None:
        """验证API配置项"""
        for i, api in enumerate(apis):
            if not hasattr(api, 'api_id') or api.api_id <= 0:
                raise ValueError(f"API配置 {i} 的API ID无效")
            
            if hasattr(api, 'execution_type'):
                valid_execution_types = ['serial', 'parallel', 'conditional']
                if api.execution_type not in valid_execution_types:
                    raise ValueError(f"API配置 {i} 的执行类型无效: {api.execution_type}")
            
            if hasattr(api, 'order') and api.order < 0:
                raise ValueError(f"API配置 {i} 的执行顺序不能为负数")

    @staticmethod
    def _validate_interaction_events(events: List[Any]) -> None:
        """验证交互事件"""
        for i, event in enumerate(events):
            if not hasattr(event, 'id') or not event.id:
                raise ValueError(f"交互事件 {i} 缺少ID")
            
            if not hasattr(event, 'trigger') or not event.trigger:
                raise ValueError(f"交互事件 {i} 缺少触发器配置")
            
            if hasattr(event, 'actions') and not event.actions:
                raise ValueError(f"交互事件 {i} 缺少执行动作")

    @staticmethod
    def _validate_workflow_configs(workflows: List[Any]) -> None:
        """验证工作流配置"""
        for i, workflow in enumerate(workflows):
            if not hasattr(workflow, 'id') or not workflow.id:
                raise ValueError(f"工作流 {i} 缺少ID")
            
            if not hasattr(workflow, 'name') or not workflow.name:
                raise ValueError(f"工作流 {i} 缺少名称")
            
            if hasattr(workflow, 'steps') and not workflow.steps:
                raise ValueError(f"工作流 {i} 缺少步骤配置")

    @staticmethod
    def validate_step_order(current_step: int, target_step: int) -> None:
        """验证步骤顺序"""
        if target_step < 0 or target_step > 3:
            raise ValueError("步骤索引必须在0-3之间")
        
        # 允许向前跳转，但不能跳过太多步骤
        if target_step > current_step + 1:
            raise ValueError("不能跳过步骤，请按顺序完成配置")

    @staticmethod
    def validate_permissions(permissions: List[str]) -> None:
        """验证权限设置"""
        if not permissions:
            return
        
        valid_permissions = [
            'read', 'write', 'delete', 'admin',
            'page:view', 'page:edit', 'page:delete',
            'api:execute', 'data:export', 'data:import'
        ]
        
        for permission in permissions:
            if permission not in valid_permissions:
                raise ValueError(f"无效的权限: {permission}")

    @staticmethod
    def validate_route_path(route_path: str) -> None:
        """验证路由路径"""
        if not route_path:
            return
        
        # 路由路径必须以/开头
        if not route_path.startswith('/'):
            raise ValueError("路由路径必须以/开头")
        
        # 不能包含特殊字符
        invalid_chars = ['<', '>', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in route_path:
                raise ValueError(f"路由路径不能包含字符: {char}")

    @staticmethod
    def validate_component_hierarchy(components: List[Any]) -> None:
        """验证组件层级关系"""
        component_ids = set()
        
        for component in components:
            if hasattr(component, 'id'):
                if component.id in component_ids:
                    raise ValueError(f"组件ID重复: {component.id}")
                component_ids.add(component.id)
            
            # 验证子组件
            if hasattr(component, 'children') and component.children:
                PageStepRule._validate_child_components(component.children, component_ids)