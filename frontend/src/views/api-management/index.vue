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
      <div class="right-panel">
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
            
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button type="text" @click="viewApi(row)">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button type="text" @click="showEditApiDialog(row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="text" @click="mockApi(row)" style="color: var(--el-color-success)">
                  <el-icon><DataBoard /></el-icon>
                  Mock
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
      v-model="mockGeneratorVisible"
      :api-info="currentMockApi || {}"
      @mock-generated="handleMockGenerated"
    />
    <!-- 测试抽屉 -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { 
  DocumentAdd, Upload, Download, Search, Refresh, ArrowDown, ArrowRight,
  View, Edit, Delete, Check, Close, Monitor, Document,
  Link, Cloudy, Phone, Connection, DataBoard, Cpu, Platform
} from '@element-plus/icons-vue'
import unifiedApi from '@/api/unified-api'
import ApiFormDialog from './components/ApiFormDialog.vue'
import MockDataGenerator from './components/MockDataGenerator.vue'
import SystemTree from '@/components/SystemTree.vue'

// 直接使用统一API
const apiProxy = unifiedApi.apiManagementApi
// 补充分域代理，避免将 system/module 误挂到 apiManagementApi 下
const systemApi = unifiedApi.system
const moduleApi = unifiedApi.module

// 路由实例
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增API')
const systemTreeRef = ref()
const apiFormDialogRef = ref()
// Mock数据生成器相关
const mockGeneratorVisible = ref(false)
const currentMockApi = ref(null)
// 已移除测试抽屉功能

// 系统相关数据
const systemList = ref([])
const moduleList = ref([])
const systemTreeData = ref([])
const selectedSystemId = ref('')
const selectedModuleId = ref('')

// API列表数据 - 确保始终是数组
const apiList = ref([])
const selectedApis = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  method: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const form = reactive({
  id: '',
  name: '',
  description: '',
  url: '',
  method: 'POST',
  system_id: '',
  module_id: '',
  enabled: true,
  tags: [],
  metadata: {}
})



// 计算属性
// 安全的API列表，确保始终返回数组
const safeApiList = computed(() => {
  if (!Array.isArray(apiList.value)) {
    console.warn('apiList不是数组格式，重置为空数组')
    return []
  }
  return apiList.value
})

const filteredApiList = computed(() => {
  let list = apiList.value
  
  // 根据选中的系统或模块筛选
  if (selectedModuleId.value) {
    // 如果选中了模块，按模块筛选
    list = list.filter(api => api.module_id === selectedModuleId.value)
  } else if (selectedSystemId.value) {
    // 如果只选中了系统，按系统筛选
    list = list.filter(api => api.system_id === selectedSystemId.value)
  }
  
  // 按关键词搜索
  if (searchForm.keyword) {
    const keyword = searchForm.keyword.toLowerCase()
    list = list.filter(api => 
      (api.name ? api.name.toLowerCase() : '').includes(keyword) ||
      api.description?.toLowerCase().includes(keyword) ||
      api.url?.toLowerCase().includes(keyword)
    )
  }
  
  // 按方法筛选
  if (searchForm.method) {
    list = list.filter(api => api.method === searchForm.method)
  }
  
  return list
})

