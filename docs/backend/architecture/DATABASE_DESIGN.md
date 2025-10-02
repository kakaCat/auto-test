# 数据库设计文档

## 📋 概述

本文档详细说明了AI自动化测试平台的数据库设计，包括表结构、关系设计、索引策略和数据流向。

## 🗄️ 数据库架构

### 技术选型
- **开发环境**: SQLite
- **生产环境**: PostgreSQL
- **ORM框架**: SQLAlchemy
- **迁移工具**: Alembic

### 设计原则
- **规范化设计**: 遵循第三范式，减少数据冗余
- **性能优化**: 合理的索引设计和查询优化
- **扩展性**: 支持未来功能扩展的表结构设计
- **一致性**: 统一的命名规范和数据类型

## 📊 核心表关系图

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    systems      │ 1───N │    modules      │ 1───N │ api_interfaces  │
│                 │       │                 │       │                 │
│ • id (PK)       │       │ • id (PK)       │       │ • id (PK)       │
│ • name          │       │ • system_id(FK) │       │ • system_id(FK) │
│ • description   │       │ • name          │       │ • module_id(FK) │
│ • category      │       │ • description   │       │ • name          │
│ • enabled       │       │ • enabled       │       │ • method        │
│ • created_at    │       │ • created_at    │       │ • path          │
│ • updated_at    │       │ • updated_at    │       │ • enabled       │
└─────────────────┘       └─────────────────┘       │ • created_at    │
         │                                           │ • updated_at    │
         │ 1                                         └─────────────────┘
         │                                                   │
         N                                                   │
┌─────────────────┐                                         │
│     pages       │                                         │
│                 │                                         │
│ • id (PK)       │                                         │
│ • system_id(FK) │                                         │
│ • name          │                                         │
│ • route_path    │                                         │
│ • page_type     │                                         │
│ • status        │                                         │
│ • config_status │                                         │
│ • created_at    │                                         │
│ • updated_at    │                                         │
└─────────────────┘                                         │
         │                                                   │
         │ 1                                                 │
         │                                                   │
         N                                                   │
┌─────────────────┐       ┌─────────────────┐               │
│ page_progress   │       │ page_step_data  │               │
│                 │       │                 │               │
│ • id (PK)       │       │ • id (PK)       │               │
│ • page_id (FK)  │       │ • page_id (FK)  │               │
│ • current_step  │       │ • step_name     │               │
│ • completed_steps│      │ • step_data     │               │
│ • step_status   │       │ • version       │               │
│ • is_completed  │       │ • is_current    │               │
│ • created_at    │       │ • created_at    │               │
│ • updated_at    │       │ • updated_at    │               │
└─────────────────┘       └─────────────────┘               │
                                                             │
┌─────────────────┐       ┌─────────────────┐               │
│page_components  │       │page_interactions│               │
│                 │       │                 │               │
│ • id (PK)       │       │ • id (PK)       │               │
│ • page_id (FK)  │       │ • page_id (FK)  │               │
│ • component_id  │       │ • interaction_id│               │
│ • component_type│       │ • interaction_type│             │
│ • component_name│       │ • source_comp_id│               │
│ • parent_id     │       │ • target_comp_id│               │
│ • position_x    │       │ • trigger_event │               │
│ • position_y    │       │ • action_type   │               │
│ • config_data   │       │ • action_config │               │
│ • style_data    │       │ • conditions    │               │
│ • created_at    │       │ • created_at    │               │
│ • updated_at    │       │ • updated_at    │               │
└─────────────────┘       └─────────────────┘               │
                                                             │
                          ┌─────────────────┐               │
                          │   page_apis     │ N─────────────┘
                          │                 │
                          │ • id (PK)       │
                          │ • page_id (FK)  │
                          │ • api_id (FK)   │
                          │ • execution_type│
                          │ • execution_order│
                          │ • trigger_action│
                          │ • api_purpose   │
                          │ • success_action│
                          │ • error_action  │
                          │ • conditions    │
                          │ • params_mapping│
                          │ • created_at    │
                          │ • updated_at    │
                          └─────────────────┘
```

## 📋 详细表设计

### 1. 系统管理相关表

#### 1.1 systems (系统表)
```sql
CREATE TABLE systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(20) NOT NULL CHECK (category IN ('backend', 'frontend')),
    base_url VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_systems_category ON systems(category);
