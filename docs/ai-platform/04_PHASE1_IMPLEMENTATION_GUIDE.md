# 第一阶段实施指南 - API编排模块开发

## 立即开始的准备工作

### 1. 环境准备

**更新依赖**：
```bash
# 在 backend/ 目录下执行
cd backend
echo "
# MCP Protocol support
mcp>=0.1.0

# Enhanced AI capabilities
openai>=1.0.0

# WebSocket support
websockets>=11.0.0
fastapi-websocket>=0.1.0
" >> requirements.txt

pip install -r requirements.txt
```

**环境变量配置**：
```bash
# 在 backend/.env 中添加
echo "
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_LLM_MODEL=gpt-3.5-turbo

# MCP Configuration
MCP_TOOLS_ENABLED=true
MAX_CONCURRENT_EXECUTIONS=5
EXECUTION_TIMEOUT=300
" >> .env
```

### 2. 数据库准备

**创建新表结构（对齐03文档最新字段）**：
```sql
-- 在现有数据库中执行
USE auto_test;

-- AI执行记录表
CREATE TABLE ai_executions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(64) UNIQUE NOT NULL,
    agent_type VARCHAR(32) NOT NULL,
    input_data JSON NOT NULL,
    output_data JSON,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_execution_id (execution_id),
    INDEX idx_status (status),
    INDEX idx_agent_type (agent_type)
);

-- MCP工具配置表
CREATE TABLE mcp_tool_configs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tool_name VARCHAR(64) NOT NULL,
    tool_type VARCHAR(32) NOT NULL,
    schema_definition JSON NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    config_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_tool_name (tool_name),
    INDEX idx_tool_type (tool_type),
    INDEX idx_enabled (is_enabled)
);

-- API编排计划表
CREATE TABLE api_orchestration_plans (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(128) NOT NULL,
    description TEXT,
    intent_text TEXT NOT NULL,
    execution_plan JSON NOT NULL,
    graph_json JSON NULL,
    metadata JSON NULL,          -- 包含 involved_system_ids、involved_module_ids、tags、owner_team 等
    preferences JSON NULL,       -- 包含 prefer_system_id、prefer_module_id，仅用于推荐上下文
    status ENUM('draft','published','archived') DEFAULT 'draft',
    tags JSON NULL,
    created_by VARCHAR(64),
    is_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_executed_at TIMESTAMP NULL,
    last_execution_status ENUM('success','failed','running','never') DEFAULT 'never',
    INDEX idx_plan_name (plan_name),
    INDEX idx_created_by (created_by),
    INDEX idx_is_template (is_template),
    INDEX idx_status (status)
);
```

## 第一周：基础设施开发

### Day 1-2: 配置和基础框架

**1. 扩展配置文件**：
```python
# backend/src/auto_test/config.py
# 在现有Config类中添加：

class Config:
    # ... 现有配置保持不变 ...
    
    # AI Configuration
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    DEFAULT_LLM_MODEL: str = Field(default="gpt-3.5-turbo", env="DEFAULT_LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.1, env="LLM_TEMPERATURE")
    
    # MCP Configuration
    MCP_TOOLS_ENABLED: bool = Field(default=True, env="MCP_TOOLS_ENABLED")
    MCP_SERVER_HOST: str = Field(default="localhost", env="MCP_SERVER_HOST")
    MCP_SERVER_PORT: int = Field(default=8003, env="MCP_SERVER_PORT")
    
    # Execution Configuration
    MAX_CONCURRENT_EXECUTIONS: int = Field(default=5, env="MAX_CONCURRENT_EXECUTIONS")
    EXECUTION_TIMEOUT: int = Field(default=300, env="EXECUTION_TIMEOUT")
    ENABLE_EXECUTION_LOGGING: bool = Field(default=True, env="ENABLE_EXECUTION_LOGGING")
```

**2. 创建MCP工具基础框架**：
```python
# backend/src/auto_test/mcp/__init__.py
"""MCP (Model Context Protocol) 工具层"""

# backend/src/auto_test/mcp/client.py
"""MCP客户端实现"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MCPClient:
    """MCP协议客户端"""
    
    def __init__(self, config):
        self.config = config
        self.tools = {}
        
    async def register_tool(self, tool_name: str, tool_schema: Dict[str, Any]):
        """注册MCP工具"""
        self.tools[tool_name] = tool_schema
        logger.info(f"注册MCP工具: {tool_name}")
        
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未找到工具: {tool_name}")
            
        logger.info(f"调用MCP工具: {tool_name}, 参数: {parameters}")
        
        # 这里实现具体的工具调用逻辑
        # 暂时返回模拟结果
        return {
            "success": True,
            "result": f"工具 {tool_name} 执行成功",
            "data": parameters
        }
```

