"""
页面分步保存服务层
Page Step Save Service Layer

遵循业务层编码规范：
- 数据收集与组装
- 业务流程协调
- 基础设施调用封装
- 统一异常处理
"""

from typing import Optional, Dict, Any
from datetime import datetime
from ..models.page_step import (
    PageBasicInfo, PageLayout, PageApiConfig, PageInteraction, PageProgress,
    PageStepSaveResponse, PageCompleteResponse, StepStatus
)
from .page_step_data_service import PageStepDataService
from ..converters.page_step_converter import PageStepConverter
from ..rules.page_step_rule import PageStepRule
from ..wrappers.page_step_wrapper import PageStepWrapper


class PageStepService:
    """页面分步保存服务"""

    @staticmethod
    def save_basic_info(page_id: int, basic_info: PageBasicInfo) -> PageStepSaveResponse:
        """保存页面基本信息"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        PageStepRule.validate_basic_info(basic_info)
        
        # 数据转换
        basic_data = PageStepConverter.basic_info_to_data(basic_info)
        
        # 保存数据
        saved_data = PageStepDataService.save_step_data(page_id, 'basic', basic_data)
        
        # 更新进度
        progress = PageStepDataService.update_progress(page_id, 'basic', ['basic'], {'basic': 'completed'})
        
        # 包装响应
        return PageStepWrapper.wrap_step_save_response(page_id, 'basic', 'completed', datetime.now())

    @staticmethod
    def save_layout(page_id: int, layout: PageLayout) -> PageStepSaveResponse:
        """保存页面布局设计"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        PageStepRule.validate_layout(layout)
        
        # 数据转换
        layout_data = PageStepConverter.layout_to_data(layout)
        
        # 保存数据
        saved_data = PageStepDataService.save_step_data(page_id, 'layout', layout_data)
        
        # 更新进度
        progress = PageStepDataService.update_progress(page_id, 'layout', ['basic', 'layout'], {'basic': 'completed', 'layout': 'completed'})
        
        # 包装响应
        return PageStepWrapper.wrap_step_save_response(page_id, 'layout', 'completed', datetime.now())

    @staticmethod
    def save_api_config(page_id: int, api_config: PageApiConfig) -> PageStepSaveResponse:
        """保存页面API配置"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        PageStepRule.validate_api_config(api_config)
        
        # 数据转换
        api_data = PageStepConverter.api_config_to_data(api_config)
        
        # 保存数据
        saved_data = PageStepDataService.save_step_data(page_id, 'api', api_data)
        
        # 更新进度
        progress = PageStepDataService.update_progress(page_id, 'api', ['basic', 'layout', 'api'], {'basic': 'completed', 'layout': 'completed', 'api': 'completed'})
        
        # 包装响应
        return PageStepWrapper.wrap_step_save_response(page_id, 'api', 'completed', datetime.now())

    @staticmethod
    def save_interaction(page_id: int, interaction: PageInteraction) -> PageStepSaveResponse:
        """保存页面交互设置"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        PageStepRule.validate_interaction(interaction)
        
        # 数据转换
        interaction_data = PageStepConverter.interaction_to_data(interaction)
        
        # 保存数据
        saved_data = PageStepDataService.save_step_data(page_id, 'interaction', interaction_data)
        
        # 更新进度
        progress = PageStepDataService.update_progress(page_id, 'interaction', ['basic', 'layout', 'api', 'interaction'], {'basic': 'completed', 'layout': 'completed', 'api': 'completed', 'interaction': 'completed'})
        
        # 包装响应
        return PageStepWrapper.wrap_step_save_response(page_id, 'interaction', 'completed', datetime.now())

    @staticmethod
    def get_progress(page_id: int) -> PageProgress:
        """获取页面配置进度"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        
        # 获取进度数据
        progress_data = PageStepDataService.get_progress(page_id)
        
        # 如果没有进度数据，创建默认进度
        if not progress_data:
            progress_data = {
                'page_id': page_id,
                'current_step': 0,
                'completed_steps': [],
                'step_status': {
                    'basic': 'pending',
                    'layout': 'pending',
                    'api': 'pending',
                    'interaction': 'pending'
                },
                'last_saved_at': datetime.now(),
                'is_completed': False
            }
        
        # 数据转换
        progress = PageStepConverter.data_to_progress(progress_data)
        
        # 包装响应
        return PageStepWrapper.wrap_progress(progress)

    @staticmethod
    def complete_page_config(page_id: int) -> PageCompleteResponse:
        """完成页面配置"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        
        # 验证所有步骤是否完成
        progress = PageStepDataService.get_progress(page_id)
        PageStepRule.validate_all_steps_completed(progress)
        
        # 标记页面配置完成
        completed_data = PageStepDataService.complete_page_config(page_id)
        
        # 包装响应
        return PageStepWrapper.wrap_complete_response(page_id, datetime.now(), 'active')

    @staticmethod
    def get_step_data(page_id: int, step: str) -> Optional[Dict[str, Any]]:
        """获取指定步骤的数据"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        PageStepRule.validate_step_name(step)
        
        # 获取步骤数据
        step_data = PageStepDataService.get_step_data(page_id, step)
        
        # 数据转换
        if step_data:
            return PageStepConverter.data_to_step_model(step, step_data)
        
        return None

    @staticmethod
    def reset_step(page_id: int, step: str) -> bool:
        """重置指定步骤"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        PageStepRule.validate_step_name(step)
        
        # 重置步骤数据
        success = PageStepDataService.reset_step_data(page_id, step)
        
        if success:
            # 更新进度状态
            PageStepDataService.update_progress(page_id, step, 'pending')
        
        return success

    @staticmethod
    def get_all_step_data(page_id: int) -> Dict[str, Any]:
        """获取所有步骤的数据"""
        # 数据验证
        PageStepRule.validate_page_id(page_id)
        
        # 获取所有步骤数据
        all_data = PageStepDataService.get_all_step_data(page_id)
        
        # 数据转换和包装
        return PageStepWrapper.wrap_all_step_data(all_data)