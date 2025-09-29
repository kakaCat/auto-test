import { describe, it, expect } from 'vitest'

describe('基本测试', () => {
  it('应该能够运行测试', () => {
    expect(1 + 1).toBe(2)
  })

  it('应该能够测试字符串', () => {
    expect('hello').toBe('hello')
  })

  it('应该能够测试对象', () => {
    const obj = { name: 'test', value: 123 }
    expect(obj.name).toBe('test')
    expect(obj.value).toBe(123)
  })

  it('应该能够测试数组', () => {
    const arr = [1, 2, 3]
    expect(arr).toHaveLength(3)
    expect(arr[0]).toBe(1)
  })
})