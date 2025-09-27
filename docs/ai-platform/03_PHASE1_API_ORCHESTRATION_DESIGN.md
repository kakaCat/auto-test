# 第一阶段：API编排模块详细设计 (基于现有系统重构)

## 模块概述

API编排模块是AI驱动测试平台的技术原型，基于现有的FastAPI + SQLAlchemy架构进行增量式集成。核心目标是在保持现有API管理功能稳定的基础上，添加AI Agent能力，让系统能够通过自然语言理解用户意图，并将其转化为一系列API调用来完成复杂的业务流程测试。

## 现有系统集成分析

### 现有技术栈复用
- **后端框架**：FastAPI 0.104.0 (保持不变)
- **ORM框架**：SQLAlchemy 2.0.0 (保持不变)  
- **AI框架**：LangChain 0.1.0, LangGraph 0.0.40 (已有，增强使用)
- **数据库**：MySQL (保持不变)
- **日志系统**：structlog + loguru (保持不变)
- **配置管理**：Pydantic Settings (保持不变)

### 现有API管理模块复用
- **API接口管理**：复用现有的 `api_interfaces.py` 和 `ApiInterfaceService`
- **系统模块管理**：复用现有的 `systems.py` 和 `modules.py`
- **数据访问层**：复用现有的 DAO 层设计
- **响应格式**：复用现有的 `success_response` 和 `error_response`

## 核心架构

### 集成架构图

