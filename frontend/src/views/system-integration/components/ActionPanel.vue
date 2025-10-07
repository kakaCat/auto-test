<template>
  <div
    v-if="selectedCount > 0"
    class="action-panel"
  >
    <div class="panel-content">
      <div class="selection-info">
        <el-icon><Select /></el-icon>
        <span>已选择 {{ selectedCount }} 项</span>
      </div>
      
      <div class="batch-actions">
        <el-button
          v-for="action in actions"
          :key="action.action"
          :type="action.type"
          :icon="action.icon"
          size="small"
          @click="handleAction(action.action)"
        >
          {{ action.label }}
        </el-button>
        
        <el-button
          size="small"
          :icon="Close"
          @click="handleClearSelection"
        >
          取消选择
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Select, Close } from '@element-plus/icons-vue'

interface Action {
  label: string
  action: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  icon?: any
}

interface Props {
  selectedCount: number
  actions: Action[]
}

interface Emits {
  (e: 'action', action: string): void
  (e: 'clear-selection'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const handleAction = (action: string): void => {
  emit('action', action)
}

const handleClearSelection = (): void => {
  emit('clear-selection')
}
</script>

<style scoped>
.action-panel {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  border-radius: 8px;
  padding: 16px 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
  z-index: 1000;
  min-width: 400px;
}

.panel-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.batch-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

@media (max-width: 768px) {
  .action-panel {
    left: 10px;
    right: 10px;
    transform: none;
    min-width: auto;
    width: calc(100% - 20px);
  }
  
  .panel-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .batch-actions {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>