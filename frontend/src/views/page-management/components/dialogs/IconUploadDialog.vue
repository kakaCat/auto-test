<template>
  <el-dialog
    v-model="dialogVisible"
    title="上传图标"
    width="400px"
    @close="handleClose"
  >
    <div class="icon-upload">
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".svg,.png,.jpg,.jpeg"
        :limit="1"
      >
        <el-icon class="el-icon--upload">
          <upload-filled />
        </el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 SVG、PNG、JPG 格式，文件大小不超过 2MB
          </div>
        </template>
      </el-upload>
    </div>

    <template #footer>
      <el-button @click="handleClose">
        取消
      </el-button>
      <el-button
        type="primary"
        :disabled="!selectedFile"
        @click="handleConfirm"
      >
        确认上传
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'upload': [iconUrl: string]
}>()

const dialogVisible = ref(false)
const selectedFile = ref<UploadFile | null>(null)

watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    selectedFile.value = null
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file
}

const handleConfirm = () => {
  if (selectedFile.value) {
    // 这里应该实现实际的文件上传逻辑
    // 暂时返回一个模拟的URL
    const mockUrl = URL.createObjectURL(selectedFile.value.raw!)
    emit('upload', mockUrl)
  }
}

const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.icon-upload {
  .upload-demo {
    width: 100%;
  }
}
</style>