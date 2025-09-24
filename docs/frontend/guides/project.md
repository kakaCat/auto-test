# AI自动化测试系统 - 前端项目文档

## 📋 项目概览

**项目名称**: AI自动化测试系统前端界面  
**版本**: 1.0.0  
**技术栈**: Vue 3 + Vite + Element Plus + Pinia  
**开发端口**: http://localhost:3000  
**API代理**: http://localhost:8000  

## 🏗️ 技术架构

### 核心技术栈
- **前端框架**: Vue 3.4.0 (Composition API)
- **构建工具**: Vite 4.5.3
- **路由管理**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **UI组件库**: Element Plus 2.4.4
- **图表库**: ECharts 5.4.3 + Vue-ECharts 6.6.1
- **代码编辑器**: Monaco Editor 0.45.0
- **HTTP客户端**: Axios 1.6.0

### 开发工具
- **代码检查**: ESLint 8.56.0
- **代码格式化**: Prettier 3.1.1
- **自动导入**: unplugin-auto-import + unplugin-vue-components
- **类型支持**: TypeScript类型定义

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── App.vue            # 根组件
│   ├── main.js            # 应用入口
│   ├── layout/            # 布局组件
│   │   └── index.vue      # 主布局(侧边栏+导航栏)
│   ├── router/            # 路由配置
│   │   └── index.js       # 路由定义
│   ├── stores/            # 状态管理
│   │   └── app.js         # 应用全局状态
│   ├── styles/            # 全局样式
│   ├── utils/             # 工具函数
│   └── views/             # 页面组件
│       ├── dashboard/           # 仪表板
│       ├── api-management/      # API管理
│       ├── workflow-orchestration/ # 工作流编排
│       ├── scenario-management/    # 场景管理
│       ├── service-management/     # 服务管理
│       ├── ai-scenario-execution/  # AI场景执行
│       ├── system-integration/     # 系统集成
│       ├── login/              # 登录页
│       └── 404.vue            # 404页面
├── package.json           # 项目依赖
├── vite.config.js         # Vite配置
└── index.html            # HTML模板
```

## 🎯 核心功能模块

### 1. 仪表板 (Dashboard)
- **路径**: `/dashboard`
- **组件**: `@/views/dashboard/index.vue`
- **功能**: 系统概览、数据统计、快速导航

### 2. API管理 (API Management)
- **路径**: `/api-management`
- **组件**: `@/views/api-management/index.vue`
- **功能**: API接口管理、测试、文档

### 3. 工作流编排 (Workflow Orchestration)
- **路径**: `/workflow-orchestration`
- **组件**: `@/views/workflow-orchestration/index.vue`
- **功能**: API调用流程设计、执行

### 4. 场景管理 (Scenario Management)
- **路径**: `/scenario-management`
- **组件**: `@/views/scenario-management/index.vue`
- **功能**: 测试场景创建、管理

### 5. 服务管理 (Service Management)
- **路径**: `/service-management`
- **主路由**: `/service-management/systems`
- **组件**: `@/views/service-management/index.vue`
- **功能**: 管理系统和模块的两级架构管理
- **子路由**:
  - 管理系统列表: `/service-management/systems`
  - 系统详情: `/service-management/systems/:systemId`
  - 模块详情: `/service-management/modules/:moduleId`

### 6. AI场景执行 (AI Scenario Execution)
- **路径**: `/ai-execution`
- **子模块**:
  - 执行控制台: `/ai-execution/console`
  - 执行历史: `/ai-execution/history`
  - AI配置: `/ai-execution/config`

### 7. 系统集成 (System Integration)
- **路径**: `/integration`
- **子模块**:
  - 集成仪表板: `/integration/dashboard`
  - 批量操作: `/integration/batch-operations`
  - 系统监控: `/integration/monitor`
  - 系统设置: `/integration/settings`

## 🔧 开发配置

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 启动命令
```bash
# 安装依赖
npm install

