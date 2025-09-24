"""
数据库连接管理 - 极简版
Database Connection Management - Simplified

提供简化的数据库连接和初始化功能
"""

import sqlite3
import logging
from typing import Optional
from contextlib import contextmanager
from ..config import get_config

logger = logging.getLogger(__name__)

# 全局数据库连接
_connection: Optional[sqlite3.Connection] = None

def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    global _connection
    
    if _connection is None:
        config = get_config()
        _connection = sqlite3.connect(
            config.DATABASE_PATH,
            check_same_thread=False,
            timeout=30.0
        )
        _connection.row_factory = sqlite3.Row
        logger.info(f"数据库连接成功: {config.DATABASE_PATH}")
    
    return _connection

@contextmanager
def get_db_cursor():
    """获取数据库游标上下文管理器"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()

def init_database():
    """初始化数据库表结构"""
    
    # 系统表
    create_systems_table = """
    CREATE TABLE IF NOT EXISTS systems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 模块表
    create_modules_table = """
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (system_id) REFERENCES systems (id),
        UNIQUE(system_id, name)
    );
    """
    
    # 初始化数据
    init_data_sql = """
    INSERT OR IGNORE INTO systems (name, description) VALUES 
    ('用户管理系统', '负责用户注册、登录、权限管理等功能'),
    ('订单管理系统', '处理订单创建、支付、发货等业务流程'),
    ('库存管理系统', '管理商品库存、入库、出库等操作');
    
    INSERT OR IGNORE INTO modules (system_id, name, description, tags) VALUES 
    (1, '用户注册', '用户账号注册功能', 'auth,register'),
    (1, '用户登录', '用户登录验证功能', 'auth,login'),
    (1, '权限管理', '用户权限分配和管理', 'auth,permission'),
    (2, '订单创建', '创建新订单功能', 'order,create'),
    (2, '支付处理', '订单支付处理功能', 'order,payment'),
    (2, '订单查询', '查询订单状态和详情', 'order,query'),
    (3, '库存查询', '查询商品库存信息', 'inventory,query'),
    (3, '库存更新', '更新商品库存数量', 'inventory,update');
    """
    
    try:
        with get_db_cursor() as cursor:
            cursor.executescript(create_systems_table)
            cursor.executescript(create_modules_table)
            cursor.executescript(init_data_sql)
        
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise