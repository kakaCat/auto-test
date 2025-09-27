# 第三阶段：需求管理模块详细设计

## 模块概述

需求管理模块是平台的最终集成阶段，目标是实现"需求即测试"的完整闭环。AI Agent能够理解业务需求，自动生成测试策略，并调用前两个阶段的能力执行完整的测试验证。

## 核心架构

### 组件架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                需求管理AI Agent                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   需求解析      │  │   策略生成      │  │   执行编排      │   │
│  │ Req Analyzer    │  │Strategy Generator│  │ Exec Orchestr   │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   知识图谱      │  │   测试规划      │  │   结果分析      │   │
│  │ Knowledge Graph │  │ Test Planner    │  │ Result Analyzer │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────┴───────────────────────────────────────┐
│                    需求管理MCP工具集                            │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ 需求工具集  │ │ 策略工具集  │ │ 编排工具集  │ │ 分析工具集  │ │
│ │             │ │             │ │             │ │             │ │
│ │ • req_parse │ │ • gen_cases │ │ • call_api  │ │ • analyze   │ │
│ │ • req_trace │ │ • gen_data  │ │ • call_ui   │ │ • report    │ │
│ │ • req_link  │ │ • gen_plan  │ │ • schedule  │ │ • metrics   │ │
│ │ • req_valid │ │ • optimize  │ │ • monitor   │ │ • insights  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                    执行能力层                                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ API编排模块 │ │ UI测试模块  │ │ 数据验证    │ │ 性能监控    │ │
│ │ (阶段1)     │ │ (阶段2)     │ │             │ │             │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. 需求解析组件 (Requirement Analyzer)

**职责**：解析和理解业务需求，提取测试要点和验收标准

**输入示例**：
```
需求标题：用户微信登录功能
需求描述：
- 用户可以通过微信扫码登录系统
- 首次登录需要绑定手机号
- 已绑定用户直接登录成功
- 登录后跳转到个人中心页面
- 支持记住登录状态7天

验收标准：
- 微信扫码成功率 > 95%
- 登录响应时间 < 3秒
- 支持iOS和Android平台
```

**输出结构**：
```json
{
  "requirement": {
    "id": "REQ_001",
    "title": "用户微信登录功能",
    "type": "feature",
    "priority": "high",
    "business_value": "提升用户登录体验，降低注册门槛",
    "stakeholders": ["产品经理", "开发团队", "测试团队"],
    "acceptance_criteria": [
      {
        "criterion": "微信扫码成功率 > 95%",
        "type": "performance",
        "measurable": true,
        "target_value": 95,
        "unit": "percent"
      },
      {
        "criterion": "登录响应时间 < 3秒", 
        "type": "performance",
        "measurable": true,
        "target_value": 3,
        "unit": "seconds"
      },
      {
        "criterion": "支持iOS和Android平台",
        "type": "compatibility",
        "measurable": false,
        "platforms": ["iOS", "Android"]
      }
    ],
    "test_scenarios": [
      {
        "scenario": "first_time_wechat_login",
        "description": "首次微信登录绑定手机号",
        "priority": "high",
        "test_type": ["functional", "ui"],
        "platforms": ["web", "ios", "android"]
      },
      {
        "scenario": "existing_user_wechat_login",
        "description": "已绑定用户微信登录",
        "priority": "high", 
        "test_type": ["functional", "ui", "performance"],
        "platforms": ["web", "ios", "android"]
      },
      {
        "scenario": "login_state_persistence",
        "description": "登录状态保持7天",
        "priority": "medium",
        "test_type": ["functional"],
        "platforms": ["web", "ios", "android"]
      }
    ]
  }
}
```

### 2. 知识图谱组件 (Knowledge Graph)

**职责**：构建和维护需求、功能、测试用例之间的关系图谱

