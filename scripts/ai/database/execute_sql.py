#!/usr/bin/env python3
"""
脚本名称：SQL执行工具
创建时间：2024-01-20
用途：执行SQL文件或SQL语句，支持事务管理和结果输出
参数：
  --sql-file: SQL文件路径
  --sql: 直接执行的SQL语句
  --db-path: 数据库文件路径（可选）
  --transaction: 使用事务执行（默认开启）
  --output: 输出格式（json/table/csv）
示例：
  python scripts/ai/database/execute_sql.py --sql-file create_tables.sql
  python scripts/ai/database/execute_sql.py --sql "SELECT * FROM systems"
  python scripts/ai/database/execute_sql.py --sql "SELECT COUNT(*) FROM api_interfaces" --output table
"""

import sys
import json
import sqlite3
import argparse
import logging
import csv
from pathlib import Path
from io import StringIO

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

def execute_sql(db_path, sql_content, use_transaction=True, output_format='json'):
    """执行SQL语句"""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        
        results = []
        
        if use_transaction:
            conn.execute("BEGIN TRANSACTION")
        
        try:
            # 分割多个SQL语句
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for stmt in statements:
                logger.info(f"执行SQL: {stmt[:100]}...")
                cur = conn.execute(stmt)
                
                # 如果是查询语句，收集结果
                if stmt.strip().upper().startswith('SELECT'):
                    rows = cur.fetchall()
                    if rows:
                        # 转换为字典列表
                        result_data = [dict(row) for row in rows]
                        results.append({
                            "sql": stmt,
                            "row_count": len(result_data),
                            "data": result_data
                        })
                    else:
                        results.append({
                            "sql": stmt,
                            "row_count": 0,
                            "data": []
                        })
                else:
                    # 非查询语句，记录影响的行数
                    results.append({
                        "sql": stmt,
                        "affected_rows": cur.rowcount,
                        "message": "执行成功"
                    })
            
            if use_transaction:
                conn.commit()
                logger.info("事务提交成功")
            
        except Exception as e:
            if use_transaction:
                conn.rollback()
                logger.error("事务回滚")
            raise e
        
        finally:
            conn.close()
        
        return {
            "db_path": str(db_path),
            "statement_count": len(statements),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"SQL执行失败: {e}")
        raise

def format_output(result, output_format):
    """格式化输出结果"""
    if output_format == 'json':
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    elif output_format == 'table':
        output = []
        output.append(f"数据库: {result['db_path']}")
        output.append(f"执行语句数: {result['statement_count']}")
        output.append("-" * 50)
        
        for i, res in enumerate(result['results'], 1):
            output.append(f"\n语句 {i}: {res['sql'][:80]}...")
            
            if 'data' in res:
                output.append(f"返回行数: {res['row_count']}")
                if res['data']:
                    # 显示前几行数据
                    for j, row in enumerate(res['data'][:5]):
                        if j == 0:
                            output.append("数据预览:")
                        output.append(f"  {dict(row)}")
                    if len(res['data']) > 5:
                        output.append(f"  ... 还有 {len(res['data']) - 5} 行")
            else:
                output.append(f"影响行数: {res.get('affected_rows', 0)}")
                output.append(f"状态: {res.get('message', '完成')}")
        
        return "\n".join(output)
    
    elif output_format == 'csv':
        output = StringIO()
        
        # 只输出查询结果的CSV
        for res in result['results']:
            if 'data' in res and res['data']:
                writer = csv.DictWriter(output, fieldnames=res['data'][0].keys())
                writer.writeheader()
                writer.writerows(res['data'])
                output.write("\n")
        
        return output.getvalue()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='执行SQL文件或语句')
    parser.add_argument('--sql-file', help='SQL文件路径')
    parser.add_argument('--sql', help='直接执行的SQL语句')
    parser.add_argument('--db-path', help='数据库文件路径')
    parser.add_argument('--no-transaction', action='store_true', help='不使用事务')
    parser.add_argument('--output', choices=['json', 'table', 'csv'], default='json', help='输出格式')
    args = parser.parse_args()
    
    if not args.sql_file and not args.sql:
        parser.error("必须指定 --sql-file 或 --sql 参数")
    
    try:
        # 确定数据库路径
        if args.db_path:
            db_path = Path(args.db_path)
        else:
            db_path = get_database_path()
        
        if not db_path.exists():
            logger.error(f"数据库文件不存在: {db_path}")
            sys.exit(1)
        
        # 获取SQL内容
        if args.sql_file:
            sql_file = Path(args.sql_file)
            if not sql_file.exists():
                logger.error(f"SQL文件不存在: {sql_file}")
                sys.exit(1)
            sql_content = sql_file.read_text(encoding='utf-8')
            logger.info(f"从文件读取SQL: {sql_file}")
        else:
            sql_content = args.sql
            logger.info("执行直接输入的SQL")
        
        # 执行SQL
        use_transaction = not args.no_transaction
        result = execute_sql(db_path, sql_content, use_transaction, args.output)
        
        # 输出结果
        formatted_output = format_output(result, args.output)
        print(formatted_output)
        
        logger.info("SQL执行完成")
        
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()