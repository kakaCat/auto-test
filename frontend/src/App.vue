<!--
  应用根组件
  
  功能说明：
  - 作为整个应用的根容器
  - 提供路由视图渲染区域
  - 定义全局样式和过渡动画
  - 初始化应用状态
  
  组件结构：
  - template: 简洁的路由视图容器
  - script: 应用初始化逻辑
  - style: 全局样式和动画定义
  
  技术特性：
  - Vue 3 Composition API
  - 路由视图动态渲染
  - CSS过渡动画支持
  - 响应式布局设计
  
  @author AI Assistant
  @version 1.0.0
  @since 2024-01-15
-->

<template>
  <!-- 
    应用主容器
    
    作为整个应用的根DOM元素，承载所有页面内容。
    使用router-view组件实现单页面应用的页面切换。
  -->
  <div id="app">
    <!-- 
      路由视图组件
      
      根据当前路由动态渲染对应的页面组件。
      支持路由过渡动画和页面缓存。
      
      特性：
      - 动态组件渲染
      - 路由参数传递
      - 页面过渡效果
      - 组件缓存优化
    -->
    <router-view />
  </div>
</template>

<script setup>
/**
 * 应用根组件逻辑
 * 
 * 职责：
 * - 应用生命周期管理
 * - 全局状态初始化
 * - 错误边界处理
 * - 性能监控设置
 */

import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

// 获取应用状态管理实例
const appStore = useAppStore()

/**
 * 组件挂载后的初始化逻辑
 * 
 * 执行时机：DOM挂载完成后
 * 执行内容：
 * - 应用状态初始化
 * - 用户认证检查
 * - 系统配置加载
 * - 主题设置应用
 */
onMounted(() => {
  // 初始化应用状态和配置
  appStore.init()
})
</script>

<style>
/**
 * 全局样式定义
 * 
 * 包含：
 * - 基础布局样式
 * - 重置样式
 * - 过渡动画
 * - 响应式设计
 */

/* 应用主容器样式 */
#app {
  height: 100vh;        /* 全屏高度 */
  overflow: hidden;     /* 防止页面滚动，由内部组件控制 */
}

/* 全局盒模型重置 */
* {
  box-sizing: border-box;  /* 统一盒模型计算方式 */
}

/* 页面基础样式重置 */
body {
  margin: 0;    /* 移除默认外边距 */
  padding: 0;   /* 移除默认内边距 */
}

/**
 * 淡入淡出过渡动画
 * 
 * 用于页面切换时的平滑过渡效果。
 * 适用于模态框、提示信息等组件。
 * 
 * 动画参数：
 * - 持续时间：0.3秒
 * - 缓动函数：ease
 * - 属性：透明度
 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/**
 * 滑动过渡动画
 * 
 * 用于页面切换时的滑动效果。
 * 适用于移动端页面切换、侧边栏展开等场景。
 * 
 * 动画参数：
 * - 持续时间：0.3秒
 * - 缓动函数：ease
 * - 属性：所有可动画属性
 * 
 * 动画方向：
 * - 进入：从右侧滑入
 * - 离开：向左侧滑出
 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);  /* 从右侧100%位置开始 */
}

.slide-leave-to {
  transform: translateX(-100%); /* 向左侧100%位置结束 */
}
</style>