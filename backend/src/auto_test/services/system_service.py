"""
系统业务层
处理系统相关的业务逻辑和数据转换
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database.dao import SystemDAO, ModuleDAO, SystemCategoryDAO
from ..models.system import System, SystemCreate, SystemUpdate
from ..utils.logger import get_logger
from ..transforms import SystemTransform

logger = get_logger(__name__)


class SystemService:
    """系统业务服务类"""
    
    @staticmethod
    def get_systems() -> List[Dict[str, Any]]:
        """
        获取所有系统列表
        
        Returns:
            List[Dict[str, Any]]: 系统列表，包含业务转换后的数据
        """
        try:
            # 调用DAO层获取原始数据
            raw_systems = SystemDAO.get_all()
            logger.info(f"获取所有系统列表，共 {len(raw_systems)} 个系统")
            
            # 使用Transform层转换数据
            transformed_systems = SystemTransform.to_list_response(raw_systems)
            
            # 为每个系统添加模块数量统计和业务规则
            enhanced_systems = []
            for system in transformed_systems:
                # 获取该系统的模块数量
                module_count = ModuleDAO.count_by_system_id(system.get('id', 0))
                # 添加模块数量信息
                enhanced_system = SystemTransform.with_module_count(system, module_count)
                # 应用业务规则
                enhanced_system = SystemService._apply_business_rules(enhanced_system)
                enhanced_systems.append(enhanced_system)
            
            return enhanced_systems
            
        except Exception as e:
            logger.error(f"获取系统列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_system_by_id(system_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取系统详情
        
        Args:
            system_id (int): 系统ID
            
        Returns:
            Optional[Dict[str, Any]]: 系统详情，包含业务转换后的数据
        """
        try:
            system = SystemDAO.get_by_id(system_id)
            if system:
                return SystemService._transform_system_output(system)
            return None
        except Exception as e:
            logger.error(f"获取系统详情失败: {str(e)}")
            raise
    
    @staticmethod
    def create_system(system_data: SystemCreate) -> Dict[str, Any]:
        """
        创建新系统
        
        Args:
            system_data (SystemCreate): 系统创建数据
            
        Returns:
            Dict[str, Any]: 创建的系统信息
        """
        try:
            # 业务规则验证
            if SystemService._is_system_name_exists(system_data.name):
                raise ValueError(f"系统名称 '{system_data.name}' 已存在")
            
            # 创建系统
            system_id = SystemDAO.create(system_data.name, system_data.description)
            created_system = SystemDAO.get_by_id(system_id)
            
            logger.info(f"系统创建成功: {system_data.name} (ID: {system_id})")
            return SystemService._transform_system_output(created_system)
        except Exception as e:
            logger.error(f"创建系统失败: {str(e)}")
            raise
    
    @staticmethod
    def update_system(system_id: int, system_data: SystemUpdate) -> Optional[Dict[str, Any]]:
        """
        更新系统信息
        
        Args:
            system_id (int): 系统ID
            system_data (SystemUpdate): 系统更新数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的系统信息
        """
        try:
            # 检查系统是否存在
            existing_system = SystemDAO.get_by_id(system_id)
            if not existing_system:
                return None
            
            # 业务规则验证
            if (system_data.name and 
                system_data.name != existing_system.get('name') and
                SystemService._is_system_name_exists(system_data.name)):
                raise ValueError(f"系统名称 '{system_data.name}' 已存在")
            
            # 更新系统
            success = SystemDAO.update(
                system_id, 
                name=system_data.name,
                description=system_data.description,
                status=system_data.status
            )
            if success:
                updated_system = SystemDAO.get_by_id(system_id)
                logger.info(f"系统更新成功: ID {system_id}")
                return SystemService._transform_system_output(updated_system)
            return None
        except Exception as e:
            logger.error(f"更新系统失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_system(system_id: int) -> bool:
        """
        删除系统
        
        Args:
            system_id (int): 系统ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查系统是否存在
            existing_system = SystemDAO.get_by_id(system_id)
            if not existing_system:
                return False
            
            # 业务规则：检查是否有关联的模块
            from ..database.dao import ModuleDAO
            modules = ModuleDAO.get_by_system_id(system_id)
            if modules:
                raise ValueError(f"无法删除系统，存在 {len(modules)} 个关联模块")
            
            # 删除系统
            success = SystemDAO.delete(system_id)
            if success:
                logger.info(f"系统删除成功: ID {system_id}")
            return success
        except Exception as e:
            logger.error(f"删除系统失败: {str(e)}")
            raise
    
    @staticmethod
    def _transform_system_output(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换系统输出格式，添加业务字段
        
        Args:
            system (Dict[str, Any]): 原始系统数据
            
        Returns:
            Dict[str, Any]: 转换后的系统数据
        """
        if not system:
            return system
        
        # 添加业务字段
        transformed = system.copy()
        
        # 添加状态描述
        status_map = {
            'active': '活跃',
            'inactive': '非活跃',
            'maintenance': '维护中'
        }
        transformed['status_display'] = status_map.get(system.get('status', 'active'), '未知')
        
        # 添加创建时间格式化
        if system.get('created_at'):
            try:
                created_at = datetime.fromisoformat(system['created_at'].replace('Z', '+00:00'))
                transformed['created_at_formatted'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
            except:
                transformed['created_at_formatted'] = system.get('created_at', '')
        
        # 添加更新时间格式化
        if system.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(system['updated_at'].replace('Z', '+00:00'))
                transformed['updated_at_formatted'] = updated_at.strftime('%Y-%m-%d %H:%M:%S')
            except:
                transformed['updated_at_formatted'] = system.get('updated_at', '')
        
        return transformed
    
    @staticmethod
    def _apply_business_rules(system: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用业务规则和验证
        
        Args:
            system (Dict[str, Any]): 转换后的系统数据
            
        Returns:
            Dict[str, Any]: 应用业务规则后的系统数据
        """
        enhanced = system.copy()
        
        # 业务规则1: 检查系统状态有效性
        valid_statuses = ['active', 'inactive', 'development', 'testing', 'production', 'maintenance', 'deprecated']
        if enhanced.get('status') not in valid_statuses:
            enhanced['status'] = 'active'  # 默认状态
        
        # 业务规则2: 确保系统名称不为空
        if not enhanced.get('name') or not enhanced.get('name').strip():
            enhanced['name'] = f"系统_{enhanced.get('id', 'unknown')}"
        
        # 业务规则3: 添加权限检查标识
        enhanced['can_edit'] = enhanced.get('status') != 'deprecated'
        enhanced['can_delete'] = enhanced.get('status') in ['inactive', 'development'] and enhanced.get('module_count', 0) == 0
        
        # 业务规则4: 添加系统重要性评估
        enhanced['importance_level'] = SystemService._assess_importance_level(enhanced)
        
        # 业务规则5: 添加系统状态建议
        enhanced['status_recommendation'] = SystemService._get_status_recommendation(enhanced)
        
        return enhanced
    
    @staticmethod
    def _assess_importance_level(system: Dict[str, Any]) -> str:
        """
        评估系统重要性等级
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            str: 重要性等级 (low, medium, high, critical)
        """
        importance_score = 0
        
        # 基于状态评估重要性
        status = system.get('status', 'active')
        if status == 'production':
            importance_score += 4
        elif status == 'testing':
            importance_score += 2
        elif status == 'active':
            importance_score += 3
        
        # 基于模块数量评估重要性
        module_count = system.get('module_count', 0)
        if module_count > 20:
            importance_score += 3
        elif module_count > 10:
            importance_score += 2
        elif module_count > 5:
            importance_score += 1
        
        # 基于系统年龄评估重要性
        age_days = system.get('system_age_days', 0)
        if age_days > 365:
            importance_score += 2
        elif age_days > 180:
            importance_score += 1
        
        # 返回重要性等级
        if importance_score >= 7:
            return 'critical'
        elif importance_score >= 5:
            return 'high'
        elif importance_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _get_status_recommendation(system: Dict[str, Any]) -> str:
        """
        获取系统状态建议
        
        Args:
            system (Dict[str, Any]): 系统数据
            
        Returns:
            str: 状态建议
        """
        status = system.get('status', 'active')
        module_count = system.get('module_count', 0)
        age_days = system.get('system_age_days', 0)
        
        if status == 'development' and age_days > 90:
            return '建议推进到测试阶段'
        elif status == 'testing' and age_days > 30:
            return '建议推进到生产环境'
        elif status == 'active' and module_count == 0:
            return '建议添加模块或考虑归档'
        elif status == 'inactive' and age_days > 180:
            return '建议考虑废弃或重新激活'
        else:
            return '状态正常'
    
    @staticmethod
    def _is_system_name_exists(name: str) -> bool:
        """
        检查系统名称是否已存在
        
        Args:
            name (str): 系统名称
            
        Returns:
            bool: 名称是否已存在
        """
        try:
            systems = SystemDAO.get_all()
            return any(system.get('name') == name for system in systems)
        except Exception as e:
            logger.error(f"检查系统名称是否存在时发生错误: {e}")
            return False
    
    @staticmethod
    def collect_systems_data(page: int = 1, size: int = 10, search: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        收集系统数据 - 支持分页和筛选
        
        Args:
            page: 页码
            size: 每页数量
            search: 搜索关键词
            status: 状态筛选
            
        Returns:
            List[Dict[str, Any]]: 系统数据列表
        """
        try:
            # 获取所有系统数据
            systems = SystemService.get_systems()
            
            # 应用筛选条件
            if status:
                systems = [s for s in systems if s.get('status') == status]
            
            if search:
                systems = [s for s in systems if search.lower() in s.get('name', '').lower() or search.lower() in s.get('description', '').lower()]
            
            # 应用分页
            start = (page - 1) * size
            end = start + size
            
            return systems[start:end]
            
        except Exception as e:
            logger.error(f"收集系统数据失败: {e}")
            return []
    
    @staticmethod
    def collect_categories_data() -> List[Dict[str, Any]]:
        """
        收集系统分类数据
        
        Returns:
            List[Dict[str, Any]]: 系统分类列表，包含code和name
        """
        try:
            # 从system_categories表获取所有分类
            categories = SystemCategoryDAO.get_all()
            logger.info(f"获取系统分类成功，共 {len(categories)} 个分类")
            return categories
            
        except Exception as e:
            logger.error(f"收集系统分类数据失败: {e}")
            return []