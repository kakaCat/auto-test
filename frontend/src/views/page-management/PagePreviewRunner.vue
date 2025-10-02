<template>
  <div class="page-preview-runner">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>Page Preview Runner · 响应映射演示</span>
          <el-tag type="success" class="ml8">运行时映射到 Store</el-tag>
        </div>
      </template>
      <div class="mode-toggle">
        <el-radio-group v-model="mode" size="small">
          <el-radio-button label="url">URL模式</el-radio-button>
          <el-radio-button label="config">配置模式</el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="mode === 'url'">
        <el-form label-width="120px" class="runner-form">
          <el-form-item label="请求URL">
            <el-input v-model="apiUrl" placeholder="输入一个GET接口URL，例如 /api/api-interfaces/v1/6" />
          </el-form-item>

          <el-form-item label="Extract映射(JSON)">
            <el-input
              type="textarea"
              v-model="mappingText"
              :rows="6"
              placeholder='例如 { "id": "apiId", "name": "apiName" }'
            />
            <div class="form-tip">提示：request封装会将后端响应中的 data 字段直接赋给 resp.data，因此通常从根路径开始映射（例如 id, name）。</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="runAndApply">执行并应用映射</el-button>
            <el-button class="ml8" @click="clearStore">清空Store</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-else>
        <el-form label-width="120px" class="runner-form">
          <el-form-item label="PageApiConfig(JSON)">
            <el-input
              type="textarea"
              v-model="configText"
              :rows="10"
              placeholder="粘贴页面API配置JSON，按order顺序执行并映射到Store"
            />
            <div class="form-tip">示例：包含一个GET接口及其映射。配置对象需含 apis 数组，元素包含 id/name/method/path/order/response.extract。</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="executorRunning" @click="runConfigSerial">运行配置（串行）</el-button>
            <el-button class="ml8" @click="clearExecutorRecords">清空记录</el-button>
            <el-button class="ml8" @click="clearStore">清空Store</el-button>
          </el-form-item>
        </el-form>

        <el-card shadow="never" class="mt16">
          <template #header>
            <div class="card-header">
              <span>执行记录</span>
              <el-tag type="info" class="ml8">usePageRuntimeExecutor.runSerial()</el-tag>
            </div>
          </template>
          <el-table :data="records" size="small" style="width: 100%">
            <el-table-column label="名称" prop="name" width="160" />
            <el-table-column label="方法" width="100">
              <template #default="scope">
                <el-tag size="small" :type="getMethodTag(scope.row.method)">{{ scope.row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="路径">
              <template #default="scope"><code>{{ scope.row.path }}</code></template>
            </el-table-column>
            <el-table-column label="耗时(ms)" prop="durationMs" width="100" />
            <el-table-column label="结果" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.success ? 'success' : 'danger'" size="small">{{ scope.row.success ? '成功' : '失败' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="消息" prop="message" />
          </el-table>
        </el-card>
      </div>
    </el-card>

    <div class="mt16 grid-2">
      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>最近响应</span>
            <el-tag type="info" class="ml8">仅展示部分字段</el-tag>
          </div>
        </template>
        <pre class="code-block">{{ prettyJson(lastResponse) }}</pre>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <span>PageRuntime Store数据</span>
            <el-tag type="warning" class="ml8">ResponseMappingConverter.apply()</el-tag>
          </div>
        </template>
        <pre class="code-block">{{ prettyJson(runtimeData) }}</pre>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from '@/utils/request'
import { usePageRuntimeStore } from '@/stores/pageRuntime'
import type { ApiResponseMapping, PageApiConfig } from '@/views/page-management/types/page-config'
import { usePageRuntimeExecutor } from '@/composables/usePageRuntimeExecutor'

const pageRuntime = usePageRuntimeStore()
const mode = ref<'url' | 'config'>('url')

// 默认演示URL与映射（可根据接口结构调整）
const apiUrl = ref('/api/api-interfaces/v1/6')
const mappingText = ref('{\n  "id": "apiId",\n  "name": "apiName"\n}')
const configText = ref(defaultConfigText())
const loading = ref(false)
const { running: executorRunning, records, runSerial, clear } = usePageRuntimeExecutor()

const runtimeData = computed(() => pageRuntime.data)
const lastResponse = computed(() => pageRuntime.lastResponse)

// 方法映射到 Element Plus Tag 类型
function getMethodTag(method: string): string {
  const types: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return types[method] || 'info'
}

function parseMapping(): ApiResponseMapping | null {
  try {
    const extract = JSON.parse(mappingText.value)
    if (!extract || typeof extract !== 'object') {
      ElMessage.warning('映射内容需为JSON对象')
      return null
    }
    const mapping: ApiResponseMapping = { extract }
    return mapping
  } catch (e) {
    ElMessage.error('映射JSON解析失败，请检查格式')
    return null
  }
}

async function runAndApply(): Promise<void> {
  const mapping = parseMapping()
  if (!mapping) return
  loading.value = true
  try {
    const resp = await request.get(apiUrl.value)
    // ApiResponse包装结构：{ success, data, message }
    if (!resp.success) {
      ElMessage.error(resp.message || '请求失败')
      return
    }
    pageRuntime.applyMapping(resp.data, mapping)
    ElMessage.success('已应用映射到PageRuntime Store')
  } catch (err: unknown) {
    ElMessage.error('请求或应用映射过程异常')
    // 控制台记录具体错误以便调试
    // eslint-disable-next-line no-console
    console.error('PreviewRunner error:', err)
  } finally {
    loading.value = false
  }
}

function parseConfig(): PageApiConfig | null {
  let cfgUnknown: unknown
  try {
    cfgUnknown = JSON.parse(configText.value)
  } catch (e) {
    ElMessage.error('配置JSON解析失败，请检查格式')
    return null
  }
  if (!cfgUnknown || typeof cfgUnknown !== 'object') {
    ElMessage.warning('配置需为JSON对象')
    return null
  }
  const cfg = cfgUnknown as PageApiConfig
  if (!Array.isArray(cfg.apis) || cfg.apis.length === 0) {
    ElMessage.warning('配置中缺少可执行的 apis 数组')
    return null
  }
  // 基本字段检查
  const invalid = cfg.apis.some(a => !a || !a.method || !a.path || typeof a.order !== 'number')
  if (invalid) {
    ElMessage.warning('apis 元素需包含 method/path/order 等基本字段')
    return null
  }
  return cfg
}

async function runConfigSerial(): Promise<void> {
  const cfg = parseConfig()
  if (!cfg) return
  try {
    await runSerial(cfg)
    ElMessage.success('配置已执行，结果与映射已写入Store')
  } catch (e: unknown) {
    ElMessage.error(e instanceof Error ? e.message : '执行配置失败')
  }
}

function clearExecutorRecords(): void {
  clear()
  ElMessage.success('执行记录已清空')
}

function clearStore(): void {
  pageRuntime.clear()
  ElMessage.success('Store已清空')
}

function prettyJson(val: unknown): string {
  try {
    return JSON.stringify(val ?? {}, null, 2)
  } catch {
    return String(val)
  }
}

function defaultConfigText(): string {
  const sample: PageApiConfig = {
    systemId: null,
    moduleId: null,
    apis: [
      {
        id: 'demo-interfaces-6',
        apiId: 6,
        name: '接口详情',
        method: 'GET',
        path: '/api/api-interfaces/v1/6',
        callType: 'serial',
        order: 1,
        params: { static: {}, dynamic: {} },
        response: { extract: { id: 'apiId', name: 'apiName' } }
        ,
        error: {}
      }
    ],
    flowChart: { nodes: [], edges: [] }
  }
  return JSON.stringify(sample, null, 2)
}
</script>

<style scoped>
.page-preview-runner {
  padding: 16px;
}
.card-header {
  display: flex;
  align-items: center;
}
.ml8 { margin-left: 8px; }
.mt16 { margin-top: 16px; }
.mode-toggle { margin-bottom: 12px; }
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.code-block {
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 6px;
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  overflow: auto;
}
</style>