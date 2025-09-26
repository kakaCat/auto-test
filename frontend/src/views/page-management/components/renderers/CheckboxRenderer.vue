<template>
  <el-checkbox-group
    :class="['canvas-checkbox-group', componentData.props?.class]"
    :style="componentData.props?.style"
    :size="componentData.props?.size || 'default'"
    :disabled="componentData.props?.disabled || false"
    model-value=""
  >
    <el-checkbox
      v-for="option in options"
      :key="option.value"
      :label="option.value"
      :disabled="option.disabled || false"
    >
      {{ option.label }}
    </el-checkbox>
  </el-checkbox-group>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  }
})

const options = computed(() => {
  return props.componentData.props?.options || [
    { label: '选项1', value: 'option1' },
    { label: '选项2', value: 'option2' },
    { label: '选项3', value: 'option3' }
  ]
})
</script>

<style scoped>
.canvas-checkbox-group {
  min-width: 120px;
}

.canvas-checkbox-group .el-checkbox {
  margin-right: 12px;
  margin-bottom: 8px;
}
</style>