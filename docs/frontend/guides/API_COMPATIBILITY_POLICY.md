# 前端 API 重构兼容性策略与迁移指南

> 适用范围：`frontend/src/api/` 重构期间及过渡期，面向开发、测试与文档维护人员。

## 目标与原则
- 保持行为兼容：重构不应影响现有页面的功能与交互表现。
- 渐进式迁移：允许新旧两套调用方式并存，通过特性开关控制。
- 可回滚：出现风险时，能够快速切回旧路径且不影响用户。
- 可观测性：关键兼容点具备日志与监控，便于定位问题。

## 兼容模式与特性开关
- 运行时开关：`VITE_API_COMPAT_MODE`（`0` 关闭兼容、`1` 开启兼容，默认 `1`）。
- 代码层开关：`ApiConfig.compatibility.enabled: boolean`，用于细粒度控制模块级兼容。
- 使用建议：
  - 开发/测试环境：开启兼容（`1`），便于对比新旧路径行为。
  - 生产逐步灰度：先开启兼容，完成阶段性迁移后再关闭。

```ts
// 示例：request.ts 中的兼容模式注入（伪代码）
export const compatMode = import.meta.env.VITE_API_COMPAT_MODE === '1';

export function normalizeError(err: unknown): ApiError {
  // 统一错误模型，兼容旧结构
  if (err && typeof err === 'object' && 'code' in (err as any)) {
    return { code: (err as any).code ?? 'UNKNOWN', message: (err as any).message ?? '未知错误' };
  }
  return { code: 'UNKNOWN', message: err instanceof Error ? err.message : '未知错误' };
}
```

## 错误与返回结构兼容
- 错误模型：统一为 `ApiError { code: string; message: string; details?: unknown }`，旧代码通过 `normalizeError()` 适配。
- 返回模型：统一为 `Result<T> { data: T; success: boolean; error?: ApiError }`，提供 `unwrapResult()` 以兼容旧直接 `data` 访问。
- 旧拦截器兼容：保持原有拦截器执行顺序，新增兼容拦截器作为末端适配层。

```ts
// 示例：Result 兼容工具
export function unwrapResult<T>(result: Result<T>): T {
  if (!result.success) throw new Error(result.error?.message ?? '请求失败');
  return result.data;
}
```

## API 调用路径兼容矩阵
- 统一入口：鼓励使用 `BaseApi + apiHandler`，但兼容保留直接 `request.*` 调用。
- 处置策略：
  - `request.get/post/...`：保留；标注 `@deprecated`；内部转发到新管道（兼容模式开启时）。
  - `BaseApi`：继续支持；错误与返回结构按新模型适配。
  - 领域 API（`module-api.ts` 等）：移除冗余 `try/catch`，依赖统一错误处理；但兼容模式下保留旧方法签名。

```ts
// 示例：旧 request.post 的兼容转发（伪代码）
export async function post(url: string, payload: unknown, options?: RequestOptions): Promise<any> {
  if (compatMode) {
    const res = await apiHandler.post(url, payload, options);
    return options?.raw ? res : res.data; // 兼容旧调用直接访问 data
  }
  // 非兼容模式，直接走全新路径/返回 Result<T>
  return apiHandler.post(url, payload, options);
}
```

## 渐进式迁移流程
- Phase 0（接入兼容层）
  - 引入 `compatMode`、`normalizeError`、`unwrapResult`。
  - 在 `request.ts` 内部增加兼容转发逻辑，不改调用方代码。
- Phase 1（替换直接 request 调用）
  - 将 `requirement-management.ts`、`page-management.ts`、`api-management.ts` 的直接 `request.*` 调用替换为 `BaseApi/apiHandler`。
  - 保留旧方法签名，返回结构通过兼容工具适配。
- Phase 2（清理冗余与规范）
  - 清理领域 API 中的重复 `try/catch` 与自定义错误包装。
  - 明确 `skipErrorHandler` 只用于特殊场景（如导出、心跳、幂等批量）。
- Phase 3（关闭兼容）
  - 在稳定版本灰度后，将 `VITE_API_COMPAT_MODE` 切换为 `0`，并移除临时兼容分支。

## 验收标准（Compatibility Acceptance Criteria）
- 行为一致：页面功能、交互与文案无差异；关键路径（登录、列表、详情、保存、导出）全部通过。
- 错误一致：相同异常场景下，错误提示与日志码保持一致或明确映射关系。
- 可回滚：切换 `VITE_API_COMPAT_MODE` 能在 1 分钟内恢复旧路径；无缓存/状态残留问题。
- 可观测：错误模型、返回结构转换点具备日志埋点；监控面板可对比新旧调用的失败率与时延。

## 风险与缓解
- 文件上传/下载：继续使用旧的 `request.upload/download`；在 Phase 1 后评估统一改造时机。
- 批量/并发：在 `apiHandler` 保留批量接口与并发控制；避免行为改变。
- 类型复杂度：通过 `Converter`（静态方法）统一数据转换，避免在调用方混杂转换逻辑。

## 回滚策略
- 即时回滚：将 `VITE_API_COMPAT_MODE=1`，并重启前端服务。
- 文档同步：在 `CHANGELOG.md` 标注关闭兼容的版本与影响范围。
- 代码清理：回滚后保留兼容工具，待问题定位完成再进行差异消除。

## 时间线建议
- T+0：引入兼容层与特性开关（Phase 0）。
- T+3 天：完成主要模块替换（Phase 1），开始灰度观察。
- T+7 天：清理冗余并统一规范（Phase 2）。
- T+14 天：根据监控结果关闭兼容（Phase 3）。

## 测试与文档映射
- 测试用例：在 `tests/test_frontend_api_calls.js` 增加新旧路径对比用例与断言。
- 文档更新：
  - `docs/frontend/README.md` 添加本指南链接。
  - 在 `DOCUMENT_MAPPING_GUIDE.md` 标注 UI/交互不变但 API 层实现调整的映射策略与检查清单。