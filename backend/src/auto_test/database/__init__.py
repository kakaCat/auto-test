# Database Package

"""
数据库模块 - 极简版
Database Module - Simplified

提供简化的数据库连接和操作功能
"""

from .connection import get_db_connection, init_database
from .dao import SystemDAO, ModuleDAO

__all__ = [
    "get_db_connection",
    "init_database", 
    "SystemDAO",
    "ModuleDAO"
]