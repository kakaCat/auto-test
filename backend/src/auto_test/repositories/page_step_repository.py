"""
页面分步保存数据仓库层
Page Step Save Repository Layer

负责数据库访问和SQL执行：
- 数据库CRUD操作
- SQL查询执行
- 事务管理
- 数据持久化
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json


class PageStepRepository:
    """页面分步保存数据仓库"""

    @staticmethod
    def save_step_data(step_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存步骤数据"""
        # 模拟数据库保存操作
        # 实际实现中应该使用数据库连接
        
        # 这里使用内存存储作为示例
        if not hasattr(PageStepRepository, '_step_data_store'):
            PageStepRepository._step_data_store = {}
        
        key = f"{step_data['page_id']}_{step_data['step']}"
        PageStepRepository._step_data_store[key] = {
            'id': len(PageStepRepository._step_data_store) + 1,
            'page_id': step_data['page_id'],
            'step': step_data['step'],
            'data': json.dumps(step_data['data']),
            'saved_at': step_data['saved_at'],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return PageStepRepository._step_data_store[key]

    @staticmethod
    def get_step_data(page_id: int, step: str) -> Optional[Dict[str, Any]]:
        """获取步骤数据"""
        if not hasattr(PageStepRepository, '_step_data_store'):
            return None
        
        key = f"{page_id}_{step}"
        step_data = PageStepRepository._step_data_store.get(key)
        
        if step_data:
            return {
                'id': step_data['id'],
                'page_id': step_data['page_id'],
                'step': step_data['step'],
                'data': json.loads(step_data['data']),
                'saved_at': step_data['saved_at'],
                'created_at': step_data['created_at'],
                'updated_at': step_data['updated_at']
            }
        
        return None

    @staticmethod
    def delete_step_data(page_id: int, step: str) -> bool:
        """删除步骤数据"""
        if not hasattr(PageStepRepository, '_step_data_store'):
            return True
        
        key = f"{page_id}_{step}"
        if key in PageStepRepository._step_data_store:
            del PageStepRepository._step_data_store[key]
        
        return True

    @staticmethod
    def save_progress(progress: Dict[str, Any]) -> Dict[str, Any]:
        """保存配置进度"""
        if not hasattr(PageStepRepository, '_progress_store'):
            PageStepRepository._progress_store = {}
        
        page_id = progress['page_id']
        PageStepRepository._progress_store[page_id] = {
            'id': page_id,
            'page_id': page_id,
            'current_step': progress['current_step'],
            'completed_steps': json.dumps(progress['completed_steps']),
            'step_status': json.dumps(progress['step_status']),
            'last_saved_at': progress['last_saved_at'],
            'is_completed': progress['is_completed'],
            'created_at': progress.get('created_at', datetime.now()),
            'updated_at': datetime.now()
        }
        
        return PageStepRepository._progress_store[page_id]

    @staticmethod
    def get_progress(page_id: int) -> Optional[Dict[str, Any]]:
        """获取配置进度"""
        if not hasattr(PageStepRepository, '_progress_store'):
            return None
        
        progress = PageStepRepository._progress_store.get(page_id)
        
        if progress:
            return {
                'id': progress['id'],
                'page_id': progress['page_id'],
                'current_step': progress['current_step'],
                'completed_steps': json.loads(progress['completed_steps']),
                'step_status': json.loads(progress['step_status']),
                'last_saved_at': progress['last_saved_at'],
                'is_completed': progress['is_completed'],
                'created_at': progress['created_at'],
                'updated_at': progress['updated_at']
            }
        
        return None

    @staticmethod
    def delete_progress(page_id: int) -> bool:
        """删除配置进度"""
        if not hasattr(PageStepRepository, '_progress_store'):
            return True
        
        if page_id in PageStepRepository._progress_store:
            del PageStepRepository._progress_store[page_id]
        
        return True

    @staticmethod
    def get_incomplete_pages() -> List[Dict[str, Any]]:
        """获取配置未完成的页面列表"""
        if not hasattr(PageStepRepository, '_progress_store'):
            return []
        
        incomplete_pages = []
        for progress in PageStepRepository._progress_store.values():
            if not progress['is_completed']:
                incomplete_pages.append({
                    'page_id': progress['page_id'],
                    'current_step': progress['current_step'],
                    'completed_steps': json.loads(progress['completed_steps']),
                    'step_status': json.loads(progress['step_status']),
                    'last_saved_at': progress['last_saved_at']
                })
        
        return incomplete_pages

    @staticmethod
    def get_step_statistics() -> Dict[str, Any]:
        """获取步骤统计信息"""
        if not hasattr(PageStepRepository, '_progress_store'):
            return {
                'total_pages': 0,
                'completed_pages': 0,
                'incomplete_pages': 0,
                'step_completion_rate': {
                    'basic': 0,
                    'layout': 0,
                    'api': 0,
                    'interaction': 0
                }
            }
        
        total_pages = len(PageStepRepository._progress_store)
        completed_pages = sum(1 for p in PageStepRepository._progress_store.values() if p['is_completed'])
        incomplete_pages = total_pages - completed_pages
        
        # 计算各步骤完成率
        step_counts = {'basic': 0, 'layout': 0, 'api': 0, 'interaction': 0}
        
        for progress in PageStepRepository._progress_store.values():
            step_status = json.loads(progress['step_status'])
            for step, status in step_status.items():
                if status == 'completed':
                    step_counts[step] += 1
        
        step_completion_rate = {}
        for step, count in step_counts.items():
            step_completion_rate[step] = (count / total_pages * 100) if total_pages > 0 else 0
        
        return {
            'total_pages': total_pages,
            'completed_pages': completed_pages,
            'incomplete_pages': incomplete_pages,
            'step_completion_rate': step_completion_rate
        }

    @staticmethod
    def cleanup_expired_drafts(days: int = 7) -> int:
        """清理过期的草稿数据"""
        if not hasattr(PageStepRepository, '_step_data_store'):
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        expired_keys = []
        
        for key, data in PageStepRepository._step_data_store.items():
            if data['saved_at'] < cutoff_date:
                expired_keys.append(key)
        
        for key in expired_keys:
            del PageStepRepository._step_data_store[key]
        
        return len(expired_keys)

    @staticmethod
    def get_all_step_data_for_page(page_id: int) -> Dict[str, Any]:
        """获取页面的所有步骤数据"""
        if not hasattr(PageStepRepository, '_step_data_store'):
            return {}
        
        steps = ['basic', 'layout', 'api', 'interaction']
        all_data = {}
        
        for step in steps:
            key = f"{page_id}_{step}"
            if key in PageStepRepository._step_data_store:
                step_data = PageStepRepository._step_data_store[key]
                all_data[step] = {
                    'data': json.loads(step_data['data']),
                    'saved_at': step_data['saved_at']
                }
        
        return all_data

    @staticmethod
    def batch_save_step_data(step_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量保存步骤数据"""
        results = []
        for step_data in step_data_list:
            result = PageStepRepository.save_step_data(step_data)
            results.append(result)
        return results

    @staticmethod
    def get_pages_by_step_status(step: str, status: str) -> List[int]:
        """根据步骤状态获取页面ID列表"""
        if not hasattr(PageStepRepository, '_progress_store'):
            return []
        
        page_ids = []
        for progress in PageStepRepository._progress_store.values():
            step_status = json.loads(progress['step_status'])
            if step_status.get(step) == status:
                page_ids.append(progress['page_id'])
        
        return page_ids