```
┌─────────────────────────────────────────────────────────────────┐
│              前端 (Vue 3 + Element Plus) - 现有+新增            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   API管理页面   │  │   AI编排界面    │  │   执行监控      │   │
│  │   (现有)        │  │   (新增)        │  │   (新增)        │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP API + WebSocket
┌─────────────────────────┴───────────────────────────────────────┐
│                FastAPI 路由层 - 现有+新增                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ api_interfaces  │  │ orchestration   │  │ executions      │   │
│  │ (现有)          │  │ (新增)          │  │ (新增)          │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                    AI Agent层 (新增)                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   意图理解      │  │   流程规划      │  │   执行引擎      │   │
│  │ Intent Parser   │  │ Flow Planner    │  │ Execution Eng   │   │
│  │ (LangChain)     │  │ (LangGraph)     │  │ (Async)         │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────┴───────────────────────────────────────┐
│                    MCP工具层 (新增)                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│ │ http_request    │ │ auth_login      │ │ data_extract    │ │ assert_equal│ │
│ │ http_get        │ │ auth_token      │ │ json_path       │ │ assert_contains│
│ │ http_post       │ │ auth_refresh    │ │ xml_parse       │ │ assert_status │ │
│ │ http_put        │ │ auth_logout     │ │ csv_read        │ │ assert_schema │ │
│ │ http_delete     │ │                 │ │                 │ │             │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────┘ │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                Service层 - 现有+增强                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ApiInterfaceServ │  │OrchestrationServ│  │ExecutionService │   │
│  │ (现有)          │  │ (新增)          │  │ (新增)          │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                   DAO层 - 现有+新增                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ApiInterfaceDAO  │  │ExecutionDAO     │  │McpToolDAO       │   │
│  │ (现有)          │  │ (新增)          │  │ (新增)          │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                   MySQL数据库 - 现有+新增                       │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │ 现有表结构      │ │ ai_executions   │ │ mcp_tool_configs│     │
│ │ api_interfaces  │ │ (新增)          │ │ (新增)          │     │
│ │ systems/modules │ │                 │ │                 │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. 列表页驱动的编排流程（基于“API调用流程列表页”）

本阶段在“API调用流程列表页”的基础上实现完整的从命名→意图→计划→可视化→保存→执行的闭环，复用现有“新建工作流”分步弹窗的交互模式。

用户路径（Step 1→5）：

1) 新建流程记录（Step1 名称目标）
- 在“API调用流程列表页”点击“新建流程”
- 填写“流程名称/目标说明/标签（可选）/偏好系统与模块（可选，仅用于推荐，不作为归属）”
- 后端创建 `api_orchestration_plans` 草稿记录，返回 `flow_id`

2) 识别意图（Step2 意图识别）
- 输入自然语言意图，或从模板/历史选择
- 后端调用“意图理解组件”解析，返回结构化意图对象

3) 生成计划（Step3 计划预览）
- 后端“流程规划组件”基于意图与上下文生成 `execution_plan`（步骤、依赖、参数映射、断言）
- 前端展示计划预览，支持关键参数占位符设置

#### Step3 计划预览——要实现什么（明确说明）

目标：把“自然语言意图 + 选中的接口上下文”转换为一个可执行但仍可编辑的结构化计划 `execution_plan`，并在前端以“可读列表 + 缺参提示”的方式预览与微调。

计划应至少包含：
- 步骤列表：每个步骤绑定一个具体接口（含 system/module），提供请求模板与输出变量。
- 依赖关系：步骤间的先后与数据依赖（例如 B 依赖 A 的输出 `orderId`）。
- 参数映射：请求参数的来源（用户输入、默认值、上一步骤响应路径）。
- 断言规则：基础正确性校验（HTTP code、字段相等、包含、数值范围等）。
- 未决占位符：需要用户在预览阶段补齐的关键入参（如 `{{customerId}}`）。

与 Step4 的关系：Step3 产出/确认“结构化计划草案”；点击“接受并进入可视化编辑”后进入 Step4 画布进行图形化微调。

##### execution_plan 结构定义（后端产出）

示例（JSON）：

```json
{
  "plan_id": "pln_xxx",
  "flow_id": "flow_123",
  "title": "创建订单并获取详情",
  "inputs": [
    { "name": "customerId", "type": "string", "required": true, "source": "user" },
    { "name": "sku", "type": "string", "required": true, "source": "user" },
    { "name": "quantity", "type": "number", "required": true, "source": "user", "default": 1 }
  ],
  "steps": [
    {
      "id": "step_create_order",
      "name": "创建订单",
      "api_interface_id": 201,
      "system_id": 10,
      "module_id": 1001,
      "request": {
        "method": "POST",
        "url": "/api/orders",
        "headers": { "Content-Type": "application/json" },
        "body": {
          "customerId": "{{customerId}}",
          "items": [ { "sku": "{{sku}}", "qty": "{{quantity}}" } ]
        }
      },
      "param_mapping": [
        { "target": "body.customerId", "from": "input.customerId" },
        { "target": "body.items[0].sku", "from": "input.sku" },
        { "target": "body.items[0].qty", "from": "input.quantity" }
      ],
      "outputs": [
        { "name": "orderId", "path": "$.data.orderId" }
      ],
      "asserts": [
        { "type": "status_code", "op": "=", "expected": 200 },
        { "type": "exists", "path": "$.data.orderId" }
      ]
    },
    {
      "id": "step_get_order",
      "name": "获取订单详情",
      "api_interface_id": 202,
      "system_id": 10,
      "module_id": 1001,
      "depends_on": ["step_create_order"],
      "request": {
        "method": "GET",
        "url": "/api/orders/{{orderId}}",
        "headers": {}
      },
      "param_mapping": [
        { "target": "path.orderId", "from": "step.step_create_order.orderId" }
      ],
      "asserts": [
        { "type": "status_code", "op": "=", "expected": 200 },
        { "type": "eq", "path": "$.data.items[0].qty", "expected": "{{quantity}}" }
      ]
    }
  ],
  "edges": [
    { "from": "step_create_order", "to": "step_get_order", "type": "data" }
  ],
  "metadata": {
    "involved_system_ids": [10],
    "involved_module_ids": [1001]
  }
}
```

类型约定（用于实现时的接口/前端类型定义，示意）：

```ts
interface ExecutionPlan {
  plan_id: string;
  flow_id: string;
  title: string;
  inputs: PlanInput[];
  steps: PlanStep[];
  edges: { from: string; to: string; type: 'data' | 'sequence' }[];
  metadata?: { involved_system_ids?: number[]; involved_module_ids?: number[] };
}
interface PlanInput { name: string; type: 'string'|'number'|'boolean'|'object'; required: boolean; source: 'user'|'env'|'secret'|'system'; default?: unknown }
interface PlanStep {
  id: string; name: string; api_interface_id: number; system_id: number; module_id: number;
  depends_on?: string[];
  request: { method: string; url: string; headers?: Record<string,string>; body?: unknown };
  param_mapping: { target: string; from: string }[];
  outputs?: { name: string; path: string }[];
  asserts?: Array<
    | { type: 'status_code'; op: '='|'in'; expected: number|number[] }
    | { type: 'exists'; path: string }
    | { type: 'eq'|'contains'|'gt'|'lt'; path: string; expected: unknown }
  >;
}
```

占位符与参数来源：
- `{{xxx}}` 表示可在预览阶段由用户补齐或由前置步骤/环境填充。
- `from` 取值规范：`input.xxx`（来自用户输入）、`env.xxx`（环境变量）、`secret.xxx`（密钥服务）、`step.<stepId>.<outputVar>`（上一步骤输出）。

##### 前端：计划预览界面（ASCII示意）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 计划预览：创建订单并获取详情                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 步骤列表                                   │ 详细/参数与断言                 │
│ 1. 创建订单 [POST /api/orders]            │ [步骤: 创建订单]                │
│ 2. 获取订单详情 [GET /api/orders/{id}]    │ 请求参数映射:                   │
│                                            │  - customerId ← 输入.customerId │
│                                            │  - sku ← 输入.sku               │
│                                            │  - qty ← 输入.quantity          │
│                                            │ 输出变量: orderId ← $.data...   │
│                                            │ 断言: status=200, exists(orderId)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 缺少参数: customerId, sku (请填写后可继续)                                   │
│ [返回上一步] [保存草稿] [接受计划并进入可视化编辑]                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

交互要点：
- 列表可展开每个步骤查看请求模板、映射和断言。
- 顶部/底部提供“保存草稿”“接受计划并进入可视化编辑（Step4）”。
- 未填写的占位符在“缺少参数”区域醒目提示，可就地编辑。

##### 后端接口约定（生成计划与校验）

- 生成：`POST /api/v1/orchestration/plan/generate`
  - 请求：`{ flow_id: string, intent_text: string, context?: { prefer_system_id?: number, prefer_module_id?: number } }`
  - 响应：`{ plan: ExecutionPlan, unresolved_inputs: string[] }`

- 校验：`POST /api/v1/orchestration/plan/validate`
  - 请求：`{ plan: ExecutionPlan }`
  - 响应：`{ ok: boolean, issues: Array<{ level: 'error'|'warn', message: string, step_id?: string }> }`

验收标准（Step3 完成态）：
- 至少生成一个包含步骤、依赖、参数映射、断言的可执行计划草案。
- 能列出所有未决占位符并支持填写；填写后校验通过。
- 可一键进入 Step4 进行可视化编辑；或保存为草稿。
- 与“系统/模块追踪”兼容：根据步骤自动聚合 `involved_system_ids/modules` 写入 `metadata`。

4) 可视化编辑（Step4 可视化）
- 打开可视化设计器，画布展示节点（API步骤）与连线（依赖）
- 左侧“接口库/工具箱”可从现有API管理模块拖拽接口到画布
- 右侧“属性面板”可编辑请求参数、输出映射、断言规则

5) 保存与执行（保存/执行）
- 保存：提交 `execution_plan + graph_json + intent_text` 写回 `api_orchestration_plans`
- 执行：填写运行入参（或由AI从文本提取），创建 `ai_executions` 记录并启动执行；通过 WebSocket 实时查看进度

#### 执行入参校验（必做）

目标：在点击“执行”前，对计划的必填输入进行一致性校验，防止无效执行。

校验规则：
- 必填检查：所有 `ExecutionPlan.inputs[].required=true` 的输入必须提供值。
- 类型检查：支持 `string/number/boolean/object`，数值范围、字符串长度、正则、枚举。
- 映射完整性：`param_mapping.from` 的来源需可解析（input/env/secret/step 输出）。
- 环境/密钥存在性：`env.*`、`secret.*` 必须存在；不存在时报错。

错误返回（HTTP 422）：
```json
{
  "code": "VALIDATION_FAILED",
  "errors": [
    { "field": "inputs.customerId", "rule": "required", "message": "customerId 不能为空" },
    { "field": "inputs.quantity", "rule": "type:number", "expected": "number", "actual": "string" },
    { "field": "steps.step_get_order.param_mapping[0]", "rule": "unresolved_source", "message": "step.step_create_order.orderId 不存在" }
  ]
}
```

接口约定：
- 预校验：`POST /api/v1/orchestration/execution/prepare`
  - 请求：`{ plan_id: string, inputs: Record<string, unknown>, env?: Record<string, string> }`
  - 响应：`{ ok: boolean, errors?: Array<...如上> }`
  - ok=false 时禁止进入执行。

前端交互：
- 在执行弹窗中联动展示未通过项，逐项修复后可重试校验。
- 支持保存“这次执行的入参模板”，便于快速复用。

#### 执行可视化内容（Run 可视化）

目标：以 DAG/时间线实时展示执行态，支持追踪、定位与复跑。

可视化要素：
- DAG 视图：节点=步骤，边=依赖；状态色板：
  - pending 灰、running 蓝、success 绿、failed 红、skipped 黄、retried 橙。
- 时间线/Gantt：按开始/结束时间展示并发与用时。
- 节点详情抽屉：
  - 基本信息：接口、系统/模块、请求方法与URL
  - 请求/响应：自动脱敏（Authorization、Set-Cookie、手机号、身份证等）
  - 断言结果：逐条通过/失败
  - 产出变量：JSONPath→值
  - 操作：仅复跑该步（依赖输入冻结）、复制 cURL、下载响应片段
- 汇总：总用时、成功/失败统计、按系统/模块的耗时与失败分布。

实时更新：WebSocket 事件
```json
{ "event": "step_started", "execution_id": "exec_1", "step_id": "step_create_order", "ts": 1710000000 }
{ "event": "log", "step_id": "step_create_order", "level": "info", "message": "POST /api/orders" }
{ "event": "step_completed", "step_id": "step_create_order", "duration_ms": 320 }
{ "event": "step_failed", "step_id": "step_get_order", "error": "404 Not Found" }
{ "event": "summary", "status": "failed", "duration_ms": 1250 }
```

ASCII 示意：
```
┌──────────────────────────────────────────────────────────────────────────┐
│ 执行监控：FLOW-2024-0001  状态：运行中  用时：00:00:12               │
├───────────────┬─────────────────────────────────────────────────────────┤
│ DAG 视图      │ 节点详情                                                 │
│ ● 创建订单    │ [创建订单]                                               │
│  └→ ● 获取详情 │ - 状态：success  (320ms)                                 │
│               │ - 接口：POST /api/orders                                 │
│               │ - 断言：2/2 通过                                         │
│               │ - 输出：orderId=123456                                   │
│               │ [复制cURL] [查看请求/响应] [仅复跑该步]                  │
├───────────────┴─────────────────────────────────────────────────────────┤
│ 日志 / 时间线：...（流式追加）                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

