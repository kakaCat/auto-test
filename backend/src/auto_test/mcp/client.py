"""MCP协议客户端实现

负责MCP协议的客户端实现，包括：
- 工具注册和管理
- 工具调用的协议处理
- 结果标准化处理
- 错误处理和重试机制
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

from ..utils.logger import get_logger
from ..database.dao_ai import MCPToolConfigDAO
from .registry import ToolRegistry
from .executor import ToolExecutor

logger = get_logger(__name__)


class MCPClient:
    """MCP协议客户端
    
    提供统一的MCP工具调用接口，支持：
    - 工具注册和发现
    - 异步工具调用
    - 结果标准化
    - 错误处理和重试
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化MCP客户端
        
        Args:
            config: 客户端配置
        """
        self.config = config or {}
        self.registry = ToolRegistry()
        self.executor = ToolExecutor()
        self._initialized = False
        
    async def initialize(self) -> None:
        """初始化客户端，加载工具配置"""
        if self._initialized:
            return
            
        try:
            # 从数据库加载工具配置
            await self._load_tool_configs()
            
            # 注册内置工具
            await self._register_builtin_tools()
            
            self._initialized = True
            logger.info("MCP客户端初始化完成")
            
        except Exception as e:
            logger.error(f"MCP客户端初始化失败: {e}")
            raise
    
    async def register_tool(self, tool_name: str, tool_schema: Dict[str, Any], 
                          tool_impl: Optional[callable] = None) -> bool:
        """注册MCP工具
        
        Args:
            tool_name: 工具名称
            tool_schema: 工具Schema定义
            tool_impl: 工具实现函数（可选）
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 验证Schema格式
            if not self._validate_tool_schema(tool_schema):
                raise ValueError(f"工具Schema格式无效: {tool_name}")
            
            # 注册到工具注册表
            success = await self.registry.register_tool(tool_name, tool_schema, tool_impl)
            
            if success:
                # 保存到数据库
                await self._save_tool_config(tool_name, tool_schema)
                logger.info(f"工具注册成功: {tool_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"工具注册失败 {tool_name}: {e}")
            return False
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any], 
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调用MCP工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 工具执行结果
        """
        if not self._initialized:
            await self.initialize()
        
        call_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            logger.info(f"开始调用工具: {tool_name}, call_id: {call_id}")
            
            # 获取工具定义
            tool_def = await self.registry.get_tool(tool_name)
            if not tool_def:
                raise ValueError(f"工具不存在: {tool_name}")
            
            # 验证参数
            validated_params = await self._validate_parameters(tool_def, parameters)
            
            # 执行工具
            result = await self.executor.execute_tool(
                tool_name=tool_name,
                tool_def=tool_def,
                parameters=validated_params,
                context=context or {}
            )
            
            # 标准化结果
            standardized_result = self._standardize_result(result, call_id, start_time)
            
            logger.info(f"工具调用成功: {tool_name}, call_id: {call_id}")
            return standardized_result
            
        except Exception as e:
            logger.error(f"工具调用失败: {tool_name}, call_id: {call_id}, error: {e}")
            return self._create_error_result(str(e), call_id, start_time)
    
    async def list_tools(self, tool_type: Optional[str] = None, 
                        enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取可用工具列表
        
        Args:
            tool_type: 工具类型筛选
            enabled_only: 是否只返回启用的工具
            
        Returns:
            List[Dict[str, Any]]: 工具列表
        """
        if not self._initialized:
            await self.initialize()
            
        return await self.registry.list_tools(tool_type, enabled_only)
    
    async def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具Schema定义
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[Dict[str, Any]]: 工具Schema，不存在时返回None
        """
        if not self._initialized:
            await self.initialize()
            
        tool_def = await self.registry.get_tool(tool_name)
        return tool_def.get('schema') if tool_def else None
    
    async def _load_tool_configs(self) -> None:
        """从数据库加载工具配置"""
        try:
            configs = MCPToolConfigDAO.get_all_enabled()
            for config in configs:
                tool_name = config['tool_name']
                schema_def = json.loads(config['schema_definition'])
                
                await self.registry.register_tool(tool_name, schema_def)
                logger.debug(f"加载工具配置: {tool_name}")
                
        except Exception as e:
            logger.error(f"加载工具配置失败: {e}")
            raise
    
    async def _register_builtin_tools(self) -> None:
        """注册内置工具"""
        from .tools import HttpTools, ValidationTools, UtilityTools
        
        # 注册HTTP工具
        await HttpTools.register_tools(self)
        
        # 注册验证工具
        await ValidationTools.register_tools(self)
        
        # 注册实用工具
        await UtilityTools.register_tools(self)
        
        logger.info("内置工具注册完成")
    
    async def _save_tool_config(self, tool_name: str, tool_schema: Dict[str, Any]) -> None:
        """保存工具配置到数据库"""
        try:
            config_data = {
                'tool_name': tool_name,
                'tool_type': tool_schema.get('type', 'custom'),
                'schema_definition': json.dumps(tool_schema, ensure_ascii=False),
                'is_enabled': True,
                'config_data': json.dumps(self.config.get(tool_name, {}), ensure_ascii=False)
            }
            
            MCPToolConfigDAO.create_or_update(config_data)
            
        except Exception as e:
            logger.error(f"保存工具配置失败 {tool_name}: {e}")
            raise
    
    def _validate_tool_schema(self, schema: Dict[str, Any]) -> bool:
        """验证工具Schema格式"""
        required_fields = ['name', 'description', 'inputSchema']
        
        for field in required_fields:
            if field not in schema:
                logger.error(f"工具Schema缺少必需字段: {field}")
                return False
        
        # 验证inputSchema格式
        input_schema = schema.get('inputSchema', {})
        if not isinstance(input_schema, dict) or 'type' not in input_schema:
            logger.error("inputSchema格式无效")
            return False
        
        return True
    
    async def _validate_parameters(self, tool_def: Dict[str, Any], 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """验证工具参数"""
        schema = tool_def.get('schema', {})
        input_schema = schema.get('inputSchema', {})
        
        # 基础类型验证
        if input_schema.get('type') == 'object':
            properties = input_schema.get('properties', {})
            required = input_schema.get('required', [])
            
            # 检查必需参数
            for req_param in required:
                if req_param not in parameters:
                    raise ValueError(f"缺少必需参数: {req_param}")
            
            # 验证参数类型（简化版本）
            validated = {}
            for param_name, param_value in parameters.items():
                if param_name in properties:
                    validated[param_name] = param_value
                else:
                    logger.warning(f"未知参数: {param_name}")
                    validated[param_name] = param_value
            
            return validated
        
        return parameters
    
    def _standardize_result(self, result: Any, call_id: str, start_time: datetime) -> Dict[str, Any]:
        """标准化工具执行结果"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'success': True,
            'call_id': call_id,
            'result': result,
            'metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration
            }
        }
    
    def _create_error_result(self, error_message: str, call_id: str, start_time: datetime) -> Dict[str, Any]:
        """创建错误结果"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'success': False,
            'call_id': call_id,
            'error': error_message,
            'result': None,
            'metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration
            }
        }