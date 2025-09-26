# 页面表设计和表关系文档

## 1. 表关系ER图

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    systems      │ 1───N │    modules      │ 1───N │ api_interfaces  │
│                 │       │                 │       │                 │
│ • id (PK)       │       │ • id (PK)       │       │ • id (PK)       │
│ • name          │       │ • system_id(FK) │       │ • system_id(FK) │
│ • description   │       │ • name          │       │ • module_id(FK) │
│ • category      │       │ • description   │       │ • name          │
│ • status        │       │ • status        │       │ • method        │
│ • created_at    │       │ • created_at    │       │ • path          │
│ • updated_at    │       │ • updated_at    │       │ • status        │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         │                                                   │
         │ 1                                                 │
         │                                                   │
         N                                                   │
┌─────────────────┐                                         │
│     pages       │                                         │
│                 │                                         │
│ • id (PK)       │                                         │
│ • system_id(FK) │                                         │
│ • module_id(FK) │                                         │
│ • name          │                                         │
│ • description   │                                         │
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

## 2. 核心表设计

### 2.1 pages（页面主表）
- **作用**: 存储页面基本信息
- **关键字段**:
  - `config_status`: 配置完成状态（incomplete/completed）
  - `page_type`: 页面类型（page/modal/drawer等）
  - `status`: 页面状态（draft/active/inactive等）

### 2.2 page_progress（页面配置进度表）
- **作用**: 跟踪页面分步配置进度
- **关键字段**:
  - `current_step`: 当前步骤
  - `completed_steps`: 已完成步骤（JSON数组）
  - `step_status`: 各步骤状态（JSON对象）

### 2.3 page_step_data（页面步骤数据表）
- **作用**: 存储各步骤的具体配置数据
- **关键字段**:
  - `step_name`: 步骤名称（basic/layout/api/interaction）
  - `step_data`: 步骤数据（JSON格式）
  - `version`: 数据版本号

### 2.4 page_apis（页面API关联表）
- **作用**: 管理页面与API的关联关系
- **关键字段**:
  - `execution_type`: 执行类型（parallel/serial/conditional）
  - `trigger_action`: 触发动作（load/click/submit等）
  - `params_mapping`: 参数映射（JSON格式）

### 2.5 page_components（页面组件表）
- **作用**: 存储页面布局和组件配置
- **关键字段**:
  - `component_type`: 组件类型（form/table/chart等）
  - `config_data`: 组件配置（JSON格式）
  - `position_x/y`: 组件位置

### 2.6 page_interactions（页面交互表）
- **作用**: 定义页面组件间的交互逻辑
- **关键字段**:
  - `interaction_type`: 交互类型（click/hover/submit等）
  - `action_type`: 动作类型（show/hide/navigate等）
  - `conditions`: 执行条件（JSON格式）

## 3. 表关系说明

### 3.1 主要关系
1. **systems → pages**: 一对多，系统包含多个页面
2. **modules → pages**: 一对多，模块包含多个页面（可选）
3. **pages → page_apis → api_interfaces**: 多对多，页面关联多个API
4. **pages → page_progress**: 一对一，每个页面有一个配置进度
5. **pages → page_step_data**: 一对多，每个页面有多个步骤数据
6. **pages → page_components**: 一对多，每个页面有多个组件
7. **pages → page_interactions**: 一对多，每个页面有多个交互

### 3.2 外键约束
- **CASCADE删除**: 删除页面时，自动删除相关的配置数据
- **SET NULL**: 删除模块时，页面的module_id设为NULL
- **RESTRICT**: 防止删除被引用的系统或API

## 4. 索引策略

### 4.1 主要索引
```sql
-- 页面表索引
CREATE INDEX idx_pages_system_id ON pages(system_id);
CREATE INDEX idx_pages_status ON pages(status);
CREATE INDEX idx_pages_config_status ON pages(config_status);

-- 步骤数据索引
CREATE INDEX idx_page_step_data_page_step ON page_step_data(page_id, step_name);
CREATE INDEX idx_page_step_data_current ON page_step_data(page_id, is_current);

-- 组件表索引
CREATE INDEX idx_page_components_page_id ON page_components(page_id);
CREATE INDEX idx_page_components_type ON page_components(page_id, component_type);

-- API关联索引
CREATE INDEX idx_page_apis_page_id ON page_apis(page_id);
CREATE INDEX idx_page_apis_execution_order ON page_apis(page_id, execution_order);
```

## 5. 数据完整性

### 5.1 约束规则
1. **唯一性约束**: 防止重复数据
2. **检查约束**: 确保状态值有效
3. **非空约束**: 确保关键字段不为空
4. **外键约束**: 维护数据一致性

### 5.2 业务规则
1. 页面必须属于某个系统
2. 步骤数据必须关联到有效页面
3. API关联必须指向存在的API
4. 组件ID在页面内必须唯一
5. 交互必须指向有效的组件

## 6. 扩展性考虑

### 6.1 版本控制
- `page_step_data`表支持版本控制
- 可以回滚到历史版本
- 支持并发编辑检测

### 6.2 权限控制
- `pages`表包含权限配置字段
- 支持细粒度权限控制
- 可扩展到组件级权限

### 6.3 多租户支持
- 通过`system_id`实现租户隔离
- 支持跨系统的页面复用
- 便于数据迁移和备份