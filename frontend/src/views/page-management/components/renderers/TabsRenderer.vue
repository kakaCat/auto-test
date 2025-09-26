<template>
  <el-tabs
    :class="['canvas-tabs', componentData.props?.class]"
    :style="componentData.props?.style"
    :type="componentData.props?.type || 'line'"
    :tab-position="componentData.props?.tabPosition || 'top'"
    :closable="componentData.props?.closable || false"
    model-value="tab1"
  >
    <el-tab-pane
      v-for="tab in tabs"
      :key="tab.name"
      :label="tab.label"
      :name="tab.name"
      :disabled="tab.disabled || false"
    >
      <div class="tab-content-placeholder">
        <el-icon><Folder /></el-icon>
        <span>{{ tab.label }}内容</span>
        <p class="tab-hint">拖拽组件到此处</p>
      </div>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup>
import { computed } from 'vue'
import { Folder } from '@element-plus/icons-vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  }
})

const tabs = computed(() => {
  return props.componentData.props?.tabs || [
    { name: 'tab1', label: '标签页1' },
    { name: 'tab2', label: '标签页2' },
    { name: 'tab3', label: '标签页3' }
  ]
})
</script>

<style scoped>
.canvas-tabs {
  min-width: 300px;
  min-height: 150px;
}

.tab-content-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  background-color: #fafafa;
  color: #909399;
  text-align: center;
  margin-top: 8px;
}

.tab-content-placeholder .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.tab-content-placeholder span {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.tab-hint {
  font-size: 12px;
  margin: 0;
  opacity: 0.8;
}
</style>