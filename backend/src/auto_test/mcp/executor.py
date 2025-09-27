"""工具执行器实现

负责MCP工具的实际执行，包括：
- 工具调用的安全执行
- 超时控制和重试机制
- 执行结果的标准化处理
- 执行日志和监控
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolExecutor:
    """工具执行器
    
    提供安全、可控的工具执行环境，支持：
    - 异步工具执行
    - 超时控制
    - 重试机制
    - 执行监控
    - 错误处理
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化工具执行器
        
        Args:
            config: 执行器配置
        """
        self.config = config or {}
        self.default_timeout = self.config.get('default_timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1)
        
        # 执行统计
        self._execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'timeout_executions': 0,
            'retry_executions': 0
        }
    
    async def execute_tool(self, tool_name: str, tool_def: Dict[str, Any], 
                          parameters: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """执行工具
        
        Args:
            tool_name: 工具名称
            tool_def: 工具定义
            parameters: 工具参数
            context: 执行上下文
            
        Returns:
            Any: 工具执行结果
            
        Raises:
            Exception: 工具执行失败时抛出异常
        """
        self._execution_stats['total_executions'] += 1
        
        # 获取工具实现
        tool_impl = tool_def.get('implementation')
        if not tool_impl:
            # 如果没有实现函数，尝试动态查找
            tool_impl = await self._resolve_tool_implementation(tool_name, tool_def)
        
        if not tool_impl:
            raise ValueError(f"工具实现不存在: {tool_name}")
        
        # 获取执行配置
        timeout = context.get('timeout', self.default_timeout)
        max_retries = context.get('max_retries', self.max_retries)
        
        # 执行工具（带重试）
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self._execution_stats['retry_executions'] += 1
                    logger.info(f"重试执行工具: {tool_name}, 第{attempt}次重试")
                    await asyncio.sleep(self.retry_delay * attempt)
                
                # 执行工具（带超时）
                result = await self._execute_with_timeout(
                    tool_impl, parameters, context, timeout
                )
                
                self._execution_stats['successful_executions'] += 1
                logger.debug(f"工具执行成功: {tool_name}")
                return result
                
            except asyncio.TimeoutError as e:
                self._execution_stats['timeout_executions'] += 1
                last_exception = e
                logger.warning(f"工具执行超时: {tool_name}, 尝试 {attempt + 1}/{max_retries + 1}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"工具执行失败: {tool_name}, 尝试 {attempt + 1}/{max_retries + 1}, 错误: {e}")
                
                # 某些错误不需要重试
                if self._is_non_retryable_error(e):
                    break
        
        # 所有重试都失败了
        self._execution_stats['failed_executions'] += 1
        logger.error(f"工具执行最终失败: {tool_name}, 错误: {last_exception}")
        raise last_exception
    
    async def _execute_with_timeout(self, tool_impl: Callable, parameters: Dict[str, Any], 
                                   context: Dict[str, Any], timeout: float) -> Any:
        """带超时的工具执行
        
        Args:
            tool_impl: 工具实现函数
            parameters: 工具参数
            context: 执行上下文
            timeout: 超时时间（秒）
            
        Returns:
            Any: 工具执行结果
            
        Raises:
            asyncio.TimeoutError: 执行超时
        """
        try:
            # 如果是异步函数
            if asyncio.iscoroutinefunction(tool_impl):
                result = await asyncio.wait_for(
                    tool_impl(parameters, context), 
                    timeout=timeout
                )
            else:
                # 如果是同步函数，在线程池中执行
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, tool_impl, parameters, context),
                    timeout=timeout
                )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"工具执行超时: {timeout}秒")
            raise
    
    async def _resolve_tool_implementation(self, tool_name: str, 
                                         tool_def: Dict[str, Any]) -> Optional[Callable]:
        """动态解析工具实现
        
        Args:
            tool_name: 工具名称
            tool_def: 工具定义
            
        Returns:
            Optional[Callable]: 工具实现函数，找不到时返回None
        """
        try:
            # 根据工具类型查找实现
            tool_type = tool_def.get('metadata', {}).get('type', 'custom')
            
            if tool_type == 'http':
                from .tools.http_tools import HttpTools
                return getattr(HttpTools, tool_name, None)
            
            elif tool_type == 'validation':
                from .tools.validation_tools import ValidationTools
                return getattr(ValidationTools, tool_name, None)
            
            elif tool_type == 'utility':
                from .tools.utility_tools import UtilityTools
                return getattr(UtilityTools, tool_name, None)
            
            else:
                logger.warning(f"未知工具类型: {tool_type}")
                return None
                
        except Exception as e:
            logger.error(f"解析工具实现失败 {tool_name}: {e}")
            return None
    
    def _is_non_retryable_error(self, error: Exception) -> bool:
        """判断是否为不可重试的错误
        
        Args:
            error: 异常对象
            
        Returns:
            bool: 是否为不可重试的错误
        """
        # 参数错误、权限错误等不需要重试
        non_retryable_types = (
            ValueError,
            TypeError,
            KeyError,
            AttributeError
        )
        
        return isinstance(error, non_retryable_types)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计信息
        
        Returns:
            Dict[str, Any]: 执行统计信息
        """
        stats = self._execution_stats.copy()
        
        # 计算成功率
        total = stats['total_executions']
        if total > 0:
            stats['success_rate'] = stats['successful_executions'] / total
            stats['failure_rate'] = stats['failed_executions'] / total
            stats['timeout_rate'] = stats['timeout_executions'] / total
        else:
            stats['success_rate'] = 0
            stats['failure_rate'] = 0
            stats['timeout_rate'] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """重置执行统计"""
        self._execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'timeout_executions': 0,
            'retry_executions': 0
        }
        logger.info("执行统计已重置")