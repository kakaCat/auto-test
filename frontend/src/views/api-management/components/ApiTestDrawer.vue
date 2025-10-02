<template>
  <el-drawer>
    v-model="visible"
    :title="drawerTitle"
    :size="isFullscreen ? '100%' : '80%'"
    direction="rtl"
    :before-close="handleClose"
    class="api-test-drawer"
    <!-- 工具栏 -->
    <div class="test-toolbar">
      <div class="toolbar-left">
        <el-button-group size="small">
          <el-button @click="toggleFullscreen">
            <el-icon><FullScreen v-if="!isFullscreen" /><Aim v-else /></el-icon>
            {{ isFullscreen ? '退出全屏' : '全屏模式' }}
          </el-button>
          <el-button @click="saveTestCase" :disabled="!hasValidRequest">
            <el-icon><FolderAdd /></el-icon>
            保存用例
          </el-button>
          <el-button @click="loadTestCase">
            <el-icon><Folder /></el-icon>
            加载用例
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <el-select v-model="currentEnvironment" size="small" style="width: 120px">
          <el-option label="开发环境" value="development" />
          <el-option label="测试环境" value="testing" />
          <el-option label="预发布" value="staging" />
        </el-select>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="test-content">
      <!-- 左侧：请求配置 -->
      <div class="request-panel">
        <el-card shadow="never" class="config-card">
          <template #header>
            <div class="card-header">
              <span>请求配置</span>
              <el-button size="small" @click="resetRequest">
                <el-icon><RefreshRight /></el-icon>
                重置
              </el-button>
            </div>
          </template>

          <!-- 基本信息 -->
          <div class="request-basic">
            <el-row :gutter="12">
              <el-col :span="6">
                <el-select v-model="requestConfig.method" placeholder="请求方法" size="small">
                  <el-option
                    v-for="method in httpMethods"
                    :key="method.value"
                    :label="method.label"
                    :value="method.value"
                  >
                    <el-tag :type="method.type" size="small">{{ method.label }}</el-tag>
                  </el-option>
                </el-select>
              </el-col>
              <el-col :span="18">
                <el-input v-model="requestConfig.url" placeholder="请求URL" size="small">
                  <template #prepend><span>{{ baseUrl }}</span></template>
                </el-input>
              </el-col>
            </el-row>
          </div>

          <!-- 认证配置 -->
          <div class="auth-config">
            <el-collapse v-model="activeAuthPanel">
              <el-collapse-item title="认证配置" name="auth">
                <el-radio-group v-model="authConfig.type">
                  <el-radio label="none">无认证</el-radio>
                  <el-radio label="bearer">Bearer Token</el-radio>
                  <el-radio label="basic">Basic Auth</el-radio>
                  <el-radio label="apikey">API Key</el-radio>
                </el-radio-group>

                <div v-if="authConfig.type === 'bearer'" class="auth-form">
                  <el-input v-model="authConfig.token" placeholder="请输入Bearer Token" type="textarea" :rows="2" />
                </div>

                <div v-if="authConfig.type === 'basic'" class="auth-form">
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-input v-model="authConfig.username" placeholder="用户名" />
                    </el-col>
                    <el-col :span="12">
                      <el-input v-model="authConfig.password" placeholder="密码" type="password" />
                    </el-col>
                  </el-row>
                </div>

                <div v-if="authConfig.type === 'apikey'" class="auth-form">
                  <el-row :gutter="12">
                    <el-col :span="8">
                      <el-input v-model="authConfig.keyName" placeholder="Key名称" />
                    </el-col>
                    <el-col :span="8">
                      <el-input v-model="authConfig.keyValue" placeholder="Key值" />
                    </el-col>
                    <el-col :span="8">
                      <el-select v-model="authConfig.keyLocation" placeholder="位置">
                        <el-option label="Header" value="header" />
                        <el-option label="Query" value="query" />
                      </el-select>
                    </el-col>
                  </el-row>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- 请求参数配置 -->
          <div class="params-config">
            <el-tabs v-model="activeParamTab" @tab-click="handleParamTabClick">
              <!-- Headers -->
              <el-tab-pane label="Headers" name="headers">
                <KeyValueEditor
                  v-model="requestConfig.headers"
                  placeholder-key="Header名称"
                  placeholder-value="Header值"
                  :presets="headerPresets"
                />
              </el-tab-pane>

              <!-- Query参数 -->
              <el-tab-pane label="Query" name="query">
                <KeyValueEditor
                  v-model="requestConfig.query"
                  placeholder-key="参数名"
                  placeholder-value="参数值"
                />
              </el-tab-pane>

              <!-- Body -->
              <el-tab-pane label="Body" name="body">
                <div class="body-config">
                  <el-radio-group v-model="requestConfig.bodyType" @change="handleBodyTypeChange">
                    <el-radio label="none">无Body</el-radio>
                    <el-radio label="json">JSON</el-radio>
                    <el-radio label="form">Form Data</el-radio>
                    <el-radio label="raw">Raw</el-radio>
                  </el-radio-group>

                  <div v-if="requestConfig.bodyType === 'json'" class="body-editor">
                    <div class="editor-toolbar">
                      <el-button size="small" @click="formatJson">
                        <el-icon><MagicStick /></el-icon>
                        格式化
                      </el-button>
                      <el-button size="small" @click="generateMockData">
                        <el-icon><DataBoard /></el-icon>
                        生成Mock数据
                      </el-button>
                    </div>
                    <el-input
                      v-model="requestConfig.body"
                      type="textarea"
                      :rows="8"
                      placeholder="请输入JSON数据"
                    />
                  </div>

                  <div v-if="requestConfig.bodyType === 'form'" class="body-editor">
                    <KeyValueEditor
                      v-model="requestConfig.formData"
                      placeholder-key="字段名"
                      placeholder-value="字段值"
                      :support-file="true"
                    />
                  </div>

                  <div v-if="requestConfig.bodyType === 'raw'" class="body-editor">
                    <el-select v-model="requestConfig.rawType" size="small" style="margin-bottom: 8px">
                      <el-option label="Text" value="text" />
                      <el-option label="XML" value="xml" />
                      <el-option label="HTML" value="html" />
                    </el-select>
                    <el-input v-model="requestConfig.body" type="textarea" :rows="8" placeholder="请输入原始数据" />
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 发送按钮 -->
          <div class="send-section">
            <el-button type="primary" size="large" @click="sendRequest" :loading="isRequesting" :disabled="!hasValidRequest">
              <el-icon><VideoPlay /></el-icon>
              {{ isRequesting ? '请求中...' : '发送请求' }}
            </el-button>
            
            <div class="send-options">
              <el-checkbox v-model="requestOptions.followRedirects">跟随重定向</el-checkbox>
              <div class="timeout-setting">
                <el-input-number v-model="requestOptions.timeout" :min="1" :max="300" size="small" style="width: 100px" />
                <span>秒超时</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：响应结果 -->
      <div class="response-panel">
        <el-card shadow="never" class="result-card">
          <template #header>
            <div class="card-header">
              <span>响应结果</span>
              <div class="response-actions">
                <el-button v-if="responseData" size="small" @click="copyResponse">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button v-if="responseData" size="small" @click="saveResponse">
                  <el-icon><Download /></el-icon>
                  保存
                </el-button>
                <el-button v-if="responseData" size="small" @click="analyzeResponse">
                  <el-icon><DataAnalysis /></el-icon>
                  分析
                </el-button>
              </div>
            </div>
          </template>

          <!-- 响应状态 -->
          <div v-if="responseData" class="response-status">
            <div class="status-line">
              <el-tag>
                :type="getStatusType(responseData.status)"
                size="large"
                effect="dark"
                {{ responseData.status }} {{ responseData.statusText }}
              </el-tag>
              <span class="response-time">{{ responseData.time }}ms</span>
              <span class="response-size">{{ formatSize(responseData.size) }}</span>
              <span class="response-timestamp">{{ formatTime(responseData.timestamp) }}</span>
            </div>
          </div>

          <!-- 响应内容 -->
          <div v-if="responseData" class="response-content">
            <el-tabs v-model="activeResponseTab">
              <!-- 响应体 -->
              <el-tab-pane label="Response Body" name="body">
                <div class="response-body">
                  <div class="body-toolbar">
                    <el-button-group size="small">
                      <el-button @click="formatResponseBody">
                        <el-icon><MagicStick /></el-icon>
                        格式化
                      </el-button>
                      <el-button @click="toggleResponseWrap">
                        <el-icon><Sort /></el-icon>
                        {{ responseWrap ? '取消换行' : '自动换行' }}
                      </el-button>
                    </el-button-group>
                  </div>
                  <pre :class="['response-text', { 'wrap-text': responseWrap }]" v-html="highlightedResponse"></pre>
                </div>
              </el-tab-pane>

              <!-- 响应头 -->
              <el-tab-pane label="Headers" name="headers">
                <div class="response-headers">
                  <div>
                    v-for="(value, key) in responseData.headers"
                    :key="key"
                    class="header-item"
                    <span class="header-key">{{ key }}:</span>
                    <span class="header-value">{{ value }}</span>
                  </div>
                </div>
              </el-tab-pane>

              <!-- Cookies -->
              <el-tab-pane label="Cookies" name="cookies">
                <div class="response-cookies">
                  <div>
                    v-for="cookie in responseData.cookies"
                    :key="cookie.name"
                    class="cookie-item"
                    <el-descriptions :column="1" size="small">
                      <el-descriptions-item label="Name">{{ cookie.name }}</el-descriptions-item>
                      <el-descriptions-item label="Value">{{ cookie.value }}</el-descriptions-item>
                      <el-descriptions-item label="Domain">{{ cookie.domain }}</el-descriptions-item>
                      <el-descriptions-item label="Path">{{ cookie.path }}</el-descriptions-item>
                    </el-descriptions>
                  </div>
                </div>
              </el-tab-pane>

              <!-- 测试结果 -->
              <el-tab-pane label="Tests" name="tests">
                <div class="test-results">
                  <div v-for="test in testResults" :key="test.name" class="test-item">
                    <el-icon v-if="test.passed" class="test-icon success"><CircleCheck /></el-icon>
                    <el-icon v-else class="test-icon error"><CircleClose /></el-icon>
                    <span class="test-name">{{ test.name }}</span>
                    <span class="test-message">{{ test.message }}</span>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-response">
            <el-empty description="暂无响应数据">
              <template #image>
                <el-icon size="64" color="#c0c4cc"><DataBoard /></el-icon>
              </template>
            </el-empty>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 底部：测试用例管理 -->
    <div class="test-cases-panel">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>API测试场景</span>
            <el-button size="small" @click="showTestCaseDialog = true">
              <el-icon><Plus /></el-icon>
              新建场景
            </el-button>
          </div>
        </template>

        <div class="test-cases-list">
          <div>
            v-for="testCase in testCases"
            :key="testCase.id"
            :class="['test-case-item', { active: currentTestCase?.id === testCase.id }]"
            @click="loadTestCaseData(testCase)"
            <div class="case-info">
              <span class="case-name">{{ testCase.name }}</span>
              <span class="case-method">{{ testCase.method }}</span>
            </div>
            <div class="case-actions">
              <el-button size="small" text @click.stop="editTestCase(testCase)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" text type="danger" @click.stop="deleteTestCase(testCase)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 测试用例对话框 -->
    <el-dialog>
      v-model="showTestCaseDialog"
      title="保存API测试场景"
      width="500px"
      <el-form :model="testCaseForm" label-width="80px">
        <el-form-item label="场景名称" required>
          <el-input v-model="testCaseForm.name" placeholder="请输入场景名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="testCaseForm.description" type="textarea" :rows="3" placeholder="请输入场景描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showTestCaseDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTestCaseData">保存</el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  FullScreen, Aim, FolderAdd, Folder, RefreshRight, VideoPlay,
  CopyDocument, Download, DataAnalysis, MagicStick, DataBoard,
  Sort, CircleCheck, CircleClose, Plus, Edit, Delete
} from '@element-plus/icons-vue'
import KeyValueEditor from './KeyValueEditor.vue'
import unifiedApi from '@/api/unified-api'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  apiData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'test-complete'])

