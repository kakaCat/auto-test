import { describe, it, expect } from 'vitest'

// 模拟 JSON 工具函数
const JsonUtils = {
  // 验证 JSON 格式
  validateJson(jsonString) {
    if (!jsonString || jsonString.trim() === '') {
      return true // 空字符串视为有效
    }
    
    try {
      JSON.parse(jsonString)
      return true
    } catch (error) {
      return false
    }
  },

  // 推断数据类型
  inferType(value) {
    if (value === null) return 'null'
    if (Array.isArray(value)) return 'array'
    if (typeof value === 'object') return 'object'
    return typeof value
  },

  // 转换 JSON 为参数列表
  convertJsonToParams(jsonData, parentKey = '', level = 0, parentId = null) {
    const params = []
    
    if (typeof jsonData !== 'object' || jsonData === null) {
      return params
    }

    Object.keys(jsonData).forEach(key => {
      const value = jsonData[key]
      const paramName = parentKey ? `${parentKey}.${key}` : key
      const paramId = this.generateId()
      
      const param = {
        id: paramId,
        name: key,
        type: this.inferType(value),
        required: true,
        level: level,
        parentId: parentId,
        example: value
      }
      
      params.push(param)
      
      // 递归处理嵌套对象
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        const nestedParams = this.convertJsonToParams(value, paramName, level + 1, paramId)
        params.push(...nestedParams)
      }
    })
    
    return params
  },

  // 生成唯一 ID
  generateId() {
    return 'param_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
  },

  // 计算 JSON 统计信息
  calculateJsonStats(obj) {
    let nodeCount = 0
    let maxDepth = 0
    
    function traverse(data, depth = 0) {
      if (data === null || typeof data !== 'object') {
        nodeCount++
        maxDepth = Math.max(maxDepth, depth)
        return
      }
      
      if (Array.isArray(data)) {
        nodeCount++
        maxDepth = Math.max(maxDepth, depth)
        data.forEach(item => traverse(item, depth + 1))
      } else {
        nodeCount++
        maxDepth = Math.max(maxDepth, depth)
        Object.values(data).forEach(value => traverse(value, depth + 1))
      }
    }
    
    traverse(obj)
    
    return {
      nodeCount,
      maxDepth,
      isValid: true
    }
  },

  // 获取数组风格描述
  getArrayStyleDescription(style) {
    const descriptions = {
      'index': '使用索引风格 (items[0], items[1])',
      'item': '使用项目风格 (items.item)',
      'expand': '展开所有数组项'
    }
    return descriptions[style] || '未知风格'
  }
}

