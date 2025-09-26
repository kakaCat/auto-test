<template>
  <el-radio-group
    :class="['canvas-radio-group', componentData.props?.class]"
    :style="componentData.props?.style"
    :size="componentData.props?.size || 'default'"
    :disabled="componentData.props?.disabled || false"
    model-value=""
  >
    <el-radio
      v-for="option in options"
      :key="option.value"
      :label="option.value"
      :disabled="option.disabled || false"
    >
      {{ option.label }}
    </el-radio>
  </el-radio-group>
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
.canvas-radio-group {
  min-width: 120px;
}

.canvas-radio-group .el-radio {
  margin-right: 12px;
  margin-bottom: 8px;
}
</style>