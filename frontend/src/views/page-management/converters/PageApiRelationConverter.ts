/**
 * PageApiRelationConverter
 * 将后端返回的“页面-API关联列表”转换为前端可执行的 ApiConfigItem[] / PageApiConfig
 * 静态工具类，遵循防腐层设计原则与命名约定
 */

import type { ApiConfigItem, PageApiConfig } from '@/views/page-management/types/page-config'

export class PageApiRelationConverter {
  /**
   * 将原始行数据转换为 ApiConfigItem 列表
   * - 字段推断：id/relation_id/api_id、api_name/name、api_method/method、api_path/path、order
   * - 统一默认值：callType=serial、params 空对象、response.extract 空对象、error 空对象
   */
  static toApiConfigItems(rows: unknown[]): ApiConfigItem[] {
    if (!Array.isArray(rows)) return []
    return rows.map((row: unknown, idx: number) => {
      const r = row as Record<string, unknown>
      const id = String((r as any).id ?? (r as any).relation_id ?? (r as any).api_id ?? `api-${idx + 1}`)
      const name = String((r as any).api_name ?? (r as any).name ?? `API ${idx + 1}`)
      const method = String((r as any).api_method ?? (r as any).method ?? 'GET').toUpperCase()
      const path = String((r as any).api_path ?? (r as any).path ?? '')
      const order = typeof (r as any).order === 'number' ? ((r as any).order as number) : (idx + 1)
      const apiId = Number((r as any).api_id ?? (r as any).id ?? idx + 1)

      const item: ApiConfigItem = {
        id,
        apiId,
        name,
        method,
        path,
        callType: 'serial',
        order,
        params: { static: {}, dynamic: {} },
        response: { extract: {} },
        error: {}
      }
      return item
    })
  }

  /**
   * 包装为 PageApiConfig
   */
  static toPageApiConfig(rows: unknown[]): PageApiConfig {
    const apis = this.toApiConfigItems(rows)
    const cfg: PageApiConfig = {
      systemId: null,
      moduleId: null,
      apis,
      flowChart: { nodes: [], edges: [] }
    }
    return cfg
  }
}