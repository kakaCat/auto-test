<template>
  <div class="scenario-management">
    <div class="page-header">
      <div class="header-content">
        <h1>场景管理</h1>
        <p>创建和管理测试场景，支持接口编排、并行/顺序执行</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建场景
        </el-button>
        <el-button @click="importScenario">
          <el-icon><Upload /></el-icon>
          导入场景
        </el-button>
      </div>
    </div>
    
    <!-- 场景统计 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总场景数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.active }}</div>
          <div class="stat-label">活跃场景</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.success }}</div>
          <div class="stat-label">成功执行</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon failed">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.failed }}</div>
          <div class="stat-label">执行失败</div>
        </div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索场景名称或描述"
          clearable
          @input="handleSearch"
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.type"
          placeholder="执行类型"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option 
            v-for="type in executionTypeOptions" 
            :key="type.value" 
            :label="type.label" 
            :value="type.value" 
          />
        </el-select>
        
        <el-select
          v-model="searchForm.status"
          placeholder="状态"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option 
            v-for="status in scenarioStatusOptions" 
            :key="status.value" 
            :label="status.label" 
            :value="status.value" 
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
    
    <!-- 场景列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="scenarioList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="场景名称" min-width="150">
          <template #default="{ row }">
            <div class="scenario-name">
              <span class="name">{{ row.name }}</span>
              <el-tag v-if="row.version" size="small" type="info">
                v{{ row.version }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="执行类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="apiCount" label="接口数量" width="80" />
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
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
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="text" @click="viewScenario(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="text" @click="editScenario(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="text" @click="executeScenario(row)">
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button type="text" @click="copyScenario(row)">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button type="text" @click="deleteScenario(row)" style="color: var(--danger-color)">
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
    <div v-if="selectedScenarios.length > 0" class="batch-actions">
      <span>已选择 {{ selectedScenarios.length }} 项</span>
      <el-button @click="batchExecute">批量执行</el-button>
      <el-button @click="batchEnable">批量启用</el-button>
      <el-button @click="batchDisable">批量禁用</el-button>
      <el-button type="danger" @click="batchDelete">批量删除</el-button>
    </div>
    
    <!-- 创建场景对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建场景"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="场景名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入场景名称" />
        </el-form-item>
        
        <el-form-item label="执行类型" prop="type">
          <el-radio-group v-model="createForm.type">
            <el-radio 
              v-for="type in executionTypeOptions" 
              :key="type.value" 
              :label="type.value"
            >
              {{ type.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="场景描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入场景描述"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-tag
            v-for="tag in createForm.tags"
            :key="tag"
            closable
            @close="removeTag(tag)"
            style="margin-right: 8px"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="tagInputVisible"
            ref="tagInputRef"
            v-model="tagInputValue"
            size="small"
            style="width: 100px"
            @keyup.enter="addTag"
            @blur="addTag"
          />
          <el-button
            v-else
            size="small"
            @click="showTagInput"
          >
            + 添加标签
          </el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createScenario">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import scenarioApi from '@/api/scenario'
import {
  executionTypeOptions,
  scenarioStatusOptions,
  defaultSearchForm,
  defaultPagination,
  defaultStats,
  defaultCreateForm,
  createFormRules,
  scenarioTableColumns,
  getTypeLabel,
  getTypeColor,
  getStatusLabel,
  getStatusColor,
  getProgressColor,
  formatTime
} from './data/index'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const createDialogVisible = ref(false)
const scenarioList = ref([])
const selectedScenarios = ref([])
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref()

// 统计数据
const stats = ref({ ...defaultStats })

// 搜索表单
const searchForm = reactive({ ...defaultSearchForm })

// 分页
const pagination = reactive({ ...defaultPagination })

// 创建表单
const createForm = reactive({ ...defaultCreateForm })

// 创建表单验证规则
const createRules = createFormRules

const createFormRef = ref()



// 显示创建对话框
const showCreateDialog = () => {
  resetCreateForm()
  createDialogVisible.value = true
}

// 重置创建表单
const resetCreateForm = () => {
  Object.assign(createForm, { ...defaultCreateForm })
  createFormRef.value?.clearValidate()
}

// 显示标签输入
const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

// 添加标签
const addTag = () => {
  const tag = tagInputValue.value.trim()
  if (tag && !createForm.tags.includes(tag)) {
    createForm.tags.push(tag)
  }
  tagInputValue.value = ''
  tagInputVisible.value = false
}

// 删除标签
const removeTag = (tag) => {
  const index = createForm.tags.indexOf(tag)
  if (index > -1) {
    createForm.tags.splice(index, 1)
  }
}

// 创建场景
const createScenario = async () => {
  try {
    await createFormRef.value.validate()
    
    // 这里调用API创建场景
    console.log('创建场景:', createForm)
    
    ElMessage.success('场景创建成功')
    createDialogVisible.value = false
    
    // 跳转到场景编辑页面
    router.push('/scenario-management/edit/new')
  } catch (error) {
    console.error('创建失败:', error)
  }
}

// 查看场景
const viewScenario = (row) => {
  router.push(`/scenario-management/view/${row.id}`)
}

// 编辑场景
const editScenario = (row) => {
  router.push(`/scenario-management/edit/${row.id}`)
}

// 执行场景
const executeScenario = async (row) => {
  try {
    ElMessage.info('开始执行场景...')
    
    // 这里调用执行API
    console.log('执行场景:', row)
    
    // 跳转到执行结果页面
    router.push(`/scenario-management/execution/${row.id}`)
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  }
}

// 复制场景
const copyScenario = async (row) => {
  try {
    // 这里调用复制API
    console.log('复制场景:', row)
    
    ElMessage.success('场景复制成功')
    loadScenarioList()
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 删除场景
const deleteScenario = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除场景 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用删除API
    console.log('删除场景:', row)
    
    ElMessage.success('删除成功')
    loadScenarioList()
  } catch (error) {
    // 用户取消删除
  }
}

// 选择变更
const handleSelectionChange = (selection) => {
  selectedScenarios.value = selection
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadScenarioList()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    type: '',
    status: ''
  })
  handleSearch()
}

// 分页变更
const handlePageChange = (page) => {
  pagination.page = page
  loadScenarioList()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadScenarioList()
}

// 批量操作
const batchExecute = () => {
  console.log('批量执行:', selectedScenarios.value)
  ElMessage.success('批量执行已启动')
}

const batchEnable = () => {
  console.log('批量启用:', selectedScenarios.value)
  ElMessage.success('批量启用成功')
}

const batchDisable = () => {
  console.log('批量禁用:', selectedScenarios.value)
  ElMessage.success('批量禁用成功')
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedScenarios.value.length} 个场景吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('批量删除:', selectedScenarios.value)
    ElMessage.success('批量删除成功')
    loadScenarioList()
  } catch (error) {
    // 用户取消删除
  }
}

// 导入场景
const importScenario = () => {
  ElMessage.info('导入功能开发中...')
}

// 加载场景列表
const loadScenarioList = async () => {
  loading.value = true
  try {
    const response = await scenarioApi.getScenarioList({
      keyword: searchForm.keyword,
      type: searchForm.type,
      status: searchForm.status,
      page: pagination.currentPage,
      pageSize: pagination.pageSize
    })
    
    if (response.success) {
      scenarioList.value = response.data || []
      pagination.total = response.total || 0
    } else {
      ElMessage.error(response.message || '加载场景列表失败')
    }
  } catch (error) {
    console.error('加载场景列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await scenarioApi.getStats()
    if (response.success) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
  loadScenarioList()
})
</script>

<style scoped>
.scenario-management {
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
.stat-icon.active { background: var(--success-color); }
.stat-icon.success { background: #67c23a; }
.stat-icon.failed { background: var(--danger-color); }

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

.scenario-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 500;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .scenario-management {
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
}
</style>