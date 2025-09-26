<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择图标"
    width="600px"
    @close="handleClose"
  >
    <div class="icon-picker">
      <div class="icon-search">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索图标"
          clearable
        />
      </div>
      
      <div class="icon-grid">
        <div
          v-for="icon in filteredIcons"
          :key="icon"
          class="icon-item"
          :class="{ active: selectedIcon === icon }"
          @click="selectIcon(icon)"
        >
          <el-icon :size="24">
            <component :is="icon" />
          </el-icon>
          <span class="icon-name">{{ icon }}</span>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :disabled="!selectedIcon">
        确认
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'select': [icon: string]
}>()

const dialogVisible = ref(false)
const searchKeyword = ref('')
const selectedIcon = ref('')

// 常用图标列表
const iconList = [
  'User', 'Setting', 'Document', 'Folder', 'Search', 'Plus', 'Edit', 'Delete',
  'View', 'Hide', 'Star', 'Heart', 'Message', 'Bell', 'Home', 'Menu',
  'Close', 'Check', 'Warning', 'Info', 'Success', 'Error', 'Loading', 'Refresh'
]

const filteredIcons = computed(() => {
  if (!searchKeyword.value) return iconList
  return iconList.filter(icon => 
    icon.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    selectedIcon.value = ''
    searchKeyword.value = ''
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

const selectIcon = (icon: string) => {
  selectedIcon.value = icon
}

const handleConfirm = () => {
  if (selectedIcon.value) {
    emit('select', selectedIcon.value)
  }
}

const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.icon-picker {
  .icon-search {
    margin-bottom: 20px;
  }

  .icon-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 12px;
    max-height: 400px;
    overflow-y: auto;

    .icon-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 12px;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #409eff;
        background-color: #f0f9ff;
      }

      &.active {
        border-color: #409eff;
        background-color: #409eff;
        color: white;
      }

      .icon-name {
        font-size: 12px;
        margin-top: 4px;
        text-align: center;
      }
    }
  }
}
</style>