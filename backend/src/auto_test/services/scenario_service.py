"""
场景服务层

负责场景数据的收集、组装和业务逻辑处理。
遵循防腐层设计原则，封装基础设施调用。

职责：
- 场景数据收集与组装
- 场景业务流程协调  
- 基础设施调用封装
- 统一异常处理
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from ..converters.scenario_converter import ScenarioConverter
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ScenarioService:
    """场景服务 - 防腐层"""
    
    @staticmethod
    def collect_scenario_stats_data() -> Dict[str, Any]:
        """收集场景统计数据"""
        try:
            # 暂时返回模拟数据，后续可扩展
            mock_data = {
                'total': 3,
                'active': 2,
                'success': 1,
                'failed': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            # 数据转换
            return ScenarioConverter.to_scenario_stats(mock_data)
            
        except Exception as e:
            logger.error(f"收集场景统计数据失败: {e}")
            return ScenarioConverter.to_default_scenario_stats()
    
    @staticmethod
    def collect_scenarios_data(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """收集场景数据（支持无分页与基础筛选）"""
        try:
            filters = filters or {}
            # 模拟数据，后续可替换为DAO查询
            scenarios_data = [
                {
                    'id': 101,
                    'name': '用户登录成功',
                    'description': '验证用户登录接口在正常凭证下返回200',
                    'status': 'active',
                    'scenario_type': 'normal',
                    'apiCount': 1,
                    'executionCount': 5,
                    'successRate': 100,
                    'lastExecutionTime': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'tags': ['auth', 'smoke'],
                    'is_parameters_saved': True,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'created_by': 'alice',
                    'apiIds': [2001]
                },
                {
                    'id': 102,
                    'name': '用户密码错误',
                    'description': '密码错误时返回401并包含错误码',
                    'status': 'active',
                    'scenario_type': 'exception',
                    'apiCount': 1,
                    'executionCount': 3,
                    'successRate': 100,
                    'lastExecutionTime': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'tags': ['auth'],
                    'is_parameters_saved': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'created_by': 'bob',
                    'apiIds': [2001]
                },
                {
                    'id': 103,
                    'name': '接口限流边界',
                    'description': '达到限流边界时返回429',
                    'status': 'inactive',
                    'scenario_type': 'boundary',
                    'apiCount': 2,
                    'executionCount': 0,
                    'successRate': 0,
                    'lastExecutionTime': None,
                    'version': '1.0.0',
                    'tags': ['rate-limit'],
                    'is_parameters_saved': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'created_by': 'alice',
                    'apiIds': [2002, 2003]
                }
            ]

            # 基础筛选
            def _match(item: Dict[str, Any]) -> bool:
                # api_id 筛选
                api_id = filters.get('api_id')
                if api_id is not None and api_id != "":
                    try:
                        api_id_int = int(api_id)
                        if api_id_int not in item.get('apiIds', []):
                            return False
                    except Exception:
                        # 非整数则忽略该筛选
                        pass

                keyword = (filters.get('keyword') or '').strip()
                if keyword:
                    if keyword.lower() not in (item.get('name', '') + item.get('description', '')).lower():
                        return False

                status = filters.get('status')
                if status and item.get('status') != status:
                    return False

                tags = filters.get('tags')
                if tags:
                    # 支持字符串逗号或列表
                    if isinstance(tags, str):
                        tag_list = [t for t in tags.split(',') if t]
                    else:
                        tag_list = list(tags) if isinstance(tags, list) else []
                    if tag_list and not set(tag_list).issubset(set(item.get('tags', []))):
                        return False

                created_by = filters.get('created_by')
                if created_by and item.get('created_by') != created_by:
                    return False

                is_params_saved = filters.get('is_parameters_saved')
                if is_params_saved is not None:
                    # 兼容字符串/布尔
                    if str(item.get('is_parameters_saved', False)).lower() != str(is_params_saved).lower():
                        return False

                # created_time_range 暂时忽略，示例数据不做时间过滤
                return True

            filtered = [s for s in scenarios_data if _match(s)]

            # 数据转换
            return ScenarioConverter.to_scenarios_list(filtered)
            
        except Exception as e:
            logger.error(f"收集场景数据失败: {e}")
            return []

    @staticmethod
    def get_creators(keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取创建人选项（示例数据）"""
        try:
            base = [
                {'label': 'Alice', 'value': 'alice'},
                {'label': 'Bob', 'value': 'bob'},
                {'label': 'Charlie', 'value': 'charlie'}
            ]
            if keyword:
                kw = keyword.strip().lower()
                return [u for u in base if kw in u['label'].lower() or kw in u['value'].lower()]
            return base
        except Exception as e:
            logger.error(f"获取创建人失败: {e}")
            return []