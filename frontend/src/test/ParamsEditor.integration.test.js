import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟 ParamsEditor 组件的核心功能
const ParamsEditor = {
  name: 'ParamsEditor',
  template: `
    <div class="params-editor">
      <div class="toolbar">
        <button @click="addParam" class="add-param-btn">添加参数</button>
        <button @click="showJsonImport" class="json-import-btn">JSON 导入</button>
        <button @click="clearAll" class="clear-all-btn">清空</button>
      </div>
      
      <div class="params-list">
        <div 
          v-for="param in params" 
          :key="param.id" 
          class="param-item"
          :class="{ 'param-required': param.required }"
        >
          <input v-model="param.name" class="param-name" />
          <select v-model="param.type" class="param-type">
            <option value="string">String</option>
            <option value="number">Number</option>
            <option value="boolean">Boolean</option>
            <option value="object">Object</option>
            <option value="array">Array</option>
          </select>
          <input v-model="param.example" class="param-example" />
          <button @click="removeParam(param.id)" class="remove-param-btn">删除</button>
        </div>
      </div>
      
      <div class="stats">
        <span class="param-count">参数数量: {{ params.length }}</span>
        <span class="required-count">必填参数: {{ requiredCount }}</span>
      </div>
      
      <!-- JSON 导入模态框 -->
      <div v-if="showModal" class="json-import-modal">
        <div class="modal-content">
          <h3>JSON 导入</h3>
          <textarea 
            v-model="jsonContent" 
            class="json-input"
            placeholder="请输入 JSON 数据"
          ></textarea>
          <div class="import-options">
            <label>
              <input 
                type="radio" 
                v-model="importMode" 
                value="merge"
              /> 合并模式
            </label>
            <label>
              <input 
                type="radio" 
                v-model="importMode" 
                value="override"
              /> 覆盖模式
            </label>
          </div>
          <div class="modal-actions">
            <button @click="handleImport" :disabled="!canImport" class="import-btn">导入</button>
            <button @click="hideJsonImport" class="cancel-btn">取消</button>
          </div>
        </div>
      </div>
    </div>
  `,
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  data() {
    return {
      params: [...this.modelValue],
      showModal: false,
      jsonContent: '',
      importMode: 'merge'
    }
  },
  computed: {
    requiredCount() {
      return this.params.filter(p => p.required).length
    },
    canImport() {
      return this.jsonContent.trim() !== '' && this.validateJson(this.jsonContent)
    }
  },
  watch: {
    params: {
      handler(newParams) {
        this.$emit('update:modelValue', newParams)
        this.$emit('change', newParams)
      },
      deep: true
    },
    modelValue: {
      handler(newValue) {
        this.params = [...newValue]
      },
      deep: true
    }
  },
  methods: {
    addParam() {
      const newParam = {
        id: this.generateId(),
        name: '',
        type: 'string',
        required: false,
        example: '',
        level: 0,
        parentId: null
      }
      this.params.push(newParam)
    },
    
    removeParam(id) {
      const index = this.params.findIndex(p => p.id === id)
      if (index > -1) {
        this.params.splice(index, 1)
      }
    },
    
    clearAll() {
      this.params = []
    },
    
    showJsonImport() {
      this.showModal = true
      this.jsonContent = ''
      this.importMode = 'merge'
    },
    
    hideJsonImport() {
      this.showModal = false
      this.jsonContent = ''
    },
    
    validateJson(jsonString) {
      if (!jsonString || jsonString.trim() === '') {
        return false
      }
      
      try {
        JSON.parse(jsonString)
        return true
      } catch (error) {
        return false
      }
    },
    
    handleImport() {
       if (!this.canImport) return
       
       try {
         const jsonData = JSON.parse(this.jsonContent)
         const newParams = this.convertJsonToParams(jsonData)
         
         if (this.importMode === 'override') {
           this.params = newParams
         } else {
           // 合并模式：更新现有参数，添加新参数
           newParams.forEach(newParam => {
             const existingIndex = this.params.findIndex(p => p.name === newParam.name)
             if (existingIndex > -1) {
               // 更新现有参数
               this.params[existingIndex] = { ...this.params[existingIndex], ...newParam }
             } else {
               // 添加新参数
               this.params.push(newParam)
             }
           })
         }
         
         this.hideJsonImport()
       } catch (error) {
         console.error('JSON 导入失败:', error)
       }
     },
    
    convertJsonToParams(jsonData, parentKey = '', level = 0, parentId = null) {
       const params = []
       
       if (typeof jsonData !== 'object' || jsonData === null) {
         return params
       }

       Object.keys(jsonData).forEach(key => {
         const value = jsonData[key]
         const paramId = this.generateId()
         
         const param = {
           id: paramId,
           name: key,
           type: this.inferType(value),
           required: true,
           level: level,
           parentId: parentId,
           example: typeof value === 'object' ? JSON.stringify(value) : value
         }
         
         params.push(param)
         
         // 递归处理嵌套对象
         if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
           const nestedParams = this.convertJsonToParams(value, key, level + 1, paramId)
           params.push(...nestedParams)
         }
       })
       
       return params
     },
    
    inferType(value) {
      if (value === null) return 'string'
      if (Array.isArray(value)) return 'array'
      if (typeof value === 'object') return 'object'
      return typeof value
    },
    
    generateId() {
      return 'param_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
    }
  }
}

