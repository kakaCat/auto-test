<template>
  <div class="end-node" :class="{ selected: data.selected, running: data.status === 'running' }">
    <div class="node-header">
      <el-icon class="node-icon"><VideoPause /></el-icon>
      <span class="node-title">{{ data.label || '结束' }}</span>
      <div class="node-status">
        <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
        <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
        <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
      </div>
    </div>
    
    <div class="node-body">
      <div class="description">工作流结束节点</div>
    </div>

    <!-- 输入端口 -->
    <Handle
      type="target"
      :position="Position.Left"
      :style="{ top: '50%' }"
      class="node-handle"
    />
  </div>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'
import { VideoPause, Loading, Check, Close } from '@element-plus/icons-vue'

defineProps(['data'])
</script>

<style scoped>
.end-node {
  min-width: 150px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.end-node:hover {
  border-color: #f56c6c;
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

.end-node.selected {
  border-color: #f56c6c;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2);
}

.end-node.running {
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

.description {
  font-size: 12px;
  color: #909399;
}

.node-handle {
  width: 12px;
  height: 12px;
  background: #f56c6c;
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