**图谱结构**：
```json
{
  "entities": [
    {
      "id": "user_login",
      "type": "feature",
      "name": "用户登录",
      "properties": {
        "complexity": "medium",
        "risk_level": "high",
        "business_impact": "critical"
      }
    },
    {
      "id": "wechat_oauth",
      "type": "component", 
      "name": "微信OAuth",
      "properties": {
        "external_dependency": true,
        "reliability": 0.98
      }
    },
    {
      "id": "phone_binding",
      "type": "process",
      "name": "手机号绑定",
      "properties": {
        "validation_required": true,
        "sms_dependency": true
      }
    }
  ],
  "relationships": [
    {
      "from": "user_login",
      "to": "wechat_oauth", 
      "type": "depends_on",
      "properties": {
        "criticality": "high"
      }
    },
    {
      "from": "wechat_oauth",
      "to": "phone_binding",
      "type": "triggers",
      "properties": {
        "condition": "first_time_user"
      }
    }
  ]
}
```

### 3. 策略生成组件 (Strategy Generator)

**职责**：基于需求分析和知识图谱，生成全面的测试策略

**策略生成算法**：
1. **风险评估**：分析需求的技术风险和业务风险
2. **覆盖分析**：确定需要覆盖的测试维度
3. **优先级排序**：基于风险和业务价值排序
4. **资源估算**：评估测试执行所需的时间和资源

**输出示例**：
```json
{
  "test_strategy": {
    "requirement_id": "REQ_001",
    "strategy_version": "1.0",
    "risk_assessment": {
      "technical_risks": [
        {
          "risk": "微信API不稳定",
          "probability": "medium",
          "impact": "high",
          "mitigation": "增加重试机制和降级方案测试"
        },
        {
          "risk": "跨平台兼容性问题",
          "probability": "low",
          "impact": "medium", 
          "mitigation": "多平台并行测试"
        }
      ],
      "business_risks": [
        {
          "risk": "用户登录失败率过高",
          "probability": "medium",
          "impact": "critical",
          "mitigation": "性能和稳定性重点测试"
        }
      ]
    },
    "test_coverage": {
      "functional_coverage": {
        "scenarios": 8,
        "priority_high": 5,
        "priority_medium": 2,
        "priority_low": 1
      },
      "platform_coverage": {
        "web": true,
        "ios": true,
        "android": true,
        "desktop": false
      },
      "test_types": [
        "functional",
        "ui",
        "performance", 
        "security",
        "compatibility"
      ]
    },
    "execution_plan": {
      "phases": [
        {
          "phase": "smoke_test",
          "duration": "2 hours",
          "test_count": 3,
          "platforms": ["web"]
        },
        {
          "phase": "functional_test",
          "duration": "1 day",
          "test_count": 15,
          "platforms": ["web", "ios", "android"]
        },
        {
          "phase": "performance_test",
          "duration": "4 hours",
          "test_count": 5,
          "platforms": ["web", "ios", "android"]
        }
      ],
      "total_duration": "2 days",
      "total_test_count": 23
    }
  }
}
```

### 4. 测试规划组件 (Test Planner)

**职责**：将测试策略转化为具体的测试计划和执行任务

**规划输出**：
```json
{
  "test_plan": {
    "plan_id": "PLAN_REQ_001_v1",
    "requirement_id": "REQ_001",
    "created_at": "2024-01-15T10:00:00Z",
    "test_suites": [
      {
        "suite_id": "SUITE_WECHAT_LOGIN_FUNCTIONAL",
        "name": "微信登录功能测试套件",
        "type": "functional",
        "priority": "high",
        "estimated_duration": "4 hours",
        "test_cases": [
          {
            "case_id": "TC_WECHAT_LOGIN_001",
            "name": "首次微信登录绑定手机号",
            "type": "ui_automation",
            "platform": "web",
            "execution_method": "ai_generated",
            "dependencies": [],
            "estimated_duration": "10 minutes"
          },
          {
            "case_id": "TC_WECHAT_LOGIN_002", 
            "name": "已绑定用户微信登录",
            "type": "ui_automation",
            "platform": "web",
            "execution_method": "ai_generated",
            "dependencies": ["TC_WECHAT_LOGIN_001"],
            "estimated_duration": "5 minutes"
          }
        ]
      },
      {
        "suite_id": "SUITE_WECHAT_LOGIN_PERFORMANCE",
        "name": "微信登录性能测试套件",
        "type": "performance",
        "priority": "medium",
        "estimated_duration": "2 hours",
        "test_cases": [
          {
            "case_id": "TC_WECHAT_PERF_001",
            "name": "登录响应时间测试",
            "type": "api_automation",
            "platform": "api",
            "execution_method": "load_test",
            "performance_criteria": {
              "response_time": "< 3s",
              "concurrent_users": 100
            }
          }
        ]
      }
    ]
  }
}
```

