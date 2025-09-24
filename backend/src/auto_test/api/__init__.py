"""
API路由 - 极简版
API Routes - Simplified

提供简化的API路由管理
"""

from .systems import router as systems_router
from .modules import router as modules_router

__all__ = [
    "systems_router",
    "modules_router"
]