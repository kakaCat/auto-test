"""
系统数据转换器
采用函数式编程风格，将DAO层原始数据转换为响应数据
"""

from typing import Dict, Any, List, Optional
from .utils import (
    pipe, format_datetime, safe_get, safe_int, safe_str, 
    create_key, add_field
)


class SystemTransform:
    """系统数据转换器 - 函数式编程风格"""
    
    @staticmethod
    def to_response(raw_system: Dict[str, Any]) -> Dict[str, Any]:
        """
        将DAO层原始数据转换为API响应数据
        
        Args:
            raw_system (Dict[str, Any]): DAO层原始系统数据
            
        Returns:
            Dict[str, Any]: 转换后的响应数据
        """
        if not raw_system:
            return {}
        
        return pipe(
            raw_system,
            SystemTransform._add_business_fields,
            SystemTransform._format_timestamps,
            SystemTransform._add_status_display,
            SystemTransform._add_computed_fields
        )
    
    @staticmethod
    def to_list_response(raw_systems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将DAO层原始数据列表转换为API响应数据列表
        
        Args:
            raw_systems (List[Dict[str, Any]]): DAO层原始系统数据列表
            
        Returns:
            List[Dict[str, Any]]: 转换后的响应数据列表
        """
        if not raw_systems:
            return []
        
        return [SystemTransform.to_response(system) for system in raw_systems]
    
    @staticmethod
    def to_summary(raw_system: Dict[str, Any]) -> Dict[str, Any]:
        """
        将DAO层原始数据转换为摘要数据
        
        Args:
            raw_system (Dict[str, Any]): DAO层原始系统数据
            
        Returns:
            Dict[str, Any]: 转换后的摘要数据
        """
        if not raw_system:
            return {}
        
        return pipe(
            raw_system,
            SystemTransform._extract_summary_fields,
            SystemTransform._add_status_display,
            SystemTransform._add_computed_fields
        )
    
    @staticmethod
    def with_module_count(system: Dict[str, Any], module_count: int = 0) -> Dict[str, Any]:
        """
        添加模块数量信息
        
        Args:
            system (Dict[str, Any]): 系统数据
            module_count (int): 模块数量
            
        Returns:
            Dict[str, Any]: 包含模块数量的系统数据
        """
        enhanced = system.copy()
        enhanced['module_count'] = module_count
        enhanced['has_modules'] = module_count > 0
        
        # 基于模块数量添加系统规模
        if module_count == 0:
            enhanced['system_scale'] = 'empty'
        elif module_count <= 5:
            enhanced['system_scale'] = 'small'
        elif module_count <= 20:
            enhanced['system_scale'] = 'medium'
        else:
            enhanced['system_scale'] = 'large'
        
        return enhanced
    
    @staticmethod
    def _add_business_fields(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加业务字段
        
        Args:
            system (Dict[str, Any]): 原始系统数据
            
        Returns:
            Dict[str, Any]: 添加业务字段后的数据
        """
        enhanced = system.copy()
        
        # 添加系统唯一键
        system_id = safe_int(system.get('id'))
        enhanced['system_key'] = create_key('SYS', system_id)
        
        # 添加活跃状态
        enhanced['is_active'] = system.get('status') == 'active'
        
        # 添加系统类型（基于名称推断）
        system_name = safe_str(system.get('name', '')).lower()
        enhanced['system_type'] = SystemTransform._infer_system_type(system_name)
        
        # 添加优先级（基于状态）
        enhanced['priority'] = SystemTransform._calculate_priority(system.get('status'))
        
        # 添加系统版本（如果有）
        enhanced['version'] = SystemTransform._extract_version(system.get('description', ''))
        
        return enhanced
    
    @staticmethod
    def _format_timestamps(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化时间戳
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            Dict[str, Any]: 格式化时间戳后的数据
        """
        enhanced = system.copy()
        
        # 格式化创建时间
        if system.get('created_at'):
            enhanced['created_at_formatted'] = format_datetime(system['created_at'])
            enhanced['created_date'] = format_datetime(system['created_at'], '%Y-%m-%d')
        
        # 格式化更新时间
        if system.get('updated_at'):
            enhanced['updated_at_formatted'] = format_datetime(system['updated_at'])
            enhanced['updated_date'] = format_datetime(system['updated_at'], '%Y-%m-%d')
        
        # 计算系统年龄（天数）
        if system.get('created_at'):
            from datetime import datetime
            try:
                created_date = datetime.fromisoformat(str(system['created_at']).replace('Z', '+00:00'))
                age_days = (datetime.now() - created_date).days
                enhanced['system_age_days'] = age_days
                enhanced['system_age_display'] = SystemTransform._format_age(age_days)
            except:
                enhanced['system_age_days'] = 0
                enhanced['system_age_display'] = '未知'
        
        return enhanced
    
    @staticmethod
    def _add_status_display(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加状态显示
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            Dict[str, Any]: 添加状态显示后的数据
        """
        enhanced = system.copy()
        
        status = safe_str(system.get('status', 'active'))
        status_map = {
            'enabled': {'display': '启用', 'color': 'success', 'icon': 'check-circle'},
            'disabled': {'display': '禁用', 'color': 'danger', 'icon': 'times-circle'},
            'active': {'display': '活跃', 'color': 'success', 'icon': 'check-circle'},
            'inactive': {'display': '非活跃', 'color': 'warning', 'icon': 'pause-circle'},
            'development': {'display': '开发中', 'color': 'info', 'icon': 'code'},
            'testing': {'display': '测试中', 'color': 'primary', 'icon': 'test-tube'},
            'production': {'display': '生产环境', 'color': 'success', 'icon': 'server'},
            'maintenance': {'display': '维护中', 'color': 'warning', 'icon': 'wrench'},
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
        
        # 添加enabled布尔字段供前端使用
        enhanced['enabled'] = status == 'active'
        
        return enhanced
    
    @staticmethod
    def _add_computed_fields(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加计算字段
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            Dict[str, Any]: 添加计算字段后的数据
        """
        enhanced = system.copy()
        
        # 计算描述长度
        description = safe_str(system.get('description', ''))
        enhanced['description_length'] = len(description)
        enhanced['has_description'] = len(description) > 0
        
        # 计算名称长度
        name = safe_str(system.get('name', ''))
        enhanced['name_length'] = len(name)
        
        # 添加搜索关键词
        enhanced['search_keywords'] = SystemTransform._generate_search_keywords(system)
        
        # 添加系统健康度评分
        enhanced['health_score'] = SystemTransform._calculate_health_score(system)
        
        return enhanced
    
    @staticmethod
    def _extract_summary_fields(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取摘要字段
        
        Args:
            system (Dict[str, Any]): 原始系统数据
            
        Returns:
            Dict[str, Any]: 摘要数据
        """
        return {
            'id': safe_int(system.get('id')),
            'name': safe_str(system.get('name')),
            'description': safe_str(system.get('description')),
            'status': safe_str(system.get('status', 'active')),
            'created_at': safe_str(system.get('created_at', ''))
        }
    
    @staticmethod
    def _infer_system_type(system_name: str) -> str:
        """
        基于系统名称推断系统类型
        
        Args:
            system_name (str): 系统名称
            
        Returns:
            str: 系统类型
        """
        if not system_name:
            return 'unknown'
        
        type_keywords = {
            'web': ['web', 'website', 'portal', 'frontend'],
            'api': ['api', 'service', 'backend', 'server'],
            'mobile': ['mobile', 'app', 'android', 'ios'],
            'desktop': ['desktop', 'client', 'application'],
            'database': ['database', 'db', 'data', 'storage'],
            'microservice': ['micro', 'service', 'ms'],
            'admin': ['admin', 'management', 'console'],
            'monitoring': ['monitor', 'log', 'metric', 'alert']
        }
        
        for system_type, keywords in type_keywords.items():
            if any(keyword in system_name for keyword in keywords):
                return system_type
        
        return 'general'
    
    @staticmethod
    def _calculate_priority(status: str) -> int:
        """
        基于状态计算优先级
        
        Args:
            status (str): 系统状态
            
        Returns:
            int: 优先级（数字越大优先级越高）
        """
        priority_map = {
            'production': 5,
            'active': 4,
            'testing': 3,
            'development': 2,
            'maintenance': 1,
            'inactive': 1,
            'deprecated': 0
        }
        
        return priority_map.get(status, 1)
    
    @staticmethod
    def _extract_version(description: str) -> str:
        """
        从描述中提取版本信息
        
        Args:
            description (str): 系统描述
            
        Returns:
            str: 版本号
        """
        import re
        
        if not description:
            return 'unknown'
        
        # 匹配版本号模式
        version_patterns = [
            r'v(\d+\.\d+\.\d+)',
            r'version\s+(\d+\.\d+\.\d+)',
            r'(\d+\.\d+\.\d+)',
            r'v(\d+\.\d+)',
            r'version\s+(\d+\.\d+)',
            r'(\d+\.\d+)'
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, description.lower())
            if match:
                return match.group(1)
        
        return 'unknown'
    
    @staticmethod
    def _format_age(age_days: int) -> str:
        """
        格式化系统年龄显示
        
        Args:
            age_days (int): 年龄天数
            
        Returns:
            str: 格式化的年龄显示
        """
        if age_days < 1:
            return '今天'
        elif age_days < 7:
            return f'{age_days}天'
        elif age_days < 30:
            weeks = age_days // 7
            return f'{weeks}周'
        elif age_days < 365:
            months = age_days // 30
            return f'{months}个月'
        else:
            years = age_days // 365
            return f'{years}年'
    
    @staticmethod
    def _generate_search_keywords(system: Dict[str, Any]) -> List[str]:
        """
        生成搜索关键词
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            List[str]: 搜索关键词列表
        """
        keywords = []
        
        # 添加名称关键词
        name = safe_str(system.get('name', ''))
        if name:
            keywords.extend(name.split())
        
        # 添加描述关键词
        description = safe_str(system.get('description', ''))
        if description:
            keywords.extend(description.split())
        
        # 添加状态关键词
        status = safe_str(system.get('status', ''))
        if status:
            keywords.append(status)
        
        # 去重并转为小写
        return list(set(keyword.lower() for keyword in keywords if keyword))
    
    @staticmethod
    def _calculate_health_score(system: Dict[str, Any]) -> int:
        """
        计算系统健康度评分
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            int: 健康度评分 (0-100)
        """
        score = 50  # 基础分数
        
        # 状态评分
        status = safe_str(system.get('status', 'active'))
        status_scores = {
            'production': 30,
            'active': 25,
            'testing': 15,
            'development': 10,
            'maintenance': 5,
            'inactive': -10,
            'deprecated': -20
        }
        score += status_scores.get(status, 0)
        
        # 描述完整性评分
        description = safe_str(system.get('description', ''))
        if len(description) > 50:
            score += 10
        elif len(description) > 20:
            score += 5
        
        # 名称规范性评分
        name = safe_str(system.get('name', ''))
        if len(name) > 3 and not name.isdigit():
            score += 10
        
        # 确保分数在0-100范围内
        return max(0, min(100, score))