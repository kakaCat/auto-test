import { describe, it, expect } from 'vitest'
import SchemaConverter from '../schemaConversion.ts'
import UrlConverter from '../urlConversion.ts'

describe('SchemaConverter', () => {
  describe('fromExample', () => {
    it('应该正确转换简单对象', () => {
      const example = {
        name: 'John',
        age: 30,
        active: true
      }
      
      const result = SchemaConverter.fromExample(example)
      
      expect(result.params).toHaveLength(3)
      expect(result.params[0]).toMatchObject({
        name: 'name',
        type: 'string',
        level: 0
      })
      expect(result.params[1]).toMatchObject({
        name: 'age',
        type: 'number',
        level: 0
      })
      expect(result.params[2]).toMatchObject({
        name: 'active',
        type: 'boolean',
        level: 0
      })
    })

    it('应该正确处理嵌套对象', () => {
      const example = {
        user: {
          profile: {
            name: 'John',
            email: 'john@example.com'
          },
          settings: {
            theme: 'dark'
          }
        }
      }
      
      const result = SchemaConverter.fromExample(example)
      
      // 应该有 user, profile, name, email, settings, theme
      expect(result.params).toHaveLength(6)
      
      const userParam = result.params.find(p => p.name === 'user')
      expect(userParam).toMatchObject({
        type: 'object',
        level: 0
      })
      
      const profileParam = result.params.find(p => p.name === 'profile')
      expect(profileParam).toMatchObject({
        type: 'object',
        level: 1,
        parentId: userParam.id
      })
    })

    it('应该正确处理数组', () => {
      const example = {
        items: [
          { id: 1, name: 'Item 1' },
          { id: 2, name: 'Item 2' }
        ]
      }
      
      const result = SchemaConverter.fromExample(example, {
        arrayStyle: 'expand'
      })
      
      const itemsParam = result.params.find(p => p.name === 'items')
      expect(itemsParam.type).toBe('array')
      
      // 应该展开数组项的所有属性
      const arrayItems = result.params.filter(p => p.parentId === itemsParam.id)
      expect(arrayItems).toHaveLength(4) // 两个数组项，每个有id和name属性
    })

    it('应该处理空值', () => {
      const example = {
        name: 'John',
        description: null,
        tags: []
      }
      
      const result = SchemaConverter.fromExample(example, {
        nullHandling: 'keep'
      })
      
      const descParam = result.params.find(p => p.name === 'description')
      expect(descParam.type).toBe('null')
    })
  })

  describe('mergeParams', () => {
    it('应该正确合并参数列表', () => {
      const existing = [
        { id: '1', name: 'name', type: 'string', level: 0 },
        { id: '2', name: 'age', type: 'number', level: 0 }
      ]
      
      const incoming = [
        { id: '3', name: 'name', type: 'string', level: 0 },
        { id: '4', name: 'email', type: 'string', level: 0 }
      ]
      
      const result = SchemaConverter.mergeParams(existing, incoming, {
        detectConflicts: true
      })
      
      expect(result.params).toHaveLength(3) // name, age, email
      expect(result.conflicts).toHaveLength(0) // 没有类型冲突
    })

    it('应该检测类型冲突', () => {
      const existing = [
        { id: '1', name: 'age', type: 'string', level: 0 }
      ]
      
      const incoming = [
        { id: '2', name: 'age', type: 'number', level: 0 }
      ]
      
      const result = SchemaConverter.mergeParams(existing, incoming, {
        detectConflicts: true
      })
      
      expect(result.conflicts).toHaveLength(1)
      expect(result.conflicts[0].type).toBe('type')
      expect(result.conflicts[0].field).toBe('age')
    })

    it('应该检测必填字段冲突', () => {
      const existing = [
        { id: '1', name: 'name', type: 'string', level: 0, required: false }
      ]
      
      const incoming = [
        { id: '2', name: 'name', type: 'string', level: 0, required: true }
      ]
      
      const result = SchemaConverter.mergeParams(existing, incoming, {
        detectConflicts: true
      })
      
      expect(result.conflicts).toHaveLength(1)
      expect(result.conflicts[0].type).toBe('required')
    })
  })

  describe('toJsonSchema', () => {
    it('应该正确导出JSON Schema', () => {
      const params = [
        { id: '1', name: 'name', type: 'string', level: 0, required: true },
        { id: '2', name: 'age', type: 'number', level: 0, required: false },
        { id: '3', name: 'profile', type: 'object', level: 0, required: true },
        { id: '4', name: 'email', type: 'string', level: 1, parentId: '3', required: true }
      ]
      
      const schema = SchemaConverter.toJsonSchema(params)
      
      expect(schema.type).toBe('object')
      expect(schema.properties).toHaveProperty('name')
      expect(schema.properties).toHaveProperty('age')
      expect(schema.properties).toHaveProperty('profile')
      expect(schema.required).toContain('name')
      expect(schema.required).toContain('profile')
      expect(schema.required).not.toContain('age')
      
      // 检查嵌套对象
      expect(schema.properties.profile.type).toBe('object')
      expect(schema.properties.profile.properties).toHaveProperty('email')
    })
  })
})