### 5. 执行编排组件 (Execution Orchestrator)

**职责**：协调API编排和UI测试模块，执行完整的测试计划

**编排流程**：
```
1. 解析测试计划
2. 识别测试类型和依赖关系
3. 调用相应的执行模块
4. 监控执行进度
5. 处理异常和重试
6. 收集执行结果
7. 生成综合报告
```

**执行调度**：
```json
{
  "execution_schedule": {
    "plan_id": "PLAN_REQ_001_v1",
    "execution_id": "EXEC_20240115_001",
    "start_time": "2024-01-15T14:00:00Z",
    "tasks": [
      {
        "task_id": "TASK_001",
        "type": "ui_automation",
        "module": "phase2_ui_automation",
        "test_cases": ["TC_WECHAT_LOGIN_001", "TC_WECHAT_LOGIN_002"],
        "platform": "web",
        "priority": 1,
        "estimated_duration": "15 minutes"
      },
      {
        "task_id": "TASK_002",
        "type": "api_automation", 
        "module": "phase1_api_orchestration",
        "test_cases": ["TC_WECHAT_PERF_001"],
        "platform": "api",
        "priority": 2,
        "estimated_duration": "30 minutes",
        "dependencies": ["TASK_001"]
      }
    ]
  }
}
```

## 需求管理界面设计

### 需求列表页面

```
┌─────────────────────────────────────────────────────────────────┐
│ 需求管理                                    [+ 新增需求] [导入]  │
├─────────────────────────────────────────────────────────────────┤
│ 搜索: [_______________] 状态:[全部▼] 优先级:[全部▼] 负责人:[全部▼]│
├─────────────────────────────────────────────────────────────────┤
│ □ 需求ID    │ 需求标题        │ 状态    │ 优先级 │ 测试覆盖率 │ 操作 │
├─────────────────────────────────────────────────────────────────┤
│ □ REQ_001   │ 用户微信登录功能│ 开发中  │ 高     │ 85%       │ 详情 │
│ □ REQ_002   │ 订单支付流程    │ 测试中  │ 高     │ 92%       │ 详情 │
│ □ REQ_003   │ 商品搜索优化    │ 已完成  │ 中     │ 78%       │ 详情 │
└─────────────────────────────────────────────────────────────────┘
```

### 跨系统/模块追踪与审计（与Phase1同步，新增）

为支持跨域追踪、筛选与审计，需求管理需与Phase1/Phase2保持一致的数据模型与接口约定。

1) 字段对齐
- 需求（Requirement）
  - `metadata.tags?: string[]`
  - `metadata.owner_team?: string`
  - `metadata.data_sensitivity?: 'internal'|'pii'|'secret'`
  - `metadata.risk_level?: 'low'|'medium'|'high'`
- 需求派生的测试计划（TestPlan/OrchestrationPlan）
  - `metadata.involved_system_ids: number[]`
  - `metadata.involved_module_ids: number[]`
  - `preferences.prefer_system_id?: number`（仅推荐上下文，不代表归属）
  - `preferences.prefer_module_id?: number`（仅推荐上下文，不代表归属）

