"""
页面分步保存数据服务层
Page Step Save Data Service Layer

负责聚合和管理页面分步保存的数据：
- 数据聚合和组装
- 多数据源统一管理
- 数据一致性保证
- 缓存管理
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

from ..repositories.page_step_repository import PageStepRepository
from ..database.dao import PageDAO
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PageStepDataService:
    """页面分步保存数据服务"""

    @staticmethod
    def save_step_data(page_id: int, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存步骤数据
        
        Args:
            page_id (int): 页面ID
            step (str): 步骤名称
            data (Dict[str, Any]): 步骤数据
            
        Returns:
            Dict[str, Any]: 保存结果
        """
        try:
            # 验证页面是否存在
            page = PageDAO.get_by_id(page_id)
            if not page:
                raise ValueError(f"页面不存在: ID {page_id}")
            
            # 如果是基本信息步骤，同时更新主页面记录
            if step == 'basic':
                PageDAO.update(
                    page_id=page_id,
                    name=data.get('name'),
                    description=data.get('description'),
                    route_path=data.get('route_path'),
                    page_type=data.get('page_type')
                )
            
            step_data = {
                'page_id': page_id,
                'step': step,
                'data': data,
                'saved_at': datetime.now()
            }
            
            result = PageStepRepository.save_step_data(step_data)
            logger.info(f"保存步骤数据成功: 页面ID {page_id}, 步骤 {step}")
            return result
            
        except Exception as e:
            logger.error(f"保存步骤数据失败: {str(e)}")
            raise

    @staticmethod
    def get_step_data(page_id: int, step: str) -> Optional[Dict[str, Any]]:
        """
        获取单个步骤数据
        
        Args:
            page_id (int): 页面ID
            step (str): 步骤名称
            
        Returns:
            Optional[Dict[str, Any]]: 步骤数据
        """
        try:
            result = PageStepRepository.get_step_data(page_id, step)
            if result:
                logger.info(f"获取步骤数据成功: 页面ID {page_id}, 步骤 {step}")
            return result
            
        except Exception as e:
            logger.error(f"获取步骤数据失败: {str(e)}")
            raise

    @staticmethod
    def get_all_steps_data(page_id: int) -> Dict[str, Any]:
        """
        获取所有步骤数据
        
        Args:
            page_id (int): 页面ID
            
        Returns:
            Dict[str, Any]: 所有步骤数据
        """
        try:
            result = PageStepRepository.get_all_steps_data(page_id)
            logger.info(f"获取所有步骤数据成功: 页面ID {page_id}")
            return result
            
        except Exception as e:
            logger.error(f"获取所有步骤数据失败: {str(e)}")
            raise

    @staticmethod
    def update_progress(page_id: int, current_step: str, completed_steps: List[str], 
                       step_status: Dict[str, str]) -> Dict[str, Any]:
        """
        更新配置进度
        
        Args:
            page_id (int): 页面ID
            current_step (str): 当前步骤
            completed_steps (List[str]): 已完成步骤列表
            step_status (Dict[str, str]): 步骤状态
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            # 步骤名称到索引的映射
            step_order = {'basic': 0, 'layout': 1, 'api': 2, 'interaction': 3}
            
            # 转换当前步骤为索引
            current_step_index = step_order.get(current_step, 0)
            
            # 转换已完成步骤为索引列表
            completed_step_indices = [step_order[step] for step in completed_steps if step in step_order]
            completed_step_indices.sort()
            
            progress = {
                'page_id': page_id,
                'current_step': current_step_index,
                'completed_steps': completed_step_indices,
                'step_status': step_status,
                'last_saved_at': datetime.now(),
                'is_completed': len(completed_step_indices) == 4
            }
            
            result = PageStepRepository.save_progress(progress)
            logger.info(f"更新配置进度成功: 页面ID {page_id}")
            return result
            
        except Exception as e:
            logger.error(f"更新配置进度失败: {str(e)}")
            raise

    @staticmethod
    def get_progress(page_id: int) -> Optional[Dict[str, Any]]:
        """
        获取配置进度
        
        Args:
            page_id (int): 页面ID
            
        Returns:
            Optional[Dict[str, Any]]: 配置进度
        """
        try:
            result = PageStepRepository.get_progress(page_id)
            if result:
                logger.info(f"获取配置进度成功: 页面ID {page_id}")
            return result
            
        except Exception as e:
            logger.error(f"获取配置进度失败: {str(e)}")
            raise

    @staticmethod
    def complete_page_config(page_id: int) -> Dict[str, Any]:
        """
        完成页面配置
        
        Args:
            page_id (int): 页面ID
            
        Returns:
            Dict[str, Any]: 完成结果
        """
        try:
            # 验证页面是否存在
            page = PageDAO.get_by_id(page_id)
            if not page:
                raise ValueError(f"页面不存在: ID {page_id}")
            
            # 获取当前进度
            progress = PageStepRepository.get_progress(page_id)
            if not progress:
                raise ValueError(f"页面配置进度不存在: ID {page_id}")
            
            # 更新为已完成状态
            progress['is_completed'] = True
            progress['completed_at'] = datetime.now()
            
            result = PageStepRepository.save_progress(progress)
            logger.info(f"完成页面配置成功: 页面ID {page_id}")
            return result
            
        except Exception as e:
            logger.error(f"完成页面配置失败: {str(e)}")
            raise

    @staticmethod
    def reset_step(page_id: int, step: str) -> bool:
        """
        重置指定步骤
        
        Args:
            page_id (int): 页面ID
            step (str): 步骤名称
            
        Returns:
            bool: 重置结果
        """
        try:
            result = PageStepRepository.delete_step_data(page_id, step)
            logger.info(f"重置步骤成功: 页面ID {page_id}, 步骤 {step}")
            return result
            
        except Exception as e:
            logger.error(f"重置步骤失败: {str(e)}")
            raise

    @staticmethod
    def delete_all_steps(page_id: int) -> bool:
        """
        删除所有步骤数据
        
        Args:
            page_id (int): 页面ID
            
        Returns:
            bool: 删除结果
        """
        try:
            # 删除所有步骤数据
            PageStepRepository.delete_all_steps_data(page_id)
            # 删除配置进度
            PageStepRepository.delete_progress(page_id)
            
            logger.info(f"删除所有步骤数据成功: 页面ID {page_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除所有步骤数据失败: {str(e)}")
            raise

    @staticmethod
    def get_incomplete_pages() -> List[Dict[str, Any]]:
        """
        获取配置未完成的页面列表
        
        Returns:
            List[Dict[str, Any]]: 未完成页面列表
        """
        try:
            result = PageStepRepository.get_incomplete_pages()
            logger.info(f"获取未完成页面列表成功: 共 {len(result)} 个页面")
            return result
            
        except Exception as e:
            logger.error(f"获取未完成页面列表失败: {str(e)}")
            raise

    @staticmethod
    def get_step_stats() -> Dict[str, Any]:
        """
        获取步骤统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            result = PageStepRepository.get_step_stats()
            logger.info("获取步骤统计信息成功")
            return result
            
        except Exception as e:
            logger.error(f"获取步骤统计信息失败: {str(e)}")
            raise

    @staticmethod
    def cleanup_expired_drafts(days: int = 30) -> int:
        """
        清理过期草稿
        
        Args:
            days (int): 过期天数，默认30天
            
        Returns:
            int: 清理的记录数
        """
        try:
            result = PageStepRepository.cleanup_expired_drafts(days)
            logger.info(f"清理过期草稿成功: 清理了 {result} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"清理过期草稿失败: {str(e)}")
            raise