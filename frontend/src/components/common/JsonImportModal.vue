<template>
  <el-dialog
    v-model="visible"
    title="JSON 导入"
    width="80%"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="json-import-modal"
    @close="handleClose"
  >
    <div class="modal-content">
      <!-- 左侧：JSON 编辑器 -->
      <div class="editor-section">
        <div class="section-header">
          <h3>JSON 数据</h3>
        </div>
        
        <div class="json-editor-container">
          <JsonEditor
            v-model="jsonContent"
            height="350px"
            placeholder="请输入 JSON 数据或 JSON Schema..."
            @change="handleJsonInput"
            @validate="handleJsonValidate"
            @format="handleJsonFormat"
          />
        </div>
        
        <!-- JSON 统计信息 -->
        <div
          v-if="jsonStats.isValid"
          class="json-stats"
        >
          <el-tag
            size="small"
            type="success"
          >
            <el-icon><CircleCheck /></el-icon>
            有效 JSON
          </el-tag>
          <span class="stats-text">
            {{ previewData.length }} 个参数 | 最大层级 {{ jsonStats.maxDepth }}
          </span>
        </div>
      </div>

      <!-- 右侧：预览和配置 -->
      <div class="preview-section">
        <!-- 导入选项配置 -->
        <div class="import-options">
          <div class="section-header">
            <h3>导入选项</h3>
          </div>
          
          <el-form
            :model="importOptions"
            label-width="120px"
            size="small"
          >
            <el-form-item label="导入模式">
              <el-radio-group v-model="importOptions.mode">
                <el-radio label="merge">
                  合并模式
                </el-radio>
                <el-radio label="override">
                  覆盖模式
                </el-radio>
              </el-radio-group>
              <div class="option-description">
                {{ importOptions.mode === 'merge' ? '与现有参数合并，保留未冲突的参数' : '完全替换现有参数' }}
              </div>
            </el-form-item>
            
            <el-form-item label="数组处理">
              <el-select
                v-model="importOptions.arrayStyle"
                placeholder="选择数组处理方式"
              >
                <el-option
                  label="展开数组项"
                  value="expand"
                />
                <el-option
                  label="仅数组类型"
                  value="type-only"
                />
                <el-option
                  label="首项示例"
                  value="first-item"
                />
              </el-select>
              <div class="option-description">
                {{ getArrayStyleDescription(importOptions.arrayStyle) }}
              </div>
            </el-form-item>
            
            <el-form-item label="空值处理">
              <el-select
                v-model="importOptions.nullHandling"
                placeholder="选择空值处理方式"
              >
                <el-option
                  label="保留为 null"
                  value="keep"
                />
                <el-option
                  label="转为字符串"
                  value="string"
                />
                <el-option
                  label="跳过空值"
                  value="skip"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="最大层级">
              <el-input-number
                v-model="importOptions.maxDepth"
                :min="1"
                :max="10"
                controls-position="right"
              />
              <div class="option-description">
                限制导入的最大嵌套层级，超出部分将被忽略
              </div>
            </el-form-item>
            
            <el-form-item label="自动推断">
              <el-switch v-model="importOptions.autoInferTypes" />
              <span class="option-label">自动推断字段类型</span>
            </el-form-item>
            
            <el-form-item label="必填字段">
              <el-switch v-model="importOptions.defaultRequired" />
              <span class="option-label">默认设置为必填</span>
            </el-form-item>
          </el-form>
        </div>

        <!-- 冲突检测 -->
        <div
          v-if="conflicts.length > 0 && importOptions.mode === 'merge'"
          class="conflict-section"
        >
          <ConflictHighlight
            :conflicts="conflicts"
            @resolve="handleConflictResolve"
            @resolve-all="handleConflictResolveAll"
          />
        </div>

        <!-- 预览树 -->
        <div class="preview-tree">
          <div class="section-header">
            <h3>预览结果</h3>
            <div class="preview-tags">
              <el-tag
                v-if="previewData.length > 0"
                size="small"
                type="primary"
              >
                {{ previewData.length }} 个参数
              </el-tag>
              <el-tag
                v-if="conflicts.length > 0"
                size="small"
                type="warning"
              >
                {{ conflicts.length }} 个冲突
              </el-tag>
            </div>
          </div>
          
          <div
            v-if="previewData.length > 0"
            class="tree-container"
          >
            <JsonPreviewTree :data="previewData" />
          </div>
          
          <div
            v-else-if="jsonContent.trim() && !jsonError"
            class="preview-empty"
          >
            <el-empty description="解析中..." />
          </div>
          
          <div
            v-else
            class="preview-placeholder"
          >
            <el-empty description="请输入 JSON 数据查看预览" />
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <template #footer>
      <div class="modal-footer">
        <div class="footer-info">
          <span
            v-if="previewData.length > 0"
            class="import-summary"
          >
            将导入 {{ previewData.length }} 个参数
            <span v-if="importOptions.mode === 'merge'">（合并模式）</span>
            <span v-else>（覆盖模式）</span>
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="handleClose">
            取消
          </el-button>
          <el-button 
            type="primary" 
            :disabled="!canImport"
            :loading="importing"
            @click="handleImport"
          >
            <el-icon><Upload /></el-icon>
            导入参数
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { 
  Upload, DataAnalysis, Folder, CircleCheck
} from '@element-plus/icons-vue'
import JsonEditor from './JsonEditor.vue'
import JsonPreviewTree from './JsonPreviewTree.vue'
import ConflictHighlight from './ConflictHighlight.vue'
import SchemaConverter from '../../utils/schemaConversion.ts'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  existingParams: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'import', 'close'])

