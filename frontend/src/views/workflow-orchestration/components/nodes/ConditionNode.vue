<template>
  <div class="condition-node" :class="{ selected: data.selected, running: data.status === 'running', expanded: isExpanded }">
    <div class="node-header" @click="toggleExpanded">
      <el-icon class="node-icon"><Share /></el-icon>
      <span class="node-title">{{ data.label || '条件分支' }}</span>
      <div class="node-controls">
        <el-icon class="expand-icon" :class="{ rotated: isExpanded }"><ArrowDown /></el-icon>
        <div class="node-status">
          <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
          <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
          <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
        </div>
      </div>
    </div>
    
    <!-- 折叠状态下的简要信息 -->
    <div v-if="!isExpanded" class="node-summary">
      <div v-if="data.config?.logicalOperator" class="summary-item">
        <span class="label">逻辑:</span>
        <span class="value">{{ data.config.logicalOperator }}</span>
      </div>
      <div v-if="data.config?.conditions?.length" class="summary-item">
        <span class="label">条件:</span>
        <span class="value">{{ data.config.conditions.length }} 个</span>
      </div>
    </div>

    <!-- 展开状态下的完整配置界面 -->
    <div v-if="isExpanded" class="node-config">
      <!-- 逻辑操作符选择 -->
      <div class="config-section">
        <label class="config-label">逻辑操作符:</label>
        <el-select v-model="logicalOperator" size="small" style="width: 100%" @change="updateNodeConfig">
          <el-option label="AND (所有条件都满足)" value="AND" />
          <el-option label="OR (任一条件满足)" value="OR" />
        </el-select>
      </div>

      <!-- 条件列表 -->
      <div class="config-section">
        <div class="section-header">
          <label class="config-label">条件列表:</label>
          <el-button size="small" type="primary" @click="addCondition">
            <el-icon><Plus /></el-icon>
            添加条件
          </el-button>
        </div>
        
        <div v-if="conditions.length === 0" class="empty-conditions">
          <el-text type="info">暂无条件，点击上方按钮添加</el-text>
        </div>

        <div v-for="(condition, index) in conditions" :key="index" class="condition-item">
          <div class="condition-header">
            <span class="condition-index">条件 {{ index + 1 }}</span>
            <el-button size="small" type="danger" text @click="removeCondition(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          
          <div class="condition-config">
            <div class="config-row">
              <label class="config-label">字段:</label>
              <el-input 
                v-model="condition.field" 
                size="small" 
                placeholder="如: response.data.status"
                @input="updateNodeConfig"
              />
            </div>
            
            <div class="config-row">
              <label class="config-label">操作符:</label>
              <el-select v-model="condition.operator" size="small" @change="updateNodeConfig">
                <el-option label="等于 (==)" value="==" />
                <el-option label="不等于 (!=)" value="!=" />
                <el-option label="大于 (>)" value=">" />
                <el-option label="大于等于 (>=)" value=">=" />
                <el-option label="小于 (<)" value="<" />
                <el-option label="小于等于 (<=)" value="<=" />
                <el-option label="包含 (contains)" value="contains" />
                <el-option label="不包含 (not contains)" value="not_contains" />
              </el-select>
            </div>
            
            <div class="config-row">
              <label class="config-label">值:</label>
              <el-input 
                v-model="condition.value" 
                size="small" 
                placeholder="比较值"
                @input="updateNodeConfig"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入端口 -->
    <Handle
      id="input"
      type="target"
      :position="Position.Left"
      :style="{ top: '50%' }"
      class="node-handle"
    />

    <!-- 输出端口 - True -->
    <Handle
      type="source"
      :position="Position.Right"
      :style="{ top: '30%' }"
      class="node-handle true-handle"
      id="true"
    />

    <!-- 输出端口 - False -->
    <Handle
      type="source"
      :position="Position.Right"
      :style="{ top: '70%' }"
      class="node-handle false-handle"
      id="false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { Share, Loading, Check, Close, ArrowDown, Plus, Delete } from '@element-plus/icons-vue'

interface Condition {
  field: string
  operator: string
  value: string
}

const props = defineProps<{
  data: {
    id: string
    label?: string
    selected?: boolean
    status?: 'idle' | 'running' | 'success' | 'error'
    config?: {
      logicalOperator?: string
      conditions?: Condition[]
    }
  }
}>()

const emit = defineEmits<{
  updateNode: [nodeId: string, updates: any]
}>()

// 响应式数据
const isExpanded = ref(false)
const logicalOperator = ref(props.data.config?.logicalOperator || 'AND')
const conditions = ref<Condition[]>(props.data.config?.conditions || [])

// 方法
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const addCondition = () => {
  conditions.value.push({
    field: '',
    operator: '==',
    value: ''
  })
  updateNodeConfig()
}

const removeCondition = (index: number) => {
  conditions.value.splice(index, 1)
  updateNodeConfig()
}

const updateNodeConfig = () => {
  emit('updateNode', props.data.id, {
    config: {
      logicalOperator: logicalOperator.value,
      conditions: conditions.value
    }
  })
}

// 监听props变化
watch(() => props.data.config, (newConfig) => {
  if (newConfig) {
    logicalOperator.value = newConfig.logicalOperator || 'AND'
    conditions.value = newConfig.conditions || []
  }
}, { immediate: true })
</script>

<style scoped>
.condition-node {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  min-width: 200px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.condition-node.expanded {
  min-width: 400px;
}

.condition-node:hover {
  border-color: #f56c6c;
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

.condition-node.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.condition-node.running {
  border-color: #e6a23c;
  animation: nodeRunning 2s infinite;
}

.condition-node.success {
  border-color: #67c23a;
}

.condition-node.error {
  border-color: #f56c6c;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
}

.node-icon {
  margin-right: 8px;
  color: #409eff;
}

.node-title {
  flex: 1;
  font-weight: 500;
  color: #303133;
}

.node-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.node-status {
  margin-left: 8px;
}

.node-summary {
  padding: 12px 16px;
  color: #606266;
  font-size: 14px;
  border-bottom: 1px solid #e0e0e0;
}

.summary-item {
  display: flex;
  margin-bottom: 4px;
}

.node-config {
  padding: 16px;
  background: #fafafa;
}

.config-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.config-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.empty-conditions {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.condition-item {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.condition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.condition-index {
  font-weight: 500;
  color: #303133;
}

.condition-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-row .config-label {
  margin-bottom: 4px;
  font-size: 12px;
}

.label {
  color: #909399;
  margin-right: 8px;
  min-width: 40px;
}

.value {
  color: #303133;
  font-weight: 500;
}

.node-handle {
  width: 12px;
  height: 12px;
  border: 2px solid white;
}

.true-handle {
  background: #67c23a;
}

.false-handle {
  background: #f56c6c;
}

@keyframes nodeRunning {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>