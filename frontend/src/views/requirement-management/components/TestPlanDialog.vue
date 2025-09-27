<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'create' ? '创建测试计划' : '编辑测试计划'"
    width="1000px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      label-width="120px"
      class="test-plan-form"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h4 class="section-title">基本信息</h4>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划名称" prop="name">
              <el-input
                v-model="form.name"
                placeholder="请输入测试计划名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标版本" prop="targetRelease">
              <el-input v-model="form.targetRelease" placeholder="如：v2.0.0" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="startDate">
              <el-date-picker
                v-model="form.startDate"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="endDate">
              <el-date-picker
                v-model="form.endDate"
                type="date"
                placeholder="选择结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="计划描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请描述测试计划的目标和范围"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </div>

      <!-- 需求范围 -->
      <div class="form-section">
        <h4 class="section-title">需求范围</h4>
        
        <div class="requirements-scope">
          <div class="scope-header">
            <span>包含的需求 ({{ form.requirementsInScope.length }})</span>
            <el-button size="small" :icon="Plus" @click="handleAddRequirement">
              添加需求
            </el-button>
          </div>
          
          <el-table :data="form.requirementsInScope" style="width: 100%">
            <el-table-column prop="title" label="需求名称" min-width="200" />
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="estimatedEffort" label="预估工作量" width="120" />
            <el-table-column prop="assignee" label="负责人" width="120">
              <template #default="{ $index }">
                <el-select
                  v-model="form.requirementsInScope[$index].assignee"
                  placeholder="选择负责人"
                  size="small"
                >
                  <el-option
                    v-for="member in teamMembers"
                    :key="member.id"
                    :label="member.name"
                    :value="member.name"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button
                  size="small"
                  :icon="Delete"
                  type="danger"
                  @click="removeRequirement($index)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 测试环境 -->
      <div class="form-section">
        <h4 class="section-title">测试环境</h4>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="测试环境" prop="testEnvironment">
              <el-select v-model="form.testEnvironment" placeholder="请选择测试环境">
                <el-option label="开发环境" value="dev" />
                <el-option label="测试环境" value="test" />
                <el-option label="预发布环境" value="staging" />
                <el-option label="生产环境" value="production" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试类型" prop="testTypes">
              <el-select v-model="form.testTypes" multiple placeholder="请选择测试类型">
                <el-option label="功能测试" value="functional" />
                <el-option label="性能测试" value="performance" />
                <el-option label="安全测试" value="security" />
                <el-option label="集成测试" value="integration" />
                <el-option label="回归测试" value="regression" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 准入准出条件 -->
      <div class="form-section">
        <h4 class="section-title">准入准出条件</h4>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="准入条件">
              <div class="criteria-list">
                <div
                  v-for="(criteria, index) in form.entryCriteria"
                  :key="index"
                  class="criteria-item"
                >
                  <el-input
                    v-model="form.entryCriteria[index]"
                    placeholder="请输入准入条件"
                    size="small"
                  />
                  <el-button
                    size="small"
                    :icon="Delete"
                    @click="removeEntryCriteria(index)"
                  />
                </div>
                <el-button
                  size="small"
                  :icon="Plus"
                  @click="addEntryCriteria"
                >
                  添加准入条件
                </el-button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="准出条件">
              <div class="criteria-list">
                <div
                  v-for="(criteria, index) in form.exitCriteria"
                  :key="index"
                  class="criteria-item"
                >
                  <el-input
                    v-model="form.exitCriteria[index]"
                    placeholder="请输入准出条件"
                    size="small"
                  />
                  <el-button
                    size="small"
                    :icon="Delete"
                    @click="removeExitCriteria(index)"
                  />
                </div>
                <el-button
                  size="small"
                  :icon="Plus"
                  @click="addExitCriteria"
                >
                  添加准出条件
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 风险评估 -->
      <div class="form-section">
        <h4 class="section-title">风险评估</h4>
        
        <el-form-item label="主要风险">
          <div class="risk-list">
            <div
              v-for="(risk, index) in form.risks"
              :key="index"
              class="risk-item"
            >
              <el-input
                v-model="form.risks[index].description"
                placeholder="风险描述"
                style="flex: 1"
              />
              <el-select
                v-model="form.risks[index].level"
                placeholder="风险等级"
                style="width: 120px"
              >
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="极高" value="critical" />
              </el-select>
              <el-input
                v-model="form.risks[index].mitigation"
                placeholder="应对措施"
                style="flex: 1"
              />
              <el-button
                size="small"
                :icon="Delete"
                @click="removeRisk(index)"
              />
            </div>
            <el-button
              size="small"
              :icon="Plus"
              @click="addRisk"
            >
              添加风险
            </el-button>
          </div>
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        {{ mode === 'create' ? '创建' : '更新' }}
      </el-button>
    </template>

    <!-- 需求选择对话框 -->
    <el-dialog
      v-model="requirementSelectVisible"
      title="选择需求"
      width="600px"
    >
      <el-table
        ref="requirementTableRef"
        :data="availableRequirements"
        @selection-change="handleRequirementSelection"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="需求名称" min-width="200" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="requirementSelectVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRequirementSelection">确定</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
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
  mode: {
    type: String,
    default: 'create' // create | edit
  }
})

