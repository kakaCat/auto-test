#!/usr/bin/env python3
"""
测试重构后的API
验证DDD架构重构是否成功
"""

import requests
import json
import sys
from datetime import datetime


def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("测试重构后的自动化测试平台API")
    print("=" * 50)
    
    # 测试根路径
    print("\n1. 测试根路径 (/)")
    try:
        response = requests.get(f"{base_url}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        assert response.status_code == 200
        assert "自动化测试平台API" in response.json()["message"]
        print("✅ 根路径测试通过")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        return False
    
    # 测试健康检查
    print("\n2. 测试健康检查 (/health)")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ 健康检查测试通过")
    except Exception as e:
        print(f"❌ 健康检查测试失败: {e}")
        return False
    
    # 测试API文档
    print("\n3. 测试API文档 (/docs)")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"状态码: {response.status_code}")
        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()
        print("✅ API文档测试通过")
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False
    
    # 测试OpenAPI规范
    print("\n4. 测试OpenAPI规范 (/openapi.json)")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        print(f"状态码: {response.status_code}")
        openapi_spec = response.json()
        print(f"API标题: {openapi_spec.get('info', {}).get('title', 'N/A')}")
        print(f"API版本: {openapi_spec.get('info', {}).get('version', 'N/A')}")
        assert response.status_code == 200
        assert openapi_spec["info"]["title"] == "自动化测试平台"
        assert openapi_spec["info"]["version"] == "2.0.0"
        print("✅ OpenAPI规范测试通过")
    except Exception as e:
        print(f"❌ OpenAPI规范测试失败: {e}")
        return False
    
    # 测试错误处理
    print("\n5. 测试错误处理 (/nonexistent)")
    try:
        response = requests.get(f"{base_url}/nonexistent")
        print(f"状态码: {response.status_code}")
        assert response.status_code == 404
        print("✅ 错误处理测试通过")
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！重构成功！")
    print("=" * 50)
    
    return True


def main():
    """主函数"""
    print(f"开始测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = test_api_endpoints()
        if success:
            print("\n✅ 重构验证成功！")
            print("DDD架构重构已完成，应用程序运行正常。")
            sys.exit(0)
        else:
            print("\n❌ 重构验证失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()