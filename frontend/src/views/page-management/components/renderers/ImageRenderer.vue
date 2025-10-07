<template>
  <div class="canvas-image">
    <img
      v-if="componentData.props?.src"
      :src="componentData.props.src"
      :alt="componentData.props?.alt || '图片'"
      :style="imageStyle"
      @error="handleImageError"
    >
    <div
      v-else
      class="image-placeholder"
    >
      <el-icon :size="24">
        <Picture />
      </el-icon>
      <span>{{ componentData.props?.alt || '图片' }}</span>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { Picture } from '@element-plus/icons-vue'

const props = defineProps({
  componentData: {
    type: Object,
    required: true
  }
})

const imageStyle = computed(() => ({
  width: '100%',
  height: '100%',
  objectFit: props.componentData.props?.objectFit || 'cover',
  borderRadius: props.componentData.props?.borderRadius || '0px'
}))

const handleImageError = (event) => {
  console.warn('图片加载失败:', event.target.src)
}
</script>

<style scoped>
.canvas-image {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border: 1px dashed #dcdfe6;
  color: #909399;
  font-size: 12px;
  gap: 8px;
}

img {
  display: block;
}
</style>