// 方法
const loadSystemList = async (retryCount = 0) => {
  try {
    // 使用新的按分类获取启用系统接口
    const response = await systemApi.getEnabledListByCategory('backend')
    // 兼容两种返回结构：数组 或 { success, data }
    const data = Array.isArray(response) ? response : (response?.data ?? [])
    if (Array.isArray(data)) {
      systemList.value = data
      await loadModuleList() // 加载系统后立即加载模块
      buildSystemTree()
    } else {
      console.warn('系统列表数据格式不正确:', data)
      systemList.value = []
      throw new Error('获取启用系统列表失败')
    }
  } catch (error) {
    console.error('加载启用系统列表失败:', error)
    systemList.value = [] // 确保在错误时设置为空数组
    
    if (retryCount < 2) {
      ElMessage.warning(`加载启用系统列表失败，正在重试... (${retryCount + 1}/3)`)
      setTimeout(() => loadSystemList(retryCount + 1), 1000)
    } else {
      ElMessage.error('加载启用系统列表失败: ' + (error.message || '网络连接错误'))
      ElMessageBox.confirm(
        '加载启用系统列表失败，是否重新尝试？',
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

const loadModuleList = async (retryCount = 0) => {
  try {
    // 使用新的启用模块接口
    const response = await moduleApi.getEnabledList()
    // 兼容两种返回结构：数组 或 { success, data }
    const data = Array.isArray(response) ? response : (response?.data ?? [])
    if (Array.isArray(data)) {
      moduleList.value = data
    } else {
      console.warn('模块列表数据格式不正确:', data)
      moduleList.value = []
      throw new Error('获取启用模块列表失败')
    }
  } catch (error) {
    console.error('加载启用模块列表失败:', error)
    moduleList.value = [] // 确保在错误时设置为空数组
    
    if (retryCount < 2) {
      ElMessage.warning(`加载启用模块列表失败，正在重试... (${retryCount + 1}/3)`)
      setTimeout(() => loadModuleList(retryCount + 1), 1000)
    } else {
      ElMessage.error('加载启用模块列表失败: ' + (error.message || '网络连接错误'))
    }
  }
}

const buildSystemTree = async () => {
  try {
    const response = await systemApi.getEnabledListByCategory('backend')
    if (response.success && response.data) {
      const systems = Array.isArray(response.data) ? response.data : []
      const modules = Array.isArray(moduleList.value) ? moduleList.value : []
      
      const treeData = []
      
      systems.forEach(system => {
        // 获取该系统下的模块
        const systemModules = modules.filter(module => 
          module && system && module.system_id === system.id
        )
        
        const systemNode = {
          id: system.id,
          label: system.name,
          type: 'system',
          category: system.category,
          children: []
        }
        
        // 添加模块作为系统的子节点
        systemModules.forEach(module => {
          const moduleNode = {
            id: module.id,
            label: module.name,
            type: 'module',
            systemId: system.id
          }
          systemNode.children.push(moduleNode)
        })
        
        treeData.push(systemNode)
      })
      
      systemTreeData.value = treeData
    }
  } catch (error) {
    console.error('获取backend系统列表失败:', error)
    systemTreeData.value = []
  }
}

const loadApiList = async (retryCount = 0) => {
  try {
    loading.value = true
    const params = {}
    
    // 只传递有值的参数，避免空字符串导致后端验证失败
    if (selectedSystemId.value) {
      params.system_id = selectedSystemId.value
    }
    if (selectedModuleId.value) {
      params.module_id = selectedModuleId.value
    }
    if (searchForm.keyword && searchForm.keyword.trim()) {
      params.keyword = searchForm.keyword.trim()
    }
    if (searchForm.method) {
      params.method = searchForm.method
    }
    params.enabled_only = false
    
    const response = await apiProxy.getApis(params)
    if (response.success) {
      // 确保数据是数组格式
      const data = response.data
      if (Array.isArray(data)) {
        // 映射后端 path 字段到前端使用的 url 字段，避免列表中URL为空
        apiList.value = data.map(api => ({
          ...api,
          url: api.url ?? api.path ?? ''
        }))
      } else if (data && typeof data === 'object' && Array.isArray(data.items)) {
        // 处理分页数据格式，同步字段映射
        apiList.value = data.items.map(api => ({
          ...api,
          url: api.url ?? api.path ?? ''
        }))
      } else {
        console.warn('API数据格式异常:', data)
        apiList.value = []
      }
      pagination.total = apiList.value.length
    } else {
      throw new Error(response.message || '获取API列表失败')
    }
  } catch (error) {
    console.error('加载API列表失败:', error)
    
    if (retryCount < 2) {
      ElMessage.warning(`加载API列表失败，正在重试... (${retryCount + 1}/3)`)
      setTimeout(() => loadApiList(retryCount + 1), 1000)
    } else {
      ElMessage.error('加载API列表失败: ' + (error.message || '网络连接错误'))
      // 显示空状态而不是错误对话框，因为这是更频繁的操作
      apiList.value = []
      pagination.total = 0
    }
  } finally {
    loading.value = false
  }
}

const handleSystemNodeClick = (data) => {
  if (data.type === 'system') {
    selectedSystemId.value = data.id
    selectedModuleId.value = ''
  } else if (data.type === 'module') {
    selectedSystemId.value = data.systemId
    selectedModuleId.value = data.id
  }
  
  // 更新URL参数
  const query = {}
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
const getSystemIcon = (category) => {
  const iconMap = {
    'backend': Cloudy,      // 后端服务使用云图标
    'frontend': Monitor,    // 前端应用使用显示器图标
    'web': Link,
    'api': Cloudy,
    'mobile': Phone,
    'desktop': Monitor,
    'database': DataBoard,
    'middleware': Connection,
    'hardware': Cpu,
    'other': Platform
  }
  return iconMap[category] || Platform
}

const getSystemTreeIcon = (data) => {
  if (data.type === 'system') {
    // 根据系统分类返回对应图标
    return getSystemIcon(data.category)
  } else if (data.type === 'module') {
    return Document // 模块使用文件图标
  } else {
    return Document
  }
}

const handleSearch = () => {
  loadApiList()
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.method = ''
  selectedSystemId.value = ''
  loadApiList()
}

const handleSelectionChange = (selection) => {
  // 确保selection是数组
  if (Array.isArray(selection)) {
    selectedApis.value = selection
  } else {
    console.warn('选择数据格式异常:', selection)
    selectedApis.value = []
  }
}

const handleApiStatusChange = async (api) => {
  try {
    await apiProxy.updateApi(api.id, { enabled: api.enabled })
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('更新API状态失败:', error)
    ElMessage.error('更新状态失败')
    api.enabled = !api.enabled // 回滚状态
  }
}

const getMethodType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return types[method] || 'info'
}

const showAddApiDialog = () => {
  dialogTitle.value = '新增API'
  resetForm(true) // 保留选中的系统和模块信息
  dialogVisible.value = true
}

const showEditApiDialog = async (api) => {
  dialogTitle.value = '编辑API'
  Object.assign(form, api)
  dialogVisible.value = true
}

const viewApi = (api) => {
  return showEditApiDialog(api)
}


const deleteApi = async (api) => {
  try {
    await ElMessageBox.confirm('确定要删除这个API吗？', '确认删除', {
      type: 'warning'
    })
    
    await apiProxy.deleteApi(api.id)
    ElMessage.success('删除成功')
    loadApiList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除API失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const mockApi = (api) => {
  currentMockApi.value = api
  mockGeneratorVisible.value = true
}

const handleMockGenerated = (mockData) => {
  console.log('Mock数据已生成:', mockData)
  ElMessage.success('Mock数据生成成功')
  mockGeneratorVisible.value = false
}

const saveApi = async (formData) => {
  try {
    if (formData.id) {
      await apiProxy.updateApi(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await apiProxy.createApi(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadApiList()
    
    // 重置子组件的保存状态
    if (apiFormDialogRef.value) {
      apiFormDialogRef.value.resetSavingState()
    }
  } catch (error) {
    console.error('保存API失败:', error)
    
    // 显示详细错误信息
    let errorMessage = '保存失败'
    
    // 处理业务错误（success: false的情况）
    if (error.message && error.message !== '请求失败') {
      errorMessage = error.message
    } else if (error.response && error.response.data) {
      if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.message) {
        errorMessage = error.response.data.message
      } else if (error.response.data.detail) {
        errorMessage = JSON.stringify(error.response.data.detail)
      } else {
        errorMessage = JSON.stringify(error.response.data)
      }
    }
    
    ElMessage.error(errorMessage)
    
    // 保存失败时也要重置子组件的保存状态
    if (apiFormDialogRef.value) {
      apiFormDialogRef.value.resetSavingState()
    }
  }
}

// 处理对话框取消事件
const handleDialogCancel = () => {
  dialogVisible.value = false
}

const resetForm = (preserveSelection = false) => {
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
    for (const key in resetData) {
      if (form.hasOwnProperty(key)) {
        form[key] = resetData[key]
      }
    }
  }
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadApiList()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadApiList()
}

const batchEnable = async () => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请先选择要启用的API')
    return
  }

  try {
    const loadingInstance = ElLoading.service({
      text: `正在启用 ${selectedApis.value.length} 个API...`,
      background: 'rgba(0, 0, 0, 0.7)'
    })

    const promises = selectedApis.value.map(api => 
      apiProxy.updateApi(api.id, { enabled: true })
    )
    await Promise.all(promises)
    
    loadingInstance.close()
    ElMessage.success(`成功启用 ${selectedApis.value.length} 个API`)
    loadApiList()
  } catch (error) {
    console.error('批量启用失败:', error)
    ElMessage.error('批量启用失败: ' + (error.message || '网络错误'))
  }
}

const batchDisable = async () => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请先选择要禁用的API')
    return
  }

  try {
    const loadingInstance = ElLoading.service({
      text: `正在禁用 ${selectedApis.value.length} 个API...`,
      background: 'rgba(0, 0, 0, 0.7)'
    })

    const promises = selectedApis.value.map(api => 
      apiProxy.updateApi(api.id, { enabled: false })
    )
    await Promise.all(promises)
    
    loadingInstance.close()
    ElMessage.success(`成功禁用 ${selectedApis.value.length} 个API`)
    loadApiList()
  } catch (error) {
    console.error('批量禁用失败:', error)
    ElMessage.error('批量禁用失败: ' + (error.message || '网络错误'))
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedApis.value.length} 个API吗？`, '确认删除', {
      type: 'warning'
    })
    
    const loadingInstance = ElLoading.service({
      text: '正在删除...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const promises = selectedApis.value.map(api => 
      apiProxy.deleteApi(api.id)
    )
    await Promise.all(promises)
    
    loadingInstance.close()
    ElMessage.success('批量删除成功')
    loadApiList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const batchTest = async () => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请先选择要测试的API')
    return
  }
  
  try {
    ElMessage.info('正在批量测试API...')
    const loadingInstance = ElLoading.service({
      text: `正在测试 ${selectedApis.value.length} 个API，请稍候...`,
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const apiIds = selectedApis.value.map(api => api.id)
    const response = await apiProxy.batchTestApis({
      api_ids: apiIds,
      headers: {},
      timeout: 30
    })
    
    loadingInstance.close()
    
    if (response.success) {
      ElMessage.success('批量测试完成')
      const results = response.data.results || []
      const successCount = results.filter(r => r.success).length
      const failCount = results.length - successCount
      
      ElMessageBox.alert(
        `<div style="text-align: left;">
          <p><strong>测试总数:</strong> ${response.data.total_count}</p>
          <p><strong>成功数量:</strong> <span style="color: #67c23a;">${response.data.success_count}</span></p>
          <p><strong>失败数量:</strong> <span style="color: #f56c6c;">${response.data.total_count - response.data.success_count}</span></p>
          <p><strong>平均响应时间:</strong> ${response.data.average_response_time}ms</p>
          <p><strong>测试时间:</strong> ${response.data.test_time}</p>
        </div>`,
        '批量测试结果',
        {
          dangerouslyUseHTMLString: true,
          type: response.data.success_count === response.data.total_count ? 'success' : 'warning'
        }
      )
    } else {
      ElMessage.error(response.message || '批量测试失败')
    }
  } catch (error) {
    console.error('批量测试失败:', error)
    ElMessage.error('批量测试失败: ' + (error.message || '网络错误'))
  }
}

const importApi = () => {
  // 导入API功能
  console.log('导入API')
}

const exportApi = () => {
  // 导出API功能
  console.log('导出API')
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
  
  await loadSystemList() // 只加载系统和模块，不预加载API列表
  
  // 从URL参数中读取系统和模块ID
  const { systemId, moduleId } = route.query
  const sysId = systemId ? String(systemId) : ''
  const modId = moduleId ? String(moduleId) : ''

  // 校验systemId是否存在于系统列表
  const systemExists = sysId && Array.isArray(systemList.value) && systemList.value.some(s => String(s.id) === sysId)
  // 校验moduleId是否存在且属于该systemId
  const moduleExists = modId && Array.isArray(moduleList.value) && moduleList.value.some(m => String(m.id) === modId && String(m.system_id ?? m.systemId) === sysId)

  if (systemExists) {
    selectedSystemId.value = sysId
    if (modId && moduleExists) {
      selectedModuleId.value = modId
    } else {
      // URL中的moduleId无效时，移除moduleId，避免后端报错
      selectedModuleId.value = ''
      router.replace({ path: route.path, query: { systemId: sysId } })
    }
    await loadApiList()
  } else if (sysId) {
    // URL中的systemId在当前系统列表中不存在，清理并提示
    ElMessage.warning('URL中的系统不存在，已重置为未选择状态')
    selectedSystemId.value = ''
    selectedModuleId.value = ''
    router.replace({ path: route.path })
  }
})

const handleTreeRefresh = async () => {
  try {
    await loadSystemList()
    await loadModuleList()
    await buildSystemTree()
    ElMessage.success('系统和模块树刷新成功')
  } catch (error) {
    console.error('刷新系统树失败:', error)
    ElMessage.error('刷新系统和模块树失败')
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
  overflow: hidden;
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
</style>