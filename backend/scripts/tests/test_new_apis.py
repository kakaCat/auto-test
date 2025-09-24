#!/usr/bin/env python3
"""
测试新添加的API接口
"""

import requests
import json

def test_api_endpoint(url, description):
    """测试API端点"""
    try:
        print(f"\n测试 {description}: {url}")
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

def main():
    """主测试函数"""
    base_url = "http://localhost:8000"
    
    # 测试系统管理API
    test_api_endpoint(f"{base_url}/api/systems", "系统列表")
    test_api_endpoint(f"{base_url}/api/systems/sys-001", "系统详情")
    
    # 测试模块管理API
    test_api_endpoint(f"{base_url}/api/modules", "模块列表")
    test_api_endpoint(f"{base_url}/api/modules?system_id=sys-001", "指定系统的模块列表")
    test_api_endpoint(f"{base_url}/api/modules/mod-001", "模块详情")
    
    # 测试原有API
    test_api_endpoint(f"{base_url}/health", "健康检查")
    test_api_endpoint(f"{base_url}/api/v1/stats", "统计信息")

if __name__ == "__main__":
    main()