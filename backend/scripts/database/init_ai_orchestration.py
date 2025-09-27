#!/usr/bin/env python3
"""
AI编排模块数据库初始化脚本

功能：
1. 创建AI编排相关的数据库表
2. 初始化MCP工具配置
3. 创建示例数据

使用方法：
python scripts/database/init_ai_orchestration.py
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.auto_test.config import Config
from src.auto_test.utils.logger import get_logger

logger = get_logger(__name__)


def get_database_path():
    """获取数据库路径"""
    config = Config()
    # 简化实现，使用SQLite数据库
    db_path = os.path.join(os.path.dirname(__file__), '../../src/auto_test/database/service_management.db')
    return db_path


def create_ai_tables(cursor):
    """创建AI编排相关表"""
    logger.info("创建AI编排相关表...")
    
    # 读取SQL文件
    sql_file = os.path.join(os.path.dirname(__file__), 'create_ai_orchestration_tables.sql')
    
    if not os.path.exists(sql_file):
        logger.error(f"SQL文件不存在: {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 执行SQL语句
    try:
        # 分割SQL语句并执行
        statements = sql_content.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
        
        logger.info("AI编排表创建成功")
        return True
        
    except Exception as e:
        logger.error(f"创建AI编排表失败: {e}")
        return False


def init_mcp_tools(cursor):
    """初始化MCP工具配置"""
    logger.info("初始化MCP工具配置...")
    
    tools_config = [
        {
            'id': int(datetime.now().timestamp() * 1000000),
            'tool_name': 'http_request',
            'tool_type': 'http',
            'schema_definition': json.dumps({
                "name": "http_request",
                "description": "执行HTTP请求",
                "type": "http",
                "version": "1.0.0",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                        },
                        "url": {"type": "string"},
                        "headers": {"type": "object"},
                        "body": {"type": "object"},
                        "timeout": {"type": "number", "default": 30}
                    },
                    "required": ["method", "url"]
                }
            }, ensure_ascii=False),
            'is_enabled': True,
            'config_data': json.dumps({"timeout": 30, "retry_count": 3}, ensure_ascii=False)
        },
        {
            'id': int(datetime.now().timestamp() * 1000000) + 1,
            'tool_name': 'validate_response',
            'tool_type': 'validation',
            'schema_definition': json.dumps({
                "name": "validate_response",
                "description": "验证HTTP响应结果",
                "type": "validation",
                "version": "1.0.0",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "response": {"type": "object"},
                        "rules": {"type": "array"},
                        "strict": {"type": "boolean", "default": False}
                    },
                    "required": ["response", "rules"]
                }
            }, ensure_ascii=False),
            'is_enabled': True,
            'config_data': json.dumps({"strict_mode": False}, ensure_ascii=False)
        },
        {
            'id': int(datetime.now().timestamp() * 1000000) + 2,
            'tool_name': 'wait_for',
            'tool_type': 'utility',
            'schema_definition': json.dumps({
                "name": "wait_for",
                "description": "等待指定时间或条件",
                "type": "utility",
                "version": "1.0.0",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "number"},
                        "condition": {"type": "string"},
                        "timeout": {"type": "number", "default": 60}
                    },
                    "required": ["duration"]
                }
            }, ensure_ascii=False),
            'is_enabled': True,
            'config_data': json.dumps({"max_wait_time": 300}, ensure_ascii=False)
        }
    ]
    
    try:
        for tool in tools_config:
            cursor.execute("""
                INSERT OR REPLACE INTO mcp_tool_configs 
                (id, tool_name, tool_type, schema_definition, is_enabled, config_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tool['id'],
                tool['tool_name'],
                tool['tool_type'],
                tool['schema_definition'],
                tool['is_enabled'],
                tool['config_data']
            ))
        
        logger.info(f"初始化了 {len(tools_config)} 个MCP工具配置")
        return True
        
    except Exception as e:
        logger.error(f"初始化MCP工具配置失败: {e}")
        return False


def create_sample_plan(cursor):
    """创建示例编排计划"""
    logger.info("创建示例编排计划...")
    
    sample_plan = {
        'id': int(datetime.now().timestamp() * 1000000),
        'plan_name': '示例API测试流程',
        'description': '这是一个示例的API测试编排计划',
        'intent_text': '测试用户注册和登录功能',
        'execution_plan': json.dumps({
            "plan_id": "sample_plan_001",
            "plan_name": "示例API测试流程",
            "description": "测试用户注册和登录功能",
            "steps": [
                {
                    "step_id": "step_1",
                    "step_name": "用户注册",
                    "step_type": "api_call",
                    "tool_name": "http_request",
                    "parameters": {
                        "method": "POST",
                        "url": "/api/users/register",
                        "body": {
                            "username": "testuser",
                            "email": "test@example.com",
                            "password": "password123"
                        }
                    },
                    "dependencies": [],
                    "timeout": 30
                },
                {
                    "step_id": "step_2",
                    "step_name": "用户登录",
                    "step_type": "api_call",
                    "tool_name": "http_request",
                    "parameters": {
                        "method": "POST",
                        "url": "/api/users/login",
                        "body": {
                            "username": "testuser",
                            "password": "password123"
                        }
                    },
                    "dependencies": ["step_1"],
                    "timeout": 30
                },
                {
                    "step_id": "step_3",
                    "step_name": "验证登录结果",
                    "step_type": "data_validation",
                    "tool_name": "validate_response",
                    "parameters": {
                        "rules": [
                            {
                                "type": "status_code",
                                "operator": "eq",
                                "value": 200
                            }
                        ]
                    },
                    "dependencies": ["step_2"],
                    "timeout": 10
                }
            ],
            "metadata": {
                "involved_system_ids": [1],
                "involved_module_ids": [1, 2],
                "total_steps": 3
            },
            "estimated_duration": 70
        }, ensure_ascii=False),
        'metadata': json.dumps({
            "involved_system_ids": [1],
            "involved_module_ids": [1, 2],
            "tags": ["示例", "用户管理"],
            "owner_team": "测试团队"
        }, ensure_ascii=False),
        'status': 'draft',
        'created_by': 'system',
        'is_template': True
    }
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO api_orchestration_plans 
            (id, plan_name, description, intent_text, execution_plan, metadata, status, created_by, is_template)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sample_plan['id'],
            sample_plan['plan_name'],
            sample_plan['description'],
            sample_plan['intent_text'],
            sample_plan['execution_plan'],
            sample_plan['metadata'],
            sample_plan['status'],
            sample_plan['created_by'],
            sample_plan['is_template']
        ))
        
        logger.info("创建示例编排计划成功")
        return True
        
    except Exception as e:
        logger.error(f"创建示例编排计划失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("开始初始化AI编排模块数据库...")
    
    # 获取数据库路径
    db_path = get_database_path()
    logger.info(f"数据库路径: {db_path}")
    
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 创建AI编排表
        if not create_ai_tables(cursor):
            logger.error("创建AI编排表失败，退出初始化")
            return False
        
        # 初始化MCP工具配置
        if not init_mcp_tools(cursor):
            logger.error("初始化MCP工具配置失败")
        
        # 创建示例计划
        if not create_sample_plan(cursor):
            logger.error("创建示例计划失败")
        
        # 提交事务
        conn.commit()
        
        logger.info("AI编排模块数据库初始化完成！")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)