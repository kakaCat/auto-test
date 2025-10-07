<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    width="80%"
    top="5vh"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    class="api-form-dialog"
    @update:model-value="handleClose"
  >
    <div class="dialog-content">
      <!-- 导航菜单 -->
      <div class="navigation-menu">
        <el-button
          text
          :type="getSectionButtonType('basic')"
          @click="scrollToSection('basic')"
        >
          基本信息
        </el-button>
        <el-button
          text
          :type="getSectionButtonType('params')"
          @click="scrollToSection('params')"
        >
          请求参数
        </el-button>
        <el-button
          text
          :type="getSectionButtonType('response')"
          @click="scrollToSection('response')"
        >
          响应参数
        </el-button>
        <el-button
          text
          :type="getSectionButtonType('tags')"
          @click="scrollToSection('tags')"
        >
          标签与认证
        </el-button>
        <div class="progress-container">
          <el-progress
            :percentage="formProgress"
            :stroke-width="10"
            striped
          />
          <span>完成度</span>
        </div>
      </div>

      <!-- 表单内容 -->
      <el-form
        ref="formRef"
        :model="localFormData"
        :rules="rules"
        label-position="top"
        class="api-form-content"
      >
        <el-collapse
          v-model="activeCollapse"
          @change="handleCollapseChange"
        >
          <!-- 基本信息 -->
          <el-collapse-item
            ref="basicSection"
            name="basic"
          >
            <template #title>
              <div class="panel-title">
                <el-icon><InfoFilled /></el-icon>
                <span>基本信息</span>
                <el-tag
                  v-if="basicInfoComplete"
                  type="success"
                  size="small"
                >
                  已完成
                </el-tag>
                <el-tag
                  v-else
                  type="warning"
                  size="small"
                >
                  {{ basicInfoProgress }}/5
                </el-tag>
              </div>
            </template>
           
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  label="API名称"
                  prop="name"
                >
                  <el-input
                    v-model="localFormData.name"
                    placeholder="请输入API名称"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  label="请求方法"
                  prop="method"
                >
                  <el-select
                    v-model="localFormData.method"
                    placeholder="选择请求方法"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="method in httpMethods"
                      :key="method.value"
                      :label="method.label"
                      :value="method.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  label="所属系统"
                  prop="systemId"
                >
                  <el-select
                    v-model="localFormData.systemId"
                    placeholder="选择所属系统"
                    style="width: 100%"
                    @change="handleSystemChange"
                  >
                    <el-option
                      v-for="system in systemList"
                      :key="String(system.id)"
                      :label="system.name"
                      :value="String(system.id)"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  label="所属模块"
                  prop="moduleId"
                >
                  <el-select
                    v-model="localFormData.moduleId"
                    placeholder="选择所属模块"
                    style="width: 100%"
                    :disabled="!localFormData.systemId"
                  >
                    <el-option
                      v-for="module in availableModules"
                      :key="String(module.id)"
                      :label="module.name"
                      :value="String(module.id)"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item
              label="URL路径"
              prop="url"
            >
              <el-input
                v-model="localFormData.url"
                placeholder="请输入API路径，如：/api/users 或完整URL"
                clearable
              >
                <template #prepend>
                  <span>{{ baseUrl }}</span>
                </template>
                <template #append>
                  <el-button
                    :disabled="localFormData.method !== 'GET'"
                    title="从URL中解析GET参数并填充表格"
                    @click="handleParseQueryClick"
                  >
                    解析GET参数
                  </el-button>
                </template>
              </el-input>
              <div
                v-if="localFormData.method === 'GET'"
                class="url-hint"
              >
                <el-text
                  type="info"
                  size="small"
                >
                  示例：/api/api-interfaces/v1/list?system_id=10&enabled_only=false，点击“解析GET参数”自动生成参数表
                </el-text>
              </div>
            </el-form-item>

            <el-form-item
              label="API描述"
              prop="description"
            >
              <el-input
                v-model="localFormData.description"
                type="textarea"
                :rows="3"
                placeholder="请输入API功能描述"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="状态">
                  <el-switch
                    v-model="localFormData.enabled"
                    active-text="启用"
                    inactive-text="禁用"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="需要登录">
                  <el-switch
                    v-model="localFormData.authRequired"
                    active-text="需要认证"
                    inactive-text="公开访问"
                  />
                  <div class="auth-hint">
                    <el-text
                      size="small"
                      type="info"
                    >
                      {{ localFormData.authRequired ? '调用时需要传递认证Token或Session' : '公开API，无需认证即可访问' }}
                    </el-text>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row
              justify="end"
              class="section-actions"
            >
              <el-button
                type="primary"
                :loading="saving"
                @click="handleSaveBasic"
              >
                保存基本信息
              </el-button>
            </el-row>
          </el-collapse-item>

          <!-- 请求参数面板 -->
          <el-collapse-item
            ref="paramsSection"
            name="params"
          >
            <template #title>
              <div class="panel-title">
                <el-icon><Setting /></el-icon>
                <span>请求参数</span>
                <el-tag
                  v-if="paramsCount > 0"
                  type="success"
                  size="small"
                >
                  {{ paramsCount }} 个参数
                </el-tag>
                <el-tag
                  v-else
                  type="info"
                  size="small"
                >
                  暂无参数
                </el-tag>
              </div>
            </template>

            <!-- 请求参数面板：四标签视图（Query / Path / JSON Body / Form Body） -->
            <el-form-item label="请求参数">
              <el-tabs
                v-model="activeParamsTab"
                type="border-card"
                class="full-width-tabs"
                style="width: 100%"
              >
                <el-tab-pane name="query">
                  <template #label>
                    <span>Query</span>
                    <el-tooltip
                      content="URL查询参数：用于拼接在URL的问号后，如 ?page=1&size=10。适合GET/DELETE请求，或无主体的请求。"
                      placement="top"
                    >
                      <el-icon style="margin-left:6px; color:#909399">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </template>
                  <ParamsEditor
                    v-model="localFormData.requestParameters"
                    :fixed-location="'query'"
                  />
                </el-tab-pane>
                <el-tab-pane name="path">
                  <template #label>
                    <span>Path</span>
                    <el-tooltip
                      content="路径参数：URL路径中的占位符，例如 /users/{id} 或 /users/:id。用于标识资源的唯一位置。"
                      placement="top"
                    >
                      <el-icon style="margin-left:6px; color:#909399">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </template>
                  <ParamsEditor
                    v-model="localFormData.requestParameters"
                    :fixed-location="'path'"
                  />
                </el-tab-pane>
                <el-tab-pane name="json">
                  <template #label>
                    <span>JSON Body</span>
                    <el-tooltip
                      content="请求体(JSON)：以 application/json 作为内容类型，适合复杂结构与嵌套对象的提交。常用于POST/PUT/PATCH请求。"
                      placement="top"
                    >
                      <el-icon style="margin-left:6px; color:#909399">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </template>
                  <ParamsEditor
                    v-model="localFormData.requestParameters"
                    :fixed-location="'json'"
                  />
                </el-tab-pane>
                <el-tab-pane name="form">
                  <template #label>
                    <span>Form Body</span>
                    <el-tooltip
                      content="表单请求体：适用于简单键值对提交。常用 Content-Type: application/x-www-form-urlencoded 或 multipart/form-data。"
                      placement="top"
                    >
                      <el-icon style="margin-left:6px; color:#909399">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </template>
                  <ParamsEditor
                    v-model="localFormData.requestParameters"
                    :fixed-location="'form'"
                  />
                </el-tab-pane>
              </el-tabs>
              <!-- 请求参数示例预览 -->
              <div
                v-if="requestExampleJson"
                class="parameter-example"
              >
                <el-collapse>
                  <el-collapse-item
                    title="参数示例预览"
                    name="request-example"
                  >
                    <pre class="example-json">{{ requestExampleJson }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-form-item>

            <el-row
              justify="end"
              class="section-actions"
            >
              <el-button
                type="primary"
                :loading="saving"
                :disabled="!localFormData.id"
                @click="handleSaveParams"
              >
                保存请求参数
              </el-button>
              <el-text
                v-if="!localFormData.id"
                type="warning"
                size="small"
                style="margin-left:8px"
              >
                请先保存基本信息以生成ID
              </el-text>
            </el-row>
          </el-collapse-item>

          <!-- 响应配置面板 -->
          <el-collapse-item
            ref="responseSection"
            name="response"
          >
            <template #title>
              <div class="panel-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>响应参数</span>
                <el-tag
                  v-if="localFormData.responseParameters && localFormData.responseParameters.length > 0"
                  type="success"
                  size="small"
                >
                  {{ localFormData.responseParameters.length }} 个字段
                </el-tag>
                <el-tag
                  v-else
                  type="info"
                  size="small"
                >
                  未配置
                </el-tag>
              </div>
            </template>

            <!-- 响应配置 (增强版) -->
            <el-form-item label="响应参数">
              <ParamsEditor v-model="localFormData.responseParameters" />
              <!-- 响应参数示例预览 -->
              <div
                v-if="responseExampleJson"
                class="parameter-example"
                style="margin-top: 12px;"
              >
                <el-collapse>
                  <el-collapse-item
                    title="响应示例预览"
                    name="response-example"
                  >
                    <pre class="example-json">{{ responseExampleJson }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-form-item>
            <el-row
              justify="end"
              class="section-actions"
            >
              <el-button
                type="primary"
                :loading="saving"
                :disabled="!localFormData.id"
                @click="handleSaveResponse"
              >
                保存响应参数
              </el-button>
              <el-text
                v-if="!localFormData.id"
                type="warning"
                size="small"
                style="margin-left:8px"
              >
                请先保存基本信息以生成ID
              </el-text>
            </el-row>
          </el-collapse-item>

          <!-- 标签管理面板 -->
          <el-collapse-item
            ref="tagsSection"
            name="tags"
          >
            <template #title>
              <div class="panel-title">
                <el-icon><PriceTag /></el-icon>
                <span>标签管理</span>
                <el-tag
                  v-if="localFormData.tags.length > 0"
                  type="success"
                  size="small"
                >
                  {{ localFormData.tags.length }} 个标签
                </el-tag>
                <el-tag
                  v-else
                  type="info"
                  size="small"
                >
                  无标签
                </el-tag>
              </div>
            </template>

            <!-- 标签 -->
            <el-form-item label="标签">
              <el-select
                v-model="localFormData.tags"
                multiple
                filterable
                allow-create
                placeholder="选择或创建标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in predefinedTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>
            <el-row
              justify="end"
              class="section-actions"
            >
              <el-button
                type="primary"
                :loading="saving"
                :disabled="!localFormData.id"
                @click="handleSaveTags"
              >
                保存标签与认证
              </el-button>
              <el-text
                v-if="!localFormData.id"
                type="warning"
                size="small"
                style="margin-left:8px"
              >
                请先保存基本信息以生成ID
              </el-text>
            </el-row>
          </el-collapse-item>
        </el-collapse>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="saving"
          @click="handleSave"
        >
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Delete, 
  InfoFilled, Setting, DataAnalysis, PriceTag 
} from '@element-plus/icons-vue'
import { apiManagementApi } from '@/api/unified-api'
import ParameterConfig from './ParameterConfig.vue'
import ParamsEditor from '@/components/common/ParamsEditor.vue'
import { ParamsConverter } from '@/utils/paramsConverter'
import SchemaConverter from '@/utils/schemaConversion'
import { debounce } from 'lodash-es'
import { useServiceStore } from '@/stores/service'

// 直接使用统一API的 API 管理入口
const apiProxy = apiManagementApi
// 轻量缓存：服务管理Store（左侧树为单一数据源）
const serviceStore = useServiceStore()

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '新增API'
  },
  formData: {
    type: Object,
    default: () => ({})
  },
  systemList: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

