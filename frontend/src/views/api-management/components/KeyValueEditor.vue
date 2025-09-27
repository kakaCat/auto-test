<template>
  <div class="key-value-editor">
    <div class="editor-header">
      <div class="header-columns">
        <div class="column-header key">{{ placeholderKey || '键' }}</div>
        <div class="column-header value">{{ placeholderValue || '值' }}</div>
        <div class="column-header actions">操作</div>
      </div>
      <div class="header-actions">
        <el-button size="small" @click="addRow">
          <el-icon><Plus /></el-icon>
          添加
        </el-button>
        <el-button v-if="presets && presets.length > 0" size="small" @click="showPresets = !showPresets">
          <el-icon><Collection /></el-icon>
          预设
        </el-button>
        <el-button v-if="items.length > 0" size="small" @click="clearAll">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </div>

    <!-- 预设选项 -->
    <div v-if="showPresets && presets && presets.length > 0" class="presets-panel">
      <div class="presets-title">常用预设</div>
      <div class="presets-list">
        <div
          v-for="preset in presets"
          :key="preset.key"
          class="preset-item"
          @click="addPreset(preset)"
        >
          <span class="preset-key">{{ preset.key }}</span>
          <span class="preset-value">{{ preset.value }}</span>
        </div>
      </div>
    </div>

    <!-- 键值对列表 -->
    <div class="editor-body">
      <draggable
        v-model="items"
        item-key="id"
        handle=".drag-handle"
        @end="handleDragEnd"
      >
        <template #item="{ element: item, index }">
          <div class="kv-row">
            <div class="row-content">
              <div class="cell key-cell">
                <el-icon class="drag-handle"><Rank /></el-icon>
                <el-input
                  v-model="item.key"
                  :placeholder="placeholderKey || '键'"
                  size="small"
                  @blur="validateKey(item, index)"
                />
              </div>
              
              <div class="cell value-cell">
                <el-input
                  v-if="!supportFile || item.type !== 'file'"
                  v-model="item.value"
                  :placeholder="placeholderValue || '值'"
                  size="small"
                  :type="item.type === 'password' ? 'password' : 'text'"
                />
                <el-upload
                  v-else
                  :auto-upload="false"
                  :show-file-list="false"
                  @change="handleFileChange($event, item)"
                >
                  <el-button size="small">
                    <el-icon><Upload /></el-icon>
                    选择文件
                  </el-button>
                  <span v-if="item.file" class="file-name">{{ item.file.name }}</span>
                </el-upload>
              </div>
              
              <div class="cell actions-cell">
                <el-button-group size="small">
                  <el-dropdown v-if="supportFile" @command="handleTypeCommand($event, item)">
                    <el-button>
                      <el-icon><Setting /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="text" :class="{ active: item.type === 'text' }">
                          文本
                        </el-dropdown-item>
                        <el-dropdown-item command="password" :class="{ active: item.type === 'password' }">
                          密码
                        </el-dropdown-item>
                        <el-dropdown-item command="file" :class="{ active: item.type === 'file' }">
                          文件
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                  
                  <el-button @click="duplicateRow(index)">
                    <el-icon><CopyDocument /></el-icon>
                  </el-button>
                  
                  <el-button type="danger" @click="removeRow(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
            </div>
            
            <!-- 描述行 -->
            <div v-if="showDescription" class="description-row">
              <el-input
                v-model="item.description"
                placeholder="描述（可选）"
                size="small"
              />
            </div>
          </div>
        </template>
      </draggable>
    </div>

    <!-- 空状态 -->
    <div v-if="items.length === 0" class="empty-state">
      <el-empty description="暂无数据">
        <el-button type="primary" @click="addRow">添加第一项</el-button>
      </el-empty>
    </div>

    <!-- 底部工具栏 -->
    <div v-if="items.length > 0" class="editor-footer">
      <div class="footer-info">
        <span>共 {{ items.length }} 项</span>
        <span v-if="enabledCount < items.length">（{{ enabledCount }} 项启用）</span>
      </div>
      
      <div class="footer-actions">
        <el-checkbox v-model="showDescription" @change="handleDescriptionToggle">
          显示描述
        </el-checkbox>
        
        <el-button size="small" @click="toggleAllEnabled">
          {{ allEnabled ? '全部禁用' : '全部启用' }}
        </el-button>
        
        <el-button size="small" @click="sortByKey">
          <el-icon><Sort /></el-icon>
          按键排序
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Delete, Collection, Rank, Setting, Upload,
  CopyDocument, Sort
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  placeholderKey: {
    type: String,
    default: '键'
  },
  placeholderValue: {
    type: String,
    default: '值'
  },
  presets: {
    type: Array,
    default: () => []
  },
  supportFile: {
    type: Boolean,
    default: false
  },
  allowDuplicate: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change'])

// 响应式数据
const items = ref([])
const showPresets = ref(false)
const showDescription = ref(false)
let itemIdCounter = 0

// 计算属性
const enabledCount = computed(() => {
  return items.value.filter(item => item.enabled !== false).length
})

const allEnabled = computed(() => {
  return items.value.length > 0 && enabledCount.value === items.value.length
})

