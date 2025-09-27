<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="dialogTitle"
    width="700px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      @submit.prevent
    >
      <el-form-item label="选择API" prop="api_id">
        <el-select
          v-model="form.api_id"
          placeholder="请选择API接口"
          style="width: 100%"
          filterable
          :disabled="mode === 'edit'"
        >
          <el-option
            v-for="api in apis"
            :key="api.id"
            :value="api.id"
          >
            <div class="api-option">
              <div class="api-main">
                <el-tag :type="getMethodColor(api.method)" size="small">
                  {{ api.method }}
                </el-tag>
                <span class="api-name">{{ api.name }}</span>
              </div>
              <div class="api-path">{{ api.path }}</div>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="执行类型" prop="execution_type">
            <el-radio-group v-model="form.execution_type">
              <el-radio label="parallel">并行执行</el-radio>
              <el-radio label="serial">串行执行</el-radio>
            </el-radio-group>
            <div class="form-tip">
              并行：与其他API同时执行；串行：按顺序依次执行
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="执行顺序" prop="execution_order">
            <el-input-number
              v-model="form.execution_order"
              :min="0"
              :max="999"
              placeholder="执行顺序"
              style="width: 100%"
            />
            <div class="form-tip">
              数字越小越先执行，仅对串行执行有效
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="触发动作" prop="trigger_action">
        <el-select
          v-model="form.trigger_action"
          placeholder="请选择触发动作"
          style="width: 100%"
          clearable
        >
          <el-option label="页面加载" value="load" />
          <el-option label="按钮点击" value="click" />
          <el-option label="表单提交" value="submit" />
          <el-option label="输入变化" value="change" />
          <el-option label="搜索操作" value="search" />
          <el-option label="弹框打开" value="open" />
          <el-option label="弹框关闭" value="close" />
          <el-option label="编辑操作" value="edit" />
          <el-option label="删除操作" value="delete" />
          <el-option label="刷新操作" value="refresh" />
          <el-option label="成功回调" value="success" />
          <el-option label="失败回调" value="error" />
        </el-select>
      </el-form-item>

      <el-form-item label="API作用" prop="api_purpose">
        <el-input
          v-model="form.api_purpose"
          placeholder="描述这个API在页面中的作用，如：获取用户列表、提交表单数据"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="成功后动作" prop="success_action">
            <el-select
              v-model="form.success_action"
              placeholder="API成功后的动作"
              style="width: 100%"
              clearable
            >
              <el-option label="跳转页面" value="跳转页面" />
              <el-option label="刷新页面" value="刷新页面" />
              <el-option label="关闭弹框" value="关闭弹框" />
              <el-option label="打开弹框" value="打开弹框" />
              <el-option label="显示成功提示" value="显示成功提示" />
              <el-option label="更新列表" value="更新列表" />
              <el-option label="重置表单" value="重置表单" />
              <el-option label="设置用户状态" value="设置用户状态" />
              <el-option label="渲染数据" value="渲染数据" />
              <el-option label="显示统计" value="显示统计" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="失败后动作" prop="error_action">
            <el-select
              v-model="form.error_action"
              placeholder="API失败后的动作"
              style="width: 100%"
              clearable
            >
              <el-option label="显示错误提示" value="显示错误提示" />
              <el-option label="显示加载失败" value="显示加载失败" />
              <el-option label="使用默认数据" value="使用默认数据" />
              <el-option label="重试请求" value="重试请求" />
              <el-option label="跳转错误页" value="跳转错误页" />
              <el-option label="隐藏组件" value="隐藏组件" />
              <el-option label="禁用功能" value="禁用功能" />
              <el-option label="记录错误日志" value="记录错误日志" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="执行条件">
        <el-input
          v-model="conditionsText"
          type="textarea"
          placeholder="可选：JSON格式的执行条件，如：{&quot;userRole&quot;: &quot;admin&quot;, &quot;hasPermission&quot;: true}"
          :rows="3"
          @blur="validateConditions"
        />
        <div class="form-tip">
          可选配置，用于控制API在特定条件下才执行，格式为JSON对象
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ mode === 'create' ? '添加' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { pageApi as pageApiService } from '@/api/page-management'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  pageApi: {
    type: Object,
    default: null
  },
  page: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create' // create, edit
  },
  apis: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const formRef = ref()
