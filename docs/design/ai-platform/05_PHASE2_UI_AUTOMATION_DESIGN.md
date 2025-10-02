# 第二阶段：页面自动化测试模块详细设计

## 模块概述

页面自动化测试模块是平台的核心价值模块，目标是让AI Agent能够像人类测试工程师一样，理解应用功能并自动生成、执行多端UI测试用例。

## 核心架构

### 组件架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                  UI测试AI Agent                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   功能理解      │  │   用例生成      │  │   执行监控      │   │
│  │ Feature Parser  │  │ Case Generator  │  │ Exec Monitor    │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   页面理解      │  │   智能定位      │  │   自适应修复    │   │
│  │ Page Analyzer   │  │ Smart Locator   │  │ Self Healing    │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────┴───────────────────────────────────────┐
│                    UI操作MCP工具集                              │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │  Web工具集  │ │ iOS工具集   │ │Android工具集│ │ 通用工具集  │ │
│ │             │ │             │ │             │ │             │ │
│ │ • web_click │ │ • ios_tap   │ │ • and_tap   │ │ • screenshot│ │
│ │ • web_input │ │ • ios_swipe │ │ • and_swipe │ │ • wait_for  │ │
│ │ • web_verify│ │ • ios_verify│ │ • and_verify│ │ • compare   │ │
│ │ • web_nav   │ │ • ios_scroll│ │ • and_scroll│ │ • ocr_text  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────────┐
│                      目标应用                                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Web应用   │ │   iOS应用   │ │ Android应用 │ │   桌面应用  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. 功能理解组件 (Feature Parser)

**职责**：理解用户描述的功能需求，提取测试要点和场景

**输入示例**：
```
"测试用户登录功能，包括正常登录、错误密码、账号不存在等场景"
```

**输出结构**：
```json
{
  "feature": "user_login",
  "description": "用户登录功能测试",
  "test_scenarios": [
    {
      "scenario": "successful_login",
      "description": "正常登录流程",
      "priority": "high",
      "test_data": {
        "username": "valid_user@example.com",
        "password": "correct_password"
      },
      "expected_outcome": "login_success"
    },
    {
      "scenario": "invalid_password", 
      "description": "错误密码登录",
      "priority": "high",
      "test_data": {
        "username": "valid_user@example.com", 
        "password": "wrong_password"
      },
      "expected_outcome": "login_failed_invalid_password"
    },
    {
      "scenario": "nonexistent_user",
      "description": "不存在的用户登录",
      "priority": "medium",
      "test_data": {
        "username": "nonexistent@example.com",
        "password": "any_password"
      },
      "expected_outcome": "login_failed_user_not_found"
    }
  ]
}
```

### 2. 页面理解组件 (Page Analyzer)

**职责**：分析页面结构，识别关键元素和交互模式

**分析维度**：
- **元素识别**：按钮、输入框、链接、文本等
- **语义理解**：元素的业务含义和作用
- **交互模式**：表单提交、导航跳转、弹窗处理等
- **状态变化**：页面加载、数据更新、错误提示等

**输出示例**：
```json
{
  "page_url": "https://app.example.com/login",
  "page_title": "用户登录",
  "elements": [
    {
      "id": "username_input",
      "type": "input",
      "semantic_role": "username_field",
      "locators": {
        "id": "username",
        "name": "username", 
        "xpath": "//input[@placeholder='用户名或邮箱']",
        "css": "input[type='email']"
      },
      "properties": {
        "required": true,
        "placeholder": "用户名或邮箱",
        "validation": "email_format"
      }
    },
    {
      "id": "password_input",
      "type": "input",
      "semantic_role": "password_field",
      "locators": {
        "id": "password",
        "name": "password",
        "xpath": "//input[@type='password']",
        "css": "input[type='password']"
      },
      "properties": {
        "required": true,
        "placeholder": "密码",
        "validation": "min_length_6"
      }
    },
    {
      "id": "login_button",
      "type": "button", 
      "semantic_role": "submit_button",
      "locators": {
        "id": "login-btn",
        "xpath": "//button[contains(text(),'登录')]",
        "css": "button.login-button"
      },
      "properties": {
        "text": "登录",
        "enabled": true
      }
    }
  ],
  "interactions": [
    {
      "type": "form_submission",
      "trigger": "login_button_click",
      "expected_outcomes": [
        "redirect_to_dashboard",
        "show_error_message"
      ]
    }
  ]
}
```

### 3. 用例生成组件 (Case Generator)

**职责**：基于功能理解和页面分析，自动生成详细的测试用例

**生成策略**：
- **正向用例**：正常业务流程
- **异常用例**：错误输入、网络异常等
- **边界用例**：极值、空值、特殊字符等
- **兼容性用例**：不同浏览器、设备、分辨率等