// 监听器
watch(() => props.modelValue, (newValue) => {
  if (Array.isArray(newValue)) {
    items.value = newValue.map(item => ({
      id: item.id || ++itemIdCounter,
      key: item.key || '',
      value: item.value || '',
      type: item.type || 'text',
      enabled: item.enabled !== false,
      description: item.description || '',
      file: item.file || null
    }))
  }
}, { immediate: true, deep: true })

watch(items, (newValue) => {
  const result = newValue.map(item => ({
    key: item.key,
    value: item.value,
    type: item.type,
    enabled: item.enabled,
    description: item.description,
    file: item.file
  }))
  emit('update:modelValue', result)
  emit('change', result)
}, { deep: true })

// 方法
const generateId = () => ++itemIdCounter

const addRow = () => {
  items.value.push({
    id: generateId(),
    key: '',
    value: '',
    type: 'text',
    enabled: true,
    description: '',
    file: null
  })
  
  // 自动聚焦到新添加的行
  nextTick(() => {
    const inputs = document.querySelectorAll('.kv-row:last-child .key-cell input')
    if (inputs.length > 0) {
      inputs[0].focus()
    }
  })
}

const removeRow = (index) => {
  items.value.splice(index, 1)
}

const duplicateRow = (index) => {
  const original = items.value[index]
  const copy = {
    ...original,
    id: generateId(),
    key: original.key + '_copy'
  }
  items.value.splice(index + 1, 0, copy)
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确认清空所有数据吗？',
      '确认清空',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    items.value = []
  } catch {
    // 用户取消
  }
}

const addPreset = (preset) => {
  // 检查是否已存在相同的键
  const exists = items.value.find(item => item.key === preset.key)
  if (exists && !props.allowDuplicate) {
    ElMessage.warning(`键 "${preset.key}" 已存在`)
    return
  }
  
  items.value.push({
    id: generateId(),
    key: preset.key,
    value: preset.value,
    type: 'text',
    enabled: true,
    description: preset.description || '',
    file: null
  })
  
  showPresets.value = false
  ElMessage.success('预设添加成功')
}

const validateKey = (item, index) => {
  if (!item.key.trim()) return
  
  if (!props.allowDuplicate) {
    // 检查重复键
    const duplicate = items.value.find((otherItem, otherIndex) => 
      otherIndex !== index && otherItem.key === item.key
    )
    
    if (duplicate) {
      ElMessage.warning('键名不能重复')
      item.key = ''
    }
  }
}

const handleTypeCommand = (command, item) => {
  item.type = command
  if (command !== 'file') {
    item.file = null
  } else {
    item.value = ''
  }
}

const handleFileChange = (file, item) => {
  item.file = file.raw
  item.value = file.name
}

const handleDragEnd = () => {
  // 拖拽结束后的处理
}

const handleDescriptionToggle = () => {
  // 切换描述显示状态
}

const toggleAllEnabled = () => {
  const targetState = !allEnabled.value
  items.value.forEach(item => {
    item.enabled = targetState
  })
}

const sortByKey = () => {
  items.value.sort((a, b) => a.key.localeCompare(b.key))
  ElMessage.success('已按键名排序')
}

// 暴露方法
defineExpose({
  addRow,
  clearAll,
  addPreset
})
</script>

<style scoped>
.key-value-editor {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.header-columns {
  display: flex;
  flex: 1;
  gap: 12px;
}

.column-header {
  font-weight: 600;
  color: #303133;
  font-size: 12px;
}

.column-header.key {
  flex: 1;
}

.column-header.value {
  flex: 1.5;
}

.column-header.actions {
  width: 120px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.presets-panel {
  padding: 12px 16px;
  background: #fafbfc;
  border-bottom: 1px solid #f0f2f5;
}

.presets-title {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.presets-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
}

.preset-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.preset-key {
  font-weight: 600;
  color: #303133;
}

.preset-value {
  color: #606266;
}

.editor-body {
  min-height: 100px;
  max-height: 400px;
  overflow-y: auto;
}

.kv-row {
  border-bottom: 1px solid #f0f2f5;
  transition: all 0.2s ease;
}

.kv-row:hover {
  background: #f8f9fa;
}

.row-content {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  gap: 12px;
}

.cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cell.key-cell {
  flex: 1;
}

.cell.value-cell {
  flex: 1.5;
}

.cell.actions-cell {
  width: 120px;
  justify-content: flex-end;
}

.drag-handle {
  cursor: move;
  color: #c0c4cc;
  transition: color 0.2s ease;
}

.drag-handle:hover {
  color: #409eff;
}

.file-name {
  margin-left: 8px;
  font-size: 12px;
  color: #606266;
}

.description-row {
  padding: 0 16px 8px 40px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
}

.footer-info {
  font-size: 12px;
  color: #606266;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-input__wrapper) {
  border-radius: 4px;
}

:deep(.el-button-group .el-button) {
  padding: 4px 8px;
}

:deep(.el-dropdown-menu__item.active) {
  color: #409eff;
  background: #f0f9ff;
}

:deep(.el-upload) {
  display: flex;
  align-items: center;
}
</style>