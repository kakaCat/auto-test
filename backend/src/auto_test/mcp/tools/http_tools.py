"""HTTP工具集合

提供HTTP相关的MCP工具实现，包括：
- HTTP请求工具
- API调用工具
- 响应处理工具
"""

import aiohttp
import json
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import logging

from ...utils.logger import get_logger

logger = get_logger(__name__)


class HttpTools:
    """HTTP工具集合
    
    提供各种HTTP操作的MCP工具实现
    """
    
    @staticmethod
    async def register_tools(mcp_client) -> None:
        """注册HTTP工具到MCP客户端
        
        Args:
            mcp_client: MCP客户端实例
        """
        # 注册HTTP请求工具
        await mcp_client.register_tool(
            'http_request',
            HttpTools.get_http_request_schema(),
            HttpTools.http_request
        )
        
        # 注册API调用工具
        await mcp_client.register_tool(
            'api_call',
            HttpTools.get_api_call_schema(),
            HttpTools.api_call
        )
        
        logger.info("HTTP工具注册完成")
    
    @staticmethod
    def get_http_request_schema() -> Dict[str, Any]:
        """获取HTTP请求工具的Schema定义"""
        return {
            "name": "http_request",
            "description": "执行HTTP请求",
            "type": "http",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                        "description": "HTTP方法"
                    },
                    "url": {
                        "type": "string",
                        "description": "请求URL"
                    },
                    "headers": {
                        "type": "object",
                        "description": "请求头",
                        "default": {}
                    },
                    "body": {
                        "type": "object",
                        "description": "请求体（JSON格式）"
                    },
                    "params": {
                        "type": "object",
                        "description": "URL查询参数"
                    },
                    "timeout": {
                        "type": "number",
                        "default": 30,
                        "description": "超时时间(秒)"
                    },
                    "follow_redirects": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否跟随重定向"
                    },
                    "verify_ssl": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否验证SSL证书"
                    }
                },
                "required": ["method", "url"]
            }
        }
    
    @staticmethod
    def get_api_call_schema() -> Dict[str, Any]:
        """获取API调用工具的Schema定义"""
        return {
            "name": "api_call",
            "description": "调用已注册的API接口",
            "type": "http",
            "version": "1.0.0",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "api_id": {
                        "type": "integer",
                        "description": "API接口ID"
                    },
                    "path_params": {
                        "type": "object",
                        "description": "路径参数",
                        "default": {}
                    },
                    "query_params": {
                        "type": "object",
                        "description": "查询参数",
                        "default": {}
                    },
                    "body": {
                        "type": "object",
                        "description": "请求体"
                    },
                    "headers": {
                        "type": "object",
                        "description": "额外的请求头",
                        "default": {}
                    },
                    "timeout": {
                        "type": "number",
                        "default": 30,
                        "description": "超时时间(秒)"
                    }
                },
                "required": ["api_id"]
            }
        }
    
    @staticmethod
    async def http_request(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行HTTP请求
        
        Args:
            parameters: 请求参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 请求结果
        """
        method = parameters['method'].upper()
        url = parameters['url']
        headers = parameters.get('headers', {})
        body = parameters.get('body')
        params = parameters.get('params')
        timeout = parameters.get('timeout', 30)
        follow_redirects = parameters.get('follow_redirects', True)
        verify_ssl = parameters.get('verify_ssl', True)
        
        start_time = time.time()
        
        try:
            # 设置默认请求头
            default_headers = {
                'User-Agent': 'AI-AutoTest-Platform/1.0',
                'Accept': 'application/json, text/plain, */*'
            }
            default_headers.update(headers)
            
            # 创建连接器配置
            connector = aiohttp.TCPConnector(
                verify_ssl=verify_ssl,
                limit=100,
                limit_per_host=30
            )
            
            # 创建超时配置
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_config,
                headers=default_headers
            ) as session:
                
                # 准备请求参数
                request_kwargs = {
                    'url': url,
                    'allow_redirects': follow_redirects
                }
                
                # 添加查询参数
                if params:
                    request_kwargs['params'] = params
                
                # 添加请求体
                if body and method in ['POST', 'PUT', 'PATCH']:
                    if isinstance(body, dict):
                        request_kwargs['json'] = body
                    else:
                        request_kwargs['data'] = body
                
                # 执行请求
                async with session.request(method, **request_kwargs) as response:
                    end_time = time.time()
                    response_time = round((end_time - start_time) * 1000, 2)  # 毫秒
                    
                    # 读取响应内容
                    response_text = await response.text()
                    
                    # 尝试解析JSON
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = response_text
                    
                    # 构建结果
                    result = {
                        'status_code': response.status,
                        'status_text': response.reason,
                        'headers': dict(response.headers),
                        'body': response_data,
                        'url': str(response.url),
                        'method': method,
                        'response_time_ms': response_time,
                        'success': 200 <= response.status < 300,
                        'content_type': response.headers.get('content-type', ''),
                        'content_length': len(response_text)
                    }
                    
                    logger.info(f"HTTP请求完成: {method} {url} -> {response.status} ({response_time}ms)")
                    return result
                    
        except aiohttp.ClientError as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            logger.error(f"HTTP请求失败: {method} {url} -> {str(e)}")
            return {
                'status_code': 0,
                'status_text': 'Client Error',
                'headers': {},
                'body': None,
                'url': url,
                'method': method,
                'response_time_ms': response_time,
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
        
        except Exception as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            logger.error(f"HTTP请求异常: {method} {url} -> {str(e)}")
            raise
    
    @staticmethod
    async def api_call(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """调用已注册的API接口
        
        Args:
            parameters: 调用参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 调用结果
        """
        from ...services.api_interface_service import ApiInterfaceService
        
        api_id = parameters['api_id']
        path_params = parameters.get('path_params', {})
        query_params = parameters.get('query_params', {})
        body = parameters.get('body')
        extra_headers = parameters.get('headers', {})
        timeout = parameters.get('timeout', 30)
        
        try:
            # 获取API接口定义
            api_interface = ApiInterfaceService.get_api_interface_by_id(api_id)
            if not api_interface:
                raise ValueError(f"API接口不存在: {api_id}")
            
            # 构建请求URL
            base_url = context.get('base_url', 'http://localhost:8002')
            api_path = api_interface['path']
            
            # 替换路径参数
            for param_name, param_value in path_params.items():
                api_path = api_path.replace(f'{{{param_name}}}', str(param_value))
            
            url = urljoin(base_url, api_path)
            
            # 构建请求头
            headers = {}
            if api_interface.get('request_headers'):
                try:
                    headers.update(json.loads(api_interface['request_headers']))
                except json.JSONDecodeError:
                    pass
            headers.update(extra_headers)
            
            # 构建请求参数
            http_params = {
                'method': api_interface['method'],
                'url': url,
                'headers': headers,
                'timeout': timeout
            }
            
            # 添加查询参数
            if query_params:
                http_params['params'] = query_params
            
            # 添加请求体
            if body:
                http_params['body'] = body
            
            # 执行HTTP请求
            result = await HttpTools.http_request(http_params, context)
            
            # 添加API接口信息
            result['api_interface'] = {
                'id': api_interface['id'],
                'name': api_interface['name'],
                'description': api_interface.get('description', ''),
                'system_id': api_interface['system_id'],
                'module_id': api_interface['module_id']
            }
            
            return result
            
        except Exception as e:
            logger.error(f"API调用失败: api_id={api_id}, error={str(e)}")
            raise