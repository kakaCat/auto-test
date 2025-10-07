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
            <el-form-item
              label="场景名称"
              prop="name"
            >
              <el-input
                v-model="formData.name"
                placeholder="请输入API测试场景名称"
              />
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
            <el-form-item
              label="请求方法"
              prop="requestConfig.method"
            >
              <el-select
                v-model="formData.requestConfig.method"
                style="width: 100%"
                disabled
              >
                <el-option
                  label="GET"
                  value="GET"
                />
                <el-option
                  label="POST"
                  value="POST"
                />
                <el-option
                  label="PUT"
                  value="PUT"
                />
                <el-option
                  label="DELETE"
                  value="DELETE"
                />
                <el-option
                  label="PATCH"
                  value="PATCH"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item
              label="请求URL"
              prop="requestConfig.url"
            >
              <el-input
                v-model="formData.requestConfig.url"
                placeholder="请求URL由API定义"
                disabled
              >
                <template #prepend>
                  <span class="base-url-prepend">{{ baseUrl }}</span>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 请求头 -->
        <el-form-item label="请求头">
          <div
            class="key-value-editor"
            style="opacity: 0.6; pointer-events: none;"
          >
            <div
              v-for="(header, index) in headersList"
              :key="index"
              class="key-value-row"
            >
              <el-input
                v-model="header.key"
                placeholder="Header名称"
                style="width: 40%"
                disabled
                @input="updateHeaders"
              />
              <el-input
                v-model="header.value"
                placeholder="Header值"
                style="width: 40%; margin-left: 10px"
                disabled
                @input="updateHeaders"
              />
              <el-button
                type="danger"
                size="small"
                style="margin-left: 10px"
                disabled
                @click="removeHeader(index)"
              >
                删除
              </el-button>
            </div>
            <el-button
              type="primary"
              size="small"
              disabled
              @click="addHeader"
            >
              添加Header
            </el-button>
          </div>
        </el-form-item>

        <!-- 请求参数面板：四表格（Query / JSON Body / Form Body / Path） -->
        <el-form-item label="请求参数">
          <el-tabs v-model="activeParamsTab">
            <el-tab-pane
              label="Query"
              name="query"
            >
              <div class="key-value-editor">
                <div
                  v-for="(param, index) in queryParamsList"
                  :key="`q-${index}`"
                  class="key-value-row"
                >
                  <el-input
                    v-model="param.key"
                    placeholder="参数名"
                    style="flex: 1"
                  />
                  <el-input
                    v-model="param.value"
                    placeholder="参数值"
                    style="flex: 1"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeQueryParam(index)"
                  >
                    删除
                  </el-button>
                </div>
                <div style="display:flex;align-items:center;gap:12px;margin-top:8px;">
                  <el-button
                    type="primary"
                    size="small"
                    @click="addQueryParam"
                  >
                    添加参数
                  </el-button>
                  <el-checkbox v-model="showQueryJson">
                    JSON模式
                  </el-checkbox>
                </div>
                <el-input
                  v-if="showQueryJson"
                  v-model="queryJson"
                  type="textarea"
                  :rows="4"
                  placeholder="JSON对象，如: { key: value }"
                  @change="applyQueryJson"
                />
                <el-button
                  size="small"
                  style="margin-top:8px"
                  @click="parseUrlToQueryAndPath"
                >
                  从URL解析
                </el-button>
              </div>
            </el-tab-pane>
            <el-tab-pane
              label="JSON Body"
              name="json"
            >
              <div class="key-value-editor">
                <div
                  v-for="(param, index) in jsonBodyList"
                  :key="`j-${index}`"
                  class="key-value-row"
                >
                  <el-input
                    v-model="param.key"
                    placeholder="字段名"
                    style="flex: 1"
                  />
                  <el-input
                    v-model="param.value"
                    placeholder="字段值"
                    style="flex: 1"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeJsonBodyParam(index)"
                  >
                    删除
                  </el-button>
                </div>
                <div style="display:flex;align-items:center;gap:12px;margin-top:8px;">
                  <el-button
                    type="primary"
                    size="small"
                    @click="addJsonBodyParam"
                  >
                    添加字段
                  </el-button>
                  <el-checkbox v-model="showJsonBodyJson">
                    JSON模式
                  </el-checkbox>
                </div>
                <el-input
                  v-if="showJsonBodyJson"
                  v-model="jsonBodyJson"
                  type="textarea"
                  :rows="6"
                  placeholder="JSON对象"
                  @change="applyJsonBodyJson"
                />
              </div>
            </el-tab-pane>
            <el-tab-pane
              label="Form Body"
              name="form"
            >
              <div class="key-value-editor">
                <div
                  v-for="(param, index) in formBodyList"
                  :key="`f-${index}`"
                  class="key-value-row"
                >
                  <el-input
                    v-model="param.key"
                    placeholder="字段名"
                    style="flex: 1"
                  />
                  <el-input
                    v-model="param.value"
                    placeholder="字段值"
                    style="flex: 1"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeFormBodyParam(index)"
                  >
                    删除
                  </el-button>
                </div>
                <div style="display:flex;align-items:center;gap:12px;margin-top:8px;">
                  <el-button
                    type="primary"
                    size="small"
                    @click="addFormBodyParam"
                  >
                    添加字段
                  </el-button>
                  <el-checkbox v-model="showFormBodyJson">
                    JSON模式
                  </el-checkbox>
                </div>
                <el-input
                  v-if="showFormBodyJson"
                  v-model="formBodyJson"
                  type="textarea"
                  :rows="6"
                  placeholder="JSON对象（将按表单键值对处理）"
                  @change="applyFormBodyJson"
                />
              </div>
            </el-tab-pane>
            <el-tab-pane
              label="Path"
              name="path"
            >
              <div class="key-value-editor">
                <div
                  v-for="(param, index) in pathParamsList"
                  :key="`p-${index}`"
                  class="key-value-row"
                >
                  <el-input
                    v-model="param.key"
                    placeholder="路径占位符名"
                    style="flex: 1"
                  />
                  <el-input
                    v-model="param.value"
                    placeholder="替换值"
                    style="flex: 1"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removePathParam(index)"
                  >
                    删除
                  </el-button>
                </div>
                <div style="display:flex;align-items:center;gap:12px;margin-top:8px;">
                  <el-button
                    type="primary"
                    size="small"
                    @click="addPathParam"
                  >
                    添加占位符
                  </el-button>
                  <el-checkbox v-model="showPathJson">
                    JSON模式
                  </el-checkbox>
                </div>
                <el-input
                  v-if="showPathJson"
                  v-model="pathJson"
                  type="textarea"
                  :rows="4"
                  placeholder="JSON对象，如: { id: 123 }"
                  @change="applyPathJson"
                />
                <el-button
                  size="small"
                  style="margin-top:8px"
                  @click="parseUrlToQueryAndPath"
                >
                  从URL识别占位符
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>

          <div
            v-if="jsonBodyList.length > 0 && formBodyList.length > 0"
            style="margin-top: 10px;"
          >
            <el-alert
              type="warning"
              title="JSON与Form同时存在，请选择请求体类型"
              show-icon
            />
            <el-radio-group
              v-model="selectedBodyScope"
              style="margin-top: 8px;"
            >
              <el-radio label="json">
                使用JSON作为请求体
              </el-radio>
              <el-radio label="form">
                使用Form作为请求体
              </el-radio>
            </el-radio-group>
          </div>
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
        
        <el-row
          :gutter="20"
          style="opacity: 0.6; pointer-events: none;"
        >
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
        <el-button @click="handleClose">
          取消
        </el-button>
        <el-button
          type="primary"
          @click="handleSave"
        >
          保存
        </el-button>
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
import apiManagementApi from '@/api/api-management'
import { ParamsConverter } from '@/utils/paramsConverter'
import SchemaConverter from '@/utils/schemaConversion'
import { useServiceStore } from '@/stores/service'