### Day 3-4: MCP工具实现

**创建HTTP工具集**：
```python
# backend/src/auto_test/mcp/tools/http_tools.py
"""HTTP请求相关的MCP工具"""
import aiohttp
import json
from typing import Dict, Any, Optional
from ..client import MCPClient
from ...utils.logger import get_logger

logger = get_logger(__name__)

class HttpTools:
    """HTTP请求工具集"""
    
    @staticmethod
    async def http_request(
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """执行HTTP请求"""
        try:
            async with aiohttp.ClientSession() as session:
                kwargs = {
                    'url': url,
                    'headers': headers or {},
                    'timeout': aiohttp.ClientTimeout(total=timeout)
                }
                
                if body and method.upper() in ['POST', 'PUT', 'PATCH']:
                    kwargs['json'] = body
                
                async with session.request(method.upper(), **kwargs) as response:
                    response_data = await response.text()
                    
                    try:
                        response_json = json.loads(response_data)
                    except json.JSONDecodeError:
                        response_json = response_data
                    
                    return {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "body": response_json,
                        "success": 200 <= response.status < 300,
                        "response_time": 0  # TODO: 计算实际响应时间
                    }
                    
        except Exception as e:
            logger.error(f"HTTP请求失败: {str(e)}")
            return {
                "status_code": 0,
                "headers": {},
                "body": None,
                "success": False,
                "error": str(e)
            }

# 工具Schema定义
HTTP_REQUEST_SCHEMA = {
    "name": "http_request",
    "description": "执行HTTP请求",
    "inputSchema": {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "description": "HTTP方法"
            },
            "url": {
                "type": "string",
                "description": "请求URL"
            },
            "headers": {
                "type": "object",
                "description": "请求头"
            },
            "body": {
                "type": "object",
                "description": "请求体"
            },
            "timeout": {
                "type": "number",
                "default": 30,
                "description": "超时时间(秒)"
            }
        },
        "required": ["method", "url"]
    }
}
```

### Day 5-7: AI Agent基础框架

**创建Agent基类**：
```python
# backend/src/auto_test/agents/__init__.py
"""AI Agent层"""

# backend/src/auto_test/agents/base_agent.py
"""Agent基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from ..utils.logger import get_logger
from ..config import Config

logger = get_logger(__name__)

class BaseAgent(ABC):
    """AI Agent基类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = self._create_llm()
        
    def _create_llm(self):
        """创建LLM实例"""
        return ChatOpenAI(
            model_name=self.config.DEFAULT_LLM_MODEL,
            temperature=self.config.LLM_TEMPERATURE,
            openai_api_key=self.config.OPENAI_API_KEY
        )
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行Agent"""
        try:
            logger.info(f"Agent {self.__class__.__name__} 开始处理")
            result = await self.process(input_data)
            logger.info(f"Agent {self.__class__.__name__} 处理完成")
            return result
        except Exception as e:
            logger.error(f"Agent {self.__class__.__name__} 处理失败: {str(e)}")
            raise
```

## 第二周：核心AI组件开发

### Day 8-10: 意图理解组件

**创建意图解析器**：
```python
# backend/src/auto_test/agents/intent_parser.py
"""意图理解组件"""
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .base_agent import BaseAgent

class IntentResult(BaseModel):
    """意图解析结果"""
    intent: str = Field(description="识别的意图类型")
    entities: Dict[str, Any] = Field(description="提取的实体信息")
    actions: List[Dict[str, Any]] = Field(description="需要执行的动作列表")
    confidence: float = Field(description="置信度")

class IntentParser(BaseAgent):
    """意图理解组件"""
    
    def __init__(self, config):
        super().__init__(config)
        self.output_parser = PydanticOutputParser(pydantic_object=IntentResult)
        self.prompt = ChatPromptTemplate.from_template("""
你是一个API测试意图理解专家。请分析用户的自然语言输入，识别其测试意图并提取关键信息。

用户输入: {user_input}

请按照以下格式输出:
{format_instructions}

分析要点:
1. 识别用户想要测试的功能
2. 提取涉及的API接口
3. 确定测试场景和步骤
4. 识别测试数据需求
""")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理意图理解"""
        user_input = input_data.get("user_input", "")
        
        formatted_prompt = self.prompt.format(
            user_input=user_input,
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = await self.llm.apredict(formatted_prompt)
        result = self.output_parser.parse(response)
        
        return {
            "intent": result.intent,
            "entities": result.entities,
            "actions": result.actions,
            "confidence": result.confidence,
            "raw_response": response
        }
```

