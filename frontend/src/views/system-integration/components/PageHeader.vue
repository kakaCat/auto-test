<template>
  <div class="page-header">
    <div class="header-content">
      <div class="title-section">
        <h1 class="page-title">
          {{ title }}
        </h1>
        <p
          v-if="description"
          class="page-description"
        >
          {{ description }}
        </p>
      </div>
      <div class="action-section">
        <el-button
          v-for="action in actions"
          :key="action.action"
          :type="action.type"
          :icon="action.icon"
          @click="handleAction(action.action)"
        >
          {{ action.label }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Action {
  label: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  action: string
  icon?: string
}

interface Props {
  title: string
  description?: string
  actions: Action[]
}

interface Emits {
  (e: 'action', action: string): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const handleAction = (action: string): void => {
  emit('action', action)
}
</script>

<style scoped>
.page-header {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-section {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.action-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
  }
  
  .action-section {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>