interface ApiItem { id?: string | number; name?: string; method?: string; url?: string; path?: string; system_id?: string | number }

// 基于系统列表计算baseUrl
const serviceStore = useServiceStore()
const systemId = ref<string>('')
const systems = computed<Array<Record<string, unknown>>>(() => {
  const listUnknown = (serviceStore as unknown as { systemsList?: unknown }).systemsList
  const valueField = listUnknown && typeof listUnknown === 'object' && 'value' in (listUnknown as { value?: unknown })
    ? (listUnknown as { value?: unknown }).value
    : listUnknown
  return Array.isArray(valueField) ? (valueField as Array<Record<string, unknown>>) : []
})

const baseUrl = computed<string>(() => {
  const sid = systemId.value || (typeof props.apiInfo?.system_id !== 'undefined' ? String(props.apiInfo.system_id as string | number) : '')
  if (!sid) return ''
  const sys = systems.value.find((s) => String(((s as Record<string, unknown>).id as string | number)) === sid)
  const rawUnknown = sys ? (((sys as Record<string, unknown>).url) ?? ((sys as Record<string, unknown>).baseUrl)) : ''
  const raw = typeof rawUnknown === 'string' ? rawUnknown : ''
  return raw.replace(/\/+$/, '')
})

const toFullUrl = (url: string): string => {
  const input = url || ''
  if (/^https?:\/\//i.test(input)) return input
  const base = baseUrl.value
  if (!base) return input
  const path = input.startsWith('/') ? input : `/${input}`
  return `${base}${path}`
}

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

// 四表格参数面板：状态与工具
const activeParamsTab = ref<'query' | 'json' | 'form' | 'path'>('query')
interface KVItem { key: string; value: string }
const queryParamsList = ref<KVItem[]>([])
const jsonBodyList = ref<KVItem[]>([])
const formBodyList = ref<KVItem[]>([])
const pathParamsList = ref<KVItem[]>([])

// JSON模式开关与字符串
const showQueryJson = ref(false)
const showJsonBodyJson = ref(false)
const showFormBodyJson = ref(false)
const showPathJson = ref(false)
const queryJson = ref('')
const jsonBodyJson = ref('')
const formBodyJson = ref('')
const pathJson = ref('')

// 选择体类型（两者同时存在时提示选择）
const selectedBodyScope = ref<'json' | 'form'>('json')

// 工具：数组->对象
const toObject = (list: KVItem[]): Record<string, unknown> => {
  const obj: Record<string, unknown> = {}
  list.forEach(({ key, value }) => {
    if (key) obj[key] = value
  })
  return obj
}

// 工具：对象->数组
const toList = (obj: Record<string, unknown> | null | undefined): KVItem[] => {
  const list: KVItem[] = []
  if (obj && typeof obj === 'object') {
    Object.entries(obj).forEach(([k, v]) => list.push({ key: k, value: String(v) }))
  }
  return list
}

// URL解析：填充Query与Path
const parseUrlToQueryAndPath = (): void => {
  const raw = formData.value.requestConfig.url || ''
  try {
    const full = toFullUrl(raw)
    const u = /^https?:\/\//i.test(full) ? new URL(full) : new URL(full, 'http://localhost')
    const qList: KVItem[] = []
    u.searchParams.forEach((v, k) => qList.push({ key: k, value: v }))
    queryParamsList.value = qList
    queryJson.value = JSON.stringify(toObject(qList), null, 2)
  } catch {
    const [path, qs] = raw.split('?')
    const qList: KVItem[] = []
    if (qs) {
      qs.split('&').forEach(pair => {
        const [k, v] = pair.split('=')
        if (k) qList.push({ key: decodeURIComponent(k), value: decodeURIComponent(v || '') })
      })
    }
    queryParamsList.value = qList
    queryJson.value = JSON.stringify(toObject(qList), null, 2)
  }
  // 识别Path占位符 {id} 或 :id
  const pathSeg = raw.split('?')[0]
  const names = new Set<string>()
  ;(pathSeg.match(/\{([a-zA-Z0-9_]+)\}/g) || []).forEach(m => {
    const n = m.replace(/[{}]/g, '')
    if (n) names.add(n)
  })
  ;(pathSeg.match(/:([a-zA-Z0-9_]+)/g) || []).forEach(m => {
    const n = m.replace(/^:/, '')
    if (n) names.add(n)
  })
  const pList = Array.from(names).map(n => ({ key: n, value: '' }))
  pathParamsList.value = pList
  pathJson.value = JSON.stringify(toObject(pList), null, 2)
}

// Query编辑
const addQueryParam = () => { queryParamsList.value.push({ key: '', value: '' }) }
const removeQueryParam = (index: number) => { queryParamsList.value.splice(index, 1) }
const applyQueryJson = () => {
  try {
    const obj = JSON.parse(queryJson.value || '{}') as Record<string, unknown>
    queryParamsList.value = toList(obj)
  } catch { /* ignore JSON parse error */ }
}

// JSON Body编辑
const addJsonBodyParam = () => { jsonBodyList.value.push({ key: '', value: '' }) }
const removeJsonBodyParam = (index: number) => { jsonBodyList.value.splice(index, 1) }
const applyJsonBodyJson = () => {
  try {
    const obj = JSON.parse(jsonBodyJson.value || '{}') as Record<string, unknown>
    jsonBodyList.value = toList(obj)
  } catch { /* ignore */ }
}

// Form Body编辑
const addFormBodyParam = () => { formBodyList.value.push({ key: '', value: '' }) }
const removeFormBodyParam = (index: number) => { formBodyList.value.splice(index, 1) }
const applyFormBodyJson = () => {
  try {
    const obj = JSON.parse(formBodyJson.value || '{}') as Record<string, unknown>
    formBodyList.value = toList(obj)
  } catch { /* ignore */ }
}

// Path编辑
const addPathParam = () => { pathParamsList.value.push({ key: '', value: '' }) }
const removePathParam = (index: number) => { pathParamsList.value.splice(index, 1) }
const applyPathJson = () => {
  try {
    const obj = JSON.parse(pathJson.value || '{}') as Record<string, unknown>
    pathParamsList.value = toList(obj)
  } catch { /* ignore */ }
}

// 初始化四表格：从现有requestConfig填充
const initializeFourParamsPanel = (): void => {
  // Query
  queryParamsList.value = toList(formData.value.requestConfig.queryParams || {})
  queryJson.value = JSON.stringify(toObject(queryParamsList.value), null, 2)
  // Body
  const bt = formData.value.requestConfig.bodyType
  const b = formData.value.requestConfig.body as Record<string, unknown> | null
  if (bt === 'json' && b) {
    jsonBodyList.value = toList(b)
    jsonBodyJson.value = JSON.stringify(b, null, 2)
  } else if (bt === 'form' && b) {
    formBodyList.value = toList(b)
    formBodyJson.value = JSON.stringify(b, null, 2)
  } else {
    jsonBodyList.value = []
    formBodyList.value = []
    jsonBodyJson.value = ''
    formBodyJson.value = ''
  }
}

// 根据 Path 列表替换URL占位符
const applyPathToUrl = (url: string): string => {
  let out = url
  const dict = toObject(pathParamsList.value)
  Object.entries(dict).forEach(([k, v]) => {
    const val = String(v ?? '')
    out = out.replace(new RegExp(`\\{${k}\\}`, 'g'), val)
    out = out.replace(new RegExp(`:${k}(?=/|$)`, 'g'), val)
  })
  return out
}

// 保存前映射：生成最终的 requestConfig
const buildFinalRequestConfig = (): void => {
  const method = (formData.value.requestConfig.method || 'GET').toUpperCase()
  // 1) URL 基础拼接与 Path 替换
  const rawUrl = formData.value.requestConfig.url || ''
  const replacedUrl = applyPathToUrl(rawUrl)
  const fullUrl = toFullUrl(replacedUrl)
  formData.value.requestConfig.url = fullUrl
  // 2) Query 参数：来自 Query 表格
  const qp = toObject(queryParamsList.value)
  if (method === 'GET' || method === 'DELETE') {
    // GET/DELETE：将 JSON/Form 合并进 Query（Query 优先）并置空 Body
    const jsonObj = toObject(jsonBodyList.value)
    const formObj = toObject(formBodyList.value)
    const merged: Record<string, unknown> = { ...formObj, ...jsonObj, ...qp }
    formData.value.requestConfig.queryParams = merged
    formData.value.requestConfig.bodyType = 'none'
    formData.value.requestConfig.body = null
  } else {
    formData.value.requestConfig.queryParams = qp
    // 3) Body：在 JSON 与 Form 中二选一
    const hasJson = jsonBodyList.value.length > 0
    const hasForm = formBodyList.value.length > 0
    const scope: 'json' | 'form' | null = hasJson && hasForm ? selectedBodyScope.value : (hasJson ? 'json' : (hasForm ? 'form' : null))
    if (scope === 'json') {
      formData.value.requestConfig.bodyType = 'json'
      formData.value.requestConfig.body = toObject(jsonBodyList.value)
    } else if (scope === 'form') {
      formData.value.requestConfig.bodyType = 'form'
      formData.value.requestConfig.body = toObject(formBodyList.value)
    } else {
      formData.value.requestConfig.bodyType = 'none'
      formData.value.requestConfig.body = null
    }
  }
}


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
    const sid = props.apiInfo?.system_id
    if (typeof sid === 'string' || typeof sid === 'number') {
      systemId.value = String(sid)
    }
    initializeHelperData()
  }
}, { immediate: true, deep: true })

