#!/usr/bin/env python3
"""
数据库迁移脚本：将表结构从UUID主键改为自增ID主键 + UUID业务标识符
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

def get_db_path():
    """获取数据库文件路径"""
    return Path(__file__).parent / "service_management.db"

def backup_database():
    """备份数据库"""
    db_path = get_db_path()
    backup_path = db_path.parent / f"service_management_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    # 复制数据库文件
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"数据库已备份到: {backup_path}")
    return backup_path

def migrate_systems_table(conn):
    """迁移 management_systems 表"""
    print("开始迁移 management_systems 表...")
    
    cursor = conn.cursor()
    
    # 1. 查询现有数据
    cursor.execute("SELECT * FROM management_systems ORDER BY created_at")
    old_data = cursor.fetchall()
    
    # 获取列名
    cursor.execute("PRAGMA table_info(management_systems)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"找到 {len(old_data)} 条系统记录")
    
    # 2. 创建新表
    cursor.execute("""
        CREATE TABLE management_systems_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT 'el-icon-menu',
            category TEXT NOT NULL DEFAULT 'custom',
            enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
            order_index INTEGER NOT NULL DEFAULT 0,
            url TEXT,
            metadata TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1)),
            deleted_at DATETIME DEFAULT NULL
        )
    """)
    
    # 3. 创建索引
    cursor.execute("CREATE UNIQUE INDEX idx_systems_new_uuid ON management_systems_new(uuid)")
    cursor.execute("CREATE INDEX idx_systems_new_name ON management_systems_new(name)")
    cursor.execute("CREATE INDEX idx_systems_new_category ON management_systems_new(category)")
    cursor.execute("CREATE INDEX idx_systems_new_enabled ON management_systems_new(enabled)")
    cursor.execute("CREATE INDEX idx_systems_new_deleted ON management_systems_new(deleted)")
    cursor.execute("CREATE INDEX idx_systems_new_deleted_at ON management_systems_new(deleted_at)")
    
    # 4. 迁移数据
    uuid_mapping = {}  # 旧UUID -> 新自增ID的映射
    
    for i, row in enumerate(old_data, 1):
        row_dict = dict(zip(columns, row))
        old_uuid = row_dict['id']
        
        # 插入新记录
        cursor.execute("""
            INSERT INTO management_systems_new (
                uuid, name, description, icon, category, enabled, order_index,
                url, metadata, created_at, updated_at, created_by, updated_by,
                deleted, deleted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            old_uuid,  # 原来的UUID现在作为业务标识符
            row_dict['name'],
            row_dict['description'],
            row_dict['icon'],
            row_dict['category'],
            row_dict['enabled'],
            row_dict['order_index'],
            row_dict['url'],
            row_dict['metadata'],
            row_dict['created_at'],
            row_dict['updated_at'],
            row_dict['created_by'],
            row_dict['updated_by'],
            row_dict['deleted'],
            row_dict['deleted_at']
        ))
        
        # 获取新的自增ID
        new_id = cursor.lastrowid
        uuid_mapping[old_uuid] = new_id
        
        print(f"  迁移系统: {row_dict['name']} (UUID: {old_uuid} -> ID: {new_id})")
    
    print(f"management_systems 表迁移完成，共迁移 {len(old_data)} 条记录")
    return uuid_mapping

