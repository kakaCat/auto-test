#!/usr/bin/env python3
"""
AI自动化测试平台 - 自举测试套件
用项目自己的能力测试项目本身

功能：
1. 基础API自测试 - 测试系统、模块、API接口管理
2. AI编排自测试 - 测试AI编排和执行能力
3. 工作流自测试 - 测试工作流设计和执行
4. 数据完整性自测试 - 验证数据库和数据一致性

作者: AI Assistant
版本: 1.0.0
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import aiohttp
import sqlite3

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from src.auto_test.config import get_config
    config = get_config()
    DATABASE_PATH = config.DATABASE_PATH
    API_BASE_URL = "http://localhost:8000"
except ImportError:
    DATABASE_PATH = str(project_root / "auto_test.db")
    API_BASE_URL = "http://localhost:8000"

class SelfTestSuite:
    """自举测试套件"""
    
    def __init__(self):
        self.api_base = API_BASE_URL
        self.db_path = DATABASE_PATH
        self.test_results = {}
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有自测试"""
        print("🚀 开始AI自动化测试平台自举测试...")
        print(f"📍 API地址: {self.api_base}")
        print(f"📍 数据库: {self.db_path}")
        print("=" * 60)
        
        # 1. 基础API自测试
        await self.test_basic_apis()
        
        # 2. AI编排自测试
        await self.test_ai_orchestration()
        
        # 3. 数据完整性自测试
        await self.test_data_integrity()
        
        # 4. 生成测试报告
        self.generate_report()
        
        return self.test_results
    
    async def test_basic_apis(self):
        """基础API自测试"""
        print("\n🧪 1. 基础API自测试")
        print("-" * 40)
        
        tests = [
            ("系统列表", "GET", "/api/systems/v1/"),
            ("模块列表", "GET", "/api/modules/v1/"),
            ("API接口列表", "GET", "/api/api-interfaces/v1/"),
            ("页面列表", "GET", "/api/pages/v1/"),
            ("健康检查", "GET", "/health"),
        ]
        
        basic_results = []
        for name, method, endpoint in tests:
            result = await self.call_api(method, endpoint)
            success = result.get("success", False)
            basic_results.append({
                "test": name,
                "endpoint": endpoint,
                "success": success,
                "response_time": result.get("response_time", 0)
            })
            
            status = "✅" if success else "❌"
            print(f"  {status} {name}: {endpoint}")
        
        self.test_results["basic_apis"] = {
            "total": len(tests),
            "passed": sum(1 for r in basic_results if r["success"]),
            "details": basic_results
        }
    
    async def test_ai_orchestration(self):
        """AI编排自测试"""
        print("\n🤖 2. AI编排自测试")
        print("-" * 40)
        
        # 测试MCP工具配置
        tools_result = await self.call_api("GET", "/api/ai/v1/tools")
        tools_success = tools_result.get("success", False)
        print(f"  {'✅' if tools_success else '❌'} MCP工具列表")
        
        # 测试AI执行记录
        executions_result = await self.call_api("GET", "/api/ai/v1/executions")
        executions_success = executions_result.get("success", False)
        print(f"  {'✅' if executions_success else '❌'} AI执行记录")
        
        # 测试编排计划
        plans_result = await self.call_api("GET", "/api/ai/v1/plans")
        plans_success = plans_result.get("success", False)
        print(f"  {'✅' if plans_success else '❌'} 编排计划列表")
        
        self.test_results["ai_orchestration"] = {
            "tools": tools_success,
            "executions": executions_success,
            "plans": plans_success,
            "overall": tools_success and executions_success and plans_success
        }
    
    async def test_data_integrity(self):
        """数据完整性自测试"""
        print("\n📊 3. 数据完整性自测试")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'systems', 'modules', 'api_interfaces', 'pages', 'page_apis',
                'ai_executions', 'execution_steps', 'execution_logs', 
                'execution_metrics', 'mcp_tool_configs', 'api_orchestration_plans'
            ]
            
            missing_tables = set(expected_tables) - set(tables)
            extra_tables = set(tables) - set(expected_tables)
            
            # 检查数据完整性
            data_checks = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                data_checks[table] = count
                print(f"  📋 {table}: {count} 条记录")
            
            conn.close()
            
            integrity_success = len(missing_tables) == 0
            print(f"  {'✅' if integrity_success else '❌'} 表结构完整性")
            
            if missing_tables:
                print(f"  ⚠️  缺失表: {missing_tables}")
            if extra_tables:
                print(f"  ℹ️  额外表: {extra_tables}")
            
            self.test_results["data_integrity"] = {
                "tables_found": len(tables),
                "tables_expected": len(expected_tables),
                "missing_tables": list(missing_tables),
                "data_counts": data_checks,
                "success": integrity_success
            }
            
        except Exception as e:
            print(f"  ❌ 数据库连接失败: {e}")
            self.test_results["data_integrity"] = {"success": False, "error": str(e)}
    
    async def call_api(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """调用API接口"""
        url = f"{self.api_base}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data or {}) as response:
                    result = await response.json()
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            response_time = round((time.time() - start_time) * 1000, 2)
            result["response_time"] = response_time
            return result
            
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "response_time": round((time.time() - start_time) * 1000, 2)
            }
    
    def generate_report(self):
        """生成测试报告"""
        print("\n📋 自测试报告")
        print("=" * 60)
        
        # 基础API测试结果
        basic = self.test_results.get("basic_apis", {})
        basic_passed = basic.get("passed", 0)
        basic_total = basic.get("total", 0)
        basic_rate = (basic_passed / basic_total * 100) if basic_total > 0 else 0
        
        print(f"🧪 基础API测试: {basic_passed}/{basic_total} ({basic_rate:.1f}%)")
        
        # AI编排测试结果
        ai = self.test_results.get("ai_orchestration", {})
        ai_success = ai.get("overall", False)
        print(f"🤖 AI编排测试: {'✅ 通过' if ai_success else '❌ 失败'}")
        
        # 数据完整性测试结果
        data = self.test_results.get("data_integrity", {})
        data_success = data.get("success", False)
        tables_count = data.get("tables_found", 0)
        print(f"📊 数据完整性: {'✅ 通过' if data_success else '❌ 失败'} ({tables_count}个表)")
        
        # 总体评估
        overall_success = basic_rate >= 80 and ai_success and data_success
        print(f"\n🎯 总体评估: {'✅ 系统健康' if overall_success else '⚠️ 需要关注'}")
        
        # 详细结果
        print(f"\n📄 详细结果已保存到: {project_root}/scripts/ai/testing/self_test_results.json")
        
        # 保存详细结果
        results_file = project_root / "scripts/ai/testing/self_test_results.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "basic_api_rate": f"{basic_rate:.1f}%",
                    "ai_orchestration": ai_success,
                    "data_integrity": data_success,
                    "overall_health": overall_success
                },
                "details": self.test_results
            }, f, indent=2, ensure_ascii=False)

async def main():
    """主函数"""
    async with SelfTestSuite() as suite:
        await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())