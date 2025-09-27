"""实用工具集合

提供通用实用工具的MCP工具实现，包括：
- 等待延时工具
- 数据处理工具
- 条件判断工具
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

from ...utils.logger import get_logger

logger = get_logger(__name__)


class UtilityTools:
    """实用工具集合
    
    提供各种通用实用工具的MCP工具实现
    """
    
    @staticmethod
    async def register_tools(mcp_client) -> None:
        """注册实用工具到MCP客户端
        
        Args:
            mcp_client: MCP客户端实例
        """
        # 注册等待工具
        await mcp_client.register_tool(
            'wait_for',
            UtilityTools.get_wait_for_schema(),
            UtilityTools.wait_for
        )
        
        # 注册数据转换工具
        await mcp_client.register_tool(
            'transform_data',
            UtilityTools.get_transform_data_schema(),
            UtilityTools.transform_data
        )
        
        # 注册条件判断工具
        await mcp_client.register_tool(
            'evaluate_condition',
            UtilityTools.get_evaluate_condition_schema(),
            UtilityTools.evaluate_condition
        )
        
        logger.info("实用工具注册完成")
    
    @staticmethod
    def get_wait_for_schema() -> Dict[str, Any]:
        """获取等待工具的Schema定义"""
        return {
            "name": "wait_for",
            "description": "等待指定时间或条件",
            "type": "utility",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "number",
                        "description": "等待时间(秒)",
                        "minimum": 0,
                        "maximum": 300
                    },
                    "condition": {
                        "type": "string",
                        "description": "等待条件（可选）"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "超时时间(秒)",
                        "default": 60
                    },
                    "check_interval": {
                        "type": "number",
                        "description": "条件检查间隔(秒)",
                        "default": 1
                    }
                },
                "required": ["duration"]
            }
        }
    
    @staticmethod
    def get_transform_data_schema() -> Dict[str, Any]:
        """获取数据转换工具的Schema定义"""
        return {
            "name": "transform_data",
            "description": "转换和处理数据",
            "type": "utility",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": ["object", "array", "string", "number"],
                        "description": "要转换的数据"
                    },
                    "transformations": {
                        "type": "array",
                        "description": "转换规则列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["extract", "format", "calculate", "filter", "map", "reduce"]
                                },
                                "source": {"type": "string", "description": "源字段路径"},
                                "target": {"type": "string", "description": "目标字段名"},
                                "expression": {"type": "string", "description": "转换表达式"},
                                "parameters": {"type": "object", "description": "转换参数"}
                            },
                            "required": ["type"]
                        }
                    }
                },
                "required": ["data", "transformations"]
            }
        }
    
    @staticmethod
    def get_evaluate_condition_schema() -> Dict[str, Any]:
        """获取条件判断工具的Schema定义"""
        return {
            "name": "evaluate_condition",
            "description": "评估条件表达式",
            "type": "utility",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "条件表达式"
                    },
                    "variables": {
                        "type": "object",
                        "description": "变量上下文",
                        "default": {}
                    },
                    "return_details": {
                        "type": "boolean",
                        "description": "是否返回详细信息",
                        "default": False
                    }
                },
                "required": ["condition"]
            }
        }
    
    @staticmethod
    async def wait_for(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """等待指定时间或条件
        
        Args:
            parameters: 等待参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 等待结果
        """
        duration = parameters['duration']
        condition = parameters.get('condition')
        timeout = parameters.get('timeout', 60)
        check_interval = parameters.get('check_interval', 1)
        
        start_time = time.time()
        
        try:
            if condition:
                # 条件等待
                logger.info(f"开始条件等待: {condition}, 超时: {timeout}秒")
                
                while time.time() - start_time < timeout:
                    # 检查条件
                    if await UtilityTools._check_condition(condition, context):
                        elapsed = time.time() - start_time
                        logger.info(f"条件满足，等待结束: {elapsed:.2f}秒")
                        return {
                            'success': True,
                            'condition_met': True,
                            'elapsed_time': elapsed,
                            'message': f"条件满足: {condition}"
                        }
                    
                    # 等待检查间隔
                    await asyncio.sleep(check_interval)
                
                # 超时
                elapsed = time.time() - start_time
                logger.warning(f"条件等待超时: {condition}")
                return {
                    'success': False,
                    'condition_met': False,
                    'elapsed_time': elapsed,
                    'message': f"条件等待超时: {condition}"
                }
            
            else:
                # 时间等待
                logger.info(f"开始时间等待: {duration}秒")
                await asyncio.sleep(duration)
                
                return {
                    'success': True,
                    'elapsed_time': duration,
                    'message': f"等待完成: {duration}秒"
                }
                
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"等待异常: {e}")
            return {
                'success': False,
                'elapsed_time': elapsed,
                'error': str(e),
                'message': f"等待异常: {str(e)}"
            }
    
    @staticmethod
    async def _check_condition(condition: str, context: Dict[str, Any]) -> bool:
        """检查条件是否满足"""
        try:
            # 简化的条件检查实现
            # 这里可以扩展支持更复杂的条件表达式
            
            # 支持变量替换
            variables = context.get('variables', {})
            for var_name, var_value in variables.items():
                condition = condition.replace(f'{{{var_name}}}', str(var_value))
            
            # 简单的条件评估
            if condition == 'true':
                return True
            elif condition == 'false':
                return False
            elif condition.startswith('time_elapsed_gt_'):
                # 时间条件：time_elapsed_gt_10
                threshold = float(condition.split('_')[-1])
                start_time = context.get('start_time', time.time())
                return time.time() - start_time > threshold
            else:
                # 尝试作为Python表达式评估（简化实现，生产环境需要更安全的方式）
                return bool(eval(condition, {"__builtins__": {}}, variables))
                
        except Exception as e:
            logger.warning(f"条件检查失败: {condition}, {e}")
            return False
    
    @staticmethod
    async def transform_data(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """转换和处理数据
        
        Args:
            parameters: 转换参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 转换结果
        """
        data = parameters['data']
        transformations = parameters['transformations']
        
        try:
            result_data = data
            transformation_results = []
            
            for transformation in transformations:
                transform_result = await UtilityTools._apply_transformation(result_data, transformation)
                transformation_results.append(transform_result)
                
                if transform_result['success']:
                    result_data = transform_result['data']
                else:
                    logger.warning(f"转换失败: {transform_result['error']}")
            
            return {
                'success': True,
                'original_data': data,
                'transformed_data': result_data,
                'transformations': transformation_results,
                'message': f"数据转换完成: {len(transformations)}个转换"
            }
            
        except Exception as e:
            logger.error(f"数据转换异常: {e}")
            return {
                'success': False,
                'original_data': data,
                'error': str(e),
                'message': f"数据转换异常: {str(e)}"
            }
    
    @staticmethod
    async def _apply_transformation(data: Any, transformation: Dict[str, Any]) -> Dict[str, Any]:
        """应用单个转换"""
        transform_type = transformation['type']
        source = transformation.get('source', '')
        target = transformation.get('target', '')
        expression = transformation.get('expression', '')
        parameters = transformation.get('parameters', {})
        
        try:
            if transform_type == 'extract':
                # 提取字段
                if source and isinstance(data, dict):
                    extracted_value = UtilityTools._extract_field(data, source)
                    if target:
                        result = {target: extracted_value}
                    else:
                        result = extracted_value
                else:
                    result = data
            
            elif transform_type == 'format':
                # 格式化数据
                if expression:
                    if isinstance(data, dict):
                        result = expression.format(**data)
                    else:
                        result = expression.format(value=data)
                else:
                    result = str(data)
            
            elif transform_type == 'calculate':
                # 计算表达式
                if expression and isinstance(data, dict):
                    # 简化的计算实现
                    result = eval(expression, {"__builtins__": {}}, data)
                else:
                    result = data
            
            elif transform_type == 'filter':
                # 过滤数据
                if isinstance(data, list) and expression:
                    result = [item for item in data if UtilityTools._evaluate_filter(item, expression)]
                elif isinstance(data, dict) and source:
                    result = {k: v for k, v in data.items() if k == source}
                else:
                    result = data
            
            elif transform_type == 'map':
                # 映射转换
                if isinstance(data, list) and expression:
                    result = [UtilityTools._apply_map_expression(item, expression) for item in data]
                else:
                    result = data
            
            elif transform_type == 'reduce':
                # 聚合操作
                if isinstance(data, list):
                    operation = parameters.get('operation', 'sum')
                    field = parameters.get('field')
                    
                    if operation == 'sum':
                        if field:
                            result = sum(item.get(field, 0) for item in data if isinstance(item, dict))
                        else:
                            result = sum(data)
                    elif operation == 'count':
                        result = len(data)
                    elif operation == 'avg':
                        if field:
                            values = [item.get(field, 0) for item in data if isinstance(item, dict)]
                        else:
                            values = data
                        result = sum(values) / len(values) if values else 0
                    else:
                        result = data
                else:
                    result = data
            
            else:
                result = data
            
            return {
                'success': True,
                'transformation': transformation,
                'data': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'transformation': transformation,
                'data': data,
                'error': str(e)
            }
    
    @staticmethod
    def _extract_field(data: Dict[str, Any], path: str) -> Any:
        """提取字段值"""
        try:
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
    def _evaluate_filter(item: Any, expression: str) -> bool:
        """评估过滤表达式"""
        try:
            if isinstance(item, dict):
                return bool(eval(expression, {"__builtins__": {}}, item))
            else:
                return bool(eval(expression, {"__builtins__": {}}, {'value': item}))
        except Exception:
            return False
    
    @staticmethod
    def _apply_map_expression(item: Any, expression: str) -> Any:
        """应用映射表达式"""
        try:
            if isinstance(item, dict):
                return eval(expression, {"__builtins__": {}}, item)
            else:
                return eval(expression, {"__builtins__": {}}, {'value': item})
        except Exception:
            return item
    
    @staticmethod
    async def evaluate_condition(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """评估条件表达式
        
        Args:
            parameters: 条件参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 评估结果
        """
        condition = parameters['condition']
        variables = parameters.get('variables', {})
        return_details = parameters.get('return_details', False)
        
        try:
            # 合并上下文变量
            all_variables = {**context.get('variables', {}), **variables}
            
            # 评估条件
            result = bool(eval(condition, {"__builtins__": {}}, all_variables))
            
            response = {
                'success': True,
                'result': result,
                'condition': condition
            }
            
            if return_details:
                response.update({
                    'variables': all_variables,
                    'evaluated_at': datetime.now().isoformat()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"条件评估异常: {e}")
            return {
                'success': False,
                'result': False,
                'condition': condition,
                'error': str(e),
                'message': f"条件评估失败: {str(e)}"
            }