# 开发模式启动
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format
```

### 开发服务器配置
- **端口**: 3000
- **主机**: 0.0.0.0
- **自动打开**: 是
- **API代理**: `/api` → `http://localhost:8000`

## 🎨 UI/UX 设计

### 布局结构
- **侧边栏**: 可折叠的导航菜单
- **顶部导航**: 面包屑导航、主题切换、用户信息
- **主内容区**: 路由视图渲染区域

### 主题系统
- **浅色主题**: 默认主题
- **深色主题**: 支持暗黑模式切换
- **主题持久化**: 本地存储保存用户偏好

### 响应式设计
- **桌面端**: 完整功能布局
- **移动端**: 自适应布局(待完善)

## 📊 状态管理

### App Store (全局状态)
```javascript
// 主要状态
- sidebarCollapsed: 侧边栏折叠状态
- theme: 主题模式 ('light' | 'dark')
- loading: 全局加载状态
- device: 设备类型 ('desktop' | 'mobile')
- user: 用户信息

// 主要方法
- toggleSidebar(): 切换侧边栏
- toggleTheme(): 切换主题
- setUser(): 设置用户信息
- logout(): 用户登出
- init(): 初始化应用状态
```

## 🔀 路由系统

### 路由结构
```javascript
// 主要路由配置
- / → Layout → /dashboard (重定向)
- /dashboard → 仪表板
- /api-management → API管理
  - /api-management/list → API列表
- /workflow-orchestration → 工作流编排
  - /workflow-orchestration/list → 流程列表
- /scenario-management → 场景管理
  - /scenario-management/list → 场景列表
- /service-management → 服务管理
  - /service-management/list → 服务列表
- /ai-execution → AI场景执行
  - /ai-execution/console → 执行控制台
  - /ai-execution/history → 执行历史
  - /ai-execution/config → AI配置
- /integration → 系统集成
  - /integration/dashboard → 集成仪表板
  - /integration/batch-operations → 批量操作
  - /integration/monitor → 系统监控
  - /integration/settings → 系统设置
```

### 路由守卫
- **全局前置守卫**: 身份验证检查
- **路由元信息**: 页面标题、图标、权限控制

## 🔌 API集成

### HTTP配置
- **基础URL**: 通过Vite代理配置
- **请求拦截**: 添加认证头、请求日志
- **响应拦截**: 错误处理、状态码处理
- **超时设置**: 默认超时配置

### 数据流
```
Vue组件 → API调用 → 后端服务 (localhost:8000)
    ↓
状态更新 → UI重新渲染
```

## 🎯 开发规范

### 代码风格
- **组件命名**: PascalCase
- **文件命名**: kebab-case
- **变量命名**: camelCase
- **常量命名**: UPPER_SNAKE_CASE

### 组件结构
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup>
// 导入
// 响应式数据
// 计算属性
// 方法
// 生命周期
</script>

<style scoped>
/* 组件样式 */
</style>
```

### Git提交规范
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 🚀 部署说明

### 构建输出
- **目录**: `dist/`
- **资源**: 静态文件、压缩后的JS/CSS
- **Source Map**: 生产环境关闭

### 环境变量
- **开发环境**: 自动代理到localhost:8000
- **生产环境**: 需要配置实际API地址

## 📝 开发注意事项

1. **组件复用**: 优先使用Element Plus组件
2. **状态管理**: 复杂状态使用Pinia管理
3. **路由懒加载**: 所有页面组件使用动态导入
4. **错误处理**: 统一错误处理和用户提示
5. **性能优化**: 合理使用计算属性和监听器
6. **类型安全**: 逐步引入TypeScript类型定义

## 🔄 更新日志

### v1.0.0 (当前版本)
- ✅ 基础项目架构搭建
- ✅ 主要功能模块实现
- ✅ 路由和状态管理配置
- ✅ UI组件库集成
- ✅ 主题系统实现

---

**文档更新时间**: 2024年12月
**维护者**: AI开发团队