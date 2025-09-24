"""
数据访问层 - 极简版
Data Access Object - Simplified

提供简化的数据库操作接口
"""

import logging
from typing import List, Dict, Any, Optional
from .connection import get_db_cursor

logger = logging.getLogger(__name__)

class SystemDAO:
    """系统数据访问对象"""
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """获取所有系统"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, description, category, status, created_at, updated_at 
                    FROM systems 
                    ORDER BY created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取系统列表失败: {e}")
            raise
    
    @staticmethod
    def get_by_id(system_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取系统"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, description, category, status, created_at, updated_at 
                    FROM systems 
                    WHERE id = ?
                """, (system_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取系统详情失败: {e}")
            raise
    
    @staticmethod
    def create(name: str, description: str = None) -> int:
        """创建系统"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO systems (name, description) 
                    VALUES (?, ?)
                """, (name, description))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"创建系统失败: {e}")
            raise
    
    @staticmethod
    def update(system_id: int, name: str = None, description: str = None, status: str = None) -> bool:
        """更新系统"""
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(system_id)
            
            with get_db_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE systems 
                    SET {', '.join(updates)} 
                    WHERE id = ?
                """, params)
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新系统失败: {e}")
            raise
    
    @staticmethod
    def delete(system_id: int) -> bool:
        """删除系统"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM systems WHERE id = ?", (system_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除系统失败: {e}")
            raise

class SystemCategoryDAO:
    """系统分类数据访问对象"""
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """获取所有系统分类"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, code, name 
                    FROM system_categories 
                    ORDER BY id
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取系统分类失败: {e}")
            raise


class ModuleDAO:
    """模块数据访问对象"""
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """获取所有模块"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT m.id, m.system_id, m.name, m.description, m.status, m.tags,
                           m.created_at, m.updated_at, s.name as system_name
                    FROM modules m
                    LEFT JOIN systems s ON m.system_id = s.id
                    ORDER BY m.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取模块列表失败: {e}")
            raise

    @staticmethod
    def get_all_modules() -> List[Dict[str, Any]]:
        """获取所有模块（别名方法）"""
        return ModuleDAO.get_all()
    
    @staticmethod
    def get_by_system_id(system_id: int) -> List[Dict[str, Any]]:
        """根据系统ID获取模块列表"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, system_id, name, description, status, tags, created_at, updated_at
                    FROM modules 
                    WHERE system_id = ?
                    ORDER BY created_at DESC
                """, (system_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取系统模块列表失败: {e}")
            raise
    
    @staticmethod
    def get_modules_by_system(system_id: int) -> List[Dict[str, Any]]:
        """根据系统ID获取模块列表（别名方法）"""
        return ModuleDAO.get_by_system_id(system_id)
    
    @staticmethod
    def get_by_id(module_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取模块"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT m.id, m.system_id, m.name, m.description, m.status, m.tags,
                           m.created_at, m.updated_at, s.name as system_name
                    FROM modules m
                    LEFT JOIN systems s ON m.system_id = s.id
                    WHERE m.id = ?
                """, (module_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取模块详情失败: {e}")
            raise
    
    @staticmethod
    def create(system_id: int, name: str, description: str = None, tags: str = None, path: str = "/") -> int:
        """创建模块"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO modules (system_id, name, description, tags, path) 
                    VALUES (?, ?, ?, ?, ?)
                """, (system_id, name, description, tags, path))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"创建模块失败: {e}")
            raise
    
    @staticmethod
    def update(module_id: int, name: str = None, description: str = None, 
               status: str = None, tags: str = None) -> bool:
        """更新模块"""
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if tags is not None:
                updates.append("tags = ?")
                params.append(tags)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(module_id)
            
            with get_db_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE modules 
                    SET {', '.join(updates)} 
                    WHERE id = ?
                """, params)
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新模块失败: {e}")
            raise
    
    @staticmethod
    def delete(module_id: int) -> bool:
        """删除模块"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM modules WHERE id = ?", (module_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除模块失败: {e}")
            raise
    
    @staticmethod
    def get_tags() -> List[str]:
        """获取所有标签"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT DISTINCT tags FROM modules WHERE tags IS NOT NULL")
                rows = cursor.fetchall()
                
                # 解析标签
                all_tags = set()
                for row in rows:
                    if row['tags']:
                        tags = [tag.strip() for tag in row['tags'].split(',')]
                        all_tags.update(tags)
                
                return sorted(list(all_tags))
        except Exception as e:
            logger.error(f"获取标签列表失败: {e}")
            raise
    
    @staticmethod
    def count_by_system_id(system_id: int) -> int:
        """根据系统ID统计模块数量"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM modules WHERE system_id = ?", (system_id,))
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"统计系统模块数量失败: {e}")
            raise

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取模块统计信息"""
        try:
            with get_db_cursor() as cursor:
                # 总模块数
                cursor.execute("SELECT COUNT(*) as total FROM modules")
                total = cursor.fetchone()['total']
                
                # 按状态统计
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM modules 
                    GROUP BY status
                """)
                status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
                
                # 按系统统计
                cursor.execute("""
                    SELECT s.name as system_name, COUNT(m.id) as count
                    FROM systems s
                    LEFT JOIN modules m ON s.id = m.system_id
                    GROUP BY s.id, s.name
                    ORDER BY count DESC
                """)
                system_stats = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total": total,
                    "by_status": status_stats,
                    "by_system": system_stats
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise


class ApiInterfaceDAO:
    """API接口数据访问对象"""
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """获取所有API接口"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, a.system_id, a.module_id, a.name, a.description, 
                           a.method, a.path, a.version, a.status, a.request_format,
                           a.response_format, a.auth_required, a.rate_limit, a.timeout,
                           a.tags, a.request_schema, a.response_schema, 
                           a.example_request, a.example_response,
                           a.created_at, a.updated_at,
                           s.name as system_name, m.name as module_name
                    FROM api_interfaces a
                    LEFT JOIN systems s ON a.system_id = s.id
                    LEFT JOIN modules m ON a.module_id = m.id
                    ORDER BY a.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取API接口列表失败: {e}")
            raise
    
    @staticmethod
    def get_by_id(api_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取API接口"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, a.system_id, a.module_id, a.name, a.description, 
                           a.method, a.path, a.version, a.status, a.request_format,
                           a.response_format, a.auth_required, a.rate_limit, a.timeout,
                           a.tags, a.request_schema, a.response_schema, 
                           a.example_request, a.example_response,
                           a.created_at, a.updated_at,
                           s.name as system_name, m.name as module_name
                    FROM api_interfaces a
                    LEFT JOIN systems s ON a.system_id = s.id
                    LEFT JOIN modules m ON a.module_id = m.id
                    WHERE a.id = ?
                """, (api_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取API接口详情失败: {e}")
            raise
    
    @staticmethod
    def get_by_system_id(system_id: int) -> List[Dict[str, Any]]:
        """根据系统ID获取API接口列表"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, a.system_id, a.module_id, a.name, a.description, 
                           a.method, a.path, a.version, a.status, a.request_format,
                           a.response_format, a.auth_required, a.rate_limit, a.timeout,
                           a.tags, a.request_schema, a.response_schema, 
                           a.example_request, a.example_response,
                           a.created_at, a.updated_at,
                           s.name as system_name, m.name as module_name
                    FROM api_interfaces a
                    LEFT JOIN systems s ON a.system_id = s.id
                    LEFT JOIN modules m ON a.module_id = m.id
                    WHERE a.system_id = ?
                    ORDER BY a.created_at DESC
                """, (system_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取系统API接口列表失败: {e}")
            raise
    
    @staticmethod
    def get_by_module_id(module_id: int) -> List[Dict[str, Any]]:
        """根据模块ID获取API接口列表"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT a.id, a.system_id, a.module_id, a.name, a.description, 
                           a.method, a.path, a.version, a.status, a.request_format,
                           a.response_format, a.auth_required, a.rate_limit, a.timeout,
                           a.tags, a.request_schema, a.response_schema, 
                           a.example_request, a.example_response,
                           a.created_at, a.updated_at,
                           s.name as system_name, m.name as module_name
                    FROM api_interfaces a
                    LEFT JOIN systems s ON a.system_id = s.id
                    LEFT JOIN modules m ON a.module_id = m.id
                    WHERE a.module_id = ?
                    ORDER BY a.created_at DESC
                """, (module_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取模块API接口列表失败: {e}")
            raise
    
    @staticmethod
    def create(api_data: Dict[str, Any]) -> int:
        """创建API接口"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_interfaces (
                        system_id, module_id, name, description, method, path, version,
                        status, request_format, response_format, auth_required, 
                        rate_limit, timeout, tags, request_schema, response_schema,
                        example_request, example_response
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    api_data.get('system_id'),
                    api_data.get('module_id'),
                    api_data.get('name'),
                    api_data.get('description'),
                    api_data.get('method'),
                    api_data.get('path'),
                    api_data.get('version', 'v1'),
                    api_data.get('status', 'active'),
                    api_data.get('request_format', 'json'),
                    api_data.get('response_format', 'json'),
                    api_data.get('auth_required', True),
                    api_data.get('rate_limit', 1000),
                    api_data.get('timeout', 30),
                    api_data.get('tags'),
                    api_data.get('request_schema'),
                    api_data.get('response_schema'),
                    api_data.get('example_request'),
                    api_data.get('example_response')
                ))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"创建API接口失败: {e}")
            raise
    
    @staticmethod
    def update(api_id: int, api_data: Dict[str, Any]) -> bool:
        """更新API接口"""
        try:
            with get_db_cursor() as cursor:
                # 构建动态更新SQL
                update_fields = []
                update_values = []
                
                for field in ['system_id', 'module_id', 'name', 'description', 'method', 
                             'path', 'version', 'status', 'request_format', 'response_format',
                             'auth_required', 'rate_limit', 'timeout', 'tags', 
                             'request_schema', 'response_schema', 'example_request', 'example_response']:
                    if field in api_data:
                        update_fields.append(f"{field} = ?")
                        update_values.append(api_data[field])
                
                if not update_fields:
                    return False
                
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(api_id)
                
                sql = f"UPDATE api_interfaces SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, update_values)
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新API接口失败: {e}")
            raise
    
    @staticmethod
    def delete(api_id: int) -> bool:
        """删除API接口"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM api_interfaces WHERE id = ?", (api_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除API接口失败: {e}")
            raise
    
    @staticmethod
    def search(keyword: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """搜索API接口"""
        try:
            with get_db_cursor() as cursor:
                where_conditions = []
                params = []
                
                # 关键词搜索
                if keyword:
                    where_conditions.append("""
                        (a.name LIKE ? OR a.description LIKE ? OR a.path LIKE ? OR a.tags LIKE ?)
                    """)
                    keyword_param = f"%{keyword}%"
                    params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
                
                # 过滤条件
                if filters:
                    if filters.get('system_id'):
                        where_conditions.append("a.system_id = ?")
                        params.append(filters['system_id'])
                    
                    if filters.get('module_id'):
                        where_conditions.append("a.module_id = ?")
                        params.append(filters['module_id'])
                    
                    if filters.get('method'):
                        where_conditions.append("a.method = ?")
                        params.append(filters['method'])
                    
                    if filters.get('status'):
                        where_conditions.append("a.status = ?")
                        params.append(filters['status'])
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                cursor.execute(f"""
                    SELECT a.id, a.system_id, a.module_id, a.name, a.description, 
                           a.method, a.path, a.version, a.status, a.request_format,
                           a.response_format, a.auth_required, a.rate_limit, a.timeout,
                           a.tags, a.request_schema, a.response_schema, 
                           a.example_request, a.example_response,
                           a.created_at, a.updated_at,
                           s.name as system_name, m.name as module_name
                    FROM api_interfaces a
                    LEFT JOIN systems s ON a.system_id = s.id
                    LEFT JOIN modules m ON a.module_id = m.id
                    WHERE {where_clause}
                    ORDER BY a.created_at DESC
                """, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"搜索API接口失败: {e}")
            raise
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取API接口统计信息"""
        try:
            with get_db_cursor() as cursor:
                # 总接口数
                cursor.execute("SELECT COUNT(*) as total FROM api_interfaces")
                total = cursor.fetchone()['total']
                
                # 按状态统计
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM api_interfaces 
                    GROUP BY status
                """)
                status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
                
                # 按方法统计
                cursor.execute("""
                    SELECT method, COUNT(*) as count 
                    FROM api_interfaces 
                    GROUP BY method
                """)
                method_stats = {row['method']: row['count'] for row in cursor.fetchall()}
                
                # 按系统统计
                cursor.execute("""
                    SELECT s.name as system_name, COUNT(a.id) as count
                    FROM systems s
                    LEFT JOIN api_interfaces a ON s.id = a.system_id
                    GROUP BY s.id, s.name
                    ORDER BY count DESC
                """)
                system_stats = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total": total,
                    "by_status": status_stats,
                    "by_method": method_stats,
                    "by_system": system_stats
                }
        except Exception as e:
            logger.error(f"获取API接口统计信息失败: {e}")
            raise
    
    @staticmethod
    def batch_update_status(api_ids: List[int], status: str) -> int:
        """批量更新API接口状态"""
        try:
            with get_db_cursor() as cursor:
                placeholders = ','.join(['?' for _ in api_ids])
                cursor.execute(f"""
                    UPDATE api_interfaces 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id IN ({placeholders})
                """, [status] + api_ids)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"批量更新API接口状态失败: {e}")
            raise
    
    @staticmethod
    def batch_delete(api_ids: List[int]) -> int:
        """批量删除API接口"""
        try:
            with get_db_cursor() as cursor:
                placeholders = ','.join(['?' for _ in api_ids])
                cursor.execute(f"DELETE FROM api_interfaces WHERE id IN ({placeholders})", api_ids)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"批量删除API接口失败: {e}")
            raise