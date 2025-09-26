<template>
  <div class="page-basic-info">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      class="basic-info-form"
    >
      <!-- 基本信息区域 -->
      <div class="form-section">
        <div class="section-title">
          <h3>基本信息</h3>
          <p>配置页面的基础信息和属性</p>
        </div>
        
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="页面名称" prop="name" required>
              <el-input
                v-model="formData.name"
                placeholder="请输入页面名称"
                maxlength="100"
                show-word-limit
                @blur="handleValidate"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="页面路径" prop="path">
              <el-input
                v-model="formData.path"
                placeholder="请输入页面路径，如：/user/list"
                maxlength="200"
                @blur="handleValidate"
              >
                <template #prepend>/</template>
              </el-input>
              <div class="form-tip">留空表示无独立路由(如弹框、抽屉等)</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="页面描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入页面功能描述"
            :rows="3"
            maxlength="500"
            show-word-limit
            @blur="handleValidate"
          />
        </el-form-item>
      </div>

      <!-- 页面配置区域 -->
      <div class="form-section">
        <div class="section-title">
          <h3>页面配置</h3>
          <p>设置页面类型、图标和状态</p>
        </div>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="页面类型" prop="type" required>
              <el-select
                v-model="formData.type"
                placeholder="请选择页面类型"
                style="width: 100%"
                @change="handleValidate"
              >
                <el-option
                  v-for="option in pageTypeOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                >
                  <div class="option-item">
                    <span class="option-label">{{ option.label }}</span>
                    <span class="option-desc">{{ option.description }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="页面状态" prop="enabled">
              <el-switch
                v-model="formData.enabled"
                active-text="启用"
                inactive-text="禁用"
                @change="handleValidate"
              />
              <div class="form-tip">禁用后页面将不会显示在导航中</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="页面图标" prop="icon">
          <div class="icon-selector">
            <div class="icon-preview">
              <el-icon v-if="formData.icon" :size="24">
                <component :is="formData.icon" />
              </el-icon>
              <span v-else class="no-icon">未选择图标</span>
            </div>
            <div class="icon-actions">
              <el-button @click="showIconPicker = true">选择图标</el-button>
              <el-button @click="showUploadDialog = true">上传图标</el-button>
              <el-button v-if="formData.icon" @click="clearIcon">清除</el-button>
            </div>
          </div>
        </el-form-item>
      </div>


    </el-form>

    <!-- 图标选择器对话框 -->
    <!-- <IconPickerDialog
      v-model="showIconPicker"
      @select="handleIconSelect"
    /> -->

    <!-- 图标上传对话框 -->
    <!-- <IconUploadDialog
      v-model="showUploadDialog"
      @upload="handleIconUpload"
    /> -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { PageBasicInfo } from '../../types/page-config'
// import IconPickerDialog from '../dialogs/IconPickerDialog.vue'
// import IconUploadDialog from '../dialogs/IconUploadDialog.vue'


const props = withDefaults(defineProps<{
  modelValue: PageBasicInfo
  isEdit?: boolean
}>(), {
  isEdit: false
})

const emit = defineEmits<{
  'update:modelValue': [value: PageBasicInfo]
  'validate': [stepIndex: number, isValid: boolean]
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const showIconPicker = ref(false)
const showUploadDialog = ref(false)


// 表单数据
const formData = reactive<PageBasicInfo>({ ...props.modelValue })

// 页面类型选项
const pageTypeOptions = [
  {
    value: 'normal',
    label: '普通页面',
    description: '标准的页面类型，有独立的路由'
  },
  {
    value: 'modal',
    label: '弹框页面',
    description: '以弹出对话框形式显示的页面'
  },
  {
    value: 'fullscreen',
    label: '全屏页面',
    description: '全屏显示的页面，通常用于展示或编辑'
  },
  {
    value: 'embedded',
    label: '嵌入页面',
    description: '嵌入到其他页面中的子页面'
  },
  {
    value: 'mobile',
    label: '移动页面',
    description: '专为移动端设计的页面'
  }
]

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入页面名称', trigger: 'blur' },
    { min: 1, max: 100, message: '页面名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  path: [
    {
      pattern: /^\/[a-zA-Z0-9\-_\/]*$/,
      message: '页面路径格式不正确，应以/开头，只能包含字母、数字、-、_、/',
      trigger: 'blur'
    }
  ],
  type: [
    { required: true, message: '请选择页面类型', trigger: 'change' }
  ]
}

// 监听表单数据变化
watch(formData, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

// 监听外部数据变化
watch(() => props.modelValue, (newVal) => {
  Object.assign(formData, newVal)
}, { deep: true })





// 处理图标选择
const handleIconSelect = (icon: string) => {
  formData.icon = icon
  showIconPicker.value = false
  handleValidate()
}

// 处理图标上传
const handleIconUpload = (iconUrl: string) => {
  formData.icon = iconUrl
  showUploadDialog.value = false
  handleValidate()
}

// 清除图标
const clearIcon = () => {
  formData.icon = ''
  handleValidate()
}

// 验证表单
const handleValidate = async () => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validate()
    emit('validate', 0, true)
    return true
  } catch (error) {
    emit('validate', 0, false)
    return false
  }
}

// 暴露验证方法
const validate = async () => {
  return await handleValidate()
}

defineExpose({
  validate
})
</script>

<style lang="scss" scoped>
.page-basic-info {
  .basic-info-form {
    max-width: 800px;
  }

  .form-section {
    margin-bottom: 40px;
    
    &:last-child {
      margin-bottom: 0;
    }

    .section-title {
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e4e7ed;

      h3 {
        margin: 0 0 5px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }

  .option-item {
    display: flex;
    flex-direction: column;
    
    .option-label {
      font-size: 14px;
      color: #303133;
    }
    
    .option-desc {
      font-size: 12px;
      color: #909399;
      margin-top: 2px;
    }
  }

  .icon-selector {
    display: flex;
    align-items: center;
    gap: 16px;

    .icon-preview {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border: 1px dashed #d9d9d9;
      border-radius: 4px;
      background-color: #fafafa;

      .no-icon {
        font-size: 12px;
        color: #c0c4cc;
      }
    }

    .icon-actions {
      display: flex;
      gap: 8px;
    }
  }
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-group__prepend) {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #909399;
}
</style>