def migrate_modules_table(conn, system_uuid_mapping):
    """迁移 service_modules 表"""
    print("开始迁移 service_modules 表...")
    
    cursor = conn.cursor()
    
    # 1. 查询现有数据
    cursor.execute("SELECT * FROM service_modules ORDER BY created_at")
    old_data = cursor.fetchall()
    
    # 获取列名
    cursor.execute("PRAGMA table_info(service_modules)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"找到 {len(old_data)} 条模块记录")
    
    # 2. 创建新表
    cursor.execute("""
        CREATE TABLE service_modules_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL UNIQUE,
            system_id INTEGER NOT NULL,
            system_uuid TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT 'el-icon-service',
            path TEXT NOT NULL,
            method TEXT DEFAULT 'GET',
            enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
            version TEXT NOT NULL DEFAULT '1.0.0',
            module_type TEXT DEFAULT 'GENERAL',
            tags TEXT,
            config TEXT,
            order_index INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1)),
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (system_id) REFERENCES management_systems_new(id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)
    
    # 3. 创建索引
    cursor.execute("CREATE UNIQUE INDEX idx_modules_new_uuid ON service_modules_new(uuid)")
    cursor.execute("CREATE INDEX idx_modules_new_system_id ON service_modules_new(system_id)")
    cursor.execute("CREATE INDEX idx_modules_new_system_uuid ON service_modules_new(system_uuid)")
    cursor.execute("CREATE INDEX idx_modules_new_name ON service_modules_new(name)")
    cursor.execute("CREATE INDEX idx_modules_new_path ON service_modules_new(path)")
    cursor.execute("CREATE INDEX idx_modules_new_method ON service_modules_new(method)")
    cursor.execute("CREATE INDEX idx_modules_new_enabled ON service_modules_new(enabled)")
    cursor.execute("CREATE INDEX idx_modules_new_module_type ON service_modules_new(module_type)")
    cursor.execute("CREATE INDEX idx_modules_new_deleted ON service_modules_new(deleted)")
    cursor.execute("CREATE INDEX idx_modules_new_deleted_at ON service_modules_new(deleted_at)")
    
    # 4. 迁移数据
    for i, row in enumerate(old_data, 1):
        row_dict = dict(zip(columns, row))
        old_uuid = row_dict['id']
        old_system_uuid = row_dict['system_id']
        
        # 查找对应的新系统ID
        new_system_id = system_uuid_mapping.get(old_system_uuid)
        if new_system_id is None:
            print(f"  警告: 模块 {row_dict['name']} 的系统UUID {old_system_uuid} 未找到对应的新ID，跳过")
            continue
        
        # 插入新记录
        cursor.execute("""
            INSERT INTO service_modules_new (
                uuid, system_id, system_uuid, name, description, icon, path, method,
                enabled, version, module_type, tags, config, order_index,
                created_at, updated_at, created_by, updated_by, deleted, deleted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            old_uuid,  # 原来的UUID现在作为业务标识符
            new_system_id,  # 新的自增系统ID
            old_system_uuid,  # 保留系统UUID作为冗余字段
            row_dict['name'],
            row_dict['description'],
            row_dict['icon'],
            row_dict['path'],
            row_dict['method'],
            row_dict['enabled'],
            row_dict['version'],
            row_dict['module_type'],
            row_dict['tags'],
            row_dict['config'],
            row_dict['order_index'],
            row_dict['created_at'],
            row_dict['updated_at'],
            row_dict['created_by'],
            row_dict['updated_by'],
            row_dict['deleted'],
            row_dict['deleted_at']
        ))
        
        new_id = cursor.lastrowid
        print(f"  迁移模块: {row_dict['name']} (UUID: {old_uuid} -> ID: {new_id}, 系统: {old_system_uuid} -> {new_system_id})")
    
    print(f"service_modules 表迁移完成")

def update_other_tables(conn, system_uuid_mapping):
    """更新其他相关表的外键引用"""
    print("更新其他表的外键引用...")
    
    cursor = conn.cursor()
    
    # 更新操作日志表
    try:
        cursor.execute("SELECT COUNT(*) FROM system_operation_logs")
        log_count = cursor.fetchone()[0]
        
        if log_count > 0:
            print(f"  更新 {log_count} 条操作日志记录...")
            
            # 这里可以根据需要更新日志表的外键引用
            # 由于日志表可能包含历史数据，我们保持原有的UUID引用
            print("  操作日志表保持原有UUID引用")
        
    except sqlite3.OperationalError:
        print("  操作日志表不存在，跳过")

def create_triggers(conn):
    """创建触发器"""
    print("创建触发器...")
    
    cursor = conn.cursor()
    
    # 系统表更新时间触发器
    cursor.execute("""
        CREATE TRIGGER update_systems_timestamp_new
        AFTER UPDATE ON management_systems_new
        BEGIN
            UPDATE management_systems_new SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)
    
    # 模块表更新时间触发器
    cursor.execute("""
        CREATE TRIGGER update_modules_timestamp_new
        AFTER UPDATE ON service_modules_new
        BEGIN
            UPDATE service_modules_new SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)
    
    print("触发器创建完成")

def replace_tables(conn):
    """替换旧表"""
    print("替换旧表...")
    
    cursor = conn.cursor()
    
    # 删除旧表
    cursor.execute("DROP TABLE IF EXISTS service_modules")
    cursor.execute("DROP TABLE IF EXISTS management_systems")
    
    # 重命名新表
    cursor.execute("ALTER TABLE management_systems_new RENAME TO management_systems")
    cursor.execute("ALTER TABLE service_modules_new RENAME TO service_modules")
    
    print("表替换完成")

def verify_migration(conn):
    """验证迁移结果"""
    print("验证迁移结果...")
    
    cursor = conn.cursor()
    
    # 检查系统表
    cursor.execute("SELECT COUNT(*) FROM management_systems")
    systems_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM service_modules")
    modules_count = cursor.fetchone()[0]
    
    print(f"  系统表记录数: {systems_count}")
    print(f"  模块表记录数: {modules_count}")
    
    # 检查外键约束
    cursor.execute("""
        SELECT COUNT(*) FROM service_modules m 
        LEFT JOIN management_systems s ON m.system_id = s.id 
        WHERE s.id IS NULL
    """)
    orphaned_modules = cursor.fetchone()[0]
    
    if orphaned_modules > 0:
        print(f"  警告: 发现 {orphaned_modules} 个孤立的模块记录")
    else:
        print("  外键约束检查通过")
    
    # 显示示例数据
    cursor.execute("SELECT id, uuid, name FROM management_systems LIMIT 3")
    systems = cursor.fetchall()
    print("  系统表示例数据:")
    for system in systems:
        print(f"    ID: {system[0]}, UUID: {system[1]}, 名称: {system[2]}")
    
    cursor.execute("SELECT id, uuid, name, system_id FROM service_modules LIMIT 3")
    modules = cursor.fetchall()
    print("  模块表示例数据:")
    for module in modules:
        print(f"    ID: {module[0]}, UUID: {module[1]}, 名称: {module[2]}, 系统ID: {module[3]}")

def main():
    """主函数"""
    print("=" * 60)
    print("数据库迁移脚本：UUID主键 -> 自增ID主键 + UUID业务标识符")
    print("=" * 60)
    
    try:
        # 1. 备份数据库
        backup_path = backup_database()
        
        # 2. 连接数据库
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = OFF")  # 临时禁用外键约束
        
        # 3. 开始事务
        conn.execute("BEGIN TRANSACTION")
        
        try:
            # 4. 迁移系统表
            system_uuid_mapping = migrate_systems_table(conn)
            
            # 5. 迁移模块表
            migrate_modules_table(conn, system_uuid_mapping)
            
            # 6. 更新其他表
            update_other_tables(conn, system_uuid_mapping)
            
            # 7. 创建触发器
            create_triggers(conn)
            
            # 8. 替换旧表
            replace_tables(conn)
            
            # 9. 提交事务
            conn.commit()
            
            # 10. 重新启用外键约束
            conn.execute("PRAGMA foreign_keys = ON")
            
            # 11. 验证迁移结果
            verify_migration(conn)
            
            print("\n" + "=" * 60)
            print("迁移完成！")
            print(f"备份文件: {backup_path}")
            print("=" * 60)
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            raise e
        
        finally:
            conn.close()
    
    except Exception as e:
        print(f"\n迁移失败: {e}")
        print("请检查备份文件并手动恢复数据库")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())