describe('ParamsEditor 集成测试', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(ParamsEditor, {
      props: {
        modelValue: []
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('基本功能', () => {
    it('应该正确渲染组件', () => {
      expect(wrapper.find('.params-editor').exists()).toBe(true)
      expect(wrapper.find('.toolbar').exists()).toBe(true)
      expect(wrapper.find('.params-list').exists()).toBe(true)
      expect(wrapper.find('.stats').exists()).toBe(true)
    })

    it('应该显示工具栏按钮', () => {
      expect(wrapper.find('.add-param-btn').exists()).toBe(true)
      expect(wrapper.find('.json-import-btn').exists()).toBe(true)
      expect(wrapper.find('.clear-all-btn').exists()).toBe(true)
    })

    it('应该显示统计信息', () => {
      expect(wrapper.find('.param-count').text()).toContain('参数数量: 0')
      expect(wrapper.find('.required-count').text()).toContain('必填参数: 0')
    })
  })

  describe('参数管理', () => {
    it('应该能够添加参数', async () => {
      await wrapper.find('.add-param-btn').trigger('click')
      
      expect(wrapper.vm.params).toHaveLength(1)
      expect(wrapper.find('.param-item').exists()).toBe(true)
      expect(wrapper.find('.param-count').text()).toContain('参数数量: 1')
    })

    it('应该能够删除参数', async () => {
      // 先添加一个参数
      await wrapper.find('.add-param-btn').trigger('click')
      expect(wrapper.vm.params).toHaveLength(1)
      
      // 删除参数
      await wrapper.find('.remove-param-btn').trigger('click')
      expect(wrapper.vm.params).toHaveLength(0)
    })

    it('应该能够清空所有参数', async () => {
      // 添加几个参数
      await wrapper.find('.add-param-btn').trigger('click')
      await wrapper.find('.add-param-btn').trigger('click')
      expect(wrapper.vm.params).toHaveLength(2)
      
      // 清空所有参数
      await wrapper.find('.clear-all-btn').trigger('click')
      expect(wrapper.vm.params).toHaveLength(0)
    })

    it('应该能够编辑参数属性', async () => {
      await wrapper.find('.add-param-btn').trigger('click')
      
      const nameInput = wrapper.find('.param-name')
      const typeSelect = wrapper.find('.param-type')
      const exampleInput = wrapper.find('.param-example')
      
      await nameInput.setValue('testParam')
      await typeSelect.setValue('number')
      await exampleInput.setValue('123')
      
      expect(wrapper.vm.params[0].name).toBe('testParam')
      expect(wrapper.vm.params[0].type).toBe('number')
      expect(wrapper.vm.params[0].example).toBe('123')
    })
  })

  describe('JSON 导入功能', () => {
    it('应该能够打开 JSON 导入模态框', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      
      expect(wrapper.vm.showModal).toBe(true)
      expect(wrapper.find('.json-import-modal').exists()).toBe(true)
    })

    it('应该能够关闭 JSON 导入模态框', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      expect(wrapper.vm.showModal).toBe(true)
      
      await wrapper.find('.cancel-btn').trigger('click')
      expect(wrapper.vm.showModal).toBe(false)
    })

    it('应该验证 JSON 格式', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      
      // 测试有效 JSON
      wrapper.vm.jsonContent = '{"name": "test"}'
      expect(wrapper.vm.canImport).toBe(true)
      
      // 测试无效 JSON
      wrapper.vm.jsonContent = '{"name": "test"'
      expect(wrapper.vm.canImport).toBe(false)
      
      // 测试空内容
      wrapper.vm.jsonContent = ''
      expect(wrapper.vm.canImport).toBe(false)
    })

    it('应该在覆盖模式下导入 JSON', async () => {
      // 先添加一个现有参数
      await wrapper.find('.add-param-btn').trigger('click')
      wrapper.vm.params[0].name = 'existingParam'
      expect(wrapper.vm.params).toHaveLength(1)
      
      // 打开导入模态框
      await wrapper.find('.json-import-btn').trigger('click')
      
      // 设置 JSON 内容和覆盖模式
      wrapper.vm.jsonContent = '{"newParam": "value", "anotherParam": 123}'
      wrapper.vm.importMode = 'override'
      
      // 执行导入
      await wrapper.find('.import-btn').trigger('click')
      
      // 验证参数被覆盖
      expect(wrapper.vm.params).toHaveLength(2)
      expect(wrapper.vm.params.find(p => p.name === 'existingParam')).toBeUndefined()
      expect(wrapper.vm.params.find(p => p.name === 'newParam')).toBeTruthy()
      expect(wrapper.vm.params.find(p => p.name === 'anotherParam')).toBeTruthy()
    })

    it('应该在合并模式下导入 JSON', async () => {
      // 先添加一个现有参数
      await wrapper.find('.add-param-btn').trigger('click')
      wrapper.vm.params[0].name = 'existingParam'
      wrapper.vm.params[0].type = 'string'
      expect(wrapper.vm.params).toHaveLength(1)
      
      // 打开导入模态框
      await wrapper.find('.json-import-btn').trigger('click')
      
      // 设置 JSON 内容和合并模式
      wrapper.vm.jsonContent = '{"existingParam": "updatedValue", "newParam": 123}'
      wrapper.vm.importMode = 'merge'
      
      // 执行导入
      await wrapper.find('.import-btn').trigger('click')
      
      // 验证参数被合并
      expect(wrapper.vm.params).toHaveLength(2)
      
      const existingParam = wrapper.vm.params.find(p => p.name === 'existingParam')
      const newParam = wrapper.vm.params.find(p => p.name === 'newParam')
      
      expect(existingParam).toBeTruthy()
      expect(existingParam.example).toBe('updatedValue')
      expect(newParam).toBeTruthy()
      expect(newParam.type).toBe('number')
    })

    it('应该处理嵌套对象的导入', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      
      const nestedJson = {
        user: {
          name: 'John',
          profile: {
            age: 30,
            bio: 'Developer'
          }
        },
        settings: {
          theme: 'dark'
        }
      }
      
      wrapper.vm.jsonContent = JSON.stringify(nestedJson)
      wrapper.vm.importMode = 'override'
      
      await wrapper.find('.import-btn').trigger('click')
      
      // 验证嵌套结构被正确导入
      expect(wrapper.vm.params.length).toBeGreaterThan(5)
      
      const userParam = wrapper.vm.params.find(p => p.name === 'user')
      const nameParam = wrapper.vm.params.find(p => p.name === 'name')
      const profileParam = wrapper.vm.params.find(p => p.name === 'profile')
      const ageParam = wrapper.vm.params.find(p => p.name === 'age')
      
      expect(userParam.type).toBe('object')
      expect(userParam.level).toBe(0)
      expect(nameParam.level).toBe(1)
      expect(profileParam.level).toBe(1)
      expect(ageParam.level).toBe(2)
    })
  })

  describe('事件发射', () => {
    it('应该在参数变化时发射事件', async () => {
      await wrapper.find('.add-param-btn').trigger('click')
      
      const updateEvents = wrapper.emitted('update:modelValue')
      const changeEvents = wrapper.emitted('change')
      
      expect(updateEvents).toBeTruthy()
      expect(changeEvents).toBeTruthy()
      expect(updateEvents[updateEvents.length - 1][0]).toHaveLength(1)
    })

    it('应该在导入后发射事件', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      
      wrapper.vm.jsonContent = '{"test": "value"}'
      await wrapper.find('.import-btn').trigger('click')
      
      const updateEvents = wrapper.emitted('update:modelValue')
      const changeEvents = wrapper.emitted('change')
      
      expect(updateEvents).toBeTruthy()
      expect(changeEvents).toBeTruthy()
    })
  })

  describe('响应式更新', () => {
    it('应该响应 modelValue 属性变化', async () => {
      const newParams = [
        { id: '1', name: 'test', type: 'string', required: true, level: 0 }
      ]
      
      await wrapper.setProps({ modelValue: newParams })
      
      expect(wrapper.vm.params).toHaveLength(1)
      expect(wrapper.vm.params[0].name).toBe('test')
    })

    it('应该更新统计信息', async () => {
      await wrapper.find('.add-param-btn').trigger('click')
      wrapper.vm.params[0].required = true
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.find('.param-count').text()).toContain('参数数量: 1')
      expect(wrapper.find('.required-count').text()).toContain('必填参数: 1')
    })
  })

  describe('边界情况', () => {
    it('应该处理大量参数', async () => {
      const largeJson = {}
      for (let i = 0; i < 100; i++) {
        largeJson[`param${i}`] = `value${i}`
      }
      
      await wrapper.find('.json-import-btn').trigger('click')
      wrapper.vm.jsonContent = JSON.stringify(largeJson)
      await wrapper.find('.import-btn').trigger('click')
      
      expect(wrapper.vm.params).toHaveLength(100)
    })

    it('应该处理包含特殊字符的参数名', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      
      const specialJson = {
        'param-with-dash': 'value1',
        'param_with_underscore': 'value2',
        'param.with.dot': 'value3'
      }
      
      wrapper.vm.jsonContent = JSON.stringify(specialJson)
      await wrapper.find('.import-btn').trigger('click')
      
      expect(wrapper.vm.params).toHaveLength(3)
      expect(wrapper.vm.params.find(p => p.name === 'param-with-dash')).toBeTruthy()
      expect(wrapper.vm.params.find(p => p.name === 'param_with_underscore')).toBeTruthy()
      expect(wrapper.vm.params.find(p => p.name === 'param.with.dot')).toBeTruthy()
    })

    it('应该处理空的 JSON 对象', async () => {
      await wrapper.find('.json-import-btn').trigger('click')
      
      wrapper.vm.jsonContent = '{}'
      await wrapper.find('.import-btn').trigger('click')
      
      expect(wrapper.vm.params).toHaveLength(0)
    })
  })
})