<!--
  应用主布局组件
  
  功能说明：
  - 提供应用的整体布局结构
  - 包含侧边栏导航、顶部导航栏、主内容区域
  - 支持响应式设计和主题切换
  - 集成用户信息和系统状态管理
  
  组件结构：
  - 侧边栏：导航菜单、Logo、折叠功能
  - 顶部栏：面包屑、主题切换、用户信息
  - 内容区：路由视图、页面过渡动画
  - 全局遮罩：加载状态指示
  
  技术特性：
  - 响应式布局适配移动端
  - 动态菜单生成
  - 状态持久化
  - 无障碍访问支持
  
  @author AI Assistant
  @version 1.0.0
  @since 2024
-->
<template>
  <div class="app-layout">
    <!-- 
      侧边栏导航区域
      - 支持折叠/展开切换
      - 动态菜单渲染
      - 路由状态同步
    -->
    <div 
      class="sidebar" 
      :class="{ 'sidebar-collapsed': appStore.sidebarCollapsed }"
    >
      <div class="sidebar-header">
        <div class="logo">
          <el-icon class="logo-icon">
            <MagicStick />
          </el-icon>
          <span v-show="!appStore.sidebarCollapsed" class="logo-text">
            AI自动化测试
          </span>
        </div>
      </div>
      
      <div class="sidebar-content">
        <el-menu
          :default-active="$route.path"
          :collapse="appStore.sidebarCollapsed"
          :unique-opened="true"
          router
          class="sidebar-menu"
        >
          <template v-for="route in menuRoutes" :key="route.path">
            <el-sub-menu 
              v-if="route.children && route.children.length > 1" 
              :index="route.path"
            >
              <template #title>
                <el-icon>
                  <component :is="route.meta?.icon || 'Menu'" />
                </el-icon>
                <span>{{ route.meta?.title }}</span>
              </template>
              
              <el-menu-item
                v-for="child in route.children.filter(item => !item.meta?.hidden)"
                :key="child.path"
                :index="child.path.startsWith('/') ? child.path : `${route.path}/${child.path}`"
              >
                <el-icon>
                  <component :is="child.meta?.icon || 'Document'" />
                </el-icon>
                <span>{{ child.meta?.title }}</span>
              </el-menu-item>
            </el-sub-menu>
            
            <el-menu-item 
              v-else-if="!route.meta?.hidden"
              :index="route.children?.[0]?.path || route.path"
            >
              <el-icon>
                <component :is="route.meta?.icon || 'Menu'" />
              </el-icon>
              <span>{{ route.meta?.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>
    </div>
    
    <!-- 
      主内容区域
      - 包含顶部导航栏和页面内容
      - 自适应剩余空间
      - 垂直布局结构
    -->
    <div class="main-container">
      <!-- 
        顶部导航栏
        - 侧边栏切换按钮
        - 面包屑导航
        - 主题切换和用户菜单
      -->
      <div class="navbar">
        <div class="navbar-left">
          <el-button
            type="text"
            @click="appStore.toggleSidebar"
            class="sidebar-toggle"
          >
            <el-icon>
              <Expand v-if="appStore.sidebarCollapsed" />
              <Fold v-else />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="navbar-right">
          <el-button
            type="text"
            @click="appStore.toggleTheme"
            class="theme-toggle"
          >
            <el-icon>
              <Sunny v-if="appStore.isDark" />
              <Moon v-else />
            </el-icon>
          </el-button>
          
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="appStore.user?.avatar">
                {{ appStore.user?.name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ appStore.user?.name || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 
        页面内容区域
        - 路由视图渲染
        - 页面切换动画
        - 滚动容器
      -->
      <div class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
    
    <!-- 
      全局加载遮罩
      - 显示全局加载状态
      - 阻止用户交互
      - 半透明背景
    -->
    <div v-if="appStore.loading" class="global-loading">
      <el-loading-directive />
    </div>
  </div>
</template>

<!--
  组件逻辑部分
  
  主要功能：
  - 菜单路由动态生成
  - 面包屑导航计算
  - 用户操作处理
  - 状态监听和同步
  
  响应式数据：
  - menuRoutes: 过滤后的菜单路由
  - breadcrumbs: 当前页面面包屑
  - userAvatar: 用户头像URL
  
  事件处理：
  - handleUserCommand: 用户下拉菜单操作
  - handleLogout: 退出登录处理
-->
<script setup>
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'

// 路由和状态管理实例
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

/**
 * 菜单路由计算属性
 * 
 * 功能说明：
 * - 从路由配置中过滤出需要显示在菜单中的路由
 * - 排除根路径、隐藏路由和布局组件
 * - 支持动态菜单生成
 * 
 * 过滤条件：
 * - 非根路径（'/'）
 * - 未标记为隐藏（meta.hidden !== true）
 * - 非布局组件（component.name !== 'Layout'）
 */
const menuRoutes = computed(() => {
  return router.getRoutes().filter(route => 
    route.path !== '/' && 
    !route.meta?.hidden && 
    route.component?.name !== 'Layout'
  )
})

/**
 * 面包屑导航计算属性
 * 
 * 功能说明：
 * - 根据当前路由匹配的路径生成面包屑
 * - 提取路由元信息中的标题
 * - 构建导航路径数组
 * 
 * 数据结构：
 * - title: 页面标题
 * - path: 路由路径
 */
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  const breadcrumbs = []
  
  matched.forEach(item => {
    if (item.meta?.title) {
      breadcrumbs.push({
        title: item.meta.title,
        path: item.path
      })
    }
  })
  
  return breadcrumbs
})

/**
 * 用户头像计算属性
 * 
 * 功能说明：
 * - 获取用户头像URL
 * - 提供默认值处理
 * - 支持头像缓存
 */
const userAvatar = computed(() => {
  return appStore.userInfo?.avatar || ''
})

/**
 * 处理用户下拉菜单命令
 * 
 * 功能说明：
 * - 处理用户操作菜单的各种命令
 * - 支持个人中心、系统设置、退出登录
 * - 提供用户反馈和确认机制
 * 
 * @param {string} command - 菜单命令类型
 */
const handleUserCommand = (command) => {
  switch (command) {
  case 'profile':
    ElMessage.info('个人中心功能开发中...')
    break
  case 'settings':
    ElMessage.info('系统设置功能开发中...')
    break
  case 'logout':
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      appStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {
      // 用户取消
    })
    break
  }
}

/**
 * 退出登录处理函数
 * 
 * 功能说明：
 * - 清除用户登录状态
 * - 显示退出成功提示
 * - 重定向到登录页面
 * - 清理本地存储数据
 */
const handleLogout = () => {
  appStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

/**
 * 监听侧边栏状态变化
 * 
 * 功能说明：
 * - 监听侧边栏折叠状态变化
 * - 自动保存状态到本地存储
 * - 确保状态持久化
 */
watch(
  () => appStore.sidebarCollapsed,
  () => {
    appStore.saveSidebarState()
  }
)
</script>

<!--
  组件样式定义
  
  样式特性：
  - 响应式布局设计
  - 主题切换支持
  - 动画过渡效果
  - 移动端适配
  
  布局结构：
  - Flexbox 水平布局
  - 侧边栏固定宽度
  - 主内容区域自适应
  - 顶部导航栏固定高度
  
  主题支持：
  - CSS 变量定义
  - 明暗主题切换
  - 颜色动态调整
-->
<style scoped>
/**
 * 应用主布局容器
 * - 全屏高度布局
 * - 水平 Flexbox 布局
 * - 背景色和字体设置
 */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: var(--bg-color-overlay);
  border-right: 1px solid var(--border-color-lighter);
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color-lighter);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-content {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  height: 48px;
  line-height: 48px;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.navbar {
  height: 60px;
  background: var(--bg-color-overlay);
  border-bottom: 1px solid var(--border-color-lighter);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sidebar-toggle {
  padding: 8px;
  font-size: 18px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-toggle {
  padding: 8px;
  font-size: 18px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.user-info:hover {
  background-color: var(--fill-color-light);
}

.username {
  font-size: 14px;
  color: var(--text-color-regular);
}

.page-content {
  flex: 1;
  overflow: auto;
  background: var(--bg-color-page);
}

.global-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dark .global-loading {
  background: rgba(0, 0, 0, 0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar:not(.sidebar-collapsed) {
    transform: translateX(0);
  }
  
  .main-container {
    width: 100%;
  }
  
  .navbar-left .el-breadcrumb {
    display: none;
  }
}
</style>