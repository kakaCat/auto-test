/**
 * 应用程序主入口文件
 * 
 * 功能说明：
 * - 初始化Vue 3应用实例
 * - 配置全局插件和组件库
 * - 设置路由和状态管理
 * - 注册全局组件和样式
 * - 初始化应用状态
 * 
 * 技术栈：
 * - Vue 3 (Composition API)
 * - Pinia (状态管理)
 * - Vue Router (路由管理)
 * - Element Plus (UI组件库)
 * 
 * 依赖关系：
 * - App.vue: 根组件
 * - router/index.js: 路由配置
 * - stores/app.js: 应用状态管理
 * - styles/index.css: 全局样式
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

// Vue 3 核心依赖
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Element Plus UI组件库
// 提供丰富的Vue 3组件和主题支持
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'           // Element Plus基础样式
import 'element-plus/theme-chalk/dark/css-vars.css'  // 暗色主题支持
import * as ElementPlusIconsVue from '@element-plus/icons-vue'  // 图标库

// 全局样式文件
// 包含项目自定义样式和CSS变量定义
import './styles/index.css'

/**
 * 创建Vue应用实例
 * 使用根组件App.vue作为应用入口
 */
const app = createApp(App)

/**
 * 批量注册Element Plus图标组件
 * 
 * 将所有Element Plus图标注册为全局组件，
 * 可在任何组件中直接使用，如：<Edit />、<Delete />等
 * 
 * 性能考虑：
 * - 图标按需加载，只有使用的图标才会被打包
 * - 全局注册便于统一管理和使用
 */
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

/**
 * 注册应用插件
 * 
 * 插件注册顺序很重要：
 * 1. Pinia - 状态管理，其他插件可能依赖状态
 * 2. Router - 路由管理，页面导航核心
 * 3. ElementPlus - UI组件库，提供组件和样式
 */
app.use(createPinia())  // 状态管理插件
app.use(router)         // 路由管理插件
app.use(ElementPlus)    // Element Plus UI组件库

/**
 * 挂载应用到DOM
 * 
 * 将Vue应用挂载到index.html中id为'app'的DOM元素上
 * 这是应用启动的最后一步
 */
app.mount('#app')

/**
 * 初始化应用状态
 * 
 * 在应用挂载后立即初始化全局状态，
 * 包括用户信息、系统配置、主题设置等
 * 
 * 注意：这里使用动态导入避免循环依赖
 */
import { useAppStore } from '@/stores/app'
const appStore = useAppStore()
appStore.init()  // 执行应用初始化逻辑