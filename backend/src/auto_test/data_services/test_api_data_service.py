"""
测试API数据服务层（DataService）
职责：统一聚合Repository访问，禁止业务逻辑，仅做数据访问编排。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..repositories.test_api_repository import TestApiRepository
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TestApiDataService:
    """测试API数据服务层"""

    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        # 空值检查
        if not data or not data.get("name") or not data.get("api_id"):
            raise ValueError("缺少必填字段: name 或 api_id")
        return TestApiRepository.create(data)

    @staticmethod
    def update(test_api_id: int, data: Dict[str, Any]) -> bool:
        if not data:
            return False
        return TestApiRepository.update(test_api_id, data)

    @staticmethod
    def get_by_id(test_api_id: int) -> Optional[Dict[str, Any]]:
        return TestApiRepository.get_by_id(test_api_id)

    @staticmethod
    def list(
        keyword: Optional[str], api_id: Optional[int], enabled_only: Optional[bool], tags: Optional[str],
        page: int, size: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        return TestApiRepository.list(keyword, api_id, enabled_only, tags, page, size)

    @staticmethod
    def delete(test_api_id: int) -> bool:
        return TestApiRepository.delete(test_api_id)