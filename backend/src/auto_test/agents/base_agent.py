"""Agent基类

提供所有AI Agent的通用功能和接口定义。
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..utils.logger import get_logger
from ..config import Config

logger = get_logger(__name__)


class BaseAgent(ABC):
    """AI Agent基类
    
    提供所有Agent的通用功能：
    - LLM模型管理
    - 执行上下文管理
    - 错误处理和重试
    - 执行日志记录
    - 性能监控
    """
    
    def __init__(self, config: Optional[Config] = None):
        """初始化Agent
        
        Args:
            config: 配置对象
        """
        self.config = config or Config()
        self.agent_id = str(uuid.uuid4())
        self.agent_type = self.__class__.__name__
        
        # 初始化LLM
        self.llm = self._create_llm()
        
        # 执行统计
        self._stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_duration': 0.0
        }
        
        logger.info(f"Agent初始化完成: {self.agent_type}, ID: {self.agent_id}")
    
    def _create_llm(self):
        """创建LLM实例"""
        try:
            # 如果没有配置OpenAI API密钥，使用模拟LLM
            if not self.config.OPENAI_API_KEY:
                logger.info("未配置OpenAI API密钥，使用模拟LLM")
                from .mock_llm import MockLLM
                return MockLLM(
                    model_name=self.config.DEFAULT_LLM_MODEL,
                    temperature=self.config.LLM_TEMPERATURE
                )
            else:
                return ChatOpenAI(
                    model_name=self.config.DEFAULT_LLM_MODEL,
                    temperature=self.config.LLM_TEMPERATURE,
                    openai_api_key=self.config.OPENAI_API_KEY,
                    max_tokens=4000,
                    request_timeout=60
                )
        except Exception as e:
            logger.error(f"创建LLM实例失败: {e}")
            raise
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据（抽象方法）
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
    
    async def run(self, input_data: Dict[str, Any], 
                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """运行Agent
        
        Args:
            input_data: 输入数据
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            logger.info(f"Agent开始执行: {self.agent_type}, execution_id: {execution_id}")
            
            # 更新统计
            self._stats['total_executions'] += 1
            
            # 准备执行上下文
            exec_context = {
                'execution_id': execution_id,
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'start_time': start_time.isoformat(),
                **(context or {})
            }
            
            # 执行处理逻辑
            result = await self.process(input_data)
            
            # 计算执行时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 更新统计
            self._stats['successful_executions'] += 1
            self._stats['total_duration'] += duration
            
            # 构建返回结果
            final_result = {
                'success': True,
                'result': result,
                'metadata': {
                    'execution_id': execution_id,
                    'agent_type': self.agent_type,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration
                }
            }
            
            logger.info(f"Agent执行成功: {self.agent_type}, duration: {duration:.2f}s")
            return final_result
            
        except Exception as e:
            # 计算执行时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 更新统计
            self._stats['failed_executions'] += 1
            self._stats['total_duration'] += duration
            
            logger.error(f"Agent执行失败: {self.agent_type}, error: {str(e)}")
            
            # 构建错误结果
            error_result = {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'result': None,
                'metadata': {
                    'execution_id': execution_id,
                    'agent_type': self.agent_type,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration
                }
            }
            
            return error_result
    
    async def call_llm(self, messages: list, **kwargs) -> str:
        """调用LLM
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Returns:
            str: LLM响应
        """
        try:
            # 转换消息格式
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    if msg['role'] == 'system':
                        formatted_messages.append(SystemMessage(content=msg['content']))
                    elif msg['role'] == 'user':
                        formatted_messages.append(HumanMessage(content=msg['content']))
                else:
                    formatted_messages.append(msg)
            
            # 调用LLM
            response = await self.llm.agenerate([formatted_messages])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise
    
    def get_system_prompt(self) -> str:
        """获取系统提示词（子类可重写）
        
        Returns:
            str: 系统提示词
        """
        return f"""你是一个专业的{self.agent_type}，负责处理自动化测试相关的任务。

请遵循以下原则：
1. 准确理解用户需求
2. 提供结构化的输出
3. 确保输出格式正确
4. 处理异常情况

当前时间: {datetime.now().isoformat()}
Agent ID: {self.agent_id}
"""
    
    def get_stats(self) -> Dict[str, Any]:
        """获取Agent执行统计
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = self._stats.copy()
        
        # 计算平均执行时间
        if stats['total_executions'] > 0:
            stats['avg_duration'] = stats['total_duration'] / stats['total_executions']
            stats['success_rate'] = stats['successful_executions'] / stats['total_executions']
        else:
            stats['avg_duration'] = 0
            stats['success_rate'] = 0
        
        return stats
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_duration': 0.0
        }
        logger.info(f"Agent统计已重置: {self.agent_type}")
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: list) -> None:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            required_fields: 必需字段列表
            
        Raises:
            ValueError: 输入数据无效时抛出
        """
        if not isinstance(input_data, dict):
            raise ValueError("输入数据必须是字典格式")
        
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"缺少必需字段: {field}")
            
            if input_data[field] is None or input_data[field] == "":
                raise ValueError(f"字段不能为空: {field}")
    
    def create_structured_prompt(self, user_input: str, context: Dict[str, Any] = None) -> list:
        """创建结构化提示词
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            list: 消息列表
        """
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()}
        ]
        
        # 添加上下文信息
        if context:
            context_str = f"上下文信息:\n{self._format_context(context)}\n\n"
            user_input = context_str + user_input
        
        messages.append({'role': 'user', 'content': user_input})
        
        return messages
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文信息
        
        Args:
            context: 上下文字典
            
        Returns:
            str: 格式化后的上下文字符串
        """
        formatted_lines = []
        
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                import json
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_str = str(value)
            
            formatted_lines.append(f"- {key}: {value_str}")
        
        return "\n".join(formatted_lines)