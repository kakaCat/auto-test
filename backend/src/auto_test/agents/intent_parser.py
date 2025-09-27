"""意图理解组件

负责解析用户的自然语言输入，识别测试意图并提取关键信息。
"""

import json
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..utils.logger import get_logger

logger = get_logger(__name__)


class IntentResult(BaseModel):
    """意图解析结果"""
    intent: str = Field(description="识别的意图类型")
    confidence: float = Field(description="置信度", ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(description="提取的实体信息")
    actions: List[Dict[str, Any]] = Field(description="需要执行的动作列表")
    context: Dict[str, Any] = Field(description="上下文信息", default_factory=dict)


class IntentParser(BaseAgent):
    """意图理解组件
    
    负责：
    - 解析用户自然语言输入
    - 识别测试意图类型
    - 提取关键实体信息
    - 生成动作序列
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # 预定义意图类型
        self.intent_types = {
            'api_test': 'API接口测试',
            'workflow_test': '工作流测试',
            'data_validation': '数据验证',
            'performance_test': '性能测试',
            'integration_test': '集成测试',
            'regression_test': '回归测试',
            'smoke_test': '冒烟测试'
        }
        
        # 关键词映射
        self.intent_keywords = {
            'api_test': ['接口', 'API', 'api', '调用', '请求', '响应'],
            'workflow_test': ['流程', '工作流', '步骤', '顺序', '串联'],
            'data_validation': ['验证', '校验', '检查', '断言', '数据'],
            'performance_test': ['性能', '压力', '负载', '并发', '响应时间'],
            'integration_test': ['集成', '联调', '端到端', 'e2e'],
            'regression_test': ['回归', '重复', '批量'],
            'smoke_test': ['冒烟', '基础', '快速']
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理意图理解
        
        Args:
            input_data: 包含用户输入的数据
            
        Returns:
            Dict[str, Any]: 意图解析结果
        """
        # 验证输入
        self.validate_input(input_data, ['user_input'])
        
        user_input = input_data['user_input']
        context = input_data.get('context', {})
        
        logger.info(f"开始意图理解: {user_input[:100]}...")
        
        try:
            # 1. 预处理用户输入
            processed_input = self._preprocess_input(user_input)
            
            # 2. 基于规则的初步意图识别
            rule_based_intent = self._rule_based_intent_detection(processed_input)
            
            # 3. 使用LLM进行深度意图理解
            llm_result = await self._llm_intent_understanding(processed_input, context, rule_based_intent)
            
            # 4. 后处理和验证
            final_result = self._post_process_result(llm_result, rule_based_intent)
            
            logger.info(f"意图理解完成: {final_result.intent} (置信度: {final_result.confidence})")
            
            return {
                'intent': final_result.intent,
                'confidence': final_result.confidence,
                'entities': final_result.entities,
                'actions': final_result.actions,
                'context': final_result.context,
                'raw_input': user_input,
                'processed_input': processed_input
            }
            
        except Exception as e:
            logger.error(f"意图理解失败: {e}")
            raise
    
    def _preprocess_input(self, user_input: str) -> str:
        """预处理用户输入
        
        Args:
            user_input: 原始用户输入
            
        Returns:
            str: 预处理后的输入
        """
        # 去除多余空格
        processed = re.sub(r'\s+', ' ', user_input.strip())
        
        # 统一标点符号
        processed = processed.replace('，', ',').replace('。', '.')
        
        # 转换常见缩写
        abbreviations = {
            'api': 'API',
            'http': 'HTTP',
            'json': 'JSON',
            'xml': 'XML',
            'url': 'URL'
        }
        
        for abbr, full in abbreviations.items():
            processed = re.sub(rf'\b{abbr}\b', full, processed, flags=re.IGNORECASE)
        
        return processed
    
    def _rule_based_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """基于规则的意图检测
        
        Args:
            user_input: 预处理后的用户输入
            
        Returns:
            Dict[str, Any]: 规则检测结果
        """
        intent_scores = {}
        
        # 计算每个意图的匹配分数
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in user_input.lower():
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        # 找到最高分意图
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
        else:
            best_intent = 'api_test'  # 默认意图
            confidence = 0.1
        
        return {
            'intent': best_intent,
            'confidence': confidence,
            'all_scores': intent_scores
        }
    
    async def _llm_intent_understanding(self, user_input: str, context: Dict[str, Any], 
                                      rule_hint: Dict[str, Any]) -> IntentResult:
        """使用LLM进行深度意图理解
        
        Args:
            user_input: 预处理后的用户输入
            context: 上下文信息
            rule_hint: 规则检测提示
            
        Returns:
            IntentResult: LLM解析结果
        """
        # 构建提示词
        prompt = self._build_intent_prompt(user_input, context, rule_hint)
        
        # 调用LLM
        response = await self.call_llm(prompt)
        
        # 解析LLM响应
        try:
            result_data = json.loads(response)
            return IntentResult(**result_data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"LLM响应解析失败，使用规则结果: {e}")
            
            # 回退到规则结果
            return IntentResult(
                intent=rule_hint['intent'],
                confidence=rule_hint['confidence'],
                entities={},
                actions=[],
                context=context
            )
    
    def _build_intent_prompt(self, user_input: str, context: Dict[str, Any], 
                           rule_hint: Dict[str, Any]) -> list:
        """构建意图理解提示词
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            rule_hint: 规则提示
            
        Returns:
            list: 提示词消息列表
        """
        system_prompt = f"""你是一个专业的测试意图理解专家。请分析用户的自然语言输入，识别其测试意图并提取关键信息。

支持的意图类型：
{json.dumps(self.intent_types, ensure_ascii=False, indent=2)}

规则检测提示：
- 初步意图: {rule_hint['intent']}
- 置信度: {rule_hint['confidence']:.2f}

请按照以下JSON格式输出结果：
{{
    "intent": "意图类型（从支持的类型中选择）",
    "confidence": 0.95,
    "entities": {{
        "api_endpoints": ["提取的API端点"],
        "parameters": {{"参数名": "参数值"}},
        "test_data": {{"测试数据"}},
        "validation_rules": ["验证规则"],
        "systems": ["涉及的系统"],
        "modules": ["涉及的模块"]
    }},
    "actions": [
        {{
            "action": "动作类型",
            "target": "目标对象",
            "parameters": {{"参数"}},
            "dependencies": ["依赖的前置动作"],
            "timeout": 30
        }}
    ],
    "context": {{
        "priority": "high|medium|low",
        "environment": "test|staging|production",
        "tags": ["标签"]
    }}
}}

分析要点：
1. 识别用户想要测试的功能
2. 提取涉及的API接口、系统、模块
3. 确定测试场景和步骤
4. 识别测试数据需求
5. 分析验证规则和断言
"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"用户输入: {user_input}"}
        ]
        
        # 添加上下文信息
        if context:
            context_info = f"\n\n上下文信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
            messages[-1]['content'] += context_info
        
        return messages
    
    def _post_process_result(self, llm_result: IntentResult, 
                           rule_hint: Dict[str, Any]) -> IntentResult:
        """后处理和验证结果
        
        Args:
            llm_result: LLM解析结果
            rule_hint: 规则检测提示
            
        Returns:
            IntentResult: 最终结果
        """
        # 验证意图类型
        if llm_result.intent not in self.intent_types:
            logger.warning(f"无效意图类型: {llm_result.intent}，使用规则结果")
            llm_result.intent = rule_hint['intent']
        
        # 调整置信度
        if llm_result.confidence < 0.3:
            # 如果LLM置信度太低，结合规则结果
            combined_confidence = (llm_result.confidence + rule_hint['confidence']) / 2
            llm_result.confidence = min(combined_confidence, 0.8)
        
        # 确保actions不为空
        if not llm_result.actions:
            llm_result.actions = self._generate_default_actions(llm_result.intent, llm_result.entities)
        
        # 设置默认上下文
        if not llm_result.context.get('priority'):
            llm_result.context['priority'] = 'medium'
        
        if not llm_result.context.get('environment'):
            llm_result.context['environment'] = 'test'
        
        return llm_result
    
    def _generate_default_actions(self, intent: str, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成默认动作序列
        
        Args:
            intent: 意图类型
            entities: 实体信息
            
        Returns:
            List[Dict[str, Any]]: 动作列表
        """
        actions = []
        
        if intent == 'api_test':
            # API测试的默认动作
            api_endpoints = entities.get('api_endpoints', [])
            for i, endpoint in enumerate(api_endpoints):
                actions.append({
                    'action': 'api_call',
                    'target': endpoint,
                    'parameters': entities.get('parameters', {}),
                    'dependencies': [f"action_{i-1}"] if i > 0 else [],
                    'timeout': 30
                })
        
        elif intent == 'workflow_test':
            # 工作流测试的默认动作
            actions.append({
                'action': 'workflow_execution',
                'target': 'workflow_sequence',
                'parameters': entities.get('parameters', {}),
                'dependencies': [],
                'timeout': 60
            })
        
        elif intent == 'data_validation':
            # 数据验证的默认动作
            actions.append({
                'action': 'data_validation',
                'target': 'validation_rules',
                'parameters': {
                    'rules': entities.get('validation_rules', []),
                    'data': entities.get('test_data', {})
                },
                'dependencies': [],
                'timeout': 15
            })
        
        # 如果没有生成任何动作，添加一个通用动作
        if not actions:
            actions.append({
                'action': 'generic_test',
                'target': 'test_execution',
                'parameters': entities,
                'dependencies': [],
                'timeout': 30
            })
        
        return actions
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return f"""你是一个专业的测试意图理解专家，具备深度理解自然语言测试需求的能力。

你的职责：
1. 准确识别用户的测试意图类型
2. 提取关键的测试实体信息
3. 生成合理的测试动作序列
4. 确保输出格式正确且完整

支持的意图类型：
{json.dumps(self.intent_types, ensure_ascii=False, indent=2)}

请始终以JSON格式输出结果，确保结构完整且字段类型正确。

当前时间: {self._get_current_time()}
Agent ID: {self.agent_id}
"""
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().isoformat()