describe('UrlConverter', () => {
  describe('fromUrl', () => {
    it('应该正确解析简单URL参数', () => {
      const url = 'https://api.example.com/users?name=John&age=30&active=true'
      
      const result = UrlConverter.fromUrl(url)
      
      expect(result.params).toHaveLength(3)
      expect(result.params[0]).toMatchObject({
        name: 'name',
        type: 'string',
        value: 'John'
      })
      expect(result.params[1]).toMatchObject({
        name: 'age',
        type: 'number',
        value: 30
      })
      expect(result.params[2]).toMatchObject({
        name: 'active',
        type: 'boolean',
        value: true
      })
    })

    it('应该处理数组参数', () => {
      const url = 'https://api.example.com/search?tags=javascript&tags=vue&tags=react'
      
      const result = UrlConverter.fromUrl(url)
      
      const tagsParam = result.params.find(p => p.name === 'tags')
      expect(tagsParam.type).toBe('array')
      expect(tagsParam.value).toEqual(['javascript', 'vue', 'react'])
    })

    it('应该处理URL编码', () => {
      const url = 'https://api.example.com/search?query=hello%20world&email=user%40example.com'
      
      const result = UrlConverter.fromUrl(url)
      
      expect(result.params[0].value).toBe('hello world')
      expect(result.params[1].value).toBe('user@example.com')
    })

    it('应该检测重复参数冲突', () => {
      const url = 'https://api.example.com/test?id=123&id=456'
      
      const result = UrlConverter.fromUrl(url, {
        detectConflicts: true
      })
      
      expect(result.conflicts).toHaveLength(1)
      expect(result.conflicts[0].type).toBe('duplicate')
      expect(result.conflicts[0].field).toBe('id')
    })

    it('应该处理嵌套对象参数', () => {
      const url = 'https://api.example.com/users?user[name]=John&user[age]=30&user[profile][email]=john@example.com'
      
      const result = UrlConverter.fromUrl(url)
      
      const userParam = result.params.find(p => p.name === 'user')
      expect(userParam.type).toBe('object')
      
      const nameParam = result.params.find(p => p.name === 'name' && p.parentId === userParam.id)
      expect(nameParam.value).toBe('John')
      
      const profileParam = result.params.find(p => p.name === 'profile' && p.parentId === userParam.id)
      expect(profileParam.type).toBe('object')
    })
  })

  describe('toUrl', () => {
    it('应该正确构建URL', () => {
      const baseUrl = 'https://api.example.com/users'
      const params = [
        { id: '1', name: 'name', type: 'string', value: 'John', level: 0, required: false },
        { id: '2', name: 'age', type: 'number', value: 30, level: 0, required: false },
        { id: '3', name: 'active', type: 'boolean', value: true, level: 0, required: false }
      ]
      
      const url = UrlConverter.toUrl(params, baseUrl)
      
      expect(url).toBe('https://api.example.com/users?name=John&age=30&active=true')
    })

    it('应该处理数组参数', () => {
      const baseUrl = 'https://api.example.com/search'
      const params = [
        { id: '1', name: 'tags', type: 'array', value: ['javascript', 'vue'], level: 0, required: false }
      ]
      
      const url = UrlConverter.toUrl(params, baseUrl)
      
      expect(url).toBe('https://api.example.com/search?tags%5B%5D=javascript&tags%5B%5D=vue')
    })

    it('应该处理URL编码', () => {
      const baseUrl = 'https://api.example.com/search'
      const params = [
        { id: '1', name: 'query', type: 'string', value: 'hello world', level: 0, required: false },
        { id: '2', name: 'email', type: 'string', value: 'user@example.com', level: 0, required: false }
      ]
      
      const url = UrlConverter.toUrl(params, baseUrl)
      
      expect(url).toBe('https://api.example.com/search?query=hello%2520world&email=user%2540example.com')
    })

    it('应该处理嵌套对象', () => {
      const baseUrl = 'https://api.example.com/search'
      const params = [
        { id: '1', name: 'user', type: 'object', level: 0, required: false },
        { id: '2', name: 'name', type: 'string', value: 'John', level: 1, parentId: '1', required: false },
        { id: '3', name: 'age', type: 'number', value: 30, level: 1, parentId: '1', required: false }
      ]
      
      const url = UrlConverter.toUrl(params, baseUrl)
      
      expect(url).toBe('https://api.example.com/search?user%5Bname%5D=John&user%5Bage%5D=30')
    })
  })

  describe('validateUrl', () => {
    it('应该验证有效URL', () => {
      expect(UrlConverter.validateUrl('https://api.example.com')).toBe(true)
      expect(UrlConverter.validateUrl('http://localhost:3000/api')).toBe(true)
      expect(UrlConverter.validateUrl('https://api.example.com/users?id=123')).toBe(true)
    })

    it('应该拒绝无效URL', () => {
      expect(UrlConverter.validateUrl('not-a-url')).toBe(false)
      expect(UrlConverter.validateUrl('ftp://example.com')).toBe(false)
      expect(UrlConverter.validateUrl('')).toBe(false)
    })
  })
})