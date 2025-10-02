<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑Mock配置' : '新增Mock配置'" width="80%" :before-close="handleClose" class="mock-edit-dialog">
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px" class="mock-form">
      <!-- 基本信息 -->
      <div class="form-section">
        <h3>基本信息</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Mock名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入Mock名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="formData.priority" :min="1" :max="100" placeholder="数字越小优先级越高" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入Mock描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="状态码" prop="statusCode">
              <el-select v-model="formData.statusCode" placeholder="选择状态码">
                <el-option label="200 - 成功" :value="200" />
                <el-option label="400 - 请求错误" :value="400" />
                <el-option label="401 - 未授权" :value="401" />
                <el-option label="403 - 禁止访问" :value="403" />
                <el-option label="404 - 未找到" :value="404" />
                <el-option label="500 - 服务器错误" :value="500" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="延迟(ms)" prop="delay">
              <el-input-number v-model="formData.delay" :min="0" :max="10000" placeholder="响应延迟时间" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="启用状态" prop="enabled">
              <el-switch v-model="formData.enabled" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 匹配条件 -->
      <div class="form-section">
        <h3>
          匹配条件
          <el-button type="primary" size="small" @click="addMatchCondition">
            <el-icon><Plus /></el-icon>
            添加条件
          </el-button>
        </h3>
        <div v-if="formData.matchConditions.length === 0" class="empty-conditions">
          <el-empty description="暂无匹配条件，点击上方按钮添加" :image-size="80" />
        </div>
        <div v-else class="conditions-list">
          <div v-for="(condition, index) in formData.matchConditions" :key="condition.id" class="condition-item">
            <el-card shadow="never" class="condition-card">
              <template #header>
                <div class="condition-header">
                  <span>条件 {{ index + 1 }}</span>
                  <el-button type="danger" size="small" text @click="removeMatchCondition(index)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
              <el-row :gutter="16">
                <el-col :span="6">
                  <el-form-item label="字段路径">
                    <el-input v-model="condition.field" placeholder="如: body.userId" />
                  </el-form-item>
                </el-col>
                <el-col :span="4">
                  <el-form-item label="操作符">
                    <el-select v-model="condition.operator">
                      <el-option label="等于" value="equals" />
                      <el-option label="不等于" value="not_equals" />
                      <el-option label="包含" value="contains" />
                      <el-option label="不包含" value="not_contains" />
                      <el-option label="大于" value="greater_than" />
                      <el-option label="小于" value="less_than" />
                      <el-option label="正则" value="regex" />
                      <el-option label="存在" value="exists" />
                      <el-option label="不存在" value="not_exists" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="期望值">
                    <el-input v-model="condition.value" placeholder="匹配的值" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="描述">
                    <el-input v-model="condition.description" placeholder="条件描述（可选）" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-card>
          </div>
        </div>
      </div>

      <!-- 响应数据 -->
      <div class="form-section">
        <h3>响应数据</h3>
        <el-form-item label="响应内容" prop="responseData">
          <div class="response-editor">
            <el-tabs v-model="responseTab" type="card">
              <el-tab-pane label="JSON编辑器" name="json">
                <el-input v-model="responseDataText" type="textarea" :rows="12" placeholder="请输入JSON格式的响应数据" @blur="validateJson" />
                <div v-if="jsonError" class="json-error">
                  <el-alert type="error" :title="jsonError" show-icon />
                </div>
              </el-tab-pane>
              <el-tab-pane label="可视化编辑" name="visual">
                <div class="visual-editor">
                  <el-alert type="info" title="可视化编辑器开发中..." show-icon />
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { MockConfig, MockMatchCondition } from '@/types/mock'
import type { ApiItem } from '../data/tableColumns'

// Props
interface Props {
  modelValue: boolean
  mockData?: MockConfig | null
  apiInfo: ApiItem
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  mockData: null
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [mockData: MockConfig]
}>()

// 响应式数据
const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const saving = ref(false)
const responseTab = ref('json')
const responseDataText = ref('')
const jsonError = ref('')

// 表单数据
const formData = reactive<MockConfig>({
  id: '',
  apiId: '',
  name: '',
  description: '',
  enabled: true,
  priority: 1,
  statusCode: 200,
  delay: 100,
  matchConditions: [],
  responseData: {},
  createdAt: '',
  updatedAt: ''
})

// 计算属性
const isEdit = computed(() => !!props.mockData?.id)

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入Mock名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在2-50个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请设置优先级', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '优先级范围1-100', trigger: 'blur' }
  ],
  statusCode: [
    { required: true, message: '请选择状态码', trigger: 'change' }
  ]
}

// 监听器
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    initFormData()
  }
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
  if (!newVal) {
    resetForm()
  }
})

watch(() => formData.responseData, (newVal) => {
  if (newVal && typeof newVal === 'object') {
    responseDataText.value = JSON.stringify(newVal, null, 2)
  }
}, { deep: true })

// 方法
const initFormData = () => {
  if (props.mockData) {
    Object.assign(formData, {
      ...props.mockData,
      matchConditions: props.mockData.matchConditions.map(condition => ({ ...condition }))
    })
    responseDataText.value = JSON.stringify(props.mockData.responseData || {}, null, 2)
  } else {
    resetFormData()
  }
}

const resetFormData = () => {
  Object.assign(formData, {
    name: '',
    description: '',
    enabled: true,
    priority: 1,
    statusCode: 200,
    delay: 100,
    matchConditions: [],
    responseData: {}
  })
  responseDataText.value = JSON.stringify({
    code: 200,
    message: '操作成功',
    data: {}
  }, null, 2)
}

const resetForm = () => {
  formRef.value?.resetFields()
  jsonError.value = ''
  saving.value = false
}

const handleClose = () => {
  visible.value = false
}

const addMatchCondition = () => {
  const newCondition: MockMatchCondition = {
    id: Date.now().toString(),
    type: 'exact',
    field: '',
    operator: 'equals',
    value: '',
    description: ''
  }
  formData.matchConditions?.push(newCondition)
}

const removeMatchCondition = (index: number) => {
  formData.matchConditions?.splice(index, 1)
}

const validateJson = () => {
  try {
    const parsed = JSON.parse(responseDataText.value)
    formData.responseData = parsed
    jsonError.value = ''
  } catch (error) {
    jsonError.value = 'JSON格式错误，请检查语法'
  }
}

const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    // 验证JSON
    validateJson()
    if (jsonError.value) {
      ElMessage.error('请修正JSON格式错误')
      return
    }

    // 验证匹配条件
    if (formData.matchConditions?.some(condition => !condition.field || !condition.value)) {
      ElMessage.error('请完善匹配条件信息')
      return
    }

    saving.value = true

    const mockConfig: MockConfig = {
      id: props.mockData?.id || '',
      apiId: props.apiInfo.id?.toString() || '',
      name: formData.name!,
      description: formData.description,
      enabled: formData.enabled!,
      priority: formData.priority!,
      matchConditions: formData.matchConditions!,
      responseData: formData.responseData!,
      statusCode: formData.statusCode!,
      delay: formData.delay,
      createdAt: props.mockData?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    emit('save', mockConfig)
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.mock-edit-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.mock-form {
  max-width: 100%;
}

.form-section {
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.empty-conditions {
  text-align: center;
  padding: 40px 0;
}

.conditions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.condition-item {
  width: 100%;
}

.condition-card {
  border: 1px solid #e4e7ed;
}

.condition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.response-editor {
  width: 100%;
}

.visual-editor {
  padding: 40px;
  text-align: center;
}

.json-error {
  margin-top: 8px;
}

.dialog-footer {
  text-align: right;
}
</style>