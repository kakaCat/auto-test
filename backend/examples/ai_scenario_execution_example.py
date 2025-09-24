#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI场景执行示例

本示例展示如何使用AI代理来智能执行场景：
1. 用户输入场景ID和参数描述
2. AI自动完善参数
3. 查询场景和接口流程
4. 智能遍历和执行接口
5. 处理执行结果
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# 导入AI场景代理
from src.auto_test.agents.scenario_agent import (
    ScenarioAgent,
    get_scenario_agent,
    execute_scenario_with_ai
)

# 导入场景管理模块
from src.auto_test.scenario_management import (
    get_scenario_manager,
    get_scenario_executor,
    ExecutionType
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_demo_data():
    """设置演示数据"""
    database_url = "mysql://user:password@localhost:3306/autotest"
    
    # 获取场景管理器
    scenario_manager = get_scenario_manager(database_url)
    await scenario_manager.initialize_database()
    
    # 创建演示场景
    demo_scenario = {
        'name': '用户注册流程',
        'description': '完整的用户注册流程，包括验证邮箱、创建用户、发送欢迎邮件',
        'execution_type': ExecutionType.SEQUENTIAL,
        'variables': {
            'user_email': '',
            'user_name': '',
            'user_phone': '',
            'verification_code': ''
        },
        'apis': [
            {
                'api_id': 1,
                'execution_order': 1,
                'is_required': True,
                'parameter_mapping': {
                    'email': '${user_email}',
                    'name': '${user_name}',
                    'phone': '${user_phone}'
                },
                'response_mapping': {
                    'verification_code': 'verification_code',
                    'user_id': 'user_id'
                },
                'pre_condition': None
            },
            {
                'api_id': 2,
                'execution_order': 2,
                'is_required': True,
                'parameter_mapping': {
                    'email': '${user_email}',
                    'code': '${verification_code}'
                },
                'response_mapping': {
                    'verified': 'email_verified'
                },
                'pre_condition': '${verification_code} != ""'
            },
            {
                'api_id': 3,
                'execution_order': 3,
                'is_required': True,
                'parameter_mapping': {
                    'user_id': '${user_id}',
                    'email': '${user_email}',
                    'name': '${user_name}'
                },
                'response_mapping': {
                    'welcome_sent': 'email_sent'
                },
                'pre_condition': '${email_verified} == true'
            }
        ]
    }
    
    # 创建场景
    result = await scenario_manager.create_scenario(demo_scenario)
    if result['success']:
        scenario_id = result['scenario_id']
        logger.info(f"演示场景创建成功，ID: {scenario_id}")
        return scenario_id
    else:
        logger.error(f"演示场景创建失败: {result.get('error')}")
        return None


async def demo_basic_ai_execution():
    """演示基本的AI场景执行"""
    print("\n=== 基本AI场景执行演示 ===")
    
    database_url = "mysql://user:password@localhost:3306/autotest"
    
    # 设置演示数据
    scenario_id = await setup_demo_data()
    if not scenario_id:
        print("演示数据设置失败")
        return
    
    # 用户输入（模拟）
    user_description = """
    我要注册一个新用户，邮箱是 john.doe@example.com，
    用户名是 John Doe，手机号是 13800138000
    """
    
    print(f"场景ID: {scenario_id}")
    print(f"用户描述: {user_description.strip()}")
    
    try:
        # 使用AI代理执行场景
        result = await execute_scenario_with_ai(
            scenario_id=scenario_id,
            user_description=user_description,
            database_url=database_url,
            agent_config={
                'auto_enhance_parameters': True,
                'stop_on_first_failure': True,
                'max_retry_attempts': 2
            }
        )
        
        # 显示执行结果
        print("\n--- 执行结果 ---")
        print(f"最终状态: {result.final_status}")
        print(f"成功步骤: {result.success_count}")
        print(f"失败步骤: {result.failure_count}")
        print(f"总执行时间: {result.total_execution_time:.2f}秒")
        
        # 显示参数增强结果
        print("\n--- 参数增强结果 ---")
        enhanced_params = result.request.enhanced_parameters
        for key, value in enhanced_params.items():
            print(f"{key}: {value}")
        
        # 显示执行步骤
        print("\n--- 执行步骤详情 ---")
        for i, step in enumerate(result.execution_steps, 1):
            print(f"步骤 {i}: {step.api_name} (API {step.api_id})")
            print(f"  状态: {step.status}")
            print(f"  执行时间: {step.execution_time:.2f}秒")
            if step.error_message:
                print(f"  错误: {step.error_message}")
            print(f"  输入参数: {step.input_parameters}")
            if step.output_result:
                print(f"  输出结果: {step.output_result}")
            print()
        
        # 显示最终结果
        if result.final_result:
            print("--- 最终结果 ---")
            print(json.dumps(result.final_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"AI场景执行失败: {e}")
        print(f"执行失败: {e}")


async def demo_advanced_ai_execution():
    """演示高级AI场景执行功能"""
    print("\n=== 高级AI场景执行演示 ===")
    
    database_url = "mysql://user:password@localhost:3306/autotest"
    
    # 创建AI代理实例
    agent = get_scenario_agent(
        database_url=database_url,
        agent_config={
            'auto_enhance_parameters': True,
            'stop_on_first_failure': False,  # 不在第一个失败时停止
            'enable_smart_recovery': True,
            'max_retry_attempts': 3
        }
    )
    
    await agent.initialize()
    
    # 测试多个场景执行
    test_cases = [
        {
            'scenario_id': 1,
            'description': '注册用户 alice@test.com，姓名 Alice Smith，电话 13900139000',
            'initial_params': {'priority': 'high'}
        },
        {
            'scenario_id': 1,
            'description': '批量注册用户，邮箱包括 bob@test.com 和 charlie@test.com',
            'initial_params': {'batch_mode': True}
        },
        {
            'scenario_id': 1,
            'description': '注册VIP用户，邮箱 vip@test.com，需要特殊处理',
            'initial_params': {'user_type': 'vip'}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i} ---")
        print(f"场景ID: {test_case['scenario_id']}")
        print(f"描述: {test_case['description']}")
        print(f"初始参数: {test_case['initial_params']}")
        
        try:
            result = await agent.process_scenario_request(
                scenario_id=test_case['scenario_id'],
                user_description=test_case['description'],
                initial_parameters=test_case['initial_params']
            )
            
            print(f"执行结果: {result.final_status}")
            print(f"成功/失败: {result.success_count}/{result.failure_count}")
            
            if result.error_summary:
                print(f"错误摘要: {result.error_summary}")
            
        except Exception as e:
            print(f"执行异常: {e}")
        
        # 短暂延迟
        await asyncio.sleep(1)
    
    # 查看代理状态
    print("\n--- 代理状态 ---")
    status = await agent.get_agent_status()
    print(f"当前状态: {status['state']}")
    print(f"执行次数: {status['execution_count']}")
    print(f"组件状态: {status['components_status']}")
    
    # 查看执行历史
    print("\n--- 执行历史 ---")
    history = await agent.get_execution_history(limit=5)
    for i, record in enumerate(history, 1):
        print(f"记录 {i}:")
        print(f"  场景ID: {record['request']['scenario_id']}")
        print(f"  状态: {record['final_status']}")
        print(f"  执行时间: {record['total_execution_time']:.2f}秒")
        print(f"  步骤数: {len(record['execution_steps'])}")


async def demo_parameter_enhancement():
    """演示参数增强功能"""
    print("\n=== 参数增强功能演示 ===")
    
    database_url = "mysql://user:password@localhost:3306/autotest"
    agent = get_scenario_agent(database_url)
    await agent.initialize()
    
    # 测试不同类型的用户描述
    test_descriptions = [
        "注册用户邮箱：test@example.com，姓名：测试用户",
        "我要创建一个账户，我的邮件地址是 admin@company.com，名字叫 Admin User，手机 13812345678",
        "批量注册用户，包括：user1@test.com (张三)，user2@test.com (李四)，user3@test.com (王五)",
        "VIP用户注册，邮箱 vip@premium.com，需要优先处理",
        "注册企业用户，公司邮箱 contact@enterprise.com，联系人 Business Manager"
    ]
    
    for i, description in enumerate(test_descriptions, 1):
        print(f"\n--- 参数增强测试 {i} ---")
        print(f"原始描述: {description}")
        
        try:
            # 模拟参数增强过程
            scenario_info = {
                'variables': {
                    'user_email': '',
                    'user_name': '',
                    'user_phone': '',
                    'user_type': 'normal',
                    'priority': 'normal'
                },
                'api_details': [
                    {
                        'api_id': 1,
                        'parameter_mapping': {
                            'email': '${user_email}',
                            'name': '${user_name}',
                            'phone': '${user_phone}',
                            'type': '${user_type}'
                        }
                    }
                ]
            }
            
            # 调用参数增强方法
            enhanced_params = await agent._enhance_parameters(
                scenario_info=scenario_info,
                user_description=description,
                raw_parameters={}
            )
            
            print("增强后的参数:")
            for key, value in enhanced_params.items():
                print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"参数增强失败: {e}")


async def demo_execution_monitoring():
    """演示执行监控功能"""
    print("\n=== 执行监控功能演示 ===")
    
    database_url = "mysql://user:password@localhost:3306/autotest"
    agent = get_scenario_agent(database_url)
    await agent.initialize()
    
    # 启动一个长时间运行的场景执行
    print("启动场景执行...")
    
    # 创建一个异步任务
    execution_task = asyncio.create_task(
        agent.process_scenario_request(
            scenario_id=1,
            user_description="长时间运行的测试场景，邮箱 longrun@test.com"
        )
    )
    
    # 监控执行状态
    for i in range(5):
        await asyncio.sleep(1)
        status = await agent.get_agent_status()
        print(f"监控 {i+1}: 代理状态 = {status['state']}")
        
        if status['current_request']:
            print(f"  当前请求: 场景 {status['current_request']['scenario_id']}")
            print(f"  执行ID: {status['current_request']['execution_id']}")
    
    # 等待执行完成
    try:
        result = await execution_task
        print(f"\n执行完成: {result.final_status}")
    except Exception as e:
        print(f"\n执行异常: {e}")
    
    # 演示取消执行
    print("\n--- 取消执行演示 ---")
    
    # 启动另一个执行
    cancel_task = asyncio.create_task(
        agent.process_scenario_request(
            scenario_id=1,
            user_description="将被取消的执行"
        )
    )
    
    # 短暂延迟后取消
    await asyncio.sleep(0.5)
    cancel_result = await agent.cancel_current_execution()
    print(f"取消结果: {cancel_result}")
    
    # 清理任务
    cancel_task.cancel()
    try:
        await cancel_task
    except asyncio.CancelledError:
        print("任务已取消")


async def demo_error_handling():
    """演示错误处理功能"""
    print("\n=== 错误处理功能演示 ===")
    
    database_url = "mysql://user:password@localhost:3306/autotest"
    agent = get_scenario_agent(
        database_url,
        agent_config={
            'stop_on_first_failure': False,
            'enable_smart_recovery': True,
            'max_retry_attempts': 2
        }
    )
    await agent.initialize()
    
    # 测试各种错误情况
    error_test_cases = [
        {
            'scenario_id': 999,  # 不存在的场景
            'description': "测试不存在的场景",
            'expected_error': "场景不存在"
        },
        {
            'scenario_id': 1,
            'description': "无效的参数描述 @@##$$",
            'expected_error': "参数解析错误"
        },
        {
            'scenario_id': 1,
            'description': "正常描述但模拟API失败",
            'expected_error': "API执行失败"
        }
    ]
    
    for i, test_case in enumerate(error_test_cases, 1):
        print(f"\n--- 错误测试 {i}: {test_case['expected_error']} ---")
        print(f"场景ID: {test_case['scenario_id']}")
        print(f"描述: {test_case['description']}")
        
        try:
            result = await agent.process_scenario_request(
                scenario_id=test_case['scenario_id'],
                user_description=test_case['description']
            )
            
            print(f"执行状态: {result.final_status}")
            if result.error_summary:
                print(f"错误摘要: {result.error_summary}")
            
            # 显示失败的步骤
            failed_steps = [step for step in result.execution_steps if step.status in ['failed', 'error']]
            if failed_steps:
                print("失败步骤:")
                for step in failed_steps:
                    print(f"  - {step.api_name}: {step.error_message}")
            
        except Exception as e:
            print(f"捕获异常: {e}")


async def main():
    """主函数"""
    print("AI场景执行代理演示")
    print("=" * 50)
    
    try:
        # 基本功能演示
        await demo_basic_ai_execution()
        
        # 高级功能演示
        await demo_advanced_ai_execution()
        
        # 参数增强演示
        await demo_parameter_enhancement()
        
        # 执行监控演示
        await demo_execution_monitoring()
        
        # 错误处理演示
        await demo_error_handling()
        
        print("\n=== 演示完成 ===")
        
    except Exception as e:
        logger.error(f"演示执行失败: {e}")
        print(f"演示失败: {e}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())