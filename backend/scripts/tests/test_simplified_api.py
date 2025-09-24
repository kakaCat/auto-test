#!/usr/bin/env python3
"""
测试简化后的API是否正常工作
"""
import requests
import json

def test_api_endpoint(url, description):
    """测试API端点"""
    try:
        print(f"\n测试: {description}")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            print("✅ 测试通过")
        else:
            print(f"❌ 测试失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("简化后的API测试")
    print("=" * 50)
    
    # 测试各个端点
    test_endpoints = [
        (f"{base_url}/", "根路径"),
        (f"{base_url}/health", "健康检查"),
        (f"{base_url}/api/v1/stats", "全局统计"),
        (f"{base_url}/api/v1/logs?limit=3", "日志API"),
    ]
    
    for url, description in test_endpoints:
        test_api_endpoint(url, description)
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()