// 响应式状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const jsonContent = ref('')
const jsonError = ref('')
const importing = ref(false)
const previewData = ref([])
const conflicts = ref([])

// 导入选项配置
const importOptions = ref({
  mode: 'merge',           // merge | override
  arrayStyle: 'expand',    // expand | type-only | first-item
  nullHandling: 'keep',    // keep | string | skip
  maxDepth: 5,             // 最大层级
  autoInferTypes: true,    // 自动推断类型
  defaultRequired: false   // 默认必填
})

// JSON 统计信息
const jsonStats = computed(() => {
  if (!jsonContent.value.trim() || jsonError.value) {
    return { isValid: false, nodeCount: 0, maxDepth: 0 }
  }
  
  try {
    const parsed = JSON.parse(jsonContent.value)
    const stats = calculateJsonStats(parsed)
    return { isValid: true, ...stats }
  } catch (e) {
    return { isValid: false, nodeCount: 0, maxDepth: 0 }
  }
})

// 是否可以导入
const canImport = computed(() => {
  return jsonContent.value.trim() && 
         !jsonError.value && 
         previewData.value.length > 0 && 
         !importing.value
})

// 工具函数
const calculateJsonStats = (obj, depth = 0) => {
  let nodeCount = 0
  let maxDepth = depth
  
  const traverse = (value, currentDepth) => {
    nodeCount++
    maxDepth = Math.max(maxDepth, currentDepth)
    
    if (Array.isArray(value)) {
      value.forEach(item => {
        if (typeof item === 'object' && item !== null) {
          traverse(item, currentDepth + 1)
        } else {
          nodeCount++
        }
      })
    } else if (typeof value === 'object' && value !== null) {
      Object.values(value).forEach(val => {
        traverse(val, currentDepth + 1)
      })
    }
  }
  
  traverse(obj, 0)
  return { nodeCount, maxDepth }
}

const getArrayStyleDescription = (style) => {
  switch (style) {
    case 'expand':
      return '展开数组中的每个元素作为独立参数'
    case 'type-only':
      return '仅创建数组类型参数，不展开内容'
    case 'first-item':
      return '使用数组第一个元素作为示例结构'
    default:
      return ''
  }
}

// JSON 处理方法
const handleJsonInput = () => {
  jsonError.value = ''
  updatePreview()
}

const handleJsonValidate = (validateResult) => {
  if (validateResult.valid) {
    jsonError.value = ''
  } else {
    jsonError.value = validateResult.error?.description || 'JSON 格式错误'
  }
  updatePreview()
}

const handleJsonFormat = () => {
  // JsonEditor 组件内部处理格式化
  updatePreview()
}

// JSON 验证方法
const validateJson = () => {
  if (!jsonContent.value.trim()) {
    return false
  }
  
  try {
    JSON.parse(jsonContent.value)
    return true
  } catch (e) {
    return false
  }
}

// 预览更新
const updatePreview = () => {
  if (!validateJson()) {
    previewData.value = []
    conflicts.value = []
    return
  }
  
  try {
    const parsed = JSON.parse(jsonContent.value)
    const newParams = convertJsonToParams(parsed)
    
    // 如果是合并模式，检测冲突
    if (importOptions.value.mode === 'merge' && props.existingParams?.length > 0) {
      const result = SchemaConverter.mergeParams(props.existingParams, newParams, {
        arrayStyle: importOptions.value.arrayStyle,
        detectConflicts: true
      })
      previewData.value = result.params
      conflicts.value = result.conflicts || []
    } else {
      previewData.value = newParams
      conflicts.value = []
    }
  } catch (e) {
    previewData.value = []
    conflicts.value = []
  }
}

