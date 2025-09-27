/**
 * Vue Router 路由配置文件
 * 
 * 功能说明：
 * - 定义应用的路由结构和导航规则
 * - 配置嵌套路由和布局组件
 * - 实现路由守卫和权限控制
 * - 设置页面元信息和导航菜单
 * 
 * 路由架构：
 * - 采用嵌套路由结构
 * - 统一使用Layout布局组件
 * - 支持动态路由和懒加载
 * - 集成权限验证和页面标题
 * 
 * 技术特性：
 * - Vue Router 4
 * - History模式导航
 * - 路由懒加载优化
 * - 导航守卫权限控制
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

/**
 * 路由配置数组
 * 
 * 路由结构说明：
 * - 主路由：使用Layout组件作为容器
 * - 子路由：具体的页面组件
 * - 元信息：包含标题、图标、权限等
 * 
 * 路由分类：
 * 1. 仪表板 - 数据概览和统计
 * 2. API管理 - API接口管理
 * 3. 工作流编排 - API调用流程
 * 4. 场景管理 - 测试用例场景
 * 5. 服务管理 - 系统和模块管理
 * 6. AI执行 - AI自动化测试
 * 7. 系统集成 - 集成管理功能
 * 8. 监控管理 - 日志和监控
 * 9. 特殊页面 - 登录、404等
 */
const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '仪表板',
          icon: 'DataBoard'
        }
      }
    ]
  },
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
        component: () => import('@/views/api-management/index.vue'),
        meta: {
          title: 'API列表',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/page-management',
    component: Layout,
    redirect: '/page-management/list',
    meta: {
      title: '页面管理',
      icon: 'Document'
    },
    children: [
      {
        path: 'list',
        name: 'PageList',
        component: () => import('@/views/page-management/index.vue'),
        meta: {
          title: '页面列表',
          icon: 'List'
        }
      }
    ]
  },
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
        component: () => import('@/views/workflow-orchestration/index.vue'),
        meta: {
          title: 'API调用流程列表',
          icon: 'List'
        }
      },
      {
        path: 'designer',
        name: 'WorkflowDesigner',
        component: () => import('@/views/workflow-orchestration/designer.vue'),
        meta: {
          title: '可视化设计器',
          icon: 'Setting'
        }
      }
    ]
  },
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
        component: () => import('@/views/scenario-management/index.vue'),
        meta: {
          title: '用例场景列表',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/service-management',
    component: Layout,
    redirect: '/service-management/systems',
    meta: {
      title: '系统管理',
      icon: 'Monitor'
    },
    children: [
      {
        path: 'systems',
        name: 'ServiceSystems',
        component: () => import('@/views/service-management/index.vue'),
        meta: {
          title: '系统列表',
          icon: 'Grid',
          description: '管理系统和模块的两级架构'
        }
      }
    ]
  },
  // {
  //   path: '/ai-execution',
  //   component: Layout,
  //   redirect: '/ai-execution/console',
  //   meta: {
  //     title: 'AI场景执行',
  //     icon: 'MagicStick'
  //   },
  //   children: [
  //     {
  //       path: 'console',
  //       name: 'AiConsole',
  //       component: () => import('@/views/ai-scenario-execution/index.vue'),
  //       meta: {
  //         title: '执行控制台',
  //         icon: 'Monitor'
  //       }
  //     },
  //     {
  //       path: 'history',
  //       name: 'AiHistory',
  //       component: () => import('@/views/ai-scenario-execution/index.vue'),
  //       meta: {
  //         title: '执行历史',
  //         icon: 'Clock'
  //       }
  //     },
  //     {
  //       path: 'config',
  //       name: 'AiConfig',
  //       component: () => import('@/views/ai-scenario-execution/index.vue'),
  //       meta: {
  //         title: 'AI配置',
  //         icon: 'Setting'
  //       }
  //     }
  //   ]
  // },
  // {
  //   path: '/integration',
  //   component: Layout,
  //   redirect: '/integration/dashboard',
  //   meta: {
  //     title: '系统集成',
  //     icon: 'Connection'
  //   },
  //   children: [
  //     {
  //       path: 'dashboard',
  //       name: 'IntegrationDashboard',
  //       component: () => import('@/views/system-integration/index.vue'),
  //       meta: {
  //         title: '集成仪表板',
  //         icon: 'DataBoard'
  //       }
  //     },
  //     {
  //       path: 'batch-operations',
  //       name: 'BatchOperations',
  //       component: () => import('@/views/system-integration/index.vue'),
  //       meta: {
  //         title: '批量操作',
  //         icon: 'Operation'
  //       }
  //     },
  //     {
  //       path: 'monitor',
  //       name: 'SystemMonitor',
  //       component: () => import('@/views/system-integration/index.vue'),
  //       meta: {
  //         title: '系统监控',
  //         icon: 'Monitor'
  //       }
  //     },
  //     {
  //       path: 'settings',
  //       name: 'SystemSettings',
  //       component: () => import('@/views/system-integration/index.vue'),
  //       meta: {
  //         title: '系统设置',
  //         icon: 'Setting'
  //       }
  //     }
  //   ]
  // },
  // {
  //   path: '/monitor',
  //   component: Layout,
  //   redirect: '/monitor/logs',
  //   meta: {
  //     title: '监控管理',
  //     icon: 'Monitor'
  //   },
  //   children: [
  //     {
  //       path: 'logs',
  //       name: 'MonitorLogs',
  //       component: () => import('@/views/monitor/logs.vue'),
  //       meta: {
  //         title: '日志管理',
  //         icon: 'DocumentCopy'
  //       }
  //     }
  //   ]
  // },
  // {
  //   path: '/api-test',
  //   component: Layout,
  //   meta: {
  //     title: 'API切换测试',
  //     icon: 'Setting'
  //   },
  //   children: [
  //     {
  //       path: '',
  //       name: 'ApiTest',
  //       component: () => import('@/views/api-test.vue'),
  //       meta: {
  //         title: 'API切换测试',
  //         icon: 'Setting'
  //       }
  //     }
  //   ]
  // },
  {
    path: '/ai-orchestration',
    component: Layout,
    redirect: '/ai-orchestration/index',
    meta: {
      title: 'AI编排',
      icon: 'MagicStick'
    },
    children: [
      {
        path: 'index',
        name: 'AiOrchestration',
        component: () => import('@/views/ai-orchestration/index.vue'),
        meta: {
          title: 'AI API编排',
          icon: 'MagicStick',
          description: '通过自然语言描述，让AI自动编排和执行API测试'
        }
      }
    ]
  },
  {
    path: '/requirement-management',
    component: Layout,
    redirect: '/requirement-management/list',
    meta: {
      title: '需求管理',
      icon: 'Document'
    },
    children: [
      {
        path: 'list',
        name: 'RequirementList',
        component: () => import('@/views/requirement-management/index.vue'),
        meta: {
          title: '需求列表',
          icon: 'List'
        }
      }
    ]
  },

  // {
  //   path: '/login',
  //   name: 'Login',
  //   component: () => import('@/views/login/index.vue'),
  //   meta: {
  //     title: '登录',
  //     hidden: true,
  //     requiresAuth: false
  //   }
  // },
  // {
  //   path: '/404',
  //   name: '404',
  //   component: () => import('@/views/404.vue'),
  //   meta: {
  //     title: '页面不存在',
  //     hidden: true,
  //     requiresAuth: false
  //   }
  // },
  // {
  //   path: '/:pathMatch(.*)*',
  //   redirect: '/404'
  // }
]

