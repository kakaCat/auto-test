"""
模块业务服务层
处理模块相关的业务逻辑和数据转换
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..database.dao import ModuleDAO, SystemDAO
from ..transforms import ModuleTransform
from ..models.module import ModuleCreate, ModuleUpdate

logger = logging.getLogger(__name__)


class ModuleService:
    """模块业务服务类"""
    
    @staticmethod
    def get_modules(system_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取模块列表
        
        Args:
            system_id (Optional[int]): 系统ID，如果提供则筛选该系统的模块
            
        Returns:
            List[Dict[str, Any]]: 模块列表
        """
        try:
            logger.info(f"获取模块列表，系统ID: {system_id}")
            
            # 调用DAO层获取原始数据
            if system_id:
                raw_modules = ModuleDAO.get_modules_by_system(system_id)
            else:
                raw_modules = ModuleDAO.get_all_modules()
            
            # 使用Transform层转换数据
            transformed_modules = ModuleTransform.to_list_response(raw_modules)
            
            # 应用业务规则
            processed_modules = []
            for module in transformed_modules:
                # 应用业务验证和增强
                processed_module = ModuleService._apply_business_rules(module)
                processed_modules.append(processed_module)
            
            logger.info(f"成功获取 {len(processed_modules)} 个模块")
            return processed_modules
            
        except Exception as e:
            logger.error(f"获取模块列表失败: {str(e)}")
            raise Exception(f"获取模块列表失败: {str(e)}")
    
    @staticmethod
    def _apply_business_rules(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用业务规则和验证
        
        Args:
            module (Dict[str, Any]): 转换后的模块数据
            
        Returns:
            Dict[str, Any]: 应用业务规则后的模块数据
        """
        enhanced = module.copy()
        
        # 业务规则1: 检查模块状态有效性
        if enhanced.get('status') not in ['active', 'inactive', 'development', 'testing', 'production', 'deprecated']:
            enhanced['status'] = 'active'  # 默认状态
        
        # 业务规则2: 确保模块名称不为空
        if not enhanced.get('name') or not enhanced.get('name').strip():
            enhanced['name'] = f"模块_{enhanced.get('id', 'unknown')}"
        
        # 业务规则3: 添加权限检查标识
        enhanced['can_edit'] = enhanced.get('status') != 'deprecated'
        enhanced['can_delete'] = enhanced.get('status') in ['inactive', 'development']
        
        # 业务规则4: 添加风险评估
        enhanced['risk_level'] = ModuleService._assess_risk_level(enhanced)
        
        return enhanced
    
    @staticmethod
    def _assess_risk_level(module: Dict[str, Any]) -> str:
        """
        评估模块风险等级
        
        Args:
            module (Dict[str, Any]): 模块数据
            
        Returns:
            str: 风险等级 (low, medium, high)
        """
        risk_score = 0
        
        # 基于状态评估风险
        status = module.get('status', 'active')
        if status == 'production':
            risk_score += 3
        elif status == 'testing':
            risk_score += 2
        elif status == 'development':
            risk_score += 1
        
        # 基于模块年龄评估风险
        age_days = module.get('system_age_days', 0)
        if age_days > 365:
            risk_score += 2
        elif age_days > 180:
            risk_score += 1
        
        # 基于描述完整性评估风险
        if not module.get('has_description', False):
            risk_score += 1
        
        # 返回风险等级
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_module_by_id(module_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取模块详情
        
        Args:
            module_id (int): 模块ID
            
        Returns:
            Optional[Dict[str, Any]]: 模块详情，包含业务转换后的数据
        """
        try:
            module = ModuleDAO.get_by_id(module_id)
            if module:
                return ModuleService._transform_module_output(module)
            return None
        except Exception as e:
            logger.error(f"获取模块详情失败: {str(e)}")
            raise
    
    @staticmethod
    def create_module(module_data: ModuleCreate) -> Dict[str, Any]:
        """
        创建新模块
        
        Args:
            module_data (ModuleCreate): 模块创建数据
            
        Returns:
            Dict[str, Any]: 创建的模块信息
        """
        try:
            # 业务规则验证
            if not SystemDAO.get_by_id(module_data.system_id):
                raise ValueError(f"系统ID {module_data.system_id} 不存在")
            
            if ModuleService._is_module_name_exists_in_system(module_data.name, module_data.system_id):
                raise ValueError(f"系统中已存在名称为 '{module_data.name}' 的模块")
            
            # 创建模块
            module_id = ModuleDAO.create(
                module_data.system_id, 
                module_data.name, 
                module_data.description, 
                module_data.tags,
                module_data.path
            )
            created_module = ModuleDAO.get_by_id(module_id)
            
            logger.info(f"模块创建成功: {module_data.name} (ID: {module_id})")
            return ModuleService._transform_module_output(created_module)
        except Exception as e:
            logger.error(f"创建模块失败: {str(e)}")
            raise
    
    @staticmethod
    def update_module(module_id: int, module_data: ModuleUpdate) -> Optional[Dict[str, Any]]:
        """
        更新模块信息
        
        Args:
            module_id (int): 模块ID
            module_data (ModuleUpdate): 模块更新数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的模块信息
        """
        try:
            # 检查模块是否存在
            existing_module = ModuleDAO.get_by_id(module_id)
            if not existing_module:
                return None
            
            # 业务规则验证
            if module_data.system_id and not SystemDAO.get_by_id(module_data.system_id):
                raise ValueError(f"系统ID {module_data.system_id} 不存在")
            
            # 检查模块名称在系统中是否重复
            check_system_id = module_data.system_id or existing_module.get('system_id')
            if (module_data.name and 
                module_data.name != existing_module.get('name') and
                ModuleService._is_module_name_exists_in_system(module_data.name, check_system_id)):
                raise ValueError(f"系统中已存在名称为 '{module_data.name}' 的模块")
            
            # 更新模块
            success = ModuleDAO.update(module_id, module_data)
            if success:
                updated_module = ModuleDAO.get_by_id(module_id)
                logger.info(f"模块更新成功: ID {module_id}")
                return ModuleService._transform_module_output(updated_module)
            return None
        except Exception as e:
            logger.error(f"更新模块失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_module(module_id: int) -> bool:
        """
        删除模块
        
        Args:
            module_id (int): 模块ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查模块是否存在
            existing_module = ModuleDAO.get_by_id(module_id)
            if not existing_module:
                return False
            
            # 删除模块
            success = ModuleDAO.delete(module_id)
            if success:
                logger.info(f"模块删除成功: ID {module_id}")
            return success
        except Exception as e:
            logger.error(f"删除模块失败: {str(e)}")
            raise
    
    @staticmethod
    def get_all_tags() -> List[str]:
        """
        获取所有模块标签
        
        Returns:
            List[str]: 标签列表
        """
        try:
            tags = ModuleDAO.get_all_tags()
            logger.info(f"获取所有标签，共 {len(tags)} 个")
            return tags
        except Exception as e:
            logger.error(f"获取标签列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_module_statistics() -> Dict[str, Any]:
        """
        获取模块统计信息
        
        Returns:
            Dict[str, Any]: 统计信息，包含业务转换后的数据
        """
        try:
            stats = ModuleDAO.get_statistics()
            
            # 添加业务统计信息
            enhanced_stats = stats.copy()
            
            # 添加状态分布
            all_modules = ModuleDAO.get_all()
            status_distribution = {}
            for module in all_modules:
                status = module.get('status', 'active')
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            enhanced_stats['status_distribution'] = status_distribution
            
            # 添加标签统计
            all_tags = ModuleDAO.get_all_tags()
            enhanced_stats['total_tags'] = len(all_tags)
            enhanced_stats['popular_tags'] = all_tags[:10]  # 前10个标签
            
            logger.info("获取模块统计信息成功")
            return enhanced_stats
        except Exception as e:
            logger.error(f"获取模块统计信息失败: {str(e)}")
            raise
    
    @staticmethod
    def _transform_module_output(module: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换模块输出格式，添加业务字段
        
        Args:
            module (Dict[str, Any]): 原始模块数据
            
        Returns:
            Dict[str, Any]: 转换后的模块数据
        """
        if not module:
            return module
        
        # 添加业务字段
        transformed = module.copy()
        
        # 添加状态描述
        status_map = {
            'active': '活跃',
            'inactive': '非活跃',
            'development': '开发中',
            'testing': '测试中',
            'production': '生产环境'
        }
        transformed['status_display'] = status_map.get(module.get('status', 'active'), '未知')
        
        # 添加系统信息
        if module.get('system_id'):
            try:
                system = SystemDAO.get_by_id(module['system_id'])
                if system:
                    transformed['system_name'] = system.get('name', '')
                    transformed['system_description'] = system.get('description', '')
            except Exception:
                pass
        
        # 处理标签
        tags = module.get('tags', '')
        if isinstance(tags, str) and tags:
            transformed['tags_list'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
        else:
            transformed['tags_list'] = []
        
        # 添加创建时间格式化
        if module.get('created_at'):
            try:
                created_at = datetime.fromisoformat(module['created_at'].replace('Z', '+00:00'))
                transformed['created_at_formatted'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
            except:
                transformed['created_at_formatted'] = module.get('created_at', '')
        
        # 添加更新时间格式化
        if module.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(module['updated_at'].replace('Z', '+00:00'))
                transformed['updated_at_formatted'] = updated_at.strftime('%Y-%m-%d %H:%M:%S')
            except:
                transformed['updated_at_formatted'] = module.get('updated_at', '')
        
        return transformed
    
    @staticmethod
    def collect_modules_data(page: int = 1, size: int = 10, search: Optional[str] = None, status: Optional[str] = None, system_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        收集模块数据 - 支持分页和筛选
        
        Args:
            page: 页码
            size: 每页数量
            search: 搜索关键词
            status: 状态筛选
            system_id: 系统ID筛选
            
        Returns:
            List[Dict[str, Any]]: 模块数据列表
        """
        try:
            # 获取所有模块数据
            modules = ModuleService.get_modules(system_id)
            
            # 应用筛选条件
            if status:
                modules = [m for m in modules if m.get('status') == status]
            
            if search:
                modules = [m for m in modules if search.lower() in m.get('name', '').lower() or search.lower() in m.get('description', '').lower()]
            
            # 应用分页
            start = (page - 1) * size
            end = start + size
            
            return modules[start:end]
            
        except Exception as e:
            logger.error(f"收集模块数据失败: {e}")
            return []

    @staticmethod
    def _is_module_name_exists_in_system(name: str, system_id: int) -> bool:
        """
        检查模块名称在指定系统中是否已存在
        
        Args:
            name (str): 模块名称
            system_id (int): 系统ID
            
        Returns:
            bool: 名称是否已存在
        """
        try:
            modules = ModuleDAO.get_by_system_id(system_id)
            return any(module.get('name') == name for module in modules)
        except Exception:
            return False