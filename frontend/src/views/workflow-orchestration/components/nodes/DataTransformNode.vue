<template>
  <div class="data-transform-node" :class="{ 
    selected: data.selected, 
    running: data.status === 'running',
    expanded: isExpanded 
  }">
    <div class="node-header" @click="toggleExpanded">
      <el-icon class="node-icon"><Operation /></el-icon>
      <span class="node-title">{{ data.label || '数据转换' }}</span>
      <div class="node-controls">
        <el-icon class="expand-icon" :class="{ expanded: isExpanded }">
          <ArrowDown />
        </el-icon>
        <div class="node-status">
          <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
          <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
          <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
        </div>
      </div>
    </div>
    
    <!-- 简要信息 -->
    <div v-if="!isExpanded" class="node-summary">
      <div v-if="transformType" class="summary-item">
        <span class="label">类型:</span>
        <span class="value">{{ getTransformTypeLabel(transformType) }}</span>
      </div>
      <div v-if="mappingRules.length" class="summary-item">
        <span class="label">规则:</span>
        <span class="value">{{ mappingRules.length }} 条</span>
      </div>
    </div>

    <!-- 详细配置 -->
    <div v-if="isExpanded" class="node-config">
      <!-- 转换类型选择 -->
      <div class="config-section">
        <label class="config-label">转换类型</label>
        <el-select 
          v-model="transformType" 
          class="config-select"
          placeholder="请选择转换类型"
          @change="updateNodeConfig"
        >
          <el-option label="字段映射" value="field_mapping" />
          <el-option label="数据格式转换" value="format_transform" />
          <el-option label="数据聚合" value="aggregation" />
          <el-option label="数据过滤" value="filtering" />
          <el-option label="自定义脚本" value="custom_script" />
        </el-select>
      </div>

      <!-- 映射规则配置 -->
      <div class="config-section">
        <div class="section-header">
          <label class="config-label">映射规则</label>
          <el-button 
            type="primary" 
            size="small" 
            @click="addMappingRule"
            :icon="Plus"
          >
            添加规则
          </el-button>
        </div>
        
        <div v-if="mappingRules.length === 0" class="empty-rules">
          <p>暂无映射规则，点击上方按钮添加</p>
        </div>
        
        <div v-else class="rules-list">
          <div 
            v-for="(rule, index) in mappingRules" 
            :key="index" 
            class="rule-item"
          >
            <div class="rule-header">
              <span class="rule-index">规则 {{ index + 1 }}</span>
              <el-icon 
                class="remove-btn" 
                @click="removeMappingRule(index)"
              >
                <Delete />
              </el-icon>
            </div>
            <div class="rule-config">
              <div class="config-row">
                <label class="config-label">源字段</label>
                <el-input 
                  v-model="rule.sourceField" 
                  placeholder="输入源字段名"
                  @input="updateNodeConfig"
                />
              </div>
              <div class="config-row">
                <label class="config-label">目标字段</label>
                <el-input 
                  v-model="rule.targetField" 
                  placeholder="输入目标字段名"
                  @input="updateNodeConfig"
                />
              </div>
              <div class="config-row">
                <label class="config-label">转换函数</label>
                <el-select 
                  v-model="rule.transformFunction" 
                  placeholder="选择转换函数"
                  @change="updateNodeConfig"
                >
                  <el-option label="直接映射" value="direct" />
                  <el-option label="字符串转数字" value="toNumber" />
                  <el-option label="数字转字符串" value="toString" />
                  <el-option label="日期格式化" value="formatDate" />
                  <el-option label="大写转换" value="toUpperCase" />
                  <el-option label="小写转换" value="toLowerCase" />
                  <el-option label="自定义函数" value="custom" />
                </el-select>
              </div>
              <div v-if="rule.transformFunction === 'custom'" class="config-row">
                <label class="config-label">自定义函数</label>
                <el-input 
                  v-model="rule.customFunction" 
                  type="textarea" 
                  :rows="3"
                  placeholder="输入JavaScript函数代码"
                  @input="updateNodeConfig"
                />
              </div>
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
      class="node-handle input-handle"
    />

    <!-- 输出端口 -->
    <Handle
      id="output"
      type="source"
      :position="Position.Right"
      :style="{ top: '50%' }"
      class="node-handle output-handle"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { Operation, Loading, Check, Close, ArrowDown, Plus, Delete } from '@element-plus/icons-vue'

interface MappingRule {
  sourceField: string
  targetField: string
  transformFunction: string
  customFunction?: string
}

const props = defineProps<{
  data: {
    id: string
    label?: string
    selected?: boolean
    status?: 'idle' | 'running' | 'success' | 'error'
    config?: {
      transformType?: string
      mappingRules?: MappingRule[]
    }
  }
}>()

const emit = defineEmits<{
  updateNode: [nodeId: string, updates: any]
}>()

// 响应式数据
const isExpanded = ref(false)
const transformType = ref(props.data.config?.transformType || '')
const mappingRules = ref<MappingRule[]>(props.data.config?.mappingRules || [])

// 方法
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const getTransformTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    field_mapping: '字段映射',
    format_transform: '数据格式转换',
    aggregation: '数据聚合',
    filtering: '数据过滤',
    custom_script: '自定义脚本'
  }
  return labels[type] || type
}

const addMappingRule = () => {
  mappingRules.value.push({
    sourceField: '',
    targetField: '',
    transformFunction: 'direct'
  })
  updateNodeConfig()
}

const removeMappingRule = (index: number) => {
  mappingRules.value.splice(index, 1)
  updateNodeConfig()
}

const updateNodeConfig = () => {
  emit('updateNode', props.data.id, {
    config: {
      transformType: transformType.value,
      mappingRules: mappingRules.value
    }
  })
}

// 监听props变化
watch(() => props.data.config, (newConfig) => {
  if (newConfig) {
    transformType.value = newConfig.transformType || ''
    mappingRules.value = newConfig.mappingRules || []
  }
}, { immediate: true })
</script>

<style scoped>
.data-transform-node {
  min-width: 200px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.data-transform-node.expanded {
  min-width: 450px;
}

.data-transform-node:hover {
  border-color: #e6a23c;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);
}

.data-transform-node.selected {
  border-color: #e6a23c;
  box-shadow: 0 0 0 2px rgba(230, 162, 60, 0.2);
}

.data-transform-node.running {
  border-color: #e6a23c;
  animation: nodeRunning 2s ease-in-out infinite;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fdf6ec;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
}

.node-icon {
  margin-right: 8px;
  color: #e6a23c;
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

.expand-icon.expanded {
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

.label {
  color: #909399;
  margin-right: 8px;
  min-width: 40px;
}

.value {
  color: #303133;
  font-weight: 500;
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

.config-select {
  width: 100%;
}

.empty-rules {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.rules-list {
  margin-top: 16px;
}

.rule-item {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rule-index {
  font-weight: 500;
  color: #303133;
}

.remove-btn {
  color: #f56c6c;
  cursor: pointer;
  padding: 4px;
}

.remove-btn:hover {
  background: #fef0f0;
  border-radius: 4px;
}

.rule-config {
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

.node-handle {
  width: 12px;
  height: 12px;
  background: #e6a23c;
  border: 2px solid white;
  border-radius: 50%;
}

.input-handle {
  background: #67c23a;
}

.output-handle {
  background: #e6a23c;
}

.node-handle:hover {
  transform: scale(1.2);
  transition: transform 0.2s;
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