**用例结构**：
```json
{
  "test_case": {
    "id": "login_test_001",
    "name": "正常用户登录测试",
    "scenario": "successful_login",
    "platform": "web",
    "priority": "high",
    "steps": [
      {
        "step": 1,
        "action": "navigate",
        "target": "login_page",
        "parameters": {
          "url": "https://app.example.com/login"
        },
        "expected": "页面加载完成"
      },
      {
        "step": 2,
        "action": "input",
        "target": "username_field",
        "parameters": {
          "value": "test@example.com"
        },
        "expected": "用户名输入成功"
      },
      {
        "step": 3,
        "action": "input", 
        "target": "password_field",
        "parameters": {
          "value": "Test123!"
        },
        "expected": "密码输入成功"
      },
      {
        "step": 4,
        "action": "click",
        "target": "login_button",
        "parameters": {},
        "expected": "登录按钮点击成功"
      },
      {
        "step": 5,
        "action": "verify",
        "target": "dashboard_page",
        "parameters": {
          "condition": "url_contains",
          "value": "/dashboard"
        },
        "expected": "成功跳转到仪表板"
      }
    ]
  }
}
```

### 4. 智能定位组件 (Smart Locator)

**职责**：提供多层次的元素定位策略，确保测试的稳定性

**定位策略层次**：
1. **语义定位**：基于元素的业务含义
2. **属性定位**：ID、Name、Class等稳定属性
3. **结构定位**：XPath、CSS选择器
4. **视觉定位**：基于图像识别和OCR
5. **AI定位**：基于机器学习的智能识别

**定位器配置**：
```json
{
  "locator_strategy": {
    "primary": {
      "type": "semantic",
      "value": "login_button",
      "confidence": 0.95
    },
    "fallback": [
      {
        "type": "id",
        "value": "login-btn",
        "confidence": 0.90
      },
      {
        "type": "xpath", 
        "value": "//button[contains(text(),'登录')]",
        "confidence": 0.85
      },
      {
        "type": "css",
        "value": "button.login-button",
        "confidence": 0.80
      },
      {
        "type": "visual",
        "value": "login_button_template.png",
        "confidence": 0.75
      }
    ]
  }
}
```

### 5. 自适应修复组件 (Self Healing)

**职责**：当测试失败时，自动分析原因并尝试修复

**修复策略**：
- **元素定位失败**：尝试备用定位器
- **页面结构变化**：重新分析页面并更新定位器
- **时序问题**：调整等待时间和重试策略
- **数据问题**：生成新的测试数据

**修复流程**：
```
1. 检测失败类型
2. 分析失败原因
3. 选择修复策略
4. 执行修复操作
5. 验证修复结果
6. 更新测试用例
```

## MCP工具详细设计

### Web操作工具集

**工具名称**：`web_click`
**描述**：点击Web页面元素

**Schema定义**：
```json
{
  "name": "web_click",
  "description": "Click on a web page element",
  "inputSchema": {
    "type": "object",
    "properties": {
      "locator": {
        "type": "object",
        "properties": {
          "strategy": {
            "type": "string",
            "enum": ["id", "name", "xpath", "css", "text", "semantic"]
          },
          "value": {
            "type": "string"
          }
        },
        "required": ["strategy", "value"]
      },
      "wait_timeout": {
        "type": "number",
        "default": 10,
        "description": "Wait timeout in seconds"
      },
      "force": {
        "type": "boolean",
        "default": false,
        "description": "Force click even if element is not visible"
      }
    },
    "required": ["locator"]
  }
}
```

**工具名称**：`web_input`
**描述**：在Web页面输入框中输入文本

**Schema定义**：
```json
{
  "name": "web_input",
  "description": "Input text into a web page element",
  "inputSchema": {
    "type": "object",
    "properties": {
      "locator": {
        "type": "object",
        "properties": {
          "strategy": {
            "type": "string",
            "enum": ["id", "name", "xpath", "css", "semantic"]
          },
          "value": {
            "type": "string"
          }
        },
        "required": ["strategy", "value"]
      },
      "text": {
        "type": "string",
        "description": "Text to input"
      },
      "clear_first": {
        "type": "boolean",
        "default": true,
        "description": "Clear existing text before input"
      }
    },
    "required": ["locator", "text"]
  }
}
```

### 移动端操作工具集

**工具名称**：`ios_tap`
**描述**：点击iOS应用元素

**Schema定义**：
```json
{
  "name": "ios_tap",
  "description": "Tap on an iOS app element",
  "inputSchema": {
    "type": "object",
    "properties": {
      "locator": {
        "type": "object",
        "properties": {
          "strategy": {
            "type": "string",
            "enum": ["accessibility_id", "xpath", "class_name", "predicate", "coordinates"]
          },
          "value": {
            "type": "string"
          }
        },
        "required": ["strategy", "value"]
      },
      "duration": {
        "type": "number",
        "default": 0.1,
        "description": "Tap duration in seconds"
      }
    },
    "required": ["locator"]
  }
}
```

### 通用验证工具集

**工具名称**：`verify_element`
**描述**：验证页面元素的存在和属性

