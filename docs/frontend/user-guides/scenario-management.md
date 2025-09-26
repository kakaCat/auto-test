# 用例场景管理指南

## 概述

用例场景是基于API调用流程或页面调用流程创建的具体测试案例，包含完整的测试数据、执行步骤、预期结果和验证规则。通过用例场景管理，可以将抽象的调用流程转化为可执行的测试案例，实现自动化测试的标准化和规模化。

## 用例场景架构

### 场景组成结构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              用例场景结构                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 基础信息                                                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ • 场景名称  • 场景描述  • 优先级  • 标签  • 创建者  • 更新时间          │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 流程引用                                                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ • 调用流程类型 (API/页面)  • 流程名称  • 流程版本  • 参数映射            │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 测试数据                                                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ • 输入数据  • 环境变量  • 全局配置  • 数据源  • 数据生成规则            │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 验证规则                                                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ • 断言配置  • 预期结果  • 性能指标  • 业务规则  • 数据完整性检查        │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 执行配置                                                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ • 执行环境  • 执行策略  • 重试机制  • 超时设置  • 并发控制              │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 创建用例场景

### 步骤1: 基础信息配置

#### 1.1 场景基本信息
```json
{
  "scenario_info": {
    "name": "用户登录成功场景",
    "description": "验证用户使用正确的用户名和密码能够成功登录系统",
    "priority": "high",
    "tags": ["登录", "用户认证", "正向测试"],
    "category": "功能测试",
    "estimated_duration": "30秒",
    "author": "张三",
    "reviewer": "李四"
  }
}
```

#### 1.2 场景分类管理
```
场景分类体系:
├─ 功能测试
│   ├─ 正向测试 (Happy Path)
│   ├─ 负向测试 (Negative Testing)
│   └─ 边界测试 (Boundary Testing)
├─ 性能测试
│   ├─ 负载测试
│   ├─ 压力测试
│   └─ 稳定性测试
├─ 安全测试
│   ├─ 认证测试
│   ├─ 授权测试
│   └─ 数据安全测试
└─ 兼容性测试
    ├─ 浏览器兼容性
    ├─ 设备兼容性
    └─ 版本兼容性
```

### 步骤2: 选择调用流程

#### 2.1 流程类型选择
```
流程类型选择:
├─ API调用流程
│   ├─ 适用场景: 接口测试、数据验证、业务逻辑测试
│   └─ 特点: 执行速度快、数据精确、易于自动化
└─ 页面调用流程
    ├─ 适用场景: UI测试、用户体验测试、端到端测试
    └─ 特点: 贴近用户操作、覆盖完整流程、验证界面交互
```

#### 2.2 流程引用配置
```json
{
  "flow_reference": {
    "flow_type": "api_call_flow",
    "flow_name": "用户登录API流程",
    "flow_version": "v1.2.0",
    "flow_id": "flow_001",
    "parameter_mapping": {
      "username": "${scenario_data.test_username}",
      "password": "${scenario_data.test_password}",
      "environment": "${global.test_environment}"
    }
  }
}
```

### 步骤3: 配置测试数据

#### 3.1 静态测试数据
```json
{
  "static_test_data": {
    "valid_user": {
      "username": "test_user_001",
      "password": "Test123456!",
      "email": "test001@example.com",
      "phone": "13800138000"
    },
    "invalid_user": {
      "username": "invalid_user",
      "password": "wrong_password",
      "email": "invalid@email",
      "phone": "invalid_phone"
    },
    "admin_user": {
      "username": "admin",
      "password": "Admin123456!",
      "role": "administrator"
    }
  }
}
```

#### 3.2 动态数据生成
```json
{
  "dynamic_data_rules": {
    "random_user": {
      "username": "user_${random_string(8)}",
      "password": "${random_password(12)}",
      "email": "${random_email()}",
      "phone": "${random_phone()}",
      "birth_date": "${random_date('1980-01-01', '2000-12-31')}"
    },
    "timestamp_data": {
      "created_at": "${now()}",
      "updated_at": "${now()}",
      "expired_at": "${add_days(now(), 30)}"
    }
  }
}
```

#### 3.3 数据源配置
```json
{
  "data_sources": {
    "database": {
      "type": "mysql",
      "connection": "test_db",
      "queries": {
        "get_test_users": "SELECT * FROM users WHERE status = 'active' LIMIT 10",
        "get_test_products": "SELECT * FROM products WHERE category = 'electronics'"
      }
    },
    "file": {
      "type": "csv",
      "path": "/data/test_users.csv",
      "encoding": "utf-8"
    },
    "api": {
      "type": "rest_api",
      "endpoint": "https://api.example.com/test-data",
      "headers": {
        "Authorization": "Bearer ${api_token}"
      }
    }
  }
}
```

