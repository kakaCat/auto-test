<!--
  API管理页面组件 (API Management)
  
  功能说明：
  - API接口的统一管理和配置
  - 支持按系统/模块分类管理
  - 提供API的增删改查操作
  - 支持批量导入导出功能
  
  页面布局：
  1. 页面头部 - 标题、描述和主要操作按钮
  2. 左侧面板 - 系统树形结构导航
  3. 右侧面板 - API列表和详细管理
  4. 搜索筛选 - 多条件API检索
  5. 批量操作 - 多选API批量处理
  
  核心功能：
  - API接口CRUD操作
  - 系统模块树形导航
  - 多条件搜索筛选
  - 批量导入导出
  - API测试和调试
  
  数据管理：
  - 响应式数据绑定
  - 分页加载优化
  - 实时搜索过滤
  - 状态持久化
  
  交互特性：
  - 左右分栏布局
  - 树形节点选择
  - 表格多选操作
  - 弹窗表单编辑
  - 拖拽排序支持
  
  技术实现：
  - Vue 3 Composition API
  - Element Plus 组件库
  - 系统树组件集成
  - 表单验证机制
  - 文件上传下载
  
  @author AI Assistant
  @version 1.0.0
  @since 2024-01-15
-->
<template>
  <div class="api-management">
    <!-- 
      页面头部区域
      - 页面标题和描述信息
      - 主要操作按钮（新增、导入、导出）
    -->
    <div class="page-header">
      <div class="header-content">
        <h1>API管理</h1>
        <p>左侧选择系统或模块，右侧管理对应的API接口</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showAddApiDialog">
          <el-icon><DocumentAdd /></el-icon>
          新增API
        </el-button>
        <el-button @click="importApi">
          <el-icon><Upload /></el-icon>
          导入API
        </el-button>
        <el-button @click="exportApi">
          <el-icon><Download /></el-icon>
          导出API
        </el-button>
        <input
          ref="importInputRef"
          type="file"
          accept=".json,.yaml,.yml"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
    </div>

    <!-- 
      主要内容区域
      - 左右分栏布局设计
      - 响应式宽度调整
    -->
    <div class="main-content">
      <!-- 
        左侧系统树导航面板
        - 系统模块树形结构
        - 支持搜索和节点选择
        - 显示层级关系
      -->
      <div class="left-panel">
        <SystemTree
          ref="systemTreeRef"
          :data="systemTreeData"
          search-placeholder="搜索系统和模块"
          :show-count="false"
          :show-disabled="false"
          :categories="['backend']"
          label-key="label"
          children-key="children"
          @node-click="handleSystemNodeClick"
          @refresh="handleTreeRefresh"
        />
      </div>

      <!-- 
        右侧API管理面板
        - API列表展示和操作
        - 搜索筛选功能
        - 批量操作支持
      -->
      <div class="right-panel" v-loading="pageLoading">
        <!-- 
          空状态提示
          - 未选择系统/模块时显示
          - 引导用户进行操作
        -->
        <div v-if="!selectedSystemId && !selectedModuleId" class="empty-state">
          <div class="empty-content">
            <el-icon size="64" color="#c0c4cc">
              <DocumentAdd />
            </el-icon>
            <h3>请选择系统或模块</h3>
            <p>从左侧树形结构中选择一个系统或模块，查看对应的API接口列表</p>
          </div>
        </div>

        <!-- 
          API管理主界面
          - 已选择系统/模块时显示
          - 包含搜索、列表、操作等功能
        -->
        <div v-else>
          <!-- 
            搜索和筛选区域
            - 关键词搜索
            - 请求方法筛选
            - 实时搜索功能
          -->
          <div class="search-section">
          <div class="search-form">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索API名称、描述或URL"
              clearable
              @input="handleSearch"
              style="width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select
              v-model="searchForm.method"
              placeholder="请求方法"
              clearable
              style="width: 120px"
              @change="handleSearch"
            >
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
              <el-option label="PATCH" value="PATCH" />
            </el-select>
            
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            
            <el-button @click="resetSearch">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </div>
        </div>

        <!-- 
          批量操作区域
          - 多选API时显示
          - 支持批量删除、导出等操作
          - 显示选中数量统计
        -->
        <div class="batch-actions" v-if="selectedApis.length > 0">
          <div class="batch-info">
            <span>已选择 {{ selectedApis.length }} 个API</span>
          </div>
          <div class="batch-buttons">
            <el-button type="success" @click="batchTest">
              <el-icon><VideoPlay /></el-icon>
              批量测试
            </el-button>
            <el-button type="primary" @click="batchEnable">
              <el-icon><Check /></el-icon>
              批量启用
            </el-button>
            <el-button type="warning" @click="batchDisable">
              <el-icon><Close /></el-icon>
              批量禁用
            </el-button>
            <el-button type="danger" @click="batchDelete">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>

        <!-- API列表 -->
        <div class="api-list-container">
          <el-table
            v-loading="loading"
            :data="safeApiList"
            stripe
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            
            <el-table-column label="API名称" prop="name" min-width="150">
              <template #default="{ row }">
                <div class="api-name">
                  <span>{{ row.name }}</span>
                  <el-tag v-if="!row.enabled" type="info" size="small">已禁用</el-tag>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="请求方法" prop="method" width="100">
              <template #default="{ row }">
                <el-tag :type="getMethodType(row.method)" size="small">
                  {{ row.method }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="URL路径" prop="url" min-width="200" show-overflow-tooltip />
            
            <el-table-column label="所属系统" prop="system_name" width="120" />
            
            <el-table-column label="描述" prop="description" min-width="150" show-overflow-tooltip />
            
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-switch
                  v-model="row.enabled"
                  @change="handleApiStatusChange(row)"
                />
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button type="text" @click="showEditApiDialog(row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="text" @click="mockApi(row)" style="color: var(--el-color-warning)">
                  <el-icon><Star /></el-icon>
                  Mock
                </el-button>
                <el-button type="text" @click="testApi(row)" style="color: var(--el-color-success)">
                  <el-icon><VideoPlay /></el-icon>
                  测试
                </el-button>
                <el-button type="text" @click="deleteApi(row)" style="color: var(--el-color-danger)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

          <!-- 分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.size"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 批量操作 -->
    <div v-if="selectedApis.length > 0" class="batch-actions">
      <span>已选择 {{ selectedApis.length }} 项</span>
      <el-button @click="batchEnable">批量启用</el-button>
      <el-button @click="batchDisable">批量禁用</el-button>
      <el-button type="danger" @click="batchDelete">批量删除</el-button>
    </div>

    <!-- API表单对话框 -->
    <ApiFormDialog
      ref="apiFormDialogRef"
      v-model="dialogVisible"
      :title="dialogTitle"
      :form-data="form"
      :system-list="systemList"
      @save="saveApi"
      @cancel="handleDialogCancel"
    />
    
    <!-- Mock数据生成器 -->
    <MockDataGenerator
      v-if="mockGeneratorVisible && currentMockApi"
      v-model="mockGeneratorVisible"
      :api-info="(currentMockApi as any)"
      @mock-generated="handleMockGenerated"
    />
    
    <!-- 测试API管理弹框 -->
    <el-dialog
      v-model="testCaseDialogVisible"
      :title="'测试API管理 - ' + (currentTestApi?.name || '')"
      width="90%"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <TestApiManagement
        v-if="testCaseDialogVisible && currentTestApi"
        :api-info="(currentTestApi as any)"
        :visible="testCaseDialogVisible"
      />
    </el-dialog>
    <!-- 测试抽屉 -->
    <ApiTestScenarioDrawer
      v-if="scenarioDrawerVisible && currentScenarioApi"
      v-model:visible="scenarioDrawerVisible"
      :api-info="(currentScenarioApi as any)"
      @params-applied="handleParamsAppliedFromDrawer"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { 
  DocumentAdd, Upload, Download, Search, Refresh, ArrowDown, ArrowRight,
  View, Edit, Delete, Check, Close, Monitor, Document,
  Link, Cloudy, Phone, Connection, DataBoard, Cpu, Platform, Star
} from '@element-plus/icons-vue'
import { apiManagementApi, systemApi, moduleApi } from '@/api/unified-api'
import ApiFormDialog from './components/ApiFormDialog.vue'
import MockDataGenerator from './components/MockDataGenerator.vue'
import TestApiManagement from './components/TestApiManagement.vue'
import SystemTree from '@/components/SystemTree.vue'
import ApiTestScenarioDrawer from './components/ApiTestScenarioDrawer.vue'
import type { ApiItem } from './data/tableColumns'
import type { ApiData } from '@/api/api-management'
import { useServiceStore } from '@/stores/service'

const serviceStore = useServiceStore()

// 类型定义
interface SystemItem {
  id: string | number
  name: string
  description?: string
  enabled?: boolean
  category?: string
  [key: string]: any
}

interface ModuleItem {
  id: string | number
  name: string
  description?: string
  system_id?: string | number
  systemId?: string | number
  enabled?: boolean
  [key: string]: any
}

// 使用统一聚合命名导入
const apiProxy = apiManagementApi
// systemApi 与 moduleApi 由命名导入提供

// 路由实例
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const pageLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增API')
// 防止重试定时器导致的加载状态异常
const retryTimerId = ref<number | null>(null)
const systemTreeRef = ref()
const apiFormDialogRef = ref()
const importInputRef = ref<HTMLInputElement | null>(null)
// Mock数据生成器相关
const mockGeneratorVisible = ref(false)
const currentMockApi = ref<ApiItem | null>(null)
// 测试API管理相关
const testCaseDialogVisible = ref(false)
const currentTestApi = ref<ApiItem | null>(null)
// 已应用的参数（从场景抽屉抛出）
interface AppliedParamsPayload {
  scenarioId: string
  variables: Record<string, any>
  config: Record<string, any>
  detail: any
}
const appliedParams = ref<AppliedParamsPayload | null>(null)
// 已移除测试抽屉功能
// 新增：场景测试抽屉
const scenarioDrawerVisible = ref(false)
const currentScenarioApi = ref<ApiItem | null>(null)

// 系统相关数据
interface TreeNode { id: string | number; label: string; type: 'system' | 'module'; category?: string; systemId?: string | number; children?: TreeNode[] }
const systemList = ref<SystemItem[]>([])
const moduleList = ref<ModuleItem[]>([])
const systemTreeData = ref<TreeNode[]>([])
const selectedSystemId = ref<string>('')
const selectedModuleId = ref<string>('')

// API列表数据 - 确保始终是数组
const apiList = ref<ApiItem[]>([])
const selectedApis = ref<ApiItem[]>([])

// 搜索表单
const searchForm = reactive<{ keyword: string; method: string }>({
  keyword: '',
  method: ''
})

// 分页
const pagination = reactive<{ page: number; size: number; total: number }>({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
interface ApiFormShape {
  id: string | number | ''
  name: string
  description: string
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  system_id: string | number
  module_id: string | number
  enabled: boolean
  tags: string[]
  metadata: Record<string, unknown>
  // 子组件回传的参数schema（可能是JSON字符串或对象或null）
  request_schema?: Record<string, unknown> | string | null
  response_schema?: Record<string, unknown> | string | null
  auth_required?: number
}

// 编辑详情类型，确保严格模式下安全访问属性
type ApiDetail = {
  id?: string | number
  name?: string
  description?: string
  url?: string
  path?: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | string
  system_id?: string | number
  module_id?: string | number
  enabled?: boolean
  tags?: string[]
  metadata?: Record<string, unknown>
  auth_required?: unknown
  request_schema?: Record<string, unknown> | unknown[] | string | null
  response_schema?: Record<string, unknown> | unknown[] | string | null
}
const form = reactive<ApiFormShape>({
  id: '',
  name: '',
  description: '',
  url: '',
  method: 'POST',
  system_id: '',
  module_id: '',
  enabled: true,
  tags: [],
  metadata: {},
  auth_required: 1
})



// 计算属性
// 安全的API列表，确保始终返回数组
const safeApiList = computed<ApiItem[]>(() => {
  if (!Array.isArray(apiList.value)) {
    console.warn('apiList不是数组格式，重置为空数组')
    return []
  }
  return apiList.value
})

const filteredApiList = computed<ApiItem[]>(() => {
  let list: ApiItem[] = apiList.value
  
  // 根据选中的系统或模块筛选（统一字符串比较，避免类型不一致）
  if (selectedModuleId.value) {
    list = list.filter(api => String(api.module_id ?? '') === String(selectedModuleId.value))
  } else if (selectedSystemId.value) {
    list = list.filter(api => String(api.system_id ?? '') === String(selectedSystemId.value))
  }
  
  // 按关键词搜索
  if (searchForm.keyword) {
    const keyword = searchForm.keyword.toLowerCase()
    list = list.filter(api => 
      (api.name ? api.name.toLowerCase() : '').includes(keyword) ||
      ((api.description ? api.description.toLowerCase() : '')).includes(keyword) ||
      ((api.url ? api.url.toLowerCase() : '')).includes(keyword)
    )
  }
  
  // 按方法筛选
  if (searchForm.method) {
    list = list.filter(api => api.method === searchForm.method)
  }
  
  return list
})

// 方法
const loadSystemList = async (retryCount = 0): Promise<void> => {
  try {
    // 使用统一的启用系统-模块树接口
    const response = await systemApi.getEnabledTree('backend')
    if (response.success) {
      const list = Array.isArray(response.data) ? response.data : []
      // 设置系统列表
      systemList.value = list as SystemItem[]
      // 聚合模块列表
      moduleList.value = (list as unknown[]).flatMap((s: unknown) => {
        const mods = (s as { modules?: unknown }).modules
        return Array.isArray(mods) ? mods : []
      }) as ModuleItem[]
      // 写入缓存
      serviceStore.setSystems(systemList.value)
      if (Array.isArray(moduleList.value)) {
        serviceStore.setSystemsAndModules(systemList.value, moduleList.value)
      }
      // 直接构建系统-模块树
      const treeData: TreeNode[] = (list as unknown[]).map((system: unknown) => {
        const sys = system as SystemItem & { modules?: ModuleItem[]; category?: string }
        const systemNode: TreeNode = {
          id: sys.id,
          label: sys.name,
          type: 'system',
          category: (sys as any).category ?? 'other',
          children: []
        }
        const mods = Array.isArray(sys.modules) ? sys.modules : []
        mods.forEach((module: ModuleItem) => {
          const moduleNode: TreeNode = {
            id: module.id,
            label: module.name,
            type: 'module',
            systemId: sys.id,
            children: []
          }
          systemNode.children!.push(moduleNode)
        })
        return systemNode
      })
      systemTreeData.value = treeData
    } else {
      console.warn('系统与模块树接口返回失败:', response)
      systemList.value = []
      moduleList.value = []
      throw new Error('获取启用系统及模块树失败')
    }
  } catch (error: unknown) {
    console.error('加载启用系统与模块树失败:', error)
    systemList.value = []
    moduleList.value = []
    // 清空缓存防止脏数据
    serviceStore.setSystems([])
    const msg = error instanceof Error ? error.message : '网络连接错误'
    
    if (retryCount < 2) {
      ElMessage.warning(`加载启用系统与模块树失败，正在重试... (${retryCount + 1}/3)`) 
      setTimeout(() => loadSystemList(retryCount + 1), 1000)
    } else {
      ElMessage.error('加载启用系统与模块树失败: ' + msg)
      ElMessageBox.confirm(
        '加载启用系统与模块树失败，是否重新尝试？',
        '网络错误',
        {
          confirmButtonText: '重试',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        loadSystemList(0)
      }).catch(() => {
        // 用户取消重试
      })
    }
  }
}

const loadModuleList = async (retryCount = 0): Promise<void> => {
  try {
    // 直接使用模块API获取启用模块列表，并保证返回结构解析正确
    const response = await moduleApi.getEnabledModules({ enabled_only: true })
    // 兼容两种返回结构：
    // 1) BaseApi.getEnabledList: response.data 为数组
    // 2) ModuleApi.getEnabledModules: response.data 为 { data: ModuleEntity[], total }
    const payload = (response as any)?.data
    const list = Array.isArray(payload) ? payload : (payload?.data ?? [])

    if (Array.isArray(list)) {
      moduleList.value = list as ModuleItem[]
      // 按系统写入模块缓存
      const grouped: Record<string, ModuleItem[]> = {}
      (list as ModuleItem[]).forEach((m: ModuleItem) => {
        const sid = String(m.system_id ?? (m as any).systemId)
        if (!grouped[sid]) grouped[sid] = []
        grouped[sid].push(m)
      })
      if (typeof (serviceStore as any).setSystemModules !== 'function') {
        throw new Error('serviceStore.setSystemModules 方法不可用')
      }
      for (const sid in grouped) {
        (serviceStore as any).setSystemModules(sid, grouped[sid])
      }
    } else {
      console.warn('模块列表数据格式不正确:', payload)
      moduleList.value = []
      throw new Error('获取启用模块列表失败')
    }
  } catch (error: unknown) {
    console.error('加载启用模块列表失败:', error)
    moduleList.value = []
    const msg = (error instanceof Error && error.message) ? error.message : '网络连接错误'
    if (retryCount < 2) {
      ElMessage.warning(`加载启用模块列表失败，正在重试... (${retryCount + 1}/3)`) 
      setTimeout(() => loadModuleList(retryCount + 1), 1000)
    } else {
      ElMessage.error('加载启用模块列表失败: ' + msg)
    }
  }
}

const buildSystemTree = async (): Promise<void> => {
  try {
    // 使用统一的启用系统-模块树接口
    const response = await systemApi.getEnabledTree('backend')
    if (response.success) {
      const systems = Array.isArray(response.data) ? response.data : []
      const treeData: TreeNode[] = (systems as unknown[]).map((s: unknown) => {
        const sys = s as SystemItem & { modules?: ModuleItem[]; category?: string }
        const node: TreeNode = {
          id: sys.id,
          label: sys.name,
          type: 'system',
          category: (sys as any).category ?? 'other',
          children: []
        }
        const mods = Array.isArray(sys.modules) ? sys.modules : []
        mods.forEach((m: ModuleItem) => {
          node.children!.push({
            id: m.id,
            label: m.name,
            type: 'module',
            systemId: sys.id,
            children: []
          } as TreeNode)
        })
        return node
      })
      systemTreeData.value = treeData
    } else {
      throw new Error('获取启用系统及模块树失败')
    }
  } catch (error: unknown) {
    console.error('获取系统-模块树失败:', error)
    systemTreeData.value = []
  }
}

const loadApiList = async (retryCount = 0): Promise<void> => {
  try {
    if (retryCount === 0) {
      loading.value = true
    }
    const params: Record<string, any> = {}
    
    // 只传递有值的参数，避免空字符串导致后端验证失败
    if (selectedSystemId.value) {
      params.system_id = String(selectedSystemId.value)
    }
    if (selectedModuleId.value) {
      params.module_id = String(selectedModuleId.value)
    }
    if (searchForm.keyword && searchForm.keyword.trim()) {
      params.keyword = searchForm.keyword.trim()
    }
    if (searchForm.method) {
      params.method = searchForm.method
    }
    params.enabled_only = false
    // 传递分页参数
    params.page = pagination.page
    params.size = pagination.size

    const response = await apiProxy.getApis(params)
    if (response.success) {
      // 确保数据是数组格式
      const data = response.data
      if (Array.isArray(data)) {
        // 映射后端 path 字段到前端使用的 url 字段，避免列表中URL为空
        apiList.value = (data as ApiItem[]).map((api: ApiItem) => ({
          ...api,
          url: api.url ?? api.path ?? ''
        } as ApiItem))
        pagination.total = Array.isArray(apiList.value) ? apiList.value.length : 0
      } else if (data && typeof data === 'object' && (Array.isArray((data as any).items) || Array.isArray((data as any).list))) {
        // 兼容分页数据或列表数据格式：支持 { items, total } 或 { list, total }
        const srcList: ApiItem[] = Array.isArray((data as any).items) ? (data as any).items : (data as any).list
        apiList.value = (srcList as ApiItem[]).map((api: ApiItem) => ({
          ...api,
          url: api.url ?? api.path ?? ''
        } as ApiItem))
        pagination.total = typeof (data as any).total === 'number' ? (data as any).total : apiList.value.length
      } else {
        console.warn('API数据格式异常:', data)
        apiList.value = []
        pagination.total = 0
      }
      // 成功后关闭加载
      loading.value = false
    } else {
      throw new Error(response.message || '获取API列表失败')
    }
  } catch (error: any) {
    console.error('加载API列表失败:', error)
    
    if (retryCount < 2) {
      ElMessage.warning(`加载API列表失败，正在重试... (${retryCount + 1}/3)`) 
      // 清理已有的重试定时器，避免多个并发重试导致loading异常
      if (retryTimerId.value) {
        clearTimeout(retryTimerId.value)
        retryTimerId.value = null
      }
      retryTimerId.value = window.setTimeout(() => {
        retryTimerId.value = null
        loadApiList(retryCount + 1)
      }, 1000)
      // 重试期间保持加载状态，不关闭
      return
    } else {
      ElMessage.error('加载API列表失败: ' + (error.message || '网络连接错误'))
      // 显示空状态而不是错误对话框，因为这是更频繁的操作
      apiList.value = []
      pagination.total = 0
      // 最终失败后关闭加载
      loading.value = false
    }
  }
}

const handleSystemNodeClick = (data: TreeNode): void => {
  if (data.type === 'system') {
    selectedSystemId.value = String(data.id)
    selectedModuleId.value = ''
  } else if (data.type === 'module') {
    selectedSystemId.value = String(data.systemId)
    selectedModuleId.value = String(data.id)
  }
  
  // 更新URL参数
  const query: Record<string, string> = {}
  if (selectedSystemId.value) {
    query.systemId = selectedSystemId.value
  }
  if (selectedModuleId.value) {
    query.moduleId = selectedModuleId.value
  }
  
  // 使用replace避免在浏览器历史中创建新条目
  router.replace({ 
    path: route.path, 
    query 
  })
  
  loadApiList()
}

/**
 * 根据系统分类获取图标
 */


const handleSearch = (): void => {
  loadApiList()
}

const resetSearch = (): void => {
  searchForm.keyword = ''
  searchForm.method = ''
  selectedSystemId.value = ''
  loadApiList()
}

const handleSelectionChange = (selection: ApiItem[]): void => {
  // 确保selection是数组
  if (Array.isArray(selection)) {
    selectedApis.value = selection
  } else {
    console.warn('选择数据格式异常:', selection)
    selectedApis.value = []
  }
}

const handleApiStatusChange = async (api: ApiItem & { enabled: boolean }): Promise<void> => {
  try {
    const res = await apiProxy.updateApi(String(api.id), { status: api.enabled ? 'active' : 'inactive' })
    if (res?.success) {
      ElMessage.success('状态更新成功')
    } else {
      ElMessage.error(res?.message || '更新状态失败')
      api.enabled = !api.enabled // 回滚状态
    }
  } catch (error: any) {
    console.error('更新API状态失败:', error)
    ElMessage.error('更新状态失败')
    api.enabled = !api.enabled // 回滚状态
  }
}

const getMethodType = (method: string): string => {
  const types: Record<string, string> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return types[method] || 'info'
}

const showAddApiDialog = (): void => {
  dialogTitle.value = '新增API'
  resetForm(true) // 保留选中的系统和模块信息
  dialogVisible.value = true
}

const showEditApiDialog = async (api: ApiItem): Promise<void> => {
  dialogTitle.value = '编辑API'
  loading.value = true
  try {
    // 先清空系统/模块，避免子组件基于旧值触发模块列表请求
    form.system_id = ''
    form.module_id = ''

    const res = await apiProxy.getApiDetail(String(api.id))
    const detail: ApiDetail = (typeof res === 'object' && res !== null && 'data' in res
      ? ((res as { data?: ApiDetail }).data ?? {})
      : {}) as ApiDetail

    // 使用详情数据填充表单，避免使用列表行数据
    form.id = detail.id ?? api.id
    form.name = detail.name ?? ''
    form.description = detail.description ?? ''
    form.url = detail.url ?? detail.path ?? ''

    // 方法字段安全处理，严格限定到允许集合
    const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] as const
    const methodVal = typeof detail.method === 'string' ? detail.method.toUpperCase() : ''
    form.method = (allowedMethods as readonly string[]).includes(methodVal)
      ? (methodVal as ApiFormShape['method'])
      : 'POST'

    form.system_id = detail.system_id ? String(detail.system_id) : (api.system_id ? String(api.system_id) : '')
    form.module_id = detail.module_id ? String(detail.module_id) : (api.module_id ? String(api.module_id) : '')
    form.enabled = detail.enabled !== undefined ? Boolean(detail.enabled) : Boolean(api.enabled)

    // 标签兼容字符串/数组
    if (Array.isArray(detail.tags)) {
      form.tags = detail.tags
    } else if (typeof (detail as { tags?: string }).tags === 'string' && (detail as { tags?: string }).tags) {
      form.tags = [(detail as { tags?: string }).tags as string]
    } else if (Array.isArray(api.tags)) {
      form.tags = api.tags
    } else {
      form.tags = []
    }

    // 元数据仅接受对象
    form.metadata = (detail.metadata && typeof detail.metadata === 'object') ? detail.metadata : {}

    // 映射认证字段：将后端的 1/'1'/true 统一为 0/1 数值
    const toStrictAuth = (val: unknown): 0 | 1 => (val === 1 || val === '1' || val === true) ? 1 : 0
    const arVal: unknown = (detail as { auth_required?: unknown }).auth_required
    form.auth_required = arVal === undefined ? 1 : toStrictAuth(arVal)

    // 回填参数schema到子组件（ApiFormDialog）以便同步表格/JSON模式（类型安全）
    const normalizeSchema = (val: unknown): Record<string, unknown> | string | null => {
      if (val === null || val === undefined) return null
      if (typeof val === 'string') return val
      if (Array.isArray(val)) {
        try {
          return JSON.stringify(val)
        } catch {
          return '[]'
        }
      }
      if (typeof val === 'object') return val as Record<string, unknown>
      return null
    }
    form.request_schema = normalizeSchema((detail as { request_schema?: unknown }).request_schema)
    form.response_schema = normalizeSchema((detail as { response_schema?: unknown }).response_schema)

    dialogVisible.value = true
  } catch (error: unknown) {
    console.error('获取API详情失败:', error)
    ElMessage.error('获取API详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}


// 修复：列表"测试"按钮应该打开测试用例管理弹框
const testApi = (api: ApiItem): void => {
  manageTestCases(api)
}


const deleteApi = async (api: ApiItem): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定要删除这个API吗？', '确认删除', {
      type: 'warning'
    })
    
    await apiProxy.deleteApi(String(api.id))
    ElMessage.success('删除成功')
    loadApiList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除API失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const mockApi = (api: ApiItem): void => {
  currentMockApi.value = api
  mockGeneratorVisible.value = true
}

const handleMockGenerated = (mockData: Record<string, any>): void => {
  console.log('Mock数据已生成:', mockData)
  ElMessage.success('Mock数据生成成功')
  mockGeneratorVisible.value = false
}

const manageTestCases = (api: ApiItem): void => {
  currentTestApi.value = api
  testCaseDialogVisible.value = true
}

const handleParamsAppliedFromDrawer = (payload: AppliedParamsPayload): void => {
  appliedParams.value = payload
  ElMessage.success('参数已接收，可用于后续测试或编排')
}

const saveApi = async (formData: ApiFormShape): Promise<void> => {
  try {
    // 调试日志：观察父组件是否接收到了子组件的 save 事件
    console.log('[ApiManagement] save event payload:', formData)

    // 统一解析并校验ID：过滤 null/undefined/空串/NaN
    const coerceId = (id: unknown): number | undefined => {
      if (id == null) return undefined
      const s = String(id).trim()
      if (!s) return undefined
      const n = Number(s)
      return Number.isNaN(n) ? undefined : n
    }

    const sysId = coerceId(formData.system_id) ?? coerceId(selectedSystemId.value)
    const modId = coerceId(formData.module_id) ?? coerceId(selectedModuleId.value)

    // 创建时必须有有效的系统/模块ID
    if (!formData.id) {
      if (sysId == null || modId == null) {
        ElMessage.error('请先选择系统与模块，或在表单中填写')
        if (apiFormDialogRef.value) apiFormDialogRef.value.resetSavingState()
        return
      }
    }

    // schema处理：创建传对象、更新传字符串
    const ensureSchemaObject = (schema: unknown): Record<string, unknown> | undefined => {
      if (schema == null) return undefined
      if (typeof schema === 'string') {
        const s = schema.trim()
        if (!s) return undefined
        try { return JSON.parse(s) as Record<string, unknown> } catch (e) {
          console.warn('request/response schema 解析失败:', e)
          return undefined
        }
      }
      if (typeof schema === 'object') return schema as Record<string, unknown>
      return undefined
    }
    const ensureSchemaString = (schema: unknown): string | undefined => {
      if (schema == null) return undefined
      if (typeof schema === 'string') {
        const s = schema.trim(); return s || undefined
      }
      if (typeof schema === 'object') {
        try { return JSON.stringify(schema as Record<string, unknown>) } catch (e) {
          console.warn('request/response schema 序列化失败:', e)
          return undefined
        }
      }
      return undefined
    }
    // 新增：统一将标签转换为逗号分隔字符串，兼容字符串或数组
    const ensureTagsString = (tags: unknown): string => {
      const arr = Array.isArray(tags)
        ? tags as string[]
        : (typeof tags === 'string'
            ? tags.split(',').map(s => s.trim()).filter(Boolean)
            : [])
      return arr.length ? arr.join(',') : ''
    }

    // 兼容处理：优先使用子组件提供的 status，其次根据 enabled 推导；同时透传扩展字段
    const ext: {
      status?: 'active' | 'inactive' | 'deprecated' | 'testing'
      request_format?: 'json' | 'form' | 'xml'
      response_format?: 'json' | 'xml' | 'text'
      version?: string
      auth_required?: number
      rate_limit?: number
      timeout?: number
      example_request?: string | null
      example_response?: string | null
    } = formData as unknown as {
      status?: 'active' | 'inactive' | 'deprecated' | 'testing'
      request_format?: 'json' | 'form' | 'xml'
      response_format?: 'json' | 'xml' | 'text'
      version?: string
      auth_required?: number
      rate_limit?: number
      timeout?: number
      example_request?: string | null
      example_response?: string | null
    }
    const statusVal: 'active' | 'inactive' | 'deprecated' | 'testing' = ext.status ?? (formData.enabled ? 'active' : 'inactive')

    if (formData.id) {
      // 更新接口：按后端ApiInterfaceUpdate要求传字符串
      const payloadUpdate: Record<string, unknown> = {
        name: formData.name,
        description: formData.description,
        method: formData.method,
        url: String(formData.url || '').trim(),
        system_id: sysId,
        module_id: modId,
        status: statusVal,
        request_format: ext.request_format,
        response_format: ext.response_format,
        version: ext.version,
        auth_required: ext.auth_required,
        rate_limit: ext.rate_limit,
        timeout: ext.timeout,
        example_request: ext.example_request,
        example_response: ext.example_response,
        tags: ensureTagsString(formData.tags),
        request_schema: ensureSchemaString(formData.request_schema),
        response_schema: ensureSchemaString(formData.response_schema)
      }
      console.log('[ApiManagement] update payload =>', payloadUpdate)

      const updateRes = await apiProxy.updateApi(String(formData.id), payloadUpdate as unknown as Partial<ApiData>)
      if (!updateRes?.success) {
        if (apiFormDialogRef.value) apiFormDialogRef.value.resetSavingState()
        return
      }
    } else {
      // 创建接口：按后端ApiInterfaceCreate要求传对象
      const payloadCreate: Record<string, unknown> = {
        name: formData.name,
        description: formData.description,
        method: formData.method,
        url: String(formData.url || '').trim(),
        system_id: Number(sysId!),
        module_id: Number(modId!),
        status: statusVal,
        request_format: ext.request_format,
        response_format: ext.response_format,
        version: ext.version,
        auth_required: ext.auth_required,
        rate_limit: ext.rate_limit,
        timeout: ext.timeout,
        example_request: ext.example_request,
        example_response: ext.example_response,
        tags: ensureTagsString(formData.tags),
        request_schema: ensureSchemaObject(formData.request_schema),
        response_schema: ensureSchemaObject(formData.response_schema)
      }
      console.log('[ApiManagement] create payload =>', payloadCreate)

      const createRes = await apiProxy.createApi(payloadCreate as unknown as Partial<ApiData>)
      if (!createRes?.success) {
        if (apiFormDialogRef.value) apiFormDialogRef.value.resetSavingState()
        return
      }
    }
    
    dialogVisible.value = false
    loadApiList()
    if (apiFormDialogRef.value) apiFormDialogRef.value.resetSavingState()
  } catch (error: unknown) {
    console.error('保存API失败:', error)
    
    let errorMessage = '保存失败'
    if (error instanceof Error && error.message && error.message !== '请求失败') {
      errorMessage = error.message
    } else if ((error as any)?.response && (error as any).response.data) {
      const respData = (error as any).response.data
      if (typeof respData === 'string') {
        errorMessage = respData
      } else if (respData.message) {
        errorMessage = respData.message
      } else if (respData.detail) {
        errorMessage = JSON.stringify(respData.detail)
      } else {
        errorMessage = JSON.stringify(respData)
      }
    }
    
    ElMessage.error(errorMessage)
    if (apiFormDialogRef.value) apiFormDialogRef.value.resetSavingState()
  }
}

// 处理对话框取消事件
const handleDialogCancel = (): void => {
  dialogVisible.value = false
  if (retryTimerId.value) {
    clearTimeout(retryTimerId.value)
    retryTimerId.value = null
  }
  loading.value = false
}

const resetForm = (preserveSelection = false): void => {
  const resetData = {
    id: '',
    name: '',
    description: '',
    url: '',
    method: 'POST',
    system_id: preserveSelection && selectedSystemId.value ? selectedSystemId.value : '',
    module_id: preserveSelection && selectedModuleId.value ? selectedModuleId.value : '',
    enabled: true,
    tags: [],
    metadata: {}
  }
  
  // 安全地重置表单数据
  try {
    Object.assign(form, resetData)
  } catch (error) {
    console.warn('重置表单数据失败:', error)
    // 如果Object.assign失败，逐个赋值
    for (const key in resetData as any) {
      if ((form as any).hasOwnProperty(key)) {
        ;(form as any)[key] = (resetData as any)[key]
      }
    }
  }
}

const handleSizeChange = (size: number): void => {
  pagination.size = size
  pagination.page = 1
  loadApiList()
}

const handlePageChange = (page: number): void => {
  pagination.page = page
  loadApiList()
}

const batchEnable = async (): Promise<void> => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请先选择要启用的API')
    return
  }

  let loadingInstance: { close: () => void } | null = null
  try {
    loadingInstance = ElLoading.service({
      text: `正在启用 ${selectedApis.value.length} 个API...`,
      background: 'rgba(0, 0, 0, 0.7)'
    })

    const results = await Promise.all(
      selectedApis.value.map((api: ApiItem) => apiProxy.updateApi(String(api.id), { status: 'active' }))
    )
    const successCount = results.filter(r => r?.success).length
    const failCount = results.length - successCount
    if (successCount > 0) {
      ElMessage.success(`成功启用 ${successCount} 个API`)
    }
    if (failCount > 0) {
      ElMessage.error(`启用失败 ${failCount} 个API`)
    }
    await loadApiList()
  } catch (error: any) {
    console.error('批量启用失败:', error)
    ElMessage.error('批量启用失败: ' + (error.message || '网络错误'))
  } finally {
    if (loadingInstance) loadingInstance.close()
  }
}

const batchDisable = async (): Promise<void> => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请先选择要禁用的API')
    return
  }

  let loadingInstance: { close: () => void } | null = null
  try {
    loadingInstance = ElLoading.service({
      text: `正在禁用 ${selectedApis.value.length} 个API...`,
      background: 'rgba(0, 0, 0, 0.7)'
    })

    const results = await Promise.all(
      selectedApis.value.map((api: ApiItem) => apiProxy.updateApi(String(api.id), { status: 'inactive' }))
    )
    const successCount = results.filter(r => r?.success).length
    const failCount = results.length - successCount
    if (successCount > 0) {
      ElMessage.success(`成功禁用 ${successCount} 个API`)
    }
    if (failCount > 0) {
      ElMessage.error(`禁用失败 ${failCount} 个API`)
    }
    await loadApiList()
  } catch (error: any) {
    console.error('批量禁用失败:', error)
    ElMessage.error('批量禁用失败: ' + (error.message || '网络错误'))
  } finally {
    if (loadingInstance) loadingInstance.close()
  }
}

