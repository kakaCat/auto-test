<template>
  <div class="system-integration-page">
    <!-- 页面头部 -->
    <PageHeader
      :title="pageConfig.title"
      :description="pageConfig.description"
      :actions="pageConfig.actions"
      @action="handleHeaderAction"
    />
    
    <!-- 统计卡片 -->
    <StatisticsCards :statistics="statistics" />
    
    <!-- 搜索表单 -->
    <SearchForm
      v-model="searchForm"
      :config="searchFormConfig"
      @search="handleSearch"
      @reset="handleReset"
    />
    
    <!-- 数据表格 -->
    <IntegrationTable
      :data="tableData"
      :config="tableConfig"
      :loading="loading"
      :pagination="pagination"
      @selection-change="handleSelectionChange"
      @action="handleTableAction"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
    
    <!-- 批量操作面板 -->
    <ActionPanel
      :selected-count="selectedItems.length"
      :actions="batchActions"
      @action="handleBatchAction"
      @clear-selection="handleClearSelection"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 导入页面专用组件
import PageHeader from './components/PageHeader.vue'
import StatisticsCards from './components/StatisticsCards.vue'
import SearchForm from './components/SearchForm.vue'
import IntegrationTable from './components/IntegrationTable.vue'
import ActionPanel from './components/ActionPanel.vue'

// 导入数据配置
import { pageConfig, batchActions, DEFAULT_PAGINATION } from './data/constants'
import { searchFormConfig, tableConfig } from './data/table-config'
import type { Integration } from './data/table-config'
import { mockIntegrations, mockStatistics } from './data/mock-data'

// 响应式数据
const loading = ref(false)
const tableData = ref<Integration[]>([])
const selectedItems = ref<Integration[]>([])
const statistics = ref(mockStatistics)

// 搜索表单
const searchForm = reactive({
  name: '',
  type: '',
  status: '',
  environment: ''
})

// 分页配置
const pagination = reactive({
  ...DEFAULT_PAGINATION,
  pageSizes: [10, 20, 50, 100],
  layout: 'total, sizes, prev, pager, next, jumper'
})

// 页面头部操作处理
const handleHeaderAction = async (action: string): Promise<void> => {
  switch (action) {
    case 'create':
      await createIntegration()
      break
    case 'import':
      await importConfiguration()
      break
    case 'refresh':
      await loadIntegrationList()
      break
    default:
      console.log('未知操作:', action)
  }
}

// 搜索处理
const handleSearch = async (searchParams: Record<string, any>): Promise<void> => {
  loading.value = true
  try {
    // 模拟搜索API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    let filteredData = [...mockIntegrations]
    
    if (searchParams.name) {
      filteredData = filteredData.filter(item => 
        item.name.toLowerCase().includes(searchParams.name.toLowerCase())
      )
    }
    
    if (searchParams.type) {
      filteredData = filteredData.filter(item => item.type === searchParams.type)
    }
    
    if (searchParams.status) {
      filteredData = filteredData.filter(item => item.status === searchParams.status)
    }
    
    if (searchParams.environment) {
      filteredData = filteredData.filter(item => item.environment === searchParams.environment)
    }
    
    tableData.value = filteredData
    pagination.total = filteredData.length
    pagination.currentPage = 1
    
    ElMessage.success('搜索完成')
  } catch (error) {
    ElMessage.error('搜索失败')
    console.error('搜索错误:', error)
  } finally {
    loading.value = false
  }
}

// 重置搜索
const handleReset = async (): Promise<void> => {
  await loadIntegrationList()
  ElMessage.info('已重置搜索条件')
}

// 表格选择变化
const handleSelectionChange = (selection: Integration[]): void => {
  selectedItems.value = selection
}

// 表格行操作
const handleTableAction = async (action: string, row: Integration): Promise<void> => {
  switch (action) {
    case 'view':
      await viewIntegration(row)
      break
    case 'edit':
      await editIntegration(row)
      break
    case 'start':
      await startIntegration(row)
      break
    case 'stop':
      await stopIntegration(row)
      break
    case 'sync':
      await syncIntegration(row)
      break
    case 'delete':
      await deleteIntegration(row)
      break
    default:
      console.log('未知操作:', action, row)
  }
}

// 批量操作
const handleBatchAction = async (action: string): Promise<void> => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要操作的项目')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要对选中的 ${selectedItems.value.length} 个项目执行"${action}"操作吗？`,
      '批量操作确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    
    // 模拟批量操作API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success(`批量${action}操作完成`)
    selectedItems.value = []
    await loadIntegrationList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`批量${action}操作失败`)
      console.error('批量操作错误:', error)
    }
  } finally {
    loading.value = false
  }
}

// 清除选择
const handleClearSelection = (): void => {
  selectedItems.value = []
}

// 分页大小变化
const handleSizeChange = (size: number): void => {
  pagination.pageSize = size
  pagination.currentPage = 1
  // 同步统一字段
  ;(pagination as any).size = size
  ;(pagination as any).page = 1
  loadIntegrationList()
}

// 当前页变化
const handleCurrentChange = (page: number): void => {
  pagination.currentPage = page
  // 同步统一字段
  ;(pagination as any).page = page
  loadIntegrationList()
}

// 业务方法
const createIntegration = async (): Promise<void> => {
  ElMessage.info('打开创建集成对话框')
}

const importConfiguration = async (): Promise<void> => {
  ElMessage.info('打开导入配置对话框')
}

const viewIntegration = async (integration: Integration): Promise<void> => {
  ElMessage.info(`查看集成: ${integration.name}`)
}

const editIntegration = async (integration: Integration): Promise<void> => {
  ElMessage.info(`编辑集成: ${integration.name}`)
}

const startIntegration = async (integration: Integration): Promise<void> => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(`启动集成 "${integration.name}" 成功`)
    await loadIntegrationList()
  } catch (error) {
    ElMessage.error('启动集成失败')
  } finally {
    loading.value = false
  }
}

const stopIntegration = async (integration: Integration): Promise<void> => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(`停止集成 "${integration.name}" 成功`)
    await loadIntegrationList()
  } catch (error) {
    ElMessage.error('停止集成失败')
  } finally {
    loading.value = false
  }
}

const syncIntegration = async (integration: Integration): Promise<void> => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success(`同步集成 "${integration.name}" 成功`)
    await loadIntegrationList()
  } catch (error) {
    ElMessage.error('同步集成失败')
  } finally {
    loading.value = false
  }
}

const deleteIntegration = async (integration: Integration): Promise<void> => {
  try {
    await ElMessageBox.confirm(
      `确定要删除集成 "${integration.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 500))
    
    ElMessage.success(`删除集成 "${integration.name}" 成功`)
    await loadIntegrationList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除集成失败')
    }
  } finally {
    loading.value = false
  }
}

const loadIntegrationList = async (): Promise<void> => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))
    
    tableData.value = mockIntegrations
    pagination.total = mockIntegrations.length
    
    // 更新统计数据
    statistics.value = mockStatistics
  } catch (error) {
    ElMessage.error('加载集成列表失败')
    console.error('加载错误:', error)
  } finally {
    loading.value = false
  }
}

// 页面初始化
onMounted(() => {
  loadIntegrationList()
})
</script>

<style scoped>
.system-integration-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .system-integration-page {
    padding: 10px;
  }
}
</style>