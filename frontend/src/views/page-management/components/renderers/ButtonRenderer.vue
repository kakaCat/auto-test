<template>
  <el-button
    :type="componentData.props?.type || 'primary'"
    :size="componentData.props?.size || 'default'"
    :disabled="componentData.props?.disabled || false"
    :loading="componentData.props?.loading || false"
    :plain="componentData.props?.plain || false"
    :round="componentData.props?.round || false"
    :circle="componentData.props?.circle || false"
    class="canvas-button"
  >
    {{ componentData.props?.text || componentData.name || '按钮' }}
  </el-button>
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
.canvas-button {
  width: 100%;
  height: 100%;
  min-width: 60px;
  min-height: 32px;
}
</style>