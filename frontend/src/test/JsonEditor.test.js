import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import JsonEditor from '@/components/common/JsonEditor.vue'

// Mock Monaco Editor
vi.mock('monaco-editor')

describe('JsonEditor', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(JsonEditor, {
      props: {
        modelValue: '',
        readonly: false
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('基本渲染', () => {
    it('应该正确渲染组件', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.json-editor').exists()).toBe(true)
    })

    it('应该渲染工具栏', () => {
      expect(wrapper.find('.json-editor-toolbar').exists()).toBe(true)
    })

    it('应该渲染编辑器容器', () => {
      expect(wrapper.find('.json-editor-container').exists()).toBe(true)
    })

    it('应该渲染状态栏', () => {
      expect(wrapper.find('.json-editor-status').exists()).toBe(true)
    })
  })

  describe('工具栏按钮', () => {
    it('应该显示格式化按钮', () => {
      const formatBtn = wrapper.find('[data-test="format-btn"]')
      expect(formatBtn.exists()).toBe(true)
      expect(formatBtn.text()).toContain('格式化')
    })

    it('应该显示验证按钮', () => {
      const validateBtn = wrapper.find('[data-test="validate-btn"]')
      expect(validateBtn.exists()).toBe(true)
      expect(validateBtn.text()).toContain('验证')
    })

    it('应该显示清空按钮', () => {
      const clearBtn = wrapper.find('[data-test="clear-btn"]')
      expect(clearBtn.exists()).toBe(true)
      expect(clearBtn.text()).toContain('清空')
    })
  })

  describe('事件处理', () => {
    it('应该触发 update:modelValue 事件', async () => {
      const testValue = '{"test": "value"}'
      
      // 模拟编辑器内容变化
      await wrapper.vm.handleContentChange(testValue)
      
      const updateEvents = wrapper.emitted('update:modelValue')
      expect(updateEvents).toBeTruthy()
      expect(updateEvents[0][0]).toBe(testValue)
    })

    it('应该触发 change 事件', async () => {
      const testValue = '{"test": "value"}'
      
      await wrapper.vm.handleContentChange(testValue)
      
      const changeEvents = wrapper.emitted('change')
      expect(changeEvents).toBeTruthy()
    })
  })

  describe('JSON 验证', () => {
    it('应该验证有效的 JSON', () => {
      const validJson = '{"name": "test", "value": 123}'
      const result = wrapper.vm.validateJson(validJson)
      
      expect(result.isValid).toBe(true)
      expect(result.error).toBe(null)
    })

    it('应该检测无效的 JSON', () => {
      const invalidJson = '{"name": "test", "value": }'
      const result = wrapper.vm.validateJson(invalidJson)
      
      expect(result.isValid).toBe(false)
      expect(result.error).toBeTruthy()
    })

    it('应该处理空字符串', () => {
      const result = wrapper.vm.validateJson('')
      
      expect(result.isValid).toBe(true)
      expect(result.error).toBe(null)
    })
  })

  describe('JSON 格式化', () => {
    it('应该格式化 JSON 字符串', () => {
      const unformattedJson = '{"name":"test","value":123}'
      const formatted = wrapper.vm.formatJson(unformattedJson)
      
      expect(formatted).toContain('\n')
      expect(formatted).toContain('  ')
    })

    it('应该处理无效 JSON', () => {
      const invalidJson = '{"name": "test", "value": }'
      const result = wrapper.vm.formatJson(invalidJson)
      
      expect(result).toBe(invalidJson) // 应该返回原始字符串
    })
  })

  describe('统计信息', () => {
    it('应该计算 JSON 统计信息', async () => {
      const testJson = '{"name": "test", "nested": {"value": 123}}'
      await wrapper.setProps({ modelValue: testJson })
      
      const stats = wrapper.vm.jsonStats
      expect(stats.isValid).toBe(true)
      expect(stats.lines).toBeGreaterThan(0)
      expect(stats.characters).toBe(testJson.length)
    })

    it('应该显示光标位置', () => {
      expect(wrapper.vm.cursorPosition).toEqual({
        line: 1,
        column: 1
      })
    })
  })

  describe('暴露的方法', () => {
    it('应该暴露 formatJson 方法', () => {
      expect(typeof wrapper.vm.formatJson).toBe('function')
    })

    it('应该暴露 validateJson 方法', () => {
      expect(typeof wrapper.vm.validateJson).toBe('function')
    })

    it('应该暴露 clearContent 方法', () => {
      expect(typeof wrapper.vm.clearContent).toBe('function')
    })
  })
})