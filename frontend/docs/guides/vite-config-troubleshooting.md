# Vite 配置故障排除指南

本文档记录了 Vite 开发环境中遇到的配置问题及其解决方案。

## SPA 路由问题

### 问题描述
在开发环境中，直接访问前端路由（如 `/api-management/list`、`/workflow-orchestration/list`）时返回 404 错误，或者刷新页面时出现 404 错误。

### 问题现象
- 通过应用内导航可以正常访问页面
- 直接在浏览器地址栏输入路由地址返回 404
- 刷新页面时出现 404 错误
- 错误响应来自后端服务器而非前端

### 根本原因
Vite 代理配置过于宽泛，将前端路由错误地代理到后端：

```javascript
// 错误的配置
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true
  }
}
```

这种配置会将所有以 `/api` 开头的请求都代理到后端，包括前端路由如：
- `/api-management/list`
- `/workflow-orchestration/list`

### 解决方案

修改 `vite.config.js` 中的代理配置，使用更精确的正则表达式：

```javascript
// 正确的配置
proxy: {
  // 只代理以 /api/ 开头且不包含 -management 或 -orchestration 的请求
  '^/api/(?!.*(-management|-orchestration))': {
    target: targetBase,
    changeOrigin: true
  }
}
```

### 配置说明

1. **正则表达式解析**：
   - `^/api/` - 匹配以 `/api/` 开头的路径
   - `(?!.*(-management|-orchestration))` - 负向前瞻，排除包含 `-management` 或 `-orchestration` 的路径

2. **匹配示例**：
   - ✅ `/api/systems/v1/` - 会被代理到后端
   - ✅ `/api/health` - 会被代理到后端
   - ❌ `/api-management/list` - 不会被代理，由前端处理
   - ❌ `/workflow-orchestration/list` - 不会被代理，由前端处理

### 验证方法

1. **测试前端路由**：
   ```bash
   curl -I http://localhost:5173/api-management/list
   # 应该返回 200 OK，Content-Type: text/html
   ```

2. **测试 API 代理**：
   ```bash
   curl http://localhost:5173/api/systems/v1/
   # 应该返回后端 JSON 数据
   ```

### 最佳实践

1. **精确匹配**：代理配置应该尽可能精确，避免误匹配前端路由
2. **命名规范**：前端路由和后端 API 路径应该有明确的区分
3. **测试验证**：修改代理配置后，务必测试前端路由和 API 代理都正常工作

### 相关文件
- `frontend/vite.config.js` - Vite 配置文件
- `frontend/src/router/index.js` - 前端路由配置

### 注意事项
- 修改 Vite 配置后需要重启开发服务器
- 确保前端路由命名不与后端 API 路径冲突
- 在生产环境中，需要配置 Web 服务器（如 Nginx）的 fallback 规则