// 响应式数据
const formRef = ref()
const saving = ref(false)
const moduleList = ref([])
// 为避免快速连续触发造成的重复请求，这里对模块列表加载进行防抖处理
const loadModuleListDebounced = debounce((systemId) => {
  void loadModuleList(systemId)
}, 200)
const activeCollapse = ref(['basic']) // 默认展开基本信息面板
const activeSection = ref('basic') // 当前激活的导航区域

// 工具方法：将可能的字符串/数组/空值统一为字符串数组
const toStringArray = (val) => {
  if (Array.isArray(val)) return val
  if (typeof val === 'string') {
    return val
      .split(',')
      .map(s => s.trim())
      .filter(Boolean)
  }
  return []
}

// 本地表单数据
const localFormData = reactive({
  id: '',
  name: '',
  description: '',
  url: '',
  method: 'GET',
  systemId: '',
  moduleId: '',
  enabled: true,
  authRequired: true, // 是否需要登录认证，默认需要
  requestParameters: [],
  responseParameters: [],
  tags: [],
  
})

// HTTP方法选项
const httpMethods = [
  { label: 'GET', value: 'GET', type: 'success' },
  { label: 'POST', value: 'POST', type: 'primary' },
  { label: 'PUT', value: 'PUT', type: 'warning' },
  { label: 'DELETE', value: 'DELETE', type: 'danger' },
  { label: 'PATCH', value: 'PATCH', type: 'info' }
]