ASCII 页面与交互布局（修正后）：

```
┌──────────────────────────────────────────────────────────────────────────┐
│ API调用流程列表页                                                        │
│ ┌───────────────┐ ┌───────────────────────────────────────────────────┐ │
│ │ 左侧筛选区    │ │ 流程列表（名称｜状态｜更新人｜更新时间）        │ │
│ │ - 关键字搜索  │ │ [新建流程] [导入] [执行历史]                    │ │
│ │ - 标签多选    │ │                                               ↑  │ │
│ │ - 状态筛选    │ │ 支持列设置：显示最近执行状态、用时、失败计数       │ │
│ │   · 草稿/发布  │ │                                               │  │ │
│ │   · 归档      │ │                                               │  │ │
│ │ - 最近执行状态│ │                                               │  │ │
│ │   · 成功/失败  │ │                                               │  │ │
│ │   · 运行中/未执行││                                               │  │ │
│ │ - 负责人/团队  │ │                                               │  │ │
│ │ - 时间范围    │ │                                               │  │ │
│ │   · 更新/执行  │ │                                               │  │ │
│ │ - 涉及系统多选 │ │                                               │  │ │
│ │ - 涉及模块多选 │ │                                               │  │ │
│ │   （基于步骤聚合，仅作筛选，不代表归属）  │                      │  │ │
│ │ - 高级：仅看我参与/我关注             │                          │  │ │
│ └───────────────┘ └───────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘

新建流程（分步弹窗 / 复用现有“新建工作流”交互模式）
┌──────────────────────────────────────────────────────────────────────────┐
│ Step1 名称目标  →  Step2 意图识别  →  Step3 计划预览  →  Step4 可视化  → 保存/执行 │
├──────────────────────────────────────────────────────────────────────────┤
│ Step4 可视化设计器                                                       │
│ ┌───────────────┐   ┌───────────────────────────────┐   ┌───────────┐  │
│ │ 接口库/工具箱 │ → │ 画布(节点=API步骤, 边=依赖)   │ ← │ 参数/断言 │  │
│ └───────────────┘   └───────────────────────────────┘   └───────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

#### 列表页布局与筛选修正说明

- 流程是“跨系统/模块”的集合，不属于单一系统/模块；因此左侧不应以“系统树归属”来分类。
- “涉及系统/模块”来自计划中步骤的聚合字段（见 ExecutionPlan.metadata），仅用于筛选/统计，不表示归属关系。
- “偏好系统与模块”仅在新建流程时作为推荐上下文来源（用于意图理解与接口推荐），不会写入流程归属。

推荐筛选项：关键字、标签、状态（草稿/已发布/归档）、最近执行状态（成功/失败/运行中/未执行）、负责人/团队、时间范围、涉及系统/模块（多选，仅筛选）、高级选项（只看我参与/我关注）。

后端接口（示例）：
- `POST /orchestration/flows` → 创建草稿流程记录（返回 `flow_id`）
- `POST /orchestration/flows/{flow_id}/intent-parse` → 文本意图解析
- `POST /orchestration/flows/{flow_id}/plan-generate` → 生成API调用计划
- `POST /orchestration/flows/{flow_id}/visualize/graph` → 生成初始画布Graph DSL
- `PUT  /orchestration/flows/{flow_id}` → 保存计划与画布（plan + graph_json + intent_text）
- `POST /orchestration/flows/{flow_id}/execute` → 触发执行（返回 `execution_id`）
- `WS   /ws/executions/{execution_id}` → 推送执行进度与日志

数据存储：
- `api_orchestration_plans`：`plan_name`、`intent_text`、`execution_plan`、`graph_json`、`is_template`、`created_by`
- `ai_executions`：`execution_id`、`agent_type`、`input_data`、`output_data`、`status`、`error_message`

与现有模块复用：
- 接口库与系统/模块筛选复用现有 `ApiInterfaceService` 与前端 `api-management` 模块
- 画布节点的“API步骤”来自现有API接口定义，参数/断言表单沿用既有表单样式与校验

权限与回滚：
- AI能力通过功能开关启用；保存采用草稿态；所有新增能力不破坏现有接口与数据

### 2. 意图理解组件 (Intent Parser)

**职责**：解析自然语言输入，提取测试意图和关键信息

**输入示例**：
```
"创建一个新用户，然后给他发送欢迎邮件，最后验证邮件是否发送成功"
```

**输出结构**：
```json
{
  "intent": "api_workflow_test",
  "entities": {
    "actions": [
      {
        "action": "create_user",
        "parameters": ["username", "email", "password"],
        "expected_result": "user_created"
      },
      {
        "action": "send_welcome_email", 
        "parameters": ["user_id"],
        "dependencies": ["create_user.user_id"],
        "expected_result": "email_sent"
      },
      {
        "action": "verify_email_status",
        "parameters": ["email_id"],
        "dependencies": ["send_welcome_email.email_id"],
        "expected_result": "email_delivered"
      }
    ]
  }
}
```

### 3. 流程规划组件 (Flow Planner)

**职责**：将解析后的意图转化为具体的API调用计划

**规划算法**：
1. **依赖分析**：构建动作间的依赖关系图
2. **参数映射**：确定动作间的数据传递关系
3. **错误处理**：为每个步骤定义失败处理策略
4. **并行优化**：识别可并行执行的独立动作

**输出示例**：
```json
{
  "execution_plan": {
    "steps": [
      {
        "step_id": "step_1",
        "tool": "http_post",
        "parameters": {
          "url": "/api/users",
          "body": {
            "username": "test_user_{{timestamp}}",
            "email": "test{{timestamp}}@example.com", 
            "password": "Test123!"
          }
        },
        "success_criteria": {
          "status_code": 201,
          "response_schema": "user_creation_schema"
        },
        "output_mapping": {
          "user_id": "$.data.id",
          "email": "$.data.email"
        }
      },
      {
        "step_id": "step_2", 
        "tool": "http_post",
        "parameters": {
          "url": "/api/notifications/email",
          "body": {
            "user_id": "{{step_1.user_id}}",
            "template": "welcome",
            "email": "{{step_1.email}}"
          }
        },
        "dependencies": ["step_1"],
        "success_criteria": {
          "status_code": 200,
          "response_contains": "email_id"
        },
        "output_mapping": {
          "email_id": "$.data.email_id"
        }
      }
    ]
  }
}
```

### 4. 执行引擎 (Execution Engine)

**职责**：按计划调用MCP工具，处理数据传递和异常情况

**执行流程**：
```
1. 初始化执行上下文
2. 按依赖顺序执行步骤
3. 处理步骤间数据传递
4. 验证执行结果
5. 记录执行日志
6. 处理异常和重试
```

### 5. 跨系统/模块追踪与审计（新增）

定位与原则
- 流程（Plan）不属于任何单一系统/模块，但需要记录“涉及的系统/模块集合”用于筛选、统计与审计。
- 步骤（Step）精确绑定其 `system_id/module_id/api_interface_id`，统一来源于现有 API 管理。
- 执行（Execution）按步骤聚合出本次“实际涉及的系统/模块”与按系统的性能/错误指标。

Plan/Step/Execution 字段建议
- Plan（`api_orchestration_plans`）
  - `metadata.involved_system_ids: number[]`
  - `metadata.involved_module_ids: number[]`
  - `metadata.tags?: string[]`
  - `metadata.owner_team?: string`
  - `metadata.data_sensitivity?: 'internal'|'pii'|'secret'`
  - `metadata.risk_level?: 'low'|'medium'|'high'`
  - `preferences.prefer_system_id?: number`（仅推荐上下文）
  - `preferences.prefer_module_id?: number`（仅推荐上下文）
- Step（`api_orchestration_steps` 或存于 plan.steps）
  - `api_interface_id: number`
  - `system_id: number`
  - `module_id: number`
  - `data_classification?: 'open'|'internal'|'pii'|'secret'`
  - `cross_boundary?: boolean`（是否跨系统）
- Execution（`ai_executions` + 明细）
  - `resolved_system_ids: number[]`
  - `resolved_module_ids: number[]`
  - `system_stats: Record<string, { count: number; success: number; failed: number; latency_ms: number }>`
  - `audit_entries: Array<{ ts:number; level:'info'|'warn'|'error'; message:string; step_id?:string }>`

写入与聚合时机
- 保存计划时：从 `steps[*].system_id/module_id` 去重聚合到 `plan.metadata.involved_*`。
- 执行完成时：从执行明细聚合 `resolved_*` 与 `system_stats`，用于报表与筛选。

接口约定（筛选/查询）
- 列表筛选：
  - `GET /api/v1/orchestration/flows?keyword=&tags=&status=&involved_system_ids=10,11&involved_module_ids=1001&owner=&exec_status=&updated_from=&updated_to=`
  - 响应项中返回 `metadata.involved_system_ids/modules` 用于渲染徽章。
- 详情查询：
  - `GET /api/v1/orchestration/flows/{id}` 返回 `plan`, `execution_plan`, `metadata`。
- 执行汇总：
  - `GET /api/v1/orchestration/executions/{execution_id}/summary` 返回 `system_stats`, `resolved_*` 与 `asserts_summary`。

列表与详情 UI 建议
- 列表页：行内展示“涉及系统/模块”徽章（最多 3 个，超出折叠为 +N）。
- 详情页：新增“涉及系统/模块”卡片；点击徽章筛选该系统/模块相关步骤。
- 可视化设计器：节点按 `system_id` 着色；图例展示系统-颜色映射。

权限与脱敏
- Wrapper 层按系统/模块进行访问控制：用户仅能看到被授权系统/模块的步骤与日志。
- Converter 层统一脱敏：`Authorization`、`Set-Cookie`、手机号/身份证等敏感字段。

验收标准
- 保存计划后 `metadata.involved_*` 正确聚合；列表筛选生效。
- 执行完成后可在执行详情看到 `resolved_*` 与 `system_stats` 并可下载审计日志。
- 可视化中节点按系统着色；点击徽章可过滤相关节点与日志。

向后兼容
- 新增字段为可选；历史计划无 `metadata.involved_*` 不影响加载与执行。
- “偏好系统/模块”仅用于推荐，不写入归属，避免与“涉及系统/模块”混淆。

## MCP工具详细设计

### HTTP请求工具集

**工具名称**：`http_request`
**描述**：执行HTTP请求并返回结构化响应

**Schema定义**：
```json
{
  "name": "http_request",
  "description": "Execute HTTP request to API endpoint",
  "inputSchema": {
    "type": "object",
    "properties": {
      "method": {
        "type": "string",
        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
        "description": "HTTP method"
      },
      "url": {
        "type": "string", 
        "description": "API endpoint URL"
      },
      "headers": {
        "type": "object",
        "description": "Request headers"
      },
      "body": {
        "type": "object",
        "description": "Request body for POST/PUT requests"
      },
      "timeout": {
        "type": "number",
        "default": 30,
        "description": "Request timeout in seconds"
      }
    },
    "required": ["method", "url"]
  }
}
```

**返回格式**：
```json
{
  "status_code": 200,
  "headers": {...},
  "body": {...},
  "response_time": 0.234,
  "success": true,
  "error": null
}
```

### 认证工具集

**工具名称**：`auth_login`
**描述**：执行用户认证并获取访问令牌

**Schema定义**：
```json
{
  "name": "auth_login",
  "description": "Authenticate user and obtain access token",
  "inputSchema": {
    "type": "object",
    "properties": {
      "auth_type": {
        "type": "string",
        "enum": ["basic", "oauth2", "jwt", "api_key"],
        "description": "Authentication type"
      },
      "credentials": {
        "type": "object",
        "description": "Authentication credentials"
      },
      "endpoint": {
        "type": "string",
        "description": "Authentication endpoint URL"
      }
    },
    "required": ["auth_type", "credentials", "endpoint"]
  }
}
```

### 数据提取工具集

**工具名称**：`data_extract`
**描述**：从API响应中提取特定数据

**Schema定义**：
```json
{
  "name": "data_extract",
  "description": "Extract data from API response using JSONPath or XPath",
  "inputSchema": {
    "type": "object", 
    "properties": {
      "source": {
        "type": "object",
        "description": "Source data object"
      },
      "path": {
        "type": "string",
        "description": "JSONPath or XPath expression"
      },
      "data_type": {
        "type": "string",
        "enum": ["json", "xml", "text"],
        "description": "Source data type"
      }
    },
    "required": ["source", "path"]
  }
}
```

### 断言验证工具集

**工具名称**：`assert_equal`
**描述**：验证两个值是否相等

**Schema定义**：
```json
{
  "name": "assert_equal",
  "description": "Assert that two values are equal",
  "inputSchema": {
    "type": "object",
    "properties": {
      "actual": {
        "description": "Actual value to check"
      },
      "expected": {
        "description": "Expected value"
      },
      "message": {
        "type": "string",
        "description": "Custom assertion message"
      }
    },
    "required": ["actual", "expected"]
  }
}
```

## 上下文管理设计

### 执行上下文结构

```json
{
  "execution_id": "exec_{{uuid}}",
  "start_time": "2024-01-15T10:30:00Z",
  "status": "running",
  "variables": {
    "step_1.user_id": "12345",
    "step_1.email": "test@example.com",
    "step_2.email_id": "email_67890"
  },
  "step_results": [
    {
      "step_id": "step_1",
      "status": "completed",
      "start_time": "2024-01-15T10:30:01Z",
      "end_time": "2024-01-15T10:30:02Z",
      "tool_used": "http_post",
      "result": {...},
      "success": true
    }
  ],
  "errors": []
}
```

### 变量传递机制

**模板语法**：使用 `{{variable_name}}` 语法引用变量
**作用域规则**：
- 全局变量：在整个执行过程中可用
- 步骤变量：仅在当前步骤及其后续步骤中可用
- 临时变量：仅在当前步骤中可用

**示例**：
```json
{
  "url": "/api/users/{{step_1.user_id}}/orders",
  "body": {
    "product_id": "{{global.default_product_id}}",
    "quantity": "{{temp.calculated_quantity}}"
  }
}
```

## 错误处理策略

### 错误分类

1. **网络错误**：连接超时、DNS解析失败
2. **HTTP错误**：4xx、5xx状态码
3. **数据错误**：响应格式不符合预期
4. **业务错误**：业务逻辑验证失败

### 重试策略

```json
{
  "retry_policy": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "base_delay": 1.0,
    "max_delay": 30.0,
    "retryable_errors": [
      "network_timeout",
      "http_5xx",
      "rate_limit"
    ]
  }
}
```

### 失败处理

```json
{
  "failure_handling": {
    "on_step_failure": "stop_execution",
    "cleanup_actions": [
      {
        "condition": "step_1.success && step_2.failed",
        "action": "rollback_user_creation"
      }
    ],
    "notification": {
      "channels": ["email", "slack"],
      "recipients": ["test-team@company.com"]
    }
  }
}
```

## 基于现有系统的实现计划

### 第一周：基础设施集成
- [ ] 安装MCP相关依赖到现有requirements.txt
- [ ] 创建新的数据库表结构 (ai_executions, mcp_tool_configs)
- [ ] 在现有config.py中添加AI和MCP配置
- [ ] 创建MCP工具基础框架 (backend/src/auto_test/mcp/)

### 第二周：AI Agent层开发
- [ ] 基于现有LangChain集成创建Agent基类
- [ ] 实现意图理解组件 (复用现有日志系统)
- [ ] 开发流程规划引擎 (集成现有Service层模式)
- [ ] 创建执行引擎 (复用现有异步支持)

### 第三周：API层集成
- [ ] 在现有FastAPI路由中添加编排接口
- [ ] 创建OrchestrationService (遵循现有Service层规范)
- [ ] 实现ExecutionDAO (复用现有DAO模式)
- [ ] 添加WebSocket支持用于实时监控

### 第四周：前端集成与测试
- [ ] 在现有Vue项目中添加AI编排界面
- [ ] 集成现有Element Plus组件库
- [ ] 复用现有API调用模式 (axios)
- [ ] 端到端测试确保现有功能无回归

## 技术实现细节

### 依赖管理
在现有 `requirements.txt` 中添加：
```txt
# MCP Protocol support
mcp>=0.1.0