### Day 11-14: 流程规划和执行引擎

**创建流程规划器**：
```python
# backend/src/auto_test/agents/flow_planner.py
"""流程规划组件"""
from typing import Dict, Any, List
from .base_agent import BaseAgent

class FlowPlanner(BaseAgent):
    """流程规划组件"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划"""
        intent_result = input_data.get("intent_result", {})
        actions = intent_result.get("actions", [])
        
        execution_plan = {
            "plan_id": f"plan_{int(time.time())}",
            "steps": [],
            "dependencies": {},
            "estimated_duration": 0,
            "metadata": {
                "involved_system_ids": [],
                "involved_module_ids": []
            }
        }
        
        for i, action in enumerate(actions):
            step = {
                "step_id": f"step_{i+1}",
                "action_type": action.get("action", "unknown"),
                "tool": self._map_action_to_tool(action),
                "parameters": action.get("parameters", {}),
                "dependencies": action.get("dependencies", []),
                "timeout": action.get("timeout", 30)
            }
            execution_plan["steps"].append(step)
        
        return execution_plan
    
    def _map_action_to_tool(self, action: Dict[str, Any]) -> str:
        """将动作映射到MCP工具"""
        action_type = action.get("action", "")
        
        mapping = {
            "create_user": "http_request",
            "send_email": "http_request", 
            "verify_status": "http_request",
            "login": "auth_login",
            "logout": "auth_logout"
        }
        
        return mapping.get(action_type, "http_request")
```

## 第三周：API层集成

### Day 15-17: FastAPI路由集成

**创建编排API（补充计划生成/校验与执行校验，保持与03一致）**：
```python
# backend/src/auto_test/api/orchestration.py
"""AI编排API接口"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from ..services.orchestration_service import OrchestrationService
from ..utils.response import success_response, error_response

router = APIRouter(tags=["AI编排"])

class OrchestrationRequest(BaseModel):
    """编排请求模型"""
    user_input: str
    context: Dict[str, Any] = {}

class PlanGenerateRequest(BaseModel):
    flow_id: str
    intent_text: str
    context: Dict[str, Any] = {}

class PlanValidateRequest(BaseModel):
    plan: Dict[str, Any]

class ExecValidateInputsRequest(BaseModel):
    plan: Dict[str, Any]
    inputs: Dict[str, Any]

@router.post("/orchestration/v1/execute", summary="执行AI编排")
async def execute_orchestration(request: OrchestrationRequest):
    """执行AI编排任务"""
    try:
        result = await OrchestrationService.execute_orchestration(
            user_input=request.user_input,
            context=request.context
        )
        return success_response(data=result, message="编排执行成功")
    except Exception as e:
        return error_response(message=f"编排执行失败: {str(e)}")

@router.post("/orchestration/plan/generate", summary="生成执行计划（Step3）")
async def generate_plan(req: PlanGenerateRequest):
    try:
        result = await OrchestrationService.generate_plan(req.flow_id, req.intent_text, req.context)
        return success_response(data=result, message="计划生成成功")
    except Exception as e:
        return error_response(message=f"计划生成失败: {str(e)}")

@router.post("/orchestration/plan/validate", summary="校验执行计划（Step3）")
async def validate_plan(req: PlanValidateRequest):
    try:
        result = await OrchestrationService.validate_plan(req.plan)
        return success_response(data=result, message="计划校验通过")
    except Exception as e:
        return error_response(message=f"计划校验失败: {str(e)}")

@router.post("/orchestration/execute/validate-inputs", summary="执行前入参校验")
async def validate_execution_inputs(req: ExecValidateInputsRequest):
    try:
        result = await OrchestrationService.validate_execution_inputs(req.plan, req.inputs)
        return success_response(data=result, message="入参校验通过")
    except Exception as e:
        return error_response(message=f"入参校验失败: {str(e)}")

@router.get("/orchestration/v1/executions/{execution_id}", summary="获取执行状态")
async def get_execution_status(execution_id: str):
    """获取执行状态"""
    try:
        status = await OrchestrationService.get_execution_status(execution_id)
        return success_response(data=status, message="获取状态成功")
    except Exception as e:
        return error_response(message=f"获取状态失败: {str(e)}")

@router.websocket("/orchestration/v1/monitor/{execution_id}")
async def monitor_execution(websocket: WebSocket, execution_id: str):
    """实时监控执行过程"""
    await websocket.accept()
    try:
        async for update in OrchestrationService.monitor_execution(execution_id):
            await websocket.send_json(update)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
```