const submitting = ref(false)
const conditionsText = ref('')

const form = reactive({
  api_id: null,
  execution_type: 'parallel',
  execution_order: 0,
  trigger_action: '',
  api_purpose: '',
  success_action: '',
  error_action: '',
  conditions: null
})

// 表单验证规则
const rules = {
  api_id: [
    { required: true, message: '请选择API接口', trigger: 'change' }
  ],
  execution_type: [
    { required: true, message: '请选择执行类型', trigger: 'change' }
  ],
  execution_order: [
    { required: true, message: '请输入执行顺序', trigger: 'blur' },
    { type: 'number', min: 0, max: 999, message: '执行顺序必须在0-999之间', trigger: 'blur' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  const pageTitle = props.page ? ` - ${props.page.name}` : ''
  return (props.mode === 'create' ? '添加API关联' : '编辑API关联') + pageTitle
})

// 监听器
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      resetForm()
      if (props.pageApi && props.mode === 'edit') {
        // 编辑模式，填充表单数据
        Object.assign(form, {
          api_id: props.pageApi.api_id,
          execution_type: props.pageApi.execution_type,
          execution_order: props.pageApi.execution_order,
          trigger_action: props.pageApi.trigger_action || '',
          api_purpose: props.pageApi.api_purpose || '',
          success_action: props.pageApi.success_action || '',
          error_action: props.pageApi.error_action || '',
          conditions: props.pageApi.conditions
        })
        
        // 设置条件文本
        if (props.pageApi.conditions) {
          conditionsText.value = JSON.stringify(props.pageApi.conditions, null, 2)
        }
      }
    }
  },
  { immediate: true }
)

// 方法
const resetForm = () => {
  Object.assign(form, {
    api_id: null,
    execution_type: 'parallel',
    execution_order: 0,
    trigger_action: '',
    api_purpose: '',
    success_action: '',
    error_action: '',
    conditions: null
  })
  
  conditionsText.value = ''
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const validateConditions = () => {
  if (!conditionsText.value.trim()) {
    form.conditions = null
    return
  }
  
  try {
    form.conditions = JSON.parse(conditionsText.value)
  } catch (error) {
    ElMessage.warning('执行条件格式不正确，请检查JSON格式')
    form.conditions = null
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  try {
    // 表单验证
    await formRef.value.validate()
    
    // 验证条件格式
    validateConditions()
    
    submitting.value = true
    
    const submitData = {
      page_id: props.page.id,
      ...form
    }
    
    let response
    if (props.mode === 'create') {
      // 添加API关联
      response = await pageApiService.addPageApi(props.page.id, submitData)
    } else {
      // 更新API关联
      response = await pageApiService.updatePageApi(props.pageApi.id, submitData)
    }
    
    if (!response.success) {
      throw new Error(response.message || '操作失败')
    }
    
    emit('success')
    
  } catch (error) {
    if (error.message) {
      console.error('提交失败:', error)
      ElMessage.error('提交失败: ' + error.message)
    }
  } finally {
    submitting.value = false
  }
}

// 工具方法
const getMethodColor = (method) => {
  const colorMap = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return colorMap[method] || ''
}
</script>

<style scoped>
.api-option {
  width: 100%;
}

.api-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.api-name {
  font-weight: 500;
  color: #303133;
}

.api-path {
  font-size: 12px;
  color: #909399;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-select-dropdown__item) {
  height: auto;
  padding: 8px 20px;
}
</style>