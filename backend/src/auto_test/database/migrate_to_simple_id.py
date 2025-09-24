#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本：从UUID结构迁移到简单自增ID结构
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """数据库迁移器"""
    
    def __init__(self, db_path: str):
        """
        初始化迁移器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"已连接到数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            raise
            
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("已断开数据库连接")
            
    def backup_current_data(self):
        """备份当前数据"""
        try:
            logger.info("开始备份当前数据...")
            
            # 备份系统数据
            systems = self.conn.execute("""
                SELECT uuid, name, description, icon, category, enabled, order_index, 
                       url, metadata, created_at, updated_at, created_by, updated_by
                FROM management_systems 
                WHERE deleted = 0
            """).fetchall()
            
            # 备份模块数据
            modules = self.conn.execute("""
                SELECT uuid, system_uuid, name, description, icon, path, method, 
                       enabled, version, module_type, tags, config, order_index,
                       created_at, updated_at, created_by, updated_by
                FROM service_modules 
                WHERE deleted = 0
            """).fetchall()
            
            # 保存备份数据
            backup_data = {
                'systems': [dict(row) for row in systems],
                'modules': [dict(row) for row in modules],
                'backup_time': datetime.now().isoformat()
            }
            
            backup_file = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"数据备份完成: {backup_file}")
            logger.info(f"备份了 {len(systems)} 个系统和 {len(modules)} 个模块")
            
            return backup_data
            
        except Exception as e:
            logger.error(f"备份数据失败: {e}")
            raise
            
    def create_new_schema(self):
        """创建新的数据库结构"""
        try:
            logger.info("开始创建新的数据库结构...")
            
            # 读取新的数据库结构
            schema_file = Path(__file__).parent / "sqlite_schema_simple.sql"
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                
            # 执行数据库结构创建
            self.conn.executescript(schema_sql)
            self.conn.commit()
            
            logger.info("新的数据库结构创建完成")
            
        except Exception as e:
            logger.error(f"创建新数据库结构失败: {e}")
            raise
            
    def migrate_data(self, backup_data):
        """迁移数据到新结构"""
        try:
            logger.info("开始迁移数据...")
            
            # 创建UUID到ID的映射
            uuid_to_id_map = {}
            
            # 迁移系统数据
            logger.info("迁移系统数据...")
            for system in backup_data['systems']:
                cursor = self.conn.execute("""
                    INSERT INTO management_systems 
                    (name, description, icon, category, enabled, order_index, url, metadata,
                     created_at, updated_at, created_by, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    system['name'], system['description'], system['icon'], 
                    system['category'], system['enabled'], system['order_index'],
                    system['url'], system['metadata'], system['created_at'],
                    system['updated_at'], system['created_by'], system['updated_by']
                ))
                
                # 记录UUID到新ID的映射
                new_id = cursor.lastrowid
                uuid_to_id_map[system['uuid']] = new_id
                logger.info(f"系统 '{system['name']}' UUID {system['uuid']} -> ID {new_id}")
                
            # 迁移模块数据
            logger.info("迁移模块数据...")
            for module in backup_data['modules']:
                # 获取对应的系统ID
                system_id = uuid_to_id_map.get(module['system_uuid'])
                if not system_id:
                    logger.warning(f"模块 '{module['name']}' 的系统UUID {module['system_uuid']} 未找到对应的ID，跳过")
                    continue
                    
                cursor = self.conn.execute("""
                    INSERT INTO service_modules 
                    (system_id, name, description, icon, path, method, enabled, version,
                     module_type, tags, config, order_index, created_at, updated_at,
                     created_by, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    system_id, module['name'], module['description'], module['icon'],
                    module['path'], module['method'], module['enabled'], module['version'],
                    module['module_type'], module['tags'], module['config'], module['order_index'],
                    module['created_at'], module['updated_at'], module['created_by'], module['updated_by']
                ))
                
                new_id = cursor.lastrowid
                logger.info(f"模块 '{module['name']}' UUID {module['uuid']} -> ID {new_id}")
                
            self.conn.commit()
            logger.info("数据迁移完成")
            
            # 保存映射关系
            mapping_file = f"uuid_to_id_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(uuid_to_id_map, f, ensure_ascii=False, indent=2)
            logger.info(f"UUID到ID映射关系已保存: {mapping_file}")
            
        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            raise
            
    def verify_migration(self):
        """验证迁移结果"""
        try:
            logger.info("开始验证迁移结果...")
            
            # 检查系统数据
            systems_count = self.conn.execute("SELECT COUNT(*) FROM management_systems WHERE deleted = 0").fetchone()[0]
            logger.info(f"迁移后系统数量: {systems_count}")
            
            # 检查模块数据
            modules_count = self.conn.execute("SELECT COUNT(*) FROM service_modules WHERE deleted = 0").fetchone()[0]
            logger.info(f"迁移后模块数量: {modules_count}")
            
            # 检查外键关系
            orphaned_modules = self.conn.execute("""
                SELECT COUNT(*) FROM service_modules m
                LEFT JOIN management_systems s ON m.system_id = s.id
                WHERE s.id IS NULL AND m.deleted = 0
            """).fetchone()[0]
            
            if orphaned_modules > 0:
                logger.warning(f"发现 {orphaned_modules} 个孤立模块（没有对应的系统）")
            else:
                logger.info("所有模块都有对应的系统，外键关系正确")
                
            logger.info("迁移验证完成")
            
        except Exception as e:
            logger.error(f"验证迁移结果失败: {e}")
            raise
            
    def run_migration(self):
        """执行完整的迁移流程"""
        try:
            logger.info("开始数据库迁移...")
            
            # 连接数据库
            self.connect()
            
            # 备份当前数据
            backup_data = self.backup_current_data()
            
            # 创建新的数据库结构
            self.create_new_schema()
            
            # 迁移数据
            self.migrate_data(backup_data)
            
            # 验证迁移结果
            self.verify_migration()
            
            logger.info("数据库迁移完成！")
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            raise
        finally:
            # 断开连接
            self.disconnect()

def main():
    """主函数"""
    import sys
    import os
    
    # 获取数据库路径
    current_dir = Path(__file__).parent.parent.parent.parent
    db_path = current_dir / "auto_test.db"
    
    if not db_path.exists():
        logger.error(f"数据库文件不存在: {db_path}")
        sys.exit(1)
        
    # 确认迁移
    print(f"即将迁移数据库: {db_path}")
    print("这将删除现有的表结构并重新创建，确保已经备份了数据库文件！")
    confirm = input("确认继续迁移？(yes/no): ")
    
    if confirm.lower() != 'yes':
        print("迁移已取消")
        sys.exit(0)
        
    # 执行迁移
    migrator = DatabaseMigrator(str(db_path))
    migrator.run_migration()

if __name__ == "__main__":
    main()