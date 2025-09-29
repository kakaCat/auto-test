<template>
  <div class="json-editor">
    <!-- 编辑器工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button 
          size="small" 
          type="primary" 
          :icon="DocumentChecked"
          @click="formatJson"
          :disabled="!modelValue"
        >
          格式化
        </el-button>
        <el-button 
          size="small" 
          type="success" 
          :icon="CircleCheck"
          @click="validateJson"
          :disabled="!modelValue"
        >
          验证
        </el-button>
        <el-button 
          size="small" 
          type="warning" 
          :icon="Delete"
          @click="clearContent"
          :disabled="!modelValue"
        >
          清空
        </el-button>
      </div>
      <div class="toolbar-right">
        <span class="editor-stats" v-if="stats.lines > 0">
          {{ stats.lines }} 行 | {{ stats.characters }} 字符
        </span>
      </div>
    </div>

    <!-- Monaco 编辑器容器 -->
    <div 
      ref="editorContainer" 
      class="editor-container"
      :style="{ height: height }"
    ></div>

    <!-- 错误信息显示 -->
    <div v-if="error" class="error-panel">
      <el-alert
        :title="error.title"
        :description="error.description"
        type="error"
        show-icon
        :closable="false"
      />
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-left">
        <span class="status-item">
          <el-icon><Document /></el-icon>
          JSON
        </span>
        <span class="status-item" v-if="cursorPosition.line > 0">
          行 {{ cursorPosition.line }}, 列 {{ cursorPosition.column }}
        </span>
      </div>
      <div class="status-right">
        <span class="status-item" :class="{ 'status-valid': isValid, 'status-invalid': !isValid }">
          <el-icon>
            <CircleCheck v-if="isValid" />
            <CircleClose v-else />
          </el-icon>
          {{ isValid ? '有效' : '无效' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import * as monaco from 'monaco-editor'
import { 
  DocumentChecked, 
  CircleCheck, 
  Delete, 
  Document, 
  CircleClose 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '300px'
  },
  readonly: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '请输入 JSON 内容...'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change', 'validate', 'format'])

// 响应式状态
const editorContainer = ref(null)
const editor = ref(null)
const error = ref(null)
const isValid = ref(true)
const cursorPosition = ref({ line: 0, column: 0 })

// 计算属性
const stats = computed(() => {
  const content = props.modelValue || ''
  return {
    lines: content.split('\n').length,
    characters: content.length
  }
})

// Monaco 编辑器初始化
const initEditor = async () => {
  if (!editorContainer.value) return

  // 创建编辑器实例
  editor.value = monaco.editor.create(editorContainer.value, {
    value: props.modelValue,
    language: 'json',
    theme: 'vs-dark',
    automaticLayout: true,
    readOnly: props.readonly,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    lineNumbers: 'on',
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 10,
    lineNumbersMinChars: 3,
    renderLineHighlight: 'all',
    selectOnLineNumbers: true,
    roundedSelection: false,
    cursorStyle: 'line',
    fontSize: 14,
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    tabSize: 2,
    insertSpaces: true,
    formatOnPaste: true,
    formatOnType: true
  })

  // 监听内容变化
  editor.value.onDidChangeModelContent(() => {
    const value = editor.value.getValue()
    emit('update:modelValue', value)
    emit('change', value)
    validateJsonContent(value)
  })

  // 监听光标位置变化
  editor.value.onDidChangeCursorPosition((e) => {
    cursorPosition.value = {
      line: e.position.lineNumber,
      column: e.position.column
    }
  })

  // 设置占位符
  if (!props.modelValue && props.placeholder) {
    setPlaceholder()
  }

  // 初始验证
  validateJsonContent(props.modelValue)
}

// 设置占位符
const setPlaceholder = () => {
  if (!editor.value) return
  
  const model = editor.value.getModel()
  if (model && !model.getValue()) {
    // 添加占位符装饰
    const decorations = editor.value.deltaDecorations([], [{
      range: new monaco.Range(1, 1, 1, 1),
      options: {
        afterContentClassName: 'editor-placeholder',
        isWholeLine: true
      }
    }])
    
    // 监听内容变化，移除占位符
    const disposable = model.onDidChangeContent(() => {
      if (model.getValue()) {
        editor.value.deltaDecorations(decorations, [])
        disposable.dispose()
      }
    })
  }
}

// JSON 验证
const validateJsonContent = (content) => {
  if (!content || !content.trim()) {
    error.value = null
    isValid.value = true
    clearErrorMarkers()
    return
  }

  try {
    JSON.parse(content)
    error.value = null
    isValid.value = true
    clearErrorMarkers()
    emit('validate', { valid: true, error: null })
  } catch (e) {
    const errorInfo = parseJsonError(e, content)
    error.value = errorInfo
    isValid.value = false
    setErrorMarkers(errorInfo)
    emit('validate', { valid: false, error: errorInfo })
  }
}

// 解析 JSON 错误信息
const parseJsonError = (error, content) => {
  const message = error.message
  let line = 1
  let column = 1
  
  // 尝试从错误信息中提取行列信息
  const positionMatch = message.match(/at position (\d+)/)
  if (positionMatch) {
    const position = parseInt(positionMatch[1])
    const lines = content.substring(0, position).split('\n')
    line = lines.length
    column = lines[lines.length - 1].length + 1
  }

  // 解析错误类型
  let title = 'JSON 语法错误'
  let description = message

  if (message.includes('Unexpected token')) {
    title = '意外的字符'
    description = `在第 ${line} 行第 ${column} 列发现意外字符`
  } else if (message.includes('Unexpected end')) {
    title = '意外的结束'
    description = 'JSON 内容不完整，可能缺少闭合括号或引号'
  } else if (message.includes('Expected')) {
    title = '缺少必要字符'
    description = `在第 ${line} 行第 ${column} 列附近缺少必要的字符`
  }

  return {
    title,
    description,
    line,
    column,
    original: message
  }
}

// 设置错误标记
const setErrorMarkers = (errorInfo) => {
  if (!editor.value) return

  const model = editor.value.getModel()
  if (!model) return

  monaco.editor.setModelMarkers(model, 'json-validation', [{
    startLineNumber: errorInfo.line,
    startColumn: errorInfo.column,
    endLineNumber: errorInfo.line,
    endColumn: errorInfo.column + 1,
    message: errorInfo.description,
    severity: monaco.MarkerSeverity.Error
  }])
}

// 清除错误标记
const clearErrorMarkers = () => {
  if (!editor.value) return

  const model = editor.value.getModel()
  if (!model) return

  monaco.editor.setModelMarkers(model, 'json-validation', [])
}

// 格式化 JSON
const formatJson = () => {
  if (!editor.value) return

  const content = editor.value.getValue()
  if (!content.trim()) return

  try {
    const parsed = JSON.parse(content)
    const formatted = JSON.stringify(parsed, null, 2)
    editor.value.setValue(formatted)
    emit('format', formatted)
  } catch (e) {
    // 如果无法解析，尝试使用编辑器的格式化功能
    editor.value.getAction('editor.action.formatDocument').run()
  }
}

// 验证 JSON
const validateJson = () => {
  const content = editor.value?.getValue() || ''
  validateJsonContent(content)
}

// 清空内容
const clearContent = () => {
  if (editor.value) {
    editor.value.setValue('')
  }
}

// 监听 props 变化
watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getValue() !== newValue) {
    editor.value.setValue(newValue || '')
  }
})

