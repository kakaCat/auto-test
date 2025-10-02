<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑API测试场景' : '新增API测试场景'"
    width="80%"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <!-- 基本信息 -->
      <el-card class="form-section">
        <template #header>
          <span>基本信息</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="场景名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入API测试场景名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="formData.enabled" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入API测试场景描述"
          />
        </el-form-item>
      </el-card>

      <!-- 请求配置 -->
      <el-card class="form-section">
        <template #header>
          <span>请求配置</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="请求方法" prop="requestConfig.method">
              <el-select v-model="formData.requestConfig.method" style="width: 100%" disabled>
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="请求URL" prop="requestConfig.url">
              <el-input v-model="formData.requestConfig.url" placeholder="请求URL由API定义" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 请求头 -->
        <el-form-item label="请求头">
          <div class="key-value-editor" style="opacity: 0.6; pointer-events: none;">
            <div
              v-for="(header, index) in headersList"
              :key="index"
              class="key-value-row"
            >
              <el-input
                v-model="header.key"
                placeholder="Header名称"
                style="width: 40%"
                @input="updateHeaders"
                disabled
              />
              <el-input
                v-model="header.value"
                placeholder="Header值"
                style="width: 40%; margin-left: 10px"
                @input="updateHeaders"
                disabled
              />
              <el-button
                type="danger"
                size="small"
                @click="removeHeader(index)"
                style="margin-left: 10px"
                disabled
              >
                删除
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addHeader" disabled>
              添加Header
            </el-button>
          </div>
        </el-form-item>

        <!-- 请求体 -->
        <el-form-item label="请求体类型">
          <el-radio-group v-model="formData.requestConfig.bodyType" disabled>
            <el-radio value="none">无</el-radio>
            <el-radio value="json">JSON</el-radio>
            <el-radio value="form">表单</el-radio>
            <el-radio value="raw">原始</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="formData.requestConfig.bodyType !== 'none'" label="请求体内容">
          <el-input
            v-if="formData.requestConfig.bodyType === 'json'"
            v-model="requestBodyJson"
            type="textarea"
            :rows="6"
            placeholder="请输入JSON格式的请求体"
            @input="updateRequestBody"
          />
          <div v-else-if="formData.requestConfig.bodyType === 'form'" class="key-value-editor">
            <div
              v-for="(param, index) in formParamsList"
              :key="index"
              class="key-value-row"
            >
              <el-input
                v-model="param.key"
                placeholder="参数名"
                style="width: 40%"
                @input="updateFormParams"
              />
              <el-input
                v-model="param.value"
                placeholder="参数值"
                style="width: 40%; margin-left: 10px"
                @input="updateFormParams"
              />
              <el-button
                type="danger"
                size="small"
                @click="removeFormParam(index)"
                style="margin-left: 10px"
              >
                删除
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addFormParam">
              添加参数
            </el-button>
          </div>
          <el-input
            v-else
            v-model="formData.requestConfig.body"
            type="textarea"
            :rows="6"
            placeholder="请输入原始请求体内容"
          />
        </el-form-item>
      </el-card>

      <!-- 期望响应 -->
      <el-card class="form-section">
        <template #header>
          <span>期望响应</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态码">
              <el-input-number
                v-model="formData.expectedResponse.statusCode"
                :min="100"
                :max="599"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="响应体">
          <el-input
            v-model="expectedResponseJson"
            type="textarea"
            :rows="6"
            placeholder="请输入期望的JSON响应体"
            @input="updateExpectedResponse"
          />
        </el-form-item>
      </el-card>

      <!-- 执行配置 -->
      <el-card class="form-section">
        <template #header>
          <span>执行配置</span>
        </template>
        
        <el-row :gutter="20" style="opacity: 0.6; pointer-events: none;">
          <el-col :span="8">
            <el-form-item label="超时时间(ms)">
              <el-input-number
                v-model="formData.executionConfig.retryCount"
                :min="1000"
                :max="300000"
                style="width: 100%"
                disabled
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="重试次数">
              <el-input-number
                v-model="formData.executionConfig.retryCount"
                :min="0"
                :max="10"
                style="width: 100%"
                disabled
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="重试延迟(ms)">
              <el-input-number
                v-model="formData.executionConfig.retryDelay"
                :min="100"
                :max="60000"
                style="width: 100%"
                disabled
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { TestCase } from '@/types/test-case'
// 设置组件名称，便于调试与路由缓存
defineOptions({ name: 'ApiScenarioEditDialog' })
type ApiItem = { id?: string | number; name?: string; method?: string; url?: string; path?: string }

type Props = {
  visible: boolean
  testCaseData: Partial<TestCase> | null
  apiInfo: ApiItem
}

