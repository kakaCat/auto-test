import { describe, it, expect } from 'vitest'
import { requirementApi } from '@/api/requirement-management'

describe('requirementApi._normalizeQueryParams', () => {
  it('归一化常见查询参数：时间范围、分页、启用过滤', () => {
    const input = {
      pageSize: 50,
      createdTimeRange: ['2024-01-01', '2024-01-31'],
      updatedTimeRange: ['2024-02-01', '2024-02-28'],
      enabledOnly: true
    }

    const out = requirementApi._normalizeQueryParams(input)
    expect(out.page_size).toBe(50)
    expect(out.created_time_range).toBe('2024-01-01,2024-01-31')
    expect(out.updated_time_range).toBe('2024-02-01,2024-02-28')
    expect(out.enabled_only).toBe(true)

    // 原字段被移除
    expect(out.pageSize).toBeUndefined()
    expect(out.createdTimeRange).toBeUndefined()
    expect(out.updatedTimeRange).toBeUndefined()
    expect(out.enabledOnly).toBeUndefined()
  })
})