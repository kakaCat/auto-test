# 类型定义文档（占位）

> 说明：记录 API 层暴露与消费的 TypeScript 类型定义，统一数据结构与约定。当前为占位版本，确保导航链接有效、结构一致。

## 编写原则
- 复杂对象优先使用 `interface`，避免 `any`，必要时使用 `unknown`
- 使用判别联合处理复杂分支：如 `type: 'success' | 'error'`
- 所有错误通过 `Error` 对象承载明确消息：`new Error('具体消息')`
- 文件命名小写短横线：如 `task-response.ts`

## 基础约定
```ts
// 仅为样例，实际请在 src/api/types 下维护
export interface WebResponse<T> {
  code: string; // 业务码
  message: string; // 可读信息
  data: T; // 负载
}

export interface PageQuery {
  page: number;
  pageSize: number;
}

export interface PageResult<T> {
  total: number;
  list: T[];
}
```

## 领域示例
```ts
export interface TaskVO {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'done' | 'failed';
}

export interface TaskListResponse extends PageResult<TaskVO> {}
```

## 校验规则
- Rule 层进行参数校验与业务规则校验
- Converter 层进行字段映射与格式标准化

---
维护者：前端团队
最后更新：占位创建