describe('JSON 工具函数测试', () => {
  describe('JSON 验证', () => {
    it('应该验证有效的 JSON', () => {
      expect(JsonUtils.validateJson('{"name": "test"}')).toBe(true)
      expect(JsonUtils.validateJson('{"age": 30, "active": true}')).toBe(true)
      expect(JsonUtils.validateJson('[]')).toBe(true)
      expect(JsonUtils.validateJson('null')).toBe(true)
    })

    it('应该检测无效的 JSON', () => {
      expect(JsonUtils.validateJson('{"name": "test"')).toBe(false)
      expect(JsonUtils.validateJson('{"name": }')).toBe(false)
      expect(JsonUtils.validateJson('invalid json')).toBe(false)
    })

    it('应该处理空字符串', () => {
      expect(JsonUtils.validateJson('')).toBe(true)
      expect(JsonUtils.validateJson('   ')).toBe(true)
    })
  })

  describe('类型推断', () => {
    it('应该正确推断基本类型', () => {
      expect(JsonUtils.inferType('string')).toBe('string')
      expect(JsonUtils.inferType(123)).toBe('number')
      expect(JsonUtils.inferType(true)).toBe('boolean')
      expect(JsonUtils.inferType(false)).toBe('boolean')
    })

    it('应该正确推断复杂类型', () => {
      expect(JsonUtils.inferType(null)).toBe('null')
      expect(JsonUtils.inferType([])).toBe('array')
      expect(JsonUtils.inferType([1, 2, 3])).toBe('array')
      expect(JsonUtils.inferType({})).toBe('object')
      expect(JsonUtils.inferType({ name: 'test' })).toBe('object')
    })
  })

  describe('JSON 转换为参数', () => {
    it('应该转换简单对象', () => {
      const json = { name: 'test', age: 30 }
      const params = JsonUtils.convertJsonToParams(json)
      
      expect(params).toHaveLength(2)
      expect(params[0].name).toBe('name')
      expect(params[0].type).toBe('string')
      expect(params[0].level).toBe(0)
      expect(params[1].name).toBe('age')
      expect(params[1].type).toBe('number')
      expect(params[1].level).toBe(0)
    })

    it('应该转换嵌套对象', () => {
      const json = {
        user: {
          name: 'test',
          profile: {
            bio: 'developer'
          }
        }
      }
      const params = JsonUtils.convertJsonToParams(json)
      
      expect(params.length).toBeGreaterThan(3)
      
      const userParam = params.find(p => p.name === 'user')
      const nameParam = params.find(p => p.name === 'name')
      const profileParam = params.find(p => p.name === 'profile')
      const bioParam = params.find(p => p.name === 'bio')
      
      expect(userParam.type).toBe('object')
      expect(userParam.level).toBe(0)
      expect(nameParam.level).toBe(1)
      expect(profileParam.level).toBe(1)
      expect(bioParam.level).toBe(2)
    })

    it('应该处理数组', () => {
      const json = { items: ['item1', 'item2'] }
      const params = JsonUtils.convertJsonToParams(json)
      
      const itemsParam = params.find(p => p.name === 'items')
      expect(itemsParam.type).toBe('array')
    })

    it('应该处理空对象', () => {
      const params = JsonUtils.convertJsonToParams({})
      expect(params).toHaveLength(0)
    })

    it('应该处理 null 值', () => {
      const params = JsonUtils.convertJsonToParams(null)
      expect(params).toHaveLength(0)
    })
  })

  describe('统计信息计算', () => {
    it('应该计算简单对象的统计信息', () => {
      const obj = { name: 'test', age: 30 }
      const stats = JsonUtils.calculateJsonStats(obj)
      
      expect(stats.nodeCount).toBeGreaterThan(0)
      expect(stats.maxDepth).toBeGreaterThan(0)
      expect(stats.isValid).toBe(true)
    })

    it('应该计算嵌套对象的统计信息', () => {
      const obj = {
        user: {
          name: 'test',
          profile: {
            bio: 'developer'
          }
        }
      }
      const stats = JsonUtils.calculateJsonStats(obj)
      
      expect(stats.nodeCount).toBeGreaterThan(3)
      expect(stats.maxDepth).toBeGreaterThan(2)
    })

    it('应该计算数组的统计信息', () => {
      const obj = { items: ['a', 'b', 'c'] }
      const stats = JsonUtils.calculateJsonStats(obj)
      
      expect(stats.nodeCount).toBeGreaterThan(3)
      expect(stats.maxDepth).toBeGreaterThan(1)
    })
  })

  describe('工具方法', () => {
    it('应该生成唯一 ID', () => {
      const id1 = JsonUtils.generateId()
      const id2 = JsonUtils.generateId()
      
      expect(id1).toBeTruthy()
      expect(id2).toBeTruthy()
      expect(id1).not.toBe(id2)
      expect(typeof id1).toBe('string')
      expect(id1.startsWith('param_')).toBe(true)
    })

    it('应该获取数组风格描述', () => {
      expect(JsonUtils.getArrayStyleDescription('index')).toContain('索引')
      expect(JsonUtils.getArrayStyleDescription('item')).toContain('项目')
      expect(JsonUtils.getArrayStyleDescription('expand')).toContain('展开')
      expect(JsonUtils.getArrayStyleDescription('unknown')).toContain('未知')
    })
  })

  describe('边界情况', () => {
    it('应该处理复杂的嵌套结构', () => {
      const complexJson = {
        users: [
          {
            id: 1,
            name: 'John',
            contacts: {
              email: 'john@example.com',
              phones: ['123-456-7890', '098-765-4321']
            }
          }
        ],
        metadata: {
          version: '1.0',
          settings: {
            theme: 'dark',
            notifications: true
          }
        }
      }
      
      const params = JsonUtils.convertJsonToParams(complexJson)
      const stats = JsonUtils.calculateJsonStats(complexJson)
      
      expect(params.length).toBeGreaterThan(5)
      expect(stats.nodeCount).toBeGreaterThan(10)
      expect(stats.maxDepth).toBeGreaterThan(3)
    })

    it('应该处理包含 null 值的对象', () => {
      const jsonWithNull = {
        name: 'test',
        value: null,
        nested: {
          data: null
        }
      }
      
      const params = JsonUtils.convertJsonToParams(jsonWithNull)
      const nullParam = params.find(p => p.name === 'value')
      
      expect(nullParam.type).toBe('null')
    })
  })
})