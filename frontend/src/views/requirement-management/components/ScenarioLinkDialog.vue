<template>
  <el-dialog
    v-model="dialogVisible"
    title="关联测试场景"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="scenario-link-content">
      <!-- 需求信息展示 -->
      <div class="requirement-info">
        <h4>当前需求：{{ requirement?.title }}</h4>
        <p class="requirement-desc">
          {{ requirement?.description }}
        </p>
      </div>

      <!-- 场景选择区域 -->
      <div class="scenario-selection">
        <div class="selection-header">
          <h4>选择测试场景</h4>
          <div class="header-actions">
            <el-input
              v-model="searchText"
              placeholder="搜索场景..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
            />
            <el-button
              :icon="Refresh"
              @click="loadAvailableScenarios"
            >
              刷新
            </el-button>
          </div>
        </div>

        <!-- 场景列表 -->
        <div class="scenario-list">
          <el-table
            ref="scenarioTableRef"
            :data="filteredScenarios"
            height="300"
            @selection-change="handleSelectionChange"
          >
            <el-table-column
              type="selection"
              width="55"
            />
            <el-table-column
              prop="name"
              label="场景名称"
              min-width="200"
            >
              <template #default="{ row }">
                <div class="scenario-name">
                  <el-icon class="scenario-icon">
                    <component :is="getScenarioIcon(row.type)" />
                  </el-icon>
                  {{ row.name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column
              prop="type"
              label="场景类型"
              width="120"
            >
              <template #default="{ row }">
                <el-tag
                  :type="getScenarioTypeTag(row.type)"
                  size="small"
                >
                  {{ getScenarioTypeText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="priority"
              label="优先级"
              width="100"
            >
              <template #default="{ row }">
                <el-tag
                  :type="getPriorityType(row.priority)"
                  size="small"
                >
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="status"
              label="状态"
              width="100"
            >
              <template #default="{ row }">
                <el-tag
                  :type="getStatusType(row.status)"
                  size="small"
                >
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="description"
              label="描述"
              min-width="200"
              show-overflow-tooltip
            />
            <el-table-column
              label="操作"
              width="80"
            >
              <template #default="{ row }">
                <el-button
                  size="small"
                  :icon="View"
                  @click="handleViewScenario(row)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 已关联场景展示 -->
      <div
        v-if="linkedScenarios?.length"
        class="linked-scenarios"
      >
        <h4>已关联场景 ({{ linkedScenarios.length }})</h4>
        <div class="linked-list">
          <div
            v-for="scenario in linkedScenarios"
            :key="scenario.id"
            class="linked-item"
          >
            <div class="linked-info">
              <el-icon class="scenario-icon">
                <component :is="getScenarioIcon(scenario.type)" />
              </el-icon>
              <span class="scenario-name">{{ scenario.name }}</span>
              <el-tag
                :type="getScenarioTypeTag(scenario.type)"
                size="small"
              >
                {{ getScenarioTypeText(scenario.type) }}
              </el-tag>
            </div>
            <div class="linked-actions">
              <el-button
                size="small"
                :icon="View"
                @click="handleViewScenario(scenario)"
              >
                查看
              </el-button>
              <el-button
                size="small"
                :icon="Close"
                type="danger"
                @click="handleUnlinkScenario(scenario)"
              >
                取消关联
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 关联配置 -->
      <div
        v-if="selectedScenarios.length"
        class="link-config"
      >
        <h4>关联配置</h4>
        <div class="config-list">
          <div
            v-for="scenario in selectedScenarios"
            :key="scenario.id"
            class="config-item"
          >
            <div class="config-info">
              <span class="scenario-name">{{ scenario.name }}</span>
            </div>
            <div class="config-options">
              <el-form-item
                label="覆盖类型"
                size="small"
              >
                <el-select
                  v-model="scenario.coverageType"
                  size="small"
                >
                  <el-option
                    label="正常路径"
                    value="happy_path"
                  />
                  <el-option
                    label="异常处理"
                    value="error_handling"
                  />
                  <el-option
                    label="边界条件"
                    value="boundary"
                  />
                  <el-option
                    label="性能测试"
                    value="performance"
                  />
                </el-select>
              </el-form-item>
              <el-form-item
                label="覆盖权重"
                size="small"
              >
                <el-input-number
                  v-model="scenario.coverageWeight"
                  :min="1"
                  :max="100"
                  size="small"
                />
              </el-form-item>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-info">
          <span v-if="selectedScenarios.length">
            已选择 {{ selectedScenarios.length }} 个场景
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="handleClose">
            取消
          </el-button>
          <el-button
            type="primary"
            :loading="submitting"
            :disabled="!selectedScenarios.length"
            @click="handleSubmit"
          >
            确认关联
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, View, Close, Operation, 
  VideoPlay, Monitor, Setting
} from '@element-plus/icons-vue'
import { requirementApi } from '@/api/requirement-management'

// 组件属性
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  requirement: {
    type: Object,
    default: null
  },
  linkedScenarios: {
    type: Array,
    default: () => []
  }
})

// 组件事件
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const scenarioTableRef = ref()
const searchText = ref('')
const submitting = ref(false)
const availableScenarios = ref([])
const selectedScenarios = ref([])

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const filteredScenarios = computed(() => {
  if (!searchText.value) return availableScenarios.value
  
  return availableScenarios.value.filter(scenario =>
    scenario.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
    scenario.description?.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 事件处理函数
const handleClose = () => {
  dialogVisible.value = false
  resetSelection()
}

const handleSelectionChange = (selection) => {
  selectedScenarios.value = selection.map(scenario => ({
    ...scenario,
    coverageType: 'happy_path',
    coverageWeight: 50
  }))
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    
    const scenarioIds = selectedScenarios.value.map(s => s.id)
    const linkData = selectedScenarios.value.map(s => ({
      scenarioId: s.id,
      coverageType: s.coverageType,
      coverageWeight: s.coverageWeight
    }))

    await requirementApi.linkScenarios(props.requirement.id, linkData)
    ElMessage.success('场景关联成功')
    
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('关联失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

const handleViewScenario = (scenario) => {
  // 在新窗口打开场景详情
  window.open(`/scenario-management/list?id=${scenario.id}`, '_blank')
}

const handleUnlinkScenario = async (scenario) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消与场景"${scenario.name}"的关联吗？`,
      '取消关联确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await requirementApi.unlinkScenario(props.requirement.id, scenario.id)
    ElMessage.success('取消关联成功')
    emit('success')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消关联失败：' + error.message)
    }
  }
}

const resetSelection = () => {
  selectedScenarios.value = []
  searchText.value = ''
  scenarioTableRef.value?.clearSelection()
}

// 数据加载函数
const loadAvailableScenarios = async () => {
  try {
    // 这里应该调用场景管理的API
    // const response = await scenarioApi.getScenarios()
    // availableScenarios.value = response.data || []
    
    // 暂时使用模拟数据
    availableScenarios.value = getMockScenarios()
  } catch (error) {
    console.error('加载可用场景失败：', error)
    availableScenarios.value = getMockScenarios()
  }
}

// 辅助函数
const getScenarioIcon = (type) => {
  const iconMap = {
    functional: Operation,
    performance: Monitor,
    security: Setting,
    integration: VideoPlay
  }
  return iconMap[type] || Operation
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

const getScenarioTypeText = (type) => {
  const textMap = {
    functional: '功能',
    performance: '性能',
    security: '安全',
    integration: '集成'
  }
  return textMap[type] || '其他'
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

const getStatusType = (status) => {
  const typeMap = {
    draft: 'info',
    active: 'success',
    inactive: 'warning',
    archived: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    active: '活跃',
    inactive: '未激活',
    archived: '已归档'
  }
  return textMap[status] || '未知'
}

// 模拟数据
const getMockScenarios = () => {
  return [
    {
      id: 'sc-001',
      name: '正常登录流程测试',
      type: 'functional',
      priority: 'high',
      status: 'active',
      description: '测试用户使用正确的用户名和密码登录系统'
    },
    {
      id: 'sc-002',
      name: '错误密码登录测试',
      type: 'functional',
      priority: 'medium',
      status: 'active',
      description: '测试用户输入错误密码时的处理逻辑'
    },
    {
      id: 'sc-003',
      name: '登录性能测试',
      type: 'performance',
      priority: 'medium',
      status: 'active',
      description: '测试登录接口的响应时间和并发处理能力'
    },
    {
      id: 'sc-004',
      name: '用户注册流程测试',
      type: 'functional',
      priority: 'high',
      status: 'active',
      description: '测试新用户注册的完整流程'
    },
    {
      id: 'sc-005',
      name: '权限验证测试',
      type: 'security',
      priority: 'high',
      status: 'active',
      description: '测试用户权限验证和访问控制'
    }
  ]
}

// 监听器
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadAvailableScenarios()
    resetSelection()
  }
})

// 组件挂载
onMounted(() => {
  loadAvailableScenarios()
})
</script>

<style scoped>
.scenario-link-content {
  max-height: 600px;
  overflow-y: auto;
}

.requirement-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.requirement-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.requirement-desc {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

.scenario-selection {
  margin-bottom: 24px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.selection-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.scenario-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.scenario-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.scenario-icon {
  color: #606266;
}

.linked-scenarios {
  margin-bottom: 24px;
}

.linked-scenarios h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.linked-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.linked-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.linked-item:last-child {
  border-bottom: none;
}

.linked-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.linked-actions {
  display: flex;
  gap: 8px;
}

.link-config {
  margin-bottom: 24px;
}

.link-config h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.config-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.config-item:last-child {
  border-bottom: none;
}

.config-info {
  flex: 1;
}

.config-options {
  display: flex;
  gap: 16px;
  align-items: center;
}

.config-options .el-form-item {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  color: #606266;
  font-size: 14px;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

/* 表格样式优化 */
:deep(.el-table__header) {
  background: #fafafa;
}

:deep(.el-table__row:hover) {
  background: #f5f7fa;
}

/* 标签样式 */
.el-tag {
  font-size: 11px;
}
</style>