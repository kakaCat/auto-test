import { describe, it, expect } from 'vitest'
import { scenarioApi } from '@/api/scenario'

describe('scenarioApi._normalizeQueryParams', () => {
  it('应保留非空 api_id 并归一化其他参数', () => {
    const input = {
      api_id: '123',
      keyword: '',
      status: 'active',
      tags: ['a', '', 'b'],
      createdBy: 'u1',
      createdTimeRange: ['2024-01-01', '2024-01-31'],
      isParametersSaved: true
    }

    const out = scenarioApi._normalizeQueryParams(input)

    // 必填上下文：api_id 存在且未被删除
    expect(out.api_id).toBe('123')

    // 空字符串与空数组被移除
    expect(out.keyword).toBeUndefined()

    // tags 数组转逗号字符串并过滤空项
    expect(out.tags).toBe('a,b')

    // camelCase → snake_case
    expect(out.created_by).toBe('u1')
    expect(out.created_time_range).toEqual(['2024-01-01', '2024-01-31'])
    expect(out.is_parameters_saved).toBe(true)
  })

  it('应移除空值字段，但不自动补全 api_id', () => {
    const input = {
      api_id: '',
      keyword: '',
      tags: []
    }

    const out = scenarioApi._normalizeQueryParams(input)

    // 空值字段被删除（调用方应保证传入有效 api_id）
    expect(out.api_id).toBeUndefined()
    expect(out.keyword).toBeUndefined()
    expect(out.tags).toBeUndefined()
  })
})