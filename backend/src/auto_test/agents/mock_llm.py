"""模拟LLM实现

用于测试环境，提供模拟的LLM响应，避免依赖真实的API密钥。
"""

import json
from typing import List, Dict, Any
from datetime import datetime


class MockLLM:
    """模拟LLM实现"""
    
    def __init__(self, model_name: str = "mock-gpt", temperature: float = 0.1, **kwargs):
        self.model_name = model_name
        self.temperature = temperature
        self.call_count = 0
    
    async def agenerate(self, messages_list: List[List]) -> 'MockLLMResult':
        """异步生成响应"""
        self.call_count += 1
        
        # 获取最后一条用户消息
        messages = messages_list[0] if messages_list else []
        user_message = ""
        
        for msg in messages:
            if hasattr(msg, 'content'):
                content = msg.content
                if "用户输入:" in content:
                    user_message = content
                    break
        
        # 根据用户输入生成模拟响应
        mock_response = self._generate_mock_response(user_message)
        
        return MockLLMResult(mock_response)
    
    def _generate_mock_response(self, user_input: str) -> str:
        """生成模拟响应"""
        # 简单的关键词匹配生成响应
        if "注册" in user_input or "register" in user_input.lower():
            return json.dumps({
                "intent": "api_test",
                "confidence": 0.9,
                "entities": {
                    "api_endpoints": ["/api/users/register"],
                    "parameters": {
                        "username": "testuser",
                        "email": "test@example.com",
                        "password": "password123"
                    },
                    "test_data": {
                        "valid_user": {
                            "username": "testuser",
                            "email": "test@example.com",
                            "password": "password123"
                        }
                    },
                    "validation_rules": ["status_code == 200", "response.data.id != null"],
                    "systems": ["用户管理系统"],
                    "modules": ["用户注册模块"]
                },
                "actions": [
                    {
                        "action": "api_call",
                        "target": "/api/users/register",
                        "parameters": {
                            "method": "POST",
                            "body": {
                                "username": "testuser",
                                "email": "test@example.com",
                                "password": "password123"
                            }
                        },
                        "dependencies": [],
                        "timeout": 30
                    },
                    {
                        "action": "data_validation",
                        "target": "validation_rules",
                        "parameters": {
                            "rules": [
                                {
                                    "type": "status_code",
                                    "operator": "eq",
                                    "value": 200
                                },
                                {
                                    "type": "json_path",
                                    "field": "data.id",
                                    "operator": "exists"
                                }
                            ]
                        },
                        "dependencies": ["step_1"],
                        "timeout": 10
                    }
                ],
                "context": {
                    "priority": "high",
                    "environment": "test",
                    "tags": ["用户管理", "注册"]
                }
            }, ensure_ascii=False)
        
        elif "登录" in user_input or "login" in user_input.lower():
            return json.dumps({
                "intent": "api_test",
                "confidence": 0.95,
                "entities": {
                    "api_endpoints": ["/api/users/login"],
                    "parameters": {
                        "username": "testuser",
                        "password": "password123"
                    },
                    "validation_rules": ["status_code == 200", "response.token != null"],
                    "systems": ["用户管理系统"],
                    "modules": ["用户认证模块"]
                },
                "actions": [
                    {
                        "action": "api_call",
                        "target": "/api/users/login",
                        "parameters": {
                            "method": "POST",
                            "body": {
                                "username": "testuser",
                                "password": "password123"
                            }
                        },
                        "dependencies": [],
                        "timeout": 30
                    }
                ],
                "context": {
                    "priority": "high",
                    "environment": "test",
                    "tags": ["用户管理", "登录"]
                }
            }, ensure_ascii=False)
        
        else:
            # 通用API测试响应
            return json.dumps({
                "intent": "api_test",
                "confidence": 0.7,
                "entities": {
                    "api_endpoints": ["/api/test"],
                    "parameters": {},
                    "validation_rules": ["status_code == 200"],
                    "systems": ["测试系统"],
                    "modules": ["测试模块"]
                },
                "actions": [
                    {
                        "action": "api_call",
                        "target": "/api/test",
                        "parameters": {
                            "method": "GET"
                        },
                        "dependencies": [],
                        "timeout": 30
                    }
                ],
                "context": {
                    "priority": "medium",
                    "environment": "test",
                    "tags": ["通用测试"]
                }
            }, ensure_ascii=False)


class MockLLMResult:
    """模拟LLM结果"""
    
    def __init__(self, response_text: str):
        self.generations = [[MockGeneration(response_text)]]


class MockGeneration:
    """模拟生成结果"""
    
    def __init__(self, text: str):
        self.text = text