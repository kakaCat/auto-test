# Vue 视图组件功能和结构文档

## 概述

本文档详细记录了 AI 自动化测试平台前端项目中所有视图组件的功能、数据结构、UI 布局和交互逻辑，为后续 AI 开发提供完整的组件参考。

## 组件架构

### 目录结构
```
src/views/
├── dashboard/                 # 仪表板
├── api-management/           # API管理
├── workflow-orchestration/   # 工作流编排
├── scenario-management/      # 场景管理
├── service-management/       # 服务管理
├── ai-scenario-execution/    # AI场景执行
├── system-integration/       # 系统集成
├── login/                    # 登录页面
└── 404.vue                   # 404错误页面
```

## 核心业务组件

### 1. 仪表板 (Dashboard)

**文件路径**: `/src/views/dashboard/index.vue`

**主要功能**:
- 系统概览和统计数据展示
- 功能模块快捷入口
- 最近活动记录
- 系统状态监控

**数据结构**:
```javascript
// 统计数据
stats: {
  apiCount: Number,      // API接口数量
  scenarioCount: Number, // 测试场景数量
  workflowCount: Number, // 工作流数量
  executionCount: Number // 执行次数
}

// 功能模块
modules: [{
  name: String,        // 模块名称
  description: String, // 模块描述
  path: String,       // 路由路径
  icon: String,       // 图标组件
  color: String       // 主题色
}]

// 活动记录
activities: [{
  id: String,
  title: String,      // 活动标题
  description: String, // 活动描述
  type: String,       // 活动类型
  time: String        // 时间戳
}]
```

**UI 布局**:
- 顶部：平台标题和描述
- 统计卡片网格：4个统计指标卡片
- 功能模块网格：各功能模块的快捷入口
- 最近活动列表：时间线形式的活动记录

### 2. API管理 (API Management)

**文件路径**: `/src/views/api-management/index.vue`

**主要功能**:
- 按服务和模块层级管理API接口
- API接口录入、编辑、删除
- 参数配置和文档管理
- 调用记录查看和统计
- 批量操作和导入导出

**数据结构**:
```javascript
// 服务列表
serviceList: [{
  id: Number,
  name: String,        // 服务名称
  description: String, // 服务描述
  status: String,      // 服务状态 (active/inactive)
  modules: [{           // 模块列表
    id: Number,
    name: String,      // 模块名称
    description: String,
    status: String,
    apis: [{            // API列表
      id: Number,
      name: String,     // API名称
      version: String,  // 版本号
      method: String,   // HTTP方法
      url: String,      // 接口地址
      description: String,
      status: String,
      callCount: Number,    // 调用次数
      lastCallTime: String  // 最后调用时间
    }]
  }]
}]

// 搜索表单
searchForm: {
  keyword: String,     // 关键词
  serviceId: String,   // 服务ID
  method: String       // HTTP方法
}
```

**UI 布局**:
- 页面头部：标题、描述和操作按钮
- 搜索筛选区：关键词搜索、服务筛选、方法筛选
- 服务树形结构：可折叠的服务-模块-API三级结构
- 操作区域：编辑、测试、删除等操作按钮

### 3. 工作流编排 (Workflow Orchestration)

**文件路径**: `/src/views/workflow-orchestration/index.vue`

**主要功能**:
- 可视化工作流设计
- 节点拖拽和连接
- 工作流模板管理
- 执行历史和监控
- 版本控制和发布

**数据结构**:
```javascript
// 工作流列表
workflowList: [{
  id: Number,
  name: String,        // 工作流名称
  description: String, // 描述
  category: String,    // 分类 (api-test/data-process/business/monitor)
  status: String,      // 状态 (running/stopped/draft/published)
  version: String,     // 版本号
  nodeCount: Number,   // 节点数量
  lastExecution: String, // 最后执行时间
  executionCount: Number // 执行次数
}]

// 统计数据
stats: {
  total: Number,       // 总工作流数
  active: Number,      // 活跃工作流数
  nodes: Number,       // 总节点数
  executions: Number   // 执行次数
}

// 模板列表
templates: [{
  id: Number,
  name: String,        // 模板名称
  description: String, // 描述
  icon: String,        // 图标
  nodeCount: Number,   // 节点数量
  usageCount: Number   // 使用次数
}]
```