// 预定义标签
const predefinedTags = [
  '用户管理', '订单管理', '商品管理', '支付管理',
  '系统管理', '日志管理', '通知管理', '报表管理',
  '认证授权', '数据查询', '数据更新', '文件上传'
]

// 基础URL：从所选系统中获取其配置的url
const baseUrl = computed(() => {
  const sid = String(localFormData.systemId || '')
  if (!sid) return ''
  const list = Array.isArray(props.systemList) ? props.systemList : []
  const system = list.find((s) => String(s.id) === sid)
  const url = system && typeof system.url === 'string' ? system.url : ''
  return url || ''
})

// 可用模块
const availableModules = computed(() => {
  if (!localFormData.systemId) return []
  const sid = String(localFormData.systemId)
  // 优先使用全局缓存的模块列表（左侧树加载后写入），避免重复请求
  const cached = serviceStore.getModulesBySystem(sid)
  if (Array.isArray(cached) && cached.length > 0) {
    return cached
  }
  // 回退到本地列表（首次进入或缓存未命中时）
  return moduleList.value.filter(module => String(module.system_id) === sid)
})

// 基本信息完成度
const basicInfoProgress = computed(() => {
  let count = 0
  if (localFormData.name) count++
  if (localFormData.method) count++
  if (localFormData.url) count++
  if (localFormData.systemId) count++
  if (localFormData.moduleId) count++
  return count
})

const basicInfoComplete = computed(() => basicInfoProgress.value === 5)

// 表单整体完成度 - 使用防抖避免频繁计算
const rawFormProgress = computed(() => {
  // 使用浅拷贝避免响应式追踪过深
  const params = [...localFormData.requestParameters]
  const hasResponse = Array.isArray(localFormData.responseParameters) && localFormData.responseParameters.length > 0
  const tags = [...localFormData.tags]
  
  let total = 0
  let completed = 0
  
  // 基本信息 (权重: 50%)
  total += 50
  completed += (basicInfoProgress.value / 5) * 50
  
  // 请求参数 (权重: 20%)
  total += 20
  if (params.length > 0) {
    completed += 20
  }
  
  // 响应配置 (权重: 20%)
  total += 20
  if (hasResponse) {
    completed += 20
  }
  
  // 标签和测试 (权重: 10%)
  total += 10
  if (tags.length > 0) {
    completed += 10
  }
  
  return Math.round((completed / total) * 100)
})

// 防抖的进度值
const formProgress = ref(rawFormProgress.value)

// 请求参数：根据当前激活Tab进行筛选，用于示例预览
const requestParamsForActiveTab = computed(() => {
  const tab = activeParamsTab.value
  const params = Array.isArray(localFormData.requestParameters) ? localFormData.requestParameters : []
  const filtered = params.filter(p => (p.location || '') === tab)
  return filtered
})

// 请求参数示例JSON字符串
const requestExampleJson = computed(() => {
  const params = requestParamsForActiveTab.value
  if (!Array.isArray(params) || params.length === 0) return ''
  try {
    const example = SchemaConverter.toExampleJson(params)
    return JSON.stringify(example, null, 2)
  } catch (e) {
    return ''
  }
})

// 响应参数示例JSON字符串
const responseExampleJson = computed(() => {
  const params = Array.isArray(localFormData.responseParameters) ? localFormData.responseParameters : []
  if (params.length === 0) return ''
  try {
    const example = SchemaConverter.toExampleJson(params)
    return JSON.stringify(example, null, 2)
  } catch (e) {
    return ''
  }
})

