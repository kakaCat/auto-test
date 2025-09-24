"""
API接口业务服务层
处理API接口相关的业务逻辑和数据转换

遵循防腐层设计原则：
- Service层负责数据收集与组装
- 不直接操作基础设施
- 使用静态方法提高性能
- 封装基础设施调用
- 统一异常处理
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..database.dao import ApiInterfaceDAO, SystemDAO, ModuleDAO
from ..models.api_interface import (
    ApiInterface, ApiInterfaceCreate, ApiInterfaceUpdate, 
    ApiInterfaceQueryRequest, ApiInterfaceStats,
    ApiInterfaceBatchRequest
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ApiInterfaceService:
    """API接口业务服务类"""
    
    @staticmethod
    def get_api_interfaces() -> List[Dict[str, Any]]:
        """
        获取所有API接口列表
        
        Returns:
            List[Dict[str, Any]]: API接口列表，包含业务转换后的数据
        """
        try:
            # 调用DAO层获取原始数据
            raw_apis = ApiInterfaceDAO.get_all()
            logger.info(f"获取所有API接口列表，共 {len(raw_apis)} 个接口")
            
            # 应用业务规则和数据增强
            enhanced_apis = []
            for api in raw_apis:
                enhanced_api = ApiInterfaceService._apply_business_rules(api)
                enhanced_apis.append(enhanced_api)
            
            return enhanced_apis
            
        except Exception as e:
            logger.error(f"获取API接口列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_api_interface_by_id(api_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取API接口详情
        
        Args:
            api_id (int): API接口ID
            
        Returns:
            Optional[Dict[str, Any]]: API接口详情
        """
        try:
            api = ApiInterfaceDAO.get_by_id(api_id)
            if not api:
                return None
            
            logger.info(f"获取API接口详情成功: ID {api_id}")
            return ApiInterfaceService._apply_business_rules(api)
            
        except Exception as e:
            logger.error(f"获取API接口详情失败: {str(e)}")
            raise
    
    @staticmethod
    def get_api_interfaces_by_system(system_id: int) -> List[Dict[str, Any]]:
        """
        根据系统ID获取API接口列表
        
        Args:
            system_id (int): 系统ID
            
        Returns:
            List[Dict[str, Any]]: API接口列表
        """
        try:
            # 验证系统是否存在
            system = SystemDAO.get_by_id(system_id)
            if not system:
                raise ValueError(f"系统不存在: ID {system_id}")
            
            raw_apis = ApiInterfaceDAO.get_by_system_id(system_id)
            logger.info(f"获取系统 {system_id} 的API接口列表，共 {len(raw_apis)} 个接口")
            
            enhanced_apis = []
            for api in raw_apis:
                enhanced_api = ApiInterfaceService._apply_business_rules(api)
                enhanced_apis.append(enhanced_api)
            
            return enhanced_apis
            
        except Exception as e:
            logger.error(f"获取系统API接口列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_api_interfaces_by_module(module_id: int) -> List[Dict[str, Any]]:
        """
        根据模块ID获取API接口列表
        
        Args:
            module_id (int): 模块ID
            
        Returns:
            List[Dict[str, Any]]: API接口列表
        """
        try:
            # 验证模块是否存在
            module = ModuleDAO.get_by_id(module_id)
            if not module:
                raise ValueError(f"模块不存在: ID {module_id}")
            
            raw_apis = ApiInterfaceDAO.get_by_module_id(module_id)
            logger.info(f"获取模块 {module_id} 的API接口列表，共 {len(raw_apis)} 个接口")
            
            enhanced_apis = []
            for api in raw_apis:
                enhanced_api = ApiInterfaceService._apply_business_rules(api)
                enhanced_apis.append(enhanced_api)
            
            return enhanced_apis
            
        except Exception as e:
            logger.error(f"获取模块API接口列表失败: {str(e)}")
            raise
    
    @staticmethod
    def create_api_interface(api_data: ApiInterfaceCreate) -> Dict[str, Any]:
        """
        创建新API接口
        
        Args:
            api_data (ApiInterfaceCreate): API接口创建数据
            
        Returns:
            Dict[str, Any]: 创建的API接口信息
        """
        try:
            # 业务规则验证
            ApiInterfaceService._validate_api_interface_data(api_data.dict())
            
            # 检查路径和方法组合是否已存在
            if ApiInterfaceService._is_api_path_method_exists(api_data.path, api_data.method, api_data.system_id):
                raise ValueError(f"API接口路径 '{api_data.path}' 和方法 '{api_data.method}' 在该系统中已存在")
            
            # 创建API接口
            api_id = ApiInterfaceDAO.create(api_data.dict())
            created_api = ApiInterfaceDAO.get_by_id(api_id)
            
            logger.info(f"API接口创建成功: {api_data.name} (ID: {api_id})")
            return ApiInterfaceService._apply_business_rules(created_api)
            
        except Exception as e:
            logger.error(f"创建API接口失败: {str(e)}")
            raise
    
    @staticmethod
    def update_api_interface(api_id: int, api_data: ApiInterfaceUpdate) -> Optional[Dict[str, Any]]:
        """
        更新API接口信息
        
        Args:
            api_id (int): API接口ID
            api_data (ApiInterfaceUpdate): API接口更新数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的API接口信息
        """
        try:
            # 检查API接口是否存在
            existing_api = ApiInterfaceDAO.get_by_id(api_id)
            if not existing_api:
                return None
            
            # 业务规则验证
            update_dict = api_data.dict(exclude_unset=True)
            if update_dict:
                ApiInterfaceService._validate_api_interface_data(update_dict, is_update=True)
                
                # 检查路径和方法组合是否冲突
                if 'path' in update_dict or 'method' in update_dict:
                    new_path = update_dict.get('path', existing_api.get('path'))
                    new_method = update_dict.get('method', existing_api.get('method'))
                    system_id = update_dict.get('system_id', existing_api.get('system_id'))
                    
                    if ApiInterfaceService._is_api_path_method_exists(new_path, new_method, system_id, exclude_id=api_id):
                        raise ValueError(f"API接口路径 '{new_path}' 和方法 '{new_method}' 在该系统中已存在")
            
            # 更新API接口
            success = ApiInterfaceDAO.update(api_id, update_dict)
            if success:
                updated_api = ApiInterfaceDAO.get_by_id(api_id)
                logger.info(f"API接口更新成功: ID {api_id}")
                return ApiInterfaceService._apply_business_rules(updated_api)
            return None
            
        except Exception as e:
            logger.error(f"更新API接口失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_api_interface(api_id: int) -> bool:
        """
        删除API接口
        
        Args:
            api_id (int): API接口ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查API接口是否存在
            existing_api = ApiInterfaceDAO.get_by_id(api_id)
            if not existing_api:
                return False
            
            success = ApiInterfaceDAO.delete(api_id)
            if success:
                logger.info(f"API接口删除成功: ID {api_id}")
            return success
            
        except Exception as e:
            logger.error(f"删除API接口失败: {str(e)}")
            raise
    
    @staticmethod
    def search_api_interfaces(query_request: ApiInterfaceQueryRequest) -> List[Dict[str, Any]]:
        """
        搜索API接口
        
        Args:
            query_request (ApiInterfaceQueryRequest): 查询请求参数
            
        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        try:
            # 构建过滤条件
            filters = {}
            if query_request.system_id:
                filters['system_id'] = query_request.system_id
            if query_request.module_id:
                filters['module_id'] = query_request.module_id
            if query_request.method:
                filters['method'] = query_request.method
            if query_request.status:
                filters['status'] = query_request.status
            if query_request.enabled_only:
                filters['status'] = 'active'  # enabled_only为True时只显示active状态的API
            
            # 执行搜索
            raw_apis = ApiInterfaceDAO.search(query_request.keyword or "", filters)
            logger.info(f"搜索API接口，关键词: '{query_request.keyword}', 结果数: {len(raw_apis)}")
            
            # 应用业务规则
            enhanced_apis = []
            for api in raw_apis:
                enhanced_api = ApiInterfaceService._apply_business_rules(api)
                enhanced_apis.append(enhanced_api)
            
            # 应用分页
            if query_request.page and query_request.size:
                start = (query_request.page - 1) * query_request.size
                end = start + query_request.size
                enhanced_apis = enhanced_apis[start:end]
            
            return enhanced_apis
            
        except Exception as e:
            logger.error(f"搜索API接口失败: {str(e)}")
            raise
    
    @staticmethod
    def get_api_interface_stats() -> Dict[str, Any]:
        """
        获取API接口统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            stats = ApiInterfaceDAO.get_stats()
            logger.info("获取API接口统计信息成功")
            
            # 添加业务计算
            stats['timestamp'] = datetime.now().isoformat()
            stats['health_score'] = ApiInterfaceService._calculate_health_score(stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"获取API接口统计信息失败: {str(e)}")
            raise
    
    @staticmethod
    def batch_update_status(batch_request: ApiInterfaceBatchRequest) -> Dict[str, Any]:
        """
        批量更新API接口状态
        
        Args:
            batch_request (ApiInterfaceBatchRequest): 批量操作请求
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            if not batch_request.api_ids:
                raise ValueError("API接口ID列表不能为空")
            
            updated_count = ApiInterfaceDAO.batch_update_status(batch_request.api_ids, batch_request.status)
            logger.info(f"批量更新API接口状态成功，更新数量: {updated_count}")
            
            return {
                'updated_count': updated_count,
                'total_count': len(batch_request.api_ids),
                'status': batch_request.status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"批量更新API接口状态失败: {str(e)}")
            raise
    
    @staticmethod
    def batch_delete(api_ids: List[int]) -> Dict[str, Any]:
        """
        批量删除API接口
        
        Args:
            api_ids (List[int]): API接口ID列表
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            if not api_ids:
                raise ValueError("API接口ID列表不能为空")
            
            deleted_count = ApiInterfaceDAO.batch_delete(api_ids)
            logger.info(f"批量删除API接口成功，删除数量: {deleted_count}")
            
            return {
                'deleted_count': deleted_count,
                'total_count': len(api_ids),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"批量删除API接口失败: {str(e)}")
            raise
    
    @staticmethod
    def collect_api_interfaces_data(page: int = 1, size: int = 10, search: Optional[str] = None, 
                                   system_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        收集API接口数据 - 支持分页和筛选
        
        Args:
            page: 页码
            size: 每页数量
            search: 搜索关键词
            system_id: 系统ID筛选
            status: 状态筛选
            
        Returns:
            List[Dict[str, Any]]: API接口数据列表
        """
        try:
            # 构建查询请求
            query_request = ApiInterfaceQueryRequest(
                keyword=search,
                system_id=system_id,
                status=status,
                page=page,
                size=size
            )
            
            return ApiInterfaceService.search_api_interfaces(query_request)
            
        except Exception as e:
            logger.error(f"收集API接口数据失败: {e}")
            return []
    
    # 私有方法
    @staticmethod
    def _apply_business_rules(api: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用业务规则
        
        Args:
            api (Dict[str, Any]): 原始API接口数据
            
        Returns:
            Dict[str, Any]: 应用业务规则后的数据
        """
        # 添加状态标签
        status = api.get('status', 'inactive')
        api['status_label'] = {
            'active': '启用',
            'inactive': '禁用',
            'deprecated': '已废弃',
            'testing': '测试中'
        }.get(status, '未知')
        
        # 添加方法标签颜色
        method = api.get('method', 'GET')
        api['method_color'] = {
            'GET': 'success',
            'POST': 'primary',
            'PUT': 'warning',
            'DELETE': 'danger',
            'PATCH': 'info'
        }.get(method, 'default')
        
        # 处理标签
        tags = api.get('tags')
        if tags and isinstance(tags, str):
            try:
                import json
                api['tags_list'] = json.loads(tags)
            except:
                api['tags_list'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
        else:
            api['tags_list'] = []
        
        # 添加完整URL
        path = api.get('path', '')
        if not path.startswith('/'):
            path = '/' + path
        api['full_url'] = path
        
        return api
    
    @staticmethod
    def _validate_api_interface_data(api_data: Dict[str, Any], is_update: bool = False) -> None:
        """
        验证API接口数据
        
        Args:
            api_data (Dict[str, Any]): API接口数据
            is_update (bool): 是否为更新操作
        """
        # 验证必填字段（仅在创建时）
        if not is_update:
            required_fields = ['name', 'method', 'path']
            for field in required_fields:
                if not api_data.get(field):
                    raise ValueError(f"字段 '{field}' 不能为空")
        
        # 验证HTTP方法
        if 'method' in api_data:
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
            if api_data['method'].upper() not in valid_methods:
                raise ValueError(f"无效的HTTP方法: {api_data['method']}")
        
        # 验证路径格式
        if 'path' in api_data:
            path = api_data['path']
            if not path.startswith('/'):
                raise ValueError("API路径必须以 '/' 开头")
        
        # 验证状态
        if 'status' in api_data:
            valid_statuses = ['active', 'inactive', 'deprecated', 'testing']
            if api_data['status'] not in valid_statuses:
                raise ValueError(f"无效的状态: {api_data['status']}")
        
        # 验证系统ID和模块ID
        if 'system_id' in api_data and api_data['system_id']:
            system = SystemDAO.get_by_id(api_data['system_id'])
            if not system:
                raise ValueError(f"系统不存在: ID {api_data['system_id']}")
        
        if 'module_id' in api_data and api_data['module_id']:
            module = ModuleDAO.get_by_id(api_data['module_id'])
            if not module:
                raise ValueError(f"模块不存在: ID {api_data['module_id']}")
    
    @staticmethod
    def _is_api_path_method_exists(path: str, method: str, system_id: int, exclude_id: Optional[int] = None) -> bool:
        """
        检查API路径和方法组合是否已存在
        
        Args:
            path (str): API路径
            method (str): HTTP方法
            system_id (int): 系统ID
            exclude_id (Optional[int]): 排除的API接口ID（用于更新时）
            
        Returns:
            bool: 是否已存在
        """
        try:
            apis = ApiInterfaceDAO.get_by_system_id(system_id)
            for api in apis:
                if (api.get('path') == path and 
                    api.get('method') == method and 
                    (exclude_id is None or api.get('id') != exclude_id)):
                    return True
            return False
        except Exception as e:
            logger.error(f"检查API路径方法是否存在时发生错误: {e}")
            return False
    
    @staticmethod
    def _calculate_health_score(stats: Dict[str, Any]) -> float:
        """
        计算API接口健康度评分
        
        Args:
            stats (Dict[str, Any]): 统计数据
            
        Returns:
            float: 健康度评分 (0-100)
        """
        try:
            total = stats.get('total', 0)
            if total == 0:
                return 100.0
            
            by_status = stats.get('by_status', {})
            active_count = by_status.get('active', 0)
            deprecated_count = by_status.get('deprecated', 0)
            
            # 计算健康度：活跃接口占比 - 废弃接口占比
            active_ratio = active_count / total
            deprecated_ratio = deprecated_count / total
            
            health_score = (active_ratio - deprecated_ratio * 0.5) * 100
            return max(0.0, min(100.0, health_score))
            
        except Exception as e:
            logger.error(f"计算健康度评分失败: {e}")
            return 50.0  # 默认评分