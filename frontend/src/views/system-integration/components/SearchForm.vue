<template>
  <div class="search-form">
    <el-form
      :model="searchForm"
      :inline="true"
      label-width="80px"
      class="search-form-content"
    >
      <el-form-item
        v-for="field in config.fields"
        :key="field.prop"
        :label="field.label"
      >
        <!-- 输入框 -->
        <el-input
          v-if="field.type === 'input'"
          v-model="searchForm[field.prop]"
          :placeholder="field.placeholder"
          :clearable="field.clearable"
          style="width: 200px"
        />
        
        <!-- 选择器 -->
        <el-select
          v-else-if="field.type === 'select'"
          v-model="searchForm[field.prop]"
          :placeholder="field.placeholder"
          :clearable="field.clearable"
          style="width: 200px"
        >
          <el-option
            v-for="option in field.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          :icon="Search"
          @click="handleSearch"
        >
          搜索
        </el-button>
        <el-button
          :icon="Refresh"
          @click="handleReset"
        >
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'

interface Option {
  label: string
  value: string | number
}

interface Field {
  prop: string
  label: string
  type: 'input' | 'select'
  placeholder?: string
  clearable?: boolean
  options?: Option[]
}

interface SearchConfig {
  fields: Field[]
}

interface Props {
  modelValue: Record<string, any>
  config: SearchConfig
}

interface Emits {
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'search', value: Record<string, any>): void
  (e: 'reset'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const searchForm = reactive({ ...props.modelValue })

// 监听表单变化，同步到父组件
watch(
  () => searchForm,
  (newValue) => {
    emit('update:modelValue', { ...newValue })
  },
  { deep: true }
)

// 监听父组件传入的值变化
watch(
  () => props.modelValue,
  (newValue) => {
    Object.assign(searchForm, newValue)
  },
  { deep: true }
)

const handleSearch = (): void => {
  emit('search', { ...searchForm })
}

const handleReset = (): void => {
  // 重置表单
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  emit('reset')
}
</script>

<style scoped>
.search-form {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-form-content {
  margin: 0;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

@media (max-width: 768px) {
  .search-form {
    padding: 16px;
  }
  
  :deep(.el-form--inline .el-form-item) {
    display: block;
    margin-right: 0;
  }
  
  :deep(.el-input),
  :deep(.el-select) {
    width: 100% !important;
  }
}
</style>