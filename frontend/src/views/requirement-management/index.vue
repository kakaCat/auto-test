<template>
  <div class="requirement-management">
    <!-- 页面头部区域 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">需求管理</h1>
        <p class="page-description">管理业务需求与测试用例的关联关系</p>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="DocumentAdd" @click="handleAddRequirement">
          新增需求
        </el-button>
        <el-button :icon="Upload" @click="handleImportRequirements">
          导入需求
        </el-button>
        <el-button :icon="Download" @click="handleExportReport">
          导出报告
        </el-button>
        <el-dropdown @command="handleTestPlanCommand">
          <el-button :icon="DataBoard">
            测试计划<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="create">制定测试计划</el-dropdown-item>
              <el-dropdown-item command="track">执行跟踪</el-dropdown-item>
              <el-dropdown-item command="coverage">覆盖率分析</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧导航面板 -->
      <div class="left-panel">
        <RequirementTree
          ref="requirementTreeRef"
          @node-click="handleTreeNodeClick"
          @node-select="handleTreeNodeSelect"
        />
      </div>

      <!-- 中间需求详情区域 -->
      <div class="center-panel">
        <div v-if="!selectedRequirement" class="empty-state">
          <el-empty description="请从左侧选择需求项目或需求条目">
            <el-button type="primary" @click="handleAddRequirement">新增需求</el-button>
          </el-empty>
        </div>
        
        <div v-else class="requirement-detail">
          <!-- 需求基本信息 -->
          <div class="requirement-info">
            <div class="info-header">
              <h3>{{ selectedRequirement.title }}</h3>
              <div class="info-actions">
                <el-button size="small" :icon="Edit" @click="handleEditRequirement">编辑</el-button>
                <el-button size="small" :icon="Delete" type="danger" @click="handleDeleteRequirement">删除</el-button>
              </div>
            </div>
            
            <div class="info-content">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="需求ID">{{ selectedRequirement.id }}</el-descriptions-item>
                <el-descriptions-item label="优先级">
                  <el-tag :type="getPriorityType(selectedRequirement.priority)">
                    {{ getPriorityText(selectedRequirement.priority) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="getStatusType(selectedRequirement.status)">
                    {{ getStatusText(selectedRequirement.status) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="类型">{{ getTypeText(selectedRequirement.type) }}</el-descriptions-item>
                <el-descriptions-item label="负责人">{{ selectedRequirement.assignee || '未分配' }}</el-descriptions-item>
                <el-descriptions-item label="目标版本">{{ selectedRequirement.targetRelease || '未设置' }}</el-descriptions-item>
                <el-descriptions-item label="预估工作量" span="2">{{ selectedRequirement.estimatedEffort || '未评估' }}</el-descriptions-item>
              </el-descriptions>
              
              <div class="description-section">
                <h4>需求描述</h4>
                <p>{{ selectedRequirement.description || '暂无描述' }}</p>
              </div>
              
              <div class="acceptance-criteria-section" v-if="selectedRequirement.acceptanceCriteria?.length">
                <h4>验收条件</h4>
                <ul class="criteria-list">
                  <li v-for="(criteria, index) in selectedRequirement.acceptanceCriteria" :key="index">
                    <el-icon class="criteria-icon"><Check /></el-icon>
                    {{ criteria }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧关联面板 -->
      <div class="right-panel">
        <div class="panel-section">
          <h4>关联场景</h4>
          <div class="scenario-list">
            <div v-if="!associatedScenarios.length" class="empty-scenarios">
              <p>暂无关联场景</p>
              <el-button size="small" type="primary" @click="handleLinkScenarios">关联场景</el-button>
            </div>
            <div v-else>
              <div v-for="scenario in associatedScenarios" :key="scenario.id" class="scenario-item">
                <div class="scenario-info">
                  <span class="scenario-name">{{ scenario.name }}</span>
                  <el-tag size="small" :type="getScenarioTypeTag(scenario.type)">{{ scenario.type }}</el-tag>
                </div>
                <div class="scenario-actions">
                  <el-button size="small" :icon="View" @click="handleViewScenario(scenario)">查看</el-button>
                  <el-button size="small" :icon="Close" @click="handleUnlinkScenario(scenario)">取消关联</el-button>
                </div>
              </div>
              <el-button size="small" type="primary" @click="handleLinkScenarios">添加关联</el-button>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h4>测试计划</h4>
          <div class="test-plan-list">
            <div v-if="!testPlans.length" class="empty-plans">
              <p>暂无测试计划</p>
              <el-button size="small" type="primary" @click="handleCreateTestPlan">创建计划</el-button>
            </div>
            <div v-else>
              <div v-for="plan in testPlans" :key="plan.id" class="plan-item">
                <div class="plan-info">
                  <span class="plan-name">{{ plan.name }}</span>
                  <el-progress :percentage="plan.progress" :stroke-width="6" />
                </div>
                <div class="plan-actions">
                  <el-button size="small" :icon="View" @click="handleViewTestPlan(plan)">查看</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h4>执行状态</h4>
          <div class="execution-status">
            <div class="status-item">
              <span class="status-label">通过率</span>
              <span class="status-value">{{ executionStats.passRate }}%</span>
            </div>
            <div class="status-item">
              <span class="status-label">覆盖率</span>
              <span class="status-value">{{ executionStats.coverage }}%</span>
            </div>
            <div class="status-item">
              <span class="status-label">执行次数</span>
              <span class="status-value">{{ executionStats.executionCount }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 需求表单对话框 -->
    <RequirementFormDialog
      v-model:visible="requirementDialogVisible"
      :requirement="currentRequirement"
      :mode="dialogMode"
      @success="handleRequirementSuccess"
    />

    <!-- 场景关联对话框 -->
    <ScenarioLinkDialog
      v-model:visible="scenarioLinkDialogVisible"
      :requirement="selectedRequirement"
      :linked-scenarios="associatedScenarios"
      @success="handleScenarioLinkSuccess"
    />

    <!-- 测试计划对话框 -->
    <TestPlanDialog
      v-model:visible="testPlanDialogVisible"
      :requirement="selectedRequirement"
      :mode="testPlanMode"
      @success="handleTestPlanSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DocumentAdd, Upload, Download, DataBoard, ArrowDown,
  Edit, Delete, View, Close, Check
} from '@element-plus/icons-vue'
import RequirementTree from './components/RequirementTree.vue'
import RequirementFormDialog from './components/RequirementFormDialog.vue'
import ScenarioLinkDialog from './components/ScenarioLinkDialog.vue'
import TestPlanDialog from './components/TestPlanDialog.vue'
import { requirementApi } from '@/api/requirement-management'

// 响应式数据
const requirementTreeRef = ref()
const selectedRequirement = ref(null)
const currentRequirement = ref(null)
const associatedScenarios = ref([])
const testPlans = ref([])

// 对话框状态
const requirementDialogVisible = ref(false)
const scenarioLinkDialogVisible = ref(false)
const testPlanDialogVisible = ref(false)
const dialogMode = ref('create') // create | edit
const testPlanMode = ref('create') // create | edit

// 执行统计数据
const executionStats = reactive({
  passRate: 0,
  coverage: 0,
  executionCount: 0
})

// 计算属性
const hasSelectedRequirement = computed(() => !!selectedRequirement.value)

// 事件处理函数
const handleTreeNodeClick = (node) => {
  if (node.type === 'requirement') {
    loadRequirementDetail(node.id)
  }
}

const handleTreeNodeSelect = (node) => {
  // 处理树节点选择
}

const handleAddRequirement = () => {
  currentRequirement.value = null
  dialogMode.value = 'create'
  requirementDialogVisible.value = true
}

const handleEditRequirement = () => {
  currentRequirement.value = selectedRequirement.value
  dialogMode.value = 'edit'
  requirementDialogVisible.value = true
}

const handleDeleteRequirement = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求"${selectedRequirement.value.title}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await requirementApi.deleteRequirement(selectedRequirement.value.id)
    ElMessage.success('需求删除成功')
    selectedRequirement.value = null
    requirementTreeRef.value?.refreshTree()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

const handleImportRequirements = () => {
  ElMessage.info('导入需求功能开发中')
}

const handleExportReport = () => {
  ElMessage.info('导出报告功能开发中')
}

const handleTestPlanCommand = (command) => {
  switch (command) {
    case 'create':
      handleCreateTestPlan()
      break
    case 'track':
      ElMessage.info('执行跟踪功能开发中')
      break
    case 'coverage':
      ElMessage.info('覆盖率分析功能开发中')
      break
  }
}

const handleLinkScenarios = () => {
  scenarioLinkDialogVisible.value = true
}

const handleUnlinkScenario = async (scenario) => {
  try {
    await requirementApi.unlinkScenario(selectedRequirement.value.id, scenario.id)
    ElMessage.success('取消关联成功')
    loadAssociatedScenarios()
  } catch (error) {
    ElMessage.error('取消关联失败：' + error.message)
  }
}

const handleViewScenario = (scenario) => {
  // 跳转到场景管理页面查看具体场景
  window.open(`/scenario-management/list?id=${scenario.id}`, '_blank')
}

const handleCreateTestPlan = () => {
  testPlanMode.value = 'create'
  testPlanDialogVisible.value = true
}

const handleViewTestPlan = (plan) => {
  ElMessage.info('查看测试计划功能开发中')
}

const handleRequirementSuccess = () => {
  requirementDialogVisible.value = false
  requirementTreeRef.value?.refreshTree()
  if (selectedRequirement.value) {
    loadRequirementDetail(selectedRequirement.value.id)
  }
}

const handleScenarioLinkSuccess = () => {
  scenarioLinkDialogVisible.value = false
  loadAssociatedScenarios()
}

const handleTestPlanSuccess = () => {
  testPlanDialogVisible.value = false
  loadTestPlans()
}

// 数据加载函数
const loadRequirementDetail = async (requirementId) => {
  try {
    const response = await requirementApi.getRequirement(requirementId)
    selectedRequirement.value = response.data
    loadAssociatedScenarios()
    loadTestPlans()
    loadExecutionStats()
  } catch (error) {
    ElMessage.error('加载需求详情失败：' + error.message)
  }
}

const loadAssociatedScenarios = async () => {
  if (!selectedRequirement.value) return
  
  try {
    const response = await requirementApi.getAssociatedScenarios(selectedRequirement.value.id)
    associatedScenarios.value = response.data || []
  } catch (error) {
    console.error('加载关联场景失败：', error)
    associatedScenarios.value = []
  }
}

const loadTestPlans = async () => {
  if (!selectedRequirement.value) return
  
  try {
    const response = await requirementApi.getTestPlans(selectedRequirement.value.id)
    testPlans.value = response.data || []
  } catch (error) {
    console.error('加载测试计划失败：', error)
    testPlans.value = []
  }
}

const loadExecutionStats = async () => {
  if (!selectedRequirement.value) return
  
  try {
    const response = await requirementApi.getExecutionStats(selectedRequirement.value.id)
    Object.assign(executionStats, response.data || {
      passRate: 0,
      coverage: 0,
      executionCount: 0
    })
  } catch (error) {
    console.error('加载执行统计失败：', error)
    Object.assign(executionStats, {
      passRate: 0,
      coverage: 0,
      executionCount: 0
    })
  }
}

// 辅助函数
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

const getStatusType = (status) => {
  const typeMap = {
    draft: 'info',
    in_development: 'warning',
    in_testing: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    in_development: '开发中',
    in_testing: '测试中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || '未知状态'
}

const getTypeText = (type) => {
  const textMap = {
    functional: '功能需求',
    performance: '性能需求',
    security: '安全需求',
    technical: '技术需求'
  }
  return textMap[type] || '其他'
}

const getScenarioTypeTag = (type) => {
  const typeMap = {
    functional: 'primary',
    performance: 'warning',
    security: 'danger',
    integration: 'success'
  }
  return typeMap[type] || 'info'
}

// 组件挂载
onMounted(() => {
  // 初始化页面数据
})
</script>

<style scoped>
.requirement-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  background: #f5f7fa;
  overflow: hidden;
}

.left-panel {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.center-panel {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.right-panel {
  width: 320px;
  background: #fff;
  border-left: 1px solid #e4e7ed;
  padding: 20px;
  overflow-y: auto;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.requirement-detail {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
}

.requirement-info .info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.requirement-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.info-actions {
  display: flex;
  gap: 8px;
}

.description-section,
.acceptance-criteria-section {
  margin-top: 24px;
}

.description-section h4,
.acceptance-criteria-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.description-section p {
  margin: 0;
  line-height: 1.6;
  color: #606266;
}

.criteria-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.criteria-list li {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.criteria-icon {
  color: #67c23a;
  margin-right: 8px;
}

.panel-section {
  margin-bottom: 24px;
}

.panel-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.scenario-item,
.plan-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 8px;
}

.scenario-info,
.plan-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.scenario-name,
.plan-name {
  font-weight: 500;
  color: #303133;
}

.scenario-actions,
.plan-actions {
  display: flex;
  gap: 4px;
}

.empty-scenarios,
.empty-plans {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.execution-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.status-label {
  color: #606266;
  font-size: 14px;
}

.status-value {
  font-weight: 600;
  color: #303133;
}
</style>