const batchDelete = async (): Promise<void> => {
  let loadingInstance: { close: () => void } | null = null
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedApis.value.length} 个API吗？`, '确认删除', {
      type: 'warning'
    })
    
    loadingInstance = ElLoading.service({
      text: '正在删除...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const promises = selectedApis.value.map(api => 
      apiProxy.deleteApi(String(api.id))
    )
    await Promise.all(promises)
    
    ElMessage.success('批量删除成功')
    await loadApiList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  } finally {
    if (loadingInstance) loadingInstance.close()
  }
}

const batchTest = async () => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请先选择要测试的API')
    return
  }
  
  let loadingInstance: { close: () => void } | null = null
  try {
    ElMessage.info('正在批量测试API...')
    loadingInstance = ElLoading.service({
      text: `正在测试 ${selectedApis.value.length} 个API，请稍候...`,
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const apiIds = selectedApis.value.map(api => String(api.id))
    const response = await apiProxy.batchTestApis(
      apiIds,
      { headers: {}, timeout: 30 }
    )
    
    if (response.success && response.data) {
      ElMessage.success('批量测试完成')
      const data = response.data
      const results = Array.isArray((data as any).results) ? (data as any).results : []
      const successCount = results.filter((r: any) => r && r.success).length
      const totalCount = (data as any).total_count ?? results.length
      const successNum = (data as any).success_count ?? successCount
      const avgTime = (data as any).average_response_time ?? 0
      const testTime = (data as any).test_time ?? ''
      
      ElMessageBox.alert(
        `<div style="text-align: left;">
          <p><strong>测试总数:</strong> ${totalCount}</p>
          <p><strong>成功数量:</strong> <span style="color: #67c23a;">${successNum}</span></p>
          <p><strong>失败数量:</strong> <span style="color: #f56c6c;">${totalCount - successNum}</span></p>
          <p><strong>平均响应时间:</strong> ${avgTime}ms</p>
          <p><strong>测试时间:</strong> ${testTime}</p>
        </div>`,
        '批量测试结果',
        {
          dangerouslyUseHTMLString: true,
          type: successNum === totalCount ? 'success' : 'warning'
        }
      )
    } else {
      ElMessage.error(response.message || '批量测试失败')
    }
  } catch (error: any) {
    console.error('批量测试失败:', error)
    ElMessage.error('批量测试失败: ' + (error.message || '网络错误'))
  } finally {
    if (loadingInstance) loadingInstance.close()
  }
}

const importApi = () => {
  // 触发隐藏的文件选择器
  if (importInputRef.value) {
    importInputRef.value.value = ''
    importInputRef.value.click()
  }
}

const exportApi = () => {
  // 根据当前筛选/选择构造导出参数
  const params: Record<string, any> = {}
  if (selectedSystemId.value) params.system_id = selectedSystemId.value
  if (selectedModuleId.value) params.module_id = selectedModuleId.value
  if (searchForm.keyword && searchForm.keyword.trim()) params.keyword = searchForm.keyword.trim()
  if (searchForm.method) params.method = searchForm.method
  apiProxy.exportApis(params).then((blob: Blob) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const fileNameParts: string[] = ['apis']
    if (params.system_id) fileNameParts.push(`sys_${params.system_id}`)
    if (params.module_id) fileNameParts.push(`mod_${params.module_id}`)
    const filename = `export_${fileNameParts.join('_')}.json`
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('导出开始，文件已生成')
  }).catch((error: any) => {
    console.error('导出API失败:', error)
    ElMessage.error(error?.message || '导出失败')
  })
}

const handleImportFile = async (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input?.files || input.files.length === 0) return
  const file = input.files[0]
  const formData = new FormData()
  formData.append('file', file)
  let loadingInstance: { close: () => void } | null = null
  try {
    loadingInstance = ElLoading.service({
      text: '正在导入API，请稍候...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    const resp = await apiProxy.importApis(formData)
    if (resp.success) {
      ElMessage.success(resp.message || '导入成功')
      // 导入成功后刷新列表
      await loadApiList()
    } else {
      ElMessage.error(resp.message || '导入失败')
    }
  } catch (error: any) {
    console.error('导入API失败:', error)
    ElMessage.error(error?.message || '导入失败')
  } finally {
    if (loadingInstance) loadingInstance.close()
    // 重置 input 值，确保下次同一文件也能触发 change
    if (importInputRef.value) importInputRef.value.value = ''
  }
}

// 数据初始化函数
const initializeData = () => {
  // 确保所有响应式数据都正确初始化
  if (!Array.isArray(apiList.value)) {
    apiList.value = []
  }
  if (!Array.isArray(selectedApis.value)) {
    selectedApis.value = []
  }
  if (!Array.isArray(systemList.value)) {
    systemList.value = []
  }
  if (!Array.isArray(moduleList.value)) {
    moduleList.value = []
  }
  if (!Array.isArray(systemTreeData.value)) {
    systemTreeData.value = []
  }
}

// 生命周期
onMounted(async () => {
  // 初始化数据
  initializeData()
  pageLoading.value = true
  try {
    await loadSystemList() // 只加载系统和模块，不预加载API列表
  } finally {
    // 页面级loading在系统/模块加载完成后立即关闭
    pageLoading.value = false
  }

  // 从URL参数中读取系统和模块ID（在pageLoading关闭后执行）
  const { systemId, moduleId } = route.query
  const sysId = systemId ? String(systemId) : ''
  const modId = moduleId ? String(moduleId) : ''

  // 校验systemId是否存在于系统列表
  const systemExists = sysId && Array.isArray(systemList.value) && systemList.value.some(s => String(s.id) === sysId)
  // 校验moduleId是否存在且属于该systemId
  const moduleExists = modId && Array.isArray(moduleList.value) && moduleList.value.some(m => String(m.id) === modId && String(m.system_id) === sysId)

  if (systemExists) {
    selectedSystemId.value = sysId
    if (modId && moduleExists) {
      selectedModuleId.value = modId
    } else {
      // URL中的moduleId无效时，移除moduleId，避免后端报错
      selectedModuleId.value = ''
      router.replace({ path: route.path, query: { systemId: sysId } })
    }
    // 在页面级loading关闭后开始API列表加载（表格级loading）
    await loadApiList()
  } else if (sysId) {
    // URL中的systemId在当前系统列表中不存在，清理并提示
    ElMessage.warning('URL中的系统不存在，已重置为未选择状态')
    selectedSystemId.value = ''
    selectedModuleId.value = ''
    router.replace({ path: route.path })
  }
})

// 组件卸载时清理定时器，避免内存泄漏和意外重试
onUnmounted(() => {
  if (retryTimerId.value) {
    clearTimeout(retryTimerId.value)
    retryTimerId.value = null
  }
})

const handleTreeRefresh = async () => {
  pageLoading.value = true
  try {
    // 使用统一树接口刷新数据
    await loadSystemList()
    ElMessage.success('系统与模块树刷新成功')
  } catch (error: unknown) {
    console.error('刷新系统树失败:', error)
    ElMessage.error('刷新系统与模块树失败')
  } finally {
    pageLoading.value = false
  }
}
</script>

<style scoped>
.api-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: white;
  padding: 24px 32px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  z-index: 10;
}

.header-content h1 {
  margin: 0 0 6px 0;
  font-size: 28px;
  color: #303133;
  font-weight: 600;
  background: linear-gradient(135deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-content p {
  margin: 0;
  color: #606266;
  font-size: 15px;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  gap: 16px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  gap: 16px;
  padding: 16px;
}

.left-panel {
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.left-panel:hover {
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.12);
}



.right-panel {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
  min-width: 0;
}

.right-panel:hover {
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.12);
}

.search-section {
  padding: 20px;
  border-bottom: 1px solid #f0f2f5;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.api-list-container {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
  color: #909399;
}

.empty-state .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #606266;
  font-weight: 500;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.api-name {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: center;
  background: #fafbfc;
}

.batch-actions {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 1000;
  backdrop-filter: blur(10px);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 响应式布局优化 */
@media (max-width: 1200px) {
  .left-panel {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .main-content {
    flex-direction: column;
    gap: 12px;
  }
  .left-panel,
  .right-panel {
    width: 100%;
  }
  .left-panel {
    max-width: 100%;
  }
}
</style>