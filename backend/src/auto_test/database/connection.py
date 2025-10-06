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
        url TEXT,
        category TEXT NOT NULL DEFAULT 'custom',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # API 接口表
    create_api_interfaces_table = """
    CREATE TABLE IF NOT EXISTS api_interfaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_id INTEGER NOT NULL,
        module_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        method TEXT NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
        path TEXT NOT NULL,
        version TEXT DEFAULT 'v1',
        status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deprecated')),
        request_format TEXT DEFAULT 'json' CHECK (request_format IN ('json', 'form', 'xml')),
        response_format TEXT DEFAULT 'json' CHECK (response_format IN ('json', 'xml', 'text')),
        auth_required INTEGER DEFAULT 1 CHECK (auth_required IN (0, 1)),
        rate_limit INTEGER DEFAULT 1000,
        timeout INTEGER DEFAULT 30,
        tags TEXT,
        request_schema TEXT,
        response_schema TEXT,
        example_request TEXT,
        example_response TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (system_id) REFERENCES systems (id) ON DELETE CASCADE,
        FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE SET NULL,
        UNIQUE(system_id, method, path, version)
    );

    CREATE INDEX IF NOT EXISTS idx_api_interfaces_system_id ON api_interfaces(system_id);
    CREATE INDEX IF NOT EXISTS idx_api_interfaces_module_id ON api_interfaces(module_id);
    CREATE INDEX IF NOT EXISTS idx_api_interfaces_method ON api_interfaces(method);
    CREATE INDEX IF NOT EXISTS idx_api_interfaces_path ON api_interfaces(path);
    CREATE INDEX IF NOT EXISTS idx_api_interfaces_version ON api_interfaces(version);
    """
    
    # 模块表
    create_modules_table = """
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        path TEXT DEFAULT '/',
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (system_id) REFERENCES systems (id),
        UNIQUE(system_id, name)
    );
    """

    # 页面表
    create_pages_table = """
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        route_path VARCHAR(200),
        page_type VARCHAR(50) DEFAULT 'page',
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_pages_system_id ON pages(system_id);
    CREATE INDEX IF NOT EXISTS idx_pages_status ON pages(status);
    """

    # 页面-API 关联表
    create_page_apis_table = """
    CREATE TABLE IF NOT EXISTS page_apis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        api_id INTEGER NOT NULL,
        execution_type VARCHAR(20) DEFAULT 'parallel',
        execution_order INTEGER DEFAULT 0,
        trigger_action VARCHAR(50),
        api_purpose VARCHAR(100),
        success_action VARCHAR(100),
        error_action VARCHAR(100),
        conditions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
        FOREIGN KEY (api_id) REFERENCES api_interfaces(id) ON DELETE CASCADE,
        UNIQUE(page_id, api_id)
    );

    CREATE INDEX IF NOT EXISTS idx_page_apis_page_id ON page_apis(page_id);
    CREATE INDEX IF NOT EXISTS idx_page_apis_api_id ON page_apis(api_id);
    CREATE INDEX IF NOT EXISTS idx_page_apis_execution_order ON page_apis(page_id, execution_order);
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
            # 确保开启外键（SQLite 默认关闭）
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.executescript(create_systems_table)
            cursor.executescript(create_modules_table)
            cursor.executescript(create_api_interfaces_table)
            cursor.executescript(create_pages_table)
            cursor.executescript(create_page_apis_table)
            cursor.executescript(init_data_sql)

            # 补丁迁移：为已有的 systems 表增加缺失的 category 列
            cursor.execute("PRAGMA table_info(systems)")
            system_columns = [row[1] if isinstance(row, tuple) else row["name"] for row in cursor.fetchall()]
            if "category" not in system_columns:
                logger.info("检测到 systems.category 缺失，正在执行迁移补丁……")
                cursor.execute("ALTER TABLE systems ADD COLUMN category TEXT NOT NULL DEFAULT 'custom'")

            # 补丁迁移：为已有的 systems 表增加缺失的 url 列
            cursor.execute("PRAGMA table_info(systems)")
            system_columns = [row[1] if isinstance(row, tuple) else row["name"] for row in cursor.fetchall()]
            if "url" not in system_columns:
                logger.info("检测到 systems.url 缺失，正在执行迁移补丁……")
                cursor.execute("ALTER TABLE systems ADD COLUMN url TEXT")

            # 补丁迁移：为已有的 modules 表增加缺失的 path 列
            cursor.execute("PRAGMA table_info(modules)")
            module_columns = [row[1] if isinstance(row, tuple) else row["name"] for row in cursor.fetchall()]
            if "path" not in module_columns:
                logger.info("检测到 modules.path 缺失，正在执行迁移补丁……")
                cursor.execute("ALTER TABLE modules ADD COLUMN path TEXT DEFAULT '/'")

            # 补丁迁移：为已有的 api_interfaces 表增加缺失的 enabled 列，并初始化值与索引
            cursor.execute("PRAGMA table_info(api_interfaces)")
            api_columns = [row[1] if isinstance(row, tuple) else row["name"] for row in cursor.fetchall()]
            if "enabled" not in api_columns:
                logger.info("检测到 api_interfaces.enabled 缺失，正在执行迁移补丁……")
                # 添加列，默认启用
                cursor.execute("ALTER TABLE api_interfaces ADD COLUMN enabled INTEGER DEFAULT 1")
                # 根据现有的 status 初始化 enabled 值：active -> 1，其它 -> 0
                cursor.execute("UPDATE api_interfaces SET enabled = CASE WHEN status = 'active' THEN 1 ELSE 0 END")
                # 创建索引以提高查询性能
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_interfaces_enabled ON api_interfaces(enabled)")

        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise