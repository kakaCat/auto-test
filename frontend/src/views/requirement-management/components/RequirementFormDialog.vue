<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'create' ? '新增需求' : '编辑需求'"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      label-width="120px"
      class="requirement-form"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h4 class="section-title">
          基本信息
        </h4>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item
              label="需求标题"
              prop="title"
            >
              <el-input
                v-model="form.title"
                placeholder="请输入需求标题"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="需求ID"
              prop="id"
            >
              <el-input
                v-model="form.id"
                placeholder="系统自动生成或手动输入"
                :disabled="mode === 'edit'"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item
              label="需求类型"
              prop="type"
            >
              <el-select
                v-model="form.type"
                placeholder="请选择需求类型"
              >
                <el-option
                  label="功能需求"
                  value="functional"
                />
                <el-option
                  label="性能需求"
                  value="performance"
                />
                <el-option
                  label="安全需求"
                  value="security"
                />
                <el-option
                  label="技术需求"
                  value="technical"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              label="优先级"
              prop="priority"
            >
              <el-select
                v-model="form.priority"
                placeholder="请选择优先级"
              >
                <el-option
                  label="关键"
                  value="critical"
                />
                <el-option
                  label="高"
                  value="high"
                />
                <el-option
                  label="中"
                  value="medium"
                />
                <el-option
                  label="低"
                  value="low"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              label="状态"
              prop="status"
            >
              <el-select
                v-model="form.status"
                placeholder="请选择状态"
              >
                <el-option
                  label="草稿"
                  value="draft"
                />
                <el-option
                  label="开发中"
                  value="in_development"
                />
                <el-option
                  label="测试中"
                  value="in_testing"
                />
                <el-option
                  label="已完成"
                  value="completed"
                />
                <el-option
                  label="已取消"
                  value="cancelled"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item
              label="所属项目"
              prop="projectId"
            >
              <el-select
                v-model="form.projectId"
                placeholder="请选择项目"
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              label="负责人"
              prop="assignee"
            >
              <el-input
                v-model="form.assignee"
                placeholder="请输入负责人"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item
              label="目标版本"
              prop="targetRelease"
            >
              <el-input
                v-model="form.targetRelease"
                placeholder="如：v2.0.0"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item
          label="预估工作量"
          prop="estimatedEffort"
        >
          <el-input
            v-model="form.estimatedEffort"
            placeholder="如：8人天、16小时"
          />
        </el-form-item>
      </div>

      <!-- 详细描述 -->
      <div class="form-section">
        <h4 class="section-title">
          详细描述
        </h4>
        
        <el-form-item
          label="需求描述"
          prop="description"
        >
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述需求的功能和实现要求"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item
          label="业务价值"
          prop="businessValue"
        >
          <el-input
            v-model="form.businessValue"
            type="textarea"
            :rows="3"
            placeholder="请描述该需求的业务价值和意义"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </div>

      <!-- 验收条件 -->
      <div class="form-section">
        <h4 class="section-title">
          验收条件
        </h4>
        
        <div class="acceptance-criteria">
          <div
            v-for="(criteria, index) in form.acceptanceCriteria"
            :key="index"
            class="criteria-item"
          >
            <el-input
              v-model="form.acceptanceCriteria[index]"
              placeholder="请输入验收条件"
              maxlength="200"
            />
            <el-button
              type="danger"
              :icon="Delete"
              size="small"
              @click="removeCriteria(index)"
            />
          </div>
          
          <el-button
            type="primary"
            :icon="Plus"
            size="small"
            @click="addCriteria"
          >
            添加验收条件
          </el-button>
        </div>
      </div>

      <!-- 依赖关系 -->
      <div class="form-section">
        <h4 class="section-title">
          依赖关系
        </h4>
        
        <el-form-item label="前置需求">
          <el-select
            v-model="form.dependencies"
            multiple
            placeholder="请选择前置需求"
            style="width: 100%"
          >
            <el-option
              v-for="req in availableRequirements"
              :key="req.id"
              :label="req.title"
              :value="req.id"
              :disabled="req.id === form.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="相关干系人">
          <el-select
            v-model="form.stakeholders"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入干系人"
            style="width: 100%"
          >
            <el-option
              label="产品经理"
              value="产品经理"
            />
            <el-option
              label="开发团队"
              value="开发团队"
            />
            <el-option
              label="测试团队"
              value="测试团队"
            />
            <el-option
              label="运维团队"
              value="运维团队"
            />
            <el-option
              label="业务方"
              value="业务方"
            />
          </el-select>
        </el-form-item>
      </div>

      <!-- 风险评估 -->
      <div class="form-section">
        <h4 class="section-title">
          风险评估
        </h4>
        
        <el-form-item
          label="技术风险"
          prop="technicalRisk"
        >
          <el-rate
            v-model="form.technicalRisk"
            :max="5"
            show-text
            :texts="riskTexts"
          />
        </el-form-item>

        <el-form-item
          label="业务风险"
          prop="businessRisk"
        >
          <el-rate
            v-model="form.businessRisk"
            :max="5"
            show-text
            :texts="riskTexts"
          />
        </el-form-item>

        <el-form-item
          label="风险说明"
          prop="riskDescription"
        >
          <el-input
            v-model="form.riskDescription"
            type="textarea"
            :rows="3"
            placeholder="请描述主要风险点和应对措施"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">
        取消
      </el-button>
      <el-button
        type="primary"
        :loading="submitting"
        @click="handleSubmit"
      >
        {{ mode === 'create' ? '创建' : '更新' }}
      </el-button>
    </template>
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
const submitting = ref(false)
const projects = ref([])
const availableRequirements = ref([])