**UI 布局**:
- 页面头部：标题和操作按钮
- 统计卡片：工作流统计数据
- 搜索筛选：关键词、状态、分类筛选
- 工作流列表：表格形式展示工作流信息
- 模板区域：常用工作流模板

### 4. 场景管理 (Scenario Management)

**文件路径**: `/src/views/scenario-management/index.vue`

**主要功能**:
- 测试场景创建和编辑
- 接口编排和配置
- 并行/顺序执行设置
- 场景模板和复用
- 执行结果分析

**数据结构**:
```javascript
// 场景列表
scenarioList: [{
  id: Number,
  name: String,        // 场景名称
  description: String, // 描述
  type: String,        // 执行类型 (parallel/sequential)
  status: String,      // 状态 (active/inactive/draft)
  apiCount: Number,    // 接口数量
  successRate: Number, // 成功率
  lastExecution: String, // 最后执行时间
  executionCount: Number // 执行次数
}]

// 统计数据
stats: {
  total: Number,       // 总场景数
  active: Number,      // 活跃场景数
  success: Number,     // 成功场景数
  executions: Number   // 总执行次数
}
```

**UI 布局**:
- 页面头部：标题和操作按钮
- 统计卡片：场景统计数据
- 搜索筛选：关键词、状态筛选
- 场景列表：表格展示场景信息
- 操作区域：编辑、执行、复制、删除等操作

### 5. 服务管理 (Service Management)

**文件路径**: `/src/views/service-management/index.vue`

**主要功能**:
- 管理系统列表展示和管理
- 系统详情查看和编辑
- 模块管理和配置
- 系统启用/禁用状态管理
- 分类筛选和搜索功能

**数据结构**:
```javascript
// 系统列表
systems: [{
  id: Number,
  name: String,        // 系统名称
  description: String, // 描述
  category: String,    // 分类 (web/mobile/desktop/api)
  enabled: Boolean,    // 启用状态
  icon: String,        // 图标
  modules: Array       // 模块列表
}]

// 模块结构
module: {
  id: Number,
  name: String,        // 模块名称
  description: String, // 描述
  version: String,     // 版本号
  enabled: Boolean,    // 启用状态
  systemId: Number     // 所属系统ID
}

// 搜索和筛选
searchKeyword: String,    // 搜索关键词
selectedCategory: String, // 分类筛选
enabledFilter: String     // 启用状态筛选
```

**UI 布局**:
- 页面头部：标题和操作按钮
- 搜索筛选区：关键词搜索、分类筛选、状态筛选
- 系统卡片网格：展示系统信息和操作菜单
- 搜索筛选：关键词、状态、类型筛选
- 服务列表：表格展示服务信息
- 操作区域：查看、编辑、测试、删除等操作

### 6. AI场景执行 (AI Scenario Execution)

**文件路径**: `/src/views/ai-scenario-execution/index.vue`

**主要功能**:
- 智能场景执行代理
- 参数增强和优化
- 场景解析和理解
- 自动化执行监控
- AI配置和调优

**数据结构**:
```javascript
// 执行统计
stats: {
  total: Number,       // 总执行次数
  running: Number,     // 执行中数量
  success: Number,     // 成功执行数
  enhanced: Number     // AI增强次数
}

// 快速执行表单
quickForm: {
  scenario: String,    // 场景ID
  enhanceMode: String, // 增强模式 (smart/basic/none)
  parameters: Object   // 执行参数
}

// 场景列表
scenarios: [{
  id: String,
  name: String,        // 场景名称
  description: String, // 描述
  type: String,        // 场景类型
  aiEnabled: Boolean   // 是否启用AI
}]
```