watch(() => props.readonly, (newValue) => {
  if (editor.value) {
    editor.value.updateOptions({ readOnly: newValue })
  }
})

// 生命周期
onMounted(async () => {
  await nextTick()
  await initEditor()
})

onUnmounted(() => {
  if (editor.value) {
    editor.value.dispose()
  }
})

// 暴露方法
defineExpose({
  formatJson,
  validateJson,
  clearContent,
  focus: () => editor.value?.focus(),
  getValue: () => editor.value?.getValue() || '',
  setValue: (value) => editor.value?.setValue(value || '')
})
</script>

<style scoped>
.json-editor {
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  overflow: hidden;
  background: var(--el-bg-color);
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--el-bg-color-page);
  border-bottom: 1px solid var(--el-border-color-light);
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.editor-stats {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.editor-container {
  position: relative;
  width: 100%;
}

.error-panel {
  padding: 8px 12px;
  border-top: 1px solid var(--el-border-color-light);
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  background: var(--el-bg-color-page);
  border-top: 1px solid var(--el-border-color-light);
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-valid {
  color: var(--el-color-success);
}

.status-invalid {
  color: var(--el-color-error);
}

/* 占位符样式 */
:deep(.editor-placeholder::after) {
  content: '请输入 JSON 内容...';
  color: var(--el-text-color-placeholder);
  font-style: italic;
  pointer-events: none;
}

/* Monaco 编辑器主题调整 */
:deep(.monaco-editor) {
  background: var(--el-bg-color) !important;
}

:deep(.monaco-editor .margin) {
  background: var(--el-bg-color) !important;
}

:deep(.monaco-editor-background) {
  background: var(--el-bg-color) !important;
}
</style>