<template>
  <el-form
    :class="['canvas-form', componentData.props?.class]"
    :style="componentData.props?.style"
    :label-width="componentData.props?.labelWidth || '80px'"
    :label-position="componentData.props?.labelPosition || 'right'"
    :size="componentData.props?.size || 'default'"
  >
    <div class="form-placeholder">
      <el-icon><Document /></el-icon>
      <span>表单容器</span>
      <p class="form-hint">
        拖拽表单项到此处
      </p>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'

defineProps({
  componentData: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.canvas-form {
  min-width: 200px;
  min-height: 120px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  position: relative;
}

.form-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 120px;
  color: #909399;
  text-align: center;
}

.form-placeholder .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.form-placeholder span {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.form-hint {
  font-size: 12px;
  margin: 0;
  opacity: 0.8;
}
</style>