watch(() => props.apiInfo, (api) => {
  formData.value.requestConfig.method = api?.method || formData.value.requestConfig.method
  formData.value.requestConfig.url = api?.url || formData.value.requestConfig.url
  const sid = api?.system_id
  if (typeof sid === 'string' || typeof sid === 'number') {
    systemId.value = String(sid)
  }
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
    const bodyAssert = formData.value.expectedResponse.body as { value?: unknown }
    const val = bodyAssert?.value ?? formData.value.expectedResponse.body
    expectedResponseJson.value = JSON.stringify(val, null, 2)
  }

  // 初始化四表格参数面板
  initializeFourParamsPanel()
  // 根据当前URL预填充Query与Path占位符
  parseUrlToQueryAndPath()
}


// 解析字符串为JSON（安全失败回退）
const parseJsonIfString = (val: unknown): unknown => {
  if (typeof val === 'string') {
    try {
      return JSON.parse(val)
    } catch {
      return val
    }
  }
  return val
}

// 从 API 详情构建请求体示例
const buildRequestBodyFromApiDetail = (apiDetail: Record<string, unknown>): unknown => {
  const reqSchemaRaw = (apiDetail as any).request_schema ?? (apiDetail as any).request_params
  const reqExampleRaw = (apiDetail as any).request_example ?? (apiDetail as any).example_request

  const reqSchema = parseJsonIfString(reqSchemaRaw)
  const reqExample = parseJsonIfString(reqExampleRaw)

  // 优先使用 request_schema 生成示例
  if (reqSchema && typeof reqSchema === 'object' && !Array.isArray(reqSchema)) {
    try {
      const params = ParamsConverter.fromSchema(reqSchema as Record<string, unknown>)
      const exampleObj = SchemaConverter.toExampleJson(params)
      return exampleObj
    } catch {
      // 转换失败时回退到示例
    }
  }
  // 回退 example_request
  if (reqExample && typeof reqExample === 'object') {
    return reqExample
  }
  return undefined
}

