"""MCP (Model Context Protocol) 工具层

MCP工具层是AI编排模块的核心基础设施，提供：
- 统一的工具注册和管理机制
- 标准化的工具调用接口
- 工具执行结果的标准化处理
- 工具配置和权限管理

架构设计：
- MCPClient: MCP协议客户端，负责工具注册和调用
- ToolRegistry: 工具注册表，管理所有可用工具
- BaseTools: 基础工具集合，提供常用工具实现
- ToolExecutor: 工具执行器，负责工具的实际执行
"""

from .client import MCPClient
from .registry import ToolRegistry
from .executor import ToolExecutor
from .tools import *

__all__ = [
    'MCPClient',
    'ToolRegistry', 
    'ToolExecutor',
    'HttpTools',
    'ValidationTools',
    'UtilityTools'
]