# Enhanced AI capabilities (基于现有LangChain)
openai>=1.0.0

# WebSocket support (基于现有FastAPI)
websockets>=11.0.0
```

### 配置集成
扩展现有 `config.py`：
```python
class Config:
    # 现有配置保持不变...
    
    # 新增AI配置
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    DEFAULT_LLM_MODEL: str = Field(default="gpt-3.5-turbo")
    
    # 新增MCP配置
    MCP_TOOLS_ENABLED: bool = Field(default=True)
    MAX_CONCURRENT_EXECUTIONS: int = Field(default=5)
```

### 数据库集成
复用现有数据库连接，添加新表：
```sql
-- 集成到现有数据库schema
USE auto_test;

-- AI执行记录表
CREATE TABLE ai_executions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(64) UNIQUE NOT NULL,
    agent_type VARCHAR(32) NOT NULL,
    input_data JSON NOT NULL,
    output_data JSON,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- MCP工具配置表
CREATE TABLE mcp_tool_configs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tool_name VARCHAR(64) NOT NULL,
    tool_type VARCHAR(32) NOT NULL,
    schema_definition JSON NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 成功验收标准

### 功能验收
- [ ] 能理解并执行包含3-5个步骤的API编排任务
- [ ] 支持常见的HTTP方法和认证方式
- [ ] 正确处理步骤间的数据传递
- [ ] 提供清晰的执行日志和错误信息

### 性能验收
- [ ] 单个API调用响应时间 < 5秒
- [ ] 复杂编排任务完成时间 < 30秒
- [ ] 支持并发执行多个编排任务

### 可靠性验收
- [ ] 网络异常重试成功率 > 90%
- [ ] 执行结果一致性 100%
- [ ] 内存泄漏检测通过

---

*本文档为API编排模块的详细技术设计，实现过程中如有调整请及时更新文档。*