// 从 API 详情构建期望响应示例
const buildExpectedResponseFromApiDetail = (apiDetail: Record<string, unknown>): unknown => {
  const respSchemaRaw = (apiDetail as any).response_schema
  const respExampleRaw = (apiDetail as any).example_response

  const respSchema = parseJsonIfString(respSchemaRaw)
  const respExample = parseJsonIfString(respExampleRaw)

  // 优先使用 response_schema 生成示例
  if (respSchema && typeof respSchema === 'object' && !Array.isArray(respSchema)) {
    try {
      const params = ParamsConverter.fromSchema(respSchema as Record<string, unknown>)
      const exampleObj = SchemaConverter.toExampleJson(params)
      return exampleObj
    } catch {
      // 转换失败时回退到示例
    }
  }
  // 回退 example_response
  if (respExample && typeof respExample === 'object') {
    return respExample
  }
  return undefined
}

// 加载 API 详情并填充请求与期望响应（仅在首次打开或未手动填写时执行）
const initializedFromApi = ref(false)
const loadApiDetailAndPopulate = async () => {
  try {
    if (!props.apiInfo?.id) return
    if (initializedFromApi.value) return
    // 若已有内容（编辑场景），不覆盖用户输入
    const hasRequestBody = !!formData.value.requestConfig.body
    const hasExpectedBody = !!formData.value.expectedResponse.body

    const res = await apiManagementApi.getApiDetail(String(props.apiInfo.id))
    const apiDetail = ((res as unknown as { data?: any }).data?.data ?? (res as unknown as { data?: any }).data ?? res) as Record<string, unknown>
    const sidUnknown = (apiDetail as Record<string, unknown>)['system_id'] ?? (apiDetail as Record<string, unknown>)['systemId'] ?? props.apiInfo?.system_id
    if (typeof sidUnknown === 'string' || typeof sidUnknown === 'number') {
      systemId.value = String(sidUnknown)
    }

    // 填充请求体
    if (!hasRequestBody) {
      const reqBody = buildRequestBodyFromApiDetail(apiDetail)
      if (reqBody && typeof reqBody === 'object') {
        formData.value.requestConfig.bodyType = 'json'
        formData.value.requestConfig.body = reqBody as Record<string, unknown>
        requestBodyJson.value = JSON.stringify(reqBody, null, 2)
      }
    }

    // 填充期望响应（用于参考）
    if (!hasExpectedBody) {
      const expectedBody = buildExpectedResponseFromApiDetail(apiDetail)
      if (expectedBody && typeof expectedBody === 'object') {
        formData.value.expectedResponse.body = { type: 'exact', value: expectedBody, assertions: [] }
        expectedResponseJson.value = JSON.stringify(expectedBody, null, 2)
      }
    }

    initializedFromApi.value = true
  } catch (error) {
    console.error('加载API详情失败:', error)
  }
}

// 对话框打开时加载API详情
watch(() => dialogVisible.value, async (visible) => {
  if (visible) {
    await loadApiDetailAndPopulate()
  }
})

// 当API信息变化且对话框处于打开状态时，尝试填充（避免冗余覆盖）
watch(() => props.apiInfo, async () => {
  if (dialogVisible.value) {
    await loadApiDetailAndPopulate()
  }
})

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
    const parsed = JSON.parse(expectedResponseJson.value)
    formData.value.expectedResponse.body = { type: 'exact', value: parsed, assertions: [] }
  } catch (error) {
    // JSON格式错误，保持原值
  }
}

// 处理保存
const handleSave = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    // 保存前生成最终的请求配置（Path替换、Query生成、Body与Content-Type处理）
    buildFinalRequestConfig()
    const finalData: TestCase = { ...formData.value }
    finalData.requestConfig = {
      ...finalData.requestConfig,
      url: toFullUrl(finalData.requestConfig.url || '')
    }
    emit('save', finalData)
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
  gap: 12px;
}

.key-value-row:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  text-align: right;
}

.base-url-prepend {
  color: #909399;
}
</style>