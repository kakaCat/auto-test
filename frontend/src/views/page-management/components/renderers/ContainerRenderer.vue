<template>
  <div
    :class="['canvas-container', componentData.props?.class]"
    :style="containerStyle"
  >
    <div class="container-placeholder">
      <el-icon><Grid /></el-icon>
      <span>容器</span>
      <p class="container-hint">
        拖拽组件到此处
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Grid } from '@element-plus/icons-vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  }
})

const containerStyle = computed(() => {
  const baseStyle = {
    padding: '16px',
    border: '2px dashed #dcdfe6',
    borderRadius: '4px',
    minHeight: '120px',
    backgroundColor: '#fafafa',
    ...props.componentData.props?.style
  }
  return baseStyle
})
</script>

<style scoped>
.canvas-container {
  min-width: 200px;
  position: relative;
}

.container-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 88px;
  color: #909399;
  text-align: center;
}

.container-placeholder .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.container-placeholder span {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.container-hint {
  font-size: 12px;
  margin: 0;
  opacity: 0.8;
}
</style>