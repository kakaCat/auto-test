"""
响应工具 - 极简版
Response Utils - Simplified

提供统一的API响应格式
"""

from typing import Any, Optional

def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response

def error_response(message: str = "操作失败", code: int = 500) -> dict:
    """错误响应"""
    return {
        "success": False,
        "message": message,
        "code": code
    }