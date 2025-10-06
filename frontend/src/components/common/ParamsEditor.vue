<template>
  <div class="params-editor" role="region" aria-label="参数编辑器">
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
        <el-button v-if="currentMode === 'table'" size="small" @click="openJsonImportModal">
          <el-icon><Upload /></el-icon>
          JSON导入
        </el-button>
        <el-button v-if="currentMode === 'json'" size="small" @click="generateFromJson" :disabled="!jsonContent.trim()">
          <el-icon><Upload /></el-icon>
          从JSON生成表格
        </el-button>
        <el-button v-if="currentMode === 'table'" size="small" @click="exportToJson" :disabled="!params.length">
          <el-icon><Download /></el-icon>
          导出JSON
        </el-button>
      </div>
    </div>

    <!-- 表格模式 -->
    <div v-if="currentMode === 'table'" class="table-mode" role="tree" aria-label="参数树">
      <div class="table-header">
        <el-button type="primary" size="small" @click="addParam">
          <el-icon><Plus /></el-icon>
          添加参数
        </el-button>
        <el-button v-if="params.length > 0" size="small" @click="clearAll">
          <el-icon><Delete /></el-icon>
          清空所有
        </el-button>
        <div class="table-search">
          <el-input v-model="searchText" size="small" clearable placeholder="搜索参数名/描述（自动展开匹配路径）" @input="handleSearchInput">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>

      <div v-if="params.length > 0" class="params-table">
        <div class="table-headers">
          <div class="header-cell name">参数名</div>
          <div class="header-cell type">类型</div>
          <div class="header-cell required">必填</div>
          <div class="header-cell description">描述</div>
          <div class="header-cell actions">操作</div>
        </div>

        <draggable v-model="params" item-key="id" handle=".drag-handle" @end="handleDragEnd">
          <template #item="{ element: param, index }">
            <div :class="['param-row', { 'is-child': param.level > 0 }]"
                 :style="{ paddingLeft: `${param.level * 20}px` }"
                 v-show="isRowVisible(param)"
                 role="treeitem"
                 :aria-level="(param.level || 0) + 1"
                 :aria-expanded="isExpandable(param) ? (!isCollapsed(param.id)) : undefined">
              <div class="row-content">
                <div class="cell name">
                  <el-icon class="drag-handle"><Rank /></el-icon>
                  <el-button v-if="isExpandable(param)"
                             class="collapse-toggle"
                             text
                             size="small"
                             aria-label="展开/折叠子参数"
                             @click="toggleCollapse(param)"
                             @keydown="onCollapseKeydown($event, param)"
                             :aria-controls="`children-of-${param.id}`"
                             :aria-expanded="!isCollapsed(param.id)"
                             :tabindex="0">
                    <el-icon>
                      <component :is="isCollapsed(param.id) ? 'CaretRight' : 'CaretBottom'" />
                    </el-icon>
                  </el-button>
                  <el-input v-model="param.name" placeholder="参数名" size="small" @blur="validateParamName(param, index)" />
                  <el-button v-if="isExpandable(param)" size="small" text @click="addChildParam(index)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                </div>

                <div class="cell type">
                  <el-select v-model="param.type" size="small" @change="handleTypeChange(param, index)">
                    <el-option label="string" value="string" />
                    <el-option label="number" value="number" />
                    <el-option label="boolean" value="boolean" />
                    <el-option label="object" value="object" />
                    <el-option label="array" value="array" />
                    <el-option label="file" value="file" />
                  </el-select>
                </div>

                <div class="cell required">
                  <el-switch v-model="param.required" size="small" />
                </div>

                <div class="cell description">
                  <el-input v-model="param.description" placeholder="参数描述" size="small" />
                </div>

                <div class="cell actions">
                  <el-button-group size="small">
                    <el-button @click="moveUp(index)" :disabled="index === 0">
                      <el-icon><ArrowUp /></el-icon>
                    </el-button>
                    <el-button @click="moveDown(index)" :disabled="index === params.length - 1">
                      <el-icon><ArrowDown /></el-icon>
                    </el-button>
                    <el-button @click="copyParam(index)">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                    <el-button type="danger" @click="removeParam(index)">
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
          <el-button type="primary" @click="addParam">添加第一个参数</el-button>
        </el-empty>
      </div>
    </div>

    <!-- JSON模式 -->
    <div v-if="currentMode === 'json'" class="json-mode">
      <div class="json-header">
        <span class="json-title">JSON Schema / 示例编辑器</span>
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
        <el-input v-model="jsonContent" type="textarea" :rows="15" placeholder="请输入JSON Schema或参数示例..." @blur="validateJson" />
      </div>

      <div v-if="jsonError" class="json-error">
        <el-alert :title="jsonError" type="error" show-icon :closable="false" />
      </div>
    </div>

    <!-- JSON 导入 Modal -->
    <JsonImportModal
      v-model="showJsonImportModal"
      :current-params="params"
      @import="handleJsonImport"
      @close="showJsonImportModal = false"
    />
  </div>
  
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { 
  Grid, Document, Plus, Delete, Upload, Download,
  Rank, ArrowUp, ArrowDown, CopyDocument,
  MagicStick, CircleCheck, CaretRight, CaretBottom, Search 
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import JsonImportModal from './JsonImportModal.vue'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  mode: {
    type: String,
    default: 'table'
  },
  // Sprint A props
  collapsible: {
    type: Boolean,
    default: true
  },
  defaultExpandDepth: {
    type: Number,
    default: 1
  },
  persistExpandState: {
    type: Boolean,
    default: true
  },
  maxAutoExpandNodes: {
    type: Number,
    default: 100
  },
  componentId: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change', 'expand-change'])

// 响应式状态
const currentMode = ref(props.mode)
const params = ref([])
const jsonContent = ref('')
const jsonError = ref('')
const searchText = ref('')
const showJsonImportModal = ref(false)
let idCounter = 0

// 折叠状态与持久化（按组件命名空间）
const COLLAPSE_STORAGE_KEY = computed(() => `paramsEditor:collapsedIds:${props.componentId || 'default'}`)
const collapsedIds = ref([])
try {
  const saved = localStorage.getItem(COLLAPSE_STORAGE_KEY.value)
  collapsedIds.value = saved ? JSON.parse(saved) : []
} catch (e) {
  collapsedIds.value = []
}
const isCollapsed = (id) => collapsedIds.value.includes(id)
const toggleCollapse = (param) => {
  const idx = collapsedIds.value.indexOf(param.id)
  if (idx >= 0) collapsedIds.value.splice(idx, 1)
  else collapsedIds.value.push(param.id)
  if (props.persistExpandState) {
    localStorage.setItem(COLLAPSE_STORAGE_KEY.value, JSON.stringify(collapsedIds.value))
  }
  emitExpandChange()
}

const emitExpandChange = () => {
  // 以 expandedKeys 语义对外抛出事件
  const allExpandableIds = params.value.filter(p => isExpandable(p)).map(p => p.id)
  const expandedKeys = allExpandableIds.filter(id => !collapsedIds.value.includes(id))
  emit('expand-change', { expandedKeys, source: 'mouse' })
}

const isExpandable = (param) => (param?.type === 'object' || param?.type === 'array')

// 工具函数
const generateId = () => ++idCounter

const isRowVisible = (param) => {
  if (!searchText.value.trim()) return true
  const text = (param.name || '') + ' ' + (param.description || '')
  const matched = text.toLowerCase().includes(searchText.value.toLowerCase())
  if (matched) {
    // 自动展开匹配路径
    const chain = []
    let p = param
    while (p && p.parentId) {
      chain.push(p.parentId)
      p = params.value.find(x => x.id === p.parentId)
    }
    chain.forEach(id => {
      const i = collapsedIds.value.indexOf(id)
      if (i >= 0) collapsedIds.value.splice(i, 1)
    })
    if (props.persistExpandState) {
      localStorage.setItem(COLLAPSE_STORAGE_KEY.value, JSON.stringify(collapsedIds.value))
    }
    emit('expand-change', { expandedKeys: params.value.filter(p => isExpandable(p)).map(p => p.id).filter(id => !collapsedIds.value.includes(id)), source: 'search' })
  }
  // 子节点在父折叠时隐藏
  const parentCollapsed = param.parentId && isCollapsed(param.parentId)
  return matched && !parentCollapsed
}

const handleSearchInput = () => {
  // 触发可见性计算与路径展开
}

// 键盘交互
const onCollapseKeydown = (e, param) => {
  if (!isExpandable(param)) return
  const key = e.key
  if (key === 'ArrowLeft') {
    // 收起当前或聚焦父级
    if (!isCollapsed(param.id)) {
      toggleCollapse(param)
      emit('expand-change', { expandedKeys: params.value.filter(p => isExpandable(p)).map(p => p.id).filter(id => !collapsedIds.value.includes(id)), source: 'keyboard' })
    } else if (param.parentId) {
      // 将焦点交给父级的折叠按钮
      const btn = document.querySelector(`[aria-controls="children-of-${param.parentId}"]`)
      if (btn) btn.focus()
    }
    e.preventDefault()
  } else if (key === 'ArrowRight') {
    // 展开当前或聚焦首个子项
    if (isCollapsed(param.id)) {
      toggleCollapse(param)
      emit('expand-change', { expandedKeys: params.value.filter(p => isExpandable(p)).map(p => p.id).filter(id => !collapsedIds.value.includes(id)), source: 'keyboard' })
    } else {
      const child = params.value.find(p => p.parentId === param.id)
      if (child) {
        const btn = document.querySelector(`[aria-controls="children-of-${child.id}"]`)
        if (btn) btn.focus()
      }
    }
    e.preventDefault()
  } else if (key === 'Enter') {
    // 展开后聚焦首个子项
    if (isCollapsed(param.id)) {
      toggleCollapse(param)
    }
    const child = params.value.find(p => p.parentId === param.id)
    if (child) {
      const btn = document.querySelector(`[aria-controls="children-of-${child.id}"]`)
      if (btn) btn.focus()
    }
    e.preventDefault()
  }
}

// 参数编辑操作
const addParam = () => {
  params.value.push({ id: generateId(), name: '', type: 'string', required: false, description: '', level: 0, parentId: null })
}
const addChildParam = (parentIndex) => {
  const parent = params.value[parentIndex]
  params.value.splice(parentIndex + 1, 0, { id: generateId(), name: '', type: 'string', required: false, description: '', level: (parent.level || 0) + 1, parentId: parent.id })
}
const removeParam = (index) => {
  const id = params.value[index]?.id
  const toRemove = [id]
  const findChildren = (pid) => {
    params.value.forEach(p => { if (p.parentId === pid) { toRemove.push(p.id); findChildren(p.id) } })
  }
  findChildren(id)
  params.value = params.value.filter(p => !toRemove.includes(p.id))
}
const copyParam = (index) => {
  const original = params.value[index]
  params.value.splice(index + 1, 0, { ...original, id: generateId(), name: `${original.name}_copy` })
}
const moveUp = (index) => {
  if (index === 0) return
  const item = params.value.splice(index, 1)[0]
  params.value.splice(index - 1, 0, item)
}
const moveDown = (index) => {
  if (index === params.value.length - 1) return
  const item = params.value.splice(index, 1)[0]
  params.value.splice(index + 1, 0, item)
}
const clearAll = () => { params.value = [] }

const validateParamName = (param, index) => {
  const name = (param.name || '').trim()
  if (!name) return
  const exists = params.value.some((p, i) => i !== index && (p.name || '').trim() === name && (p.level || 0) === (param.level || 0) && p.parentId === param.parentId)
  if (exists) {
    param.name = ''
  }
}

const handleTypeChange = (param, index) => {
  if (param.type !== 'object' && param.type !== 'array') {
    // 删除所有子节点
    const toRemove = []
    const collectChildren = (pid) => {
      params.value.forEach(p => { if (p.parentId === pid) { toRemove.push(p.id); collectChildren(p.id) } })
    }
    collectChildren(param.id)
    if (toRemove.length > 0) {
      params.value = params.value.filter(p => !toRemove.includes(p.id))
    }
    // 类型变更为原子类型时清理其折叠状态
    const idx = collapsedIds.value.indexOf(param.id)
    if (idx >= 0) collapsedIds.value.splice(idx, 1)
    if (props.persistExpandState) {
      localStorage.setItem(COLLAPSE_STORAGE_KEY.value, JSON.stringify(collapsedIds.value))
    }
  }
}

const handleDragEnd = () => {
  // 拖拽结束后可选择重新计算层级或仅保持顺序
}

// JSON转换
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

const convertExampleToParams = (data, level = 0, parentId = null) => {
  const fields = []
  if (typeof data !== 'object' || data === null) return fields
  Object.entries(data).forEach(([key, value]) => {
    const type = inferType(value)
    const id = generateId()
    const field = { id, name: key, type, required: true, description: '', level, parentId }
    fields.push(field)
    if (type === 'object') {
      fields.push(...convertExampleToParams(value, level + 1, id))
    } else if (type === 'array') {
      const first = value.length > 0 ? value[0] : null
      const itemType = inferType(first)
      if (itemType === 'object') {
        fields.push(...convertExampleToParams(first || {}, level + 1, id))
      }
    }
  })
  return fields
}

const exportToJson = () => {
  const obj = {}
  // 仅生成顶层示例对象（与现有request_schema保存逻辑保持一致）
  params.value.forEach(p => { if (p.level === 0 && p.name) obj[p.name] = null })
  jsonContent.value = JSON.stringify(obj, null, 2)
  currentMode.value = 'json'
}

const generateFromJson = () => {
  if (!jsonContent.value.trim()) return
  try {
    const parsed = JSON.parse(jsonContent.value)
    params.value = convertExampleToParams(parsed)
    currentMode.value = 'table'
    // 默认展开层级控制
    setInitialCollapse()
  } catch (e) {
    jsonError.value = 'JSON格式错误：' + e.message
  }
}

const formatJson = () => {
  try {
    const parsed = JSON.parse(jsonContent.value)
    jsonContent.value = JSON.stringify(parsed, null, 2)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'JSON格式错误：' + e.message
  }
}

const validateJson = () => {
  if (!jsonContent.value.trim()) { jsonError.value = ''; return }
  try { JSON.parse(jsonContent.value); jsonError.value = '' } catch (e) { jsonError.value = 'JSON格式错误：' + e.message }
}

// JSON 导入相关方法
const openJsonImportModal = () => {
  showJsonImportModal.value = true
}

const handleJsonImport = (importData) => {
  const { params: importedParams, options } = importData
  
  if (options.mode === 'override') {
    // 覆盖模式：完全替换现有参数
    params.value = importedParams.map(param => ({
      ...param,
      id: generateId() // 重新生成 ID 避免冲突
    }))
  } else {
    // 合并模式：与现有参数合并
    const mergedParams = [...params.value]
    
    importedParams.forEach(importParam => {
      // 检查是否存在同名参数（同层级）
      const existingIndex = mergedParams.findIndex(p => 
        p.name === importParam.name && 
        p.level === importParam.level && 
        p.parentId === importParam.parentId
      )
      
      if (existingIndex >= 0) {
        // 更新现有参数
        mergedParams[existingIndex] = {
          ...mergedParams[existingIndex],
          ...importParam,
          id: mergedParams[existingIndex].id // 保持原有 ID
        }
      } else {
        // 添加新参数
        mergedParams.push({
          ...importParam,
          id: generateId()
        })
      }
    })
    
    params.value = mergedParams
  }
  
  // 设置初始折叠状态
  setInitialCollapse()
  
  // 触发变更事件
  emit('update:modelValue', params.value)
  emit('change', params.value)
  
  // 关闭 Modal
  showJsonImportModal.value = false
}

const handleModeChange = (mode) => {
  if (mode === 'json') {
    exportToJson()
  } else if (mode === 'table' && jsonContent.value.trim()) {
    generateFromJson()
  }
}

const setInitialCollapse = () => {
  if (!props.collapsible) return
  // 将超过默认层级的节点折叠
  const targetIds = params.value.filter(p => isExpandable(p) && (p.level || 0) >= props.defaultExpandDepth).map(p => p.id)
  collapsedIds.value = Array.from(new Set([...(collapsedIds.value || []), ...targetIds]))
  if (props.persistExpandState) {
    localStorage.setItem(COLLAPSE_STORAGE_KEY.value, JSON.stringify(collapsedIds.value))
  }
  emitExpandChange()
}

// 监听与双向绑定
let isInternalUpdate = false
watch(() => props.modelValue, (val) => {
  if (isInternalUpdate) return
  params.value = Array.isArray(val) ? [...val] : []
  // 初始折叠策略（仅在表格模式下）
  if (currentMode.value === 'table') {
    setInitialCollapse()
  }
}, { immediate: true, deep: true })

watch(params, (val) => {
  isInternalUpdate = true
  emit('update:modelValue', val)
  emit('change', val)
  nextTick(() => { isInternalUpdate = false })
}, { deep: true })

</script>

<style scoped>
.params-editor {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  width: 100%;
  box-sizing: border-box;
}
.mode-switcher { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-bottom: 1px solid #e4e7ed; }
.mode-actions { display: flex; gap: 8px; }
.table-mode { padding: 20px; }
.table-header { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; }
.table-search { margin-left: auto; width: 300px; }
.params-table { border: 1px solid #e4e7ed; border-radius: 8px; overflow: hidden; margin-bottom: 20px; }
.table-headers { display: flex; background: #f5f7fa; border-bottom: 1px solid #e4e7ed; }
.header-cell { padding: 8px 12px; font-weight: 500; color: #606266; }
.header-cell.name { flex: 2; }
.header-cell.type { flex: 1; }
.header-cell.required { width: 80px; }
.header-cell.description { flex: 2; }
.header-cell.actions { width: 200px; text-align: right; }
.param-row { display: flex; border-bottom: 1px solid #ebeef5; }
.row-content { display: flex; width: 100%; align-items: center; }
.cell { padding: 8px 12px; display: flex; align-items: center; gap: 8px; }
.cell.name { flex: 2; }
.cell.type { flex: 1; }
.cell.required { width: 80px; }
.cell.description { flex: 2; }
.cell.actions { width: 200px; justify-content: flex-end; }
.collapse-toggle { margin-right: 4px; }
.json-mode { padding: 16px 20px; }
.json-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.json-title { font-weight: 600; color: #303133; }
.json-editor { margin-top: 8px; }
.json-error { margin-top: 8px; }
</style>