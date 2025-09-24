# 路由配置与菜单结构文档

## 📋 路由系统概览

本项目使用 Vue Router 4 进行路由管理，采用嵌套路由结构，所有主要页面都在 Layout 组件内渲染。

## 🏗️ 路由架构

### 基础配置
```javascript
// 路由模式: HTML5 History模式
// 基础路径: /
// 滚动行为: 保持位置或回到顶部
```

### 路由守卫
- **全局前置守卫**: 身份验证检查
- **页面标题设置**: 自动设置浏览器标题
- **登录状态检查**: 未登录用户重定向到登录页

## 🗂️ 完整路由结构

### 1. 根路由 (/)
```javascript
{
  path: '/',
  component: Layout,
  redirect: '/dashboard',
  children: [
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: '@/views/dashboard/index.vue',
      meta: {
        title: '仪表板',
        icon: 'DataBoard'
      }
    }
  ]
}
```

### 2. API管理 (/api-management)
```javascript
{
  path: '/api-management',
  component: Layout,
  redirect: '/api-management/list',
  meta: {
    title: 'API管理',
    icon: 'Connection'
  },
  children: [
    {
      path: 'list',
      name: 'ApiList',
      component: '@/views/api-management/index.vue',
      meta: {
        title: 'API列表',
        icon: 'List'
      }
    }
  ]
}
```
- **完整路径**: `/api-management/list`
- **功能**: API接口的增删改查、测试、文档管理

### 3. 工作流编排 (/workflow-orchestration)
```javascript
{
  path: '/workflow-orchestration',
  component: Layout,
  redirect: '/workflow-orchestration/list',
  meta: {
    title: 'API调用流程',
    icon: 'Share'
  },
  children: [
    {
      path: 'list',
      name: 'WorkflowList',
      component: '@/views/workflow-orchestration/index.vue',
      meta: {
        title: 'API调用流程列表',
        icon: 'List'
      }
    }
  ]
}
```
- **完整路径**: `/workflow-orchestration/list`
- **功能**: API调用流程的设计、编排、执行

### 4. 场景管理 (/scenario-management)
```javascript
{
  path: '/scenario-management',
  component: Layout,
  redirect: '/scenario-management/list',
  meta: {
    title: '用例场景管理',
    icon: 'Operation'
  },
  children: [
    {
      path: 'list',
      name: 'ScenarioList',
      component: '@/views/scenario-management/index.vue',
      meta: {
        title: '用例场景列表',
        icon: 'List'
      }
    }
  ]
}
```
- **完整路径**: `/scenario-management/list`
- **功能**: 测试场景的创建、管理、执行

### 5. 服务管理 (/service-management)
```javascript
{
  path: '/service-management',
  component: Layout,
  redirect: '/service-management/systems',
  meta: {
    title: '服务管理',
    icon: 'Monitor'
  },
  children: [
    {
      path: 'systems',
      name: 'ServiceSystems',
      component: '@/views/service-management/index.vue',
      meta: {
        title: '管理系统',
        icon: 'Grid'
      }
    },
    {
      path: 'systems/:systemId',
      name: 'SystemDetail',
      component: '@/views/service-management/system-detail.vue',
      meta: {
        title: '系统详情',
        hidden: true
      }
    },
    {
      path: 'modules/:moduleId',
      name: 'ModuleDetail',
      component: '@/views/service-management/module-detail.vue',
      meta: {
        title: '模块详情',
        hidden: true
      }
    }
  ]
}
```
- **主路径**: `/service-management/systems`
- **功能**: 管理系统和模块的两级架构管理

### 6. AI场景执行 (/ai-execution)
```javascript
{
  path: '/ai-execution',
  component: Layout,
  redirect: '/ai-execution/console',
  meta: {
    title: 'AI场景执行',
    icon: 'MagicStick'
  },
  children: [
    {
      path: 'console',
      name: 'AiConsole',
      component: '@/views/ai-scenario-execution/index.vue',
      meta: {
        title: '执行控制台',
        icon: 'Monitor'
      }
    },
    {
      path: 'history',
      name: 'AiHistory',
      component: '@/views/ai-scenario-execution/index.vue',
      meta: {
        title: '执行历史',
        icon: 'Clock'
      }
    },
    {
      path: 'config',
      name: 'AiConfig',
      component: '@/views/ai-scenario-execution/index.vue',
      meta: {
        title: 'AI配置',
        icon: 'Setting'
      }
    }
  ]
}
```
- **子路径**:
  - `/ai-execution/console` - 执行控制台
  - `/ai-execution/history` - 执行历史
  - `/ai-execution/config` - AI配置

