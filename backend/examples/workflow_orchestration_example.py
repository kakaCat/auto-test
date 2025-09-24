#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流编排模块使用示例

本示例展示如何使用工作流编排模块来创建、执行和监控接口调用流程。
包括：
1. 创建工作流定义
2. 添加节点和连接
3. 执行工作流
4. 监控执行状态
5. 查看执行结果
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 导入工作流编排模块
from src.auto_test.workflow_orchestration import (
    WorkflowOrchestrator,
    WorkflowExecutor,
    WorkflowMonitor,
    NodeType,
    ConnectionType,
    get_workflow_db_manager
)

# 导入API管理模块
from src.auto_test.api_management import (
    APIRecorder,
    APICaller,
    get_api_db_manager
)


class WorkflowExample:
    """工作流编排示例类"""
    
    def __init__(self):
        """初始化示例"""
        self.orchestrator = WorkflowOrchestrator()
        self.executor = WorkflowExecutor()
        self.monitor = WorkflowMonitor()
        self.api_recorder = APIRecorder()
        self.api_caller = APICaller()
        
    async def setup_database(self):
        """设置数据库"""
        print("正在初始化数据库...")
        
        # 初始化工作流数据库
        workflow_db = get_workflow_db_manager()
        await workflow_db.create_tables()
        
        # 初始化API管理数据库
        api_db = get_api_db_manager()
        await api_db.create_tables()
        
        print("数据库初始化完成")
    
    async def setup_sample_apis(self):
        """设置示例API"""
        print("正在录入示例API...")
        
        # 录入用户登录API
        login_api = await self.api_recorder.record_api(
            name="用户登录",
            url="https://api.example.com/auth/login",
            method="POST",
            headers={"Content-Type": "application/json"},
            request_body={
                "username": "{{username}}",
                "password": "{{password}}"
            },
            description="用户登录接口",
            tags=["auth", "login"]
        )
        
        # 录入获取用户信息API
        user_info_api = await self.api_recorder.record_api(
            name="获取用户信息",
            url="https://api.example.com/user/profile",
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {{token}}"
            },
            description="获取用户详细信息",
            tags=["user", "profile"]
        )
        
        # 录入更新用户信息API
        update_user_api = await self.api_recorder.record_api(
            name="更新用户信息",
            url="https://api.example.com/user/profile",
            method="PUT",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {{token}}"
            },
            request_body={
                "name": "{{name}}",
                "email": "{{email}}"
            },
            description="更新用户信息接口",
            tags=["user", "update"]
        )
        
        print(f"已录入API: {login_api.id}, {user_info_api.id}, {update_user_api.id}")
        return login_api.id, user_info_api.id, update_user_api.id
    
    async def create_sample_workflow(self, login_api_id: int, user_info_api_id: int, update_user_api_id: int):
        """创建示例工作流"""
        print("正在创建示例工作流...")
        
        # 创建工作流定义
        workflow = await self.orchestrator.create_workflow(
            name="用户信息管理流程",
            description="完整的用户登录、获取信息、更新信息流程",
            version="1.0",
            tags=["user", "management"]
        )
        
        print(f"创建工作流: {workflow.id} - {workflow.name}")
        
        # 添加开始节点
        start_node = await self.orchestrator.add_node(
            workflow.id,
            name="开始",
            node_type=NodeType.START,
            description="流程开始"
        )
        
        # 添加登录节点
        login_node = await self.orchestrator.add_node(
            workflow.id,
            name="用户登录",
            node_type=NodeType.API_CALL,
            config={
                "api_id": login_api_id,
                "parameters": {
                    "username": "{{input.username}}",
                    "password": "{{input.password}}"
                },
                "output_mapping": {
                    "token": "response.data.token",
                    "user_id": "response.data.user_id"
                }
            },
            description="执行用户登录"
        )
        
        # 添加条件判断节点
        condition_node = await self.orchestrator.add_node(
            workflow.id,
            name="登录结果判断",
            node_type=NodeType.CONDITION,
            config={
                "condition": "{{login.response.status}} == 200",
                "true_path": "获取用户信息",
                "false_path": "登录失败处理"
            },
            description="判断登录是否成功"
        )
        
        # 添加获取用户信息节点
        get_user_node = await self.orchestrator.add_node(
            workflow.id,
            name="获取用户信息",
            node_type=NodeType.API_CALL,
            config={
                "api_id": user_info_api_id,
                "parameters": {
                    "token": "{{login.token}}"
                },
                "output_mapping": {
                    "user_info": "response.data"
                }
            },
            description="获取用户详细信息"
        )
        
        # 添加更新用户信息节点
        update_user_node = await self.orchestrator.add_node(
            workflow.id,
            name="更新用户信息",
            node_type=NodeType.API_CALL,
            config={
                "api_id": update_user_api_id,
                "parameters": {
                    "token": "{{login.token}}",
                    "name": "{{input.new_name}}",
                    "email": "{{input.new_email}}"
                },
                "condition": "{{input.should_update}} == true"
            },
            description="更新用户信息（可选）"
        )
        
        # 添加结束节点
        end_node = await self.orchestrator.add_node(
            workflow.id,
            name="结束",
            node_type=NodeType.END,
            description="流程结束"
        )
        
        # 添加失败处理节点
        failure_node = await self.orchestrator.add_node(
            workflow.id,
            name="登录失败处理",
            node_type=NodeType.END,
            config={
                "error_message": "登录失败，请检查用户名和密码"
            },
            description="处理登录失败情况"
        )
        
        # 创建连接关系
        connections = [
            (start_node.id, login_node.id, ConnectionType.SEQUENCE),
            (login_node.id, condition_node.id, ConnectionType.SEQUENCE),
            (condition_node.id, get_user_node.id, ConnectionType.CONDITIONAL_TRUE),
            (condition_node.id, failure_node.id, ConnectionType.CONDITIONAL_FALSE),
            (get_user_node.id, update_user_node.id, ConnectionType.CONDITIONAL),
            (get_user_node.id, end_node.id, ConnectionType.SEQUENCE),
            (update_user_node.id, end_node.id, ConnectionType.SEQUENCE)
        ]
        
        for from_node, to_node, conn_type in connections:
            await self.orchestrator.add_connection(
                workflow.id,
                from_node,
                to_node,
                conn_type
            )
        
        print(f"工作流创建完成，包含 {len(await self.orchestrator.get_workflow_nodes(workflow.id))} 个节点")
        return workflow.id
    
    async def execute_workflow_example(self, workflow_id: int):
        """执行工作流示例"""
        print("正在执行工作流...")
        
        # 准备输入参数
        input_data = {
            "username": "test_user",
            "password": "test_password",
            "should_update": True,
            "new_name": "Updated Name",
            "new_email": "updated@example.com"
        }
        
        # 执行工作流
        execution = await self.executor.execute_workflow(
            workflow_id,
            input_data,
            execution_name="用户信息管理测试执行"
        )
        
        print(f"工作流执行已启动: {execution.id}")
        
        # 等待执行完成（实际应用中可能需要轮询或使用回调）
        await asyncio.sleep(2)
        
        # 检查执行状态
        execution_details = await self.monitor.get_execution_details(execution.id)
        print(f"执行状态: {execution_details['status']}")
        print(f"执行结果: {json.dumps(execution_details['result'], indent=2, ensure_ascii=False)}")
        
        return execution.id
    
    async def monitor_workflow_example(self, workflow_id: int):
        """监控工作流示例"""
        print("正在获取工作流监控信息...")
        
        # 获取执行统计
        stats = await self.monitor.get_execution_stats(workflow_id)
        print(f"执行统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 获取性能分析
        performance = await self.monitor.get_performance_analysis(workflow_id)
        print(f"性能分析: {json.dumps(performance, indent=2, ensure_ascii=False)}")
        
        # 获取错误分析
        errors = await self.monitor.get_error_analysis(workflow_id)
        if errors:
            print(f"错误分析: {json.dumps(errors, indent=2, ensure_ascii=False)}")
        else:
            print("没有发现错误")
    
    async def batch_operations_example(self):
        """批量操作示例"""
        print("正在演示批量操作...")
        
        # 获取所有工作流
        workflows = await self.orchestrator.get_workflows()
        print(f"当前共有 {len(workflows)} 个工作流")
        
        # 批量执行（如果有多个工作流）
        if len(workflows) > 0:
            workflow_id = workflows[0].id
            
            # 创建多个执行实例
            executions = []
            for i in range(3):
                input_data = {
                    "username": f"test_user_{i}",
                    "password": "test_password",
                    "should_update": i % 2 == 0,
                    "new_name": f"User {i}",
                    "new_email": f"user{i}@example.com"
                }
                
                execution = await self.executor.execute_workflow(
                    workflow_id,
                    input_data,
                    execution_name=f"批量测试执行 {i+1}"
                )
                executions.append(execution.id)
            
            print(f"已创建 {len(executions)} 个执行实例")
            
            # 等待所有执行完成
            await asyncio.sleep(3)
            
            # 检查所有执行状态
            for exec_id in executions:
                details = await self.monitor.get_execution_details(exec_id)
                print(f"执行 {exec_id}: {details['status']}")
    
    async def export_import_example(self, workflow_id: int):
        """导出导入示例"""
        print("正在演示工作流导出导入...")
        
        # 导出工作流
        exported_data = await self.orchestrator.export_workflow(workflow_id)
        print(f"工作流已导出，数据大小: {len(json.dumps(exported_data))} 字符")
        
        # 修改名称后导入为新工作流
        exported_data['name'] = f"{exported_data['name']} (副本)"
        exported_data['description'] = f"{exported_data['description']} - 从导出数据创建"
        
        new_workflow = await self.orchestrator.import_workflow(exported_data)
        print(f"已导入新工作流: {new_workflow.id} - {new_workflow.name}")
        
        return new_workflow.id


async def main():
    """主函数"""
    print("=== 工作流编排模块使用示例 ===")
    
    example = WorkflowExample()
    
    try:
        # 1. 设置数据库
        await example.setup_database()
        
        # 2. 录入示例API
        login_api_id, user_info_api_id, update_user_api_id = await example.setup_sample_apis()
        
        # 3. 创建示例工作流
        workflow_id = await example.create_sample_workflow(
            login_api_id, user_info_api_id, update_user_api_id
        )
        
        # 4. 执行工作流
        execution_id = await example.execute_workflow_example(workflow_id)
        
        # 5. 监控工作流
        await example.monitor_workflow_example(workflow_id)
        
        # 6. 批量操作示例
        await example.batch_operations_example()
        
        # 7. 导出导入示例
        new_workflow_id = await example.export_import_example(workflow_id)
        
        print("\n=== 示例执行完成 ===")
        print(f"原工作流ID: {workflow_id}")
        print(f"新工作流ID: {new_workflow_id}")
        print(f"执行ID: {execution_id}")
        
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())