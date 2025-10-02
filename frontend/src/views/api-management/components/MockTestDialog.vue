<template>
  <el-dialog v-model="visible" :title="`测试Mock - ${mockData?.name}`" width="70%" :before-close="handleClose" class="mock-test-dialog">
    <div class="mock-test">
      <!-- Mock信息 -->
      <div class="mock-info">
        <el-descriptions title="Mock配置信息" :column="2" border>
          <el-descriptions-item label="Mock名称">{{ mockData?.name }}</el-descriptions-item>
          <el-descriptions-item label="优先级">{{ mockData?.priority }}</el-descriptions-item>
          <el-descriptions-item label="状态码">{{ mockData?.statusCode }}</el-descriptions-item>
          <el-descriptions-item label="延迟">{{ mockData?.delay }}ms</el-descriptions-item>
          <el-descriptions-item label="启用状态">
            <el-tag :type="mockData?.enabled ? 'success' : 'danger'">
              {{ mockData?.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="匹配条件数">{{ mockData?.matchConditions?.length || 0 }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 测试输入 -->
      <div class="test-input">
        <h3>测试输入</h3>
        <el-tabs v-model="inputTab" type="card">
          <el-tab-pane label="请求参数" name="params">
            <el-form :model="testForm" label-width="100px">
              <el-form-item label="请求方法">
                <el-tag>{{ apiInfo.method }}</el-tag>
              </el-form-item>
              <el-form-item label="请求URL">
                <el-input v-model="testForm.url" :value="apiInfo.url" readonly />
              </el-form-item>
              <el-form-item label="请求头">
                <el-input v-model="testForm.headers" type="textarea" :rows="3" placeholder="JSON格式的请求头" />
              </el-form-item>
              <el-form-item label="请求体">
                <el-input v-model="testForm.body" type="textarea" :rows="8" placeholder="JSON格式的请求体" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="快速模板" name="templates">
            <div class="templates">
              <el-button v-for="template in testTemplates" :key="template.name" @click="applyTemplate(template)" style="margin: 4px;">
                {{ template.name }}
              </el-button>
            </div>
            <el-divider />
            <div class="template-preview">
              <h4>模板预览</h4>
              <pre v-if="selectedTemplate">{{ JSON.stringify(selectedTemplate.data, null, 2) }}</pre>
              <el-empty v-else description="选择上方模板查看内容" :image-size="60" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 匹配条件检查 -->
      <div class="match-check">
        <h3>
          匹配条件检查
          <el-button type="primary" size="small" @click="checkMatch">
            <el-icon><Search /></el-icon>
            检查匹配
          </el-button>
        </h3>
        <div v-if="matchResults.length > 0" class="match-results">
          <div v-for="(result, index) in matchResults" :key="index" class="match-result">
            <el-card shadow="never" :class="{ 'match-success': result.matched, 'match-failed': !result.matched }">
              <template #header>
                <div class="result-header">
                  <span>条件 {{ index + 1 }}: {{ result.condition.field }}</span>
                  <el-tag :type="result.matched ? 'success' : 'danger'" size="small">
                    {{ result.matched ? '匹配' : '不匹配' }}
                  </el-tag>
                </div>
              </template>
              <div class="result-content">
                <p><strong>期望:</strong> {{ result.condition.operator }} {{ result.condition.value }}</p>
                <p><strong>实际:</strong> {{ result.actualValue }}</p>
                <p v-if="result.reason"><strong>原因:</strong> {{ result.reason }}</p>
              </div>
            </el-card>
          </div>
        </div>
        <el-empty v-else description="点击检查匹配按钮查看结果" :image-size="60" />
      </div>

      <!-- 测试结果 -->
      <div class="test-result">
        <h3>
          测试结果
          <el-button type="success" size="small" @click="runTest" :loading="testing">
            <el-icon><VideoPlay /></el-icon>
            执行测试
          </el-button>
        </h3>
        <div v-if="testResult" class="result-display">
          <el-tabs v-model="resultTab" type="card">
            <el-tab-pane label="响应数据" name="response">
              <div class="response-info">
                <el-descriptions :column="3" border size="small">
                  <el-descriptions-item label="状态码">
                    <el-tag :type="getStatusType(testResult.statusCode)">
                      {{ testResult.statusCode }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="响应时间">{{ testResult.responseTime }}ms</el-descriptions-item>
                  <el-descriptions-item label="数据来源">
                    <el-tag :type="testResult.isMocked ? 'warning' : 'primary'">
                      {{ testResult.isMocked ? 'Mock数据' : '真实接口' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
              <div class="response-body">
                <h4>响应内容</h4>
                <pre class="json-display">{{ JSON.stringify(testResult.data, null, 2) }}</pre>
              </div>
            </el-tab-pane>
            <el-tab-pane label="请求详情" name="request">
              <div class="request-details">
                <h4>请求信息</h4>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="URL">{{ testResult.request?.url }}</el-descriptions-item>
                  <el-descriptions-item label="方法">{{ testResult.request?.method }}</el-descriptions-item>
                  <el-descriptions-item label="请求头">
                    <pre>{{ JSON.stringify(testResult.request?.headers, null, 2) }}</pre>
                  </el-descriptions-item>
                  <el-descriptions-item label="请求体">
                    <pre>{{ JSON.stringify(testResult.request?.body, null, 2) }}</pre>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        <el-empty v-else description="点击执行测试按钮查看结果" :image-size="60" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="saveAsTestCase">保存为API测试场景</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, VideoPlay } from '@element-plus/icons-vue'
import type { MockConfig } from '@/types/mock'
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
}>()

// 响应式数据
const visible = ref(props.modelValue)
const inputTab = ref('params')
const resultTab = ref('response')
const testing = ref(false)
const selectedTemplate = ref<TestTemplate | null>(null)

// 测试表单
const testForm = reactive({
  url: '',
  headers: '{\n  "Content-Type": "application/json"\n}',
  body: '{\n  "type": "success",\n  "userId": 123\n}'
})

// 强类型定义，避免使用 any
interface TestTemplate {
  name: string
  data: {
    headers: Record<string, unknown>
    body: unknown
  }
}

type Operator = 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'regex' | 'exists' | 'not_exists'

interface MatchCondition {
  field: string
  operator: Operator
  value: unknown
}

interface MatchResult {
  condition: MatchCondition
  actualValue: unknown
  matched: boolean
  reason?: string
}

interface TestResult {
  statusCode: number
  responseTime: number
  data: unknown
  isMocked: boolean
  request: {
    url: string
    method: string
    headers: Record<string, unknown>
    body: unknown
  }
}

// 匹配结果
const matchResults = ref<MatchResult[]>([])

// 测试结果
const testResult = ref<TestResult | null>(null)

// 测试模板
const testTemplates = ref<TestTemplate[]>([
  {
    name: '成功场景',
    data: {
      headers: { 'Content-Type': 'application/json' },
      body: { type: 'success', userId: 123 }
    }
  },
  {
    name: '错误场景',
    data: {
      headers: { 'Content-Type': 'application/json' },
      body: { type: 'error', userId: 456 }
    }
  },
  {
    name: '空数据',
    data: {
      headers: { 'Content-Type': 'application/json' },
      body: {}
    }
  }
])

// 监听器
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    initTestForm()
  }
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
  if (!newVal) {
    resetTest()
  }
})

// 方法
const initTestForm = () => {
  testForm.url = props.apiInfo.url
}

const resetTest = () => {
  matchResults.value = []
  testResult.value = null
  selectedTemplate.value = null
  testing.value = false
}

const handleClose = () => {
  visible.value = false
}

const applyTemplate = (template: TestTemplate) => {
  selectedTemplate.value = template
  testForm.headers = JSON.stringify(template.data.headers, null, 2)
  testForm.body = JSON.stringify(template.data.body, null, 2)
}

const checkMatch = (): void => {
  const mockData = props.mockData
  if (!mockData || !mockData.matchConditions) {
    ElMessage.warning('该Mock没有配置匹配条件')
    return
  }

  try {
    const requestData: { headers: Record<string, unknown>; body: unknown } = {
      headers: JSON.parse(testForm.headers) as Record<string, unknown>,
      body: JSON.parse(testForm.body) as unknown
    }

    matchResults.value = mockData.matchConditions.map((condition: MatchCondition) => {
      const actualValue = getValueByPath(requestData, condition.field)
      const matched = checkConditionMatch(condition, actualValue)

      return {
        condition,
        actualValue,
        matched,
        reason: matched ? '条件匹配成功' : '条件不匹配'
      } as MatchResult
    })
  } catch (error) {
    ElMessage.error('请求数据解析失败，请检查JSON格式')
  }
}

const getValueByPath = (obj: Record<string, unknown>, path: string): unknown => {
  const keys = path.split('.')
  let current: unknown = obj
  for (const key of keys) {
    if (typeof current === 'object' && current !== null && key in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[key]
    } else {
      return undefined
    }
  }
  return current
}

const checkConditionMatch = (condition: MatchCondition, actualValue: unknown): boolean => {
  const { operator, value } = condition

  switch (operator) {
    case 'equals':
      return actualValue === value
    case 'not_equals':
      return actualValue !== value
    case 'contains':
      return String(actualValue).includes(String(value))
    case 'not_contains':
      return !String(actualValue).includes(String(value))
    case 'greater_than':
      return Number(actualValue) > Number(value)
    case 'less_than':
      return Number(actualValue) < Number(value)
    case 'regex':
      try {
        return new RegExp(String(value)).test(String(actualValue))
      } catch {
        return false
      }
    default:
      return false
  }
}

const runTest = async (): Promise<void> => {
  testing.value = true

  try {
    const startTime = Date.now()

    // 检查是否匹配Mock条件
    checkMatch()
    const allMatched = matchResults.value.every(result => result.matched)

    let responseData: unknown
    let isMocked = false
    const mockData = props.mockData

    if (allMatched && mockData && mockData.enabled) {
      // 使用Mock数据
      responseData = mockData.responseData
      isMocked = true

      // 模拟延迟
      if (mockData.delay) {
        await new Promise(resolve => setTimeout(resolve, mockData.delay))
      }
    } else {
      // 调用真实接口（这里模拟）
      responseData = {
        code: 200,
        message: '真实接口响应',
        data: { realData: true }
      }
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    const endTime = Date.now()

    testResult.value = {
      statusCode: isMocked ? (mockData?.statusCode ?? 200) : 200,
      responseTime: endTime - startTime,
      data: responseData,
      isMocked,
      request: {
        url: testForm.url,
        method: props.apiInfo.method,
        headers: JSON.parse(testForm.headers) as Record<string, unknown>,
        body: JSON.parse(testForm.body) as unknown
      }
    }

    ElMessage.success('测试执行完成')
  } catch (error) {
    ElMessage.error('测试执行失败')
    console.error(error)
  } finally {
    testing.value = false
  }
}

const getStatusType = (statusCode: number) => {
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 400 && statusCode < 500) return 'warning'
  if (statusCode >= 500) return 'danger'
  return 'info'
}

const saveAsTestCase = () => {
  // TODO: 实现保存为API测试场景功能
  ElMessage.info('保存为API测试场景功能开发中...')
}
</script>

<style scoped>
.mock-test-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.mock-test {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mock-info,
.test-input,
.match-check,
.test-result {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.mock-info h3,
.test-input h3,
.match-check h3,
.test-result h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.templates {
  margin-bottom: 16px;
}

.template-preview {
  background: white;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.template-preview h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.template-preview pre {
  margin: 0;
  font-size: 12px;
  color: #303133;
}

.match-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.match-result .el-card {
  border: 1px solid #e4e7ed;
}

.match-result.match-success .el-card {
  border-color: #67c23a;
  background: #f0f9ff;
}

.match-result.match-failed .el-card {
  border-color: #f56c6c;
  background: #fef0f0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.result-content p {
  margin: 4px 0;
  font-size: 14px;
}

.result-display {
  background: white;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.response-info {
  margin-bottom: 16px;
}

.response-body h4,
.request-details h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.json-display {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  margin: 0;
}

.dialog-footer {
  text-align: right;
}
</style>

  {
    name: '成功场景',
    data: {
      headers: { 'Content-Type': 'application/json' },
      body: { type: 'success', userId: 123 }
    }
  },
  {
    name: '错误场景',
    data: {
      headers: { 'Content-Type': 'application/json' },
      body: { type: 'error', userId: 456 }
    }
  },
  {
    name: '空数据',
    data: {
      headers: { 'Content-Type': 'application/json' },
      body: {}
    }
  }
])