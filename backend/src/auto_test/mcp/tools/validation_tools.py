"""验证工具集合

提供数据验证相关的MCP工具实现，包括：
- 响应验证工具
- 数据断言工具
- 格式检查工具
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...utils.logger import get_logger

logger = get_logger(__name__)


class ValidationTools:
    """验证工具集合
    
    提供各种数据验证的MCP工具实现
    """
    
    @staticmethod
    async def register_tools(mcp_client) -> None:
        """注册验证工具到MCP客户端
        
        Args:
            mcp_client: MCP客户端实例
        """
        # 注册响应验证工具
        await mcp_client.register_tool(
            'validate_response',
            ValidationTools.get_validate_response_schema(),
            ValidationTools.validate_response
        )
        
        # 注册数据断言工具
        await mcp_client.register_tool(
            'assert_data',
            ValidationTools.get_assert_data_schema(),
            ValidationTools.assert_data
        )
        
        logger.info("验证工具注册完成")
    
    @staticmethod
    def get_validate_response_schema() -> Dict[str, Any]:
        """获取响应验证工具的Schema定义"""
        return {
            "name": "validate_response",
            "description": "验证HTTP响应结果",
            "type": "validation",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "object",
                        "description": "HTTP响应对象",
                        "properties": {
                            "status_code": {"type": "integer"},
                            "headers": {"type": "object"},
                            "body": {"type": ["object", "string", "array"]}
                        },
                        "required": ["status_code"]
                    },
                    "rules": {
                        "type": "array",
                        "description": "验证规则列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["status_code", "header", "body", "json_path", "regex"]
                                },
                                "field": {"type": "string"},
                                "operator": {
                                    "type": "string",
                                    "enum": ["eq", "ne", "gt", "gte", "lt", "lte", "contains", "not_contains", "exists", "not_exists", "matches"]
                                },
                                "value": {"type": ["string", "number", "boolean", "null"]},
                                "message": {"type": "string"}
                            },
                            "required": ["type", "operator"]
                        }
                    },
                    "strict": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否严格模式（遇到失败立即停止）"
                    }
                },
                "required": ["response", "rules"]
            }
        }
    
    @staticmethod
    def get_assert_data_schema() -> Dict[str, Any]:
        """获取数据断言工具的Schema定义"""
        return {
            "name": "assert_data",
            "description": "对数据进行断言检查",
            "type": "validation",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": ["object", "array", "string", "number", "boolean"],
                        "description": "要验证的数据"
                    },
                    "assertions": {
                        "type": "array",
                        "description": "断言列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "数据路径（JSONPath格式）"},
                                "condition": {"type": "string", "description": "断言条件"},
                                "expected": {"type": ["string", "number", "boolean", "null"], "description": "期望值"},
                                "message": {"type": "string", "description": "失败消息"}
                            },
                            "required": ["condition"]
                        }
                    }
                },
                "required": ["data", "assertions"]
            }
        }
    
    @staticmethod
    async def validate_response(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """验证HTTP响应结果
        
        Args:
            parameters: 验证参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        response = parameters['response']
        rules = parameters['rules']
        strict = parameters.get('strict', False)
        
        validation_results = []
        passed_count = 0
        failed_count = 0
        
        try:
            for rule in rules:
                result = await ValidationTools._validate_single_rule(response, rule)
                validation_results.append(result)
                
                if result['passed']:
                    passed_count += 1
                else:
                    failed_count += 1
                    
                    # 严格模式下遇到失败立即停止
                    if strict:
                        break
            
            overall_success = failed_count == 0
            
            return {
                'success': overall_success,
                'passed_count': passed_count,
                'failed_count': failed_count,
                'total_rules': len(rules),
                'results': validation_results,
                'summary': f"验证完成: {passed_count}个通过, {failed_count}个失败"
            }
            
        except Exception as e:
            logger.error(f"响应验证异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'passed_count': passed_count,
                'failed_count': failed_count + 1,
                'results': validation_results
            }
    
    @staticmethod
    async def _validate_single_rule(response: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """验证单个规则"""
        rule_type = rule['type']
        operator = rule['operator']
        expected_value = rule.get('value')
        field = rule.get('field')
        message = rule.get('message', f"验证规则失败: {rule_type}")
        
        try:
            # 获取实际值
            actual_value = None
            
            if rule_type == 'status_code':
                actual_value = response.get('status_code')
            
            elif rule_type == 'header':
                headers = response.get('headers', {})
                actual_value = headers.get(field) if field else None
            
            elif rule_type == 'body':
                body = response.get('body')
                if field and isinstance(body, dict):
                    actual_value = body.get(field)
                else:
                    actual_value = body
            
            elif rule_type == 'json_path':
                # 简化的JSONPath实现
                body = response.get('body')
                if field and isinstance(body, dict):
                    actual_value = ValidationTools._extract_json_path(body, field)
            
            elif rule_type == 'regex':
                # 正则表达式匹配
                body = response.get('body')
                if isinstance(body, str) and field:
                    match = re.search(field, body)
                    actual_value = match.group(0) if match else None
            
            # 执行比较
            passed = ValidationTools._compare_values(actual_value, operator, expected_value)
            
            return {
                'rule': rule,
                'actual_value': actual_value,
                'expected_value': expected_value,
                'passed': passed,
                'message': message if not passed else f"验证通过: {rule_type}"
            }
            
        except Exception as e:
            return {
                'rule': rule,
                'actual_value': None,
                'expected_value': expected_value,
                'passed': False,
                'message': f"验证异常: {str(e)}"
            }
    
    @staticmethod
    def _extract_json_path(data: Dict[str, Any], path: str) -> Any:
        """简化的JSONPath提取"""
        try:
            # 支持简单的点号路径，如 "data.user.id"
            keys = path.split('.')
            current = data
            
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    index = int(key)
                    current = current[index] if 0 <= index < len(current) else None
                else:
                    return None
            
            return current
            
        except Exception:
            return None
    
    @staticmethod
    def _compare_values(actual: Any, operator: str, expected: Any) -> bool:
        """比较值"""
        try:
            if operator == 'eq':
                return actual == expected
            elif operator == 'ne':
                return actual != expected
            elif operator == 'gt':
                return actual > expected
            elif operator == 'gte':
                return actual >= expected
            elif operator == 'lt':
                return actual < expected
            elif operator == 'lte':
                return actual <= expected
            elif operator == 'contains':
                return expected in str(actual) if actual is not None else False
            elif operator == 'not_contains':
                return expected not in str(actual) if actual is not None else True
            elif operator == 'exists':
                return actual is not None
            elif operator == 'not_exists':
                return actual is None
            elif operator == 'matches':
                return bool(re.match(str(expected), str(actual))) if actual is not None else False
            else:
                return False
                
        except Exception:
            return False
    
    @staticmethod
    async def assert_data(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """对数据进行断言检查
        
        Args:
            parameters: 断言参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 断言结果
        """
        data = parameters['data']
        assertions = parameters['assertions']
        
        assertion_results = []
        passed_count = 0
        failed_count = 0
        
        try:
            for assertion in assertions:
                result = await ValidationTools._execute_assertion(data, assertion)
                assertion_results.append(result)
                
                if result['passed']:
                    passed_count += 1
                else:
                    failed_count += 1
            
            overall_success = failed_count == 0
            
            return {
                'success': overall_success,
                'passed_count': passed_count,
                'failed_count': failed_count,
                'total_assertions': len(assertions),
                'results': assertion_results,
                'summary': f"断言完成: {passed_count}个通过, {failed_count}个失败"
            }
            
        except Exception as e:
            logger.error(f"数据断言异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'passed_count': passed_count,
                'failed_count': failed_count + 1,
                'results': assertion_results
            }
    
    @staticmethod
    async def _execute_assertion(data: Any, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个断言"""
        path = assertion.get('path', '')
        condition = assertion['condition']
        expected = assertion.get('expected')
        message = assertion.get('message', f"断言失败: {condition}")
        
        try:
            # 提取数据
            if path:
                actual_value = ValidationTools._extract_json_path(data, path) if isinstance(data, dict) else data
            else:
                actual_value = data
            
            # 执行断言
            passed = ValidationTools._evaluate_condition(actual_value, condition, expected)
            
            return {
                'assertion': assertion,
                'actual_value': actual_value,
                'expected_value': expected,
                'passed': passed,
                'message': message if not passed else f"断言通过: {condition}"
            }
            
        except Exception as e:
            return {
                'assertion': assertion,
                'actual_value': None,
                'expected_value': expected,
                'passed': False,
                'message': f"断言异常: {str(e)}"
            }
    
    @staticmethod
    def _evaluate_condition(actual: Any, condition: str, expected: Any) -> bool:
        """评估断言条件"""
        try:
            # 支持的条件类型
            if condition == 'not_null':
                return actual is not None
            elif condition == 'is_null':
                return actual is None
            elif condition == 'equals':
                return actual == expected
            elif condition == 'not_equals':
                return actual != expected
            elif condition == 'greater_than':
                return actual > expected
            elif condition == 'less_than':
                return actual < expected
            elif condition == 'contains':
                return expected in str(actual) if actual is not None else False
            elif condition == 'is_empty':
                return not actual if actual is not None else True
            elif condition == 'is_not_empty':
                return bool(actual)
            elif condition == 'is_type':
                return type(actual).__name__ == expected
            elif condition == 'length_equals':
                return len(actual) == expected if hasattr(actual, '__len__') else False
            elif condition == 'length_greater_than':
                return len(actual) > expected if hasattr(actual, '__len__') else False
            elif condition == 'matches_regex':
                return bool(re.match(str(expected), str(actual))) if actual is not None else False
            else:
                # 尝试直接评估表达式（简化实现）
                return bool(eval(condition.replace('actual', repr(actual))))
                
        except Exception:
            return False