// JSON 转换为参数格式
const convertJsonToParams = (data, level = 0, parentId = null) => {
  const result = []
  let idCounter = Date.now()
  
  const generateId = () => `import_${++idCounter}`
  
  const processValue = (key, value, currentLevel, currentParentId) => {
    if (currentLevel >= importOptions.value.maxDepth) return []
    
    const id = generateId()
    const param = {
      id,
      name: key,
      level: currentLevel,
      parentId: currentParentId,
      required: importOptions.value.defaultRequired,
      description: ''
    }
    
    // 处理 null 值
    if (value === null) {
      switch (importOptions.value.nullHandling) {
        case 'skip':
          return []
        case 'string':
          param.type = 'string'
          break
        default:
          param.type = 'string'
      }
      return [param]
    }
    
    // 处理数组
    if (Array.isArray(value)) {
      param.type = 'array'
      const children = []
      
      if (importOptions.value.arrayStyle === 'expand') {
        value.forEach((item, index) => {
          children.push(...processValue(index.toString(), item, currentLevel + 1, id))
        })
      } else if (importOptions.value.arrayStyle === 'first-item' && value.length > 0) {
        children.push(...processValue('0', value[0], currentLevel + 1, id))
      }
      
      return [param, ...children]
    }
    
    // 处理对象
    if (typeof value === 'object') {
      param.type = 'object'
      const children = []
      
      Object.entries(value).forEach(([childKey, childValue]) => {
        children.push(...processValue(childKey, childValue, currentLevel + 1, id))
      })
      
      return [param, ...children]
    }
    
    // 处理基本类型
    if (importOptions.value.autoInferTypes) {
      param.type = typeof value
      if (param.type === 'number' && !Number.isInteger(value)) {
        param.type = 'number'
      }
    } else {
      param.type = 'string'
    }
    
    return [param]
  }
  
  if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
    Object.entries(data).forEach(([key, value]) => {
      result.push(...processValue(key, value, level, parentId))
    })
  }
  
  return result
}

// 冲突处理
const handleConflictResolve = (conflictId, resolution) => {
  const conflictIndex = conflicts.value.findIndex(c => c.id === conflictId)
  if (conflictIndex === -1) return
  
  const conflict = conflicts.value[conflictIndex]
  
  // 根据解决方案更新参数
  const paramIndex = previewData.value.findIndex(p => p.id === conflict.paramId)
  if (paramIndex !== -1) {
    const param = previewData.value[paramIndex]
    
    switch (resolution.action) {
      case 'keep-existing':
        // 保持现有参数，从预览中移除新参数
        previewData.value.splice(paramIndex, 1)
        break
      case 'use-incoming':
        // 使用新参数，保持当前状态
        break
      case 'manual-edit':
        // 手动编辑，应用用户的修改
        Object.assign(param, resolution.value)
        break
    }
  }
  
  // 移除已解决的冲突
  conflicts.value.splice(conflictIndex, 1)
}

const handleConflictResolveAll = (action) => {
  conflicts.value.forEach(conflict => {
    handleConflictResolve(conflict.id, { action })
  })
}

// 事件处理
const handleClose = () => {
  visible.value = false
  emit('close')
}

const handleImport = async () => {
  if (!canImport.value) return
  
  importing.value = true
  
  try {
    await nextTick()
    
    const importData = {
      params: previewData.value,
      options: { ...importOptions.value },
      stats: jsonStats.value
    }
    
    emit('import', importData)
    
    // 重置状态
    jsonContent.value = ''
    jsonError.value = ''
    previewData.value = []
    
    visible.value = false
  } catch (error) {
    console.error('导入失败:', error)
  } finally {
    importing.value = false
  }
}

// 监听选项变化，更新预览
watch(importOptions, updatePreview, { deep: true })
watch(jsonContent, updatePreview)
</script>

<style scoped>
.json-import-modal {
  --el-dialog-padding-primary: 0;
}

.modal-content {
  display: flex;
  height: 600px;
  gap: 20px;
  padding: 20px;
}

.editor-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.preview-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.preview-tags {
  display: flex;
  gap: 8px;
}

.conflict-section {
  margin-bottom: 16px;
  padding: 16px;
  background: var(--el-color-warning-light-9);
  border: 1px solid var(--el-color-warning-light-7);
  border-radius: 6px;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.json-editor-container {
  flex: 1;
  margin-bottom: 12px;
}

.json-editor {
  height: 100%;
}

.json-editor :deep(.el-textarea__inner) {
  height: 100% !important;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.json-error {
  margin-bottom: 12px;
}

.json-stats {
  display: flex;
  gap: 8px;
}

.import-options {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.option-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.option-label {
  margin-left: 8px;
  font-size: 14px;
  color: #606266;
}

.preview-tree {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.tree-container {
  flex: 1;
  overflow: auto;
  margin-top: 12px;
}

.preview-empty,
.preview-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.footer-info {
  flex: 1;
}

.import-summary {
  font-size: 14px;
  color: #606266;
}

.footer-actions {
  display: flex;
  gap: 12px;
}
</style>