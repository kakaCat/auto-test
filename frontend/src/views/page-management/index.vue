<template>
  <div class="page-management">
    <!-- 
      页面头部区域
      - 页面标题和描述信息
      - 主要操作按钮（新增、导入、导出）
    -->
    <div class="page-header">
      <div class="header-content">
        <h1>页面管理</h1>
        <p>左侧选择系统，右侧管理对应的页面和页面中的API调用关系</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showAddPageDialog">
          <el-icon><DocumentAdd /></el-icon>
          新增页面
        </el-button>
        <el-button @click="importPages">
          <el-icon><Upload /></el-icon>
          导入页面
        </el-button>
        <el-button @click="exportPages">
          <el-icon><Download /></el-icon>
          导出页面
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
        - 系统树形结构
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
          label-key="label"
          children-key="children"
          @node-click="handleSystemNodeClick"
          @refresh="handleTreeRefresh"
        />
      </div>

      <!-- 
        右侧页面管理主面板
        - 页面列表展示
        - 页面详情和API关联管理
        - 搜索和筛选功能
      -->
      <div class="right-panel">
        <!-- 搜索和筛选区域 -->
        <div class="search-section">
          <div class="search-form">
            <el-form :model="searchForm" inline>
              <el-form-item label="关键词">
                <el-input
                  v-model="searchForm.keyword"
                  placeholder="搜索页面名称或描述"
                  clearable
                  @keyup.enter="searchPages"
                  style="width: 200px"
                />
              </el-form-item>
              <el-form-item label="页面类型">
                <el-select
                  v-model="searchForm.pageType"
                  placeholder="选择页面类型"
                  clearable
                  style="width: 150px"
                >
                  <el-option label="页面" value="page" />
                  <el-option label="弹框" value="modal" />
                  <el-option label="抽屉" value="drawer" />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select
                  v-model="searchForm.status"
                  placeholder="选择状态"
                  clearable
                  style="width: 120px"
                >
                  <el-option label="活跃" value="active" />
                  <el-option label="非活跃" value="inactive" />
                  <el-option label="草稿" value="draft" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="searchPages">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
                <el-button @click="resetSearch">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 页面列表区域 -->
        <div class="pages-section">
          <div class="section-header">
            <h3>页面列表</h3>
            <div class="section-actions">
              <el-button size="small" @click="refreshPages">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <!-- 页面表格列表 -->
          <div class="pages-table" v-loading="loading">
            <el-table
              :data="filteredPageList"
              stripe
              @selection-change="handleSelectionChange"
              @row-click="selectPage"
              highlight-current-row
            >
              <el-table-column type="selection" width="55" />
              
              <el-table-column label="页面名称" prop="name" min-width="150">
                <template #default="{ row }">
                  <div class="page-name-cell">
                    <span class="page-name">{{ row.name }}</span>
                    <el-tag v-if="row.status === 'inactive'" type="info" size="small">已禁用</el-tag>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column label="类型" prop="page_type" width="100">
                <template #default="{ row }">
                  <el-tag :type="getPageTypeColor(row.page_type)" size="small">
                    {{ row.page_type_display || row.page_type }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column label="路由" prop="route_path" min-width="200" show-overflow-tooltip>
                <template #default="{ row }">
                  <code v-if="row.route_path" class="route-path">{{ row.route_path }}</code>
                  <span v-else class="no-route">-</span>
                </template>
              </el-table-column>
              
              <el-table-column label="状态" prop="status" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusColor(row.status)" size="small">
                    {{ row.status_display || row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column label="系统/模块" prop="system_name" width="150" show-overflow-tooltip>
                <template #default="{ row }">
                  <span>{{ row.system_name || '-' }}</span>
                </template>
              </el-table-column>
              
              <el-table-column label="API数量" prop="api_count" width="100" align="center">
                <template #default="{ row }">
                  <el-badge :value="row.api_count || 0" :max="99" type="primary">
                    <el-icon><Connection /></el-icon>
                  </el-badge>
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click.stop="editPage(row)">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button type="text" size="small" @click.stop="managePageApis(row)">
                    <el-icon><Connection /></el-icon>
                    API管理
                  </el-button>
                  <el-dropdown @command="handlePageAction" @click.stop>
                    <el-button type="text" size="small">
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item :command="'copy-' + row.id">
                          <el-icon><CopyDocument /></el-icon>
                          复制页面
                        </el-dropdown-item>
                        <el-dropdown-item :command="'delete-' + row.id" divided>
                          <el-icon><Delete /></el-icon>
                          删除页面
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="filteredPageList.length > 0">
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

          <!-- 空状态 -->
          <div v-if="!loading && filteredPageList.length === 0" class="empty-state">
            <el-empty description="暂无页面数据">
              <el-button type="primary" @click="showAddPageDialog">创建第一个页面</el-button>
            </el-empty>
          </div>
        </div>

        <!-- 批量操作区域 -->
        <div class="batch-actions" v-if="selectedPages.length > 0">
          <div class="batch-info">
            <span>已选择 {{ selectedPages.length }} 个页面</span>
          </div>
          <div class="batch-buttons">
            <el-button type="success" @click="batchEnable">
              <el-icon><Check /></el-icon>
              批量启用
            </el-button>
            <el-button type="warning" @click="batchDisable">
              <el-icon><Close /></el-icon>
              批量禁用
            </el-button>
            <el-button type="primary" @click="batchExport">
              <el-icon><Download /></el-icon>
              批量导出
            </el-button>
            <el-button type="danger" @click="batchDelete">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>

        <!-- 页面API关联管理区域 -->
        <div class="page-apis-section" v-if="selectedPage">
          <div class="section-header">
            <h3>页面API关联 - {{ selectedPage.name }}</h3>
            <div class="section-actions">
              <el-button type="primary" size="small" @click="showAddApiDialog">
                <el-icon><Plus /></el-icon>
                添加API
              </el-button>
            </div>
          </div>

          <!-- API关联列表 -->
          <div class="apis-list">
            <el-table :data="selectedPage.apis" style="width: 100%">
              <el-table-column prop="api_name" label="API名称" width="200">
                <template #default="{ row }">
                  <div class="api-info">
                    <el-tag :type="getMethodColor(row.api_method)" size="small">
                      {{ row.api_method }}
                    </el-tag>
                    <span class="api-name">{{ row.api_name || '未知API' }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="api_path" label="API路径" width="250">
                <template #default="{ row }">
                  <code class="api-path">{{ row.api_path || '-' }}</code>
                </template>
              </el-table-column>
              
              <el-table-column prop="execution_type" label="执行类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.execution_type === 'parallel' ? 'success' : 'warning'" size="small">
                    {{ row.execution_type_display }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column prop="execution_order" label="执行顺序" width="100" />
              
              <el-table-column prop="trigger_action" label="触发动作" width="120" />
              
              <el-table-column prop="api_purpose" label="API作用" width="150">
                <template #default="{ row }">
                  <span class="api-purpose">{{ row.api_purpose || '-' }}</span>
                </template>
              </el-table-column>
              
              <el-table-column prop="success_action" label="成功动作" width="150">
                <template #default="{ row }">
                  <span class="success-action">{{ row.success_action || '-' }}</span>
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click="editPageApi(row)">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button type="text" size="small" @click="deletePageApi(row)" class="danger">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </div>

    <!-- 页面表单对话框 -->
    <PageFormDialog
      v-model:visible="pageDialogVisible"
      :page="currentPage"
      :mode="dialogMode"
      :systems="systemList"
      @success="handlePageSuccess"
    />

    <!-- 页面API关联表单对话框 -->
    <PageApiFormDialog
      v-model:visible="pageApiDialogVisible"
      :page-api="currentPageApi"
      :page="selectedPage"
      :mode="apiDialogMode"
      :apis="availableApis"
      @success="handlePageApiSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  DocumentAdd,
  Upload,
  Download,
  Refresh,
  MoreFilled,
  Edit,
  Delete,
  CopyDocument,
  Plus,
  Link,
  Connection
} from '@element-plus/icons-vue'

// 组件导入
import SystemTree from '@/components/SystemTree.vue'
import PageFormDialog from './components/PageFormDialog.vue'
import PageApiFormDialog from './components/PageApiFormDialog.vue'

// API导入
import { pageApi, pageUtils } from '@/api/page-management.js'
import unifiedApi from '@/api/unified-api'

// 直接使用统一API
const apiProxy = unifiedApi

// 路由实例
const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const systemTreeRef = ref()

// 系统相关数据
const systemList = ref([])
const moduleList = ref([])
const systemTreeData = ref([])
const selectedSystemId = ref(null)
const selectedModuleId = ref('')

// 页面相关数据
const pageList = ref([])
const selectedPageId = ref(null)
const selectedPage = ref(null)
const selectedPages = ref([])
const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  pageType: '',
  status: ''
})

// 对话框状态
const pageDialogVisible = ref(false)
const pageApiDialogVisible = ref(false)
const dialogMode = ref('create') // create, edit
const apiDialogMode = ref('create') // create, edit
const currentPage = ref(null)
const currentPageApi = ref(null)

// API相关数据
const availableApis = ref([])

// 计算属性
const filteredPageList = computed(() => {
  let list = pageList.value
  
  // 根据选中的系统或模块筛选
  if (selectedModuleId.value) {
    // 如果选中了模块，按模块筛选
    list = list.filter(page => page.module_id === selectedModuleId.value)
  } else if (selectedSystemId.value) {
    // 如果只选中了系统，按系统筛选
    list = list.filter(page => page.system_id === selectedSystemId.value)
  }
  
  // 根据搜索条件筛选
  if (searchForm.keyword) {
    const keyword = searchForm.keyword.toLowerCase()
    list = list.filter(page => 
      page.name.toLowerCase().includes(keyword) ||
      (page.description && page.description.toLowerCase().includes(keyword))
    )
  }
  
  if (searchForm.pageType) {
    list = list.filter(page => page.page_type === searchForm.pageType)
  }
  
  if (searchForm.status) {
    list = list.filter(page => page.status === searchForm.status)
  }
  
  return list
})

// 生命周期
onMounted(async () => {
  try {
    // 先加载系统和模块数据
    await Promise.all([
      loadSystemList(),
      loadModuleList()
    ])
    // 构建系统树
    buildSystemTree()
    
    // 从URL参数中读取系统和模块ID
    const { systemId, moduleId } = route.query
    if (systemId) {
      selectedSystemId.value = systemId
      if (moduleId) {
        selectedModuleId.value = moduleId
      }
    }
    
    // 加载其他数据
    loadPageList()
    loadAvailableApis()
  } catch (error) {
    console.error('初始化页面数据失败:', error)
  }
})

// 方法
const loadSystemList = async () => {
  try {
    // 使用新的按分类获取启用系统接口
    const response = await apiProxy.system.getEnabledListByCategory('frontend')
    if (response.success) {
      systemList.value = response.data || []
    } else {
      throw new Error(response.message || '获取启用系统列表失败')
    }
  } catch (error) {
    console.error('加载启用系统列表失败:', error)
    ElMessage.error('加载启用系统列表失败')
    systemList.value = []
  }
}

const loadModuleList = async () => {
  try {
    // 使用新的启用模块接口
    const response = await apiProxy.module.getEnabledList()
    if (response.success) {
      moduleList.value = response.data || []
    } else {
      throw new Error(response.message || '获取启用模块列表失败')
    }
  } catch (error) {
    console.error('加载启用模块列表失败:', error)
    ElMessage.error('加载启用模块列表失败')
    moduleList.value = []
  }
}

const buildSystemTree = () => {
  try {
    const systems = Array.isArray(systemList.value) ? systemList.value : []
    const modules = Array.isArray(moduleList.value) ? moduleList.value : []
    
    const treeData = []
    
    // 添加"全部"节点
    treeData.push({
      id: 'all',
      label: '全部',
      type: 'all',
      children: []
    })
    
    // 构建系统树
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
  } catch (error) {
    console.error('构建系统树失败:', error)
    ElMessage.error('构建系统树失败')
    systemTreeData.value = []
  }
}

const loadPageList = async () => {
  try {
    loading.value = true
    const response = await pageApi.getPages()
    if (response.success) {
      pageList.value = response.data
    } else {
      throw new Error(response.message || '获取页面列表失败')
    }
  } catch (error) {
    console.error('加载页面列表失败:', error)
    ElMessage.error('加载页面列表失败')
  } finally {
    loading.value = false
  }
}

const loadAvailableApis = async () => {
  try {
    const response = await unifiedApi.getApis()
    if (response.success) {
      availableApis.value = response.data
    } else {
      throw new Error(response.message || '获取API列表失败')
    }
  } catch (error) {
    console.error('加载API列表失败:', error)
  }
}

const handleSystemNodeClick = (data) => {
  if (data.type === 'system') {
    selectedSystemId.value = data.id
    selectedModuleId.value = ''
    selectedPageId.value = null
    selectedPage.value = null
  } else if (data.type === 'module') {
    selectedSystemId.value = data.systemId
    selectedModuleId.value = data.id
    selectedPageId.value = null
    selectedPage.value = null
  } else {
    // 全部系统
    selectedSystemId.value = ''
    selectedModuleId.value = ''
    selectedPageId.value = null
    selectedPage.value = null
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
  
  // 重新加载页面列表
  loadPageList()
}

const selectPage = (page) => {
  selectedPageId.value = page.id
  selectedPage.value = page
}

const searchPages = () => {
  // 搜索逻辑已在计算属性中实现
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.pageType = ''
  searchForm.status = ''
}

const refreshPages = () => {
  loadPageList()
}

const handleTreeRefresh = async () => {
  try {
    // 重新加载系统和模块列表
    await Promise.all([
      loadSystemList(),
      loadModuleList()
    ])
    // 重新构建系统树
    buildSystemTree()
    ElMessage.success('系统和模块树刷新成功')
  } catch (error) {
    console.error('刷新系统树失败:', error)
    ElMessage.error('刷新系统和模块树失败')
  }
}

const showAddPageDialog = () => {
  currentPage.value = null
  dialogMode.value = 'create'
  pageDialogVisible.value = true
}

const showAddApiDialog = () => {
  currentPageApi.value = null
  apiDialogMode.value = 'create'
  pageApiDialogVisible.value = true
}

const handlePageAction = (command) => {
  const [action, pageId] = command.split('-')
  const page = pageList.value.find(p => p.id === parseInt(pageId))
  
  switch (action) {
    case 'edit':
      editPage(page)
      break
    case 'copy':
      copyPage(page)
      break
    case 'delete':
      deletePage(page)
      break
  }
}

const editPage = (page) => {
  currentPage.value = page
  dialogMode.value = 'edit'
  pageDialogVisible.value = true
}

const copyPage = (page) => {
  currentPage.value = { ...page, name: page.name + ' (副本)' }
  dialogMode.value = 'create'
  pageDialogVisible.value = true
}

const deletePage = async (page) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除页面 "${page.name}" 吗？此操作将同时删除该页面的所有API关联。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await pageApi.deletePage(page.id)
    if (response.success) {
      ElMessage.success('删除页面成功')
      loadPageList()
      
      if (selectedPageId.value === page.id) {
        selectedPageId.value = null
        selectedPage.value = null
      }
    } else {
      throw new Error(response.message || '删除页面失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除页面失败:', error)
      ElMessage.error('删除页面失败')
    }
  }
}

const editPageApi = (pageApi) => {
  currentPageApi.value = pageApi
  apiDialogMode.value = 'edit'
  pageApiDialogVisible.value = true
}

const deletePageApi = async (pageApiItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这个API关联吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await pageApi.deletePageApi(pageApiItem.id)
    if (response.success) {
      ElMessage.success('删除API关联成功')
      loadPageList()
    } else {
      throw new Error(response.message || '删除API关联失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除API关联失败:', error)
      ElMessage.error('删除API关联失败')
    }
  }
}