### 7. 系统集成 (/integration)
```javascript
{
  path: '/integration',
  component: Layout,
  redirect: '/integration/dashboard',
  meta: {
    title: '系统集成',
    icon: 'Connection'
  },
  children: [
    {
      path: 'dashboard',
      name: 'IntegrationDashboard',
      component: '@/views/system-integration/index.vue',
      meta: {
        title: '集成仪表板',
        icon: 'DataBoard'
      }
    },
    {
      path: 'batch-operations',
      name: 'BatchOperations',
      component: '@/views/system-integration/index.vue',
      meta: {
        title: '批量操作',
        icon: 'Operation'
      }
    },
    {
      path: 'monitor',
      name: 'SystemMonitor',
      component: '@/views/system-integration/index.vue',
      meta: {
        title: '系统监控',
        icon: 'Monitor'
      }
    },
    {
      path: 'settings',
      name: 'SystemSettings',
      component: '@/views/system-integration/index.vue',
      meta: {
        title: '系统设置',
        icon: 'Setting'
      }
    }
  ]
}
```
- **子路径**:
  - `/integration/dashboard` - 集成仪表板
  - `/integration/batch-operations` - 批量操作
  - `/integration/monitor` - 系统监控
  - `/integration/settings` - 系统设置

### 8. 特殊路由

#### 登录页面
```javascript
{
  path: '/login',
  name: 'Login',
  component: '@/views/login/index.vue',
  meta: {
    title: '登录',
    hidden: true,
    requiresAuth: false
  }
}
```

#### 404页面
```javascript
{
  path: '/404',
  name: '404',
  component: '@/views/404.vue',
  meta: {
    title: '页面不存在',
    hidden: true,
    requiresAuth: false
  }
}
```

#### 通配符路由
```javascript
{
  path: '/:pathMatch(.*)*',
  redirect: '/404'
}
```

## 🎯 菜单结构

### 侧边栏菜单层级
```
AI自动化测试
├── 📊 仪表板
├── 🔗 API管理
│   └── 📋 API列表
├── 🔄 API调用流程
│   └── 📋 API调用流程列表
├── 🎭 用例场景管理
│   └── 📋 用例场景列表
├── 🖥️ 服务管理
│   └── 📋 服务列表
├── 🪄 AI场景执行
│   ├── 🖥️ 执行控制台
│   ├── 🕐 执行历史
│   └── ⚙️ AI配置
└── 🔌 系统集成
    ├── 📊 集成仪表板
    ├── 🔄 批量操作
    ├── 📈 系统监控
    └── ⚙️ 系统设置
```

### 菜单渲染逻辑
```javascript
// Layout组件中的菜单渲染
<el-menu
  :default-active="$route.path"
  :collapse="appStore.sidebarCollapsed"
  :unique-opened="true"
  router
  class="sidebar-menu"
>
  <template v-for="route in menuRoutes" :key="route.path">
    <!-- 多子菜单的路由组 -->
    <el-sub-menu 
      v-if="route.children && route.children.length > 1" 
      :index="route.path"
    >
      <!-- 子菜单项 -->
    </el-sub-menu>
    
    <!-- 单页面路由 -->
    <el-menu-item 
      v-else-if="!route.meta?.hidden"
      :index="route.children?.[0]?.path || route.path"
    >
      <!-- 菜单项内容 -->
    </el-menu-item>
  </template>
</el-menu>
```

## 🔐 路由权限控制

### Meta字段说明
```javascript
meta: {
  title: '页面标题',        // 显示在浏览器标题和面包屑中
  icon: '图标名称',         // Element Plus图标
  hidden: false,          // 是否在菜单中隐藏
  requiresAuth: true      // 是否需要登录(默认true)
}
```

### 权限检查流程
1. **路由跳转前检查**: `router.beforeEach`
2. **登录状态验证**: 检查localStorage中的用户信息
3. **重定向逻辑**:
   - 未登录访问需要权限的页面 → 跳转到登录页
   - 已登录访问登录页 → 跳转到首页

## 🧭 面包屑导航

### 生成规则
- 根据当前路由路径自动生成
- 显示路由层级关系
- 支持点击跳转到上级页面

### 示例
```
首页 / API管理 / API列表
首页 / AI场景执行 / 执行控制台
首页 / 系统集成 / 系统监控
```

## 🔄 路由懒加载

### 实现方式
所有页面组件都使用动态导入实现懒加载：
```javascript
component: () => import('@/views/dashboard/index.vue')
```

### 优势
- 减少初始包大小
- 提高首屏加载速度
- 按需加载页面资源

## 📱 路由状态管理

### 当前路由信息
- 通过 `$route` 获取当前路由信息
- 用于菜单高亮、面包屑生成等

### 路由跳转方法
```javascript
// 编程式导航
this.$router.push('/api-management/list')
this.$router.replace('/dashboard')
this.$router.go(-1)

// 声明式导航
<router-link to="/dashboard">仪表板</router-link>
```

## 🛠️ 开发注意事项

### 添加新路由
1. 在 `routes` 数组中添加路由配置
2. 创建对应的Vue组件
3. 设置合适的meta信息
4. 确保路径和组件路径匹配

### 路由调试
- 使用Vue DevTools查看路由状态
- 检查路由守卫执行情况
- 验证权限控制逻辑

### 性能优化
- 合理使用路由懒加载
- 避免过深的路由嵌套
- 优化路由守卫逻辑

---

**文档更新时间**: 2024年12月  
**维护者**: AI开发团队