"""AI编排模块数据访问对象

提供AI编排相关的数据库操作，包括：
- MCP工具配置管理
- AI执行记录管理
- 编排计划管理
- 执行步骤和日志管理
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .dao import get_db_cursor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MCPToolConfigDAO:
    """MCP工具配置数据访问对象"""
    
    @staticmethod
    def create_or_update(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建或更新工具配置"""
        try:
            with get_db_cursor() as cursor:
                tool_name = config_data['tool_name']
                
                # 检查是否已存在
                cursor.execute(
                    "SELECT id FROM mcp_tool_configs WHERE tool_name = ?",
                    (tool_name,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # 更新
                    cursor.execute("""
                        UPDATE mcp_tool_configs 
                        SET tool_type = ?, schema_definition = ?, is_enabled = ?, 
                            config_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE tool_name = ?
                    """, (
                        config_data['tool_type'],
                        config_data['schema_definition'],
                        config_data['is_enabled'],
                        config_data.get('config_data'),
                        tool_name
                    ))
                    config_id = existing['id']
                else:
                    # 创建
                    config_id = int(datetime.now().timestamp() * 1000000)  # 微秒时间戳作为ID
                    cursor.execute("""
                        INSERT INTO mcp_tool_configs 
                        (id, tool_name, tool_type, schema_definition, is_enabled, config_data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        config_id,
                        tool_name,
                        config_data['tool_type'],
                        config_data['schema_definition'],
                        config_data['is_enabled'],
                        config_data.get('config_data')
                    ))
                
                # 返回完整记录
                cursor.execute("SELECT * FROM mcp_tool_configs WHERE id = ?", (config_id,))
                return dict(cursor.fetchone())
                
        except Exception as e:
            logger.error(f"创建/更新MCP工具配置失败: {e}")
            raise
    
    @staticmethod
    def get_all_enabled() -> List[Dict[str, Any]]:
        """获取所有启用的工具配置"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM mcp_tool_configs 
                    WHERE is_enabled = 1 
                    ORDER BY tool_name
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取启用的工具配置失败: {e}")
            raise
    
    @staticmethod
    def get_by_name(tool_name: str) -> Optional[Dict[str, Any]]:
        """根据工具名称获取配置"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM mcp_tool_configs WHERE tool_name = ?",
                    (tool_name,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取工具配置失败: {e}")
            raise


class AIExecutionDAO:
    """AI执行记录数据访问对象"""
    
    @staticmethod
    def create_execution(execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建执行记录"""
        try:
            with get_db_cursor() as cursor:
                execution_id = execution_data['execution_id']
                exec_record_id = int(datetime.now().timestamp() * 1000000)
                
                cursor.execute("""
                    INSERT INTO ai_executions 
                    (id, execution_id, agent_type, input_data, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    exec_record_id,
                    execution_id,
                    execution_data['agent_type'],
                    json.dumps(execution_data['input_data'], ensure_ascii=False),
                    execution_data.get('status', 'pending')
                ))
                
                # 返回创建的记录
                cursor.execute("SELECT * FROM ai_executions WHERE id = ?", (exec_record_id,))
                return dict(cursor.fetchone())
                
        except Exception as e:
            logger.error(f"创建AI执行记录失败: {e}")
            raise
    
    @staticmethod
    def update_execution(execution_id: str, update_data: Dict[str, Any]) -> bool:
        """更新执行记录"""
        try:
            with get_db_cursor() as cursor:
                set_clauses = []
                params = []
                
                for key, value in update_data.items():
                    if key in ['status', 'error_message']:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)
                    elif key == 'output_data':
                        set_clauses.append("output_data = ?")
                        params.append(json.dumps(value, ensure_ascii=False))
                    elif key == 'end_time':
                        set_clauses.append("end_time = CURRENT_TIMESTAMP")
                
                if set_clauses:
                    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(execution_id)
                    
                    cursor.execute(f"""
                        UPDATE ai_executions 
                        SET {', '.join(set_clauses)}
                        WHERE execution_id = ?
                    """, params)
                    
                    return cursor.rowcount > 0
                
                return False
                
        except Exception as e:
            logger.error(f"更新AI执行记录失败: {e}")
            raise
    
    @staticmethod
    def get_by_execution_id(execution_id: str) -> Optional[Dict[str, Any]]:
        """根据执行ID获取记录"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM ai_executions WHERE execution_id = ?",
                    (execution_id,)
                )
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    # 解析JSON字段
                    if result.get('input_data'):
                        result['input_data'] = json.loads(result['input_data'])
                    if result.get('output_data'):
                        result['output_data'] = json.loads(result['output_data'])
                    return result
                return None
        except Exception as e:
            logger.error(f"获取AI执行记录失败: {e}")
            raise


class OrchestrationPlanDAO:
    """编排计划数据访问对象"""
    
    @staticmethod
    def create_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建编排计划"""
        try:
            with get_db_cursor() as cursor:
                plan_id = int(datetime.now().timestamp() * 1000000)
                
                cursor.execute("""
                    INSERT INTO api_orchestration_plans 
                    (id, plan_name, description, intent_text, execution_plan, 
                     graph_json, metadata, preferences, status, tags, created_by, is_template)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    plan_id,
                    plan_data['plan_name'],
                    plan_data.get('description'),
                    plan_data['intent_text'],
                    json.dumps(plan_data['execution_plan'], ensure_ascii=False),
                    json.dumps(plan_data.get('graph_json'), ensure_ascii=False) if plan_data.get('graph_json') else None,
                    json.dumps(plan_data.get('metadata'), ensure_ascii=False) if plan_data.get('metadata') else None,
                    json.dumps(plan_data.get('preferences'), ensure_ascii=False) if plan_data.get('preferences') else None,
                    plan_data.get('status', 'draft'),
                    json.dumps(plan_data.get('tags'), ensure_ascii=False) if plan_data.get('tags') else None,
                    plan_data.get('created_by'),
                    plan_data.get('is_template', False)
                ))
                
                # 返回创建的记录
                cursor.execute("SELECT * FROM api_orchestration_plans WHERE id = ?", (plan_id,))
                return dict(cursor.fetchone())
                
        except Exception as e:
            logger.error(f"创建编排计划失败: {e}")
            raise
    
    @staticmethod
    def get_by_id(plan_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取编排计划"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT * FROM api_orchestration_plans WHERE id = ?", (plan_id,))
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    # 解析JSON字段
                    json_fields = ['execution_plan', 'graph_json', 'metadata', 'preferences', 'tags']
                    for field in json_fields:
                        if result.get(field):
                            result[field] = json.loads(result[field])
                    return result
                return None
        except Exception as e:
            logger.error(f"获取编排计划失败: {e}")
            raise
    
    @staticmethod
    def search_plans(filters: Dict[str, Any], page: int = 1, size: int = 10) -> List[Dict[str, Any]]:
        """搜索编排计划"""
        try:
            with get_db_cursor() as cursor:
                where_conditions = []
                params = []
                
                # 构建筛选条件
                if filters.get('keyword'):
                    where_conditions.append("(plan_name LIKE ? OR description LIKE ?)")
                    keyword = f"%{filters['keyword']}%"
                    params.extend([keyword, keyword])
                
                if filters.get('status'):
                    where_conditions.append("status = ?")
                    params.append(filters['status'])
                
                if filters.get('created_by'):
                    where_conditions.append("created_by = ?")
                    params.append(filters['created_by'])
                
                if filters.get('is_template') is not None:
                    where_conditions.append("is_template = ?")
                    params.append(filters['is_template'])
                
                # 构建查询
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                offset = (page - 1) * size
                
                cursor.execute(f"""
                    SELECT * FROM api_orchestration_plans 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, params + [size, offset])
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    # 解析JSON字段
                    json_fields = ['execution_plan', 'graph_json', 'metadata', 'preferences', 'tags']
                    for field in json_fields:
                        if result.get(field):
                            try:
                                result[field] = json.loads(result[field])
                            except json.JSONDecodeError:
                                result[field] = None
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"搜索编排计划失败: {e}")
            raise


class ExecutionStepDAO:
    """执行步骤数据访问对象"""
    
    @staticmethod
    def create_step(step_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建执行步骤"""
        try:
            with get_db_cursor() as cursor:
                step_record_id = int(datetime.now().timestamp() * 1000000)
                
                cursor.execute("""
                    INSERT INTO execution_steps 
                    (id, execution_id, step_id, step_name, step_type, status,
                     input_data, system_id, module_id, api_interface_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    step_record_id,
                    step_data['execution_id'],
                    step_data['step_id'],
                    step_data['step_name'],
                    step_data['step_type'],
                    step_data.get('status', 'pending'),
                    json.dumps(step_data.get('input_data'), ensure_ascii=False) if step_data.get('input_data') else None,
                    step_data.get('system_id'),
                    step_data.get('module_id'),
                    step_data.get('api_interface_id')
                ))
                
                # 返回创建的记录
                cursor.execute("SELECT * FROM execution_steps WHERE id = ?", (step_record_id,))
                return dict(cursor.fetchone())
                
        except Exception as e:
            logger.error(f"创建执行步骤失败: {e}")
            raise
    
    @staticmethod
    def update_step(step_id: str, update_data: Dict[str, Any]) -> bool:
        """更新执行步骤"""
        try:
            with get_db_cursor() as cursor:
                set_clauses = []
                params = []
                
                for key, value in update_data.items():
                    if key in ['status', 'error_message', 'retry_count']:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)
                    elif key in ['output_data']:
                        set_clauses.append(f"{key} = ?")
                        params.append(json.dumps(value, ensure_ascii=False))
                    elif key == 'start_time':
                        set_clauses.append("start_time = CURRENT_TIMESTAMP")
                    elif key == 'end_time':
                        set_clauses.append("end_time = CURRENT_TIMESTAMP")
                
                if set_clauses:
                    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(step_id)
                    
                    cursor.execute(f"""
                        UPDATE execution_steps 
                        SET {', '.join(set_clauses)}
                        WHERE step_id = ?
                    """, params)
                    
                    return cursor.rowcount > 0
                
                return False
                
        except Exception as e:
            logger.error(f"更新执行步骤失败: {e}")
            raise
    
    @staticmethod
    def get_steps_by_execution(execution_id: str) -> List[Dict[str, Any]]:
        """获取执行的所有步骤"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT s.*, sys.name as system_name, mod.name as module_name, 
                           api.name as api_name
                    FROM execution_steps s
                    LEFT JOIN management_systems sys ON s.system_id = sys.id
                    LEFT JOIN service_modules mod ON s.module_id = mod.id
                    LEFT JOIN api_interfaces api ON s.api_interface_id = api.id
                    WHERE s.execution_id = ?
                    ORDER BY s.created_at
                """, (execution_id,))
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    # 解析JSON字段
                    if result.get('input_data'):
                        result['input_data'] = json.loads(result['input_data'])
                    if result.get('output_data'):
                        result['output_data'] = json.loads(result['output_data'])
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"获取执行步骤失败: {e}")
            raise