// 组件事件
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const formRef = ref()
const requirementTableRef = ref()
const submitting = ref(false)
const requirementSelectVisible = ref(false)
const availableRequirements = ref([])
const selectedRequirementsForAdd = ref([])

// 团队成员数据
const teamMembers = ref([
  { id: '1', name: '测试工程师A' },
  { id: '2', name: '测试工程师B' },
  { id: '3', name: '测试工程师C' },
  { id: '4', name: '开发工程师A' },
  { id: '5', name: '开发工程师B' }
])

// 表单数据
const form = reactive({
  id: '',
  name: '',
  targetRelease: '',
  startDate: '',
  endDate: '',
  description: '',
  testEnvironment: 'test',
  testTypes: ['functional'],
  requirementsInScope: [],
  entryCriteria: ['代码开发完成', '单元测试通过'],
  exitCriteria: ['所有测试用例执行完成', '缺陷修复完成'],
  risks: [
    {
      description: '测试环境不稳定',
      level: 'medium',
      mitigation: '提前准备备用环境'
    }
  ]
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入计划名称', trigger: 'blur' },
    { min: 5, max: 100, message: '名称长度在 5 到 100 个字符', trigger: 'blur' }
  ],
  targetRelease: [
    { required: true, message: '请输入目标版本', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  endDate: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入计划描述', trigger: 'blur' }
  ],
  testEnvironment: [
    { required: true, message: '请选择测试环境', trigger: 'change' }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 事件处理函数
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    // 数据清理
    const cleanedForm = {
      ...form,
      entryCriteria: form.entryCriteria.filter(c => c.trim()),
      exitCriteria: form.exitCriteria.filter(c => c.trim()),
      risks: form.risks.filter(r => r.description.trim())
    }

    if (props.mode === 'create') {
      await requirementApi.createTestPlan(cleanedForm)
      ElMessage.success('测试计划创建成功')
    } else {
      await requirementApi.updateTestPlan(form.id, cleanedForm)
      ElMessage.success('测试计划更新成功')
    }

    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

const handleAddRequirement = () => {
  loadAvailableRequirements()
  requirementSelectVisible.value = true
}

const handleRequirementSelection = (selection) => {
  selectedRequirementsForAdd.value = selection
}

const confirmRequirementSelection = () => {
  const newRequirements = selectedRequirementsForAdd.value.filter(req => 
    !form.requirementsInScope.find(existing => existing.id === req.id)
  )
  
  form.requirementsInScope.push(...newRequirements.map(req => ({
    ...req,
    assignee: ''
  })))
  
  requirementSelectVisible.value = false
  selectedRequirementsForAdd.value = []
}

const removeRequirement = (index) => {
  form.requirementsInScope.splice(index, 1)
}

const addEntryCriteria = () => {
  form.entryCriteria.push('')
}

const removeEntryCriteria = (index) => {
  if (form.entryCriteria.length > 1) {
    form.entryCriteria.splice(index, 1)
  }
}

const addExitCriteria = () => {
  form.exitCriteria.push('')
}

const removeExitCriteria = (index) => {
  if (form.exitCriteria.length > 1) {
    form.exitCriteria.splice(index, 1)
  }
}

const addRisk = () => {
  form.risks.push({
    description: '',
    level: 'medium',
    mitigation: ''
  })
}

const removeRisk = (index) => {
  form.risks.splice(index, 1)
}

const resetForm = () => {
  Object.assign(form, {
    id: '',
    name: '',
    targetRelease: '',
    startDate: '',
    endDate: '',
    description: '',
    testEnvironment: 'test',
    testTypes: ['functional'],
    requirementsInScope: [],
    entryCriteria: ['代码开发完成', '单元测试通过'],
    exitCriteria: ['所有测试用例执行完成', '缺陷修复完成'],
    risks: [
      {
        description: '测试环境不稳定',
        level: 'medium',
        mitigation: '提前准备备用环境'
      }
    ]
  })
  
  formRef.value?.clearValidate()
}

const loadFormData = () => {
  if (props.requirement && props.mode === 'create') {
    // 基于当前需求创建测试计划
    form.name = `${props.requirement.title} - 测试计划`
    form.targetRelease = props.requirement.targetRelease || ''
    form.requirementsInScope = [{ ...props.requirement, assignee: '' }]
  }
}

// 数据加载函数
const loadAvailableRequirements = async () => {
  try {
    const response = await requirementApi.getRequirements()
    availableRequirements.value = response.data || []
  } catch (error) {
    console.error('加载需求列表失败：', error)
    availableRequirements.value = []
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
  return textMap[status] || '未知'
}

// 监听器
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadFormData()
  }
})
</script>

<style scoped>
.test-plan-form {
  max-height: 600px;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 16px;
  background: #409eff;
  margin-right: 8px;
  border-radius: 2px;
}

.requirements-scope {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
}

.scope-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
  color: #303133;
}

.criteria-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background: #fafafa;
}

.criteria-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.criteria-item:last-child {
  margin-bottom: 0;
}

.risk-list {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  background: #fafafa;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.risk-item:last-child {
  margin-bottom: 0;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-date-picker) {
  width: 100%;
}
</style>