> 事件协议（与03文档一致）：
> - `execution_started`、`step_started`、`step_succeeded`、`step_failed`、`execution_completed`
> - 每个事件包含：`timestamp`、`execution_id`、`step_id?`、`message`、`metrics?`、`logs?`

### Day 18-21: Service层实现

**创建编排服务**：
```python
# backend/src/auto_test/services/orchestration_service.py
"""编排服务层"""
import asyncio
import uuid
from typing import Dict, Any, AsyncGenerator
from ..agents.intent_parser import IntentParser
from ..agents.flow_planner import FlowPlanner
from ..agents.execution_engine import ExecutionEngine
from ..database.dao import ExecutionDAO
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class OrchestrationService:
    """编排服务类"""
    
    @staticmethod
    async def execute_orchestration(user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行编排任务"""
        config = Config()
        execution_id = str(uuid.uuid4())
        
        try:
            # 1. 意图理解
            intent_parser = IntentParser(config)
            intent_result = await intent_parser.run({"user_input": user_input})
            
            # 2. 流程规划
            flow_planner = FlowPlanner(config)
            execution_plan = await flow_planner.run({"intent_result": intent_result})

            # 2.1 计划校验（Step3）
            await OrchestrationService.validate_plan(execution_plan)

            # 3. 保存执行记录
            await ExecutionDAO.create_execution({
                "execution_id": execution_id,
                "agent_type": "orchestration",
                "input_data": {"user_input": user_input, "context": context},
                "status": "running"
            })
            
            # 4. 异步执行
            asyncio.create_task(OrchestrationService._execute_plan(execution_id, execution_plan))
            
            return {
                "execution_id": execution_id,
                "status": "started",
                "intent_result": intent_result,
                "execution_plan": execution_plan
            }
            
        except Exception as e:
            logger.error(f"编排执行失败: {str(e)}")
            await ExecutionDAO.update_execution(execution_id, {
                "status": "failed",
                "error_message": str(e)
            })
            raise

    @staticmethod
    async def generate_plan(flow_id: str, intent_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划（Step3）"""
        # 省略：调用 IntentParser/FlowPlanner，并聚合 metadata.involved_system_ids/modules
        return {"plan": {"steps": [], "metadata": {"involved_system_ids": [], "involved_module_ids": []}}, "unresolved_inputs": []}

    @staticmethod
    async def validate_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
        """校验执行计划（Step3）"""
        # 省略：结构校验、依赖闭环校验、参数映射校验
        return {"ok": True, "issues": []}

    @staticmethod
    async def validate_execution_inputs(plan: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行前入参校验（必选）"""
        # 省略：验证必填参数、类型与范围、正则、跨字段规则
        return {"ok": True, "errors": []}
    
    @staticmethod
    async def _execute_plan(execution_id: str, execution_plan: Dict[str, Any]):
        """执行计划"""
        config = Config()
        execution_engine = ExecutionEngine(config)
        
        try:
            result = await execution_engine.run({
                "execution_id": execution_id,
                "execution_plan": execution_plan
            })
            
            await ExecutionDAO.update_execution(execution_id, {
                "status": "completed",
                "output_data": result
            })
            
        except Exception as e:
            logger.error(f"计划执行失败: {str(e)}")
            await ExecutionDAO.update_execution(execution_id, {
                "status": "failed", 
                "error_message": str(e)
            })
```

## 第四周：前端集成

### Day 22-24: Vue组件开发

