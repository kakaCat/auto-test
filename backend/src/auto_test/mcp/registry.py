"""工具注册表实现

负责管理所有MCP工具的注册、发现和元数据管理。
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """工具注册表
    
    管理所有可用的MCP工具，提供：
    - 工具注册和注销
    - 工具发现和查询
    - 工具元数据管理
    - 工具版本控制
    """
    
    def __init__(self):
        """初始化工具注册表"""
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def register_tool(self, tool_name: str, tool_schema: Dict[str, Any], 
                          tool_impl: Optional[Callable] = None) -> bool:
        """注册工具
        
        Args:
            tool_name: 工具名称
            tool_schema: 工具Schema定义
            tool_impl: 工具实现函数
            
        Returns:
            bool: 注册是否成功
        """
        async with self._lock:
            try:
                if tool_name in self._tools:
                    logger.warning(f"工具已存在，将覆盖: {tool_name}")
                
                tool_def = {
                    'name': tool_name,
                    'schema': tool_schema,
                    'implementation': tool_impl,
                    'registered_at': datetime.now().isoformat(),
                    'enabled': True,
                    'call_count': 0,
                    'last_called': None,
                    'metadata': {
                        'type': tool_schema.get('type', 'custom'),
                        'version': tool_schema.get('version', '1.0.0'),
                        'description': tool_schema.get('description', ''),
                        'tags': tool_schema.get('tags', [])
                    }
                }
                
                self._tools[tool_name] = tool_def
                logger.info(f"工具注册成功: {tool_name}")
                return True
                
            except Exception as e:
                logger.error(f"工具注册失败 {tool_name}: {e}")
                return False
    
    async def unregister_tool(self, tool_name: str) -> bool:
        """注销工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 注销是否成功
        """
        async with self._lock:
            if tool_name in self._tools:
                del self._tools[tool_name]
                logger.info(f"工具注销成功: {tool_name}")
                return True
            else:
                logger.warning(f"工具不存在，无法注销: {tool_name}")
                return False
    
    async def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具定义
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[Dict[str, Any]]: 工具定义，不存在时返回None
        """
        return self._tools.get(tool_name)
    
    async def list_tools(self, tool_type: Optional[str] = None, 
                        enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取工具列表
        
        Args:
            tool_type: 工具类型筛选
            enabled_only: 是否只返回启用的工具
            
        Returns:
            List[Dict[str, Any]]: 工具列表
        """
        tools = []
        
        for tool_name, tool_def in self._tools.items():
            # 筛选条件
            if enabled_only and not tool_def.get('enabled', True):
                continue
                
            if tool_type and tool_def.get('metadata', {}).get('type') != tool_type:
                continue
            
            # 构建返回信息
            tool_info = {
                'name': tool_name,
                'description': tool_def.get('schema', {}).get('description', ''),
                'type': tool_def.get('metadata', {}).get('type', 'custom'),
                'version': tool_def.get('metadata', {}).get('version', '1.0.0'),
                'enabled': tool_def.get('enabled', True),
                'call_count': tool_def.get('call_count', 0),
                'last_called': tool_def.get('last_called'),
                'registered_at': tool_def.get('registered_at'),
                'tags': tool_def.get('metadata', {}).get('tags', [])
            }
            
            tools.append(tool_info)
        
        # 按名称排序
        tools.sort(key=lambda x: x['name'])
        return tools
    
    async def update_tool_stats(self, tool_name: str) -> None:
        """更新工具调用统计
        
        Args:
            tool_name: 工具名称
        """
        async with self._lock:
            if tool_name in self._tools:
                tool_def = self._tools[tool_name]
                tool_def['call_count'] = tool_def.get('call_count', 0) + 1
                tool_def['last_called'] = datetime.now().isoformat()
    
    async def enable_tool(self, tool_name: str) -> bool:
        """启用工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 操作是否成功
        """
        async with self._lock:
            if tool_name in self._tools:
                self._tools[tool_name]['enabled'] = True
                logger.info(f"工具已启用: {tool_name}")
                return True
            return False
    
    async def disable_tool(self, tool_name: str) -> bool:
        """禁用工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 操作是否成功
        """
        async with self._lock:
            if tool_name in self._tools:
                self._tools[tool_name]['enabled'] = False
                logger.info(f"工具已禁用: {tool_name}")
                return True
            return False
    
    async def get_tool_stats(self) -> Dict[str, Any]:
        """获取工具统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        total_tools = len(self._tools)
        enabled_tools = sum(1 for tool in self._tools.values() if tool.get('enabled', True))
        total_calls = sum(tool.get('call_count', 0) for tool in self._tools.values())
        
        # 按类型统计
        type_stats = {}
        for tool in self._tools.values():
            tool_type = tool.get('metadata', {}).get('type', 'custom')
            type_stats[tool_type] = type_stats.get(tool_type, 0) + 1
        
        # 最常用工具
        most_used = sorted(
            [(name, tool.get('call_count', 0)) for name, tool in self._tools.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_tools': total_tools,
            'enabled_tools': enabled_tools,
            'disabled_tools': total_tools - enabled_tools,
            'total_calls': total_calls,
            'type_distribution': type_stats,
            'most_used_tools': most_used
        }
    
    async def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """搜索工具
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Dict[str, Any]]: 匹配的工具列表
        """
        query_lower = query.lower()
        matching_tools = []
        
        for tool_name, tool_def in self._tools.items():
            # 搜索工具名称
            if query_lower in tool_name.lower():
                matching_tools.append(tool_def)
                continue
            
            # 搜索描述
            description = tool_def.get('schema', {}).get('description', '').lower()
            if query_lower in description:
                matching_tools.append(tool_def)
                continue
            
            # 搜索标签
            tags = tool_def.get('metadata', {}).get('tags', [])
            if any(query_lower in tag.lower() for tag in tags):
                matching_tools.append(tool_def)
        
        return matching_tools