// 表单数据
const form = reactive({
  id: '',
  title: '',
  type: 'functional',
  priority: 'medium',
  status: 'draft',
  projectId: '',
  assignee: '',
  targetRelease: '',
  estimatedEffort: '',
  description: '',
  businessValue: '',
  acceptanceCriteria: [''],
  dependencies: [],
  stakeholders: [],
  technicalRisk: 1,
  businessRisk: 1,
  riskDescription: ''
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入需求标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度在 5 到 100 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择需求类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  projectId: [
    { required: true, message: '请选择所属项目', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 10, max: 1000, message: '描述长度在 10 到 1000 个字符', trigger: 'blur' }
  ]
}

// 风险等级文本
const riskTexts = ['极低', '低', '中等', '高', '极高']

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

    // 清理空的验收条件
    const cleanedForm = {
      ...form,
      acceptanceCriteria: form.acceptanceCriteria.filter(criteria => criteria.trim())
    }

    if (props.mode === 'create') {
      await requirementApi.createRequirement(cleanedForm)
      ElMessage.success('需求创建成功')
    } else {
      await requirementApi.updateRequirement(form.id, cleanedForm)
      ElMessage.success('需求更新成功')
    }

    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

const addCriteria = () => {
  form.acceptanceCriteria.push('')
}

const removeCriteria = (index) => {
  if (form.acceptanceCriteria.length > 1) {
    form.acceptanceCriteria.splice(index, 1)
  }
}

const resetForm = () => {
  Object.assign(form, {
    id: '',
    title: '',
    type: 'functional',
    priority: 'medium',
    status: 'draft',
    projectId: '',
    assignee: '',
    targetRelease: '',
    estimatedEffort: '',
    description: '',
    businessValue: '',
    acceptanceCriteria: [''],
    dependencies: [],
    stakeholders: [],
    technicalRisk: 1,
    businessRisk: 1,
    riskDescription: ''
  })
  
  // 清除表单验证状态
  formRef.value?.clearValidate()
}

const loadFormData = () => {
  if (props.requirement && props.mode === 'edit') {
    Object.assign(form, {
      ...props.requirement,
      acceptanceCriteria: props.requirement.acceptanceCriteria?.length 
        ? [...props.requirement.acceptanceCriteria]
        : ['']
    })
  }
}

// 数据加载函数
const loadProjects = async () => {
  try {
    const response = await requirementApi.getProjects()
    projects.value = response.data || []
  } catch (error) {
    console.error('加载项目列表失败：', error)
    // 使用模拟数据
    projects.value = [
      { id: 'proj-001', name: '用户管理系统' },
      { id: 'proj-002', name: '订单管理系统' },
      { id: 'proj-003', name: '商品管理系统' }
    ]
  }
}

const loadAvailableRequirements = async () => {
  try {
    const response = await requirementApi.getRequirements()
    availableRequirements.value = response.data || []
  } catch (error) {
    console.error('加载需求列表失败：', error)
    availableRequirements.value = []
  }
}

// 监听器
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadFormData()
    loadProjects()
    loadAvailableRequirements()
  }
})

watch(() => props.requirement, () => {
  if (props.visible) {
    loadFormData()
  }
})

// 组件挂载
onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.requirement-form {
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

.acceptance-criteria {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.criteria-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.criteria-item:last-child {
  margin-bottom: 0;
}

.criteria-item .el-input {
  flex: 1;
}

/* 表单项样式优化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
}

/* 评分组件样式 */
:deep(.el-rate) {
  display: flex;
  align-items: center;
}

:deep(.el-rate__text) {
  margin-left: 12px;
  font-size: 14px;
  color: #606266;
}
</style>