"""
页面分步保存数据服务层
Page Step Save Data Service Layer

负责数据聚合和多数据源管理：
- 统一管理Repository、Redis、ES等多种数据源
- 屏蔽底层存储差异
- 提供数据聚合功能
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from ..repositories.page_step_repository import PageStepRepository
from ..database.dao import PageDAO
from ..models.page_step import StepStatus


class PageStepDataService:
    """页面分步保存数据服务"""

    @staticmethod
    def save_step_data(page_id: int, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """保存步骤数据"""
        # 确保页面存在
        page = PageDAO.get_by_id(page_id)
        if not page:
            raise ValueError(f"页面不存在: {page_id}")
        
        # 如果是基本信息步骤，同时更新主页面记录
        if step == 'basic':
            print(f"正在更新页面 {page_id} 的基本信息...")
            print(f"更新数据: name={data.get('name')}, description={data.get('description')}, route_path={data.get('route_path')}, page_type={data.get('page_type')}")
            result = PageDAO.update(
                page_id=page_id,
                name=data.get('name'),
                description=data.get('description'),
                route_path=data.get('route_path'),
                page_type=data.get('page_type')
            )
            print(f"更新结果: {result}")
        
        # 保存步骤数据
        step_data = {
            'page_id': page_id,
            'step': step,
            'data': data,
            'saved_at': datetime.now()
        }
        
        return PageStepRepository.save_step_data(step_data)

    @staticmethod
    def get_step_data(page_id: int, step: str) -> Optional[Dict[str, Any]]:
        """获取步骤数据"""
        return PageStepRepository.get_step_data(page_id, step)

    @staticmethod
    def get_all_step_data(page_id: int) -> Dict[str, Any]:
        """获取所有步骤数据"""
        steps = ['basic', 'layout', 'api', 'interaction']
        all_data = {}
        
        for step in steps:
            step_data = PageStepRepository.get_step_data(page_id, step)
            if step_data:
                all_data[step] = step_data['data']
        
        return all_data

    @staticmethod
    def update_progress(page_id: int, step: str, status: StepStatus) -> Dict[str, Any]:
        """更新配置进度"""
        # 获取当前进度
        progress = PageStepRepository.get_progress(page_id)
        
        if not progress:
            # 创建新的进度记录
            progress = {
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
        
        # 更新步骤状态
        progress['step_status'][step] = status
        progress['last_saved_at'] = datetime.now()
        
        # 更新当前步骤和已完成步骤
        step_order = {'basic': 0, 'layout': 1, 'api': 2, 'interaction': 3}
        step_index = step_order[step]
        
        if status == 'completed':
            if step_index not in progress['completed_steps']:
                progress['completed_steps'].append(step_index)
                progress['completed_steps'].sort()
            
            # 更新当前步骤为下一个未完成的步骤
            next_step = step_index + 1
            if next_step < 4:
                progress['current_step'] = next_step
            else:
                progress['current_step'] = 3  # 最后一步
        
        # 检查是否所有步骤都完成
        if len(progress['completed_steps']) == 4:
            progress['is_completed'] = True
        
        return PageStepRepository.save_progress(progress)

    @staticmethod
    def get_progress(page_id: int) -> Optional[Dict[str, Any]]:
        """获取配置进度"""
        return PageStepRepository.get_progress(page_id)

    @staticmethod
    def complete_page_config(page_id: int) -> Dict[str, Any]:
        """完成页面配置"""
        # 更新页面状态为激活
        PageDAO.update(page_id=page_id, status='active')
        
        # 更新进度为完成状态
        progress = PageStepRepository.get_progress(page_id)
        if progress:
            progress['is_completed'] = True
            progress['last_saved_at'] = datetime.now()
            PageStepRepository.save_progress(progress)
        
        return {
            'page_id': page_id,
            'completed_at': datetime.now(),
            'status': 'active'
        }

    @staticmethod
    def reset_step_data(page_id: int, step: str) -> bool:
        """重置步骤数据"""
        return PageStepRepository.delete_step_data(page_id, step)

    @staticmethod
    def delete_all_step_data(page_id: int) -> bool:
        """删除所有步骤数据"""
        steps = ['basic', 'layout', 'api', 'interaction']
        success = True
        
        for step in steps:
            if not PageStepRepository.delete_step_data(page_id, step):
                success = False
        
        # 删除进度记录
        if not PageStepRepository.delete_progress(page_id):
            success = False
        
        return success

    @staticmethod
    def get_pages_with_incomplete_config() -> List[Dict[str, Any]]:
        """获取配置未完成的页面列表"""
        return PageStepRepository.get_incomplete_pages()

    @staticmethod
    def get_step_statistics() -> Dict[str, Any]:
        """获取步骤统计信息"""
        return PageStepRepository.get_step_statistics()

    @staticmethod
    def cleanup_expired_drafts(days: int = 7) -> int:
        """清理过期的草稿数据"""
        return PageStepRepository.cleanup_expired_drafts(days)