<template>
  <div class="ai-scenario-execution">
    <div class="page-header">
      <div class="header-content">
        <h1>AI场景执行</h1>
        <p>智能场景执行代理，支持参数增强、场景解析和自动化执行</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="createExecution"
        >
          <el-icon><Plus /></el-icon>
          新建执行
        </el-button>
        <el-button @click="showTemplates">
          <el-icon><Document /></el-icon>
          场景模板
        </el-button>
        <el-button @click="showSettings">
          <el-icon><Setting /></el-icon>
          AI配置
        </el-button>
      </div>
    </div>
    
    <!-- AI执行统计 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.total }}
          </div>
          <div class="stat-label">
            总执行次数
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon running">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.running }}
          </div>
          <div class="stat-label">
            执行中
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.success }}
          </div>
          <div class="stat-label">
            成功执行
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon enhanced">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">
            {{ stats.enhanced }}
          </div>
          <div class="stat-label">
            AI增强次数
          </div>
        </div>
      </div>
    </div>
    
    <!-- 快速执行区域 -->
    <div class="quick-execution">
      <div class="quick-header">
        <h3>快速执行</h3>
        <el-button
          type="text"
          @click="showQuickHelp"
        >
          <el-icon><QuestionFilled /></el-icon>
          使用说明
        </el-button>
      </div>
      
      <div class="execution-form">
        <div class="form-row">
          <el-select
            v-model="quickForm.scenario"
            placeholder="选择场景"
            style="width: 200px"
            @change="onScenarioChange"
          >
            <el-option
              v-for="scenario in scenarios"
              :key="scenario.id"
              :label="scenario.name"
              :value="scenario.id"
            />
          </el-select>
          
          <el-select
            v-model="quickForm.enhanceMode"
            placeholder="增强模式"
            style="width: 150px"
          >
            <el-option
              label="智能增强"
              value="smart"
            />
            <el-option
              label="基础增强"
              value="basic"
            />
            <el-option
              label="无增强"
              value="none"
            />
          </el-select>
          
          <el-button
            type="primary"
            :loading="quickExecuting"
            :disabled="!quickForm.scenario"
            @click="quickExecute"
          >
            <el-icon><VideoPlay /></el-icon>
            立即执行
          </el-button>
        </div>
        
        <div class="form-row">
          <el-input
            v-model="quickForm.parameters"
            type="textarea"
            :rows="3"
            placeholder="输入执行参数（JSON格式）或自然语言描述，AI将自动解析和增强"
            style="flex: 1"
          />
        </div>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-form">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索执行记录"
          clearable
          style="width: 300px"
          @input="handleSearch"
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
            label="执行中"
            value="running"
          />
          <el-option
            label="成功"
            value="success"
          />
          <el-option
            label="失败"
            value="failed"
          />
          <el-option
            label="已取消"
            value="cancelled"
          />
        </el-select>
        
        <el-select
          v-model="searchForm.enhanceMode"
          placeholder="增强模式"
          clearable
          style="width: 120px"
          @change="handleSearch"
        >
          <el-option
            label="智能增强"
            value="smart"
          />
          <el-option
            label="基础增强"
            value="basic"
          />
          <el-option
            label="无增强"
            value="none"
          />
        </el-select>
        
        <el-date-picker
          v-model="searchForm.dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          style="width: 300px"
          @change="handleSearch"
        />
        
        <el-button
          type="primary"
          @click="handleSearch"
        >
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>
    
    <!-- 执行记录列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="executionList"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column
          type="selection"
          width="55"
        />
        
        <el-table-column
          prop="id"
          label="执行ID"
          width="100"
        />
        
        <el-table-column
          prop="scenarioName"
          label="场景名称"
          min-width="150"
        >
          <template #default="{ row }">
            <div class="scenario-info">
              <span class="name">{{ row.scenarioName }}</span>
              <el-tag
                v-if="row.aiEnhanced"
                size="small"
                type="success"
              >
                <el-icon><MagicStick /></el-icon>
                AI增强
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="enhanceMode"
          label="增强模式"
          width="100"
        >
          <template #default="{ row }">
            <el-tag
              :type="getEnhanceModeColor(row.enhanceMode)"
              size="small"
            >
              {{ getEnhanceModeLabel(row.enhanceMode) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="status"
          label="状态"
          width="100"
        >
          <template #default="{ row }">
            <div class="status-indicator">
              <el-tag
                :type="getStatusColor(row.status)"
                size="small"
              >
                {{ getStatusLabel(row.status) }}
              </el-tag>
              <div
                v-if="row.status === 'running'"
                class="running-indicator"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="progress"
          label="进度"
          width="120"
        >
          <template #default="{ row }">
            <div class="progress-info">
              <el-progress
                :percentage="row.progress"
                :stroke-width="6"
                :show-text="false"
                :color="getProgressColor(row.status)"
              />
              <span class="progress-text">{{ row.progress }}%</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="duration"
          label="执行时长"
          width="100"
        >
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        
        <el-table-column
          prop="enhancedParams"
          label="增强参数"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <div class="enhanced-params">
              <span v-if="row.enhancedParams">{{ row.enhancedParams }}</span>
              <span
                v-else
                class="no-data"
              >-</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="result"
          label="执行结果"
          min-width="150"
        >
          <template #default="{ row }">
            <div class="result-info">
              <span
                v-if="row.result"
                class="result-text"
              >{{ row.result }}</span>
              <span
                v-else
                class="no-data"
              >-</span>
              <el-button
                v-if="row.resultDetails"
                type="text"
                size="small"
                @click="viewResult(row)"
              >
                查看详情
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="startTime"
          label="开始时间"
          width="150"
        >
          <template #default="{ row }">
            {{ formatTime(row.startTime) }}
          </template>
        </el-table-column>
        
        <el-table-column
          prop="executor"
          label="执行者"
          width="100"
        />
        
        <el-table-column
          label="操作"
          width="200"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              type="text"
              @click="viewExecution(row)"
            >
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button 
              v-if="row.status === 'running'"
              type="text" 
              style="color: var(--warning-color)"
              @click="stopExecution(row)"
            >
              <el-icon><VideoPause /></el-icon>
              停止
            </el-button>
            <el-button 
              v-else
              type="text" 
              @click="reExecute(row)"
            >
              <el-icon><Refresh /></el-icon>
              重新执行
            </el-button>
            <el-button
              type="text"
              style="color: var(--danger-color)"
              @click="deleteExecution(row)"
            >
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
    <div
      v-if="selectedExecutions.length > 0"
      class="batch-actions"
    >
      <span>已选择 {{ selectedExecutions.length }} 项</span>
      <el-button @click="batchStop">
        批量停止
      </el-button>
      <el-button @click="batchReExecute">
        批量重新执行
      </el-button>
      <el-button
        type="danger"
        @click="batchDelete"
      >
        批量删除
      </el-button>
    </div>
    
    <!-- 执行结果详情对话框 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="执行结果详情"
      width="800px"
    >
      <div
        v-if="currentResult"
        class="result-details"
      >
        <div class="result-section">
          <h4>基本信息</h4>
          <el-descriptions
            :column="2"
            border
          >
            <el-descriptions-item label="执行ID">
              {{ currentResult.id }}
            </el-descriptions-item>
            <el-descriptions-item label="场景名称">
              {{ currentResult.scenarioName }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusColor(currentResult.status)">
                {{ getStatusLabel(currentResult.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="执行时长">
              {{ formatDuration(currentResult.duration) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="result-section">
          <h4>AI增强信息</h4>
          <div class="enhanced-info">
            <p><strong>增强模式：</strong>{{ getEnhanceModeLabel(currentResult.enhanceMode) }}</p>
            <p><strong>原始参数：</strong></p>
            <pre class="code-block">{{ currentResult.originalParams }}</pre>
            <p><strong>增强后参数：</strong></p>
            <pre class="code-block">{{ currentResult.enhancedParams }}</pre>
          </div>
        </div>
        
        <div class="result-section">
          <h4>执行日志</h4>
          <div class="log-container">
            <pre class="log-content">{{ currentResult.logs }}</pre>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="resultDialogVisible = false">
          关闭
        </el-button>
        <el-button
          type="primary"
          @click="downloadResult"
        >
          下载报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const quickExecuting = ref(false)
const resultDialogVisible = ref(false)
const executionList = ref([])
const selectedExecutions = ref([])
const currentResult = ref(null)

// 统计数据
const stats = ref({
  total: 0,
  running: 0,
  success: 0,
  enhanced: 0
})

// 场景列表
const scenarios = ref([
  { id: 1, name: 'API接口测试' },
  { id: 2, name: '数据验证流程' },
  { id: 3, name: '业务流程测试' },
  { id: 4, name: '性能压测' }
])

// 快速执行表单
const quickForm = reactive({
  scenario: '',
  enhanceMode: 'smart',
  parameters: ''
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  enhanceMode: '',
  dateRange: []
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取增强模式标签
const getEnhanceModeLabel = (mode) => {
  const labelMap = {
    smart: '智能增强',
    basic: '基础增强',
    none: '无增强'
  }
  return labelMap[mode] || mode
}

// 获取增强模式颜色
const getEnhanceModeColor = (mode) => {
  const colorMap = {
    smart: 'primary',
    basic: 'success',
    none: 'info'
  }
  return colorMap[mode] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labelMap = {
    running: '执行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return labelMap[status] || status
}

// 获取状态颜色
const getStatusColor = (status) => {
  const colorMap = {
    running: 'primary',
    success: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return colorMap[status] || 'info'
}

// 获取进度条颜色
const getProgressColor = (status) => {
  const colorMap = {
    running: '#409eff',
    success: '#67c23a',
    failed: '#f56c6c',
    cancelled: '#e6a23c'
  }
  return colorMap[status] || '#909399'
}

// 格式化时长
const formatDuration = (duration) => {
  if (!duration) return '-'
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

// 场景变更
const onScenarioChange = (scenarioId) => {
  const scenario = scenarios.value.find(s => s.id === scenarioId)
  if (scenario) {
    // 可以根据场景预设一些参数
    console.log('选择场景:', scenario)
  }
}

// 快速执行
const quickExecute = async () => {
  if (!quickForm.scenario) {
    ElMessage.warning('请选择执行场景')
    return
  }
  
  quickExecuting.value = true
  try {
    // 这里调用AI场景执行API
    console.log('快速执行:', quickForm)
    
    ElMessage.success('执行已启动，正在进行AI参数增强...')
    
    // 模拟执行过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('执行完成')
    
    // 清空表单
    Object.assign(quickForm, {
      scenario: '',
      enhanceMode: 'smart',
      parameters: ''
    })
    
    // 刷新列表
    loadExecutionList()
  } catch (error) {
    console.error('执行失败:', error)
    ElMessage.error('执行失败')
  } finally {
    quickExecuting.value = false
  }
}

// 创建执行
const createExecution = () => {
  router.push('/ai-scenario-execution/create')
}

// 查看执行
const viewExecution = (row) => {
  router.push(`/ai-scenario-execution/view/${row.id}`)
}

// 查看结果
const viewResult = (row) => {
  currentResult.value = {
    ...row,
    originalParams: '{\n  "url": "https://api.example.com/users",\n  "method": "GET"\n}',
    logs: `[2024-01-15 10:30:00] 开始执行场景: ${row.scenarioName}
[2024-01-15 10:30:01] AI参数增强开始...
[2024-01-15 10:30:02] 检测到缺少认证头，自动添加Authorization
[2024-01-15 10:30:02] 优化请求参数格式
[2024-01-15 10:30:03] AI参数增强完成
[2024-01-15 10:30:03] 开始执行API请求
[2024-01-15 10:30:04] 请求成功，状态码: 200
[2024-01-15 10:30:04] 响应验证通过
[2024-01-15 10:30:05] 执行完成，结果: 成功`
  }
  resultDialogVisible.value = true
}

// 停止执行
const stopExecution = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止执行 "${row.scenarioName}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用停止API
    console.log('停止执行:', row)
    
    // 更新状态
    row.status = 'cancelled'
    
    ElMessage.success('执行已停止')
  } catch (error) {
    // 用户取消停止
  }
}

// 重新执行
const reExecute = async (row) => {
  try {
    // 这里调用重新执行API
    console.log('重新执行:', row)
    
    ElMessage.success('重新执行已启动')
    loadExecutionList()
  } catch (error) {
    console.error('重新执行失败:', error)
    ElMessage.error('重新执行失败')
  }
}

// 删除执行记录
const deleteExecution = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除执行记录 "${row.id}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里调用删除API
    console.log('删除执行记录:', row)
    
    ElMessage.success('删除成功')
    loadExecutionList()
  } catch (error) {
    // 用户取消删除
  }
}

// 选择变更
const handleSelectionChange = (selection) => {
  selectedExecutions.value = selection
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadExecutionList()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    status: '',
    enhanceMode: '',
    dateRange: []
  })
  handleSearch()
}

// 分页变更
const handlePageChange = (page) => {
  pagination.page = page
  loadExecutionList()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadExecutionList()
}

// 批量操作
const batchStop = () => {
  console.log('批量停止:', selectedExecutions.value)
  ElMessage.success('批量停止成功')
}

const batchReExecute = () => {
  console.log('批量重新执行:', selectedExecutions.value)
  ElMessage.success('批量重新执行已启动')
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedExecutions.value.length} 条执行记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('批量删除:', selectedExecutions.value)
    ElMessage.success('批量删除成功')
    loadExecutionList()
  } catch (error) {
    // 用户取消删除
  }
}

// 显示模板
const showTemplates = () => {
  ElMessage.info('场景模板功能开发中...')
}

// 显示设置
const showSettings = () => {
  ElMessage.info('AI配置功能开发中...')
}

// 显示快速帮助
const showQuickHelp = () => {
  ElMessage.info('使用说明功能开发中...')
}

// 下载结果
const downloadResult = () => {
  ElMessage.success('报告下载已开始')
}

// 加载执行列表
const loadExecutionList = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    executionList.value = [
      {
        id: 'EXE001',
        scenarioName: 'API接口测试',
        enhanceMode: 'smart',
        status: 'success',
        progress: 100,
        duration: 15000,
        enhancedParams: '{"url":"https://api.example.com/users","method":"GET","headers":{"Authorization":"Bearer xxx"}}',
        result: '测试通过，响应时间: 120ms',
        resultDetails: true,
        startTime: new Date(Date.now() - 1000 * 60 * 30),
        executor: '张三',
        aiEnhanced: true
      },
      {
        id: 'EXE002',
        scenarioName: '数据验证流程',
        enhanceMode: 'basic',
        status: 'running',
        progress: 65,
        duration: 8000,
        enhancedParams: '{"data_source":"database","validation_rules":["not_null","format_check"]}',
        result: '',
        resultDetails: false,
        startTime: new Date(Date.now() - 1000 * 60 * 8),
        executor: '李四',
        aiEnhanced: true
      },
      {
        id: 'EXE003',
        scenarioName: '业务流程测试',
        enhanceMode: 'smart',
        status: 'failed',
        progress: 45,
        duration: 12000,
        enhancedParams: '{"workflow_id":"WF001","test_data":{"user_id":123,"action":"purchase"}}',
        result: '执行失败：连接超时',
        resultDetails: true,
        startTime: new Date(Date.now() - 1000 * 60 * 60),
        executor: '王五',
        aiEnhanced: true
      },
      {
        id: 'EXE004',
        scenarioName: '性能压测',
        enhanceMode: 'none',
        status: 'success',
        progress: 100,
        duration: 45000,
        enhancedParams: '',
        result: '压测完成，TPS: 1200',
        resultDetails: true,
        startTime: new Date(Date.now() - 1000 * 60 * 120),
        executor: '赵六',
        aiEnhanced: false
      }
    ]
    
    pagination.total = 4
    
    // 更新统计数据
    stats.value = {
      total: 156,
      running: 3,
      success: 142,
      enhanced: 134
    }
  } catch (error) {
    console.error('加载执行列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadExecutionList()
})
</script>

<style scoped>
.ai-scenario-execution {
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
.stat-icon.running { background: var(--warning-color); }
.stat-icon.success { background: var(--success-color); }
.stat-icon.enhanced { background: #722ed1; }

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

.quick-execution {
  background: var(--bg-color-overlay);
  border: 1px solid var(--border-color-lighter);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.quick-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.quick-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.execution-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
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

.scenario-info {
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
  background: var(--primary-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-text {
  font-size: 12px;
  color: var(--text-color-regular);
  text-align: center;
}

.enhanced-params {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-text {
  font-size: 14px;
}

.no-data {
  color: var(--text-color-placeholder);
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

.result-details {
  max-height: 600px;
  overflow-y: auto;
}

.result-section {
  margin-bottom: 24px;
}

.result-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 12px 0;
}

.enhanced-info p {
  margin: 8px 0;
  color: var(--text-color-regular);
}

.code-block {
  background: var(--bg-color-page);
  border: 1px solid var(--border-color-lighter);
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: var(--text-color-primary);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 8px 0;
}

.log-container {
  background: #1e1e1e;
  border-radius: 4px;
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.log-content {
  color: #d4d4d4;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-scenario-execution {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-row > * {
    width: 100% !important;
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