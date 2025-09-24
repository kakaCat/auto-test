<template>
  <div class="workflow-orchestration">
    <div class="page-header">
      <div class="header-content">
        <h1>工作流编排</h1>
        <p>可视化工作流设计和编排，支持多种节点类型和连接方式</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="createWorkflow">
          <el-icon><Plus /></el-icon>
          新建工作流
        </el-button>
        <el-button @click="importWorkflow">
          <el-icon><Upload /></el-icon>
          导入工作流
        </el-button>
        <el-button @click="showTemplates">
          <el-icon><Document /></el-icon>
          模板库
        </el-button>
      </div>
    </div>
    
    <!-- 工作流统计 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><Share /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总工作流</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon running">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.running }}</div>
          <div class="stat-label">运行中</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon nodes">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.nodes }}</div>
          <div class="stat-label">总节点数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon executions">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.executions }}</div>
          <div class="stat-label">执行次数</div>
        </div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索工作流名称或描述"
          clearable
          @input="handleSearch"
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="状态"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option 
            v-for="status in workflowStatusOptions" 
            :key="status.value" 
            :label="status.label" 
            :value="status.value" 
          />
        </el-select>
        
        <el-select
          v-model="searchForm.category"
          placeholder="分类"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option 
            v-for="category in workflowCategoryOptions" 
            :key="category.value" 
            :label="category.label" 
            :value="category.value" 
          />
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
    
    <!-- 工作流列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="workflowList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="工作流名称" min-width="150">
          <template #default="{ row }">
            <div class="workflow-name">
              <span class="name">{{ row.name }}</span>
              <el-tag v-if="row.version" size="small" type="info">
                v{{ row.version }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryColor(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="nodeCount" label="节点数" width="80" />
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <div class="status-indicator">
              <el-tag :type="getStatusColor(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
              <div v-if="row.status === 'running'" class="running-indicator"></div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="executionCount" label="执行次数" width="100" />
        
        <el-table-column prop="successRate" label="成功率" width="100">
          <template #default="{ row }">
            <div class="success-rate">
              <span>{{ row.successRate }}%</span>
              <el-progress
                :percentage="row.successRate"
                :stroke-width="4"
                :show-text="false"
                :color="getProgressColor(row.successRate)"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="lastExecutionTime" label="最后执行" width="150">
          <template #default="{ row }">
            {{ formatTime(row.lastExecutionTime) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="creator" label="创建者" width="100" />
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="text" @click="viewWorkflow(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="text" @click="editWorkflow(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              v-if="row.status !== 'running'"
              type="text" 
              @click="executeWorkflow(row)"
            >
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button 
              v-else
              type="text" 
              @click="stopWorkflow(row)"
              style="color: var(--warning-color)"
            >
              <el-icon><VideoPause /></el-icon>
              停止
            </el-button>
            <el-button type="text" @click="copyWorkflow(row)">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button type="text" @click="deleteWorkflow(row)" style="color: var(--danger-color)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
    
    <!-- 批量操作 -->
    <div v-if="selectedWorkflows.length > 0" class="batch-actions">
      <span>已选择 {{ selectedWorkflows.length }} 项</span>
      <el-button @click="batchExecute">批量执行</el-button>
      <el-button @click="batchStop">批量停止</el-button>
      <el-button @click="batchPublish">批量发布</el-button>
      <el-button type="danger" @click="batchDelete">批量删除</el-button>
    </div>
    
    <!-- 模板库对话框 -->
    <el-dialog
      v-model="templatesDialogVisible"
      title="工作流模板库"
      width="800px"
    >
      <div class="templates-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          @click="useTemplate(template)"
        >
          <div class="template-icon">
            <el-icon>
              <component :is="template.icon" />
            </el-icon>
          </div>
          <div class="template-content">
            <h3>{{ template.name }}</h3>
            <p>{{ template.description }}</p>
            <div class="template-meta">
              <span class="node-count">{{ template.nodeCount }} 个节点</span>
              <span class="usage-count">使用 {{ template.usageCount }} 次</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="templatesDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import workflowApi from '@/api/workflow'
import {
  workflowStatusOptions,
  workflowCategoryOptions,
  defaultSearchForm,
  defaultPagination,
  defaultStats,
  workflowTableColumns,
  getStatusColor,
  getStatusLabel,
  getProgressColor,
  formatTime,
  workflowTemplates
} from './data/index'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const templatesDialogVisible = ref(false)
const workflowList = ref([])
const selectedWorkflows = ref([])

// 统计数据
const stats = ref({ ...defaultStats })

// 搜索表单
const searchForm = reactive({ ...defaultSearchForm })

// 分页
const pagination = reactive({ ...defaultPagination })

// 模板数据
const templates = ref(workflowTemplates)

// 获取分类标签
const getCategoryLabel = (category) => {
  const labelMap = {
    'api-test': 'API测试',
    'data-processing': '数据处理',
    'auto-deploy': '自动化部署',
    'monitoring': '监控告警',
    'data-sync': '数据同步',
    'other': '其他'
  }
  return labelMap[category] || category
}

// 获取分类颜色
const getCategoryColor = (category) => {
  const colorMap = {
    'api-test': 'primary',
    'data-processing': 'success',
    'auto-deploy': 'warning',
    'monitoring': 'danger',
    'data-sync': 'info',
    'other': 'info'
  }
  return colorMap[category] || 'info'
}

// 创建工作流
const createWorkflow = () => {
  router.push('/workflow-orchestration/designer/new')
}

// 查看工作流
const viewWorkflow = (row) => {
  router.push(`/workflow-orchestration/view/${row.id}`)
}

// 编辑工作流
const editWorkflow = (row) => {
  router.push(`/workflow-orchestration/designer/${row.id}`)
}

// 执行工作流
const executeWorkflow = async (row) => {
  try {
    ElMessage.info('开始执行工作流...')
    
    // 这里调用执行API
    console.log('执行工作流:', row)
    
    // 更新状态
    row.status = 'running'
    
    ElMessage.success('工作流执行已启动')
    
    // 跳转到执行监控页面
    router.push(`/workflow-orchestration/monitor/${row.id}`)
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  }
}

// 停止工作流
const stopWorkflow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止工作流 "${row.name}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用停止API
    console.log('停止工作流:', row)
    
    // 更新状态
    row.status = 'stopped'
    
    ElMessage.success('工作流已停止')
  } catch (error) {
    // 用户取消停止
  }
}

// 复制工作流
const copyWorkflow = async (row) => {
  try {
    // 这里调用复制API
    console.log('复制工作流:', row)
    
    ElMessage.success('工作流复制成功')
    loadWorkflowList()
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 删除工作流
const deleteWorkflow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除工作流 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用删除API
    console.log('删除工作流:', row)
    
    ElMessage.success('删除成功')
    loadWorkflowList()
  } catch (error) {
    // 用户取消删除
  }
}

// 选择变更
const handleSelectionChange = (selection) => {
  selectedWorkflows.value = selection
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadWorkflowList()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    category: ''
  })
  handleSearch()
}

// 分页变更
const handlePageChange = (page) => {
  pagination.page = page
  loadWorkflowList()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadWorkflowList()
}

// 批量操作
const batchExecute = () => {
  console.log('批量执行:', selectedWorkflows.value)
  ElMessage.success('批量执行已启动')
}

const batchStop = () => {
  console.log('批量停止:', selectedWorkflows.value)
  ElMessage.success('批量停止成功')
}

const batchPublish = () => {
  console.log('批量发布:', selectedWorkflows.value)
  ElMessage.success('批量发布成功')
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedWorkflows.value.length} 个工作流吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('批量删除:', selectedWorkflows.value)
    ElMessage.success('批量删除成功')
    loadWorkflowList()
  } catch (error) {
    // 用户取消删除
  }
}

