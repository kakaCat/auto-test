# 路由与导航规范（Routing & Navigation Standards）

> Status: Stable
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Tags: frontend, standards, routing, navigation

## 适用范围
- 适用于基于 Vue Router 的路由与导航实现，源代码位于 `frontend/src/router/`。

## 基本原则
- 路由命名：`RouteName.ModuleAction`（如 `Api.List`、`Page.Edit`）。
- Path 规范：`/api-management/list`、`/page-management/detail/:id`；参数使用短横线分隔。
- 懒加载：页面使用动态导入；按需代码分割。

## 守卫与权限
- 使用全局前置守卫处理鉴权与重定向；在模块内最小化局部守卫。
- 未授权与未找到：提供统一的 401/404 路由与页面。

## 导航与可达性
- Breadcrumb 与 Tab 导航遵循路由层级；显式命名与互链。
- 保持返回与前进行为一致；避免破坏浏览器导航栈。

## 示例
```ts
import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { name: 'Api.List', path: '/api-management/list', component: () => import('@/views/api-management/List.vue') },
    { name: 'Page.Detail', path: '/page-management/detail/:id', component: () => import('@/views/page-management/Detail.vue') },
    { name: 'NotFound', path: '/:pathMatch(.*)*', component: () => import('@/views/NotFound.vue') }
  ]
})
```

---
本规范统一路由命名与导航行为，提升一致性与可维护性。