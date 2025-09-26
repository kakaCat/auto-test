<template>
  <el-input
    :type="componentData.props?.type || 'text'"
    :placeholder="componentData.props?.placeholder || '请输入内容'"
    :disabled="componentData.props?.disabled || false"
    :readonly="componentData.props?.readonly || false"
    :clearable="componentData.props?.clearable || false"
    :show-password="componentData.props?.showPassword || false"
    :size="componentData.props?.size || 'default'"
    :maxlength="componentData.props?.maxlength"
    :minlength="componentData.props?.minlength"
    class="canvas-input"
    model-value=""
  />
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.canvas-input {
  width: 100%;
  height: 100%;
}

.canvas-input :deep(.el-input__wrapper) {
  height: 100%;
}
</style>