const handlePageSuccess = () => {
  pageDialogVisible.value = false
  loadPageList()
  ElMessage.success(dialogMode.value === 'create' ? '创建页面成功' : '更新页面成功')
}

const handlePageApiSuccess = () => {
  pageApiDialogVisible.value = false
  loadPageList()
  ElMessage.success(apiDialogMode.value === 'create' ? '添加API关联成功' : '更新API关联成功')
}

const importPages = () => {
  ElMessage.info('导入功能开发中...')
}

const exportPages = () => {
  ElMessage.info('导出功能开发中...')
}

// 工具方法
const getPageTypeColor = (type) => {
  return pageUtils.getPageTypeColor(type)
}

const getStatusColor = (status) => {
  return pageUtils.getPageStatusColor(status)
}

const getMethodColor = (method) => {
  return pageUtils.getMethodColor(method)
}

// 表格选择变化
const handleSelectionChange = (selection) => {
  selectedPages.value = selection
}

// 分页相关方法
const handleSizeChange = (size) => {
  pagination.value.size = size
  pagination.value.page = 1
  loadPageList()
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadPageList()
}

// 批量操作方法
const batchEnable = async () => {
  try {
    const pageIds = selectedPages.value.map(page => page.id)
    const response = await pageApi.batchUpdatePageStatus(pageIds, 'active')
    if (response.success) {
      ElMessage.success('批量启用成功')
      loadPageList()
      selectedPages.value = []
    } else {
      throw new Error(response.message || '批量启用失败')
    }
  } catch (error) {
    console.error('批量启用失败:', error)
    ElMessage.error('批量启用失败')
  }
}