CREATE INDEX idx_systems_enabled ON systems(enabled);
CREATE INDEX idx_systems_order ON systems(order_index);
```

#### 1.2 modules (模块表)
```sql
CREATE TABLE modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    path VARCHAR(255),
    version VARCHAR(20),
    enabled BOOLEAN DEFAULT TRUE,
    tags TEXT, -- JSON array as string
    config JSON,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_modules_system_id ON modules(system_id);
CREATE INDEX idx_modules_enabled ON modules(enabled);
CREATE UNIQUE INDEX idx_modules_system_name ON modules(system_id, name);
```

### 2. API管理相关表

#### 2.1 api_interfaces (API接口表)
```sql
CREATE TABLE api_interfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    module_id INTEGER,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    method VARCHAR(10) NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    path VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0.0',
    request_schema JSON,
    response_schema JSON,
    headers JSON,
    parameters JSON,
    tags TEXT, -- JSON array as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_api_interfaces_system_id ON api_interfaces(system_id);
CREATE INDEX idx_api_interfaces_module_id ON api_interfaces(module_id);
CREATE INDEX idx_api_interfaces_method ON api_interfaces(method);
CREATE INDEX idx_api_interfaces_enabled ON api_interfaces(enabled);
CREATE UNIQUE INDEX idx_api_interfaces_system_path ON api_interfaces(system_id, method, path);
```

### 3. 页面管理相关表

#### 3.1 pages (页面表)
```sql
CREATE TABLE pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    route_path VARCHAR(255) NOT NULL,
    page_type VARCHAR(20) DEFAULT 'page' CHECK (page_type IN ('page', 'modal', 'drawer', 'fullscreen', 'embedded', 'mobile')),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive')),
    config_status VARCHAR(20) DEFAULT 'incomplete' CHECK (config_status IN ('incomplete', 'completed')),
    icon VARCHAR(100),
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_pages_system_id ON pages(system_id);
CREATE INDEX idx_pages_status ON pages(status);
CREATE INDEX idx_pages_config_status ON pages(config_status);
CREATE UNIQUE INDEX idx_pages_system_route ON pages(system_id, route_path);
```

#### 3.2 page_progress (页面配置进度表)
```sql
CREATE TABLE page_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    current_step INTEGER DEFAULT 1,
    completed_steps TEXT, -- JSON array as string
    step_status VARCHAR(20) DEFAULT 'in_progress',
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

-- 索引
CREATE UNIQUE INDEX idx_page_progress_page_id ON page_progress(page_id);
```

#### 3.3 page_step_data (页面步骤数据表)
```sql
CREATE TABLE page_step_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    step_name VARCHAR(50) NOT NULL,
    step_data JSON,
    version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_page_step_data_page_id ON page_step_data(page_id);
CREATE UNIQUE INDEX idx_page_step_data_page_step ON page_step_data(page_id, step_name);
```

#### 3.4 page_apis (页面API关联表)
```sql
CREATE TABLE page_apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    api_id INTEGER NOT NULL,
    execution_type VARCHAR(20) DEFAULT 'manual' CHECK (execution_type IN ('manual', 'auto', 'conditional')),
    execution_order INTEGER DEFAULT 0,
    trigger_action VARCHAR(50),
    api_purpose TEXT,
    success_action VARCHAR(100),
    error_action VARCHAR(100),
    conditions JSON,
    params_mapping JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
    FOREIGN KEY (api_id) REFERENCES api_interfaces(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_page_apis_page_id ON page_apis(page_id);
CREATE INDEX idx_page_apis_api_id ON page_apis(api_id);
CREATE INDEX idx_page_apis_execution_order ON page_apis(execution_order);
CREATE UNIQUE INDEX idx_page_apis_page_api ON page_apis(page_id, api_id);
```

### 4. 工作流相关表

#### 4.1 workflows (工作流表)
```sql
CREATE TABLE workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive')),
    version VARCHAR(20) DEFAULT '1.0.0',
    config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_version ON workflows(version);
```

#### 4.2 workflow_steps (工作流步骤表)
```sql
CREATE TABLE workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('api', 'condition', 'loop', 'parallel')),
    config JSON,
    order_index INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_workflow_steps_workflow_id ON workflow_steps(workflow_id);