### 步骤4: 配置验证规则

#### 4.1 响应验证
```json
{
  "response_validation": {
    "status_code": {
      "expected": 200,
      "operator": "equals"
    },
    "response_time": {
      "expected": 2000,
      "operator": "less_than",
      "unit": "milliseconds"
    },
    "response_body": {
      "success": {
        "expected": true,
        "path": "$.success"
      },
      "user_id": {
        "expected": "not_null",
        "path": "$.data.user_id"
      },
      "token": {
        "expected": "^[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$",
        "path": "$.data.access_token",
        "operator": "regex_match"
      }
    }
  }
}
```

#### 4.2 业务规则验证
```json
{
  "business_validation": {
    "user_permissions": {
      "description": "验证用户权限正确分配",
      "rules": [
        {
          "condition": "user.role == 'admin'",
          "expected": "permissions.includes('user_management')"
        },
        {
          "condition": "user.role == 'user'",
          "expected": "!permissions.includes('admin_panel')"
        }
      ]
    },
    "data_consistency": {
      "description": "验证数据一致性",
      "rules": [
        {
          "field": "user.email",
          "validation": "email_format"
        },
        {
          "field": "user.phone",
          "validation": "phone_format"
        }
      ]
    }
  }
}
```

#### 4.3 性能指标验证
```json
{
  "performance_validation": {
    "response_time": {
      "p50": 500,
      "p95": 1000,
      "p99": 2000,
      "unit": "milliseconds"
    },
    "throughput": {
      "min_rps": 100,
      "target_rps": 500,
      "max_rps": 1000
    },
    "resource_usage": {
      "cpu_threshold": 80,
      "memory_threshold": 85,
      "disk_io_threshold": 70
    }
  }
}
```

### 步骤5: 执行配置

#### 5.1 环境配置
```json
{
  "execution_environment": {
    "target_environment": "test",
    "browser_config": {
      "browser": "chrome",
      "version": "latest",
      "headless": false,
      "window_size": "1920x1080"
    },
    "network_config": {
      "bandwidth": "broadband",
      "latency": "low",
      "packet_loss": 0
    },
    "device_config": {
      "device_type": "desktop",
      "os": "windows",
      "screen_resolution": "1920x1080"
    }
  }
}
```

#### 5.2 执行策略
```json
{
  "execution_strategy": {
    "retry_config": {
      "max_retries": 3,
      "retry_interval": 2000,
      "retry_conditions": ["network_error", "timeout", "server_error"]
    },
    "timeout_config": {
      "scenario_timeout": 300000,
      "step_timeout": 30000,
      "element_timeout": 10000
    },
    "parallel_config": {
      "enable_parallel": true,
      "max_parallel": 5,
      "parallel_strategy": "by_scenario"
    }
  }
}
```

## 场景类型详解

### API测试场景

#### 正向测试场景
```json
{
  "scenario_name": "API正向测试-用户创建",
  "flow_type": "api_call_flow",
  "test_data": {
    "user_info": {
      "username": "new_user_001",
      "email": "newuser@example.com",
      "password": "SecurePass123!",
      "role": "user"
    }
  },
  "validations": [
    {
      "type": "status_code",
      "expected": 201
    },
    {
      "type": "response_schema",
      "schema": "user_creation_response_schema"
    },
    {
      "type": "database_check",
      "query": "SELECT * FROM users WHERE username = '${test_data.username}'",
      "expected": "record_exists"
    }
  ]
}
```

#### 负向测试场景
```json
{
  "scenario_name": "API负向测试-无效数据",
  "flow_type": "api_call_flow",
  "test_cases": [
    {
      "case_name": "用户名为空",
      "test_data": {
        "username": "",
        "email": "test@example.com",
        "password": "Test123!"
      },
      "expected_result": {
        "status_code": 400,
        "error_message": "用户名不能为空"
      }
    },
    {
      "case_name": "邮箱格式错误",
      "test_data": {
        "username": "testuser",
        "email": "invalid-email",
        "password": "Test123!"
      },
      "expected_result": {
        "status_code": 400,
        "error_message": "邮箱格式不正确"
      }
    }
  ]
}
```

### 页面测试场景

#### UI功能测试场景
```json
{
  "scenario_name": "页面功能测试-用户注册",
  "flow_type": "page_call_flow",
  "test_steps": [
    {
      "step": "打开注册页面",
      "validation": "页面标题包含'用户注册'"
    },
    {
      "step": "填写注册信息",
      "test_data": {
        "username": "ui_test_user",
        "email": "uitest@example.com",
        "password": "UITest123!",
        "confirm_password": "UITest123!"
      }
    },
    {
      "step": "提交注册表单",
      "validation": "显示注册成功消息"
    },
    {
      "step": "验证跳转",
      "validation": "跳转到登录页面"
    }
  ]
}
```

