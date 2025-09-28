#!/usr/bin/env python3
"""
脚本名称：数据库表查询工具
创建时间：2024-01-20
用途：查询SQLite数据库中的所有表，支持过滤和详细信息显示
参数：
  --db-path: 数据库文件路径（可选，默认使用项目配置）
  --filter: 表名过滤模式（可选）
  --details: 显示表结构详细信息（可选）
示例：
  python scripts/ai/database/query_tables.py
  python scripts/ai/database/query_tables.py --filter "api_*"
  python scripts/ai/database/query_tables.py --details
"""

import sys
import json
import sqlite3
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_path():
    """获取数据库路径"""
    root = Path.cwd()
    
    # 尝试从后端配置获取
    try:
        sys.path.insert(0, str(root / "backend"))
        from src.auto_test.config import get_config
        return Path(get_config().DATABASE_PATH)
    except Exception:
        pass
    
    # 尝试备用路径
    try:
        sys.path.insert(0, str(root / "backend" / "src"))
        from auto_test.config import get_config
        return Path(get_config().DATABASE_PATH)
    except Exception:
        pass
    
    # 默认路径
    return root / "auto_test.db"

def query_tables(db_path, filter_pattern=None, show_details=False):
    """查询数据库表"""
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        # 查询所有非系统表
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        if filter_pattern:
            query += f" AND name LIKE '{filter_pattern}'"
        query += " ORDER BY name"
        
        cur.execute(query)
        tables = [row[0] for row in cur.fetchall()]
        
        result = {
            "db_path": str(db_path),
            "table_count": len(tables),
            "tables": tables
        }
        
        if show_details:
            table_details = {}
            for table in tables:
                cur.execute(f"PRAGMA table_info({table})")
                columns = cur.fetchall()
                table_details[table] = {
                    "columns": [{"name": col[1], "type": col[2], "not_null": bool(col[3]), "pk": bool(col[5])} for col in columns],
                    "column_count": len(columns)
                }
            result["table_details"] = table_details
        
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"查询数据库失败: {e}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='查询SQLite数据库表信息')
    parser.add_argument('--db-path', help='数据库文件路径')
    parser.add_argument('--filter', help='表名过滤模式（支持SQL LIKE语法）')
    parser.add_argument('--details', action='store_true', help='显示表结构详细信息')
    parser.add_argument('--format', choices=['json', 'table'], default='json', help='输出格式')
    args = parser.parse_args()
    
    try:
        # 确定数据库路径
        if args.db_path:
            db_path = Path(args.db_path)
        else:
            db_path = get_database_path()
        
        if not db_path.exists():
            logger.error(f"数据库文件不存在: {db_path}")
            sys.exit(1)
        
        logger.info(f"查询数据库: {db_path}")
        
        # 查询表信息
        result = query_tables(db_path, args.filter, args.details)
        
        # 输出结果
        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"数据库路径: {result['db_path']}")
            print(f"表数量: {result['table_count']}")
            print("表列表:")
            for table in result['tables']:
                print(f"  - {table}")
                if args.details and 'table_details' in result:
                    details = result['table_details'][table]
                    print(f"    列数: {details['column_count']}")
                    for col in details['columns']:
                        pk_mark = " (PK)" if col['pk'] else ""
                        null_mark = " NOT NULL" if col['not_null'] else ""
                        print(f"      {col['name']}: {col['type']}{pk_mark}{null_mark}")
        
        logger.info("查询完成")
        
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()