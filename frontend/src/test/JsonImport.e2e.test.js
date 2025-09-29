import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟完整的 JSON 导入流程
const JsonImportApp = {
  name: 'JsonImportApp',
  template: `
    <div class="json-import-app">
      <h2>API 参数编辑器</h2>
      
      <!-- 参数编辑器 -->
      <div class="params-editor">
        <div class="toolbar">
          <button @click="addParam" class="add-param-btn">添加参数</button>
          <button @click="openJsonImport" class="json-import-btn">JSON 导入</button>
          <button @click="clearAll" class="clear-all-btn">清空</button>
        </div>
        
        <div class="params-list">
          <div 
            v-for="param in params" 
            :key="param.id" 
            class="param-item"
            :data-testid="'param-' + param.id"
          >
            <input 
              v-model="param.name" 
              class="param-name" 
              :data-testid="'param-name-' + param.id"
              placeholder="参数名"
            />
            <select 
              v-model="param.type" 
              class="param-type"
              :data-testid="'param-type-' + param.id"
            >
              <option value="string">String</option>
              <option value="number">Number</option>
              <option value="boolean">Boolean</option>
              <option value="object">Object</option>
              <option value="array">Array</option>
            </select>
            <input 
              v-model="param.example" 
              class="param-example"
              :data-testid="'param-example-' + param.id"
              placeholder="示例值"
            />
            <label class="param-required">
              <input 
                type="checkbox" 
                v-model="param.required"
                :data-testid="'param-required-' + param.id"
              />
              必填
            </label>
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
        <div class="modal-overlay" @click="closeJsonImport"></div>
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
                /> 合并模式 (保留现有参数，更新同名参数)
              </label>
              <label>
                <input 
                  type="radio" 
                  v-model="importMode" 
                  value="override"
                  data-testid="import-mode-override"
                /> 覆盖模式 (清空现有参数，导入新参数)
              </label>
            </div>
            
            <div class="json-preview" v-if="jsonPreview">
              <h4>预览 ({{ jsonPreview.length }} 个参数):</h4>
              <div class="preview-list">
                <div 
                  v-for="param in jsonPreview.slice(0, 5)" 
                  :key="param.name"
                  class="preview-item"
                >
                  <span class="preview-name">{{ param.name }}</span>
                  <span class="preview-type">{{ param.type }}</span>
                  <span class="preview-example">{{ param.example }}</span>
                </div>
                <div v-if="jsonPreview.length > 5" class="preview-more">
                  ... 还有 {{ jsonPreview.length - 5 }} 个参数
                </div>
              </div>
            </div>
            
            <div class="validation-message" v-if="validationMessage">
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
              导入 {{ jsonPreview ? '(' + jsonPreview.length + ' 个参数)' : '' }}
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
      
      <!-- 操作历史 -->
      <div class="operation-history" v-if="operationHistory.length > 0">
        <h3>操作历史:</h3>
        <div 
          v-for="(operation, index) in operationHistory" 
          :key="index"
          class="history-item"
          :data-testid="'history-' + index"
        >
          <span class="history-time">{{ operation.time }}</span>
          <span class="history-action">{{ operation.action }}</span>
          <span class="history-details">{{ operation.details }}</span>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      params: [],
      showJsonModal: false,
      jsonContent: '',
      importMode: 'merge',
      operationHistory: []
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
    
    jsonPreview() {
      if (!this.canImport) return null
      
      try {
        const jsonData = JSON.parse(this.jsonContent)
        return this.convertJsonToParams(jsonData)
      } catch (error) {
        return null
      }
    },
    
    validationMessage() {
      if (!this.jsonContent.trim()) return ''
      
      if (this.isJsonValid) {
        const preview = this.jsonPreview
        if (preview && preview.length > 0) {
          return `✓ 有效的 JSON，将导入 ${preview.length} 个参数`
        }
        return '✓ 有效的 JSON，但没有可导入的参数'
      } else {
        return '✗ 无效的 JSON 格式'
      }
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
      this.addToHistory('添加参数', `添加了新参数 ${newParam.id}`)
    },
    
    removeParam(id) {
      const index = this.params.findIndex(p => p.id === id)
      if (index > -1) {
        const param = this.params[index]
        this.params.splice(index, 1)
        this.addToHistory('删除参数', `删除了参数 "${param.name || param.id}"`)
      }
    },
    
    clearAll() {
      const count = this.params.length
      this.params = []
      this.addToHistory('清空参数', `清空了 ${count} 个参数`)
    },
    
    openJsonImport() {
      this.showJsonModal = true
      this.jsonContent = ''
      this.importMode = 'merge'
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
        const originalCount = this.params.length
        
        if (this.importMode === 'override') {
          this.params = newParams
          this.addToHistory('JSON 导入 (覆盖)', `覆盖导入 ${newParams.length} 个参数，原有 ${originalCount} 个参数被清空`)
        } else {
          // 合并模式
          let updatedCount = 0
          let addedCount = 0
          
          newParams.forEach(newParam => {
            const existingIndex = this.params.findIndex(p => p.name === newParam.name)
            if (existingIndex > -1) {
              this.params[existingIndex] = { ...this.params[existingIndex], ...newParam }
              updatedCount++
            } else {
              this.params.push(newParam)
              addedCount++
            }
          })
          
          this.addToHistory('JSON 导入 (合并)', `合并导入：更新 ${updatedCount} 个参数，新增 ${addedCount} 个参数`)
        }
        
        this.closeJsonImport()
      } catch (error) {
        console.error('JSON 导入失败:', error)
        this.addToHistory('JSON 导入失败', error.message)
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
    },
    
    addToHistory(action, details) {
      this.operationHistory.unshift({
        time: new Date().toLocaleTimeString(),
        action,
        details
      })
      
      // 保持历史记录不超过 10 条
      if (this.operationHistory.length > 10) {
        this.operationHistory = this.operationHistory.slice(0, 10)
      }
    }
  }
}

describe('JSON 导入端到端测试', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(JsonImportApp)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('完整的 JSON 导入流程', () => {
    it('应该完成完整的 JSON 导入流程', async () => {
      // 1. 验证初始状态
      expect(wrapper.find('[data-testid="param-count"]').text()).toContain('参数数量: 0')
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
      
      // 2. 打开 JSON 导入模态框
      await wrapper.find('.json-import-btn').trigger('click')
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(true)
      
      // 3. 输入 JSON 数据
      const jsonData = {
        name: 'John Doe',
        age: 30,
        email: 'john@example.com',
        active: true,
        profile: {
          bio: 'Software Developer',
          skills: ['JavaScript', 'Vue.js', 'Node.js']
        }
      }
      
      const jsonInput = wrapper.find('[data-testid="json-input"]')
      await jsonInput.setValue(JSON.stringify(jsonData, null, 2))
      
      // 4. 验证 JSON 预览
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.jsonPreview).toBeTruthy()
      expect(wrapper.vm.jsonPreview.length).toBeGreaterThan(5) // 包含嵌套对象的参数
      expect(wrapper.vm.validationMessage).toContain('有效的 JSON')
      
      // 5. 选择导入模式
      await wrapper.find('[data-testid="import-mode-override"]').trigger('click')
      expect(wrapper.vm.importMode).toBe('override')
      
      // 6. 执行导入
      await wrapper.find('[data-testid="import-btn"]').trigger('click')
      
      // 7. 验证导入结果
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
      expect(wrapper.vm.params.length).toBeGreaterThan(5)
      
      // 验证顶级参数
      const nameParam = wrapper.vm.params.find(p => p.name === 'name')
      const ageParam = wrapper.vm.params.find(p => p.name === 'age')
      const profileParam = wrapper.vm.params.find(p => p.name === 'profile')
      
      expect(nameParam).toBeTruthy()
      expect(nameParam.type).toBe('string')
      expect(nameParam.example).toBe('John Doe')
      
      expect(ageParam).toBeTruthy()
      expect(ageParam.type).toBe('number')
      expect(ageParam.example).toBe('30')
      
      expect(profileParam).toBeTruthy()
      expect(profileParam.type).toBe('object')
      
      // 验证嵌套参数
      const bioParam = wrapper.vm.params.find(p => p.name === 'bio')
      expect(bioParam).toBeTruthy()
      expect(bioParam.level).toBe(1)
      expect(bioParam.parentId).toBe(profileParam.id)
      
      // 8. 验证操作历史
      expect(wrapper.vm.operationHistory.length).toBeGreaterThan(0)
      expect(wrapper.vm.operationHistory[0].action).toContain('JSON 导入')
    })

    it('应该处理合并模式导入', async () => {
      // 1. 先添加一些现有参数
      await wrapper.find('.add-param-btn').trigger('click')
      await wrapper.find('.add-param-btn').trigger('click')
      
      wrapper.vm.params[0].name = 'existingParam1'
      wrapper.vm.params[0].type = 'string'
      wrapper.vm.params[1].name = 'existingParam2'
      wrapper.vm.params[1].type = 'number'
      
      expect(wrapper.vm.params).toHaveLength(2)
      
      // 2. 打开导入模态框
      await wrapper.find('.json-import-btn').trigger('click')
      
      // 3. 输入包含同名参数的 JSON
      const jsonData = {
        existingParam1: 'updated value',
        newParam: 'new value'
      }
      
      await wrapper.find('[data-testid="json-input"]').setValue(JSON.stringify(jsonData))
      
      // 4. 选择合并模式
      await wrapper.find('[data-testid="import-mode-merge"]').trigger('click')
      expect(wrapper.vm.importMode).toBe('merge')
      
      // 5. 执行导入
      await wrapper.find('[data-testid="import-btn"]').trigger('click')
      
      // 6. 验证合并结果
      expect(wrapper.vm.params).toHaveLength(3) // 2个原有 + 1个新增
      
      const existingParam1 = wrapper.vm.params.find(p => p.name === 'existingParam1')
      const existingParam2 = wrapper.vm.params.find(p => p.name === 'existingParam2')
      const newParam = wrapper.vm.params.find(p => p.name === 'newParam')
      
      expect(existingParam1.example).toBe('updated value') // 被更新
      expect(existingParam2.type).toBe('number') // 保持不变
      expect(newParam).toBeTruthy() // 新增
    })

    it('应该处理错误的 JSON 输入', async () => {
      // 1. 打开导入模态框
      await wrapper.find('.json-import-btn').trigger('click')
      
      // 2. 输入无效的 JSON
      await wrapper.find('[data-testid="json-input"]').setValue('{ invalid json }')
      
      // 3. 验证错误状态
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.isJsonValid).toBe(false)
      expect(wrapper.vm.canImport).toBe(false)
      expect(wrapper.vm.validationMessage).toContain('无效的 JSON')
      
      // 4. 导入按钮应该被禁用
      const importBtn = wrapper.find('[data-testid="import-btn"]')
      expect(importBtn.attributes('disabled')).toBeDefined()
      
      // 5. 修正 JSON
      await wrapper.find('[data-testid="json-input"]').setValue('{"valid": "json"}')
      
      // 6. 验证修正后的状态
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.isJsonValid).toBe(true)
      expect(wrapper.vm.canImport).toBe(true)
      expect(wrapper.vm.validationMessage).toContain('有效的 JSON')
    })

    it('应该处理取消操作', async () => {
      // 1. 打开导入模态框
      await wrapper.find('.json-import-btn').trigger('click')
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(true)
      
      // 2. 输入一些数据
      await wrapper.find('[data-testid="json-input"]').setValue('{"test": "data"}')
      
      // 3. 点击取消按钮
      await wrapper.find('[data-testid="cancel-btn"]').trigger('click')
      
      // 4. 验证模态框关闭且数据被清空
      expect(wrapper.find('[data-testid="json-import-modal"]').exists()).toBe(false)
      expect(wrapper.vm.jsonContent).toBe('')
      expect(wrapper.vm.params).toHaveLength(0) // 没有导入任何参数
    })

    it('应该处理复杂的嵌套数据结构', async () => {
      // 1. 准备复杂的嵌套 JSON
      const complexJson = {
        user: {
          personal: {
            name: 'John',
            age: 30,
            address: {
              street: '123 Main St',
              city: 'New York',
              coordinates: {
                lat: 40.7128,
                lng: -74.0060
              }
            }
          },
          professional: {
            title: 'Developer',
            company: 'Tech Corp',
            skills: ['JavaScript', 'Python', 'Go']
          }
        },
        settings: {
          theme: 'dark',
          notifications: true,
          privacy: {
            public: false,
            analytics: true
          }
        }
      }
      
      // 2. 打开导入模态框并输入数据
      await wrapper.find('.json-import-btn').trigger('click')
      await wrapper.find('[data-testid="json-input"]').setValue(JSON.stringify(complexJson))
      
      // 3. 执行导入
      await wrapper.find('[data-testid="import-btn"]').trigger('click')
      
      // 4. 验证嵌套结构
      expect(wrapper.vm.params.length).toBeGreaterThan(15) // 应该有很多参数
      
      // 验证不同层级的参数
      const userParam = wrapper.vm.params.find(p => p.name === 'user')
      const personalParam = wrapper.vm.params.find(p => p.name === 'personal')
      const nameParam = wrapper.vm.params.find(p => p.name === 'name')
      const addressParam = wrapper.vm.params.find(p => p.name === 'address')
      const coordinatesParam = wrapper.vm.params.find(p => p.name === 'coordinates')
      const latParam = wrapper.vm.params.find(p => p.name === 'lat')
      
      expect(userParam.level).toBe(0)
      expect(personalParam.level).toBe(1)
      expect(nameParam.level).toBe(2)
      expect(addressParam.level).toBe(2)
      expect(coordinatesParam.level).toBe(3)
      expect(latParam.level).toBe(4)
      
      // 验证父子关系
      expect(personalParam.parentId).toBe(userParam.id)
      expect(nameParam.parentId).toBe(personalParam.id)
      expect(latParam.parentId).toBe(coordinatesParam.id)
    })

    it('应该处理大量参数的性能测试', async () => {
      // 1. 生成大量参数的 JSON
      const largeJson = {}
      for (let i = 0; i < 500; i++) {
        largeJson[`param${i}`] = {
          value: `value${i}`,
          index: i,
          active: i % 2 === 0,
          metadata: {
            created: new Date().toISOString(),
            tags: [`tag${i}`, `category${i % 10}`]
          }
        }
      }
      
      // 2. 记录开始时间
      const startTime = performance.now()
      
      // 3. 执行导入
      await wrapper.find('.json-import-btn').trigger('click')
      await wrapper.find('[data-testid="json-input"]').setValue(JSON.stringify(largeJson))
      await wrapper.find('[data-testid="import-btn"]').trigger('click')
      
      // 4. 记录结束时间
      const endTime = performance.now()
      const duration = endTime - startTime
      
      // 5. 验证性能和结果
       expect(duration).toBeLessThan(1000) // 应该在 1 秒内完成
       expect(wrapper.vm.params.length).toBeGreaterThan(500) // 每个对象会产生多个参数
      
      // 验证参数结构
      const param0 = wrapper.vm.params.find(p => p.name === 'param0')
      const valueParam = wrapper.vm.params.find(p => p.name === 'value' && p.parentId === param0?.id)
      const metadataParam = wrapper.vm.params.find(p => p.name === 'metadata' && p.parentId === param0?.id)
      
      expect(param0).toBeTruthy()
      expect(valueParam).toBeTruthy()
      expect(metadataParam).toBeTruthy()
    })

    it('应该维护状态一致性', async () => {
      // 1. 执行多次导入操作
      const operations = [
        { json: '{"step1": "value1"}', mode: 'override' },
        { json: '{"step1": "updated1", "step2": "value2"}', mode: 'merge' },
        { json: '{"step3": "value3"}', mode: 'override' },
        { json: '{"step3": "updated3", "step4": "value4"}', mode: 'merge' }
      ]
      
      for (const operation of operations) {
        await wrapper.find('.json-import-btn').trigger('click')
        await wrapper.find('[data-testid="json-input"]').setValue(operation.json)
        await wrapper.find(`[data-testid="import-mode-${operation.mode}"]`).trigger('click')
        await wrapper.find('[data-testid="import-btn"]').trigger('click')
      }
      
      // 2. 验证最终状态
       expect(wrapper.vm.params.length).toBeGreaterThan(1) // 至少有一些参数
      
      const step3Param = wrapper.vm.params.find(p => p.name === 'step3')
      const step4Param = wrapper.vm.params.find(p => p.name === 'step4')
      
      expect(step3Param.example).toBe('updated3')
      expect(step4Param.example).toBe('value4')
      
      // 3. 验证操作历史
      expect(wrapper.vm.operationHistory.length).toBe(4)
      expect(wrapper.vm.operationHistory.every(h => h.action.includes('JSON 导入'))).toBe(true)
    })
  })
})