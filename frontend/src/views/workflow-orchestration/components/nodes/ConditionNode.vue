<template>
  <div class="condition-node" :class="{ selected: data.selected, running: data.status === 'running' }">
    <div class="node-header">
      <el-icon class="node-icon"><Share /></el-icon>
      <span class="node-title">{{ data.label || '条件分支' }}</span>
      <div class="node-status">
        <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
        <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
        <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
      </div>
    </div>
    
    <div class="node-body">
      <div class="config-display">
        <div v-if="data.config && data.config.logicalOperator" class="config-item">
          <span class="label">逻辑:</span>
          <span class="value">{{ data.config.logicalOperator }}</span>
        </div>
        <div v-if="data.config && data.config.conditions && data.config.conditions.length" class="config-item">
          <span class="label">条件:</span>
          <span class="value">{{ data.config.conditions.length }} 个</span>
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

<script setup>
import { Handle, Position } from '@vue-flow/core'
import { Share, Loading, Check, Close } from '@element-plus/icons-vue'

defineProps(['data'])
</script>

<style scoped>
.condition-node {
  min-width: 200px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.condition-node:hover {
  border-color: #f56c6c;
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

.condition-node.selected {
  border-color: #f56c6c;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2);
}

.condition-node.running {
  border-color: #f56c6c;
  animation: nodeRunning 2s ease-in-out infinite;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: #fef0f0;
  border-radius: 6px 6px 0 0;
}

.node-icon {
  font-size: 16px;
  margin-right: 8px;
  color: #f56c6c;
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