// 导入工作流
const importWorkflow = () => {
  ElMessage.info('导入功能开发中...')
}

// 显示模板库
const showTemplates = () => {
  templatesDialogVisible.value = true
}

// 使用模板
const useTemplate = (template) => {
  templatesDialogVisible.value = false
  router.push(`/workflow-orchestration/designer/new?template=${template.id}`)
}

// 加载工作流列表
const loadWorkflowList = async () => {
  loading.value = true
  try {
    const response = await workflowApi.getWorkflowList({
      keyword: searchForm.keyword,
      status: searchForm.status,
      category: searchForm.category,
      page: pagination.currentPage,
      pageSize: pagination.pageSize
    })
    
    if (response.success) {
      workflowList.value = response.data || []
      pagination.total = response.total || 0
    } else {
      ElMessage.error(response.message || '加载工作流列表失败')
    }
  } catch (error) {
    console.error('加载工作流列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await workflowApi.getStats()
    if (response.success) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
  loadWorkflowList()
})
</script>

<style scoped>
.workflow-orchestration {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.header-content p {
  color: var(--text-color-regular);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total { background: var(--primary-color); }
.stat-icon.running { background: var(--success-color); }
.stat-icon.nodes { background: var(--warning-color); }
.stat-icon.executions { background: #722ed1; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-regular);
}

.search-section {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.table-section {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
}

.workflow-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 500;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.running-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.success-rate {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.success-rate span {
  font-size: 12px;
  color: var(--text-color-regular);
}

.pagination-wrapper {
  padding: 16px;
  display: flex;
  justify-content: center;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 12px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.template-card {
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
}

.template-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.template-content {
  flex: 1;
}

.template-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.template-content p {
  font-size: 14px;
  color: var(--text-color-regular);
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-color-placeholder);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .workflow-orchestration {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-form > * {
    width: 100% !important;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
}
</style>