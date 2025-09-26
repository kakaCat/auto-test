<template>
  <el-select
    :class="['canvas-select', componentData.props?.class]"
    :style="componentData.props?.style"
    :placeholder="componentData.props?.placeholder || '请选择'"
    :size="componentData.props?.size || 'default'"
    :disabled="componentData.props?.disabled || false"
    :clearable="componentData.props?.clearable || false"
    :multiple="componentData.props?.multiple || false"
    model-value=""
  >
    <el-option
      v-for="option in options"
      :key="option.value"
      :label="option.label"
      :value="option.value"
    />
  </el-select>
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
.canvas-select {
  min-width: 120px;
  width: 100%;
}
</style>