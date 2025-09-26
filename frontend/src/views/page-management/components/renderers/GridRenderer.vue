<template>
  <el-row
    :class="['canvas-grid', componentData.props?.class]"
    :style="componentData.props?.style"
    :gutter="componentData.props?.gutter || 20"
    :justify="componentData.props?.justify || 'start'"
    :align="componentData.props?.align || 'top'"
  >
    <el-col
      v-for="col in columns"
      :key="col.id"
      :span="col.span"
      :offset="col.offset || 0"
      :push="col.push || 0"
      :pull="col.pull || 0"
    >
      <div class="grid-col-placeholder">
        <el-icon><Grid /></el-icon>
        <span>{{ col.span }}/24</span>
      </div>
    </el-col>
  </el-row>
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

const columns = computed(() => {
  return props.componentData.props?.columns || [
    { id: 1, span: 12 },
    { id: 2, span: 12 }
  ]
})
</script>

<style scoped>
.canvas-grid {
  min-width: 200px;
  min-height: 80px;
}

.grid-col-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  background-color: #fafafa;
  color: #909399;
  text-align: center;
}

.grid-col-placeholder .el-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.grid-col-placeholder span {
  font-size: 12px;
  font-weight: 500;
}
</style>