// 监听原始进度变化，使用防抖更新
watch(rawFormProgress, debounce((newProgress) => {
  formProgress.value = newProgress
}, 100))

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入API名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入URL路径', trigger: ['blur', 'change'] },
    { validator: (_, value, callback) => {
        const v = (value || '').trim()
        if (v === '') { callback(); return }
        const isPath = v.startsWith('/')
        const isHttp = /^https?:\/\//i.test(v)
        if (!isPath && !isHttp) {
          callback(new Error('URL必须以 / 开头或以 http(s):// 开头'))
          return
        }
        callback()
      }, trigger: ['blur', 'change'] }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  systemId: [
    { required: true, message: '请选择所属系统', trigger: 'change' }
  ],
  moduleId: [
    { required: true, message: '请选择所属模块', trigger: 'change' }
  ]
}

// 监听表单数据变化
watch(() => props.formData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    const oldSystemId = localFormData.systemId
    
    // 逐个赋值，避免Object.assign触发递归更新
    localFormData.id = newData.id || ''
    localFormData.name = newData.name || ''
    localFormData.description = newData.description || ''
    localFormData.url = newData.path || newData.url || '' // 后端path字段映射为前端url字段
    localFormData.method = newData.method || 'GET'
    localFormData.systemId = newData.system_id != null ? String(newData.system_id) : ''
    localFormData.moduleId = newData.module_id != null ? String(newData.module_id) : ''
    localFormData.enabled = newData.enabled !== undefined ? newData.enabled : true
    localFormData.authRequired = newData.auth_required !== undefined ? (newData.auth_required === 1 || newData.auth_required === '1' || newData.auth_required === true) : true // 认证字段映射：严格判断 1/'1'/true 为需要认证，其余为公开
    // 初始化请求参数：优先从 request_schema，其次从 request_example/example_request，兼容 legacy parameters 字段
    try {
      if (newData.request_schema) {
        const reqSchemaObj = typeof newData.request_schema === 'string'
          ? JSON.parse(newData.request_schema)
          : newData.request_schema
        localFormData.requestParameters = ParamsConverter.fromSchema(reqSchemaObj)
      } else if (newData.request_example || newData.example_request) {
        const reqExampleSource = newData.request_example ?? newData.example_request
        const reqExampleObj = typeof reqExampleSource === 'string'
          ? JSON.parse(reqExampleSource)
          : reqExampleSource
        localFormData.requestParameters = ParamsConverter.fromExample(reqExampleObj)
      } else if (Array.isArray(newData.parameters)) {
        localFormData.requestParameters = newData.parameters
      } else {
        localFormData.requestParameters = []
      }
    } catch (e) {
      console.warn('初始化请求参数失败，已回退为空：', e)
      localFormData.requestParameters = []
    }
    // 初始化响应参数：优先从 response_schema，其次从 response_example 推断
    try {
      if (newData.response_schema) {
        const schemaObj = typeof newData.response_schema === 'string'
          ? JSON.parse(newData.response_schema)
          : newData.response_schema
        localFormData.responseParameters = ParamsConverter.fromSchema(schemaObj)
      } else if (newData.response_example) {
        const exampleObj = typeof newData.response_example === 'string'
          ? JSON.parse(newData.response_example)
          : newData.response_example
        localFormData.responseParameters = ParamsConverter.fromExample(exampleObj)
      } else {
        localFormData.responseParameters = []
      }
    } catch (e) {
      console.warn('初始化响应参数失败，已回退为空：', e)
      localFormData.responseParameters = []
    }
    localFormData.tags = toStringArray(newData.tags)
    
    
    // 保持静默：编辑弹窗初始化期间不自动加载模块列表，避免额外请求
    // 初始化阶段优先使用缓存：如果左侧树已加载过该系统的模块，则直接填充下拉
    if (localFormData.systemId) {
      const sid = String(localFormData.systemId)
      const cachedModules = serviceStore.getModulesBySystem(sid)
      moduleList.value = Array.isArray(cachedModules) ? cachedModules : []
    } else {
      moduleList.value = []
    }
    // if (localFormData.systemId && localFormData.systemId !== oldSystemId) {
    //   loadModuleListDebounced(localFormData.systemId)
    // }
  }
  // 移除else分支中的resetForm调用，避免递归更新
}, { immediate: true, deep: true })

// 已移除：弹框打开即加载模块列表的监听，避免旧的 systemId 触发请求。
// 现在仅在 systemId 变化时加载模块列表（见上方对 formData 的 watch 和 handleSystemChange）。

// 四表格面板状态与方法
const activeParamsTab = ref('query')
const queryList = ref([])
const formList = ref([])
const pathParamsList = ref([])
const showQueryJson = ref(false)
const queryJson = ref('')
const showFormJson = ref(false)
const formJson = ref('')
const showPathJson = ref(false)
const pathJson = ref('')
const jsonBody = ref('')
const activeBodyType = ref('none')

const hasBothBodies = computed(() => {
  const hasJson = (jsonBody.value || '').trim().length > 0
  const hasForm = formList.value.filter(item => (item.key ?? '').trim()).length > 0
  return hasJson && hasForm
})

const paramsCount = computed(() => Array.isArray(localFormData.requestParameters) ? localFormData.requestParameters.length : 0)

const addQueryParam = () => { queryList.value.push({ key: '', value: '' }) }
const removeQueryParam = (index) => { queryList.value.splice(index, 1) }
const applyQueryJson = () => {
  try {
    const obj = JSON.parse(queryJson.value || '{}')
    queryList.value = Object.keys(obj).map(k => ({ key: k, value: String(obj[k] ?? '') }))
  } catch (e) {
    ElMessage.error('Query JSON解析失败')
  }
}

