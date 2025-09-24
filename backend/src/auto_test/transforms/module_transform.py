"""
模块数据转换器
采用函数式编程风格，将DAO层原始数据转换为响应数据
"""

from typing import Dict, Any, List, Optional
from .utils import (
    pipe, format_datetime, safe_get, safe_int, safe_str, 
    parse_tags, create_key, add_field
)


class ModuleTransform:
    """模块数据转换器 - 函数式编程风格"""
    
    @staticmethod
    def to_response(raw_module: Dict[str, Any]) -> Dict[str, Any]:
        """
        将DAO层原始数据转换为API响应数据
        
        Args:
            raw_module (Dict[str, Any]): DAO层原始模块数据
            
        Returns:
            Dict[str, Any]: 转换后的响应数据
        """
        if not raw_module:
            return {}
        
        return pipe(
            raw_module,
            ModuleTransform._add_business_fields,
            ModuleTransform._format_timestamps,
            ModuleTransform._process_tags,
            ModuleTransform._add_status_display,
            ModuleTransform._add_computed_fields
        )
    
    @staticmethod
    def to_list_response(raw_modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将DAO层原始数据列表转换为API响应数据列表
        
        Args:
            raw_modules (List[Dict[str, Any]]): DAO层原始模块数据列表
            
        Returns:
            List[Dict[str, Any]]: 转换后的响应数据列表
        """
        if not raw_modules:
            return []
        
        return [ModuleTransform.to_response(module) for module in raw_modules]
    
    @staticmethod
    def to_summary(raw_module: Dict[str, Any]) -> Dict[str, Any]:
        """
        将DAO层原始数据转换为摘要数据
        
        Args:
            raw_module (Dict[str, Any]): DAO层原始模块数据
            
        Returns:
            Dict[str, Any]: 转换后的摘要数据
        """
        if not raw_module:
            return {}
        
        return pipe(
            raw_module,
            ModuleTransform._extract_summary_fields,
            ModuleTransform._add_status_display,
            ModuleTransform._process_tags
        )
    
    @staticmethod
    def _add_business_fields(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加业务字段
        
        Args:
            module (Dict[str, Any]): 原始模块数据
            
        Returns:
            Dict[str, Any]: 添加业务字段后的数据
        """
        enhanced = module.copy()
        
        # 添加模块唯一键
        system_id = safe_int(module.get('system_id'))
        module_id = safe_int(module.get('id'))
        enhanced['module_key'] = create_key(system_id, module_id)
        
        # 添加活跃状态
        enhanced['is_active'] = module.get('status') == 'active'
        
        # 添加模块类型（基于名称推断）
        module_name = safe_str(module.get('name', '')).lower()
        enhanced['module_type'] = ModuleTransform._infer_module_type(module_name)
        
        # 添加优先级（基于状态）
        enhanced['priority'] = ModuleTransform._calculate_priority(module.get('status'))
        
        return enhanced
    
    @staticmethod
    def _format_timestamps(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化时间戳
        
        Args:
            module (Dict[str, Any]): 模块数据
            
        Returns:
            Dict[str, Any]: 格式化时间戳后的数据
        """
        enhanced = module.copy()
        
        # 格式化创建时间
        if module.get('created_at'):
            enhanced['created_at_formatted'] = format_datetime(module['created_at'])
            enhanced['created_date'] = format_datetime(module['created_at'], '%Y-%m-%d')
        
        # 格式化更新时间
        if module.get('updated_at'):
            enhanced['updated_at_formatted'] = format_datetime(module['updated_at'])
            enhanced['updated_date'] = format_datetime(module['updated_at'], '%Y-%m-%d')
        
        return enhanced
    
    @staticmethod
    def _process_tags(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理标签
        
        Args:
            module (Dict[str, Any]): 模块数据
            
        Returns:
            Dict[str, Any]: 处理标签后的数据
        """
        enhanced = module.copy()
        
        # 解析标签字符串
        tags_str = safe_str(module.get('tags', ''))
        tags_list = parse_tags(tags_str)
        
        enhanced['tags_list'] = tags_list
        enhanced['tags_count'] = len(tags_list)
        enhanced['has_tags'] = len(tags_list) > 0
        
        # 添加标签分类
        enhanced['tag_categories'] = ModuleTransform._categorize_tags(tags_list)
        
        return enhanced
    
    @staticmethod
    def _add_status_display(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加状态显示
        
        Args:
            module (Dict[str, Any]): 模块数据
            
        Returns:
            Dict[str, Any]: 添加状态显示后的数据
        """
        enhanced = module.copy()
        
        status = safe_str(module.get('status', 'active'))
        status_map = {
            'active': {'display': '活跃', 'color': 'success', 'icon': 'check-circle'},
            'inactive': {'display': '非活跃', 'color': 'warning', 'icon': 'pause-circle'},
            'development': {'display': '开发中', 'color': 'info', 'icon': 'code'},
            'testing': {'display': '测试中', 'color': 'primary', 'icon': 'test-tube'},
            'production': {'display': '生产环境', 'color': 'success', 'icon': 'server'},
            'deprecated': {'display': '已废弃', 'color': 'danger', 'icon': 'archive'}
        }
        
        status_info = status_map.get(status, {
            'display': '未知', 
            'color': 'secondary', 
            'icon': 'question-circle'
        })
        
        enhanced['status_display'] = status_info['display']
        enhanced['status_color'] = status_info['color']
        enhanced['status_icon'] = status_info['icon']
        
        return enhanced
    
    @staticmethod
    def _add_computed_fields(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加计算字段
        
        Args:
            module (Dict[str, Any]): 模块数据
            
        Returns:
            Dict[str, Any]: 添加计算字段后的数据
        """
        enhanced = module.copy()
        
        # 计算描述长度
        description = safe_str(module.get('description', ''))
        enhanced['description_length'] = len(description)
        enhanced['has_description'] = len(description) > 0
        
        # 计算名称长度
        name = safe_str(module.get('name', ''))
        enhanced['name_length'] = len(name)
        
        # 添加搜索关键词
        enhanced['search_keywords'] = ModuleTransform._generate_search_keywords(module)
        
        return enhanced
    
    @staticmethod
    def _extract_summary_fields(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取摘要字段
        
        Args:
            module (Dict[str, Any]): 原始模块数据
            
        Returns:
            Dict[str, Any]: 摘要数据
        """
        return {
            'id': safe_int(module.get('id')),
            'name': safe_str(module.get('name')),
            'description': safe_str(module.get('description')),
            'status': safe_str(module.get('status', 'active')),
            'system_id': safe_int(module.get('system_id')),
            'tags': safe_str(module.get('tags', '')),
            'created_at': safe_str(module.get('created_at', ''))
        }
    
    @staticmethod
    def _infer_module_type(module_name: str) -> str:
        """
        基于模块名称推断模块类型
        
        Args:
            module_name (str): 模块名称
            
        Returns:
            str: 模块类型
        """
        if not module_name:
            return 'unknown'
        
        type_keywords = {
            'api': ['api', 'interface', 'endpoint'],
            'ui': ['ui', 'page', 'view', 'component'],
            'service': ['service', 'business', 'logic'],
            'data': ['data', 'database', 'model'],
            'util': ['util', 'helper', 'tool'],
            'test': ['test', 'spec', 'mock']
        }
        
        for module_type, keywords in type_keywords.items():
            if any(keyword in module_name for keyword in keywords):
                return module_type
        
        return 'general'
    
    @staticmethod
    def _calculate_priority(status: str) -> int:
        """
        基于状态计算优先级
        
        Args:
            status (str): 模块状态
            
        Returns:
            int: 优先级（数字越大优先级越高）
        """
        priority_map = {
            'production': 5,
            'active': 4,
            'testing': 3,
            'development': 2,
            'inactive': 1,
            'deprecated': 0
        }
        
        return priority_map.get(status, 1)
    
    @staticmethod
    def _categorize_tags(tags: List[str]) -> Dict[str, List[str]]:
        """
        标签分类
        
        Args:
            tags (List[str]): 标签列表
            
        Returns:
            Dict[str, List[str]]: 分类后的标签
        """
        categories = {
            'technology': [],
            'business': [],
            'environment': [],
            'other': []
        }
        
        tech_keywords = ['api', 'ui', 'backend', 'frontend', 'database', 'service']
        business_keywords = ['user', 'order', 'payment', 'product', 'customer']
        env_keywords = ['dev', 'test', 'prod', 'staging', 'local']
        
        for tag in tags:
            tag_lower = tag.lower()
            if any(keyword in tag_lower for keyword in tech_keywords):
                categories['technology'].append(tag)
            elif any(keyword in tag_lower for keyword in business_keywords):
                categories['business'].append(tag)
            elif any(keyword in tag_lower for keyword in env_keywords):
                categories['environment'].append(tag)
            else:
                categories['other'].append(tag)
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    @staticmethod
    def _generate_search_keywords(module: Dict[str, Any]) -> List[str]:
        """
        生成搜索关键词
        
        Args:
            module (Dict[str, Any]): 模块数据
            
        Returns:
            List[str]: 搜索关键词列表
        """
        keywords = []
        
        # 添加名称关键词
        name = safe_str(module.get('name', ''))
        if name:
            keywords.extend(name.split())
        
        # 添加描述关键词
        description = safe_str(module.get('description', ''))
        if description:
            keywords.extend(description.split())
        
        # 添加标签关键词
        tags = parse_tags(safe_str(module.get('tags', '')))
        keywords.extend(tags)
        
        # 去重并转为小写
        return list(set(keyword.lower() for keyword in keywords if keyword))
    
    @staticmethod
    def with_system_info(module: Dict[str, Any], system_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        添加系统信息到模块数据
        
        Args:
            module (Dict[str, Any]): 模块数据
            system_info (Optional[Dict[str, Any]]): 系统信息
            
        Returns:
            Dict[str, Any]: 包含系统信息的模块数据
        """
        enhanced = module.copy()
        
        if system_info:
            enhanced['system_name'] = safe_str(system_info.get('name', ''))
            enhanced['system_description'] = safe_str(system_info.get('description', ''))
            enhanced['system_status'] = safe_str(system_info.get('status', ''))
        
        return enhanced