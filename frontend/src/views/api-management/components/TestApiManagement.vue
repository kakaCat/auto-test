<template>
  <div class="test-case-management">
    <!-- 头部操作栏 -->
    <div class="header-actions">
      <div class="left-actions">
        <el-button
          type="primary"
          @click="handleAddTestCase"
        >
          <el-icon><Plus /></el-icon>
          新增API测试场景
        </el-button>
        <el-button
          type="success"
          :disabled="selectedTestCases.length === 0"
          @click="handleBatchExecute"
        >
          <el-icon><VideoPlay /></el-icon>
          批量执行 ({{ selectedTestCases.length }})
        </el-button>
        <el-button
          type="danger"
          :disabled="selectedTestCases.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </div>
      <div class="right-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索测试场景..."
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>
          导入
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 测试用例列表 -->
    <el-table
      v-loading="loading"
      :data="filteredTestCases"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column
        type="selection"
        width="55"
      />
      <el-table-column
        prop="name"
        label="场景名称"
        min-width="150"
      >
        <template #default="{ row }">
          <div class="test-case-name">
            <span>{{ row.name }}</span>
            <el-tag
              v-if="row.enabled"
              type="success"
              size="small"
              style="margin-left: 8px"
            >
              启用
            </el-tag>
            <el-tag
              v-else
              type="info"
              size="small"
              style="margin-left: 8px"
            >
              禁用
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="description"
        label="描述"
        min-width="200"
        show-overflow-tooltip
      />
      <el-table-column
        prop="method"
        label="请求方法"
        width="100"
      >
        <template #default="{ row }">
          <el-tag :type="getMethodTagType(row.requestConfig.method)">
            {{ row.requestConfig.method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="最后执行"
        width="150"
      >
        <template #default="{ row }">
          <span v-if="row.lastExecutedAt">
            {{ formatTime(row.lastExecutedAt) }}
          </span>
          <span
            v-else
            class="text-gray"
          >未执行</span>
        </template>
      </el-table-column>
      <el-table-column
        label="执行状态"
        width="120"
      >
        <template #default="{ row }">
          <el-tag
            v-if="row.executionCount > 0"
            :type="row.successCount === row.executionCount ? 'success' : 'danger'"
          >
            {{ row.successCount }}/{{ row.executionCount }}
          </el-tag>
          <span
            v-else
            class="text-gray"
          >-</span>
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        width="200"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :loading="row.executing"
            @click="handleExecuteTestCase(row)"
          >
            执行
          </el-button>
          <el-button
            type="default"
            size="small"
            @click="handleEditTestCase(row)"
          >
            编辑
          </el-button>
          <el-button
            type="default"
            size="small"
            @click="handleDuplicateTestCase(row)"
          >
            复制
          </el-button>
          <el-popconfirm
            title="确定删除这个场景吗？"
            @confirm="handleDeleteTestCase(row)"
          >
            <template #reference>
              <el-button
                type="danger"
                size="small"
              >
                删除
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalTestCases"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 测试场景列表/测试场景编辑对话框 -->
    <ApiScenarioEditDialog
      v-model:visible="editDialogVisible"
      :test-case-data="currentTestCase"
      :api-info="apiInfo"
      @save="handleTestCaseSave"
    />

    <!-- 批量执行结果对话框 -->
    <ApiScenarioExecutionResultDialog
      v-model:visible="executionResultVisible"
      :execution-results="batchExecutionResults"
      :api-info="apiInfo"
    />

    <!-- 执行报告区域：显示单个执行与批量执行的报告 -->
    <el-card
      v-if="lastSingleExecution || batchExecutionResults.length"
      class="execution-report"
      style="margin-top: 16px"
    >
      <template #header>
        <div class="card-header">
          <span>执行报告</span>
        </div>
      </template>

      <!-- 单个执行报告 -->
      <div
        v-if="lastSingleExecution"
        class="single-execution-report"
      >
        <el-descriptions
          :column="3"
          border
        >
          <el-descriptions-item label="场景名称">
            {{ lastSingleExecution.testCase.name }}
          </el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="lastSingleExecution.success ? 'success' : 'danger'">
              {{ lastSingleExecution.success ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态码">
            {{ lastSingleExecution.statusCode }}
          </el-descriptions-item>
          <el-descriptions-item label="响应时间">
            {{ lastSingleExecution.responseTime }}ms
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatTime(lastSingleExecution.executedAt) }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息">
            <span
              v-if="lastSingleExecution.error"
              class="error-text"
            >{{ lastSingleExecution.error }}</span>
            <span
              v-else
              class="success-text"
            >-</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 批量执行报告列表 -->
      <div
        v-if="batchExecutionResults.length"
        style="margin-top: 16px"
      >
        <el-table
          :data="batchExecutionResults"
          style="width: 100%"
        >
          <el-table-column
            prop="testCase.name"
            label="场景名称"
            min-width="160"
          />
          <el-table-column
            label="执行状态"
            width="100"
          >
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'">
                {{ row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="statusCode"
            label="状态码"
            width="100"
          />
          <el-table-column
            label="响应时间"
            width="120"
          >
            <template #default="{ row }">
              {{ row.responseTime }}ms
            </template>
          </el-table-column>
          <el-table-column
            prop="executedAt"
            label="执行时间"
            width="180"
          >
            <template #default="{ row }">
              {{ formatTime(row.executedAt) }}
            </template>
          </el-table-column>
          <el-table-column
            label="错误信息"
            min-width="200"
          >
            <template #default="{ row }">
              <span
                v-if="row.error"
                class="error-text"
              >{{ row.error }}</span>
              <span
                v-else
                class="success-text"
              >-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, VideoPlay, Delete, Search, Upload, Download } from '@element-plus/icons-vue'
import ApiScenarioEditDialog from './ApiScenarioEditDialog.vue'
import ApiScenarioExecutionResultDialog from './ApiScenarioExecutionResultDialog.vue'
import { apiManagementApi, testApisApi } from '@/api/unified-api'
import type { TestCase, TestRequestConfig, TestResponseBodyAssertion } from '@/types/test-case'

import { normalizeList } from '@/utils/listNormalizer'
import { RuntimeExecutor } from '@/utils/runtimeExecutor'
const props = defineProps<{ apiInfo: any; visible?: boolean }>()

// 响应式数据
const testCases = ref<TestCase[]>([])
const selectedTestCases = ref<TestCase[]>([])
const searchKeyword = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const editDialogVisible = ref(false)
const executionResultVisible = ref(false)
const lastSingleExecution = ref<{
  testCase: TestCase
  success: boolean
  statusCode: number
  responseTime: number
  executedAt: string
  error?: string
  response?: { statusCode: number; headers: Record<string, unknown>; body: unknown }
  assertionResults?: any[]
} | null>(null)
const currentTestCase = ref<Partial<TestCase> | null>(null)
const batchExecutionResults = ref<Array<{
  testCase: TestCase
  success: boolean
  statusCode: number
  responseTime: number
  executedAt: string
  error?: string
  response?: { statusCode: number; headers: Record<string, unknown>; body: unknown }
  assertionResults?: any[]
}>>([])

// 统一后端API代理
const apiProxy = apiManagementApi
const testApisProxy = testApisApi

// 构建后端测试请求体
const buildTestPayload = (testCase: TestCase): Record<string, any> => {
  const cfg = testCase.requestConfig || ({} as any)
  const headers = cfg.headers || {}
  const queryParams = cfg.queryParams || {}
  const bodyType = cfg.bodyType || 'json'
  const body = cfg.body ?? null
  return {
    method: cfg.method || 'GET',
    url: cfg.url || '',
    headers,
    query_params: queryParams,
    body_type: bodyType,
    body,
    timeout: cfg.timeout ?? 30000,
    follow_redirects: cfg.followRedirects ?? true,
    validate_ssl: cfg.validateSSL ?? true,
    // 透传期望响应，便于后端或前端校验
    expected_response: testCase.expectedResponse || { statusCode: 200 }
  }
}

// 保存到后端的payload构建（snake_case 对齐后端）
const buildSavePayload = (testCase: TestCase): Record<string, unknown> => {
  const cfg = testCase.requestConfig || ({} as any)
  const expected = testCase.expectedResponse || { statusCode: 200 }
  const tags = Array.isArray(testCase.tags) ? testCase.tags.join(',') : (testCase.tags as any)
  return {
    api_id: testCase.apiId,
    name: testCase.name,
    description: testCase.description ?? '',
    enabled: testCase.enabled ?? true,
    tags,
    request_config: {
      method: cfg.method || 'GET',
      url: cfg.url || '',
      headers: cfg.headers || {},
      query_params: cfg.queryParams || {},
      body_type: cfg.bodyType || 'json',
      body: cfg.body ?? null,
      timeout: cfg.timeout ?? 30000,
      follow_redirects: cfg.followRedirects ?? true,
      validate_ssl: cfg.validateSSL ?? true
    },
    expected_response: {
      status_code: (expected as any).statusCode ?? (expected as any).status_code ?? 200,
      headers: (expected as any).headers || {},
      body: (expected as any).body || { type: 'exact', assertions: [] },
      response_time: (expected as any).responseTime ?? (expected as any).response_time,
      size: (expected as any).size
    }
  }
}

// 计算属性
const filteredTestCases = computed(() => {
  let filtered = testCases.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(testCase => 
      testCase.name.toLowerCase().includes(keyword) ||
      testCase.description?.toLowerCase().includes(keyword)
    )
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const totalTestCases = computed(() => {
  let filtered = testCases.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(testCase => 
      testCase.name.toLowerCase().includes(keyword) ||
      testCase.description?.toLowerCase().includes(keyword)
    )
  }
  
  return filtered.length
})

// 方法
const getMethodTagType = (method: string) => {
  const typeMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return typeMap[method] || 'default'
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

const handleSelectionChange = (selection: TestCase[]) => {
  selectedTestCases.value = selection
}

const handleAddTestCase = () => {
  currentTestCase.value = {
    apiId: props.apiInfo.id?.toString() || '',
    name: '',
    description: '',
    enabled: true,
    requestConfig: {
      method: props.apiInfo.method || 'GET',
      url: props.apiInfo.url || '',
      headers: {} as Record<string, string>,
      queryParams: {} as Record<string, any>,
      bodyType: 'json',
      body: null,
      timeout: 30000,
      followRedirects: true,
      validateSSL: true
    },
    expectedResponse: {
      statusCode: 200,
      headers: {},
      body: { type: 'exact', assertions: [] }
    },
    executionConfig: {
      retryCount: 0,
      retryDelay: 1000,
      continueOnFailure: false,
      parallel: false,
      variables: {}
    }
  }
  editDialogVisible.value = true
}

const handleEditTestCase = async (testCase: TestCase): Promise<void> => {
  try {
    loading.value = true
    const idNum = Number(testCase.id)
    const detailId: number | string = Number.isFinite(idNum) ? idNum : testCase.id
    const resp = await testApisProxy.getDetail(detailId)
    const detail = (resp as any)?.data ?? resp
    if (resp && (resp as any).success && detail) {
      const mapped = mapDetailToTestCase(detail, testCase)
      currentTestCase.value = mapped
    } else {
      ElMessage.warning((resp as any)?.message || '获取测试场景详情失败，使用列表数据回显')
      currentTestCase.value = { ...testCase }
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : '获取测试场景详情失败'
    ElMessage.error(msg)
    currentTestCase.value = { ...testCase }
  } finally {
    loading.value = false
    editDialogVisible.value = true
  }
}

const handleDuplicateTestCase = (testCase: TestCase) => {
  currentTestCase.value = {
    ...testCase,
    id: undefined,
    name: `${testCase.name} - 副本`,
    createdAt: undefined,
    updatedAt: undefined,
    lastExecutedAt: undefined,
    // 移除未定义类型字段，保持与 TestCase 类型一致
  }
  editDialogVisible.value = true
}

const handleDeleteTestCase = async (testCase: TestCase) => {
  try {
    // 这里应该调用删除API
    const index = testCases.value.findIndex(t => t.id === testCase.id)
    if (index > -1) {
      testCases.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleExecuteTestCase = async (testCase: TestCase) => {
  try {
    (testCase as any).executing = true
    // 执行前拉取详情，确保包含完整的 request_config（含 query_params）
    const idNum = Number(testCase.id)
    const detailId: number | string = Number.isFinite(idNum) ? idNum : testCase.id
    let execCase: TestCase = testCase
    try {
      const resp = await testApisProxy.getDetail(detailId)
      const detail = (resp as any)?.data ?? resp
      if (resp && (resp as any).success && detail) {
        execCase = mapDetailToTestCase(detail, testCase)
      }
    } catch {
      // 获取详情失败则回退使用列表项数据
    }

    const result = await RuntimeExecutor.executeTestCase(execCase)
    const { success, executedAt } = result
    // 更新测试用例状态
    testCase.lastExecutedAt = executedAt
    testCase.executionCount = (testCase.executionCount || 0) + 1
    testCase.successCount = (testCase.successCount || 0) + (success ? 1 : 0)
    // 更新单个执行报告
    lastSingleExecution.value = result
    ElMessage[success ? 'success' : 'error'](success ? '测试场景执行完成' : (result.error || '执行失败'))
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '执行失败'
    ElMessage.error(msg)
  } finally {
    (testCase as any).executing = false
  }
}

const handleBatchExecute = async () => {
  try {
    loading.value = true
    const promises = selectedTestCases.value.map(async (tc) => {
      (tc as any).executing = true
      try {
        // 执行前获取详情，确保包含完整的请求配置
        const idNum = Number(tc.id)
        const detailId: number | string = Number.isFinite(idNum) ? idNum : tc.id
        let execTc: TestCase = tc
        try {
          const resp = await testApisProxy.getDetail(detailId)
          const detail = (resp as any)?.data ?? resp
          if (resp && (resp as any).success && detail) {
            execTc = mapDetailToTestCase(detail, tc)
          }
        } catch {
          // 忽略详情获取错误，回退使用列表项
        }

        const result = await RuntimeExecutor.executeTestCase(execTc)
        const { executedAt, success } = result
        // 更新测试用例状态
        tc.lastExecutedAt = executedAt
        tc.executionCount = (tc.executionCount || 0) + 1
        tc.successCount = (tc.successCount || 0) + (success ? 1 : 0)
        return result
      } catch (err: unknown) {
        const now = new Date().toISOString()
        tc.lastExecutedAt = now
        tc.executionCount = (tc.executionCount || 0) + 1
        const msg = err instanceof Error ? err.message : '执行失败'
        return { testCase: tc, success: false, statusCode: 0, responseTime: 0, executedAt: now, error: msg }
      } finally {
        (tc as any).executing = false
      }
    })
    const results = await Promise.all(promises)
    batchExecutionResults.value = results
    executionResultVisible.value = true
    ElMessage.success(`批量执行完成，共执行 ${results.length} 个测试场景`)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : '批量执行失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedTestCases.value.length} 个测试场景吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 删除选中的测试用例
    const idsToDelete = selectedTestCases.value.map(t => t.id)
    testCases.value = testCases.value.filter(t => !idsToDelete.includes(t.id))
    selectedTestCases.value = []
    
    ElMessage.success('批量删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

const handleImport = () => {
  ElMessage.info('导入功能开发中...')
}

const handleExport = () => {
  if (selectedTestCases.value.length === 0) {
    ElMessage.warning('请先选择要导出的测试场景')
    return
  }
  
  const exportData = {
    version: '1.0',
    apiId: props.apiInfo.id,
    apiName: props.apiInfo.name,
    testCases: selectedTestCases.value,
    exportedAt: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.apiInfo.name}-test-scenarios.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
}

const handleTestCaseSave = async (testCaseData: TestCase): Promise<void> => {
  try {
    loading.value = true
    const payload = buildSavePayload(testCaseData)
    // 调试：确认是否传递了描述字段到后端
    console.debug('Saving TestCase payload(description,name,api_id):', (payload as any).description, (payload as any).name, (payload as any).api_id)

    const hasId = !!testCaseData.id
    let resp: any
    if (hasId) {
      const idNum = Number(testCaseData.id)
      const id: number | string = Number.isFinite(idNum) ? idNum : testCaseData.id
      resp = await testApisProxy.update(id, payload)
    } else {
      resp = await testApisProxy.create(payload)
    }

    const ok = !!(resp as any)?.success
    if (ok) {
      ElMessage.success((resp as any)?.message || (hasId ? '测试场景更新成功' : '测试场景创建成功'))
    } else {
      ElMessage.warning((resp as any)?.message || '保存完成，但返回未标记成功')
    }

    await fetchTestCases()
    editDialogVisible.value = false
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : '保存测试场景失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const mapItemToTestCase = (item: any): TestCase => {
  const defaultReq: TestRequestConfig = {
    method: props.apiInfo.method || 'GET',
    url: props.apiInfo.url || '',
    headers: {} as Record<string, string>,
    queryParams: {} as Record<string, any>,
    bodyType: 'json',
    body: null,
    timeout: 30000,
    followRedirects: true,
    validateSSL: true
  }
  const tagsArr = (item?.tags || '')
    .split(',')
    .map((t: string) => t.trim())
    .filter((t: string) => !!t)

  // 使用后端返回的 request_config/expected_response 进行安全映射（包含 query_params）
  const requestConfig: TestRequestConfig = mapRequestConfigFromDetail(item as Record<string, unknown>, defaultReq)
  const expectedResponse: TestCase['expectedResponse'] = mapExpectedResponseFromDetail(item as Record<string, unknown>, { statusCode: 200, body: { type: 'exact', assertions: [] } })

  return {
    id: String(item?.id ?? Date.now()),
    apiId: String(item?.api_id ?? props.apiInfo.id ?? ''),
    name: item?.name || '',
    description: (typeof item?.description === 'string' ? item.description : (typeof item?.desc === 'string' ? item.desc : (typeof item?.remark === 'string' ? item.remark : undefined))),
    enabled: item?.enabled ?? true,
    priority: 'medium',
    tags: tagsArr,
    requestConfig,
    expectedResponse,
    preConditions: [],
    postActions: [],
    executionConfig: { retryCount: 0, retryDelay: 1000, continueOnFailure: false, parallel: false, variables: {} },
    createdAt: item?.created_at || new Date().toISOString(),
    updatedAt: item?.updated_at || item?.created_at || new Date().toISOString(),
    executionCount: 0,
    successCount: 0
  }
}

// 类型守卫与规范化工具
const isRecord = (val: unknown): val is Record<string, unknown> => typeof val === 'object' && val !== null
const toStringRecord = (val: unknown): Record<string, string> => {
  const r: Record<string, string> = {}
  if (isRecord(val)) {
    for (const [k, v] of Object.entries(val)) {
      if (typeof v === 'string') r[k] = v
      else if (v != null) r[k] = String(v)
    }
  }
  return r
}
const toAnyRecord = (val: unknown): Record<string, any> => (isRecord(val) ? (val as Record<string, any>) : {})

// TestResponseBodyAssertion 类型守卫
const isResponseBodyAssertion = (val: unknown): val is TestResponseBodyAssertion => {
  if (!isRecord(val)) return false
  const rec = val as Record<string, unknown>
  const typeVal = rec['type']
  const assertionsVal = rec['assertions']
  const typeOk = typeof typeVal === 'string'
  const assertionsOk = Array.isArray(assertionsVal)
  return typeOk && assertionsOk
}

// 从后端详情映射请求配置
const mapRequestConfigFromDetail = (detail: Record<string, unknown>, fallback: TestRequestConfig): TestRequestConfig => {
  const req = toAnyRecord(detail['request_config'])
  const method = typeof req.method === 'string' ? req.method : fallback.method
  const url = typeof req.url === 'string' ? req.url : fallback.url
  const headers = isRecord(req.headers) ? toStringRecord(req.headers) : fallback.headers
  const queryParams = isRecord(req.query_params) ? toAnyRecord(req.query_params) : fallback.queryParams
  const bodyTypeRaw = req.body_type
  const bodyType: TestRequestConfig['bodyType'] = bodyTypeRaw === 'form' || bodyTypeRaw === 'raw' || bodyTypeRaw === 'none' ? bodyTypeRaw : 'json'
  const body = req.body ?? fallback.body
  const timeout = typeof req.timeout === 'number' ? req.timeout : (typeof req.timeout === 'string' ? parseInt(req.timeout, 10) : fallback.timeout)
  const followRedirects = typeof req.follow_redirects === 'boolean' ? req.follow_redirects : fallback.followRedirects
  const validateSSL = typeof req.validate_ssl === 'boolean' ? req.validate_ssl : fallback.validateSSL
  return {
    method,
    url,
    headers,
    queryParams,
    bodyType,
    body,
    timeout,
    followRedirects,
    validateSSL
  }
}

// 从后端详情映射期望响应
const mapExpectedResponseFromDetail = (detail: Record<string, unknown>, fallback: TestCase['expectedResponse']): TestCase['expectedResponse'] => {
  const exp = toAnyRecord(detail['expected_response'])
  const statusRaw = exp.statusCode ?? exp.status_code
  let statusCode: number | number[] = fallback.statusCode ?? 200
  if (typeof statusRaw === 'number') statusCode = statusRaw
  else if (Array.isArray(statusRaw) && statusRaw.every(n => typeof n === 'number')) statusCode = statusRaw as number[]
  const headers = isRecord(exp.headers) ? toStringRecord(exp.headers) : fallback.headers
  const bodyRaw = exp.body
  const body: TestCase['expectedResponse']['body'] = isResponseBodyAssertion(bodyRaw)
    ? bodyRaw
    : (fallback.body ?? { type: 'exact', assertions: [] })
  const responseTime = typeof exp.responseTime === 'number' ? exp.responseTime : (typeof exp.response_time === 'number' ? exp.response_time : fallback.responseTime)
  const size = typeof exp.size === 'number' ? exp.size : fallback.size
  return { statusCode, headers, body, responseTime, size }
}

// 将后端详情数据安全映射为前端 TestCase
const mapDetailToTestCase = (detail: unknown, fallback: TestCase): TestCase => {
  if (!isRecord(detail)) {
    // 如果不是对象，直接回退到列表数据
    return { ...fallback }
  }
  const idRaw = detail['id']
  const id = typeof idRaw === 'string' || typeof idRaw === 'number' ? String(idRaw) : fallback.id
  const apiIdRaw = detail['api_id'] ?? fallback.apiId
  const apiId = typeof apiIdRaw === 'string' || typeof apiIdRaw === 'number' ? String(apiIdRaw) : fallback.apiId
  const name = typeof detail['name'] === 'string' ? (detail['name'] as string) : fallback.name
  const description = typeof detail['description'] === 'string'
    ? (detail['description'] as string)
    : (typeof detail['desc'] === 'string'
        ? (detail['desc'] as string)
        : (typeof detail['remark'] === 'string'
            ? (detail['remark'] as string)
            : fallback.description))
  const enabled = typeof detail['enabled'] === 'boolean' ? (detail['enabled'] as boolean) : fallback.enabled
  const tagsRaw = detail['tags']
  const tags: string[] = Array.isArray(tagsRaw) ? (tagsRaw as unknown[]).map(v => String(v)) : (typeof tagsRaw === 'string' ? tagsRaw.split(',').map(s => s.trim()).filter(Boolean) : fallback.tags)

  const defaultReq: TestRequestConfig = fallback.requestConfig
  const requestConfig = mapRequestConfigFromDetail(detail, defaultReq)
  const expectedResponse = mapExpectedResponseFromDetail(detail, fallback.expectedResponse)

  const createdAt = typeof detail['created_at'] === 'string' ? (detail['created_at'] as string) : fallback.createdAt
  const updatedAt = typeof detail['updated_at'] === 'string' ? (detail['updated_at'] as string) : (createdAt || fallback.updatedAt)

  // 其他执行统计保持回显数据
  const executionCount = fallback.executionCount ?? 0
  const successCount = fallback.successCount ?? 0
  const lastExecutedAt = fallback.lastExecutedAt

  return {
    id,
    apiId,
    name,
    description,
    enabled,
    priority: fallback.priority ?? 'medium',
    tags,
    requestConfig,
    expectedResponse,
    preConditions: fallback.preConditions ?? [],
    postActions: fallback.postActions ?? [],
    executionConfig: fallback.executionConfig ?? { retryCount: 0, retryDelay: 1000, continueOnFailure: false, parallel: false, variables: {} },
    createdAt: createdAt || new Date().toISOString(),
    updatedAt: updatedAt || createdAt || new Date().toISOString(),
    executionCount,
    successCount,
    lastExecutedAt
  }
}

const fetchTestCases = async () => {
  try {
    loading.value = true
    const apiIdRaw = props.apiInfo.id
    const api_id = typeof apiIdRaw === 'string' ? parseInt(apiIdRaw as string, 10) : (apiIdRaw as number | undefined)
    const resp = await testApisProxy.getList({
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchKeyword.value || undefined,
      api_id: Number.isFinite(api_id as number) ? (api_id as number) : undefined
    })
    const normalized = normalizeList(resp)
    const items = normalized.list as any[]
    testCases.value = items.map(mapItemToTestCase)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载测试场景失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTestCases()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchTestCases()
}

const initializeData = () => {
  // 改为从后端加载测试用例列表
  fetchTestCases()
}

onMounted(() => {
  initializeData()
})
</script>

<style scoped>
.test-case-management {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-actions {
  display: flex;
  gap: 10px;
}

.right-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.test-case-name {
  display: flex;
  align-items: center;
}

.text-gray {
  color: #999;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>