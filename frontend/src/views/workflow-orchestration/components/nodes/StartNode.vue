<template>
  <div
    class="start-node"
    :class="{ selected: data.selected, running: data.status === 'running' }"
  >
    <div class="node-header">
      <el-icon class="node-icon">
        <VideoPlay />
      </el-icon>
      <span class="node-title">{{ data.label || '开始' }}</span>
      <div class="node-status">
        <el-icon
          v-if="data.status === 'running'"
          class="rotating"
        >
          <Loading />
        </el-icon>
        <el-icon
          v-else-if="data.status === 'success'"
          style="color: #67c23a"
        >
          <Check />
        </el-icon>
        <el-icon
          v-else-if="data.status === 'error'"
          style="color: #f56c6c"
        >
          <Close />
        </el-icon>
      </div>
    </div>
    
    <div class="node-body">
      <div class="description">
        工作流开始节点
      </div>
    </div>

    <!-- 输出端口 -->
    <Handle
      id="output"
      type="source"
      :position="Position.Right"
      :style="{ top: '50%' }"
      class="node-handle"
    />
  </div>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'
import { VideoPlay, Loading, Check, Close } from '@element-plus/icons-vue'

defineProps(['data'])
</script>

<style scoped>
.start-node {
  min-width: 150px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.start-node:hover {
  border-color: #67c23a;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.start-node.selected {
  border-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.start-node.running {
  border-color: #67c23a;
  animation: nodeRunning 2s ease-in-out infinite;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: #f0f9ff;
  border-radius: 6px 6px 0 0;
}

.node-icon {
  font-size: 16px;
  margin-right: 8px;
  color: #67c23a;
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
  background: #67c23a;
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