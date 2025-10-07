"""
API测试场景管理 Service 层占位实现
遵循：业务编排、规则复用、事务控制（后续接入仓储层）。
当前为骨架实现，返回示例数据结构以便前端联调。
"""

from typing import Optional, Dict, Any, List, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TestApiService:
    @staticmethod
    def list_test_apis(
        keyword: Optional[str], api_id: Optional[int], enabled_only: Optional[bool],
        tags: Optional[str], page: int, size: int
    ) -> Dict[str, Any]:
        logger.info(
            "List test apis, keyword=%s, api_id=%s, enabled_only=%s, tags=%s, page=%s, size=%s",
            keyword, api_id, enabled_only, tags, page, size,
        )
        from ..data_services.test_api_data_service import TestApiDataService
        items, total = TestApiDataService.list(keyword, api_id, enabled_only, tags, page, size)
        return {"items": items, "page": page, "size": size, "total": total}

    @staticmethod
    def create_test_api(payload: Any) -> Dict[str, Any]:
        data = TestApiService._to_dict(payload)
        # 通过DataService持久化
        from ..data_services.test_api_data_service import TestApiDataService
        new_id = TestApiDataService.create(data)
        logger.info("Create test api persisted, id=%s, payload=%s", new_id, data)
        detail = TestApiDataService.get_by_id(new_id)
        return detail or {"id": new_id, **data}

    @staticmethod
    def get_test_api_by_id(test_api_id: int) -> Dict[str, Any]:
        logger.info("Get test api by id=%s", test_api_id)
        from ..data_services.test_api_data_service import TestApiDataService
        detail = TestApiDataService.get_by_id(test_api_id)
        return detail or {
            "id": test_api_id,
            "name": "Sample Test API Detail",
            "enabled": True,
            "tags": "regression",
            "config": {"env": "dev"},
        }

    @staticmethod
    def update_test_api(test_api_id: int, payload: Any) -> Dict[str, Any]:
        data = TestApiService._to_dict(payload)
        from ..data_services.test_api_data_service import TestApiDataService
        updated = TestApiDataService.update(test_api_id, data)
        logger.info("Update test api id=%s, updated=%s, payload=%s", test_api_id, updated, data)
        detail = TestApiDataService.get_by_id(test_api_id)
        return detail or {"id": test_api_id, **data}

    @staticmethod
    def delete_test_api(test_api_id: int) -> bool:
        logger.info("Delete test api id=%s", test_api_id)
        return True

    @staticmethod
    def list_runs(test_api_id: int, page: int, size: int) -> Dict[str, Any]:
        logger.info("List runs for test_api_id=%s", test_api_id)
        items = [
            {
                "run_id": "101",
                "status": "success",
                "started_at": "2024-01-02T10:00:00Z",
                "ended_at": "2024-01-02T10:00:05Z",
            }
        ]
        return {"items": items, "page": page, "size": size, "total": 1}

    @staticmethod
    def list_reports(test_api_id: int) -> Dict[str, Any]:
        logger.info("List reports for test_api_id=%s", test_api_id)
        items = [
            {
                "report_id": 201,
                "run_id": "101",
                "summary": {"passed": 5, "failed": 0},
            }
        ]
        return {"items": items, "total": 1}

    @staticmethod
    def execute_test_api(test_api_id: int, payload: Any) -> Dict[str, Any]:
        data = TestApiService._to_dict(payload)
        logger.info("Execute test api id=%s, payload=%s", test_api_id, data)
        return {
            "run_id": "301",
            "status": "success",
            "assertions": [{"name": "status_code", "passed": True}],
            "response_status_code": 200,
            "response_time_ms": 42,
        }

    @staticmethod
    def batch_execute(payload: Any) -> Dict[str, Any]:
        data = TestApiService._to_dict(payload)
        logger.info("Batch execute, payload=%s", data)
        items = [
            {"test_api_id": tid, "run_id": str(300 + idx), "status": "success"}
            for idx, tid in enumerate(data.get("test_api_ids", [1, 2, 3]))
        ]
        return {"items": items}

    @staticmethod
    def import_test_apis(payload: Any) -> Dict[str, Any]:
        data = TestApiService._to_dict(payload)
        logger.info("Import test apis, payload=%s", data)
        return {"imported": True, "count": len(data.get("items", []))}

    @staticmethod
    def export_test_apis(payload: Any) -> Dict[str, Any]:
        data = TestApiService._to_dict(payload)
        logger.info("Export test apis, payload=%s", data)
        return {
            "exported": True,
            "items": data.get("items", []),
            "format": data.get("format", "json"),
        }

    @staticmethod
    def _to_dict(payload: Any) -> Dict[str, Any]:
        try:
            # pydantic v2
            if hasattr(payload, "model_dump"):
                return payload.model_dump()
            # pydantic v1
            if hasattr(payload, "dict"):
                return payload.dict()
            if isinstance(payload, dict):
                return payload
            return {"value": str(payload)}
        except Exception:
            return payload if isinstance(payload, dict) else {"value": str(payload)}