#### 用户体验测试场景
```json
{
  "scenario_name": "用户体验测试-购物流程",
  "flow_type": "page_call_flow",
  "user_journey": [
    {
      "stage": "发现商品",
      "actions": ["搜索商品", "浏览商品列表", "查看商品详情"],
      "metrics": ["页面加载时间", "搜索响应时间", "图片加载时间"]
    },
    {
      "stage": "购买决策",
      "actions": ["比较商品", "查看评价", "添加到购物车"],
      "metrics": ["操作响应时间", "页面交互流畅度"]
    },
    {
      "stage": "完成购买",
      "actions": ["结算", "填写地址", "选择支付方式", "确认订单"],
      "metrics": ["表单填写体验", "支付流程时间"]
    }
  ]
}
```

## 数据驱动测试

### 参数化测试场景

#### 多数据集测试
```json
{
  "scenario_name": "参数化登录测试",
  "flow_type": "api_call_flow",
  "data_driven": true,
  "test_data_sets": [
    {
      "set_name": "有效用户数据",
      "data": [
        {"username": "user1", "password": "pass1", "expected": "success"},
        {"username": "user2", "password": "pass2", "expected": "success"},
        {"username": "admin", "password": "admin123", "expected": "success"}
      ]
    },
    {
      "set_name": "无效用户数据",
      "data": [
        {"username": "invalid", "password": "wrong", "expected": "failure"},
        {"username": "", "password": "pass", "expected": "failure"},
        {"username": "user", "password": "", "expected": "failure"}
      ]
    }
  ]
}
```

#### 边界值测试
```json
{
  "scenario_name": "边界值测试-用户名长度",
  "flow_type": "api_call_flow",
  "boundary_test": {
    "field": "username",
    "test_values": [
      {"value": "", "description": "空值", "expected": "failure"},
      {"value": "a", "description": "最小长度-1", "expected": "failure"},
      {"value": "ab", "description": "最小长度", "expected": "success"},
      {"value": "a".repeat(50), "description": "最大长度", "expected": "success"},
      {"value": "a".repeat(51), "description": "最大长度+1", "expected": "failure"}
    ]
  }
}
```

## 场景执行管理

### 执行计划

#### 单场景执行
```json
{
  "execution_plan": {
    "plan_name": "单场景执行计划",
    "execution_type": "single_scenario",
    "scenario_id": "scenario_001",
    "schedule": {
      "type": "immediate",
      "execution_time": "now"
    },
    "notifications": {
      "on_success": ["email:admin@example.com"],
      "on_failure": ["email:admin@example.com", "slack:#testing"]
    }
  }
}
```

#### 批量执行
```json
{
  "execution_plan": {
    "plan_name": "回归测试执行计划",
    "execution_type": "batch",
    "scenarios": [
      {"id": "scenario_001", "priority": 1},
      {"id": "scenario_002", "priority": 1},
      {"id": "scenario_003", "priority": 2}
    ],
    "execution_strategy": {
      "parallel_execution": true,
      "max_parallel": 3,
      "stop_on_failure": false
    },
    "schedule": {
      "type": "cron",
      "expression": "0 2 * * *",
      "timezone": "Asia/Shanghai"
    }
  }
}
```

### 执行监控

#### 实时监控
```json
{
  "monitoring_config": {
    "real_time_metrics": {
      "execution_progress": true,
      "success_rate": true,
      "failure_rate": true,
      "average_execution_time": true,
      "resource_usage": true
    },
    "alerts": {
      "failure_threshold": 10,
      "timeout_threshold": 300,
      "resource_threshold": 90
    },
    "dashboard": {
      "refresh_interval": 5,
      "auto_refresh": true,
      "display_charts": true
    }
  }
}
```

## 结果分析和报告

### 执行结果

#### 详细执行报告
```json
{
  "execution_report": {
    "scenario_id": "scenario_001",
    "scenario_name": "用户登录成功场景",
    "execution_time": "2024-01-15 14:30:00",
    "duration": "25.6秒",
    "status": "passed",
    "steps": [
      {
        "step_name": "发送登录请求",
        "status": "passed",
        "duration": "1.2秒",
        "request": {
          "url": "https://api.example.com/login",
          "method": "POST",
          "headers": {"Content-Type": "application/json"},
          "body": {"username": "test_user", "password": "***"}
        },
        "response": {
          "status_code": 200,
          "headers": {"Content-Type": "application/json"},
          "body": {"success": true, "token": "***", "user_id": 12345}
        }
      }
    ],
    "validations": [
      {
        "name": "状态码验证",
        "status": "passed",
        "expected": 200,
        "actual": 200
      },
      {
        "name": "响应时间验证",
        "status": "passed",
        "expected": "< 2000ms",
        "actual": "1200ms"
      }
    ],
    "screenshots": ["login_page.png", "success_page.png"],
    "logs": ["execution.log", "error.log"]
  }
}
```

