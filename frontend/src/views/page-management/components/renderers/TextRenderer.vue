<template>
  <div
    class="canvas-text"
    :style="textStyle"
  >
    {{ componentData.props?.text || componentData.name || '文本内容' }}
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  }
})

const textStyle = computed(() => ({
  fontSize: props.componentData.props?.fontSize || '14px',
  color: props.componentData.props?.color || '#333',
  fontWeight: props.componentData.props?.fontWeight || 'normal',
  textAlign: props.componentData.props?.textAlign || 'left',
  lineHeight: props.componentData.props?.lineHeight || '1.5',
  fontFamily: props.componentData.props?.fontFamily || 'inherit'
}))
</script>

<style scoped>
.canvas-text {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 4px 8px;
  word-wrap: break-word;
  overflow: hidden;
}
</style>