// 响应式数据
const visible = ref(false)
const isFullscreen = ref(false)
const isRequesting = ref(false)
const currentEnvironment = ref('development')
const activeAuthPanel = ref([])
const activeParamTab = ref('headers')
const activeResponseTab = ref('body')
const responseWrap = ref(false)
const showTestCaseDialog = ref(false)

// 请求配置
const requestConfig = reactive({
  method: 'GET',
  url: '',
  headers: [],
  query: [],
  bodyType: 'none',
  body: '',
  formData: [],
  rawType: 'text'
})

// 认证配置
const authConfig = reactive({
  type: 'none',
  token: '',
  username: '',
  password: '',
  keyName: '',
  keyValue: '',
  keyLocation: 'header'
})

// 请求选项
const requestOptions = reactive({
  followRedirects: true,
  timeout: 30
})

// 响应数据
const responseData = ref(null)
const testResults = ref([])

// 测试用例
const testCases = ref([])
const currentTestCase = ref(null)
const testCaseForm = reactive({
  name: '',
  description: ''
})

// HTTP方法选项
const httpMethods = [
  { label: 'GET', value: 'GET', type: 'success' },
  { label: 'POST', value: 'POST', type: 'primary' },
  { label: 'PUT', value: 'PUT', type: 'warning' },
  { label: 'DELETE', value: 'DELETE', type: 'danger' },
  { label: 'PATCH', value: 'PATCH', type: 'info' },
  { label: 'HEAD', value: 'HEAD', type: '' },
  { label: 'OPTIONS', value: 'OPTIONS', type: '' }
]

