import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import JsonImportModal from '@/components/common/JsonImportModal.vue'

// Mock 子组件
vi.mock('@/components/common/JsonEditor.vue', () => ({
  default: {
    name: 'JsonEditor',
    template: '<div class="mock-json-editor"></div>',
    props: ['modelValue', 'readonly'],
    emits: ['update:modelValue', 'change', 'validate', 'format']
  }
}))

vi.mock('@/components/common/JsonPreviewTree.vue', () => ({
  default: {
    name: 'JsonPreviewTree',
    template: '<div class="mock-json-preview-tree"></div>',
    props: ['data']
  }
}))

describe('JsonImportModal', () => {
  let wrapper

  const defaultProps = {
    modelValue: false,
    currentParams: []
  }

  beforeEach(() => {
    wrapper = mount(JsonImportModal, {
      props: defaultProps
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('基本渲染', () => {
    it('应该正确渲染组件', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('应该渲染 JsonEditor 组件', () => {
      expect(wrapper.find('.mock-json-editor').exists()).toBe(true)
    })

    it('应该渲染 JsonPreviewTree 组件', () => {
      expect(wrapper.find('.mock-json-preview-tree').exists()).toBe(true)
    })

    it('应该显示正确的标题', () => {
      expect(wrapper.text()).toContain('JSON 导入')
    })
  })

  describe('导入选项', () => {
    it('应该显示导入模式选项', () => {
      expect(wrapper.text()).toContain('导入模式')
      expect(wrapper.text()).toContain('覆盖模式')
      expect(wrapper.text()).toContain('合并模式')
    })

    it('应该显示数组风格选项', () => {
      expect(wrapper.text()).toContain('数组风格')
      expect(wrapper.text()).toContain('索引风格')
      expect(wrapper.text()).toContain('项目风格')
    })

    it('应该显示其他选项', () => {
      expect(wrapper.text()).toContain('忽略 null 值')
      expect(wrapper.text()).toContain('最大层级')
    })
  })

  describe('JSON 处理', () => {
    it('应该验证有效的 JSON', () => {
      const validJson = '{"name": "test", "value": 123}'
      const result = wrapper.vm.validateJson(validJson)
      
      expect(result).toBe(true)
    })

    it('应该检测无效的 JSON', () => {
      const invalidJson = '{"name": "test", "value": }'
      const result = wrapper.vm.validateJson(invalidJson)
      
      expect(result).toBe(false)
    })

    it('应该处理空字符串', () => {
      const result = wrapper.vm.validateJson('')
      
      expect(result).toBe(true)
    })
  })

  describe('JSON 转换为参数', () => {
    it('应该转换简单对象', () => {
      const json = { name: 'test', age: 30 }
      const params = wrapper.vm.convertJsonToParams(json)
      
      expect(params).toHaveLength(2)
      expect(params[0].name).toBe('name')
      expect(params[0].type).toBe('string')
      expect(params[1].name).toBe('age')
      expect(params[1].type).toBe('number')
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
      const params = wrapper.vm.convertJsonToParams(json)
      
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

    it('应该转换数组', () => {
      const json = {
        items: ['item1', 'item2']
      }
      const params = wrapper.vm.convertJsonToParams(json)
      
      const itemsParam = params.find(p => p.name === 'items')
      expect(itemsParam.type).toBe('array')
    })

    it('应该推断正确的数据类型', () => {
      const json = {
        stringField: 'test',
        numberField: 123,
        booleanField: true,
        nullField: null,
        arrayField: [],
        objectField: {}
      }
      const params = wrapper.vm.convertJsonToParams(json)
      
      expect(params.find(p => p.name === 'stringField').type).toBe('string')
      expect(params.find(p => p.name === 'numberField').type).toBe('number')
      expect(params.find(p => p.name === 'booleanField').type).toBe('boolean')
      expect(params.find(p => p.name === 'nullField').type).toBe('null')
      expect(params.find(p => p.name === 'arrayField').type).toBe('array')
      expect(params.find(p => p.name === 'objectField').type).toBe('object')
    })
  })

  describe('统计信息', () => {
    it('应该计算 JSON 统计信息', async () => {
      const testJson = '{"name": "test", "nested": {"value": 123}}'
      wrapper.vm.jsonContent = testJson
      await wrapper.vm.updatePreview()
      
      const stats = wrapper.vm.jsonStats
      expect(stats.isValid).toBe(true)
      expect(stats.nodeCount).toBeGreaterThan(0)
      expect(stats.maxDepth).toBeGreaterThan(1)
    })
  })

  describe('导入按钮状态', () => {
    it('应该在有效 JSON 时启用导入按钮', async () => {
      wrapper.vm.jsonContent = '{"test": "value"}'
      await wrapper.vm.updatePreview()
      
      expect(wrapper.vm.canImport).toBe(true)
    })

    it('应该在无效 JSON 时禁用导入按钮', async () => {
      wrapper.vm.jsonContent = '{"test": "value"'
      await wrapper.vm.updatePreview()
      
      expect(wrapper.vm.canImport).toBe(false)
    })

    it('应该在空内容时禁用导入按钮', () => {
      wrapper.vm.jsonContent = ''
      
      expect(wrapper.vm.canImport).toBe(false)
    })
  })

  describe('事件处理', () => {
    it('应该处理导入事件', async () => {
      wrapper.vm.jsonContent = '{"test": "value"}'
      wrapper.vm.previewData = [
        { name: 'test', type: 'string', required: true, level: 0, parentId: null }
      ]
      
      await wrapper.vm.handleImport()
      
      const importEvents = wrapper.emitted('import')
      expect(importEvents).toBeTruthy()
      expect(importEvents[0][0].params).toHaveLength(1)
      expect(importEvents[0][0].options).toBeTruthy()
    })

    it('应该处理取消事件', async () => {
      await wrapper.vm.handleCancel()
      
      const closeEvents = wrapper.emitted('close')
      expect(closeEvents).toBeTruthy()
    })

    it('应该处理对话框关闭事件', async () => {
      await wrapper.vm.handleDialogClose()
      
      const updateEvents = wrapper.emitted('update:modelValue')
      expect(updateEvents).toBeTruthy()
      expect(updateEvents[0][0]).toBe(false)
    })
  })

  describe('工具方法', () => {
    it('应该生成唯一 ID', () => {
      const id1 = wrapper.vm.generateId()
      const id2 = wrapper.vm.generateId()
      
      expect(id1).toBeTruthy()
      expect(id2).toBeTruthy()
      expect(id1).not.toBe(id2)
    })

    it('应该获取数组风格描述', () => {
      const indexDesc = wrapper.vm.getArrayStyleDescription('index')
      const itemDesc = wrapper.vm.getArrayStyleDescription('item')
      
      expect(indexDesc).toContain('索引')
      expect(itemDesc).toContain('项目')
    })
  })

  describe('响应式状态', () => {
    it('应该响应 modelValue 变化', async () => {
      await wrapper.setProps({ modelValue: true })
      
      expect(wrapper.vm.visible).toBe(true)
    })

    it('应该响应 currentParams 变化', async () => {
      const testParams = [
        { id: '1', name: 'test', type: 'string' }
      ]
      await wrapper.setProps({ currentParams: testParams })
      
      // 验证组件接收到了新的参数
      expect(wrapper.props('currentParams')).toEqual(testParams)
    })
  })
})