2) 聚合与回写时机
- 从计划中的步骤聚合 `involved_system_ids/modules` 并写入计划 `metadata`；需求记录中仅保存引用（简化：可选缓存聚合结果）。
- 当执行完成时，将按执行实际涉及的系统/模块与关键指标（成功率、P95、错误数）更新到“需求覆盖报告”。

3) 筛选与统计
- 列表支持：标签、状态、负责人/团队、时间范围、涉及系统（多选）、涉及模块（多选）。
- 说明：系统/模块用于筛选与统计，不表示归属关系；需求的归属仍以产品域/团队为准。

4) 权限与脱敏
- 参照Phase1的权限模型：基于团队/角色控制可见范围，`data_sensitivity` 控制字段脱敏与导出限制。

5) 与执行编排联动
- 需求 → 计划映射：在策略生成/测试规划阶段，透传 `preferences.prefer_system_id/module_id` 作为推荐上下文。
- 计划 → 执行：Run视图事件协议与Phase1一致，支持从需求详情页“查看最近执行”。

### 需求详情页面

```
┌─────────────────────────────────────────────────────────────────┐
│ REQ_001: 用户微信登录功能                        [编辑] [测试]  │
├─────────────────────────────────────────────────────────────────┤
│ 基本信息                                                        │
│ 状态: 开发中    优先级: 高    负责人: 张三    预计完成: 2024-01-20│
│                                                                 │
│ 需求描述                                                        │
│ 用户可以通过微信扫码登录系统，首次登录需要绑定手机号...          │
│                                                                 │
│ AI生成的测试策略                                    [重新生成]  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🤖 基于需求分析，AI建议以下测试策略：                        │ │
│ │                                                             │ │
│ │ 📊 风险评估：                                               │ │
│ │ • 微信API依赖 - 中等风险，建议增加降级测试                  │ │
│ │ • 跨平台兼容性 - 低风险，建议多平台并行测试                 │ │
│ │                                                             │ │
│ │ 🎯 测试重点：                                               │ │
│ │ • 功能测试：首次登录、已绑定用户登录、状态保持               │ │
│ │ • 性能测试：登录响应时间、并发登录                          │ │
│ │ • 兼容性测试：iOS、Android、Web三端                        │ │
│ │                                                             │ │
│ │ ⏱️ 预计执行时间：2天，23个测试用例                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 测试用例 (AI自动生成)                           [查看全部]      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🧪 TC_001: 首次微信登录绑定手机号                           │ │
│ │    平台: Web, iOS, Android  │  状态: 待执行  │  预计: 10分钟  │ │
│ │                                                             │ │
│ │ 🧪 TC_002: 已绑定用户微信登录                               │ │
│ │    平台: Web, iOS, Android  │  状态: 待执行  │  预计: 5分钟   │ │
│ │                                                             │ │
│ │ 🧪 TC_003: 登录状态保持7天                                  │ │
│ │    平台: Web, iOS, Android  │  状态: 待执行  │  预计: 15分钟  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ 执行历史                                                        │
│ 2024-01-15 14:30  执行测试套件  成功率: 95%  耗时: 1.5小时      │
│ 2024-01-14 16:20  执行测试套件  成功率: 88%  耗时: 2.1小时      │
└─────────────────────────────────────────────────────────────────┘
```

## MCP工具详细设计

### 需求解析工具

**工具名称**：`requirement_parse`
**描述**：解析需求文档，提取测试要点

**Schema定义**：
```json
{
  "name": "requirement_parse",
  "description": "Parse requirement document and extract test points",
  "inputSchema": {
    "type": "object",
    "properties": {
      "requirement_text": {
        "type": "string",
        "description": "Requirement description text"
      },
      "acceptance_criteria": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of acceptance criteria"
      },
      "context": {
        "type": "object",
        "properties": {
          "project_type": {"type": "string"},
          "technology_stack": {"type": "array"},
          "existing_features": {"type": "array"}
        }
      }
    },
    "required": ["requirement_text"]
  }
}
```