**UI 布局**:
- 页面头部：标题和操作按钮
- 统计卡片：AI执行统计数据
- 快速执行区：场景选择和参数配置
- 执行历史：历史执行记录列表
- AI配置：智能增强参数设置

### 7. 系统集成 (System Integration)

**文件路径**: `/src/views/system-integration/index.vue`

**主要功能**:
- 接口流程编排集成
- 系统间数据同步
- 集成配置管理
- 监控和告警
- 性能分析

**数据结构**:
```javascript
// 集成列表
integrationList: [{
  id: Number,
  name: String,        // 集成名称
  description: String, // 描述
  type: String,        // 集成类型 (api/workflow/data/message)
  status: String,      // 状态 (running/stopped/configuring/error)
  environment: String, // 环境 (dev/test/prod)
  lastExecution: String, // 最后执行时间
  successRate: Number  // 成功率
}]

// 统计数据
stats: {
  total: Number,       // 总集成数
  active: Number,      // 活跃集成数
  apis: Number,        // 集成API数
  success: Number      // 成功集成数
}
```

**UI 布局**:
- 页面头部：标题和操作按钮
- 统计卡片：集成统计数据
- 快速操作：常用集成操作入口
- 搜索筛选：多维度筛选条件
- 集成列表：表格展示集成信息

## 辅助页面组件

### 8. 登录页面 (Login)

**文件路径**: `/src/views/login/index.vue`

**主要功能**:
- 用户身份验证
- 记住密码功能
- 密码找回入口
- 注册引导

**数据结构**:
```javascript
// 登录表单
loginForm: {
  username: String,    // 用户名
  password: String,    // 密码
  remember: Boolean    // 记住密码
}

// 表单验证规则
loginRules: {
  username: Array,     // 用户名验证规则
  password: Array      // 密码验证规则
}
```

**UI 布局**:
- 左侧：登录表单区域
- 右侧：产品介绍和特性展示
- 响应式设计：移动端适配

### 9. 404错误页面

**文件路径**: `/src/views/404.vue`

**主要功能**:
- 友好的错误提示
- 导航建议
- 返回操作

**UI 布局**:
- 中心化错误信息展示
- 操作建议和导航按钮
- 简洁的视觉设计

## 组件共同特性

### 1. 响应式设计
- 所有组件都支持移动端适配
- 使用 Element Plus 的响应式栅格系统
- 断点适配：xs, sm, md, lg, xl

### 2. 状态管理
- 使用 Pinia 进行状态管理
- 组件间数据共享通过 store
- 持久化存储用户偏好设置

### 3. 国际化支持
- 预留国际化接口
- 文本内容可配置化
- 支持多语言切换

### 4. 主题系统
- 支持明暗主题切换
- CSS 变量定义主题色彩
- 组件样式统一管理

### 5. 权限控制
- 基于角色的权限管理
- 组件级权限控制
- 操作权限验证

### 6. 性能优化
- 路由懒加载
- 组件按需加载
- 虚拟滚动支持

## 开发规范

### 1. 组件结构
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup>
// 组合式 API
// 导入依赖
// 响应式数据
// 计算属性
// 方法定义
// 生命周期钩子
</script>

<style scoped>
/* 组件样式 */
</style>
```

### 2. 命名规范
- 组件文件：kebab-case
- 变量和方法：camelCase
- 常量：UPPER_SNAKE_CASE
- CSS 类名：kebab-case

### 3. 代码组织
- 逻辑相关的代码放在一起
- 使用组合式函数提取复用逻辑
- 保持组件职责单一

### 4. 错误处理
- 统一的错误处理机制
- 用户友好的错误提示
- 错误日志记录

### 5. 测试覆盖
- 单元测试覆盖核心逻辑
- 集成测试验证组件交互
- E2E 测试保证用户流程

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 完成所有核心业务组件
- 实现基础功能和 UI 布局

### 后续规划
- 组件性能优化
- 更多交互特性
- 移动端体验优化
- 国际化完善

---

*本文档将随着项目发展持续更新，确保与实际代码保持同步。*