CREATE INDEX idx_workflow_steps_order ON workflow_steps(order_index);
CREATE UNIQUE INDEX idx_workflow_steps_workflow_order ON workflow_steps(workflow_id, order_index);
```

### 5. 场景管理相关表

#### 5.1 scenarios (场景表)
```sql
CREATE TABLE scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_id INTEGER,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive')),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    tags TEXT, -- JSON array as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_scenarios_category_id ON scenarios(category_id);
CREATE INDEX idx_scenarios_status ON scenarios(status);
CREATE INDEX idx_scenarios_priority ON scenarios(priority);
```

#### 5.2 scenario_steps (场景步骤表)
```sql
CREATE TABLE scenario_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('api', 'assertion', 'data_setup', 'cleanup')),
    config JSON,
    order_index INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_scenario_steps_scenario_id ON scenario_steps(scenario_id);
CREATE INDEX idx_scenario_steps_order ON scenario_steps(order_index);
CREATE UNIQUE INDEX idx_scenario_steps_scenario_order ON scenario_steps(scenario_id, order_index);
```

### 6. 需求管理相关表

#### 6.1 requirements (需求表)
```sql
CREATE TABLE requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(20) DEFAULT 'feature' CHECK (type IN ('feature', 'bug', 'enhancement', 'task')),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'rejected', 'implemented')),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assignee VARCHAR(100),
    reporter VARCHAR(100),
    labels TEXT, -- JSON array as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_requirements_status ON requirements(status);
CREATE INDEX idx_requirements_priority ON requirements(priority);
CREATE INDEX idx_requirements_assignee ON requirements(assignee);
CREATE INDEX idx_requirements_type ON requirements(type);
```

#### 6.2 requirement_attachments (需求附件表)
```sql
CREATE TABLE requirement_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    size INTEGER,
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_requirement_attachments_requirement_id ON requirement_attachments(requirement_id);
```

### 7. 分类管理相关表

#### 7.1 categories (分类表)
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL CHECK (type IN ('system', 'scenario', 'requirement', 'api')),
    parent_id INTEGER,
    order_index INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_enabled ON categories(enabled);
CREATE INDEX idx_categories_order ON categories(order_index);
```

## 🔗 表关系说明

### 核心关系
1. **systems → modules**: 一对多关系，一个系统包含多个模块
2. **systems → api_interfaces**: 一对多关系，一个系统包含多个API
3. **modules → api_interfaces**: 一对多关系，一个模块包含多个API
4. **systems → pages**: 一对多关系，一个系统包含多个页面
5. **pages → page_apis**: 一对多关系，一个页面关联多个API

### 扩展关系
1. **pages → page_progress**: 一对一关系，页面配置进度跟踪
2. **pages → page_step_data**: 一对多关系，页面步骤数据存储
3. **scenarios → scenario_steps**: 一对多关系，场景包含多个步骤
4. **workflows → workflow_steps**: 一对多关系，工作流包含多个步骤

## 📊 数据完整性约束

### 外键约束
- **级联删除**: 删除父记录时自动删除子记录
- **置空约束**: 删除引用记录时将外键置空
- **引用完整性**: 确保外键引用的有效性

### 检查约束
- **枚举值检查**: 状态、类型等字段的值域限制
- **非空约束**: 关键字段的非空限制
- **唯一性约束**: 业务唯一性保证

### 默认值设计
- **时间戳**: 自动设置创建和更新时间
- **状态字段**: 合理的默认状态值
- **布尔字段**: 明确的默认布尔值

## 🚀 性能优化策略

### 索引策略
- **主键索引**: 所有表的主键自动索引
- **外键索引**: 所有外键字段建立索引
- **查询索引**: 基于常用查询条件建立复合索引
- **唯一索引**: 业务唯一性约束索引

### 查询优化
- **避免N+1查询**: 使用JOIN或预加载
- **分页查询**: 大数据量的分页处理
- **条件索引**: 基于WHERE条件的索引优化
- **排序优化**: ORDER BY字段的索引支持

### 数据类型优化
- **整型主键**: 使用INTEGER主键提升性能
- **VARCHAR长度**: 合理设置字符串字段长度
- **JSON字段**: 灵活的配置数据存储
- **时间戳**: 统一的时间字段类型

## 🔧 维护策略

### 数据迁移
- **版本控制**: 使用Alembic管理数据库版本
- **向前兼容**: 确保新版本向前兼容
- **数据备份**: 迁移前的数据备份策略
- **回滚机制**: 迁移失败的回滚方案

### 数据清理
- **软删除**: 重要数据使用软删除机制
- **归档策略**: 历史数据的归档处理
- **清理任务**: 定期清理临时数据
- **监控告警**: 数据量和性能监控

---

**文档版本**: v2.0  
**最后更新**: 2024年1月  
**维护者**: 数据库设计团队