### 策略生成工具

**工具名称**：`generate_test_strategy`
**描述**：基于需求分析生成测试策略

**Schema定义**：
```json
{
  "name": "generate_test_strategy",
  "description": "Generate comprehensive test strategy based on requirement analysis",
  "inputSchema": {
    "type": "object",
    "properties": {
      "requirement_analysis": {
        "type": "object",
        "description": "Parsed requirement analysis result"
      },
      "constraints": {
        "type": "object",
        "properties": {
          "time_budget": {"type": "string"},
          "resource_limit": {"type": "number"},
          "platform_priority": {"type": "array"}
        }
      },
      "risk_tolerance": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Risk tolerance level"
      }
    },
    "required": ["requirement_analysis"]
  }
}
```

### 执行编排工具

**工具名称**：`orchestrate_execution`
**描述**：编排和执行测试计划

**Schema定义**：
```json
{
  "name": "orchestrate_execution", 
  "description": "Orchestrate and execute test plan across multiple modules",
  "inputSchema": {
    "type": "object",
    "properties": {
      "test_plan": {
        "type": "object",
        "description": "Detailed test plan to execute"
      },
      "execution_mode": {
        "type": "string",
        "enum": ["sequential", "parallel", "hybrid"],
        "description": "Execution mode"
      },
      "resource_allocation": {
        "type": "object",
        "properties": {
          "max_concurrent_tasks": {"type": "number"},
          "timeout_per_task": {"type": "number"}
        }
      }
    },
    "required": ["test_plan"]
  }
}
```

## 数据流设计

### 完整执行流程

```
需求输入 → 需求解析 → 知识图谱查询 → 策略生成 → 测试规划 → 执行编排 → 结果分析 → 报告生成
    ↓           ↓           ↓           ↓           ↓           ↓           ↓           ↓
  文本描述   结构化需求   关联分析    测试策略    执行计划    任务调度    执行结果    综合报告
    ↓           ↓           ↓           ↓           ↓           ↓           ↓           ↓
  验收标准   测试场景    风险评估    覆盖分析    资源分配    进度监控    问题诊断    改进建议
```

### 模块间协作

```
需求管理模块 (第三阶段)
    ↓ 调用API编排任务
API编排模块 (第一阶段)
    ↓ 返回API测试结果
需求管理模块 (第三阶段)
    ↓ 调用UI测试任务  
UI测试模块 (第二阶段)
    ↓ 返回UI测试结果
需求管理模块 (第三阶段)
    ↓ 综合分析结果
生成最终报告
```

## 实现计划

### 第一周：基础架构
- [ ] 需求数据模型设计
- [ ] 知识图谱基础框架
- [ ] 基础MCP工具实现

### 第二周：核心AI组件
- [ ] 需求解析引擎
- [ ] 策略生成算法
- [ ] 测试规划器

### 第三周：集成与编排
- [ ] 执行编排引擎
- [ ] 模块间调用接口
- [ ] 结果分析器

### 第四周：界面与优化
- [ ] 需求管理界面
- [ ] 报告生成器
- [ ] 性能优化

## 成功验收标准

### 功能验收
- [ ] 能理解复杂的业务需求并生成测试策略
- [ ] 自动调用API编排和UI测试模块
- [ ] 生成全面的测试报告和改进建议
- [ ] 支持需求变更的影响分析

### 业务验收
- [ ] 需求到测试的转化时间 < 1小时
- [ ] 测试覆盖率提升 > 200%
- [ ] 缺陷发现率提升 > 150%
- [ ] 测试维护成本降低 > 60%

### 用户体验验收
- [ ] 界面操作直观易用
- [ ] AI生成内容准确率 > 85%
- [ ] 执行进度实时可见
- [ ] 报告内容清晰有价值

---

*本文档为需求管理模块的详细技术设计，实现过程中如有调整请及时更新文档。*