**Schema定义**：
```json
{
  "name": "verify_element",
  "description": "Verify element existence and properties",
  "inputSchema": {
    "type": "object",
    "properties": {
      "locator": {
        "type": "object",
        "properties": {
          "strategy": {
            "type": "string"
          },
          "value": {
            "type": "string"
          }
        },
        "required": ["strategy", "value"]
      },
      "verification": {
        "type": "object",
        "properties": {
          "exists": {
            "type": "boolean",
            "description": "Verify element exists"
          },
          "visible": {
            "type": "boolean", 
            "description": "Verify element is visible"
          },
          "text": {
            "type": "string",
            "description": "Verify element text content"
          },
          "attribute": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "value": {"type": "string"}
            }
          }
        }
      }
    },
    "required": ["locator", "verification"]
  }
}
```

## 测试执行流程

### 执行架构

```
用户输入: "测试登录功能"
    ↓
功能理解: 解析为登录测试场景
    ↓
页面分析: 识别登录页面元素
    ↓
用例生成: 生成多个测试场景
    ↓
执行调度: 按优先级执行用例
    ↓
智能定位: 定位页面元素
    ↓
操作执行: 调用MCP工具
    ↓
结果验证: 检查执行结果
    ↓
自适应修复: 处理失败情况
    ↓
报告生成: 输出测试报告
```

### 并发执行策略

**浏览器池管理**：
```json
{
  "browser_pool": {
    "chrome": {
      "max_instances": 5,
      "headless": true,
      "window_size": "1920x1080"
    },
    "firefox": {
      "max_instances": 3,
      "headless": true,
      "window_size": "1920x1080"
    },
    "safari": {
      "max_instances": 2,
      "headless": false,
      "window_size": "1920x1080"
    }
  }
}
```

## 与Phase1编排对齐（新增）

为保证跨阶段一致性，页面自动化模块在以下方面与Phase1（API编排）保持一致：

### 1) 执行事件协议一致
- 事件类型：`execution_started`、`step_started`、`step_succeeded`、`step_failed`、`execution_completed`。
- 事件字段：`timestamp`、`execution_id`、`step_id?`、`message`、`metrics?`、`logs?`、`artifacts?`（截图/视频）。
- 通信通道：`WS /ws/executions/{execution_id}`（与Phase1共用协议，新增UI特有字段放在 `artifacts`）。

### 2) Run视图与可视化
- 复用Phase1的Run视图结构：DAG节点（步骤）+ 右侧详情抽屉。
- UI步骤节点扩展：`screenshot_url`、`video_url`、`element_locator`、`retry_count`。
- 失败态展示：错误截图/视频、元素定位回溯（主定位器/回退定位器）。

### 3) 跨系统/模块追踪（筛选/审计）
- 与Phase1对齐的元数据：
  - `metadata.involved_system_ids: number[]`
  - `metadata.involved_module_ids: number[]`
  - `metadata.tags?: string[]`
- 作用：仅用于列表筛选、统计与审计，不表示归属关系。
- UI用例到系统/模块的映射：
  - Web端：业务系统/模块按被测应用的域划分；
  - 移动端：以业务域（如“支付”、“登录”）映射到模块维度。

### 4) 执行入参校验
- 触发时机：启动执行前；按`required/enum/pattern/range`等规则进行快速失败校验。
- 接口复用：`POST /orchestration/execute/validate-inputs`，当 `type=ui_automation` 时校验UI特有入参（设备/浏览器/分辨率等）。


**设备池管理**：
```json
{
  "device_pool": {
    "ios_simulators": [
      {
        "device": "iPhone 14 Pro",
        "os_version": "16.0",
        "status": "available"
      }
    ],
    "android_emulators": [
      {
        "device": "Pixel 6",
        "os_version": "13.0", 
        "status": "available"
      }
    ]
  }
}
```

## 实现计划

### 第一周：基础框架
- [ ] Playwright/Appium集成
- [ ] 基础MCP工具实现
- [ ] 简单的页面分析器

### 第二周：核心AI组件
- [ ] 功能理解组件
- [ ] 用例生成引擎
- [ ] 智能定位器

### 第三周：高级特性
- [ ] 自适应修复机制
- [ ] 多平台支持
- [ ] 并发执行框架

### 第四周：集成测试
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 稳定性测试

## 成功验收标准

### 功能验收
- [ ] 能理解并执行复杂的UI测试场景
- [ ] 支持Web、iOS、Android三端测试
- [ ] 自动生成覆盖正向、异常、边界的测试用例
- [ ] 具备基本的自愈能力

### 性能验收
- [ ] 单个测试用例执行时间 < 2分钟
- [ ] 支持10个并发测试执行
- [ ] 元素定位成功率 > 95%

### 稳定性验收
- [ ] 连续运行24小时无崩溃
- [ ] 内存使用稳定，无泄漏
- [ ] 网络异常恢复能力 > 90%

---

*本文档为UI自动化测试模块的详细技术设计，实现过程中如有调整请及时更新文档。*