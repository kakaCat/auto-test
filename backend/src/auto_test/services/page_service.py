"""
页面管理服务层
Page Management Service Layer

遵循极简控制器编码规范：
- Service层负责数据收集与组装
- 业务逻辑防腐层
- 统一异常处理
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database.dao import PageDAO, PageApiDAO, SystemDAO, ApiInterfaceDAO
from ..models.page import PageCreate, PageUpdate, PageApiCreate, PageApiUpdate
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PageService:
    """页面管理服务"""
    
    @staticmethod
    def get_pages(system_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取页面列表
        
        Args:
            system_id (Optional[int]): 系统ID，如果提供则只获取该系统的页面
            
        Returns:
            List[Dict[str, Any]]: 页面列表
        """
        try:
            raw_pages = PageDAO.get_all(system_id)
            logger.info(f"获取页面列表，共 {len(raw_pages)} 个页面")
            
            enhanced_pages = []
            for page in raw_pages:
                enhanced_page = PageService._transform_page_output(page)
                # 获取页面关联的API列表
                page_apis = PageApiDAO.get_by_page_id(page['id'])
                enhanced_page['apis'] = [PageService._transform_page_api_output(api) for api in page_apis]
                enhanced_page['api_count'] = len(page_apis)
                enhanced_pages.append(enhanced_page)
            
            return enhanced_pages
            
        except Exception as e:
            logger.error(f"获取页面列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_page_by_id(page_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取页面详情
        
        Args:
            page_id (int): 页面ID
            
        Returns:
            Optional[Dict[str, Any]]: 页面详情
        """
        try:
            page = PageDAO.get_by_id(page_id)
            if not page:
                return None
            
            enhanced_page = PageService._transform_page_output(page)
            # 获取页面关联的API列表
            page_apis = PageApiDAO.get_by_page_id(page_id)
            enhanced_page['apis'] = [PageService._transform_page_api_output(api) for api in page_apis]
            enhanced_page['api_count'] = len(page_apis)
            
            logger.info(f"获取页面详情成功: ID {page_id}")
            return enhanced_page
            
        except Exception as e:
            logger.error(f"获取页面详情失败: {str(e)}")
            raise
    
    @staticmethod
    def create_page(page_data: PageCreate) -> Dict[str, Any]:
        """
        创建页面
        
        Args:
            page_data (PageCreate): 页面创建数据
            
        Returns:
            Dict[str, Any]: 创建的页面信息
        """
        try:
            # 验证系统是否存在
            system = SystemDAO.get_by_id(page_data.system_id)
            if not system:
                raise ValueError(f"系统不存在: ID {page_data.system_id}")
            
            # 创建页面
            page_id = PageDAO.create(
                system_id=page_data.system_id,
                name=page_data.name,
                description=page_data.description,
                route_path=page_data.route_path,
                page_type=page_data.page_type,
                status=page_data.status
            )
            
            # 获取创建的页面信息
            created_page = PageDAO.get_by_id(page_id)
            enhanced_page = PageService._transform_page_output(created_page)
            enhanced_page['apis'] = []
            enhanced_page['api_count'] = 0
            
            logger.info(f"页面创建成功: ID {page_id}")
            return enhanced_page
            
        except Exception as e:
            logger.error(f"创建页面失败: {str(e)}")
            raise
    
    @staticmethod
    def update_page(page_id: int, page_data: PageUpdate) -> Optional[Dict[str, Any]]:
        """
        更新页面
        
        Args:
            page_id (int): 页面ID
            page_data (PageUpdate): 页面更新数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的页面信息
        """
        try:
            # 检查页面是否存在
            existing_page = PageDAO.get_by_id(page_id)
            if not existing_page:
                return None
            
            # 更新页面
            success = PageDAO.update(
                page_id=page_id,
                name=page_data.name,
                description=page_data.description,
                route_path=page_data.route_path,
                page_type=page_data.page_type,
                status=page_data.status
            )
            
            if success:
                updated_page = PageDAO.get_by_id(page_id)
                enhanced_page = PageService._transform_page_output(updated_page)
                # 获取页面关联的API列表
                page_apis = PageApiDAO.get_by_page_id(page_id)
                enhanced_page['apis'] = [PageService._transform_page_api_output(api) for api in page_apis]
                enhanced_page['api_count'] = len(page_apis)
                
                logger.info(f"页面更新成功: ID {page_id}")
                return enhanced_page
            
            return None
            
        except Exception as e:
            logger.error(f"更新页面失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_page(page_id: int) -> bool:
        """
        删除页面
        
        Args:
            page_id (int): 页面ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 先删除页面的所有API关联
            PageApiDAO.delete_by_page_id(page_id)
            
            # 删除页面
            success = PageDAO.delete(page_id)
            if success:
                logger.info(f"页面删除成功: ID {page_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除页面失败: {str(e)}")
            raise
    
    @staticmethod
    def search_pages(keyword: str = None, system_id: int = None, page_type: str = None,
                    status: str = None, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """
        搜索页面
        
        Args:
            keyword (str): 搜索关键词
            system_id (int): 系统ID
            page_type (str): 页面类型
            status (str): 状态
            page (int): 页码
            size (int): 每页数量
            
        Returns:
            Dict[str, Any]: 搜索结果
        """
        try:
            pages = PageDAO.search(keyword, system_id, page_type, status, page, size)
            
            enhanced_pages = []
            for page_data in pages:
                enhanced_page = PageService._transform_page_output(page_data)
                # 获取页面关联的API列表
                page_apis = PageApiDAO.get_by_page_id(page_data['id'])
                enhanced_page['apis'] = [PageService._transform_page_api_output(api) for api in page_apis]
                enhanced_page['api_count'] = len(page_apis)
                enhanced_pages.append(enhanced_page)
            
            # 获取总数（简化实现，实际应该单独查询）
            total = len(enhanced_pages)
            total_pages = (total + size - 1) // size
            
            logger.info(f"搜索页面成功，共 {total} 个结果")
            
            return {
                'pages': enhanced_pages,
                'total': total,
                'page': page,
                'size': size,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"搜索页面失败: {str(e)}")
            raise
    
    @staticmethod
    def add_page_api(page_api_data: PageApiCreate) -> Dict[str, Any]:
        """
        添加页面API关联
        
        Args:
            page_api_data (PageApiCreate): 页面API关联数据
            
        Returns:
            Dict[str, Any]: 创建的关联信息
        """
        try:
            # 验证页面是否存在
            page = PageDAO.get_by_id(page_api_data.page_id)
            if not page:
                raise ValueError(f"页面不存在: ID {page_api_data.page_id}")
            
            # 验证API是否存在
            api = ApiInterfaceDAO.get_by_id(page_api_data.api_id)
            if not api:
                raise ValueError(f"API接口不存在: ID {page_api_data.api_id}")
            
            # 处理条件数据
            conditions_str = None
            if page_api_data.conditions:
                conditions_str = json.dumps(page_api_data.conditions)
            
            # 创建关联
            relation_id = PageApiDAO.create(
                page_id=page_api_data.page_id,
                api_id=page_api_data.api_id,
                execution_type=page_api_data.execution_type,
                execution_order=page_api_data.execution_order,
                trigger_action=page_api_data.trigger_action,
                api_purpose=page_api_data.api_purpose,
                success_action=page_api_data.success_action,
                error_action=page_api_data.error_action,
                conditions=conditions_str
            )
            
            # 获取创建的关联信息
            page_apis = PageApiDAO.get_by_page_id(page_api_data.page_id)
            created_relation = next((api for api in page_apis if api['id'] == relation_id), None)
            
            if created_relation:
                enhanced_relation = PageService._transform_page_api_output(created_relation)
                logger.info(f"页面API关联创建成功: ID {relation_id}")
                return enhanced_relation
            
            raise Exception("创建关联后无法获取关联信息")
            
        except Exception as e:
            logger.error(f"添加页面API关联失败: {str(e)}")
            raise
    
    @staticmethod
    def update_page_api(relation_id: int, page_api_data: PageApiUpdate) -> Optional[Dict[str, Any]]:
        """
        更新页面API关联
        
        Args:
            relation_id (int): 关联ID
            page_api_data (PageApiUpdate): 更新数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的关联信息
        """
        try:
            # 处理条件数据
            conditions_str = None
            if page_api_data.conditions:
                conditions_str = json.dumps(page_api_data.conditions)
            
            # 更新关联
            success = PageApiDAO.update(
                relation_id=relation_id,
                execution_type=page_api_data.execution_type,
                execution_order=page_api_data.execution_order,
                trigger_action=page_api_data.trigger_action,
                api_purpose=page_api_data.api_purpose,
                success_action=page_api_data.success_action,
                error_action=page_api_data.error_action,
                conditions=conditions_str
            )
            
            if success:
                # 获取更新后的关联信息（需要通过页面ID查询）
                # 这里简化实现，实际应该有更直接的方法
                logger.info(f"页面API关联更新成功: ID {relation_id}")
                return {"id": relation_id, "updated": True}
            
            return None
            
        except Exception as e:
            logger.error(f"更新页面API关联失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_page_api(relation_id: int) -> bool:
        """
        删除页面API关联
        
        Args:
            relation_id (int): 关联ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            success = PageApiDAO.delete(relation_id)
            if success:
                logger.info(f"页面API关联删除成功: ID {relation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除页面API关联失败: {str(e)}")
            raise
    
    @staticmethod
    def _transform_page_output(page: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换页面输出格式
        
        Args:
            page (Dict[str, Any]): 原始页面数据
            
        Returns:
            Dict[str, Any]: 转换后的页面数据
        """
        if not page:
            return {}
        
        # 基础字段转换
        transformed = {
            'id': page.get('id'),
            'system_id': page.get('system_id'),
            'name': page.get('name'),
            'description': page.get('description'),
            'route_path': page.get('route_path'),
            'page_type': page.get('page_type'),
            'status': page.get('status'),
            'created_at': page.get('created_at'),
            'updated_at': page.get('updated_at')
        }
        
        # 添加业务字段
        transformed.update({
            'status_display': PageService._get_status_display(page.get('status')),
            'page_type_display': PageService._get_page_type_display(page.get('page_type')),
            'created_at_formatted': PageService._format_datetime(page.get('created_at')),
            'updated_at_formatted': PageService._format_datetime(page.get('updated_at')),
            'has_route': bool(page.get('route_path')),
            'can_edit': True,  # 简化实现，实际应该根据权限判断
            'can_delete': True  # 简化实现，实际应该根据权限判断
        })
        
        return transformed
    
    @staticmethod
    def _transform_page_api_output(page_api: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换页面API关联输出格式
        
        Args:
            page_api (Dict[str, Any]): 原始页面API关联数据
            
        Returns:
            Dict[str, Any]: 转换后的页面API关联数据
        """
        if not page_api:
            return {}
        
        # 解析条件数据
        conditions = None
        if page_api.get('conditions'):
            try:
                conditions = json.loads(page_api['conditions'])
            except:
                conditions = None
        
        # 基础字段转换
        transformed = {
            'id': page_api.get('id'),
            'page_id': page_api.get('page_id'),
            'api_id': page_api.get('api_id'),
            'execution_type': page_api.get('execution_type'),
            'execution_order': page_api.get('execution_order'),
            'trigger_action': page_api.get('trigger_action'),
            'api_purpose': page_api.get('api_purpose'),
            'success_action': page_api.get('success_action'),
            'error_action': page_api.get('error_action'),
            'conditions': conditions,
            'created_at': page_api.get('created_at'),
            'updated_at': page_api.get('updated_at')
        }
        
        # 添加API信息
        transformed.update({
            'api_name': page_api.get('api_name'),
            'api_method': page_api.get('method'),
            'api_path': page_api.get('path'),
            'api_description': page_api.get('api_description'),
            'execution_type_display': PageService._get_execution_type_display(page_api.get('execution_type')),
            'has_conditions': bool(conditions)
        })
        
        return transformed
    
    @staticmethod
    def _get_status_display(status: str) -> str:
        """获取状态显示文本"""
        status_map = {
            'active': '活跃',
            'inactive': '非活跃',
            'draft': '草稿'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def _get_page_type_display(page_type: str) -> str:
        """获取页面类型显示文本"""
        type_map = {
            'page': '页面',
            'modal': '弹框',
            'drawer': '抽屉'
        }
        return type_map.get(page_type, page_type)
    
    @staticmethod
    def _get_execution_type_display(execution_type: str) -> str:
        """获取执行类型显示文本"""
        type_map = {
            'parallel': '并行',
            'serial': '串行'
        }
        return type_map.get(execution_type, execution_type)
    
    @staticmethod
    def _format_datetime(dt_str: str) -> str:
        """格式化日期时间"""
        if not dt_str:
            return ""
        try:
            # 简化实现，直接返回原字符串
            return dt_str
        except:
            return dt_str