"""API管理模块使用示例"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

# 设置环境变量（实际使用时应该在.env文件中配置）
os.environ.setdefault('DATABASE_URL', 'mysql+pymysql://username:password@localhost:3306/api_management')
os.environ.setdefault('DATABASE_ECHO', 'false')

from src.auto_test.api_management import (
    APIRecorder, 
    APICaller, 
    DatabaseManager,
    get_database_manager
)


def setup_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    db_manager = get_database_manager()
    
    # 创建所有表
    db_manager.create_tables()
    print("数据库表创建完成")
    
    return db_manager


def example_api_recording():
    """API录入示例"""
    print("\n=== API录入示例 ===")
    
    # 获取数据库管理器和API录入器
    db_manager = get_database_manager()
    recorder = APIRecorder(db_manager)
    
    # 示例1: 录入一个GET接口
    print("\n1. 录入GET接口")
    api_data = {
        'name': '获取用户信息',
        'description': '根据用户ID获取用户详细信息',
        'url': 'https://api.example.com/users/{user_id}',
        'method': 'GET',
        'content_type': 'application/json',
        'timeout': 30,
        'retry_count': 3,
        'auth_type': 'bearer',
        'auth_config': {'token': 'your_bearer_token_here'},
        'tags': ['user', 'profile'],
        'is_active': True
    }
    
    api_id = recorder.create_api(api_data)
    print(f"创建API成功，ID: {api_id}")
    
    # 为GET接口添加参数
    parameters = [
        {
            'name': 'user_id',
            'param_type': 'path',
            'data_type': 'integer',
            'is_required': True,
            'description': '用户ID',
            'min_value': 1
        },
        {
            'name': 'include_profile',
            'param_type': 'query',
            'data_type': 'boolean',
            'is_required': False,
            'description': '是否包含详细资料',
            'default_value': 'false'
        },
        {
            'name': 'Authorization',
            'param_type': 'header',
            'data_type': 'string',
            'is_required': True,
            'description': '认证令牌',
            'pattern': r'^Bearer .+'
        }
    ]
    
    for param in parameters:
        param_id = recorder.add_api_parameter(api_id, param)
        print(f"添加参数 '{param['name']}' 成功，ID: {param_id}")
    
    # 示例2: 录入一个POST接口
    print("\n2. 录入POST接口")
    post_api_data = {
        'name': '创建用户',
        'description': '创建新用户账户',
        'url': 'https://api.example.com/users',
        'method': 'POST',
        'content_type': 'application/json',
        'timeout': 60,
        'retry_count': 2,
        'auth_type': 'api_key',
        'auth_config': {'api_key': 'your_api_key', 'key_name': 'X-API-Key'},
        'tags': ['user', 'create'],
        'is_active': True
    }
    
    post_api_id = recorder.create_api(post_api_data)
    print(f"创建POST API成功，ID: {post_api_id}")
    
    # 为POST接口添加参数
    post_parameters = [
        {
            'name': 'username',
            'param_type': 'body',
            'data_type': 'string',
            'is_required': True,
            'description': '用户名',
            'min_length': 3,
            'max_length': 50,
            'pattern': r'^[a-zA-Z0-9_]+$'
        },
        {
            'name': 'email',
            'param_type': 'body',
            'data_type': 'string',
            'is_required': True,
            'description': '邮箱地址',
            'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'
        },
        {
            'name': 'age',
            'param_type': 'body',
            'data_type': 'integer',
            'is_required': False,
            'description': '年龄',
            'min_value': 18,
            'max_value': 120
        },
        {
            'name': 'Content-Type',
            'param_type': 'header',
            'data_type': 'string',
            'is_required': True,
            'description': '内容类型',
            'default_value': 'application/json'
        }
    ]
    
    for param in post_parameters:
        param_id = recorder.add_api_parameter(post_api_id, param)
        print(f"添加参数 '{param['name']}' 成功，ID: {param_id}")
    
    return api_id, post_api_id


def example_api_calling_sync(api_id: int, post_api_id: int):
    """同步API调用示例"""
    print("\n=== 同步API调用示例 ===")
    
    # 获取API调用器
    db_manager = get_database_manager()
    caller = APICaller(db_manager)
    
    # 示例1: 调用GET接口
    print("\n1. 调用GET接口")
    try:
        # 准备参数
        get_parameters = {
            'user_id': 123,
            'include_profile': True,
            'Authorization': 'Bearer your_actual_token_here'
        }
        
        # 调用API
        result = caller.call_api_sync(
            api_id=api_id,
            parameters=get_parameters,
            caller_info={'user': 'test_user', 'source': 'example_script'}
        )
        
        print(f"调用成功: {result['success']}")
        print(f"状态码: {result['status_code']}")
        print(f"响应时间: {result['duration_ms']}ms")
        print(f"请求ID: {result['request_id']}")
        
        if result['success']:
            print(f"响应数据: {result['data']}")
        
    except Exception as e:
        print(f"调用失败: {e}")
    
    # 示例2: 调用POST接口
    print("\n2. 调用POST接口")
    try:
        # 准备参数
        post_parameters = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'age': 25,
            'Content-Type': 'application/json'
        }
        
        # 调用API
        result = caller.call_api_sync(
            api_id=post_api_id,
            parameters=post_parameters,
            caller_info={'user': 'test_user', 'source': 'example_script'}
        )
        
        print(f"调用成功: {result['success']}")
        print(f"状态码: {result['status_code']}")
        print(f"响应时间: {result['duration_ms']}ms")
        print(f"请求ID: {result['request_id']}")
        
        if result['success']:
            print(f"响应数据: {result['data']}")
        
    except Exception as e:
        print(f"调用失败: {e}")


async def example_api_calling_async(api_id: int):
    """异步API调用示例"""
    print("\n=== 异步API调用示例 ===")
    
    # 使用异步上下文管理器
    db_manager = get_database_manager()
    
    async with APICaller(db_manager) as caller:
        try:
            # 准备参数
            parameters = {
                'user_id': 456,
                'include_profile': False,
                'Authorization': 'Bearer your_actual_token_here'
            }
            
            # 异步调用API
            result = await caller.call_api_async(
                api_id=api_id,
                parameters=parameters,
                caller_info={'user': 'async_user', 'source': 'async_example'}
            )
            
            print(f"异步调用成功: {result['success']}")
            print(f"状态码: {result['status_code']}")
            print(f"响应时间: {result['duration_ms']}ms")
            print(f"请求ID: {result['request_id']}")
            
            if result['success']:
                print(f"响应数据: {result['data']}")
            
        except Exception as e:
            print(f"异步调用失败: {e}")


def example_batch_operations():
    """批量操作示例"""
    print("\n=== 批量操作示例 ===")
    
    db_manager = get_database_manager()
    recorder = APIRecorder(db_manager)
    
    # 批量导入API
    print("\n1. 批量导入API")
    apis_data = [
        {
            'name': '获取商品列表',
            'description': '分页获取商品列表',
            'url': 'https://api.shop.com/products',
            'method': 'GET',
            'content_type': 'application/json',
            'tags': ['product', 'list']
        },
        {
            'name': '获取商品详情',
            'description': '根据商品ID获取详情',
            'url': 'https://api.shop.com/products/{product_id}',
            'method': 'GET',
            'content_type': 'application/json',
            'tags': ['product', 'detail']
        },
        {
            'name': '创建订单',
            'description': '创建新订单',
            'url': 'https://api.shop.com/orders',
            'method': 'POST',
            'content_type': 'application/json',
            'tags': ['order', 'create']
        }
    ]
    
    imported_ids = recorder.batch_import_apis(apis_data)
    print(f"批量导入成功，导入了 {len(imported_ids)} 个API")
    
    # 批量导出API
    print("\n2. 批量导出API")
    exported_data = recorder.batch_export_apis(tags=['product'])
    print(f"导出了 {len(exported_data)} 个包含'product'标签的API")
    
    return imported_ids


def example_statistics_and_monitoring():
    """统计和监控示例"""
    print("\n=== 统计和监控示例 ===")
    
    db_manager = get_database_manager()
    recorder = APIRecorder(db_manager)
    caller = APICaller(db_manager)
    
    # 获取API统计信息
    print("\n1. API统计信息")
    stats = recorder.get_api_statistics()
    print(f"总API数量: {stats['total_apis']}")
    print(f"活跃API数量: {stats['active_apis']}")
    print(f"按方法分组: {stats['by_method']}")
    print(f"按标签分组: {stats['by_tags']}")
    
    # 获取调用统计信息
    print("\n2. 调用统计信息")
    call_stats = caller.get_call_statistics()
    print(f"总调用次数: {call_stats['total_calls']}")
    print(f"成功调用次数: {call_stats['successful_calls']}")
    print(f"失败调用次数: {call_stats['failed_calls']}")
    print(f"成功率: {call_stats['success_rate']:.2f}%")
    print(f"平均响应时间: {call_stats['average_duration_ms']:.2f}ms")
    
    # 获取最近的调用历史
    print("\n3. 最近调用历史")
    recent_calls = caller.get_call_history(limit=5)
    for call in recent_calls:
        print(f"  - {call.created_at}: {call.request_method} {call.request_url} -> {call.response_status} ({call.duration_ms}ms)")


def example_search_and_filter():
    """搜索和过滤示例"""
    print("\n=== 搜索和过滤示例 ===")
    
    db_manager = get_database_manager()
    recorder = APIRecorder(db_manager)
    
    # 按名称搜索
    print("\n1. 按名称搜索API")
    apis = recorder.search_apis(name='用户')
    print(f"找到 {len(apis)} 个包含'用户'的API")
    for api in apis:
        print(f"  - {api.name}: {api.method} {api.url}")
    
    # 按标签过滤
    print("\n2. 按标签过滤API")
    apis = recorder.search_apis(tags=['user'])
    print(f"找到 {len(apis)} 个包含'user'标签的API")
    for api in apis:
        print(f"  - {api.name}: {api.tags}")
    
    # 按方法过滤
    print("\n3. 按方法过滤API")
    apis = recorder.search_apis(method='POST')
    print(f"找到 {len(apis)} 个POST方法的API")
    for api in apis:
        print(f"  - {api.name}: {api.method} {api.url}")


def main():
    """主函数"""
    print("API管理模块使用示例")
    print("=" * 50)
    
    try:
        # 1. 初始化数据库
        setup_database()
        
        # 2. API录入示例
        api_id, post_api_id = example_api_recording()
        
        # 3. 同步API调用示例
        example_api_calling_sync(api_id, post_api_id)
        
        # 4. 异步API调用示例
        asyncio.run(example_api_calling_async(api_id))
        
        # 5. 批量操作示例
        example_batch_operations()
        
        # 6. 统计和监控示例
        example_statistics_and_monitoring()
        
        # 7. 搜索和过滤示例
        example_search_and_filter()
        
        print("\n=== 示例运行完成 ===")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()