**创建AI编排界面（补充计划预览与可视化监控）**：
```vue
<!-- frontend/src/views/api-orchestration/index.vue -->
<template>
  <div class="orchestration-page">
    <div class="page-header">
      <h1>AI API编排</h1>
      <p>通过自然语言描述，让AI自动编排和执行API测试</p>
    </div>
    
    <div class="main-content">
      <!-- 输入区域 -->
      <div class="input-section">
        <el-card>
          <template #header>
            <span>描述您的测试需求</span>
          </template>
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="4"
            placeholder="例如：创建一个新用户，然后给他发送欢迎邮件，最后验证邮件是否发送成功"
          />
          <div class="input-actions">
            <el-button type="primary" @click="executeOrchestration" :loading="executing">
              <el-icon><VideoPlay /></el-icon>
              执行编排
            </el-button>
            <el-button @click="clearInput">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 计划预览（Step3） -->
      <div class="plan-preview" v-if="executionResult?.execution_plan">
        <el-card>
          <template #header>
            <span>计划预览（Step3）</span>
          </template>
          <el-table :data="executionResult.execution_plan.steps">
            <el-table-column prop="step_id" label="步骤ID" />
            <el-table-column prop="action_type" label="动作" />
            <el-table-column prop="tool" label="工具" />
            <el-table-column label="参数">
              <template #default="{ row }">
                {{ JSON.stringify(row.parameters) }}
              </template>
            </el-table-column>
          </el-table>
          <div class="plan-actions">
            <el-button @click="validatePlan" type="primary">校验计划</el-button>
          </div>
        </el-card>
      </div>

      <!-- 执行结果区域（Run 视图） -->
      <div class="result-section" v-if="executionResult">
        <el-card>
          <template #header>
            <span>执行结果</span>
            <el-tag :type="getStatusType(executionResult.status)">
              {{ executionResult.status }}
            </el-tag>
          </template>
          
          <!-- 意图理解结果 -->
          <div class="intent-result">
            <h4>意图理解</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="识别意图">
                {{ executionResult.intent_result?.intent }}
              </el-descriptions-item>
              <el-descriptions-item label="置信度">
                {{ (executionResult.intent_result?.confidence * 100).toFixed(1) }}%
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- 执行计划（DAG简化渲染） -->
          <div class="execution-plan">
            <h4>执行计划</h4>
            <el-timeline>
              <el-timeline-item
                v-for="step in executionResult.execution_plan?.steps"
                :key="step.step_id"
                :type="getStepStatus(step)"
              >
                <div class="step-content">
                  <strong>{{ step.action_type }}</strong>
                  <p>工具: {{ step.tool }}</p>
                  <p>参数: {{ JSON.stringify(step.parameters) }}</p>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Delete } from '@element-plus/icons-vue'
import unifiedApi from '@/api/unified-api'

const userInput = ref('')
const executing = ref(false)
const executionResult = ref(null)

const executeOrchestration = async () => {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入测试需求描述')
    return
  }
  
  executing.value = true
  
  try {
    const response = await unifiedApi.orchestrationApi.execute({
      user_input: userInput.value,
      context: {}
    })
    
    if (response.success) {
      executionResult.value = response.data
      ElMessage.success('编排执行成功')
      
      // 开始监控执行状态
      monitorExecution(response.data.execution_id)
    } else {
      ElMessage.error(response.message || '编排执行失败')
    }
  } catch (error) {
    ElMessage.error('编排执行失败: ' + error.message)
  } finally {
    executing.value = false
  }
}

const monitorExecution = (executionId) => {
  // 使用WebSocket监控执行进度
  const ws = new WebSocket(`ws://localhost:8002/api/orchestration/v1/monitor/${executionId}`)
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data)
    // 更新执行状态
    if (executionResult.value) {
      Object.assign(executionResult.value, update)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error)
  }
}

const clearInput = () => {
  userInput.value = ''
  executionResult.value = null
}

const getStatusType = (status) => {
  const typeMap = {
    'running': 'warning',
    'completed': 'success', 
    'failed': 'danger',
    'pending': 'info'
  }
  return typeMap[status] || 'info'
}

const getStepStatus = (step) => {
  return step.status === 'completed' ? 'success' : 'primary'
}
</script>
```

### Day 25-28: 集成测试和优化

**集成测试清单**：
- [ ] 验证现有API管理功能无回归
- [ ] 测试AI编排的端到端流程
- [ ] 验证WebSocket实时监控功能
- [ ] 测试错误处理和异常情况
- [ ] 性能测试和优化

## 验收标准

### 功能验收
- [ ] 能够理解简单的自然语言测试需求
- [ ] 能够生成基本的API调用计划
- [ ] 能够执行HTTP请求并返回结果
- [ ] 提供实时的执行状态监控
- [ ] 现有API管理功能完全正常

### 技术验收
- [ ] 代码遵循现有项目规范
- [ ] 数据库操作使用现有DAO模式
- [ ] 日志记录使用现有日志系统
- [ ] 错误处理符合现有响应格式
- [ ] 前端界面风格与现有页面一致

### 性能验收
- [ ] AI意图理解响应时间 < 5秒
- [ ] 简单编排任务执行时间 < 30秒
- [ ] 系统整体响应时间增加 < 20%
- [ ] 支持至少5个并发编排任务

---

*本指南提供了第一阶段开发的详细步骤，请按照计划逐步实施，确保每个阶段的质量和稳定性。*
const validatePlan = async () => {
  if (!executionResult.value?.execution_plan) return
  const res = await unifiedApi.orchestrationApi.validatePlan({
    plan: executionResult.value.execution_plan
  })
  if (res.success && res.data?.ok) {
    ElMessage.success('计划校验通过')
  } else {
    ElMessage.error('计划校验失败')
  }
}