type Emits = {
  (e: 'update:visible', value: boolean): void
  (e: 'save', testCase: TestCase): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const isEdit = computed(() => !!props.testCaseData?.id)

// 表单数据
const formData = ref<TestCase>({
  id: '',
  apiId: '',
  name: '',
  description: '',
  enabled: true,
  category: '',
  priority: 'medium',
  tags: [],
  requestConfig: {
    method: props.apiInfo?.method || 'GET',
    url: props.apiInfo?.url || '',
    headers: {},
    queryParams: {},
    bodyType: 'none',
    body: null,
    timeout: 30000,
    followRedirects: true,
    validateSSL: true
  },
  expectedResponse: {
    statusCode: 200,
    headers: {},
    body: undefined
  },
  preConditions: [],
  postActions: [],
  executionConfig: {
    retryCount: 0,
    retryDelay: 1000,
    continueOnFailure: false,
    parallel: false,
    variables: {}
  },
  createdAt: '',
  updatedAt: '',
  executionCount: 0,
  successCount: 0
})

// 辅助数据
const headersList = ref<Array<{ key: string; value: string }>>([])
const formParamsList = ref<Array<{ key: string; value: string }>>([])
const requestBodyJson = ref('')
const expectedResponseJson = ref('')

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入API测试场景名称', trigger: 'blur' }
  ],
  'requestConfig.method': [
    { required: true, message: '请求方法由API定义', trigger: 'change' }
  ],
  'requestConfig.url': [
    { required: true, message: '请求URL由API定义', trigger: 'blur' }
  ]
}

// 监听props变化：确保方法与URL始终与API一致
watch(() => props.testCaseData, (newData) => {
  if (newData) {
    formData.value = {
      ...formData.value,
      ...newData,
      apiId: props.apiInfo.id?.toString() || ''
    }
    formData.value.requestConfig.method = props.apiInfo.method || formData.value.requestConfig.method
    formData.value.requestConfig.url = props.apiInfo.url || formData.value.requestConfig.url
    initializeHelperData()
  }
}, { immediate: true, deep: true })

watch(() => props.apiInfo, (api) => {
  formData.value.requestConfig.method = api?.method || formData.value.requestConfig.method
  formData.value.requestConfig.url = api?.url || formData.value.requestConfig.url
})

// 初始化辅助数据
const initializeHelperData = () => {
  // 初始化headers列表
  headersList.value = Object.entries(formData.value.requestConfig.headers || {}).map(([key, value]) => ({
    key,
    value: value as string
  }))
  
  // 初始化表单参数列表
  if (formData.value.requestConfig.bodyType === 'form' && formData.value.requestConfig.body) {
    formParamsList.value = Object.entries(formData.value.requestConfig.body).map(([key, value]) => ({
      key,
      value: String(value)
    }))
  }
  
  // 初始化JSON字符串
  if (formData.value.requestConfig.bodyType === 'json' && formData.value.requestConfig.body) {
    requestBodyJson.value = JSON.stringify(formData.value.requestConfig.body, null, 2)
  }
  
  if (formData.value.expectedResponse.body) {
    expectedResponseJson.value = JSON.stringify(formData.value.expectedResponse.body, null, 2)
  }
}

// Headers操作
const addHeader = () => {
  headersList.value.push({ key: '', value: '' })
}

const removeHeader = (index: number) => {
  headersList.value.splice(index, 1)
  updateHeaders()
}

const updateHeaders = () => {
  const headers: Record<string, string> = {}
  headersList.value.forEach(header => {
    if (header.key && header.value) {
      headers[header.key] = header.value
    }
  })
  formData.value.requestConfig.headers = headers
}

// 表单参数操作
const addFormParam = () => {
  formParamsList.value.push({ key: '', value: '' })
}

const removeFormParam = (index: number) => {
  formParamsList.value.splice(index, 1)
  updateFormParams()
}

const updateFormParams = () => {
  const params: Record<string, unknown> = {}
  formParamsList.value.forEach(param => {
    if (param.key && param.value) {
      params[param.key] = param.value
    }
  })
  formData.value.requestConfig.body = params
}

// 更新请求体
const updateRequestBody = () => {
  try {
    formData.value.requestConfig.body = JSON.parse(requestBodyJson.value)
  } catch (error) {
    // JSON格式错误，保持原值
  }
}

// 更新期望响应
const updateExpectedResponse = () => {
  try {
    formData.value.expectedResponse.body = JSON.parse(expectedResponseJson.value)
  } catch (error) {
    // JSON格式错误，保持原值
  }
}

// 处理保存
const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('save', formData.value)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 处理关闭
const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.form-section {
  margin-bottom: 20px;
}

.key-value-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
}

.key-value-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.key-value-row:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  text-align: right;
}
</style>