### 趋势分析

#### 执行趋势报告
```json
{
  "trend_analysis": {
    "time_period": "last_30_days",
    "scenario_id": "scenario_001",
    "metrics": {
      "success_rate": {
        "current": 95.2,
        "previous": 93.8,
        "trend": "improving"
      },
      "average_execution_time": {
        "current": "24.5秒",
        "previous": "26.1秒",
        "trend": "improving"
      },
      "failure_reasons": [
        {"reason": "网络超时", "count": 3, "percentage": 60},
        {"reason": "数据验证失败", "count": 2, "percentage": 40}
      ]
    }
  }
}
```

## 场景维护

### 版本管理

#### 场景版本控制
```json
{
  "version_control": {
    "scenario_id": "scenario_001",
    "current_version": "v1.3.0",
    "version_history": [
      {
        "version": "v1.3.0",
        "date": "2024-01-15",
        "changes": ["更新验证规则", "优化测试数据"],
        "author": "张三"
      },
      {
        "version": "v1.2.0",
        "date": "2024-01-10",
        "changes": ["添加性能验证", "修复数据问题"],
        "author": "李四"
      }
    ]
  }
}
```

### 依赖管理

#### 场景依赖关系
```json
{
  "dependencies": {
    "scenario_id": "scenario_001",
    "depends_on": [
      {
        "type": "flow",
        "id": "flow_001",
        "version": "v1.2.0"
      },
      {
        "type": "test_data",
        "id": "user_data_set_001"
      },
      {
        "type": "environment",
        "id": "test_env_001"
      }
    ],
    "used_by": [
      {
        "type": "requirement",
        "id": "req_001"
      },
      {
        "type": "test_suite",
        "id": "suite_001"
      }
    ]
  }
}
```

## 最佳实践

### 1. 场景设计原则

#### 独立性原则
- 每个场景应该能够独立执行
- 不依赖其他场景的执行结果
- 具有完整的测试数据和环境配置

#### 可重复性原则
- 场景执行结果应该是可重复的
- 使用确定性的测试数据
- 清理测试环境，避免数据污染

#### 可维护性原则
- 使用清晰的命名规范
- 添加详细的描述和注释
- 模块化设计，便于复用

### 2. 数据管理

#### 测试数据隔离
- 为不同环境准备独立的测试数据
- 使用数据工厂模式生成测试数据
- 定期清理和更新测试数据

#### 敏感数据保护
- 使用变量引用而不是硬编码敏感信息
- 在日志和报告中屏蔽敏感数据
- 使用加密存储敏感配置

### 3. 执行优化

#### 并行执行
- 识别可以并行执行的场景
- 合理设置并行度，避免资源竞争
- 处理并行执行中的数据冲突

#### 失败快速定位
- 添加详细的日志和截图
- 使用断言提供清晰的错误信息
- 建立失败场景的快速重现机制

## 常见问题

### Q1: 如何处理场景间的数据依赖？
**A**: 
1. 尽量设计独立的场景，避免依赖
2. 使用共享的测试数据源
3. 通过数据库或API准备依赖数据
4. 使用场景链的方式处理必要的依赖

### Q2: 如何提高场景执行的稳定性？
**A**: 
1. 添加适当的等待和重试机制
2. 使用稳定的测试数据
3. 定期维护和更新场景
4. 监控执行环境的稳定性

### Q3: 如何管理大量的测试场景？
**A**: 
1. 使用标签和分类进行组织
2. 建立场景的优先级体系
3. 定期清理过时的场景
4. 使用自动化工具进行批量管理

### Q4: 如何评估场景的测试覆盖率？
**A**: 
1. 建立需求与场景的追溯关系
2. 使用代码覆盖率工具
3. 分析业务流程的覆盖情况
4. 定期评估和补充测试场景

## 总结

用例场景管理是自动化测试体系的核心环节，通过系统化的场景设计、数据管理、执行监控和结果分析，可以构建高效、稳定、可维护的测试体系。掌握本指南中的管理方法和最佳实践，您将能够：

- 设计高质量的测试场景
- 有效管理测试数据和执行配置
- 优化场景执行的稳定性和效率
- 建立完善的测试覆盖体系

通过合理的场景管理，可以大大提高自动化测试的质量和效率，为产品质量保障提供有力支撑。