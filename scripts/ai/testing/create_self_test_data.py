#!/usr/bin/env python3
"""
为自测试创建测试数据
在系统中注册"AI测试平台"作为被测试系统

作者: AI Assistant
版本: 1.0.0
"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from src.auto_test.config import get_config
    config = get_config()
    DATABASE_PATH = config.DATABASE_PATH
except ImportError:
    DATABASE_PATH = str(project_root / "auto_test.db")

import sqlite3

def create_self_test_data():
    """创建自测试数据"""
    print("🔧 创建自测试数据...")
    print(f"📍 数据库: {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. 创建"AI测试平台"系统
        system_data = {
            "name": "AI测试平台",
            "description": "AI驱动的自动化测试平台 - 自测试目标系统",
            "status": "active",
            "category": "self_test"
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO systems (name, description, status, category)
            VALUES (?, ?, ?, ?)
        """, (system_data["name"], system_data["description"], 
              system_data["status"], system_data["category"]))
        
        system_id = cursor.lastrowid
        print(f"✅ 创建系统: {system_data['name']} (ID: {system_id})")
        
        # 2. 创建测试模块
        modules = [
            {"name": "系统管理", "description": "系统和模块管理功能", "path": "/api/systems"},
            {"name": "API管理", "description": "API接口管理功能", "path": "/api/api-interfaces"},
            {"name": "AI编排", "description": "AI编排和执行功能", "path": "/api/ai"},
            {"name": "页面管理", "description": "页面和页面API管理", "path": "/api/pages"},
            {"name": "健康检查", "description": "系统健康状态检查", "path": "/health"}
        ]
        
        module_ids = []
        for module in modules:
            cursor.execute("""
                INSERT OR REPLACE INTO modules (system_id, name, description, path, status)
                VALUES (?, ?, ?, ?, ?)
            """, (system_id, module["name"], module["description"], module["path"], "active"))
            
            module_id = cursor.lastrowid
            module_ids.append(module_id)
            print(f"✅ 创建模块: {module['name']} (ID: {module_id})")
        
        # 3. 创建API接口
        apis = [
            # 系统管理API
            {"module_idx": 0, "name": "获取系统列表", "method": "GET", "path": "/api/systems/v1/", "description": "获取所有系统列表"},
            {"module_idx": 0, "name": "创建系统", "method": "POST", "path": "/api/systems/v1/", "description": "创建新系统"},
            
            # API管理API
            {"module_idx": 1, "name": "获取API列表", "method": "GET", "path": "/api/api-interfaces/v1/", "description": "获取API接口列表"},
            {"module_idx": 1, "name": "测试API", "method": "POST", "path": "/api/api-interfaces/v1/{id}/test", "description": "测试指定API接口"},
            
            # AI编排API
            {"module_idx": 2, "name": "获取MCP工具", "method": "GET", "path": "/api/ai/v1/tools", "description": "获取MCP工具列表"},
            {"module_idx": 2, "name": "获取执行记录", "method": "GET", "path": "/api/ai/v1/executions", "description": "获取AI执行记录"},
            
            # 页面管理API
            {"module_idx": 3, "name": "获取页面列表", "method": "GET", "path": "/api/pages/v1/", "description": "获取页面列表"},
            
            # 健康检查API
            {"module_idx": 4, "name": "健康检查", "method": "GET", "path": "/health", "description": "系统健康状态检查"}
        ]
        
        for api in apis:
            module_id = module_ids[api["module_idx"]]
            cursor.execute("""
                INSERT OR REPLACE INTO api_interfaces 
                (system_id, module_id, name, method, path, description, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (system_id, module_id, api["name"], api["method"], api["path"], 
                  api["description"], "active"))
            
            api_id = cursor.lastrowid
            print(f"✅ 创建API: {api['name']} (ID: {api_id})")
        
        # 4. 创建自测试页面
        cursor.execute("""
            INSERT OR REPLACE INTO pages (system_id, name, description, route_path, page_type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (system_id, "自测试仪表板", "AI测试平台自举测试仪表板", "/self-test", "dashboard", "active"))
        
        page_id = cursor.lastrowid
        print(f"✅ 创建页面: 自测试仪表板 (ID: {page_id})")
        
        # 5. 关联页面与API
        cursor.execute("SELECT id FROM api_interfaces WHERE module_id IN ({})".format(
            ','.join('?' * len(module_ids))), module_ids)
        api_ids = [row[0] for row in cursor.fetchall()]
        
        for i, api_id in enumerate(api_ids):
            cursor.execute("""
                INSERT OR REPLACE INTO page_apis (page_id, api_id, execution_order, api_purpose)
                VALUES (?, ?, ?, ?)
            """, (page_id, api_id, i + 1, "自测试API调用"))
        
        print(f"✅ 关联页面API: {len(api_ids)} 个接口")
        
        conn.commit()
        print(f"\n🎉 自测试数据创建完成！")
        print(f"📊 系统ID: {system_id}")
        print(f"📊 模块数: {len(modules)}")
        print(f"📊 API数: {len(apis)}")
        
    except Exception as e:
        print(f"❌ 创建自测试数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_self_test_data()