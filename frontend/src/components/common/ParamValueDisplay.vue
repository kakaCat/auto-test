<template>
  <div class="param-value-display">
    <div class="param-header">
      <span class="param-name">{{ param.name }}</span>
      <el-tag :type="getTypeTagType(param.type)" size="small" class="param-type">
        {{ getTypeText(param.type) }}
      </el-tag>
      <el-tag v-if="param.required" type="danger" size="small" class="required-tag">
        必填
      </el-tag>
    </div>
    
    <div v-if="param.description" class="param-description">
      {{ param.description }}
    </div>
    
    <div class="param-value">
      <div class="value-label">示例值:</div>
      <div class="value-content" :class="`value-${param.type}`">
        <template v-if="param.type === 'object'">
          <pre class="json-value">{{ formatObjectValue(param.value) }}</pre>
        </template>
        <template v-else-if="param.type === 'array'">
          <div class="array-value">
            <el-tag
              v-for="(item, index) in getArrayItems(param.value)"
              :key="index"
              size="small"
              class="array-item"
            >
              {{ item }}
            </el-tag>
          </div>
        </template>
        <template v-else-if="param.type === 'boolean'">
          <el-switch
            :model-value="param.value"
            disabled
            class="boolean-value"
          />
          <span class="boolean-text">{{ param.value ? 'true' : 'false' }}</span>
        </template>
        <template v-else-if="param.type === 'null'">
          <span class="null-value">null</span>
        </template>
        <template v-else-if="param.type === 'file'">
          <div class="file-value">
            <el-icon><Document /></el-icon>
            <span>{{ getFileName(param.value) }}</span>
          </div>
        </template>
        <template v-else>
          <span class="simple-value">{{ formatSimpleValue(param.value) }}</span>
        </template>
      </div>
    </div>
    
    <div v-if="showMetadata" class="param-metadata">
      <div class="metadata-item">
        <span class="metadata-label">层级:</span>
        <span class="metadata-value">{{ param.level || 0 }}</span>
      </div>
      <div v-if="param.parentId" class="metadata-item">
        <span class="metadata-label">父级ID:</span>
        <span class="metadata-value">{{ param.parentId }}</span>
      </div>
      <div class="metadata-item">
        <span class="metadata-label">ID:</span>
        <span class="metadata-value">{{ param.id }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Document } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  param: {
    type: Object,
    required: true
  },
  showMetadata: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

// 计算属性和方法
const getTypeTagType = (type) => {
  switch (type) {
    case 'string': return 'primary'
    case 'number': return 'success'
    case 'boolean': return 'warning'
    case 'object': return 'info'
    case 'array': return 'danger'
    case 'file': return 'warning'
    case 'null': return 'info'
    default: return 'default'
  }
}

const getTypeText = (type) => {
  switch (type) {
    case 'string': return '字符串'
    case 'number': return '数字'
    case 'boolean': return '布尔值'
    case 'object': return '对象'
    case 'array': return '数组'
    case 'file': return '文件'
    case 'null': return '空值'
    default: return type
  }
}

const formatObjectValue = (value) => {
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2)
  }
  return String(value || '{}')
}

const getArrayItems = (value) => {
  if (Array.isArray(value)) {
    return value.slice(0, 5).map(item => 
      typeof item === 'object' ? JSON.stringify(item) : String(item)
    )
  }
  if (typeof value === 'string' && value.includes(',')) {
    return value.split(',').slice(0, 5).map(item => item.trim())
  }
  return [String(value || '[]')]
}

const formatSimpleValue = (value) => {
  if (value === null || value === undefined) {
    return ''
  }
  if (typeof value === 'string' && value.length > 50) {
    return value.substring(0, 50) + '...'
  }
  return String(value)
}

const getFileName = (value) => {
  if (typeof value === 'string') {
    if (value.startsWith('data:')) {
      return 'Base64 文件'
    }
    const parts = value.split('/')
    return parts[parts.length - 1] || value
  }
  return '文件'
}
</script>

<style scoped>
.param-value-display {
  font-size: 13px;
  line-height: 1.4;
}

.param-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.param-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.param-type {
  font-size: 11px;
}

.required-tag {
  font-size: 11px;
}

.param-description {
  color: #606266;
  font-size: 12px;
  margin-bottom: 8px;
  font-style: italic;
}

.param-value {
  margin-bottom: 8px;
}

.value-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
}

.value-content {
  padding: 6px 8px;
  border-radius: 4px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
}

.value-object .json-value {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
  color: #495057;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 100px;
  overflow-y: auto;
}

.value-array .array-value {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.array-item {
  font-size: 11px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.value-boolean {
  display: flex;
  align-items: center;
  gap: 8px;
}

.boolean-value {
  pointer-events: none;
}

.boolean-text {
  font-weight: 500;
  color: #606266;
}

.null-value {
  color: #909399;
  font-style: italic;
}

.file-value {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
}

.simple-value {
  color: #495057;
  word-break: break-all;
}

.param-metadata {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid #e9ecef;
  font-size: 11px;
}

.metadata-item {
  display: flex;
  gap: 4px;
}

.metadata-label {
  color: #909399;
  font-weight: 500;
}

.metadata-value {
  color: #606266;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* 紧凑模式 */
.param-value-display.compact .param-header {
  margin-bottom: 4px;
}

.param-value-display.compact .param-description {
  margin-bottom: 4px;
}

.param-value-display.compact .param-value {
  margin-bottom: 4px;
}

.param-value-display.compact .value-content {
  padding: 4px 6px;
}

/* 不同类型的颜色主题 */
.value-string {
  border-left: 3px solid #409eff;
}

.value-number {
  border-left: 3px solid #67c23a;
}

.value-boolean {
  border-left: 3px solid #e6a23c;
}

.value-object {
  border-left: 3px solid #909399;
}

.value-array {
  border-left: 3px solid #f56c6c;
}

.value-file {
  border-left: 3px solid #e6a23c;
}

.value-null {
  border-left: 3px solid #c0c4cc;
}
</style>