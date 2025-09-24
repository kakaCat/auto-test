"""
统计服务层

负责统计数据的收集、组装和业务逻辑处理。
遵循防腐层设计原则，封装基础设施调用。

职责：
- 数据收集与组装
- 业务流程协调  
- 基础设施调用封装
- 统一异常处理
"""

from typing import Dict, Any
from datetime import datetime

from .system_service import SystemService
from .module_service import ModuleService
from ..converters.stats_converter import StatsConverter
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StatsService:
    """统计服务 - 防腐层"""
    
    @staticmethod
    def collect_stats_data() -> Dict[str, Any]:
        """收集综合统计数据"""
        try:
            # 数据收集
            systems_data = SystemService.collect_systems_data()
            modules_data = ModuleService.collect_modules_data()
            
            # 数据组装
            stats_data = {
                'systems': systems_data,
                'modules': modules_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # 数据转换
            return StatsConverter.to_comprehensive_stats(stats_data)
            
        except Exception as e:
            logger.error(f"收集综合统计数据失败: {e}")
            return StatsConverter.to_default_stats()
    
    @staticmethod
    def collect_systems_stats_data() -> Dict[str, Any]:
        """收集系统统计数据"""
        try:
            # 数据收集
            systems_data = SystemService.collect_systems_data()
            
            # 数据转换
            return StatsConverter.to_systems_stats(systems_data)
            
        except Exception as e:
            logger.error(f"收集系统统计数据失败: {e}")
            return StatsConverter.to_default_systems_stats()
    
    @staticmethod
    def collect_modules_stats_data() -> Dict[str, Any]:
        """收集模块统计数据"""
        try:
            # 数据收集
            modules_data = ModuleService.collect_modules_data()
            
            # 数据转换
            return StatsConverter.to_modules_stats(modules_data)
            
        except Exception as e:
            logger.error(f"收集模块统计数据失败: {e}")
            return StatsConverter.to_default_modules_stats()
    
    @staticmethod
    def collect_workflows_stats_data() -> Dict[str, Any]:
        """收集工作流统计数据"""
        try:
            # 暂时返回默认数据，后续可扩展
            return StatsConverter.to_workflows_stats({})
            
        except Exception as e:
            logger.error(f"收集工作流统计数据失败: {e}")
            return StatsConverter.to_default_workflows_stats()
    
    @staticmethod
    def collect_scenarios_stats_data() -> Dict[str, Any]:
        """收集场景统计数据"""
        try:
            # 暂时返回默认数据，后续可扩展
            return StatsConverter.to_scenarios_stats({})
            
        except Exception as e:
            logger.error(f"收集场景统计数据失败: {e}")
            return StatsConverter.to_default_scenarios_stats()