const batchDisable = async () => {
  try {
    const pageIds = selectedPages.value.map(page => page.id)
    const response = await pageApi.batchUpdatePageStatus(pageIds, 'inactive')
    if (response.success) {
      ElMessage.success('批量禁用成功')
      loadPageList()
      selectedPages.value = []
    } else {
      throw new Error(response.message || '批量禁用失败')
    }
  } catch (error) {
    console.error('批量禁用失败:', error)
    ElMessage.error('批量禁用失败')
  }
}

const batchExport = () => {
  ElMessage.info('批量导出功能开发中...')
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedPages.value.length} 个页面吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const pageIds = selectedPages.value.map(page => page.id)
    const response = await pageApi.batchDeletePages(pageIds)
    if (response.success) {
      ElMessage.success('批量删除成功')
      loadPageList()
      selectedPages.value = []
      
      // 如果当前选中的页面被删除，清空选择
      if (selectedPageId.value && pageIds.includes(selectedPageId.value)) {
        selectedPageId.value = null
        selectedPage.value = null
      }
    } else {
      throw new Error(response.message || '批量删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}
</script>

<style scoped>
.page-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.header-content h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 300px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow: hidden;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-section {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.pages-section {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.page-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-card.active {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.page-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.page-meta {
  display: flex;
  gap: 8px;
}

.card-content {
  color: #606266;
  font-size: 14px;
}

.page-description {
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.page-route,
.api-count {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 16px;
}

.batch-info {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}

.page-apis-section {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 24px;
  max-height: 400px;
  overflow: auto;
}

.api-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.api-name {
  font-weight: 500;
}

.api-path {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.danger {
  color: #f56c6c !important;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}
</style>