// Header预设
const headerPresets = [
  { key: 'Content-Type', value: 'application/json' },
  { key: 'Accept', value: 'application/json' },
  { key: 'User-Agent', value: 'API-Test-Client/1.0' },
  { key: 'Authorization', value: 'Bearer ' }
]

// 计算属性
const drawerTitle = computed(() => {
  return props.apiData.name ? `API测试 - ${props.apiData.name}` : 'API测试'
})

const baseUrl = computed(() => {
  return import.meta.env?.VITE_UNIFIED_API_BASE_URL || 'http://127.0.0.1:8000'
})
 
const hasValidRequest = computed(() => {
  return requestConfig.url.trim() !== ''
})

const highlightedResponse = computed(() => {
  if (!responseData.value?.body) return ''
  
  try {
    const parsed = JSON.parse(responseData.value.body)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return responseData.value.body
  }
})

// 监听器
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
  if (newValue && props.apiData) {
    initializeFromApiData()
  }
})

watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 方法
const initializeFromApiData = () => {
  if (props.apiData) {
    requestConfig.method = props.apiData.method || 'GET'
    requestConfig.url = props.apiData.path || props.apiData.url || ''
    
    // 根据API定义生成默认参数
    if (props.apiData.parameters) {
      generateDefaultParams()
    }
    
    // 设置认证
    if (props.apiData.auth_required) {
      authConfig.type = 'bearer'
    }
  }
}

