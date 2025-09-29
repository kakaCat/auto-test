import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'

// 简化的 JSON 导入应用
const JsonImportApp = {
  name: 'JsonImportApp',
  template: `
    <div class="json-import-app">
      <h2>API 参数编辑器</h2>
      
      <!-- 参数编辑器 -->
      <div class="params-editor">
        <div class="toolbar">
          <button @click="addParam" class="add-param-btn" data-testid="add-param-btn">添加参数</button>
          <button @click="openJsonImport" class="json-import-btn" data-testid="json-import-btn">JSON 导入</button>
          <button @click="clearAll" class="clear-all-btn" data-testid="clear-all-btn">清空</button>
        </div>
        
        <div class="params-list">
          <div 
            v-for="param in params" 
            :key="param.id" 
            class="param-item"
            :data-testid="'param-' + param.id"
          >
            <span class="param-name">{{ param.name }}</span>
            <span class="param-type">{{ param.type }}</span>
            <span class="param-example">{{ param.example }}</span>
            <button 
              @click="removeParam(param.id)" 
              class="remove-param-btn"
              :data-testid="'remove-param-' + param.id"
            >
              删除
            </button>
          </div>
        </div>
        
        <div class="stats">
          <span class="param-count" data-testid="param-count">参数数量: {{ params.length }}</span>
          <span class="required-count" data-testid="required-count">必填参数: {{ requiredCount }}</span>
        </div>
      </div>
      
      <!-- JSON 导入模态框 -->
      <div v-if="showJsonModal" class="json-import-modal" data-testid="json-import-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>JSON 导入</h3>
            <button @click="closeJsonImport" class="close-btn" data-testid="close-modal-btn">×</button>
          </div>
          
          <div class="modal-body">
            <div class="json-input-section">
              <label>JSON 数据:</label>
              <textarea 
                v-model="jsonContent" 
                class="json-input"
                data-testid="json-input"
                placeholder="请输入 JSON 数据"
                rows="10"
              ></textarea>
            </div>
            
            <div class="import-options">
              <h4>导入模式:</h4>
              <label>
                <input 
                  type="radio" 
                  v-model="importMode" 
                  value="merge"
                  data-testid="import-mode-merge"
                /> 合并模式
              </label>
              <label>
                <input 
                  type="radio" 
                  v-model="importMode" 
                  value="override"
                  data-testid="import-mode-override"
                /> 覆盖模式
              </label>
            </div>
            
            <div class="validation-message" v-if="validationMessage" data-testid="validation-message">
              <span :class="{ 'error': !isJsonValid, 'success': isJsonValid }">
                {{ validationMessage }}
              </span>
            </div>
          </div>
          
          <div class="modal-footer">
            <button 
              @click="handleImport" 
              :disabled="!canImport" 
              class="import-btn"
              data-testid="import-btn"
            >
              导入
            </button>
            <button 
              @click="closeJsonImport" 
              class="cancel-btn"
              data-testid="cancel-btn"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      params: [],
      showJsonModal: false,
      jsonContent: '',
      importMode: 'merge'
    }
  },
  computed: {
    requiredCount() {
      return this.params.filter(p => p.required).length
    },
    
    isJsonValid() {
      return this.validateJson(this.jsonContent)
    },
    
    canImport() {
      return this.jsonContent.trim() !== '' && this.isJsonValid
    },
    
    validationMessage() {
      if (!this.jsonContent.trim()) return ''
      
      if (this.isJsonValid) {
        return '✓ 有效的 JSON'
      } else {
        return '✗ 无效的 JSON 格式'
      }
    }
  },
  methods: {
    addParam() {
      const newParam = {
        id: this.generateId(),
        name: `param${this.params.length + 1}`,
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
    
    openJsonImport() {
      this.showJsonModal = true
      this.jsonContent = ''
      // 不重置 importMode，保持用户选择
    },
    
    closeJsonImport() {
      this.showJsonModal = false
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
          // 合并模式
          newParams.forEach(newParam => {
            const existingIndex = this.params.findIndex(p => p.name === newParam.name)
            if (existingIndex > -1) {
              this.params[existingIndex] = { ...this.params[existingIndex], ...newParam }
            } else {
              this.params.push(newParam)
            }
          })
        }
        
        this.closeJsonImport()
      } catch (error) {
        console.error('JSON 导入失败:', error)
      }
    },
    
    convertJsonToParams(jsonData, level = 0, parentId = null) {
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
          example: typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value)
        }
        
        params.push(param)
        
        // 递归处理嵌套对象
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          const nestedParams = this.convertJsonToParams(value, level + 1, paramId)
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

describe('JSON 导入最终测试', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(JsonImportApp)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('基础功能测试', () => {
    it('应该正确渲染初始状态', () => {
      expect(wrapper.find('h2').text()).toBe('API 参数编辑器')
      expect(wrapper.find('[data-testid="param-count"]').text()).toContain('参数数量: 0')
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
    })

    it('应该能够添加和删除参数', async () => {
      // 添加参数
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      expect(wrapper.vm.params).toHaveLength(1)
      expect(wrapper.find('[data-testid="param-count"]').text()).toContain('参数数量: 1')

      // 删除参数
      const paramId = wrapper.vm.params[0].id
      await wrapper.find(`[data-testid="remove-param-${paramId}"]`).trigger('click')
      expect(wrapper.vm.params).toHaveLength(0)
    })

    it('应该能够清空所有参数', async () => {
      // 添加几个参数
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      expect(wrapper.vm.params).toHaveLength(2)

      // 清空
      await wrapper.find('[data-testid="clear-all-btn"]').trigger('click')
      expect(wrapper.vm.params).toHaveLength(0)
    })
  })

  describe('JSON 导入模态框', () => {
    it('应该能够打开和关闭模态框', async () => {
      // 打开模态框
      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(true)

      // 关闭模态框
      await wrapper.find('[data-testid="close-modal-btn"]').trigger('click')
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
    })

    it('应该验证 JSON 输入', async () => {
      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')

      // 输入无效 JSON
      await wrapper.find('[data-testid="json-input"]').setValue('{ invalid json }')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.isJsonValid).toBe(false)
      expect(wrapper.find('[data-testid="validation-message"]').text()).toContain('无效的 JSON')

      // 输入有效 JSON
      await wrapper.find('[data-testid="json-input"]').setValue('{"valid": "json"}')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.isJsonValid).toBe(true)
      expect(wrapper.find('[data-testid="validation-message"]').text()).toContain('有效的 JSON')
    })

    it('应该根据 JSON 有效性启用/禁用导入按钮', async () => {
      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')

      // 无效 JSON - 按钮禁用
      await wrapper.find('[data-testid="json-input"]').setValue('{ invalid }')
      await wrapper.vm.$nextTick()
      expect(wrapper.find('[data-testid="import-btn"]').attributes('disabled')).toBeDefined()

      // 有效 JSON - 按钮启用
      await wrapper.find('[data-testid="json-input"]').setValue('{"test": "value"}')
      await wrapper.vm.$nextTick()
      expect(wrapper.find('[data-testid="import-btn"]').attributes('disabled')).toBeUndefined()
    })
  })

  describe('JSON 导入功能', () => {
    it('应该能够导入简单的 JSON 对象', async () => {
      const jsonData = {
        name: 'John',
        age: 30,
        active: true
      }

      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')
      await wrapper.find('[data-testid="json-input"]').setValue(JSON.stringify(jsonData))
      await wrapper.find('[data-testid="import-btn"]').trigger('click')

      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
      expect(wrapper.vm.params).toHaveLength(3)

      const nameParam = wrapper.vm.params.find(p => p.name === 'name')
      const ageParam = wrapper.vm.params.find(p => p.name === 'age')
      const activeParam = wrapper.vm.params.find(p => p.name === 'active')

      expect(nameParam.type).toBe('string')
      expect(nameParam.example).toBe('John')
      expect(ageParam.type).toBe('number')
      expect(ageParam.example).toBe('30')
      expect(activeParam.type).toBe('boolean')
      expect(activeParam.example).toBe('true')
    })

    it('应该能够导入嵌套的 JSON 对象', async () => {
      const jsonData = {
        user: {
          name: 'John',
          profile: {
            bio: 'Developer'
          }
        }
      }

      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')
      await wrapper.find('[data-testid="json-input"]').setValue(JSON.stringify(jsonData))
      await wrapper.find('[data-testid="import-btn"]').trigger('click')

      expect(wrapper.vm.params.length).toBeGreaterThan(3)

      const userParam = wrapper.vm.params.find(p => p.name === 'user')
      const nameParam = wrapper.vm.params.find(p => p.name === 'name')
      const profileParam = wrapper.vm.params.find(p => p.name === 'profile')
      const bioParam = wrapper.vm.params.find(p => p.name === 'bio')

      expect(userParam.level).toBe(0)
      expect(nameParam.level).toBe(1)
      expect(profileParam.level).toBe(1)
      expect(bioParam.level).toBe(2)

      expect(nameParam.parentId).toBe(userParam.id)
      expect(bioParam.parentId).toBe(profileParam.id)
    })

    it('应该处理覆盖模式', async () => {
      // 先添加一些参数
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      expect(wrapper.vm.params).toHaveLength(2)

      // 导入 JSON (覆盖模式)
      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')
      
      // 确保模式设置正确
      wrapper.vm.importMode = 'override'
      await wrapper.vm.$nextTick()
      
      await wrapper.find('[data-testid="json-input"]').setValue('{"newParam": "value"}')
      await wrapper.vm.$nextTick()
      
      // 验证模式和数据
      expect(wrapper.vm.importMode).toBe('override')
      expect(wrapper.vm.isJsonValid).toBe(true)
      
      await wrapper.find('[data-testid="import-btn"]').trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.params).toHaveLength(1)
      expect(wrapper.vm.params[0].name).toBe('newParam')
    })

    it('应该处理合并模式', async () => {
      // 先添加一个参数
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      wrapper.vm.params[0].name = 'existingParam'
      expect(wrapper.vm.params).toHaveLength(1)

      // 导入 JSON (合并模式)
      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')
      await wrapper.find('[data-testid="import-mode-merge"]').trigger('click')
      await wrapper.find('[data-testid="json-input"]').setValue('{"newParam": "value"}')
      await wrapper.find('[data-testid="import-btn"]').trigger('click')

      expect(wrapper.vm.params).toHaveLength(2)
      expect(wrapper.vm.params.some(p => p.name === 'existingParam')).toBe(true)
      expect(wrapper.vm.params.some(p => p.name === 'newParam')).toBe(true)
    })

    it('应该处理取消操作', async () => {
      await wrapper.find('[data-testid="add-param-btn"]').trigger('click')
      const originalCount = wrapper.vm.params.length

      await wrapper.find('[data-testid="json-import-btn"]').trigger('click')
      await wrapper.find('[data-testid="json-input"]').setValue('{"test": "value"}')
      await wrapper.find('[data-testid="cancel-btn"]').trigger('click')

      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
      expect(wrapper.vm.params).toHaveLength(originalCount)
    })
  })

  describe('工具方法测试', () => {
    it('应该正确推断数据类型', () => {
      expect(wrapper.vm.inferType('string')).toBe('string')
      expect(wrapper.vm.inferType(123)).toBe('number')
      expect(wrapper.vm.inferType(true)).toBe('boolean')
      expect(wrapper.vm.inferType([])).toBe('array')
      expect(wrapper.vm.inferType({})).toBe('object')
      expect(wrapper.vm.inferType(null)).toBe('string')
    })

    it('应该正确验证 JSON', () => {
      expect(wrapper.vm.validateJson('')).toBe(false)
      expect(wrapper.vm.validateJson('invalid')).toBe(false)
      expect(wrapper.vm.validateJson('{"valid": "json"}')).toBe(true)
      expect(wrapper.vm.validateJson('[]')).toBe(true)
    })

    it('应该生成唯一 ID', () => {
      const id1 = wrapper.vm.generateId()
      const id2 = wrapper.vm.generateId()
      
      expect(id1).toBeTruthy()
      expect(id2).toBeTruthy()
      expect(id1).not.toBe(id2)
      expect(id1).toMatch(/^param_/)
      expect(id2).toMatch(/^param_/)
    })
  })
})