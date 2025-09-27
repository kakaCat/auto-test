<template>
  <div class="parameter-config">
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
          :disabled="!parameters.length"
        >
          <el-icon><Download /></el-icon>
          导出JSON
        </el-button>
      </div>
    </div>

    <!-- 表格模式 -->
    <div v-if="currentMode === 'table'" class="table-mode">
      <div class="table-header">
        <el-button type="primary" size="small" @click="addParameter">
          <el-icon><Plus /></el-icon>
          添加参数
        </el-button>
        <el-button 
          v-if="parameters.length > 0" 
          size="small" 
          @click="clearAll"
        >
          <el-icon><Delete /></el-icon>
          清空所有
        </el-button>
      </div>

      <div v-if="parameters.length > 0" class="parameter-table">
        <div class="table-headers">
          <div class="header-cell name">参数名</div>
          <div class="header-cell type">类型</div>
          <div class="header-cell required">必填</div>
          <div class="header-cell description">描述</div>
          <div class="header-cell actions">操作</div>
        </div>
        
        <draggable 
          v-model="parameters" 
          item-key="id"
          handle=".drag-handle"
          @end="handleDragEnd"
        >
          <template #item="{ element: param, index }">
            <div 
              :class="['parameter-row', { 'is-child': param.level > 0 }]"
              :style="{ paddingLeft: `${param.level * 20}px` }"
            >
              <div class="row-content">
                <div class="cell name">
                  <el-icon class="drag-handle"><Rank /></el-icon>
                  <el-input
                    v-model="param.name"
                    placeholder="参数名"
                    size="small"
                    @blur="validateParameterName(param, index)"
                  />
                  <el-button
                    v-if="param.type === 'object' || param.type === 'array'"
                    size="small"
                    text
                    @click="addChildParameter(index)"
                  >
                    <el-icon><Plus /></el-icon>
                  </el-button>
                </div>
                
                <div class="cell type">
                  <el-select
                    v-model="param.type"
                    size="small"
                    @change="handleTypeChange(param, index)"
                  >
                    <el-option label="string" value="string" />
                    <el-option label="number" value="number" />
                    <el-option label="boolean" value="boolean" />
                    <el-option label="object" value="object" />
                    <el-option label="array" value="array" />
                    <el-option label="file" value="file" />
                  </el-select>
                </div>
                
                <div class="cell required">
                  <el-switch
                    v-model="param.required"
                    size="small"
                  />
                </div>
                
                <div class="cell description">
                  <el-input
                    v-model="param.description"
                    placeholder="参数描述"
                    size="small"
                  />
                </div>
                
                <div class="cell actions">
                  <el-button-group size="small">
                    <el-button @click="moveUp(index)" :disabled="index === 0">
                      <el-icon><ArrowUp /></el-icon>
                    </el-button>
                    <el-button @click="moveDown(index)" :disabled="index === parameters.length - 1">
                      <el-icon><ArrowDown /></el-icon>
                    </el-button>
                    <el-button @click="copyParameter(index)">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                    <el-button type="danger" @click="removeParameter(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-button-group>
                </div>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <div v-else class="empty-state">
        <el-empty description="暂无参数配置">
          <el-button type="primary" @click="addParameter">添加第一个参数</el-button>
        </el-empty>
      </div>
    </div>

    <!-- JSON模式 -->
    <div v-if="currentMode === 'json'" class="json-mode">
      <div class="json-header">
        <span class="json-title">JSON Schema 编辑器</span>
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
          :rows="15"
          placeholder="请输入JSON Schema或参数示例..."
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

    <!-- 参数示例展示 -->
    <div v-if="parameters.length > 0 && currentMode === 'table'" class="parameter-example">
      <el-collapse>
        <el-collapse-item title="参数示例预览" name="example">
          <pre class="example-json">{{ parameterExample }}</pre>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Grid, Document, Plus, Delete, Upload, Download, 
  Rank, ArrowUp, ArrowDown, CopyDocument, 
  MagicStick, CircleCheck 
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  mode: {
    type: String,
    default: 'table' // table | json
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change'])

// 响应式数据
const currentMode = ref(props.mode)
const jsonContent = ref('')
const jsonError = ref('')
const parameters = ref([])
let parameterIdCounter = 0

// 计算属性
const parameterExample = computed(() => {
  return JSON.stringify(generateExample(parameters.value), null, 2)
})

// 监听器
watch(() => props.modelValue, (newValue) => {
  if (Array.isArray(newValue)) {
    parameters.value = newValue.map(param => ({
      ...param,
      id: param.id || ++parameterIdCounter,
      level: param.level || 0
    }))
  }
}, { immediate: true, deep: true })

watch(parameters, (newValue) => {
  emit('update:modelValue', newValue)
  emit('change', newValue)
}, { deep: true })

// 方法
const generateId = () => ++parameterIdCounter

const addParameter = (parentIndex = -1, level = 0) => {
  const newParam = {
    id: generateId(),
    name: '',
    type: 'string',
    required: false,
    description: '',
    level: level,
    parentId: parentIndex >= 0 ? parameters.value[parentIndex].id : null
  }
  
  if (parentIndex >= 0) {
    // 添加子参数
    parameters.value.splice(parentIndex + 1, 0, newParam)
  } else {
    // 添加顶级参数
    parameters.value.push(newParam)
  }
}

const addChildParameter = (parentIndex) => {
  const parent = parameters.value[parentIndex]
  const level = parent.level + 1
  addParameter(parentIndex, level)
}

const removeParameter = async (index) => {
  const param = parameters.value[index]
  
  // 检查是否有子参数
  const hasChildren = parameters.value.some(p => p.parentId === param.id)
  
  if (hasChildren) {
    try {
      await ElMessageBox.confirm(
        '删除此参数将同时删除其所有子参数，确认删除吗？',
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
  
  // 删除参数及其子参数
  const toRemove = [param.id]
  const findChildren = (parentId) => {
    parameters.value.forEach(p => {
      if (p.parentId === parentId) {
        toRemove.push(p.id)
        findChildren(p.id)
      }
    })
  }
  findChildren(param.id)
  
  parameters.value = parameters.value.filter(p => !toRemove.includes(p.id))
}

const moveUp = (index) => {
  if (index > 0) {
    const temp = parameters.value[index]
    parameters.value[index] = parameters.value[index - 1]
    parameters.value[index - 1] = temp
  }
}

const moveDown = (index) => {
  if (index < parameters.value.length - 1) {
    const temp = parameters.value[index]
    parameters.value[index] = parameters.value[index + 1]
    parameters.value[index + 1] = temp
  }
}

const copyParameter = (index) => {
  const original = parameters.value[index]
  const copy = {
    ...original,
    id: generateId(),
    name: original.name + '_copy'
  }
  parameters.value.splice(index + 1, 0, copy)
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确认清空所有参数配置吗？',
      '确认清空',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    parameters.value = []
  } catch {
    // 用户取消
  }
}

const handleTypeChange = (param, index) => {
  // 如果类型改为非object/array，删除子参数
  if (param.type !== 'object' && param.type !== 'array') {
    const childrenToRemove = parameters.value.filter(p => p.parentId === param.id)
    if (childrenToRemove.length > 0) {
      ElMessageBox.confirm(
        '更改参数类型将删除其所有子参数，确认更改吗？',
        '确认更改',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        const toRemove = [param.id]
        const findChildren = (parentId) => {
          parameters.value.forEach(p => {
            if (p.parentId === parentId) {
              toRemove.push(p.id)
              findChildren(p.id)
            }
          })
        }
        findChildren(param.id)
        parameters.value = parameters.value.filter(p => p.id === param.id || !toRemove.includes(p.id))
      }).catch(() => {
        // 恢复原类型
        nextTick(() => {
          param.type = param.type === 'object' ? 'array' : 'object'
        })
      })
    }
  }
}

const validateParameterName = (param, index) => {
  if (!param.name.trim()) return
  
  // 检查同级参数名重复
  const siblings = parameters.value.filter(p => p.parentId === param.parentId && p.id !== param.id)
  const duplicate = siblings.find(p => p.name === param.name)
  
  if (duplicate) {
    ElMessage.warning('参数名不能重复')
    param.name = ''
  }
}

const handleDragEnd = () => {
  // 拖拽结束后重新计算层级关系
  // 这里可以添加更复杂的层级重新计算逻辑
}

const handleModeChange = (mode) => {
  if (mode === 'json' && parameters.value.length > 0) {
    // 切换到JSON模式时，将表格数据转换为JSON
    jsonContent.value = JSON.stringify(generateJsonSchema(parameters.value), null, 2)
  } else if (mode === 'table' && jsonContent.value.trim()) {
    // 切换到表格模式时，尝试解析JSON
    try {
      const parsed = JSON.parse(jsonContent.value)
      const converted = convertJsonToParameters(parsed)
      parameters.value = converted
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
    const converted = convertJsonToParameters(parsed)
    parameters.value = converted
    currentMode.value = 'table'
    ElMessage.success('JSON转换成功')
  } catch (error) {
    ElMessage.error('JSON格式错误：' + error.message)
  }
}

const exportToJson = () => {
  if (parameters.value.length === 0) {
    ElMessage.warning('暂无参数可导出')
    return
  }
  
  const schema = generateJsonSchema(parameters.value)
  jsonContent.value = JSON.stringify(schema, null, 2)
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

// 工具函数
const generateExample = (params) => {
  const example = {}
  
  params.forEach(param => {
    if (param.level === 0) {
      example[param.name] = generateValueExample(param, params)
    }
  })
  
  return example
}

const generateValueExample = (param, allParams) => {
  switch (param.type) {
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
      const children = allParams.filter(p => p.parentId === param.id)
      children.forEach(child => {
        obj[child.name] = generateValueExample(child, allParams)
      })
      return obj
    case 'file':
      return 'file_upload'
    default:
      return null
  }
}

const generateJsonSchema = (params) => {
  const schema = {
    type: 'object',
    properties: {},
    required: []
  }
  
  params.forEach(param => {
    if (param.level === 0) {
      schema.properties[param.name] = generatePropertySchema(param, params)
      if (param.required) {
        schema.required.push(param.name)
      }
    }
  })
  
  return schema
}

const generatePropertySchema = (param, allParams) => {
  const property = {
    type: param.type,
    description: param.description
  }
  
  if (param.type === 'object') {
    property.properties = {}
    property.required = []
    
    const children = allParams.filter(p => p.parentId === param.id)
    children.forEach(child => {
      property.properties[child.name] = generatePropertySchema(child, allParams)
      if (child.required) {
        property.required.push(child.name)
      }
    })
  } else if (param.type === 'array') {
    property.items = { type: 'string' } // 简化处理
  }
  
  return property
}

const convertJsonToParameters = (json, level = 0, parentId = null) => {
  const params = []
  
  if (json.properties) {
    Object.entries(json.properties).forEach(([name, prop]) => {
      const param = {
        id: generateId(),
        name,
        type: prop.type || 'string',
        required: json.required?.includes(name) || false,
        description: prop.description || '',
        level,
        parentId
      }
      
      params.push(param)
      
      if (prop.properties) {
        const children = convertJsonToParameters(prop, level + 1, param.id)
        params.push(...children)
      }
    })
  }
  
  return params
}

// 暴露方法
defineExpose({
  addParameter,
  clearAll,
  exportToJson,
  generateFromJson
})
</script>

<style scoped>
.parameter-config {
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

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.parameter-table {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
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
.header-cell.actions { flex: 1.5; }

.parameter-row {
  border-bottom: 1px solid #f0f2f5;
  transition: all 0.2s ease;
}

.parameter-row:hover {
  background: #f8f9fa;
}

.parameter-row.is-child {
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
.cell.actions { flex: 1.5; justify-content: center; }

.drag-handle {
  cursor: move;
  color: #909399;
}

.drag-handle:hover {
  color: #409eff;
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

.parameter-example {
  margin-top: 20px;
  padding: 0 20px 20px;
}

.example-json {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #303133;
  overflow-x: auto;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
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

:deep(.el-collapse-item__header) {
  font-weight: 600;
}

:deep(.el-button-group .el-button) {
  padding: 4px 8px;
}
</style>