const generateDefaultParams = () => {
  // 根据API参数定义生成默认的测试数据
  // 这里可以实现智能参数生成逻辑
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handleClose = () => {
  visible.value = false
}

const resetRequest = () => {
  Object.assign(requestConfig, {
    method: props.apiData.method || 'GET',
    url: props.apiData.path || '',
    headers: [],
    query: [],
    bodyType: 'none',
    body: '',
    formData: [],
    rawType: 'text'
  })
  
  Object.assign(authConfig, {
    type: 'none',
    token: '',
    username: '',
    password: '',
    keyName: '',
    keyValue: '',
    keyLocation: 'header'
  })
}

const handleParamTabClick = (tab) => {
  activeParamTab.value = tab.name
}

const handleBodyTypeChange = () => {
  requestConfig.body = ''
  requestConfig.formData = []
}

const formatJson = () => {
  try {
    const parsed = JSON.parse(requestConfig.body)
    requestConfig.body = JSON.stringify(parsed, null, 2)
    ElMessage.success('JSON格式化成功')
  } catch (error) {
    ElMessage.error('JSON格式错误')
  }
}

const generateMockData = () => {
  // 根据API定义生成Mock数据
  const mockData = {
    name: 'test_user',
    email: 'test@example.com',
    age: 25,
    active: true
  }
  requestConfig.body = JSON.stringify(mockData, null, 2)
  ElMessage.success('Mock数据生成成功')
}

const sendRequest = async () => {
  if (!hasValidRequest.value) {
    ElMessage.warning('请配置有效的请求URL')
    return
  }
  
  isRequesting.value = true
  
  try {
    // 构建请求配置
    const config = buildRequestConfig()
    
    // 发送请求到后端草稿测试接口
    const resp = await unifiedApi.apiManagementApi.testApiDraft(config)

    if (resp && resp.success) {
      const data = resp.data || {}
      const mapped = convertToViewResponse(data.response)
      responseData.value = mapped

      // 如果后端返回了校验结果，则优先展示
      if (data.validation && Array.isArray(data.validation.results)) {
        testResults.value = data.validation.results.map((r) => ({
          name: (r.rule && r.rule.type) ? `规则: ${r.rule.type}` : '规则校验',
          passed: !!r.passed,
          message: r.message || ''
        }))
      } else {
        // 否则运行内置的基础测试
        runTests(mapped)
      }

      ElMessage.success('请求发送成功')
    } else {
      ElMessage.error((resp && resp.message) ? resp.message : '请求失败')
    }
  } catch (error) {
    ElMessage.error('请求失败: ' + error.message)
  } finally {
    isRequesting.value = false
  }
}

const buildRequestConfig = () => {
  const config = {
    method: requestConfig.method,
    url: baseUrl.value + requestConfig.url,
    headers: {},
    timeout: requestOptions.timeout
  }
  
  // 处理Headers
  requestConfig.headers.forEach(header => {
    if (header.key && header.value) {
      config.headers[header.key] = header.value
    }
  })
  
  // 处理认证
  if (authConfig.type === 'bearer' && authConfig.token) {
    config.headers['Authorization'] = `Bearer ${authConfig.token}`
  } else if (authConfig.type === 'basic' && authConfig.username) {
    const credentials = btoa(`${authConfig.username}:${authConfig.password}`)
    config.headers['Authorization'] = `Basic ${credentials}`
  } else if (authConfig.type === 'apikey' && authConfig.keyName) {
    if (authConfig.keyLocation === 'header') {
      config.headers[authConfig.keyName] = authConfig.keyValue
    } else {
      config.params = config.params || {}
      config.params[authConfig.keyName] = authConfig.keyValue
    }
  }
  
  // 处理Query参数
  if (requestConfig.query.length > 0) {
    config.params = config.params || {}
    requestConfig.query.forEach(param => {
      if (param.key && param.value) {
        config.params[param.key] = param.value
      }
    })
  }
  
  // 处理Body
  if (requestConfig.bodyType === 'json' && requestConfig.body) {
    config.headers['Content-Type'] = 'application/json'
    try {
      config.body = JSON.parse(requestConfig.body)
    } catch (e) {
      // 保留原始字符串，后端将按text处理
      config.body = requestConfig.body
    }
  } else if (requestConfig.bodyType === 'form' && requestConfig.formData.length > 0) {
    const formData = new FormData()
    requestConfig.formData.forEach(item => {
      if (item.key && item.value) {
        formData.append(item.key, item.value)
      }
    })
    config.body = formData
  } else if (requestConfig.bodyType === 'raw' && requestConfig.body) {
    config.body = requestConfig.body
  }
  
  return config
}

// 将后端响应结构转换为视图模型
const convertToViewResponse = (resp) => {
  if (!resp) return null
  const body = resp.body
  let bodyText = ''
  try {
    if (typeof body === 'string') {
      bodyText = body
    } else if (body !== null && body !== undefined) {
      bodyText = JSON.stringify(body, null, 2)
    } else {
      bodyText = ''
    }
  } catch (e) {
    bodyText = String(body)
  }

  return {
    status: resp.status_code,
    statusText: resp.status_text || '',
    headers: resp.headers || {},
    body: bodyText,
    time: resp.response_time_ms || 0,
    size: resp.content_length || 0,
    timestamp: Date.now(),
    cookies: []
  }
}

const runTests = (response) => {
  const tests = []
  
  // 状态码测试
  tests.push({
    name: '状态码检查',
    passed: response.status >= 200 && response.status < 300,
    message: `期望2xx，实际${response.status}`
  })
  
  // 响应时间测试
  tests.push({
    name: '响应时间检查',
    passed: response.time < 2000,
    message: `响应时间${response.time}ms`
  })
  
  // JSON格式测试
  try {
    JSON.parse(response.body)
    tests.push({
      name: 'JSON格式检查',
      passed: true,
      message: '响应为有效JSON格式'
    })
  } catch {
    tests.push({
      name: 'JSON格式检查',
      passed: false,
      message: '响应不是有效JSON格式'
    })
  }
  
  testResults.value = tests
}

const getStatusType = (status) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'warning'
  if (status >= 400 && status < 500) return 'danger'
  if (status >= 500) return 'danger'
  return 'info'
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const formatResponseBody = () => {
  if (responseData.value?.body) {
    try {
      const parsed = JSON.parse(responseData.value.body)
      responseData.value.body = JSON.stringify(parsed, null, 2)
      ElMessage.success('响应格式化成功')
    } catch {
      ElMessage.warning('响应不是有效的JSON格式')
    }
  }
}

const toggleResponseWrap = () => {
  responseWrap.value = !responseWrap.value
}

const copyResponse = () => {
  if (responseData.value?.body) {
    navigator.clipboard.writeText(responseData.value.body)
    ElMessage.success('响应内容已复制到剪贴板')
  }
}

const saveResponse = () => {
  if (responseData.value?.body) {
    const blob = new Blob([responseData.value.body], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `api-response-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('响应已保存到文件')
  }
}

const analyzeResponse = () => {
  ElMessage.info('响应分析功能开发中...')
}

const saveTestCase = () => {
  testCaseForm.name = `${requestConfig.method} ${requestConfig.url}`
  testCaseForm.description = ''
  showTestCaseDialog.value = true
}

const saveTestCaseData = () => {
  if (!testCaseForm.name.trim()) {
    ElMessage.warning('请输入场景名称')
    return
  }
  
  const testCase = {
    id: Date.now(),
    name: testCaseForm.name,
    description: testCaseForm.description,
    method: requestConfig.method,
    config: JSON.parse(JSON.stringify(requestConfig)),
    auth: JSON.parse(JSON.stringify(authConfig)),
    options: JSON.parse(JSON.stringify(requestOptions)),
    createdAt: new Date().toISOString()
  }
  
  testCases.value.push(testCase)
  showTestCaseDialog.value = false
  
  // 保存到本地存储
  localStorage.setItem('api-test-cases', JSON.stringify(testCases.value))
  
  ElMessage.success('API测试场景保存成功')
}

const loadTestCase = () => {
  // 从本地存储加载测试用例
  const saved = localStorage.getItem('api-test-cases')
  if (saved) {
    try {
      testCases.value = JSON.parse(saved)
      ElMessage.success('API测试场景加载成功')
    } catch {
      ElMessage.error('API测试场景数据格式错误')
    }
  } else {
    ElMessage.info('暂无保存的API测试场景')
  }
}

const loadTestCaseData = (testCase) => {
  currentTestCase.value = testCase
  Object.assign(requestConfig, testCase.config)
  Object.assign(authConfig, testCase.auth)
  Object.assign(requestOptions, testCase.options)
  ElMessage.success(`已加载API测试场景: ${testCase.name}`)
}

const editTestCase = (testCase) => {
  testCaseForm.name = testCase.name
  testCaseForm.description = testCase.description
  showTestCaseDialog.value = true
}

const deleteTestCase = async (testCase) => {
  try {
    await ElMessageBox.confirm(
      `确认删除API测试场景 "${testCase.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = testCases.value.findIndex(tc => tc.id === testCase.id)
    if (index > -1) {
      testCases.value.splice(index, 1)
      localStorage.setItem('api-test-cases', JSON.stringify(testCases.value))
      ElMessage.success('API测试场景删除成功')
    }
  } catch {
    // 用户取消
  }
}

// 暴露方法
defineExpose({
  sendRequest,
  resetRequest,
  saveTestCase
})
</script>

<style scoped>
.api-test-drawer {
  --el-drawer-padding-primary: 0;
}

.test-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.test-content {
  display: flex;
  height: calc(100vh - 200px);
  gap: 16px;
  padding: 20px;
}

.request-panel {
  flex: 1;
  min-width: 400px;
}

.response-panel {
  flex: 1;
  min-width: 400px;
}

.config-card,
.result-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.request-basic {
  margin-bottom: 16px;
}

.auth-config {
  margin-bottom: 16px;
}

.auth-form {
  margin-top: 12px;
}

.params-config {
  margin-bottom: 16px;
}

.body-config {
  margin-top: 12px;
}

.body-editor {
  margin-top: 12px;
}

.editor-toolbar {
  margin-bottom: 8px;
}

.send-section {
  text-align: center;
  padding: 20px 0;
  border-top: 1px solid #f0f2f5;
}

.send-options {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 12px;
  color: #606266;
}

.response-status {
  margin-bottom: 16px;
}

.status-line {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.response-time,
.response-size,
.response-timestamp {
  font-size: 12px;
  color: #606266;
}

.response-content {
  flex: 1;
  overflow: hidden;
}

.response-body {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.body-toolbar {
  margin-bottom: 8px;
}

.response-text {
  flex: 1;
  overflow: auto;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre;
}

.response-text.wrap-text {
  white-space: pre-wrap;
}

.response-headers {
  max-height: 400px;
  overflow-y: auto;
}

.header-item {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.header-key {
  font-weight: 600;
  color: #303133;
  min-width: 150px;
}

.header-value {
  color: #606266;
  word-break: break-all;
}

.response-cookies {
  max-height: 400px;
  overflow-y: auto;
}

.cookie-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.test-results {
  max-height: 400px;
  overflow-y: auto;
}

.test-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.test-icon.success {
  color: #67c23a;
}

.test-icon.error {
  color: #f56c6c;
}

.test-name {
  font-weight: 600;
  color: #303133;
}

.test-message {
  color: #606266;
  font-size: 12px;
}

.empty-response {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.test-cases-panel {
  padding: 0 20px 20px;
}

.test-cases-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.test-case-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 200px;
}

.test-case-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.test-case-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.case-info {
  flex: 1;
}

.case-name {
  display: block;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.case-method {
  font-size: 12px;
  color: #606266;
}

.case-actions {
  display: flex;
  gap: 4px;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-drawer__body) {
  padding: 0;
}

:deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

:deep(.el-tab-pane) {
  height: 100%;
  overflow: auto;
}
</style>