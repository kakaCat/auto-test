/**
 * 应用全局状态管理
 * 
 * 功能说明：
 * - 管理应用的全局状态和配置
 * - 处理用户认证和会话管理
 * - 控制UI主题和布局状态
 * - 响应式设备类型检测
 * - 本地存储状态持久化
 * 
 * 状态分类：
 * - UI状态：侧边栏、主题、加载状态
 * - 用户状态：登录信息、权限数据
 * - 设备状态：屏幕尺寸、设备类型
 * 
 * 技术特性：
 * - Pinia状态管理
 * - Composition API
 * - 响应式状态更新
 * - 本地存储持久化
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024-01-15
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 应用状态管理Store
 * 
 * 使用Composition API风格定义状态管理逻辑，
 * 提供响应式状态和操作方法。
 */
export const useAppStore = defineStore('app', () => {
  /**
   * 响应式状态定义
   * 
   * 状态说明：
   * - sidebarCollapsed: 侧边栏折叠状态
   * - theme: 应用主题（light/dark）
   * - loading: 全局加载状态
   * - device: 设备类型（desktop/tablet/mobile）
   * - user: 当前登录用户信息
   */
  const sidebarCollapsed = ref(false)  // 侧边栏是否折叠
  const theme = ref('light')           // 当前主题模式
  const loading = ref(false)           // 全局加载状态
  const device = ref('desktop')        // 设备类型
  const user = ref(null)               // 用户信息
  
  /**
   * 计算属性定义
   * 
   * 基于基础状态计算派生状态，
   * 提供便捷的状态访问接口。
   */
  const isDark = computed(() => theme.value === 'dark')    // 是否为暗色主题
  const isLoggedIn = computed(() => !!user.value)         // 是否已登录
  
  /**
   * 状态操作方法
   * 
   * 提供状态修改的标准接口，
   * 确保状态变更的一致性和可追踪性。
   */
  
  /**
   * 切换侧边栏折叠状态
   * 
   * 用于响应用户点击侧边栏折叠按钮的操作。
   * 自动保存状态到本地存储。
   */
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    saveSidebarState()  // 保存状态到本地存储
  }
  
  /**
   * 切换主题模式
   * 
   * 在明亮和暗色主题之间切换。
   * 自动更新DOM类名和本地存储。
   */
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    updateTheme()
  }
  
  /**
   * 设置指定主题
   * 
   * @param {string} newTheme - 主题名称（'light' | 'dark'）
   * 
   * 用于程序化设置主题，如从配置文件加载主题设置。
   */
  const setTheme = (newTheme) => {
    theme.value = newTheme
    updateTheme()
  }
  
  /**
   * 设置全局加载状态
   * 
   * @param {boolean} status - 加载状态
   * 
   * 用于显示/隐藏全局加载指示器，
   * 通常在API请求期间使用。
   */
  const setLoading = (status) => {
    loading.value = status
  }
  
  /**
   * 设置设备类型
   * 
   * @param {string} deviceType - 设备类型（'desktop' | 'tablet' | 'mobile'）
   * 
   * 根据屏幕尺寸自动检测或手动设置设备类型，
   * 用于响应式布局调整。
   */
  const setDevice = (deviceType) => {
    device.value = deviceType
  }
  
  /**
   * 设置用户信息
   * 
   * @param {Object|null} userData - 用户数据对象
   * 
   * 功能：
   * - 更新当前用户状态
   * - 同步保存到本地存储
   * - 支持清空用户信息（传入null）
   * 
   * 数据结构：
   * {
   *   id: number,
   *   username: string,
   *   email: string,
   *   avatar: string,
   *   permissions: string[]
   * }
   */
  const setUser = (userData) => {
    user.value = userData
    // 同步到本地存储
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  /**
   * 用户登出
   * 
   * 功能：
   * - 清空用户状态
   * - 清除本地存储的用户信息
   * - 清除认证令牌
   * - 重置相关权限状态
   * 
   * 安全考虑：
   * - 彻底清除敏感信息
   * - 防止信息泄露
   */
  const logout = () => {
    user.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    // 可以在这里添加其他清理逻辑
  }

  /**
   * 保存侧边栏状态到本地存储
   * 
   * 将当前侧边栏折叠状态持久化到localStorage，
   * 确保用户刷新页面后状态保持一致。
   */
  const saveSidebarState = () => {
    localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed.value))
  }
  
  /**
   * 更新主题样式
   * 
   * 功能：
   * - 更新HTML根元素的CSS类名
   * - 触发CSS主题变量切换
   * - 保存主题设置到本地存储
   * 
   * 实现原理：
   * - 通过添加/移除'dark'类名控制主题
   * - CSS变量自动响应类名变化
   * - 支持Element Plus暗色主题
   */
  const updateTheme = () => {
    const html = document.documentElement
    if (theme.value === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
    // 持久化主题设置
    localStorage.setItem('theme', theme.value)
  }
  
  /**
   * 应用初始化方法
   * 
   * 执行时机：应用启动时调用
   * 
   * 初始化流程：
   * 1. 恢复用户偏好设置（主题、侧边栏状态）
   * 2. 恢复用户登录状态
   * 3. 检测设备类型并设置响应式布局
   * 4. 注册窗口大小变化监听器
   * 
   * 错误处理：
   * - 本地存储数据损坏时自动清理
   * - 提供降级方案确保应用正常运行
   */
  const init = () => {
    /**
     * 恢复主题设置
     * 
     * 从localStorage读取用户的主题偏好，
     * 如果没有保存的设置则使用默认的light主题。
     */
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      setTheme(savedTheme)
    }
    
    /**
     * 恢复侧边栏状态
     * 
     * 从localStorage读取侧边栏折叠状态，
     * 包含错误处理确保数据格式正确。
     */
    const savedSidebarState = localStorage.getItem('sidebarCollapsed')
    if (savedSidebarState) {
      try {
        sidebarCollapsed.value = JSON.parse(savedSidebarState)
      } catch (error) {
        console.error('解析侧边栏状态失败:', error)
        localStorage.removeItem('sidebarCollapsed')
      }
    }
    
    /**
     * 恢复用户登录状态
     * 
     * 从localStorage读取用户信息，
     * 实现页面刷新后的登录状态保持。
     * 
     * 安全考虑：
     * - 验证数据格式完整性
     * - 损坏数据自动清理
     */
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('user')
      }
    }
    
    /**
     * 设备类型检测和响应式布局
     * 
     * 根据窗口宽度自动检测设备类型，
     * 并调整相应的UI布局和交互行为。
     * 
     * 断点设置：
     * - mobile: < 768px
     * - tablet: 768px - 1024px
     * - desktop: >= 1024px
     * 
     * 响应式行为：
     * - 移动端自动折叠侧边栏
     * - 平板和桌面端保持用户设置
     */
    const checkDevice = () => {
      const width = window.innerWidth
      if (width < 768) {
        setDevice('mobile')
        sidebarCollapsed.value = true  // 移动端强制折叠侧边栏
      } else if (width < 1024) {
        setDevice('tablet')
      } else {
        setDevice('desktop')
      }
    }
    
    // 初始检测
    checkDevice()
    
    // 监听窗口大小变化，实现动态响应式布局
    window.addEventListener('resize', checkDevice)
  }
  
  return {
    // 状态
    sidebarCollapsed,
    theme,
    loading,
    device,
    user,
    
    // 计算属性
    isDark,
    isLoggedIn,
    
    // 方法
    toggleSidebar,
    toggleTheme,
    setTheme,
    setLoading,
    setDevice,
    setUser,
    logout,
    saveSidebarState,
    init
  }
})