"""
测试API仓储层
Repository for Test API entities: CRUD operations against SQLite.
遵循：禁止业务逻辑，仅做数据库访问与事务管理。
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from ..database.connection import get_db_cursor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TestApiRepository:
    """测试API仓储层（Repository）
    - 负责对 test_apis 表的增删改查
    - 不包含任何业务逻辑
    """

    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """创建测试API
        Args:
            data: 传入的数据字典，字段使用 snake_case
        Returns:
            新记录的ID
        """
        # 序列化JSON字段
        request_config = TestApiRepository._to_json_text(data.get("request_config"))
        execution_config = TestApiRepository._to_json_text(data.get("execution_config"))
        expected_response = TestApiRepository._to_json_text(data.get("expected_response"))
        metadata = TestApiRepository._to_json_text(data.get("metadata"))

        enabled_val = data.get("enabled")
        if isinstance(enabled_val, bool):
            enabled = 1 if enabled_val else 0
        elif enabled_val is None:
            enabled = 1
        else:
            try:
                enabled = 1 if int(enabled_val) == 1 else 0
            except Exception:
                enabled = 1

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO test_apis (
                    api_id, name, description, enabled, tags,
                    request_config, execution_config, expected_response, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("api_id"),
                    data.get("name"),
                    data.get("description"),
                    enabled,
                    data.get("tags"),
                    request_config,
                    execution_config,
                    expected_response,
                    metadata,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def update(test_api_id: int, data: Dict[str, Any]) -> bool:
        """更新测试API，支持部分字段更新"""
        update_fields: List[str] = []
        update_values: List[Any] = []

        # 允许更新的字段集合
        allowed = {
            "api_id",
            "name",
            "description",
            "enabled",
            "tags",
            "request_config",
            "execution_config",
            "expected_response",
            "metadata",
        }

        # 先处理类型转换
        to_serialize = {"request_config", "execution_config", "expected_response", "metadata"}
        for key in list(data.keys()):
            if key not in allowed:
                data.pop(key)
                continue
            if key in to_serialize:
                data[key] = TestApiRepository._to_json_text(data.get(key))
            elif key == "enabled":
                val = data.get("enabled")
                if isinstance(val, bool):
                    data[key] = 1 if val else 0
                elif val is None:
                    data[key] = None
                else:
                    try:
                        data[key] = 1 if int(val) == 1 else 0
                    except Exception:
                        data[key] = 0

        for field, value in data.items():
            update_fields.append(f"{field} = ?")
            update_values.append(value)

        if not update_fields:
            return False

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(test_api_id)

        sql = f"UPDATE test_apis SET {', '.join(update_fields)} WHERE id = ?"
        with get_db_cursor() as cursor:
            cursor.execute(sql, update_values)
            return cursor.rowcount > 0

    @staticmethod
    def get_by_id(test_api_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取测试API详情"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, api_id, name, description, enabled, tags,
                       request_config, execution_config, expected_response, metadata,
                       created_at, updated_at
                FROM test_apis
                WHERE id = ?
                """,
                (test_api_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            result = dict(row)
            # 反序列化JSON字段
            for key in ["request_config", "execution_config", "expected_response", "metadata"]:
                if result.get(key):
                    try:
                        result[key] = json.loads(result[key])
                    except Exception:
                        # 保持原样（容错处理）
                        pass
            # enabled 映射为布尔
            result["enabled"] = bool(result.get("enabled", 1))
            return result

    @staticmethod
    def list(
        keyword: Optional[str], api_id: Optional[int], enabled_only: Optional[bool], tags: Optional[str],
        page: int, size: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """分页查询测试API列表"""
        where: List[str] = []
        params: List[Any] = []

        if keyword:
            like = f"%{keyword}%"
            where.append("(name LIKE ? OR description LIKE ? OR tags LIKE ?)")
            params.extend([like, like, like])
        if api_id is not None:
            where.append("api_id = ?")
            params.append(api_id)
        if enabled_only:
            where.append("enabled = 1")
        if tags:
            where.append("tags LIKE ?")
            params.append(f"%{tags}%")

        where_clause = " AND ".join(where) if where else "1=1"
        offset = max(page - 1, 0) * size

        with get_db_cursor() as cursor:
            cursor.execute(
                f"""
                SELECT id, api_id, name, description, enabled, tags, created_at, updated_at
                FROM test_apis
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [size, offset],
            )
            items = [dict(r) for r in cursor.fetchall()]

            cursor.execute(
                f"SELECT COUNT(*) as total FROM test_apis WHERE {where_clause}",
                params,
            )
            total = cursor.fetchone()[0]

        # 映射 enabled
        for it in items:
            it["enabled"] = bool(it.get("enabled", 1))

        return items, total

    @staticmethod
    def delete(test_api_id: int) -> bool:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM test_apis WHERE id = ?", (test_api_id,))
            return cursor.rowcount > 0

    @staticmethod
    def _to_json_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return json.dumps({"value": str(value)}, ensure_ascii=False)
        if isinstance(value, str):
            return value
        # 其他类型统一转字符串
        return json.dumps(value, ensure_ascii=False)