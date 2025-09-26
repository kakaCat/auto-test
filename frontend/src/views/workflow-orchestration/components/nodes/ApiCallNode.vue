<template>
  <div class="api-call-node" :class="{ selected: data.selected, running: data.status === 'running' }">
    <div class="node-header">
      <el-icon class="node-icon"><Connection /></el-icon>
      <span class="node-title">{{ data.label || 'API调用' }}</span>
      <div class="node-status">
        <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
        <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
        <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
      </div>
    </div>
    
    <div class="node-body">
      <div class="config-display">
        <div v-if="data.config?.system" class="config-item">
          <span class="label">系统:</span>
          <span class="value">{{ data.config.system }}</span>
        </div>
        <div v-if="data.config?.module" class="config-item">
          <span class="label">模块:</span>
          <span class="value">{{ data.config.module }}</span>
        </div>
        <div v-if="data.config?.api" class="config-item">
          <span class="label">API:</span>
          <span class="value">{{ data.config.api }}</span>
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
import { Connection, Loading, Check, Close } from '@element-plus/icons-vue'

defineProps<{
  data: {
    label?: string
    selected?: boolean
    status?: 'idle' | 'running' | 'success' | 'error'
    config?: {
      system?: string
      module?: string
      api?: string
      method?: string
    }
  }
}>()
</script>

<style scoped>
.api-call-node {
  min-width: 200px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.api-call-node:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.api-call-node.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.api-call-node.running {
  border-color: #409eff;
  animation: nodeRunning 2s ease-in-out infinite;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  border-radius: 6px 6px 0 0;
}

.node-icon {
  font-size: 16px;
  margin-right: 8px;
  color: #409eff;
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
  background: #409eff;
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