#!/usr/bin/env python3
"""
AI编排模块测试脚本

测试AI编排模块的基本功能：
1. MCP工具注册和调用
2. 意图理解
3. 流程规划
4. 计划校验

使用方法：
python test_orchestration.py
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auto_test.mcp.client import MCPClient
from auto_test.agents.intent_parser import IntentParser
from auto_test.agents.flow_planner import FlowPlanner
from auto_test.config import Config
from auto_test.utils.logger import get_logger

logger = get_logger(__name__)


async def test_mcp_client():
    """测试MCP客户端"""
    print("\n=== 测试MCP客户端 ===")
    
    try:
        config = Config()
        client = MCPClient()
        
        # 初始化客户端
        await client.initialize()
        print("✅ MCP客户端初始化成功")
        
        # 获取工具列表
        tools = await client.list_tools()
        print(f"✅ 获取到 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 测试HTTP工具调用
        if tools:
            tool_name = tools[0]['name']
            print(f"\n测试工具调用: {tool_name}")
            
            if tool_name == 'http_request':
                result = await client.call_tool(tool_name, {
                    'method': 'GET',
                    'url': 'https://httpbin.org/get'
                })
                
                if result['success']:
                    print("✅ HTTP工具调用成功")
                    print(f"  状态码: {result['result'].get('status_code')}")
                else:
                    print(f"❌ HTTP工具调用失败: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP客户端测试失败: {e}")
        return False


async def test_intent_parser():
    """测试意图理解"""
    print("\n=== 测试意图理解 ===")
    
    try:
        config = Config()
        parser = IntentParser(config)
        
        # 测试用例
        test_inputs = [
            "测试用户注册接口",
            "调用获取用户信息的API",
            "验证登录接口返回的数据格式"
        ]
        
        for user_input in test_inputs:
            print(f"\n测试输入: {user_input}")
            
            result = await parser.run({
                'user_input': user_input
            })
            
            if result['success']:
                intent_result = result['result']
                print(f"✅ 意图识别: {intent_result.get('intent')}")
                print(f"  置信度: {intent_result.get('confidence', 0):.2f}")
                print(f"  动作数量: {len(intent_result.get('actions', []))}")
            else:
                print(f"❌ 意图理解失败: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 意图理解测试失败: {e}")
        return False


async def test_flow_planner():
    """测试流程规划"""
    print("\n=== 测试流程规划 ===")
    
    try:
        config = Config()
        planner = FlowPlanner(config)
        
        # 模拟意图理解结果
        mock_intent_result = {
            'intent': 'api_test',
            'confidence': 0.9,
            'entities': {
                'api_endpoints': ['/api/users/register', '/api/users/login'],
                'parameters': {'username': 'testuser', 'password': 'test123'},
                'validation_rules': ['status_code == 200']
            },
            'actions': [
                {
                    'action': 'api_call',
                    'target': '/api/users/register',
                    'parameters': {
                        'method': 'POST',
                        'body': {'username': 'testuser', 'password': 'test123'}
                    },
                    'dependencies': [],
                    'timeout': 30
                },
                {
                    'action': 'api_call',
                    'target': '/api/users/login',
                    'parameters': {
                        'method': 'POST',
                        'body': {'username': 'testuser', 'password': 'test123'}
                    },
                    'dependencies': ['step_1'],
                    'timeout': 30
                }
            ]
        }
        
        result = await planner.run({
            'intent_result': mock_intent_result,
            'context': {}
        })
        
        if result['success']:
            plan = result['result']['execution_plan']
            print(f"✅ 流程规划成功")
            print(f"  计划ID: {plan.get('plan_id')}")
            print(f"  步骤数量: {len(plan.get('steps', []))}")
            print(f"  预估时长: {plan.get('estimated_duration')}秒")
            
            # 显示步骤详情
            for step in plan.get('steps', []):
                print(f"  步骤: {step.get('step_id')} - {step.get('step_name')}")
        else:
            print(f"❌ 流程规划失败: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 流程规划测试失败: {e}")
        return False


async def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            # 测试工具列表API
            async with session.get('http://127.0.0.1:8002/api/orchestration/tools') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('success'):
                        print("✅ 工具列表API正常")
                        tools = data.get('data', [])
                        print(f"  可用工具: {len(tools)}个")
                    else:
                        print(f"❌ 工具列表API返回错误: {data.get('message')}")
                else:
                    print(f"❌ 工具列表API请求失败: {resp.status}")
            
            # 测试计划生成API
            plan_data = {
                'intent_text': '测试用户注册接口',
                'context': {}
            }
            
            async with session.post(
                'http://127.0.0.1:8002/api/orchestration/plan/generate',
                json=plan_data
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('success'):
                        print("✅ 计划生成API正常")
                        plan = data.get('data', {}).get('plan', {})
                        print(f"  生成步骤: {len(plan.get('steps', []))}个")
                    else:
                        print(f"❌ 计划生成API返回错误: {data.get('message')}")
                else:
                    print(f"❌ 计划生成API请求失败: {resp.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始AI编排模块测试...")
    
    # 测试结果
    results = []
    
    # 1. 测试MCP客户端
    results.append(await test_mcp_client())
    
    # 2. 测试意图理解
    results.append(await test_intent_parser())
    
    # 3. 测试流程规划
    results.append(await test_flow_planner())
    
    # 4. 测试API端点
    results.append(await test_api_endpoints())
    
    # 汇总结果
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 测试结果汇总:")
    print(f"  通过: {passed}/{total}")
    print(f"  成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！AI编排模块基本功能正常")
    else:
        print("⚠️  部分测试失败，需要进一步调试")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)