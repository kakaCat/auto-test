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
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..database.dao import ApiInterfaceDAO, SystemDAO, ModuleDAO
from ..models.api_interface import (
    ApiInterface, ApiInterfaceCreate, ApiInterfaceUpdate, 
    ApiInterfaceQueryRequest, ApiInterfaceStats,
    ApiInterfaceBatchRequest
)
from ..utils.logger import get_logger
from ..mcp.tools.http_tools import HttpTools
from ..mcp.tools.validation_tools import ValidationTools

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
            existing_api = ApiInterfaceService._get_existing_api_by_path_method(api_data.path, api_data.method, api_data.system_id)
            if existing_api:
                system_info = SystemDAO.get_by_id(api_data.system_id)
                system_name = system_info.get('name', f'ID:{api_data.system_id}') if system_info else f'ID:{api_data.system_id}'
                raise ValueError(f"API接口路径 '{api_data.path}' 和方法 '{api_data.method}' 在系统 \"{system_name}\" 中已存在（现有API: \"{existing_api.get('name', '未命名')}\" ID:{existing_api.get('id')}）。请修改路径或方法，或考虑更新现有API。")
            
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
                
                # 处理enabled和status字段的双向同步
                if 'enabled' in update_dict:
                    enabled = update_dict['enabled']
                    if isinstance(enabled, bool):
                        update_dict['status'] = 'active' if enabled else 'inactive'
                    else:
                        update_dict['status'] = 'active' if enabled == 1 else 'inactive'
                elif 'status' in update_dict:
                    status = update_dict['status']
                    update_dict['enabled'] = 1 if status == 'active' else 0
                
                # 检查路径和方法组合是否冲突
                if 'path' in update_dict or 'method' in update_dict:
                    new_path = update_dict.get('path', existing_api.get('path'))
                    new_method = update_dict.get('method', existing_api.get('method'))
                    system_id = update_dict.get('system_id', existing_api.get('system_id'))
                    
                    conflicting_api = ApiInterfaceService._get_existing_api_by_path_method(new_path, new_method, system_id, exclude_id=api_id)
                    if conflicting_api:
                        system_info = SystemDAO.get_by_id(system_id)
                        system_name = system_info.get('name', f'ID:{system_id}') if system_info else f'ID:{system_id}'
                        raise ValueError(f"API接口路径 '{new_path}' 和方法 '{new_method}' 在系统 \"{system_name}\" 中已存在（冲突API: \"{conflicting_api.get('name', '未命名')}\" ID:{conflicting_api.get('id')}）。请修改路径或方法。")
            
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

    # ======================================================================
    # 草稿正确性校验（无需保存）
    # ======================================================================
    @staticmethod
    def test_api_draft(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于前端表单的草稿配置进行正确性校验（不保存）

        Args:
            test_data: 前端提交的测试数据，预期包含：
                - method: HTTP方法
                - url: 完整URL或基础URL+路径
                - headers: 可选，请求头字典
                - params: 可选，查询参数字典
                - body: 可选，请求体对象或字符串
                - timeout: 可选，超时秒数
                - rules: 可选，响应验证规则列表

        Returns:
            Dict[str, Any]: 校验结果，包含请求响应与规则校验摘要
        """
        try:
            # 输入校验（快速失败）
            if not test_data or 'method' not in test_data or 'url' not in test_data:
                raise ValueError('缺少必要参数：method 或 url')

            method = str(test_data.get('method', 'GET')).upper()
            url = str(test_data.get('url'))
            headers = test_data.get('headers') or {}
            params = test_data.get('params')
            body = test_data.get('body')
            timeout = test_data.get('timeout', 30)
            rules = test_data.get('rules') or []

            # 构造HTTP请求参数
            http_params = {
                'method': method,
                'url': url,
                'headers': headers,
                'timeout': timeout
            }
            if params:
                http_params['params'] = params
            if body is not None:
                http_params['body'] = body

            # 执行HTTP请求（使用内置HttpTools）
            response = asyncio.run(HttpTools.http_request(http_params, context={}))

            # 规则校验（可选）
            validation_summary: Optional[Dict[str, Any]] = None
            if isinstance(rules, list) and len(rules) > 0:
                validate_params = {
                    'response': {
                        'status_code': response.get('status_code'),
                        'headers': response.get('headers', {}),
                        'body': response.get('body')
                    },
                    'rules': rules,
                    'strict': False
                }
                validation_summary = asyncio.run(ValidationTools.validate_response(validate_params, context={}))

            return {
                'request': {
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'params': params,
                    'timeout': timeout
                },
                'response': response,
                'validation': validation_summary
            }
        except Exception as e:
            logger.error(f"草稿正确性校验失败: {e}")
            raise
    
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
        # 双向转换enabled和status字段以保持前后端兼容性
        
        # 如果有enabled字段，转换为status
        if 'enabled' in api and api['enabled'] is not None:
            enabled = api.get('enabled', 0)
            if isinstance(enabled, bool):
                api['status'] = 'active' if enabled else 'inactive'
            else:
                api['status'] = 'active' if enabled == 1 else 'inactive'
        
        # 如果有status字段，转换为enabled
        status = api.get('status', 'inactive')
        api['enabled'] = status == 'active'
        
        # 添加状态标签
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
        
        # 处理请求模式（优先使用 request_schema，兼容旧字段 request_params）
        import json
        request_schema = api.get('request_schema')
        if isinstance(request_schema, str):
            try:
                api['request_schema'] = json.loads(request_schema)
            except Exception:
                api['request_schema'] = {}
        elif request_schema is None:
            # 兼容旧字段 request_params
            request_params = api.get('request_params')
            if isinstance(request_params, str):
                try:
                    api['request_schema'] = json.loads(request_params)
                except Exception:
                    api['request_schema'] = {}
            else:
                api['request_schema'] = request_params or {}
        else:
            api['request_schema'] = request_schema

        # 处理响应模式（优先使用 response_schema，兼容字段 example_response 作为回退）
        response_schema = api.get('response_schema')
        if isinstance(response_schema, str):
            try:
                api['response_schema'] = json.loads(response_schema)
            except Exception:
                api['response_schema'] = {}
        elif response_schema is None or response_schema == {}:
            example_response = api.get('example_response')
            if isinstance(example_response, str):
                try:
                    api['response_schema'] = json.loads(example_response)
                except Exception:
                    api['response_schema'] = {}
            else:
                api['response_schema'] = example_response or {}
        else:
            api['response_schema'] = response_schema
        
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
            required_fields = ['name', 'method', 'path', 'system_id', 'module_id']
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
        if 'system_id' in api_data:
            if not api_data['system_id']:
                if not is_update:
                    raise ValueError("系统ID不能为空")
            else:
                system = SystemDAO.get_by_id(api_data['system_id'])
                if not system:
                    raise ValueError(f"系统不存在: ID {api_data['system_id']}")
        
        if 'module_id' in api_data:
            if not api_data['module_id']:
                if not is_update:
                    raise ValueError("模块ID不能为空")
            else:
                module = ModuleDAO.get_by_id(api_data['module_id'])
                if not module:
                    raise ValueError(f"模块不存在: ID {api_data['module_id']}")
                
                # 验证模块是否属于指定的系统
                if 'system_id' in api_data and api_data['system_id']:
                    if module.get('system_id') != api_data['system_id']:
                        raise ValueError(f"模块 ID {api_data['module_id']} 不属于系统 ID {api_data['system_id']}")
    
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
            return ApiInterfaceDAO.check_path_method_exists(path, method, system_id, exclude_id)
        except Exception as e:
            logger.error(f"检查API路径方法是否存在时发生错误: {e}")
            return False

    @staticmethod
    def _get_existing_api_by_path_method(path: str, method: str, system_id: int, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        获取已存在的API接口详细信息
        
        Args:
            path (str): API路径
            method (str): HTTP方法
            system_id (int): 系统ID
            exclude_id (Optional[int]): 排除的API接口ID（用于更新时）
            
        Returns:
            Optional[Dict[str, Any]]: 已存在的API接口信息，如果不存在则返回None
        """
        try:
            return ApiInterfaceDAO.get_by_path_method(path, method, system_id, exclude_id)
        except Exception as e:
            logger.error(f"获取已存在API接口信息时发生错误: {e}")
            return None
    
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