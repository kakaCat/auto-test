#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本 - 从旧架构迁移到新架构

功能概述：
- 从SQLite数据库迁移数据到新的SQLAlchemy模型
- 保持数据完整性和一致性
- 提供回滚机制
- 生成迁移报告

迁移步骤：
1. 备份原始数据
2. 创建新的数据库表结构
3. 迁移API信息数据
4. 迁移API调用记录数据
5. 验证数据完整性
6. 生成迁移报告
"""

import os
import sys
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.auto_test.core.config import get_settings
from src.auto_test.core.database import DatabaseManager, get_db_session
from src.auto_test.core.models import APIInfoModel, APICallRecordModel
from src.auto_test.core.container import ApplicationContainer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataMigrator:
    """数据迁移器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.container = ApplicationContainer()
        self.migration_report = {
            "start_time": None,
            "end_time": None,
            "status": "pending",
            "api_info_migrated": 0,
            "api_records_migrated": 0,
            "errors": [],
            "warnings": []
        }
    
    def backup_original_data(self) -> bool:
        """备份原始数据"""
        try:
            logger.info("开始备份原始数据...")
            
            # 查找原始数据库文件
            original_db_paths = [
                "/Users/mac/Documents/ai/auto-test/backend/api_info.db",
                "/Users/mac/Documents/ai/auto-test/backend/src/auto_test/api_info.db",
                "/Users/mac/Documents/ai/auto-test/api_info.db"
            ]
            
            original_db_path = None
            for path in original_db_paths:
                if os.path.exists(path):
                    original_db_path = path
                    break
            
            if not original_db_path:
                logger.warning("未找到原始数据库文件，跳过备份")
                self.migration_report["warnings"].append("未找到原始数据库文件")
                return True
            
            # 创建备份
            backup_path = f"{original_db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(original_db_path, backup_path)
            
            logger.info(f"原始数据备份完成: {backup_path}")
            return True
            
        except Exception as e:
            error_msg = f"备份原始数据失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def create_new_tables(self) -> bool:
        """创建新的数据库表结构"""
        try:
            logger.info("开始创建新的数据库表结构...")
            
            # 初始化数据库
            self.db_manager.init_database()
            
            logger.info("新的数据库表结构创建完成")
            return True
            
        except Exception as e:
            error_msg = f"创建新表结构失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def get_original_data(self) -> tuple[List[Dict], List[Dict]]:
        """获取原始数据"""
        api_info_data = []
        api_records_data = []
        
        try:
            # 查找原始数据库文件
            original_db_paths = [
                "/Users/mac/Documents/ai/auto-test/backend/api_info.db",
                "/Users/mac/Documents/ai/auto-test/backend/src/auto_test/api_info.db",
                "/Users/mac/Documents/ai/auto-test/api_info.db"
            ]
            
            original_db_path = None
            for path in original_db_paths:
                if os.path.exists(path):
                    original_db_path = path
                    break
            
            if not original_db_path:
                logger.warning("未找到原始数据库文件")
                return api_info_data, api_records_data
            
            # 连接原始数据库
            conn = sqlite3.connect(original_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取表列表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 迁移API信息表
            if 'api_info' in tables:
                cursor.execute("SELECT * FROM api_info")
                api_info_data = [dict(row) for row in cursor.fetchall()]
                logger.info(f"找到 {len(api_info_data)} 条API信息记录")
            
            # 迁移API调用记录表
            if 'api_call_records' in tables:
                cursor.execute("SELECT * FROM api_call_records")
                api_records_data = [dict(row) for row in cursor.fetchall()]
                logger.info(f"找到 {len(api_records_data)} 条API调用记录")
            
            conn.close()
            
        except Exception as e:
            error_msg = f"获取原始数据失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
        
        return api_info_data, api_records_data
    
    def migrate_api_info(self, api_info_data: List[Dict]) -> bool:
        """迁移API信息数据"""
        try:
            logger.info("开始迁移API信息数据...")
            
            with next(get_db_session()) as db:
                for api_data in api_info_data:
                    try:
                        # 转换数据格式
                        new_api_data = {
                            "name": api_data.get("name", ""),
                            "url": api_data.get("url", ""),
                            "method": api_data.get("method", "GET"),
                            "description": api_data.get("description"),
                            "headers": api_data.get("headers"),
                            "parameters": api_data.get("parameters"),
                            "response_example": api_data.get("response_example"),
                            "status": api_data.get("status", "active"),
                            "category": api_data.get("category"),
                            "tags": api_data.get("tags")
                        }
                        
                        # 创建新记录
                        api = APIInfoModel.create(db, **new_api_data)
                        
                        # 如果原始数据有ID，尝试保持
                        if "id" in api_data and api_data["id"]:
                            api.id = api_data["id"]
                        
                        # 如果原始数据有时间戳，尝试保持
                        if "created_at" in api_data and api_data["created_at"]:
                            api.created_at = datetime.fromisoformat(api_data["created_at"])
                        if "updated_at" in api_data and api_data["updated_at"]:
                            api.updated_at = datetime.fromisoformat(api_data["updated_at"])
                        
                        self.migration_report["api_info_migrated"] += 1
                        
                    except Exception as e:
                        error_msg = f"迁移API信息记录失败 {api_data.get('name', 'Unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_report["errors"].append(error_msg)
                        continue
                
                db.commit()
            
            logger.info(f"API信息数据迁移完成，成功迁移 {self.migration_report['api_info_migrated']} 条记录")
            return True
            
        except Exception as e:
            error_msg = f"迁移API信息数据失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def migrate_api_records(self, api_records_data: List[Dict]) -> bool:
        """迁移API调用记录数据"""
        try:
            logger.info("开始迁移API调用记录数据...")
            
            with next(get_db_session()) as db:
                for record_data in api_records_data:
                    try:
                        # 转换数据格式
                        new_record_data = {
                            "api_id": record_data.get("api_id", ""),
                            "request_url": record_data.get("request_url", ""),
                            "request_method": record_data.get("request_method", "GET"),
                            "request_headers": record_data.get("request_headers"),
                            "request_body": record_data.get("request_body"),
                            "response_status": record_data.get("response_status"),
                            "response_body": record_data.get("response_body"),
                            "response_time": record_data.get("response_time"),
                            "success": record_data.get("success", True),
                            "error_message": record_data.get("error_message")
                        }
                        
                        # 创建新记录
                        record = APICallRecordModel.create(db, **new_record_data)
                        
                        # 如果原始数据有ID，尝试保持
                        if "id" in record_data and record_data["id"]:
                            record.id = record_data["id"]
                        
                        # 如果原始数据有时间戳，尝试保持
                        if "created_at" in record_data and record_data["created_at"]:
                            record.created_at = datetime.fromisoformat(record_data["created_at"])
                        
                        self.migration_report["api_records_migrated"] += 1
                        
                    except Exception as e:
                        error_msg = f"迁移API调用记录失败 {record_data.get('id', 'Unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_report["errors"].append(error_msg)
                        continue
                
                db.commit()
            
            logger.info(f"API调用记录数据迁移完成，成功迁移 {self.migration_report['api_records_migrated']} 条记录")
            return True
            
        except Exception as e:
            error_msg = f"迁移API调用记录数据失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def verify_migration(self) -> bool:
        """验证迁移结果"""
        try:
            logger.info("开始验证迁移结果...")
            
            with next(get_db_session()) as db:
                # 验证API信息表
                api_count = db.query(APIInfoModel).count()
                logger.info(f"新数据库中API信息记录数: {api_count}")
                
                # 验证API调用记录表
                record_count = db.query(APICallRecordModel).count()
                logger.info(f"新数据库中API调用记录数: {record_count}")
                
                # 检查数据完整性
                if api_count != self.migration_report["api_info_migrated"]:
                    warning_msg = f"API信息记录数不匹配: 预期 {self.migration_report['api_info_migrated']}, 实际 {api_count}"
                    logger.warning(warning_msg)
                    self.migration_report["warnings"].append(warning_msg)
                
                if record_count != self.migration_report["api_records_migrated"]:
                    warning_msg = f"API调用记录数不匹配: 预期 {self.migration_report['api_records_migrated']}, 实际 {record_count}"
                    logger.warning(warning_msg)
                    self.migration_report["warnings"].append(warning_msg)
            
            logger.info("迁移结果验证完成")
            return True
            
        except Exception as e:
            error_msg = f"验证迁移结果失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def generate_report(self) -> str:
        """生成迁移报告"""
        report_content = f"""
数据迁移报告
============

迁移时间: {self.migration_report['start_time']} - {self.migration_report['end_time']}
迁移状态: {self.migration_report['status']}

迁移统计:
- API信息记录: {self.migration_report['api_info_migrated']} 条
- API调用记录: {self.migration_report['api_records_migrated']} 条

错误信息:
{chr(10).join(f"- {error}" for error in self.migration_report['errors']) if self.migration_report['errors'] else "无"}

警告信息:
{chr(10).join(f"- {warning}" for warning in self.migration_report['warnings']) if self.migration_report['warnings'] else "无"}

迁移建议:
1. 请验证新系统的功能是否正常
2. 如有问题，可使用备份文件进行回滚
3. 确认无误后，可删除备份文件
4. 更新应用配置以使用新的API模块
"""
        
        # 保存报告到文件
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"迁移报告已保存到: {report_file}")
        return report_content
    
    def run_migration(self) -> bool:
        """运行完整的迁移流程"""
        self.migration_report["start_time"] = datetime.now().isoformat()
        
        try:
            logger.info("开始数据迁移流程...")
            
            # 1. 备份原始数据
            if not self.backup_original_data():
                self.migration_report["status"] = "failed"
                return False
            
            # 2. 创建新表结构
            if not self.create_new_tables():
                self.migration_report["status"] = "failed"
                return False
            
            # 3. 获取原始数据
            api_info_data, api_records_data = self.get_original_data()
            
            # 4. 迁移API信息
            if api_info_data and not self.migrate_api_info(api_info_data):
                self.migration_report["status"] = "failed"
                return False
            
            # 5. 迁移API调用记录
            if api_records_data and not self.migrate_api_records(api_records_data):
                self.migration_report["status"] = "failed"
                return False
            
            # 6. 验证迁移结果
            if not self.verify_migration():
                self.migration_report["status"] = "failed"
                return False
            
            self.migration_report["status"] = "success"
            self.migration_report["end_time"] = datetime.now().isoformat()
            
            # 7. 生成报告
            report = self.generate_report()
            print(report)
            
            logger.info("数据迁移流程完成！")
            return True
            
        except Exception as e:
            error_msg = f"迁移流程失败: {e}"
            logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            self.migration_report["status"] = "failed"
            self.migration_report["end_time"] = datetime.now().isoformat()
            return False


def main():
    """主函数"""
    print("开始数据迁移...")
    
    migrator = DataMigrator()
    success = migrator.run_migration()
    
    if success:
        print("✅ 数据迁移成功完成！")
        return 0
    else:
        print("❌ 数据迁移失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())