<template>
  <div class="response-config">
    <!-- 模式切换 -->
    <div class="mode-switcher">
      <el-radio-group v-model="currentMode" @change="handleModeChange">
        <el-radio-button label="table">
          <el-icon><Grid /></el-icon>
          表格模式
        </el-radio-button>
        <el-radio-button label="json">
          <el-icon><Document /></el-icon>
          JSON模式
        </el-radio-button>
      </el-radio-group>
      
      <div class="mode-actions">
        <el-button 
          v-if="currentMode === 'json'" 
          size="small" 
          @click="generateFromJson"
          :disabled="!jsonContent.trim()"
        >
          <el-icon><Upload /></el-icon>
          从JSON生成表格
        </el-button>
        <el-button 
          v-if="currentMode === 'table'" 
          size="small" 
          @click="exportToJson"
          :disabled="!responses.length"
        >
          <el-icon><Download /></el-icon>
          导出JSON
        </el-button>
      </div>
    </div>

    <!-- 表格模式 -->
    <div v-if="currentMode === 'table'" class="table-mode">
      <!-- 状态码标签页 -->
      <el-tabs v-model="activeStatusCode" @tab-click="handleTabClick">
        <el-tab-pane
          v-for="response in responses"
          :key="response.statusCode"
          :label="`${response.statusCode} ${getStatusText(response.statusCode)}`"
          :name="response.statusCode"
        >
          <template #label>
            <span :class="['status-tab', getStatusType(response.statusCode)]">
              {{ response.statusCode }} {{ getStatusText(response.statusCode) }}
              <el-button
                v-if="responses.length > 1"
                size="small"
                text
                @click.stop="removeStatusCode(response.statusCode)"
              >
                <el-icon><Close /></el-icon>
              </el-button>
            </span>
          </template>
          
          <!-- 响应字段配置 -->
          <div class="response-fields">
            <div class="fields-header">
              <el-input
                v-model="response.description"
                placeholder="响应描述"
                style="width: 300px"
              />
              <div class="field-actions">
                <el-button size="small" @click="addField(response.statusCode)">
                  <el-icon><Plus /></el-icon>
                  添加字段
                </el-button>
                <el-button 
                  v-if="response.fields.length > 0" 
                  size="small" 
                  @click="clearFields(response.statusCode)"
                >
                  <el-icon><Delete /></el-icon>
                  清空字段
                </el-button>
              </div>
            </div>

            <div v-if="response.fields.length > 0" class="fields-table">
              <div class="table-headers">
                <div class="header-cell name">字段名</div>
                <div class="header-cell type">类型</div>
                <div class="header-cell required">必返</div>
                <div class="header-cell description">描述</div>
                <div class="header-cell actions">操作</div>
              </div>
              
              <draggable 
                v-model="response.fields" 
                item-key="id"
                handle=".drag-handle"
              >
                <template #item="{ element: field, index }">
                  <div 
                    :class="['field-row', { 'is-child': field.level > 0 }]"
                    :style="{ paddingLeft: `${field.level * 20}px` }"
                  >
                    <div class="row-content">
                      <div class="cell name">
                        <el-icon class="drag-handle"><Rank /></el-icon>
                        <el-input
                          v-model="field.name"
                          placeholder="字段名"
                          size="small"
                        />
                        <el-button
                          v-if="field.type === 'object' || field.type === 'array'"
                          size="small"
                          text
                          @click="addChildField(response.statusCode, index)"
                        >
                          <el-icon><Plus /></el-icon>
                        </el-button>
                      </div>
                      
                      <div class="cell type">
                        <el-select
                          v-model="field.type"
                          size="small"
                          @change="handleFieldTypeChange(field, index, response.statusCode)"
                        >
                          <el-option label="string" value="string" />
                          <el-option label="number" value="number" />
                          <el-option label="boolean" value="boolean" />
                          <el-option label="object" value="object" />
                          <el-option label="array" value="array" />
                          <el-option label="null" value="null" />
                        </el-select>
                      </div>
                      
                      <div class="cell required">
                        <el-switch
                          v-model="field.required"
                          size="small"
                        />
                      </div>
                      
                      <div class="cell description">
                        <el-input
                          v-model="field.description"
                          placeholder="字段描述"
                          size="small"
                        />
                      </div>
                      
                      <div class="cell actions">
                        <el-button-group size="small">
                          <el-button @click="copyField(response.statusCode, index)">
                            <el-icon><CopyDocument /></el-icon>
                          </el-button>
                          <el-button type="danger" @click="removeField(response.statusCode, index)">
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </el-button-group>
                      </div>
                    </div>
                  </div>
                </template>
              </draggable>
            </div>

            <div v-else class="empty-fields">
              <el-empty description="暂无响应字段">
                <el-button type="primary" @click="addField(response.statusCode)">
                  添加第一个字段
                </el-button>
              </el-empty>
            </div>

            <!-- 响应示例 -->
            <div class="response-example">
              <div class="example-header">
                <span>响应示例</span>
                <el-button size="small" @click="generateExample(response.statusCode)">
                  <el-icon><MagicStick /></el-icon>
                  自动生成
                </el-button>
              </div>
              <el-input
                v-model="response.example"
                type="textarea"
                :rows="6"
                placeholder="请输入响应示例（JSON格式）"
              />
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 添加状态码按钮 -->
        <template #addable>
          <el-dropdown @command="addStatusCode">
            <el-button size="small">
              <el-icon><Plus /></el-icon>
              添加状态码
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="200">200 成功</el-dropdown-item>
                <el-dropdown-item command="400">400 请求错误</el-dropdown-item>
                <el-dropdown-item command="401">401 未授权</el-dropdown-item>
                <el-dropdown-item command="403">403 禁止访问</el-dropdown-item>
                <el-dropdown-item command="404">404 未找到</el-dropdown-item>
                <el-dropdown-item command="500">500 服务器错误</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-tabs>
    </div>

    <!-- JSON模式 -->
    <div v-if="currentMode === 'json'" class="json-mode">
      <div class="json-header">
        <span class="json-title">响应参数JSON编辑器</span>
        <div class="json-actions">
          <el-button size="small" @click="formatJson">
            <el-icon><MagicStick /></el-icon>
            格式化
          </el-button>
          <el-button size="small" @click="validateJson">
            <el-icon><CircleCheck /></el-icon>
            验证
          </el-button>
        </div>
      </div>
      
      <div class="json-editor">
        <el-input
          v-model="jsonContent"
          type="textarea"
          :rows="20"
          placeholder="请输入响应示例JSON..."
          @blur="validateJson"
        />
      </div>
      
      <div v-if="jsonError" class="json-error">
        <el-alert
          :title="jsonError"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Grid, Document, Plus, Delete, Upload, Download, Close,
  Rank, CopyDocument, MagicStick, CircleCheck 
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  mode: {
    type: String,
    default: 'table'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change'])

// 响应式数据
const currentMode = ref(props.mode)
const jsonContent = ref('')
const jsonError = ref('')
const responses = ref([])
const activeStatusCode = ref('200')
let fieldIdCounter = 0

// 状态码映射
const statusCodeMap = {
  200: '成功',
  400: '请求错误',
  401: '未授权',
  403: '禁止访问',
  404: '未找到',
  500: '服务器错误'
}

// 工具函数 - 按依赖顺序声明，确保所有函数在调用前已声明

// 1. 基础工具函数
const generateId = () => ++fieldIdCounter

const getStatusText = (code) => statusCodeMap[code] || '自定义'

const getStatusType = (code) => {
  const num = parseInt(code)
  if (num >= 200 && num < 300) return 'success'
  if (num >= 300 && num < 400) return 'warning'
  if (num >= 400 && num < 500) return 'danger'
  if (num >= 500) return 'error'
  return 'info'
}

// 2. 数据生成函数（按依赖顺序）
const generateFieldValue = (field, allFields) => {
  switch (field.type) {
    case 'string':
      return 'string_value'
    case 'number':
      return 123
    case 'boolean':
      return true
    case 'array':
      return ['item1', 'item2']
    case 'object':
      const obj = {}
      const children = allFields.filter(f => f.parentId === field.id)
      children.forEach(child => {
        obj[child.name] = generateFieldValue(child, allFields)
      })
      return obj
    case 'null':
      return null
    default:
      return null
  }
}

const generateExampleFromFields = (fields) => {
  const example = {}
  
  fields.forEach(field => {
    if (field.level === 0) {
      example[field.name] = generateFieldValue(field, fields)
    }
  })
  
  return example
}

const generateResponseJson = (responses) => {
  const result = {}
  
  responses.forEach(response => {
    result[response.statusCode] = {
      description: response.description,
      example: response.example ? JSON.parse(response.example || '{}') : generateExampleFromFields(response.fields)
    }
  })
  
  return result
}

// 将示例JSON转换为字段列表（与请求参数一致的推断规则）
const inferType = (value) => {
  if (value === null) return 'null'
  if (Array.isArray(value)) return 'array'
  switch (typeof value) {
    case 'string': return 'string'
    case 'number': return 'number'
    case 'boolean': return 'boolean'
    case 'object': return 'object'
    default: return 'string'
  }
}

const convertExampleToParameters = (data, level = 0, parentId = null) => {
  const fields = []
  if (typeof data !== 'object' || data === null) {
    return fields
  }
  
  // 对象：逐键生成字段
  Object.entries(data).forEach(([key, value]) => {
    const type = inferType(value)
    const id = generateId()
    const field = {
      id,
      name: key,
      type,
      required: true,
      description: '',
      level,
      parentId
    }
    fields.push(field)
    
    // 嵌套结构处理
    if (type === 'object') {
      fields.push(...convertExampleToParameters(value, level + 1, id))
    } else if (type === 'array') {
      const first = value.length > 0 ? value[0] : null
      const itemType = inferType(first)
      if (itemType === 'object') {
        fields.push(...convertExampleToParameters(first || {}, level + 1, id))
      }
      // 原生类型数组无需额外子字段
    }
  })
  
  return fields
}

// 3. 初始化函数
const initializeDefaultResponse = () => {
  responses.value = [{
    statusCode: '200',
    description: '成功响应',
    fields: [],
    example: ''
  }]
  activeStatusCode.value = '200'
}

const convertJsonToResponses = (json) => {
  const newResponses = []
  
  Object.entries(json).forEach(([statusCode, config]) => {
    let exampleObj = {}
    if (config && typeof config === 'object' && 'example' in config) {
      const ex = config.example
      if (typeof ex === 'string') {
        try { exampleObj = JSON.parse(ex) } catch { exampleObj = {} }
      } else {
        exampleObj = ex || {}
      }
    } else {
      // 如果没有标准结构，则将整个config视为示例JSON
      exampleObj = config || {}
    }

    const fields = convertExampleToParameters(exampleObj)

    newResponses.push({
      statusCode,
      description: (config && config.description) || statusCodeMap[statusCode] || '自定义响应',
      fields,
      example: JSON.stringify(exampleObj || {}, null, 2)
    })
  })
  
  if (newResponses.length === 0) {
    initializeDefaultResponse()
  } else {
    responses.value = newResponses
    activeStatusCode.value = newResponses[0].statusCode
  }
}

// 监听器
let isInternalUpdate = false

watch(() => props.modelValue, (newValue) => {
  if (isInternalUpdate) return // 防止内部更新触发循环
  
  if (newValue) {
    try {
      const parsed = JSON.parse(newValue)
      if (typeof parsed === 'object') {
        convertJsonToResponses(parsed)
      }
    } catch {
      jsonContent.value = newValue
    }
  } else {
    initializeDefaultResponse()
  }
}, { immediate: true })

watch(responses, (newValue) => {
  isInternalUpdate = true
  const result = generateResponseJson(newValue)
  emit('update:modelValue', result)
  emit('change', result)
  nextTick(() => {
    isInternalUpdate = false
  })
}, { deep: true })

// 4. 状态码管理函数

const addStatusCode = (code) => {
  const exists = responses.value.find(r => r.statusCode === code)
  if (exists) {
    ElMessage.warning('该状态码已存在')
    return
  }
  
  responses.value.push({
    statusCode: code,
    description: statusCodeMap[code] || '自定义响应',
    fields: [],
    example: ''
  })
  
  activeStatusCode.value = code
}

const removeStatusCode = async (code) => {
  if (responses.value.length <= 1) {
    ElMessage.warning('至少需要保留一个状态码')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认删除状态码 ${code} 及其所有配置吗？`,
      '确认删除',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    responses.value = responses.value.filter(r => r.statusCode !== code)
    
    if (activeStatusCode.value === code) {
      activeStatusCode.value = responses.value[0].statusCode
    }
  } catch {
    // 用户取消
  }
}

const addField = (statusCode, parentIndex = -1, level = 0) => {
  const response = responses.value.find(r => r.statusCode === statusCode)
  if (!response) return
  
  const newField = {
    id: generateId(),
    name: '',
    type: 'string',
    required: false,
    description: '',
    level: level,
    parentId: parentIndex >= 0 ? response.fields[parentIndex].id : null
  }
  
  if (parentIndex >= 0) {
    response.fields.splice(parentIndex + 1, 0, newField)
  } else {
    response.fields.push(newField)
  }
}

const addChildField = (statusCode, parentIndex) => {
  const response = responses.value.find(r => r.statusCode === statusCode)
  if (!response) return
  
  const parent = response.fields[parentIndex]
  const level = parent.level + 1
  addField(statusCode, parentIndex, level)
}

const removeField = async (statusCode, index) => {
  const response = responses.value.find(r => r.statusCode === statusCode)
  if (!response) return
  
  const field = response.fields[index]
  
  // 检查是否有子字段
  const hasChildren = response.fields.some(f => f.parentId === field.id)
  
  if (hasChildren) {
    try {
      await ElMessageBox.confirm(
        '删除此字段将同时删除其所有子字段，确认删除吗？',
        '确认删除',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }
  }
  
  // 删除字段及其子字段
  const toRemove = [field.id]
  const findChildren = (parentId) => {
    response.fields.forEach(f => {
      if (f.parentId === parentId) {
        toRemove.push(f.id)
        findChildren(f.id)
      }
    })
  }
  findChildren(field.id)
  
  response.fields = response.fields.filter(f => !toRemove.includes(f.id))
}

const copyField = (statusCode, index) => {
  const response = responses.value.find(r => r.statusCode === statusCode)
  if (!response) return
  
  const original = response.fields[index]
  const copy = {
    ...original,
    id: generateId(),
    name: original.name + '_copy'
  }
  response.fields.splice(index + 1, 0, copy)
}

const clearFields = async (statusCode) => {
  try {
    await ElMessageBox.confirm(
      '确认清空所有响应字段吗？',
      '确认清空',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = responses.value.find(r => r.statusCode === statusCode)
    if (response) {
      response.fields = []
    }
  } catch {
    // 用户取消
  }
}

const handleFieldTypeChange = (field, index, statusCode) => {
  if (field.type !== 'object' && field.type !== 'array') {
    const response = responses.value.find(r => r.statusCode === statusCode)
    if (!response) return
    
    const childrenToRemove = response.fields.filter(f => f.parentId === field.id)
    if (childrenToRemove.length > 0) {
      ElMessageBox.confirm(
        '更改字段类型将删除其所有子字段，确认更改吗？',
        '确认更改',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        const toRemove = [field.id]
        const findChildren = (parentId) => {
          response.fields.forEach(f => {
            if (f.parentId === parentId) {
              toRemove.push(f.id)
              findChildren(f.id)
            }
          })
        }
        findChildren(field.id)
        response.fields = response.fields.filter(f => f.id === field.id || !toRemove.includes(f.id))
      }).catch(() => {
        // 恢复原类型
        nextTick(() => {
          field.type = field.type === 'object' ? 'array' : 'object'
        })
      })
    }
  }
}

const generateExample = (statusCode) => {
  const response = responses.value.find(r => r.statusCode === statusCode)
  if (!response) return
  
  const example = generateExampleFromFields(response.fields)
  response.example = JSON.stringify(example, null, 2)
}



const handleTabClick = (tab) => {
  activeStatusCode.value = tab.name
}

const handleModeChange = (mode) => {
  if (mode === 'json' && responses.value.length > 0) {
    jsonContent.value = JSON.stringify(generateResponseJson(responses.value), null, 2)
  } else if (mode === 'table' && jsonContent.value.trim()) {
    try {
      const parsed = JSON.parse(jsonContent.value)
      convertJsonToResponses(parsed)
    } catch (error) {
      ElMessage.warning('JSON格式有误，无法转换为表格模式')
      currentMode.value = 'json'
    }
  }
}

const generateFromJson = () => {
  if (!jsonContent.value.trim()) {
    ElMessage.warning('请先输入JSON内容')
    return
  }
  
  try {
    const parsed = JSON.parse(jsonContent.value)
    convertJsonToResponses(parsed)
    currentMode.value = 'table'
    ElMessage.success('JSON转换成功')
  } catch (error) {
    ElMessage.error('JSON格式错误：' + error.message)
  }
}

const exportToJson = () => {
  if (responses.value.length === 0) {
    ElMessage.warning('暂无响应配置可导出')
    return
  }
  
  const json = generateResponseJson(responses.value)
  jsonContent.value = JSON.stringify(json, null, 2)
  currentMode.value = 'json'
  ElMessage.success('导出JSON成功')
}

const formatJson = () => {
  try {
    const parsed = JSON.parse(jsonContent.value)
    jsonContent.value = JSON.stringify(parsed, null, 2)
    jsonError.value = ''
    ElMessage.success('JSON格式化成功')
  } catch (error) {
    ElMessage.error('JSON格式错误：' + error.message)
  }
}

const validateJson = () => {
  if (!jsonContent.value.trim()) {
    jsonError.value = ''
    return
  }
  
  try {
    JSON.parse(jsonContent.value)
    jsonError.value = ''
  } catch (error) {
    jsonError.value = 'JSON格式错误：' + error.message
  }
}

// 初始化
if (!responses.value.length) {
  initializeDefaultResponse()
}

// 暴露方法
defineExpose({
  addStatusCode,
  generateExample,
  exportToJson,
  generateFromJson
})
</script>

<style scoped>
.response-config {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.mode-switcher {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-bottom: 1px solid #e4e7ed;
}

.mode-actions {
  display: flex;
  gap: 8px;
}

.table-mode {
  padding: 20px;
}

.status-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tab.success { background: #f0f9ff; color: #059669; }
.status-tab.warning { background: #fffbeb; color: #d97706; }
.status-tab.danger { background: #fef2f2; color: #dc2626; }
.status-tab.error { background: #fef2f2; color: #dc2626; }
.status-tab.info { background: #f0f9ff; color: #2563eb; }

.response-fields {
  margin-top: 16px;
}

.fields-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.field-actions {
  display: flex;
  gap: 8px;
}

.fields-table {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.table-headers {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  color: #303133;
}

.header-cell {
  padding: 12px;
  border-right: 1px solid #e4e7ed;
}

.header-cell:last-child {
  border-right: none;
}

.header-cell.name { flex: 2; }
.header-cell.type { flex: 1; }
.header-cell.required { flex: 0.8; }
.header-cell.description { flex: 2; }
.header-cell.actions { flex: 1.2; }

.field-row {
  border-bottom: 1px solid #f0f2f5;
  transition: all 0.2s ease;
}

.field-row:hover {
  background: #f8f9fa;
}

.field-row.is-child {
  background: #fafbfc;
}

.row-content {
  display: flex;
  align-items: center;
}

.cell {
  padding: 12px;
  border-right: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cell:last-child {
  border-right: none;
}

.cell.name { flex: 2; }
.cell.type { flex: 1; }
.cell.required { flex: 0.8; justify-content: center; }
.cell.description { flex: 2; }
.cell.actions { flex: 1.2; justify-content: center; }

.drag-handle {
  cursor: move;
  color: #909399;
}

.drag-handle:hover {
  color: #409eff;
}

.empty-fields {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 20px;
}

.response-example {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.example-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}

.json-mode {
  padding: 20px;
}

.json-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.json-title {
  font-weight: 600;
  color: #303133;
}

.json-actions {
  display: flex;
  gap: 8px;
}

.json-editor {
  margin-bottom: 16px;
}

.json-error {
  margin-top: 16px;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  border-radius: 8px;
}

:deep(.el-button-group .el-button) {
  padding: 4px 8px;
}
</style>