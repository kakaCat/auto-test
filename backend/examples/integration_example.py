#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成模块使用示例

本示例展示如何使用集成模块来统一管理API和工作流编排，
实现完整的接口流程自动化解决方案。
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# 导入集成模块
from src.auto_test.integration import (
    get_integrated_manager,
    get_workflow_api_bridge,
    get_unified_monitor,
    get_batch_processor,
    initialize_integration,
    get_system_status
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_integration():
    """演示基本集成功能"""
    print("\n=== 基本集成功能演示 ===")
    
    # 初始化集成模块
    print("1. 初始化集成模块...")
    init_result = await initialize_integration()
    print(f"初始化结果: {init_result}")
    
    # 获取管理器实例
    manager = get_integrated_manager()
    
    # 录入示例API
    print("\n2. 录入示例API...")
    api1 = await manager.record_api(
        name="获取用户信息",
        url="https://jsonplaceholder.typicode.com/users/1",
        method="GET",
        description="获取用户详细信息"
    )
    print(f"录入API: {api1['name']} (ID: {api1['id']})")
    
    api2 = await manager.record_api(
        name="获取用户文章",
        url="https://jsonplaceholder.typicode.com/users/{user_id}/posts",
        method="GET",
        description="获取指定用户的文章列表"
    )
    print(f"录入API: {api2['name']} (ID: {api2['id']})")
    
    # 创建工作流
    print("\n3. 创建工作流...")
    workflow = await manager.create_workflow(
        name="用户信息获取流程",
        description="获取用户信息并获取其文章列表"
    )
    print(f"创建工作流: {workflow['name']} (ID: {workflow['id']})")
    
    # 添加节点
    print("\n4. 添加工作流节点...")
    start_node = await manager.add_workflow_node(
        workflow_id=workflow['id'],
        node_type="START",
        name="开始"
    )
    
    api1_node = await manager.add_workflow_node(
        workflow_id=workflow['id'],
        node_type="API_CALL",
        name="获取用户信息",
        config={"api_id": api1['id']}
    )
    
    api2_node = await manager.add_workflow_node(
        workflow_id=workflow['id'],
        node_type="API_CALL",
        name="获取用户文章",
        config={
            "api_id": api2['id'],
            "parameter_mapping": {
                "user_id": "${previous.response.id}"
            }
        }
    )
    
    end_node = await manager.add_workflow_node(
        workflow_id=workflow['id'],
        node_type="END",
        name="结束"
    )
    
    # 添加连接
    print("\n5. 添加节点连接...")
    await manager.add_workflow_connection(
        workflow_id=workflow['id'],
        source_node_id=start_node['id'],
        target_node_id=api1_node['id']
    )
    
    await manager.add_workflow_connection(
        workflow_id=workflow['id'],
        source_node_id=api1_node['id'],
        target_node_id=api2_node['id']
    )
    
    await manager.add_workflow_connection(
        workflow_id=workflow['id'],
        source_node_id=api2_node['id'],
        target_node_id=end_node['id']
    )
    
    # 执行工作流
    print("\n6. 执行工作流...")
    execution = await manager.execute_workflow(
        workflow_id=workflow['id'],
        parameters={"user_id": 1}
    )
    print(f"工作流执行ID: {execution['execution_id']}")
    
    # 等待执行完成
    print("\n7. 等待执行完成...")
    await asyncio.sleep(5)
    
    # 获取执行状态
    status = await manager.get_workflow_execution_status(execution['execution_id'])
    print(f"执行状态: {status['status']}")
    if status.get('result'):
        print(f"执行结果: {json.dumps(status['result'], indent=2, ensure_ascii=False)}")


async def demo_batch_operations():
    """演示批量操作功能"""
    print("\n=== 批量操作功能演示 ===")
    
    batch_processor = get_batch_processor()
    
    # 批量导入API
    print("\n1. 批量导入API...")
    apis_data = [
        {
            "name": "获取所有用户",
            "url": "https://jsonplaceholder.typicode.com/users",
            "method": "GET",
            "description": "获取所有用户列表"
        },
        {
            "name": "获取所有文章",
            "url": "https://jsonplaceholder.typicode.com/posts",
            "method": "GET",
            "description": "获取所有文章列表"
        },
        {
            "name": "获取所有评论",
            "url": "https://jsonplaceholder.typicode.com/comments",
            "method": "GET",
            "description": "获取所有评论列表"
        }
    ]
    
    import_result = await batch_processor.batch_import_apis(apis_data, validate=True)
    print(f"批量导入结果: 成功 {import_result['success']}, 失败 {import_result['failed']}")
    
    # 批量测试API
    if import_result['imported_apis']:
        print("\n2. 批量测试API...")
        api_ids = [api['id'] for api in import_result['imported_apis']]
        test_result = await batch_processor.batch_test_apis(api_ids, concurrent_limit=3)
        print(f"批量测试结果: 成功 {test_result['success']}, 失败 {test_result['failed']}")
        
        # 显示测试详情
        for result in test_result['test_results']:
            status = "✓" if result['success'] else "✗"
            print(f"  {status} API {result['api_id']}: {result.get('execution_time', 0):.2f}s")
    
    # 创建批量工作流
    print("\n3. 批量创建工作流...")
    workflows_data = [
        {
            "name": "数据收集流程",
            "description": "收集用户、文章和评论数据",
            "nodes": [
                {"id": "start", "name": "开始", "type": "START"},
                {"id": "users", "name": "获取用户", "type": "API_CALL", "config": {"api_name": "获取所有用户"}},
                {"id": "posts", "name": "获取文章", "type": "API_CALL", "config": {"api_name": "获取所有文章"}},
                {"id": "end", "name": "结束", "type": "END"}
            ],
            "connections": [
                {"source_node": "start", "target_node": "users"},
                {"source_node": "users", "target_node": "posts"},
                {"source_node": "posts", "target_node": "end"}
            ]
        }
    ]
    
    workflow_result = await batch_processor.batch_create_workflows(workflows_data)
    print(f"批量创建工作流结果: 成功 {workflow_result['success']}, 失败 {workflow_result['failed']}")


async def demo_monitoring_analysis():
    """演示监控分析功能"""
    print("\n=== 监控分析功能演示 ===")
    
    monitor = get_unified_monitor()
    
    # 获取系统仪表板
    print("\n1. 获取系统仪表板...")
    dashboard = await monitor.get_system_dashboard()
    print(f"系统健康评分: {dashboard['health_score']:.1f}")
    print(f"API管理状态: {dashboard.get('api_management', {})}")
    print(f"工作流状态: {dashboard.get('workflow_orchestration', {})}")
    
    if dashboard.get('alerts'):
        print(f"\n系统告警 ({len(dashboard['alerts'])}个):")
        for alert in dashboard['alerts'][:5]:  # 显示前5个告警
            print(f"  - [{alert['severity']}] {alert['message']}")
    
    # API性能分析
    print("\n2. API性能分析...")
    try:
        api_analysis = await monitor.get_api_performance_analysis(time_range=1)  # 最近1小时
        print(f"总API调用次数: {api_analysis['total_calls']}")
        
        if api_analysis.get('api_performance'):
            print("API性能详情:")
            for api_id, perf in list(api_analysis['api_performance'].items())[:3]:  # 显示前3个
                print(f"  - {perf['api_name']}: 成功率 {perf['success_rate']:.1%}, 平均响应时间 {perf['avg_response_time']:.2f}s")
    except Exception as e:
        print(f"API性能分析暂无数据: {e}")
    
    # 工作流执行分析
    print("\n3. 工作流执行分析...")
    try:
        workflow_analysis = await monitor.get_workflow_execution_analysis(time_range=1)
        print(f"总执行次数: {workflow_analysis['total_executions']}")
        print(f"成功率: {workflow_analysis['success_rate']:.1%}")
        print(f"平均执行时间: {workflow_analysis['execution_time_stats']['avg_time']:.2f}s")
    except Exception as e:
        print(f"工作流执行分析暂无数据: {e}")
    
    # 错误分析
    print("\n4. 错误分析...")
    try:
        error_analysis = await monitor.get_error_analysis(time_range=1)
        print(f"API错误数: {error_analysis['api_errors']['total_count']}")
        print(f"工作流错误数: {error_analysis['workflow_errors']['total_count']}")
        
        if error_analysis.get('recommendations'):
            print("改进建议:")
            for rec in error_analysis['recommendations'][:3]:
                print(f"  - {rec}")
    except Exception as e:
        print(f"错误分析暂无数据: {e}")


async def demo_data_import_export():
    """演示数据导入导出功能"""
    print("\n=== 数据导入导出功能演示 ===")
    
    batch_processor = get_batch_processor()
    
    # 创建示例数据目录
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 导出API数据
    print("\n1. 导出API数据...")
    try:
        api_export = await batch_processor.export_to_file(
            file_path=str(data_dir / "apis_export.json"),
            data_type="apis"
        )
        print(f"导出API数据: {api_export['record_count']}条记录, 文件大小: {api_export['file_size']}字节")
    except Exception as e:
        print(f"导出API数据失败: {e}")
    
    # 导出工作流数据
    print("\n2. 导出工作流数据...")
    try:
        workflow_export = await batch_processor.export_to_file(
            file_path=str(data_dir / "workflows_export.json"),
            data_type="workflows"
        )
        print(f"导出工作流数据: {workflow_export['record_count']}条记录, 文件大小: {workflow_export['file_size']}字节")
    except Exception as e:
        print(f"导出工作流数据失败: {e}")
    
    # 导出执行记录
    print("\n3. 导出执行记录...")
    try:
        execution_export = await batch_processor.export_to_file(
            file_path=str(data_dir / "executions_export.json"),
            data_type="executions"
        )
        print(f"导出执行记录: {execution_export['record_count']}条记录, 文件大小: {execution_export['file_size']}字节")
    except Exception as e:
        print(f"导出执行记录失败: {e}")
    
    # 数据备份
    print("\n4. 创建数据备份...")
    try:
        backup_result = await batch_processor.backup_data(str(data_dir / "backup"))
        print(f"备份完成: {backup_result['timestamp']}")
        print(f"备份文件:")
        for data_type, info in backup_result['files'].items():
            print(f"  - {data_type}: {info['records']}条记录, {info['size']}字节")
    except Exception as e:
        print(f"数据备份失败: {e}")


async def demo_advanced_workflow():
    """演示高级工作流功能"""
    print("\n=== 高级工作流功能演示 ===")
    
    manager = get_integrated_manager()
    bridge = get_workflow_api_bridge()
    
    # 创建条件分支工作流
    print("\n1. 创建条件分支工作流...")
    try:
        workflow = await manager.create_conditional_workflow(
            name="用户状态检查流程",
            description="根据用户状态执行不同操作",
            api_configs=[
                {
                    "name": "检查用户状态",
                    "url": "https://jsonplaceholder.typicode.com/users/1",
                    "method": "GET"
                },
                {
                    "name": "激活用户",
                    "url": "https://jsonplaceholder.typicode.com/users/1",
                    "method": "PUT",
                    "body": {"active": True}
                }
            ],
            condition="${response.id} > 0"
        )
        print(f"创建条件工作流: {workflow['name']} (ID: {workflow['id']})")
        
        # 执行条件工作流
        execution = await manager.execute_workflow(
            workflow_id=workflow['id'],
            parameters={"user_id": 1}
        )
        print(f"执行ID: {execution['execution_id']}")
        
    except Exception as e:
        print(f"创建条件工作流失败: {e}")
    
    # API推荐
    print("\n2. API推荐功能...")
    try:
        # 模拟工作流节点配置
        node_config = {
            "description": "获取用户信息",
            "expected_response": "user data with id, name, email"
        }
        
        recommendations = await bridge.recommend_apis_for_node(node_config)
        if recommendations:
            print("推荐的API:")
            for rec in recommendations[:3]:
                print(f"  - {rec['api_name']} (匹配度: {rec['score']:.2f})")
        else:
            print("暂无API推荐")
            
    except Exception as e:
        print(f"API推荐失败: {e}")
    
    # 使用情况分析
    print("\n3. API使用情况分析...")
    try:
        usage_analysis = await bridge.analyze_api_usage()
        print(f"分析了 {len(usage_analysis.get('api_usage', {}))} 个API的使用情况")
        
        if usage_analysis.get('recommendations'):
            print("优化建议:")
            for rec in usage_analysis['recommendations'][:3]:
                print(f"  - {rec}")
                
    except Exception as e:
        print(f"使用情况分析失败: {e}")


async def demo_system_status():
    """演示系统状态检查"""
    print("\n=== 系统状态检查 ===")
    
    # 获取系统状态
    status = await get_system_status()
    print(f"系统初始化状态: {'已初始化' if status['initialized'] else '未初始化'}")
    print(f"系统健康评分: {status['health_score']:.1f}")
    print(f"告警数量: {status['alerts_count']}")
    
    if status.get('error'):
        print(f"系统错误: {status['error']}")
    
    # 显示组件状态
    components = status.get('components_status', {})
    if components:
        print("\n组件状态:")
        for component, data in components.items():
            if isinstance(data, dict) and data:
                print(f"  - {component}: 正常运行")
                if 'total_calls' in data:
                    print(f"    总调用次数: {data['total_calls']}")
                if 'success_rate' in data:
                    print(f"    成功率: {data['success_rate']:.1%}")
            else:
                print(f"  - {component}: 无数据")


async def main():
    """主函数"""
    print("接口流程编排集成模块演示")
    print("=" * 50)
    
    try:
        # 基本集成功能
        await demo_basic_integration()
        
        # 批量操作功能
        await demo_batch_operations()
        
        # 监控分析功能
        await demo_monitoring_analysis()
        
        # 数据导入导出功能
        await demo_data_import_export()
        
        # 高级工作流功能
        await demo_advanced_workflow()
        
        # 系统状态检查
        await demo_system_status()
        
        print("\n=== 演示完成 ===")
        print("\n集成模块功能演示已完成！")
        print("您可以根据需要使用以下功能:")
        print("1. 统一的API和工作流管理")
        print("2. 批量操作和数据处理")
        print("3. 实时监控和性能分析")
        print("4. 数据导入导出和备份")
        print("5. 高级工作流编排")
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {e}")
        print(f"\n演示失败: {e}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())