# API 管理保存失败出现“2 条日志/重复提示”的根因与修复

## 现象
- 点击保存（创建/更新）接口失败时，控制台会看到两条错误日志；页面也可能弹出两次错误提示。

## 根因
1) 全局 Axios 拦截器在业务失败（`success === false`）和 HTTP 异常时都会默认 `ElMessage.error` 并 `logger.error`。
2) 业务层（apiHandler / unified-api / 页面 index.vue 的 catch）又进行了一次错误提示与日志打印。
3) 两处同时提示与记录，形成重复。

## 修复策略
- 采用“上层统一处理”的策略：当调用方（apiHandler/业务层/页面）准备自行处理错误时，通过 `config.skipErrorHandler = true` 告知全局拦截器跳过默认提示与日志。

## 代码改动
- frontend/src/utils/apiHandler.ts
  - 为 `get/post/put/patch/delete` 封装统一传入 `{ skipErrorHandler: true }`，由 apiHandler/业务层自行决定是否弹窗与日志。
- frontend/src/api/unified-api.ts
  - API 管理域（api-interfaces）相关方法统一传入 `{ skipErrorHandler: true }`，避免与页面层重复提示。
- frontend/src/utils/request.ts
  - 在请求/响应错误拦截器中，检测到 `skipErrorHandler: true` 时，不再 `ElMessage.error` 也不再 `logger.error`，彻底避免重复。

## 验证
- 保存失败时只出现一次错误提示与一次错误日志。
- 其他未显式传入 `skipErrorHandler: true` 的调用仍使用全局默认提示策略。

## 备注
- 如果页面层需要更细粒度的提示（如根据字段/状态码定制消息），保持 `skipErrorHandler: true` 并在 `catch` 中自定义提示即可。