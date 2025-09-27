"""AI Agent层

AI Agent层是平台的"大脑"，负责理解、规划和决策，包括：
- 意图理解：解析用户自然语言输入，识别测试意图
- 流程规划：基于意图生成可执行的API调用计划
- 执行引擎：协调MCP工具执行计划，监控执行过程

架构设计：
- BaseAgent: Agent基类，提供通用功能
- IntentParser: 意图理解组件
- FlowPlanner: 流程规划组件  
- ExecutionEngine: 执行引擎组件
"""

from .base_agent import BaseAgent
from .intent_parser import IntentParser
from .flow_planner import FlowPlanner
from .execution_engine import ExecutionEngine

__all__ = [
    'BaseAgent',
    'IntentParser',
    'FlowPlanner',
    'ExecutionEngine'
]