const addFormParam = () => { formList.value.push({ key: '', value: '' }) }
const removeFormParam = (index) => { formList.value.splice(index, 1) }
const applyFormJson = () => {
  try {
    const obj = JSON.parse(formJson.value || '{}')
    formList.value = Object.keys(obj).map(k => ({ key: k, value: String(obj[k] ?? '') }))
  } catch (e) {
    ElMessage.error('Form JSON解析失败')
  }
}

const addPathParam = () => { pathParamsList.value.push({ key: '', value: '' }) }
const removePathParam = (index) => { pathParamsList.value.splice(index, 1) }
const applyPathJson = () => {
  try {
    const obj = JSON.parse(pathJson.value || '{}')
    pathParamsList.value = Object.keys(obj).map(k => ({ key: k, value: String(obj[k] ?? '') }))
  } catch (e) {
    ElMessage.error('Path JSON解析失败')
  }
}

const parseUrlToQueryAndPath = () => {
  // 优先使用 Query 面板中的输入（允许直接粘贴完整 URL）；若无则回退到基本信息中的 URL 字段
  const candidate = (queryJson.value || localFormData.url || '').trim()
  if (!candidate) {
    ElMessage.warning('请先输入URL')
    return
  }

  // 选择解析来源：当内容看起来像 URL（含 ?、以 http(s):// 或 / 开头）时，直接使用；否则回退到基本信息中的 URL
  const source = (() => {
    if (/^https?:\/\//i.test(candidate) || candidate.startsWith('/') || candidate.includes('?')) return candidate
    const basic = String(localFormData.url || '').trim()
    return basic || candidate
  })()

  const toFullUrl = (u) => {
    if (/^https?:\/\//i.test(u)) return u
    // 支持以 / 开头的相对路径或纯路径
    const path = u.startsWith('/') ? u : `/${u}`
    return `${baseUrl.value}${path}`
  }

  let parsed
  try {
    parsed = new URL(toFullUrl(source))
  } catch {
    ElMessage.error('URL格式不正确，无法解析')
    return
  }

  // 解析 Query 参数
  const entries = []
  parsed.searchParams.forEach((value, key) => { entries.push({ key, value: String(value ?? '') }) })
  queryList.value = entries

  // 若勾选了 JSON 模式，则同步填充 queryJson 便于查看
  if (showQueryJson.value) {
    const obj = {}
    entries.forEach(({ key, value }) => { obj[key] = value })
    try { queryJson.value = JSON.stringify(obj, null, 2) } catch {}
  }

  // 将基础信息中的 URL 规范为纯路径（去除查询串和协议域名）
  localFormData.url = parsed.pathname

  // 识别路径占位符（{id} 形式）
  const matches = [...parsed.pathname.matchAll(/\{([a-zA-Z0-9_]+)\}/g)]
  pathParamsList.value = matches.map(m => ({ key: m[1], value: '' }))

  ElMessage.success(`已解析 ${entries.length} 个Query参数，识别 ${pathParamsList.value.length} 个占位符`)
}

watch(jsonBody, (newVal) => {
  const hasJson = (newVal || '').trim().length > 0
  const hasForm = formList.value.filter(i => (i.key ?? '').trim()).length > 0
  activeBodyType.value = hasJson && !hasForm ? 'json' : (hasForm && !hasJson ? 'form' : activeBodyType.value)
})
watch(formList, () => {
  const hasJson = (jsonBody.value || '').trim().length > 0
  const hasForm = formList.value.filter(i => (i.key ?? '').trim()).length > 0
  activeBodyType.value = hasForm && !hasJson ? 'form' : (hasJson && !hasForm ? 'json' : activeBodyType.value)
}, { deep: true })

// 方法
async function loadModuleList(systemId = null) {
  try {
    const params = {}
    if (systemId) {
      // 后端可能期望数字，尽量转换；否则传原值
      const numId = Number(systemId)
      params.system_id = Number.isFinite(numId) ? numId : systemId
    }
    
    const response = await apiProxy.getModuleList(params)
    if (response.success && Array.isArray(response.data)) {
      moduleList.value = response.data.map(module => ({
        id: String(module.id),
        name: module.name,
        system_id: String(module.system_uuid || module.system_id),
        description: module.description,
        enabled: module.enabled
      }))
      // 将最新模块列表写入全局缓存，保持单一数据源
      const sid = String(systemId ?? localFormData.systemId ?? '')
      if (sid) {
        serviceStore.setSystemModules(sid, moduleList.value)
      }
    } else {
      moduleList.value = []
    }
  } catch (error) {
    console.error('加载模块列表失败:', error)
    moduleList.value = []
  }
}

const handleSystemChange = () => {
  // 清空模块选择
  localFormData.moduleId = ''
  // 重新加载该系统下的模块数据
  if (localFormData.systemId) {
    const sid = String(localFormData.systemId)
    if (serviceStore.hasModules(sid)) {
      moduleList.value = serviceStore.getModulesBySystem(sid)
    } else {
      loadModuleListDebounced(sid)
    }
  } else {
    moduleList.value = []
  }
}

const handleParametersChange = (parameters) => {
  // 参数变化时的处理逻辑
  console.log('Parameters changed:', parameters)
}

const handleResponseChange = (response) => {
  // 响应变化时的处理逻辑
  console.log('Response changed:', response)
}

// 已移除草稿态调试功能

const handleCollapseChange = (activeNames) => {
  activeCollapse.value = activeNames
  // 保存折叠状态到本地存储
  localStorage.setItem('api-form-collapse-state', JSON.stringify(activeNames))
}

const getSectionButtonType = (section) => {
  return activeSection.value === section ? 'primary' : ''
}

const scrollToSection = (section) => {
  activeSection.value = section
  
  // 确保对应面板展开
  if (!activeCollapse.value.includes(section)) {
    activeCollapse.value.push(section)
  }
  
  // 滚动到对应区域
  nextTick(() => {
    const sectionRef = `${section}Section`
    if (formRef.value && formRef.value.$refs && formRef.value.$refs[sectionRef]) {
      formRef.value.$refs[sectionRef].$el.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  })
}

const resetForm = () => {
  try {
    // 逐个赋值重置表单数据，避免Object.assign触发递归更新
    localFormData.id = ''
    localFormData.name = ''
    localFormData.description = ''
    localFormData.url = ''
    localFormData.method = 'GET'
    localFormData.systemId = ''
    localFormData.moduleId = ''
    localFormData.enabled = true
    localFormData.authRequired = true
    localFormData.requestParameters = []
    localFormData.responseParameters = []
    localFormData.tags = []
    
  } catch (error) {
    console.warn('重置表单数据失败:', error)
  }
  
  // 使用nextTick确保DOM更新完成后再清除验证
  nextTick(() => {
    try {
      // 多重检查确保formRef存在且有效
      if (formRef.value && 
          typeof formRef.value === 'object' && 
          formRef.value.clearValidate && 
          typeof formRef.value.clearValidate === 'function') {
        formRef.value.clearValidate()
      }
    } catch (error) {
      console.warn('清除表单验证失败:', error)
    }
  })
}

const handleClose = () => {
  emit('update:modelValue', false)
  emit('cancel')
}

// 显式“取消”按钮事件：通知父组件执行取消收尾逻辑，再关闭弹窗
const handleCancel = () => {
  emit('cancel')
  emit('update:modelValue', false)
}

const handleSave = async () => {
  if (!formRef.value || !formRef.value.validate) {
    ElMessage.error('表单未初始化，请稍后重试')
    return
  }

  try {
    // 表单验证
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请检查表单填写是否正确')
      return
    }

    saving.value = true

    // 响应参数采用统一编辑器结构，无需示例校验

    // 从四表格面板构建请求体Schema与格式
    const selectedBodyType = (() => {
      const hasJson = (jsonBody.value || '').trim().length > 0
      const hasForm = formList.value.filter(i => (i.key ?? '').trim()).length > 0
      if (hasJson && hasForm) return activeBodyType.value === 'form' ? 'form' : 'json'
      if (hasJson) return 'json'
      if (hasForm) return 'form'
      return 'json'
    })()
    const schemaObj = (() => {
      try {
        if (selectedBodyType === 'json') {
          const parsed = JSON.parse(jsonBody.value || '{}')
          let params = ParamsConverter.fromExample(parsed)
          // 标注 JSON Body 的 location
          params = params.map(p => ({ ...p, location: 'json' }))
          return ParamsConverter.toRequestSchema(params)
        } else if (selectedBodyType === 'form') {
          const obj = {}
          formList.value.forEach(item => {
            const k = (item.key || '').trim()
            if (!k) return
            obj[k] = item.value ?? ''
          })
          let params = ParamsConverter.fromExample(obj)
          // 标注 Form Body 的 location
          params = params.map(p => ({ ...p, location: 'form' }))
          return ParamsConverter.toRequestSchema(params)
        }
      } catch (e) {
        console.warn('构建请求体Schema失败:', e)
      }
      if (Array.isArray(localFormData.requestParameters) && localFormData.requestParameters.length > 0) {
        return ParamsConverter.toRequestSchema(localFormData.requestParameters)
      }
      return null
    })()

    // 准备保存数据，严格按照后端ApiInterfaceCreate模型构建
    const saveData = {
      id: localFormData.id,
      name: localFormData.name,
      method: localFormData.method,
      url: String(localFormData.url || '').trim(),
      system_id: parseInt(localFormData.systemId),
      description: localFormData.description || null,
      module_id: localFormData.moduleId ? parseInt(localFormData.moduleId) : null,
      version: 'v1',
      status: localFormData.enabled ? 'active' : 'inactive',
      request_format: selectedBodyType,
      response_format: 'json',
      auth_required: localFormData.authRequired ? 1 : 0,
      rate_limit: 1000,
      timeout: 30,
      tags: (() => {
        const arr = toStringArray(localFormData.tags)
        return arr.length > 0 ? arr.join(',') : null
      })(),
      request_schema: schemaObj ?? null,
      response_schema: (Array.isArray(localFormData.responseParameters) && localFormData.responseParameters.length > 0)
        ? ParamsConverter.toSchema(localFormData.responseParameters)
        : null,
      example_response: null
    }

    emit('save', saveData)
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
    saving.value = false
  } finally {
    // 无论成功与否，都重置保存按钮loading状态，避免按钮卡住
    saving.value = false
  }
}

// 重置保存状态的方法
const resetSavingState = () => {
  saving.value = false
}

// 暴露方法给父组件
defineExpose({
  resetSavingState
})

// 分段保存方法
const handleSaveBasic = async () => {
  if (!formRef.value || !formRef.value.validate) {
    ElMessage.error('表单未初始化，请稍后重试')
    return
  }
  try {
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请检查基本信息是否填写完整')
      return
    }
    // 基础校验
    const sid = parseInt(localFormData.systemId)
    if (!Number.isFinite(sid)) {
      ElMessage.error('系统ID无效')
      return
    }
    saving.value = true
    const payload = {
      name: localFormData.name,
      method: localFormData.method,
      url: String(localFormData.url || '').trim(),
      system_id: sid,
      description: localFormData.description || undefined,
      module_id: localFormData.moduleId ? parseInt(localFormData.moduleId) : undefined,
      version: 'v1',
      status: localFormData.enabled ? 'active' : 'inactive',
      request_format: 'json',
      response_format: 'json',
      auth_required: localFormData.authRequired ? 1 : 0,
      tags: (() => {
        const arr = toStringArray(localFormData.tags)
        return arr.length > 0 ? arr.join(',') : undefined
      })()
    }
    let resp
    if (!localFormData.id) {
      resp = await apiProxy.createApi(payload)
    } else {
      resp = await apiProxy.updateApi(String(localFormData.id), payload)
    }
    if (resp && resp.success) {
      const dataRaw = resp.data
       const d = (typeof dataRaw === 'object' && dataRaw !== null) ? dataRaw : {}
       const newId = d.id ?? d.uuid ?? d.api_id
       if (newId !== undefined && newId !== null) {
         localFormData.id = String(newId)
       }
       // 同步后端返回的最新字段，保证保存后回显正确
       if (typeof d.name === 'string') localFormData.name = d.name
       if (typeof d.method === 'string') localFormData.method = d.method
       const pathOrUrl = typeof d.path === 'string' ? d.path : (typeof d.url === 'string' ? d.url : undefined)
       if (pathOrUrl) localFormData.url = pathOrUrl
       if (d.system_id !== undefined && d.system_id !== null) localFormData.systemId = String(d.system_id)
       if (d.module_id !== undefined && d.module_id !== null) localFormData.moduleId = String(d.module_id)
       if (typeof d.status === 'string') localFormData.enabled = String(d.status).toLowerCase() === 'active'
       const ar = d.auth_required
       localFormData.authRequired = (ar === 1 || ar === '1' || ar === true)
       localFormData.tags = toStringArray(d.tags)
       ElMessage.success('基本信息已保存')
    } else {
      throw new Error(resp?.message || '保存基本信息失败')
    }
  } catch (error) {
    console.error('保存基本信息失败:', error)
    ElMessage.error('保存基本信息失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleSaveParams = async () => {
  if (!localFormData.id) {
    ElMessage.warning('请先保存基本信息以生成ID')
    return
  }
  try {
    saving.value = true
    const hasParams = Array.isArray(localFormData.requestParameters) && localFormData.requestParameters.length > 0
    const schemaObj = hasParams
      ? ParamsConverter.toRequestSchema(localFormData.requestParameters)
      : {}
    const payload = {
      request_schema: schemaObj,
      request_format: 'json'
    }
    const resp = await apiProxy.updateApi(String(localFormData.id), payload)
    if (resp && resp.success) {
      const dataRaw = resp.data
      const d = (typeof dataRaw === 'object' && dataRaw !== null) ? dataRaw : {}
      const serverSchema = d && d.request_schema
      let normalizedSchema = null
      if (typeof serverSchema === 'string') {
        try { normalizedSchema = JSON.parse(serverSchema) } catch (e) { normalizedSchema = null }
      } else if (serverSchema && typeof serverSchema === 'object') {
        normalizedSchema = serverSchema
      }
      if (normalizedSchema) {
        localFormData.requestParameters = ParamsConverter.fromSchema(normalizedSchema)
      } else if (!hasParams) {
        localFormData.requestParameters = []
      }
      ElMessage.success(hasParams ? '请求参数已保存' : '已清空请求参数')
    } else {
      throw new Error(resp?.message || '保存请求参数失败')
    }
  } catch (error) {
    console.error('保存请求参数失败:', error)
    ElMessage.error('保存请求参数失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleSaveResponse = async () => {
  if (!localFormData.id) {
    ElMessage.warning('请先保存基本信息以生成ID')
    return
  }
  try {
    saving.value = true
    const schemaObj = Array.isArray(localFormData.responseParameters) && localFormData.responseParameters.length > 0
      ? ParamsConverter.toSchema(localFormData.responseParameters)
      : null
    const payload = {
      response_schema: schemaObj || undefined,
      response_format: 'json'
    }
    const resp = await apiProxy.updateApi(String(localFormData.id), payload)
    if (resp && resp.success) {
      const dataRaw = resp.data
      const d = (typeof dataRaw === 'object' && dataRaw !== null) ? dataRaw : {}
      const serverSchema = d && d.response_schema
      let normalizedSchema = null
      if (typeof serverSchema === 'string') {
        try { normalizedSchema = JSON.parse(serverSchema) } catch (e) { normalizedSchema = null }
      } else if (serverSchema && typeof serverSchema === 'object') {
        normalizedSchema = serverSchema
      }
      if (normalizedSchema) {
        localFormData.responseParameters = ParamsConverter.fromSchema(normalizedSchema)
      }
      ElMessage.success('响应参数已保存')
    } else {
      throw new Error(resp?.message || '保存响应参数失败')
    }
  } catch (error) {
    console.error('保存响应参数失败:', error)
    ElMessage.error('保存响应参数失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleSaveTags = async () => {
  if (!localFormData.id) {
    ElMessage.warning('请先保存基本信息以生成ID')
    return
  }
  try {
    saving.value = true
    const payload = {
      tags: (() => {
        const arr = toStringArray(localFormData.tags)
        return arr.length > 0 ? arr.join(',') : undefined
      })(),
      auth_required: localFormData.authRequired ? 1 : 0
    }
    const resp = await apiProxy.updateApi(String(localFormData.id), payload)
    if (resp && resp.success) {
      const dataRaw = resp.data
      const d = (typeof dataRaw === 'object' && dataRaw !== null) ? dataRaw : {}
      const ar = d.auth_required
      localFormData.authRequired = (ar === 1 || ar === '1' || ar === true)
      localFormData.tags = toStringArray(d.tags)
      ElMessage.success('标签与认证已保存')
    } else {
      throw new Error(resp?.message || '保存标签与认证失败')
    }
  } catch (error) {
    console.error('保存标签与认证失败:', error)
    ElMessage.error('保存标签与认证失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// ——— 增强：从URL解析GET查询参数并填充到参数表 ———
const handleParseQueryClick = async () => {
  if (localFormData.method !== 'GET') {
    ElMessage.warning('仅在GET方法下支持从URL解析参数')
    return
  }
  const urlInput = (localFormData.url || '').trim()
  if (!urlInput) {
    ElMessage.warning('请先输入包含查询参数的URL')
    return
  }

  const toFullUrl = (u) => {
    if (/^https?:\/\//i.test(u)) return u
    // 支持以 / 开头的相对路径或纯路径
    const path = u.startsWith('/') ? u : `/${u}`
    return `${baseUrl.value}${path}`
  }

  let parsed
  try {
    parsed = new URL(toFullUrl(urlInput))
  } catch (e) {
    ElMessage.error('URL格式不正确，无法解析查询参数')
    return
  }

  const entries = []
  parsed.searchParams.forEach((value, key) => {
    entries.push({ key, value })
  })

  if (entries.length === 0) {
    ElMessage.info('URL中未包含查询参数')
    return
  }

  // 若已有参数，提示是否覆盖
  if (Array.isArray(localFormData.requestParameters) && localFormData.requestParameters.length > 0) {
    try {
      await ElMessageBox.confirm(
        '检测到已配置的请求参数，是否用URL中的查询参数替换？',
        '覆盖确认',
        { confirmButtonText: '替换', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }
  }

  // 转换为参数表结构
  const newParams = entries.map(({ key, value }) => ({
    // id/level/parentId由参数组件填充或使用默认
    name: key,
    type: 'string',
    required: false,
    description: String(value ?? ''),
    level: 0,
    parentId: null
  }))

  // 仅保留路径部分
  localFormData.url = parsed.pathname
  // 覆盖参数
  localFormData.requestParameters = newParams
  ElMessage.success(`已解析 ${newParams.length} 个查询参数并填充表格`)
}

// 自动提示：当GET且URL出现查询串时，引导用户点击解析
const urlParseHintShown = ref(false)
watch(() => localFormData.url, (newVal) => {
  if (localFormData.method === 'GET' && typeof newVal === 'string' && newVal.includes('?')) {
    if (!urlParseHintShown.value) {
      ElMessage.info('检测到查询参数，点击“解析GET参数”可自动生成参数表')
      urlParseHintShown.value = true
    }
  }
})

// 方法切换时重置提示标记
watch(() => localFormData.method, () => {
  urlParseHintShown.value = false
})

// 生命周期
onMounted(() => {
  // 仅恢复折叠状态，不在挂载时加载模块列表，避免不必要请求
  const savedState = localStorage.getItem('api-form-collapse-state')
  if (savedState) {
    try {
      activeCollapse.value = JSON.parse(savedState)
    } catch {
      activeCollapse.value = ['basic']
    }
  }
})
</script>

<style scoped>
.dialog-content { width: 100%; }
.api-form-content { width: 100%; }
:deep(.el-form) { width: 100%; }
:deep(.el-form-item__content) { width: 100%; }
.params-section {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.params-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.params-header {
  margin-bottom: 16px;
  font-weight: 600;
  color: #303133;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.param-row:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
  margin-top: 20px;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  padding: 24px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

:deep(.el-dialog__body) {
  padding: 24px;
  background: #fafbfc;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.el-textarea__inner:hover) {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  padding: 12px 24px;
  transition: all 0.2s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-tag) {
  border-radius: 16px;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

.auth-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.auth-hint .el-text {
  font-size: 12px;
  line-height: 1.4;
}

.test-config {
  width: 100%;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
}

.test-hint {
  margin-top: 12px;
  padding: 8px 12px;
  background: #ecfdf5;
  border-radius: 6px;
  border-left: 3px solid #10b981;
}

.test-hint .el-text {
  font-size: 12px;
  line-height: 1.4;
}

.test-hint .el-text {
  font-size: 12px;
  line-height: 1.4;
}

.progress-indicator {
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.progress-text {
  display: block;
  text-align: center;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.quick-navigation {
  margin-bottom: 20px;
  text-align: center;
  padding: 12px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #f0f2f5;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.panel-title .el-icon {
  color: #409eff;
}

.panel-title .el-tag {
  margin-left: auto;
}

:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item) {
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

:deep(.el-collapse-item:hover) {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

:deep(.el-collapse-item__header) {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-bottom: 1px solid #e4e7ed;
  padding: 16px 20px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-collapse-item__content) {
  padding: 24px;
  background: #fafbfc;
}

:deep(.el-collapse-item__arrow) {
  color: #409eff;
  font-weight: bold;
}

:deep(.el-progress-bar__outer) {
  border-radius: 10px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 10px;
}

/* 让请求参数的 Tabs 卡片占满宽度 */
.full-width-tabs { width: 100%; }
.full-width-tabs :deep(.el-tabs__header),
.full-width-tabs :deep(.el-tabs__content) { width: 100%; }

/* 示例展示样式 */
.parameter-example {
  margin-top: 12px;
}
.example-json {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  max-height: 280px;
  overflow: auto;
}
</style>