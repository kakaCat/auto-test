"""
数据模型 - 极简版
Data Models - Simplified

提供简化的数据模型定义
"""

from .system import System, SystemCreate, SystemUpdate
from .module import Module, ModuleCreate, ModuleUpdate
from .api_interface import (
    ApiInterface, ApiInterfaceCreate, ApiInterfaceUpdate,
    ApiInterfaceQueryRequest, ApiInterfaceResponse, ApiInterfaceStats,
    ApiInterfaceBatchRequest, ApiInterfaceImportRequest, ApiInterfaceExportResponse
)

__all__ = [
    "System",
    "SystemCreate", 
    "SystemUpdate",
    "Module",
    "ModuleCreate",
    "ModuleUpdate",
    "ApiInterface",
    "ApiInterfaceCreate",
    "ApiInterfaceUpdate",
    "ApiInterfaceQueryRequest",
    "ApiInterfaceResponse",
    "ApiInterfaceStats",
    "ApiInterfaceBatchRequest",
    "ApiInterfaceImportRequest",
    "ApiInterfaceExportResponse"
]