<template>
  <div class="data-transform-node" :class="{ selected: data.selected, running: data.status === 'running' }">
    <div class="node-header">
      <el-icon class="node-icon"><Operation /></el-icon>
      <span class="node-title">{{ data.label || '数据转换' }}</span>
      <div class="node-status">
        <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
        <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
        <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
      </div>
    </div>
    
    <div class="node-body">
      <div class="config-display">
        <div v-if="data.config?.transformType" class="config-item">
          <span class="label">类型:</span>
          <span class="value">{{ data.config.transformType }}</span>
        </div>
        <div v-if="data.config?.mappingRules?.length" class="config-item">
          <span class="label">规则:</span>
          <span class="value">{{ data.config.mappingRules.length }} 条</span>
        </div>
      </div>
    </div>

    <!-- 输入端口 -->
    <Handle
      type="target"
      :position="Position.Left"
      :style="{ top: '50%' }"
      class="node-handle"
    />

    <!-- 输出端口 -->
    <Handle
      type="source"
      :position="Position.Right"
      :style="{ top: '50%' }"
      class="node-handle"
    />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { Operation, Loading, Check, Close } from '@element-plus/icons-vue'

defineProps<{
  data: {
    label?: string
    selected?: boolean
    status?: 'idle' | 'running' | 'success' | 'error'
    config?: {
      transformType?: string
      mappingRules?: any[]
    }
  }
}>()
</script>

<style scoped>
.data-transform-node {
  min-width: 200px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
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
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: #fdf6ec;
  border-radius: 6px 6px 0 0;
}

.node-icon {
  font-size: 16px;
  margin-right: 8px;
  color: #e6a23c;
}

.node-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.node-status {
  font-size: 16px;
}

.node-body {
  padding: 10px;
}

.config-display {
  font-size: 12px;
}

.config-item {
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

.node-handle {
  width: 12px;
  height: 12px;
  background: #e6a23c;
  border: 2px solid white;
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