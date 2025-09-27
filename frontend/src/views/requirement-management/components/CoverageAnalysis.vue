<template>
  <div class="coverage-analysis">
    <!-- 分析头部 -->
    <div class="analysis-header">
      <h3>需求测试覆盖率分析</h3>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateRangeChange"
        />
        <el-button :icon="Refresh" @click="refreshAnalysis">刷新</el-button>
        <el-button :icon="Download" @click="handleExportAnalysis">导出</el-button>
      </div>
    </div>

    <!-- 总体覆盖率概览 -->
    <div class="coverage-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="overview-card">
            <div class="card-header">
              <el-icon class="card-icon"><Document /></el-icon>
              <span class="card-title">总需求数</span>
            </div>
            <div class="card-value">{{ overallStats.totalRequirements }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-card">
            <div class="card-header">
              <el-icon class="card-icon success"><Check /></el-icon>
              <span class="card-title">已覆盖需求</span>
            </div>
            <div class="card-value success">{{ overallStats.coveredRequirements }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-card">
            <div class="card-header">
              <el-icon class="card-icon primary"><DataBoard /></el-icon>
              <span class="card-title">覆盖率</span>
            </div>
            <div class="card-value primary">{{ overallStats.coveragePercentage }}%</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-card">
            <div class="card-header">
              <el-icon class="card-icon warning"><Target /></el-icon>
              <span class="card-title">目标覆盖率</span>
            </div>
            <div class="card-value warning">{{ overallStats.targetCoverage }}%</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 覆盖率图表 -->
    <div class="coverage-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="chart-card">
            <h4>按类别覆盖率</h4>
            <div ref="categoryChartRef" class="chart-container"></div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="chart-card">
            <h4>覆盖率趋势</h4>
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 详细覆盖率表格 -->
    <div class="coverage-table">
      <div class="table-header">
        <h4>详细覆盖率分析</h4>
        <div class="table-actions">
          <el-input
            v-model="searchText"
            placeholder="搜索需求..."
            :prefix-icon="Search"
            style="width: 200px"
            clearable
          />
          <el-select v-model="filterCategory" placeholder="筛选类别" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="功能需求" value="functional" />
            <el-option label="性能需求" value="performance" />
            <el-option label="安全需求" value="security" />
            <el-option label="技术需求" value="technical" />
          </el-select>
        </div>
      </div>
      
      <el-table :data="filteredCoverageData" style="width: 100%">
        <el-table-column prop="requirementId" label="需求ID" width="120" />
        <el-table-column prop="requirementName" label="需求名称" min-width="200" />
        <el-table-column prop="category" label="类别" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryText(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scenarioCount" label="关联场景数" width="120" />
        <el-table-column prop="coveragePercentage" label="覆盖率" width="120">
          <template #default="{ row }">
            <div class="coverage-cell">
              <el-progress
                :percentage="row.coveragePercentage"
                :stroke-width="8"
                :show-text="false"
                :color="getCoverageColor(row.coveragePercentage)"
              />
              <span class="coverage-text">{{ row.coveragePercentage }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getCoverageStatusType(row.status)" size="small">
              {{ getCoverageStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" :icon="View" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 覆盖率详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="覆盖率详情"
      width="800px"
    >
      <div v-if="selectedCoverageDetail" class="coverage-detail">
        <div class="detail-header">
          <h4>{{ selectedCoverageDetail.requirementName }}</h4>
          <el-tag :type="getCoverageStatusType(selectedCoverageDetail.status)">
            {{ getCoverageStatusText(selectedCoverageDetail.status) }}
          </el-tag>
        </div>
        
        <div class="detail-content">
          <div class="coverage-breakdown">
            <h5>覆盖率分解</h5>
            <el-table :data="selectedCoverageDetail.scenarioBreakdown" size="small">
              <el-table-column prop="scenarioName" label="场景名称" min-width="200" />
              <el-table-column prop="coverageType" label="覆盖类型" width="120">
                <template #default="{ row }">
                  <el-tag size="small">{{ getCoverageTypeText(row.coverageType) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="weight" label="权重" width="80">
                <template #default="{ row }">{{ row.weight }}%</template>
              </el-table-column>
              <el-table-column prop="executionStatus" label="执行状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getExecutionStatusType(row.executionStatus)" size="small">
                    {{ getExecutionStatusText(row.executionStatus) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div class="gap-analysis" v-if="selectedCoverageDetail.gaps?.length">
            <h5>覆盖率缺口</h5>
            <ul class="gap-list">
              <li v-for="gap in selectedCoverageDetail.gaps" :key="gap.id" class="gap-item">
                <el-icon class="gap-icon"><Warning /></el-icon>
                <span>{{ gap.description }}</span>
                <el-tag type="warning" size="small">{{ gap.severity }}</el-tag>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh, Download, Search, View, Document, Check,
  DataBoard, Target, Warning
} from '@element-plus/icons-vue'
import { requirementApi } from '@/api/requirement-management'

// 响应式数据
const categoryChartRef = ref()
const trendChartRef = ref()
const dateRange = ref([])
const searchText = ref('')
const filterCategory = ref('')
const detailDialogVisible = ref(false)
const selectedCoverageDetail = ref(null)

// 覆盖率数据
const overallStats = reactive({
  totalRequirements: 0,
  coveredRequirements: 0,
  coveragePercentage: 0,
  targetCoverage: 95
})

const coverageData = ref([])

// 计算属性
const filteredCoverageData = computed(() => {
  let filtered = coverageData.value

  if (searchText.value) {
    filtered = filtered.filter(item =>
      item.requirementName.toLowerCase().includes(searchText.value.toLowerCase()) ||
      item.requirementId.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }

  if (filterCategory.value) {
    filtered = filtered.filter(item => item.category === filterCategory.value)
  }

  return filtered
})

// 事件处理函数
const handleDateRangeChange = () => {
  loadCoverageAnalysis()
}

const refreshAnalysis = () => {
  loadCoverageAnalysis()
}

const handleExportAnalysis = async () => {
  try {
    const params = {
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1],
      category: filterCategory.value
    }
    
    await requirementApi.exportCoverageAnalysis(params)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

const handleViewDetail = (row) => {
  selectedCoverageDetail.value = {
    ...row,
    scenarioBreakdown: getMockScenarioBreakdown(row.requirementId),
    gaps: getMockGaps(row.requirementId)
  }
  detailDialogVisible.value = true
}

// 数据加载函数
const loadCoverageAnalysis = async () => {
  try {
    const params = {
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1]
    }
    
    const response = await requirementApi.getCoverageAnalysis(params)
    const data = response.data || getMockCoverageData()
    
    // 更新总体统计
    Object.assign(overallStats, data.overall || {
      totalRequirements: 25,
      coveredRequirements: 23,
      coveragePercentage: 92,
      targetCoverage: 95
    })
    
    // 更新详细数据
    coverageData.value = data.details || getMockCoverageDetails()
    
    // 更新图表
    nextTick(() => {
      updateCharts(data)
    })
  } catch (error) {
    console.error('加载覆盖率分析失败：', error)
    // 使用模拟数据
    loadMockData()
  }
}

const loadMockData = () => {
  Object.assign(overallStats, {
    totalRequirements: 25,
    coveredRequirements: 23,
    coveragePercentage: 92,
    targetCoverage: 95
  })
  
  coverageData.value = getMockCoverageDetails()
}

const updateCharts = (data) => {
  // 这里可以集成图表库如 ECharts
  // 暂时显示占位信息
  console.log('更新图表数据：', data)
}

// 辅助函数
const getCoverageColor = (percentage) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getCategoryType = (category) => {
  const typeMap = {
    functional: 'primary',
    performance: 'warning',
    security: 'danger',
    technical: 'info'
  }
  return typeMap[category] || 'info'
}

const getCategoryText = (category) => {
  const textMap = {
    functional: '功能',
    performance: '性能',
    security: '安全',
    technical: '技术'
  }
  return textMap[category] || '其他'
}

const getPriorityType = (priority) => {
  const typeMap = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    critical: '关键',
    high: '高',
    medium: '中',
    low: '低'
  }
  return textMap[priority] || '未设置'
}

const getCoverageStatusType = (status) => {
  const typeMap = {
    excellent: 'success',
    good: 'primary',
    fair: 'warning',
    poor: 'danger'
  }
  return typeMap[status] || 'info'
}

const getCoverageStatusText = (status) => {
  const textMap = {
    excellent: '优秀',
    good: '良好',
    fair: '一般',
    poor: '较差'
  }
  return textMap[status] || '未知'
}

const getCoverageTypeText = (type) => {
  const textMap = {
    happy_path: '正常路径',
    error_handling: '异常处理',
    boundary: '边界条件',
    performance: '性能测试'
  }
  return textMap[type] || '其他'
}

const getExecutionStatusType = (status) => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    pending: 'warning',
    skipped: 'info'
  }
  return typeMap[status] || 'info'
}

const getExecutionStatusText = (status) => {
  const textMap = {
    passed: '通过',
    failed: '失败',
    pending: '待执行',
    skipped: '跳过'
  }
  return textMap[status] || '未知'
}

// 模拟数据
const getMockCoverageData = () => {
  return {
    overall: {
      totalRequirements: 25,
      coveredRequirements: 23,
      coveragePercentage: 92,
      targetCoverage: 95
    },
    details: getMockCoverageDetails()
  }
}

const getMockCoverageDetails = () => {
  return [
    {
      requirementId: 'REQ-001',
      requirementName: '用户登录功能',
      category: 'functional',
      priority: 'high',
      scenarioCount: 3,
      coveragePercentage: 95,
      status: 'excellent'
    },
    {
      requirementId: 'REQ-002',
      requirementName: '用户注册功能',
      category: 'functional',
      priority: 'high',
      scenarioCount: 4,
      coveragePercentage: 88,
      status: 'good'
    },
    {
      requirementId: 'REQ-003',
      requirementName: '权限验证功能',
      category: 'security',
      priority: 'critical',
      scenarioCount: 2,
      coveragePercentage: 65,
      status: 'fair'
    },
    {
      requirementId: 'REQ-004',
      requirementName: '性能优化需求',
      category: 'performance',
      priority: 'medium',
      scenarioCount: 1,
      coveragePercentage: 40,
      status: 'poor'
    }
  ]
}

const getMockScenarioBreakdown = (requirementId) => {
  return [
    {
      scenarioName: '正常登录流程测试',
      coverageType: 'happy_path',
      weight: 60,
      executionStatus: 'passed'
    },
    {
      scenarioName: '错误密码登录测试',
      coverageType: 'error_handling',
      weight: 25,
      executionStatus: 'passed'
    },
    {
      scenarioName: '登录性能测试',
      coverageType: 'performance',
      weight: 15,
      executionStatus: 'pending'
    }
  ]
}

const getMockGaps = (requirementId) => {
  return [
    {
      id: 'gap-001',
      description: '缺少边界条件测试场景',
      severity: '中等'
    },
    {
      id: 'gap-002',
      description: '安全测试覆盖不足',
      severity: '高'
    }
  ]
}

// 组件挂载
onMounted(() => {
  loadCoverageAnalysis()
})
</script>

<style scoped>
.coverage-analysis {
  padding: 20px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.analysis-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.coverage-overview {
  margin-bottom: 24px;
}

.overview-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.card-icon {
  font-size: 20px;
  color: #606266;
}

.card-icon.success {
  color: #67c23a;
}

.card-icon.primary {
  color: #409eff;
}

.card-icon.warning {
  color: #e6a23c;
}

.card-title {
  font-size: 14px;
  color: #606266;
}

.card-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.card-value.success {
  color: #67c23a;
}

.card-value.primary {
  color: #409eff;
}

.card-value.warning {
  color: #e6a23c;
}

.coverage-charts {
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.chart-card h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 4px;
  color: #909399;
}

.coverage-table {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.table-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.coverage-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coverage-text {
  font-weight: 500;
  min-width: 40px;
}

.coverage-detail {
  max-height: 500px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.coverage-breakdown,
.gap-analysis {
  margin-bottom: 20px;
}

.coverage-breakdown h5,
.gap-analysis h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.gap-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.gap-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  margin-bottom: 8px;
}

.gap-icon {
  color: #f56c6c;
}

/* 进度条样式 */
:deep(.el-progress-bar__outer) {
  border-radius: 4px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>