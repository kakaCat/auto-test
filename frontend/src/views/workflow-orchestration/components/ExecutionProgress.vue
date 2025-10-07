<template>
  <div
    v-if="visible"
    class="execution-progress"
  >
    <div class="progress-header">
      <h4>执行进度</h4>
      <el-button 
        type="text" 
        class="close-btn"
        @click="$emit('close')"
      >
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    
    <div class="progress-content">
      <!-- 总体进度 -->
      <div class="overall-progress">
        <div class="progress-info">
          <span>总体进度</span>
          <span>{{ completedNodes }}/{{ totalNodes }}</span>
        </div>
        <el-progress 
          :percentage="overallProgress" 
          :status="progressStatus"
          :stroke-width="8"
        />
      </div>
      
      <!-- 节点执行状态列表 -->
      <div class="node-list">
        <div class="list-header">
          节点执行状态
        </div>
        <div class="node-items">
          <div 
            v-for="node in nodeList" 
            :key="node.id"
            class="node-item"
            :class="getNodeStatusClass(node.status)"
          >
            <div class="node-info">
              <div class="node-name">
                {{ node.label }}
              </div>
              <div class="node-type">
                {{ getNodeTypeText(node.type) }}
              </div>
            </div>
            
            <div class="node-status">
              <el-icon class="status-icon">
                <Loading v-if="node.status === 'running'" />
                <Check v-else-if="node.status === 'success'" />
                <Close v-else-if="node.status === 'error'" />
                <Clock v-else />
              </el-icon>
              <span class="status-text">{{ getStatusText(node.status) }}</span>
            </div>
            
            <!-- 执行时间 -->
            <div
              v-if="node.executionTime"
              class="execution-time"
            >
              {{ node.executionTime }}ms
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误信息 -->
      <div
        v-if="errorNodes.length > 0"
        class="error-section"
      >
        <div class="error-header">
          执行错误
        </div>
        <div class="error-items">
          <div 
            v-for="error in errorNodes" 
            :key="error.id"
            class="error-item"
          >
            <div class="error-node">
              {{ error.label }}
            </div>
            <div class="error-message">
              {{ error.error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Close, Check, Loading, Clock } from '@element-plus/icons-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  nodeStates: {
    type: Map,
    default: () => new Map()
  },
  nodes: {
    type: Array,
    default: () => []
  }
})

defineEmits(['close'])

// 计算节点列表
const nodeList = computed(() => {
  return props.nodes.map(node => {
    const state = props.nodeStates.get(node.id)
    return {
      id: node.id,
      label: node.data?.label || node.id,
      type: node.type,
      status: state?.status || 'pending',
      executionTime: state?.executionTime,
      error: state?.error
    }
  })
})

// 计算总体进度
const totalNodes = computed(() => props.nodes.length)
const completedNodes = computed(() => {
  return nodeList.value.filter(node => 
    node.status === 'success' || node.status === 'error'
  ).length
})

const overallProgress = computed(() => {
  if (totalNodes.value === 0) return 0
  return Math.round((completedNodes.value / totalNodes.value) * 100)
})

const progressStatus = computed(() => {
  const hasError = nodeList.value.some(node => node.status === 'error')
  const isRunning = nodeList.value.some(node => node.status === 'running')
  
  if (hasError) return 'exception'
  if (isRunning) return undefined
  if (overallProgress.value === 100) return 'success'
  return undefined
})

// 错误节点
const errorNodes = computed(() => {
  return nodeList.value.filter(node => node.status === 'error')
})

// 获取节点状态样式类
const getNodeStatusClass = (status) => {
  return `node-${status}`
}

// 获取节点类型文本
const getNodeTypeText = (type) => {
  const typeMap = {
    'start': '开始节点',
    'end': '结束节点',
    'api-call': 'API调用',
    'data-transform': '数据转换',
    'condition': '条件分支',
    'parallel': '并行执行'
  }
  return typeMap[type] || type
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待执行',
    'running': '执行中',
    'success': '成功',
    'error': '失败'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.execution-progress {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 350px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
}

.progress-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.close-btn {
  padding: 4px;
  color: #909399;
}

.progress-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.overall-progress {
  margin-bottom: 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.node-list {
  margin-bottom: 20px;
}

.list-header {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.node-items {
  max-height: 300px;
  overflow-y: auto;
}

.node-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.node-item.node-pending {
  background: #f5f7fa;
  border-color: #e4e7ed;
}

.node-item.node-running {
  background: #ecf5ff;
  border-color: #409eff;
}

.node-item.node-success {
  background: #f0f9ff;
  border-color: #67c23a;
}

.node-item.node-error {
  background: #fef0f0;
  border-color: #f56c6c;
}

.node-info {
  flex: 1;
}

.node-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.node-type {
  font-size: 12px;
  color: #909399;
}

.node-status {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-right: 8px;
}

.status-icon {
  font-size: 16px;
}

.node-pending .status-icon {
  color: #909399;
}

.node-running .status-icon {
  color: #409eff;
}

.node-success .status-icon {
  color: #67c23a;
}

.node-error .status-icon {
  color: #f56c6c;
}

.status-text {
  font-size: 12px;
  color: #606266;
}

.execution-time {
  font-size: 12px;
  color: #909399;
  min-width: 50px;
  text-align: right;
}

.error-section {
  border-top: 1px solid #e4e7ed;
  padding-top: 16px;
}

.error-header {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
  margin-bottom: 12px;
}

.error-item {
  padding: 8px 12px;
  background: #fef0f0;
  border-radius: 4px;
  margin-bottom: 8px;
}

.error-node {
  font-size: 12px;
  font-weight: 500;
  color: #f56c6c;
  margin-bottom: 4px;
}

.error-message {
  font-size: 12px;
  color: #606266;
  word-break: break-word;
}
</style>