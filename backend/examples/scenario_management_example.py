#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
场景管理示例代码

本示例展示如何使用场景管理系统来：
1. 录入场景
2. 添加多个接口编排
3. 配置并行和顺序执行流程
4. 将信息存储到MySQL数据库

运行前请确保：
- 已安装所需依赖
- MySQL数据库已配置
- API管理模块已设置
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

# 导入场景管理模块
from src.auto_test.scenario_management import (
    get_scenario_manager,
    get_scenario_executor,
    get_scenario_integration,
    ScenarioManager,
    ScenarioExecutor,
    ExecutionType
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = "mysql+aiomysql://username:password@localhost:3306/auto_test_db"


class ScenarioManagementDemo:
    """场景管理演示类"""
    
    def __init__(self, database_url: str = DATABASE_URL):
        """初始化演示类
        
        Args:
            database_url: 数据库连接URL
        """
        self.database_url = database_url
        self.scenario_manager = None
        self.scenario_executor = None
        self.integration = None
    
    async def initialize(self):
        """初始化组件"""
        logger.info("初始化场景管理组件...")
        
        # 初始化管理器
        self.scenario_manager = get_scenario_manager(self.database_url)
        self.scenario_executor = get_scenario_executor(self.database_url)
        self.integration = get_scenario_integration(self.database_url)
        
        # 初始化数据库
        await self.scenario_manager.initialize_database()
        
        logger.info("场景管理组件初始化完成")
    
    async def demo_basic_scenario_creation(self):
        """演示基本场景创建"""
        logger.info("\n=== 演示基本场景创建 ===")
        
        # 创建用户注册场景
        scenario_data = {
            'name': '用户注册流程',
            'description': '完整的用户注册流程，包括验证、创建和通知',
            'execution_type': ExecutionType.SEQUENTIAL.value,
            'config': {
                'timeout_seconds': 300,
                'retry_on_failure': True,
                'max_retries': 3
            },
            'variables': {
                'user_email': 'test@example.com',
                'user_name': 'TestUser',
                'notification_enabled': True
            }
        }
        
        result = await self.scenario_manager.create_scenario(**scenario_data)
        if result['success']:
            scenario_id = result['scenario']['id']
            logger.info(f"场景创建成功，ID: {scenario_id}")
            
            # 添加API到场景
            apis = [
                {
                    'api_id': 1,  # 邮箱验证API
                    'execution_order': 1,
                    'parameter_mapping': {
                        'email': '${user_email}'
                    },
                    'response_mapping': {
                        'is_valid': 'email_validation_result'
                    },
                    'is_required': True,
                    'timeout_seconds': 30
                },
                {
                    'api_id': 2,  # 用户创建API
                    'execution_order': 2,
                    'parameter_mapping': {
                        'email': '${user_email}',
                        'name': '${user_name}'
                    },
                    'response_mapping': {
                        'user_id': 'created_user_id',
                        'status': 'creation_status'
                    },
                    'pre_condition': '${email_validation_result} == true',
                    'is_required': True,
                    'timeout_seconds': 60
                },
                {
                    'api_id': 3,  # 发送欢迎邮件API
                    'execution_order': 3,
                    'parameter_mapping': {
                        'user_id': '${created_user_id}',
                        'email': '${user_email}'
                    },
                    'is_required': False,
                    'timeout_seconds': 30
                }
            ]
            
            for api_config in apis:
                api_result = await self.scenario_manager.add_api_to_scenario(
                    scenario_id=scenario_id,
                    **api_config
                )
                if api_result['success']:
                    logger.info(f"API {api_config['api_id']} 添加成功")
                else:
                    logger.error(f"API {api_config['api_id']} 添加失败: {api_result.get('error')}")
            
            return scenario_id
        else:
            logger.error(f"场景创建失败: {result.get('error')}")
            return None
    
    async def demo_parallel_scenario_creation(self):
        """演示并行场景创建"""
        logger.info("\n=== 演示并行场景创建 ===")
        
        # 创建数据同步场景（多个数据源并行同步）
        scenario_data = {
            'name': '多数据源同步',
            'description': '并行同步多个数据源的数据',
            'execution_type': ExecutionType.PARALLEL.value,
            'config': {
                'timeout_seconds': 600,
                'allow_partial_success': True
            },
            'variables': {
                'sync_timestamp': datetime.utcnow().isoformat(),
                'batch_size': 1000
            }
        }
        
        result = await self.scenario_manager.create_scenario(**scenario_data)
        if result['success']:
            scenario_id = result['scenario']['id']
            logger.info(f"并行场景创建成功，ID: {scenario_id}")
            
            # 添加并行执行的API
            parallel_apis = [
                {
                    'api_id': 4,  # 用户数据同步
                    'execution_order': 1,
                    'execution_group': 'sync_group_1',
                    'parameter_mapping': {
                        'timestamp': '${sync_timestamp}',
                        'batch_size': '${batch_size}',
                        'data_type': 'users'
                    },
                    'response_mapping': {
                        'synced_count': 'users_synced_count'
                    },
                    'timeout_seconds': 300
                },
                {
                    'api_id': 5,  # 订单数据同步
                    'execution_order': 1,
                    'execution_group': 'sync_group_1',
                    'parameter_mapping': {
                        'timestamp': '${sync_timestamp}',
                        'batch_size': '${batch_size}',
                        'data_type': 'orders'
                    },
                    'response_mapping': {
                        'synced_count': 'orders_synced_count'
                    },
                    'timeout_seconds': 300
                },
                {
                    'api_id': 6,  # 产品数据同步
                    'execution_order': 1,
                    'execution_group': 'sync_group_1',
                    'parameter_mapping': {
                        'timestamp': '${sync_timestamp}',
                        'batch_size': '${batch_size}',
                        'data_type': 'products'
                    },
                    'response_mapping': {
                        'synced_count': 'products_synced_count'
                    },
                    'timeout_seconds': 300
                }
            ]
            
            for api_config in parallel_apis:
                api_result = await self.scenario_manager.add_api_to_scenario(
                    scenario_id=scenario_id,
                    **api_config
                )
                if api_result['success']:
                    logger.info(f"并行API {api_config['api_id']} 添加成功")
            
            return scenario_id
        else:
            logger.error(f"并行场景创建失败: {result.get('error')}")
            return None
    
    async def demo_mixed_scenario_creation(self):
        """演示混合执行场景创建"""
        logger.info("\n=== 演示混合执行场景创建 ===")
        
        # 创建电商订单处理场景（混合并行和顺序执行）
        scenario_data = {
            'name': '电商订单处理流程',
            'description': '包含验证、库存检查、支付处理和物流安排的完整订单流程',
            'execution_type': ExecutionType.MIXED.value,
            'config': {
                'timeout_seconds': 900,
                'rollback_on_failure': True
            },
            'variables': {
                'order_id': 'ORD-2024-001',
                'customer_id': 'CUST-001',
                'payment_method': 'credit_card'
            }
        }
        
        result = await self.scenario_manager.create_scenario(**scenario_data)
        if result['success']:
            scenario_id = result['scenario']['id']
            logger.info(f"混合执行场景创建成功，ID: {scenario_id}")
            
            # 添加混合执行的API
            mixed_apis = [
                # 第一组：订单验证（顺序执行）
                {
                    'api_id': 7,  # 订单信息验证
                    'execution_order': 1,
                    'execution_group': 'validation',
                    'parameter_mapping': {
                        'order_id': '${order_id}'
                    },
                    'response_mapping': {
                        'is_valid': 'order_valid',
                        'order_details': 'validated_order'
                    },
                    'is_required': True,
                    'timeout_seconds': 30
                },
                {
                    'api_id': 8,  # 客户信息验证
                    'execution_order': 2,
                    'execution_group': 'validation',
                    'parameter_mapping': {
                        'customer_id': '${customer_id}'
                    },
                    'response_mapping': {
                        'customer_valid': 'customer_verified'
                    },
                    'pre_condition': '${order_valid} == true',
                    'is_required': True,
                    'timeout_seconds': 30
                },
                
                # 第二组：并行检查（库存、价格、优惠）
                {
                    'api_id': 9,  # 库存检查
                    'execution_order': 3,
                    'execution_group': 'parallel_checks',
                    'parameter_mapping': {
                        'order_details': '${validated_order}'
                    },
                    'response_mapping': {
                        'stock_available': 'inventory_status'
                    },
                    'timeout_seconds': 60
                },
                {
                    'api_id': 10,  # 价格计算
                    'execution_order': 3,
                    'execution_group': 'parallel_checks',
                    'parameter_mapping': {
                        'order_details': '${validated_order}',
                        'customer_id': '${customer_id}'
                    },
                    'response_mapping': {
                        'final_price': 'calculated_price'
                    },
                    'timeout_seconds': 45
                },
                {
                    'api_id': 11,  # 优惠券验证
                    'execution_order': 3,
                    'execution_group': 'parallel_checks',
                    'parameter_mapping': {
                        'customer_id': '${customer_id}',
                        'order_details': '${validated_order}'
                    },
                    'response_mapping': {
                        'discount_amount': 'applied_discount'
                    },
                    'is_required': False,
                    'timeout_seconds': 30
                },
                
                # 第三组：支付处理（顺序执行）
                {
                    'api_id': 12,  # 支付处理
                    'execution_order': 4,
                    'execution_group': 'payment',
                    'parameter_mapping': {
                        'customer_id': '${customer_id}',
                        'amount': '${calculated_price}',
                        'discount': '${applied_discount}',
                        'payment_method': '${payment_method}'
                    },
                    'response_mapping': {
                        'payment_id': 'transaction_id',
                        'payment_status': 'payment_result'
                    },
                    'pre_condition': '${inventory_status} == "available"',
                    'is_required': True,
                    'timeout_seconds': 120
                },
                
                # 第四组：后续处理（并行执行）
                {
                    'api_id': 13,  # 库存扣减
                    'execution_order': 5,
                    'execution_group': 'post_payment',
                    'parameter_mapping': {
                        'order_details': '${validated_order}',
                        'payment_id': '${transaction_id}'
                    },
                    'pre_condition': '${payment_result} == "success"',
                    'timeout_seconds': 60
                },
                {
                    'api_id': 14,  # 物流安排
                    'execution_order': 5,
                    'execution_group': 'post_payment',
                    'parameter_mapping': {
                        'order_id': '${order_id}',
                        'customer_id': '${customer_id}'
                    },
                    'pre_condition': '${payment_result} == "success"',
                    'timeout_seconds': 90
                },
                {
                    'api_id': 15,  # 发送确认邮件
                    'execution_order': 5,
                    'execution_group': 'post_payment',
                    'parameter_mapping': {
                        'customer_id': '${customer_id}',
                        'order_id': '${order_id}',
                        'payment_id': '${transaction_id}'
                    },
                    'is_required': False,
                    'timeout_seconds': 30
                }
            ]
            
            for api_config in mixed_apis:
                api_result = await self.scenario_manager.add_api_to_scenario(
                    scenario_id=scenario_id,
                    **api_config
                )
                if api_result['success']:
                    logger.info(f"混合API {api_config['api_id']} 添加成功")
            
            return scenario_id
        else:
            logger.error(f"混合执行场景创建失败: {result.get('error')}")
            return None
    
    async def demo_scenario_execution(self, scenario_id: int, scenario_name: str):
        """演示场景执行"""
        logger.info(f"\n=== 演示场景执行: {scenario_name} ===")
        
        # 获取场景详情
        scenario_result = await self.scenario_manager.get_scenario(scenario_id)
        if not scenario_result['success']:
            logger.error(f"获取场景失败: {scenario_result.get('error')}")
            return
        
        scenario = scenario_result['scenario']
        logger.info(f"场景信息: {scenario['name']} - {scenario['execution_type']}")
        logger.info(f"包含 {len(scenario['apis'])} 个API")
        
        # 执行场景
        execution_variables = {
            'execution_id': f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'environment': 'demo'
        }
        
        logger.info("开始执行场景...")
        execution_result = await self.scenario_executor.execute_scenario(
            scenario_id=scenario_id,
            variables=execution_variables
        )
        
        if execution_result['success']:
            execution_record = execution_result['execution_record']
            logger.info(f"场景执行完成，执行ID: {execution_record['id']}")
            logger.info(f"执行状态: {execution_record['status']}")
            logger.info(f"执行时间: {execution_record['execution_time']}秒")
            
            # 显示API执行结果
            api_results = execution_record.get('api_results', [])
            for api_result in api_results:
                logger.info(
                    f"  API {api_result['api_id']}: {api_result['status']} "
                    f"({api_result['execution_time']}秒)"
                )
        else:
            logger.error(f"场景执行失败: {execution_result.get('error')}")
    
    async def demo_scenario_management_operations(self):
        """演示场景管理操作"""
        logger.info("\n=== 演示场景管理操作 ===")
        
        # 列出所有场景
        scenarios_result = await self.scenario_manager.list_scenarios()
        if scenarios_result['success']:
            scenarios = scenarios_result['scenarios']
            logger.info(f"当前共有 {len(scenarios)} 个场景:")
            for scenario in scenarios:
                logger.info(
                    f"  - {scenario['name']} (ID: {scenario['id']}, "
                    f"类型: {scenario['execution_type']})"
                )
        
        # 创建场景模板
        template_result = await self.scenario_manager.create_scenario_template(
            name="API测试模板",
            description="用于API测试的通用模板",
            template_config={
                'default_timeout': 60,
                'default_retry_count': 2,
                'required_variables': ['api_endpoint', 'test_data']
            }
        )
        
        if template_result['success']:
            template_id = template_result['template']['id']
            logger.info(f"场景模板创建成功，ID: {template_id}")
            
            # 从模板创建场景
            from_template_result = await self.scenario_manager.create_scenario_from_template(
                template_id=template_id,
                scenario_name="基于模板的API测试场景",
                variables={
                    'api_endpoint': 'https://api.example.com/test',
                    'test_data': {'key': 'value'}
                }
            )
            
            if from_template_result['success']:
                logger.info("从模板创建场景成功")
    
    async def demo_batch_operations(self):
        """演示批量操作"""
        logger.info("\n=== 演示批量操作 ===")
        
        # 批量创建场景
        batch_scenarios = [
            {
                'name': '批量测试场景1',
                'description': '批量创建的测试场景1',
                'execution_type': ExecutionType.SEQUENTIAL.value
            },
            {
                'name': '批量测试场景2',
                'description': '批量创建的测试场景2',
                'execution_type': ExecutionType.PARALLEL.value
            }
        ]
        
        batch_result = await self.scenario_manager.batch_create_scenarios(batch_scenarios)
        if batch_result['success']:
            logger.info(f"批量创建 {len(batch_result['scenarios'])} 个场景成功")
        
        # 导出场景
        export_result = await self.scenario_manager.export_scenarios(
            format='json',
            include_execution_records=False
        )
        
        if export_result['success']:
            logger.info("场景导出成功")
            # 这里可以保存到文件
            # with open('scenarios_export.json', 'w') as f:
            #     json.dump(export_result['data'], f, indent=2)
    
    async def demo_integration_features(self):
        """演示集成功能"""
        logger.info("\n=== 演示集成功能 ===")
        
        # 获取集成状态
        status_result = await self.integration.get_integration_status()
        if status_result['success']:
            status = status_result['status']
            logger.info("集成状态:")
            logger.info(f"  工作流模块可用: {status['workflow_available']}")
            logger.info(f"  API管理模块可用: {status['api_management_available']}")
            logger.info(f"  场景总数: {status['statistics']['total_scenarios']}")
        
        # 如果有场景，演示转换功能
        scenarios_result = await self.scenario_manager.list_scenarios()
        if scenarios_result['success'] and scenarios_result['scenarios']:
            first_scenario = scenarios_result['scenarios'][0]
            scenario_id = first_scenario['id']
            
            # 获取转换建议
            recommendations_result = await self.integration.get_conversion_recommendations(
                source_type='scenario',
                source_id=scenario_id
            )
            
            if recommendations_result['success']:
                recommendations = recommendations_result['recommendations']
                logger.info(f"场景 {scenario_id} 转换建议:")
                logger.info(f"  转换可行性: {recommendations['conversion_feasible']}")
                logger.info(f"  推荐执行类型: {recommendations['recommended_execution_type']}")
                
                if recommendations['potential_issues']:
                    logger.info("  潜在问题:")
                    for issue in recommendations['potential_issues']:
                        logger.info(f"    - {issue}")
    
    async def run_complete_demo(self):
        """运行完整演示"""
        logger.info("开始场景管理完整演示")
        
        try:
            # 初始化
            await self.initialize()
            
            # 创建不同类型的场景
            sequential_scenario_id = await self.demo_basic_scenario_creation()
            parallel_scenario_id = await self.demo_parallel_scenario_creation()
            mixed_scenario_id = await self.demo_mixed_scenario_creation()
            
            # 演示场景管理操作
            await self.demo_scenario_management_operations()
            
            # 演示批量操作
            await self.demo_batch_operations()
            
            # 演示场景执行（注意：这里只是演示，实际执行需要真实的API）
            if sequential_scenario_id:
                logger.info("\n注意：以下场景执行仅为演示，实际执行需要配置真实的API")
                # await self.demo_scenario_execution(sequential_scenario_id, "用户注册流程")
            
            # 演示集成功能
            await self.demo_integration_features()
            
            logger.info("\n=== 场景管理演示完成 ===")
            logger.info("演示内容包括:")
            logger.info("1. 顺序执行场景创建和配置")
            logger.info("2. 并行执行场景创建和配置")
            logger.info("3. 混合执行场景创建和配置")
            logger.info("4. 场景管理操作（列表、模板、批量操作）")
            logger.info("5. 集成功能演示")
            logger.info("\n所有场景信息已存储到MySQL数据库中")
            
        except Exception as e:
            logger.error(f"演示过程中发生错误: {e}")
            raise


async def main():
    """主函数"""
    # 创建演示实例
    demo = ScenarioManagementDemo()
    
    # 运行完整演示
    await demo.run_complete_demo()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())