/**
 * 创建路由实例
 * 
 * 配置说明：
 * - 使用HTML5 History模式，支持干净的URL
 * - 配置滚动行为，提升用户体验
 * - 集成路由配置数组
 * 
 * History模式优势：
 * - URL更美观，无#号
 * - 支持服务端渲染
 * - 更好的SEO支持
 */
const router = createRouter({
  history: createWebHistory(),  // HTML5 History模式
  routes,                       // 路由配置
  
  /**
   * 滚动行为配置
   * 
   * 控制路由切换时的页面滚动行为：
   * - 如果有保存的滚动位置，恢复到该位置
   * - 否则滚动到页面顶部
   * 
   * 应用场景：
   * - 浏览器前进/后退时恢复滚动位置
   * - 新页面访问时回到顶部
   * - 提升用户浏览体验
   */
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition  // 恢复保存的滚动位置
    } else {
      return { top: 0 }     // 滚动到页面顶部
    }
  }
})

/**
 * 全局前置路由守卫
 * 
 * 功能职责：
 * - 动态设置页面标题
 * - 权限验证和登录检查
 * - 路由访问控制
 * - 用户状态验证
 * 
 * 执行时机：
 * - 每次路由跳转前执行
 * - 在路由组件渲染前完成验证
 * 
 * 验证流程：
 * 1. 设置页面标题
 * 2. 检查路由权限要求
 * 3. 验证用户登录状态
 * 4. 决定是否允许访问
 */
router.beforeEach((to, from, next) => {
  /**
   * 动态设置页面标题
   * 
   * 根据路由元信息设置浏览器标题栏显示内容。
   * 格式：页面标题 - 应用名称
   * 
   * SEO优化：
   * - 提供有意义的页面标题
   * - 便于搜索引擎索引
   * - 改善用户体验
   */
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI自动化测试平台`
  } else {
    document.title = 'AI自动化测试平台'
  }
  
  /**
   * 权限验证逻辑
   * 
   * 验证步骤：
   * 1. 检查目标路由是否需要登录权限
   * 2. 获取当前用户登录状态
   * 3. 根据权限要求和登录状态决定跳转
   * 
   * 权限规则：
   * - requiresAuth !== false: 需要登录
   * - requiresAuth === false: 无需登录
   * - 默认所有页面都需要登录
   */
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  let isLoggedIn = !!localStorage.getItem('user')  // 检查本地存储的用户信息
  
  // 如果没有用户信息，自动设置默认测试用户（开发环境）
  if (!isLoggedIn && process.env.NODE_ENV === 'development') {
    const defaultUser = {
      id: 1,
      username: 'admin',
      name: '管理员',
      avatar: '',
      roles: ['admin']
    }
    localStorage.setItem('user', JSON.stringify(defaultUser))
    isLoggedIn = true
  }
  
  if (requiresAuth && !isLoggedIn) {
    // 需要登录但未登录，重定向到登录页
    next('/login')
  } else if (to.path === '/login' && isLoggedIn) {
    // 已登录用户访问登录页，重定向到首页
    next('/')
  } else {
    // 权限验证通过，允许访问
    next()
  }
})

export default router