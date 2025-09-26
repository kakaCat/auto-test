<template>
  <el-dialog
    v-model="visible"
    title="新建工作流向导"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 步骤指示器 -->
    <el-steps :active="currentStep" align-center class="wizard-steps">
      <el-step title="基本信息" icon="Edit" />
      <el-step title="创建方式" icon="Setting" />
      <el-step title="完成创建" icon="Check" />
    </el-steps>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <!-- 步骤1: 基本信息 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-form :model="formData" :rules="rules" ref="basicFormRef" label-width="120px">
          <el-form-item label="工作流名称" prop="name" required>
            <el-input 
              v-model="formData.name" 
              placeholder="请输入工作流名称"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="描述" prop="description">
            <el-input 
              v-model="formData.description" 
              type="textarea"
              placeholder="请输入工作流描述"
              :rows="3"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="分类" prop="category">
            <el-select v-model="formData.category" placeholder="请选择分类">
              <el-option label="API测试" value="api_test" />
              <el-option label="数据处理" value="data_process" />
              <el-option label="监控告警" value="monitoring" />
              <el-option label="自动化部署" value="deployment" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="关联应用" prop="appId">
            <el-select v-model="formData.appId" placeholder="请选择关联应用" clearable>
              <el-option 
                v-for="app in applications" 
                :key="app.id" 
                :label="app.name" 
                :value="app.id" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="标签" prop="tags">
            <el-input 
              v-model="formData.tags" 
              placeholder="多个标签用逗号分隔"
            />
          </el-form-item>
          
          <el-form-item label="优先级" prop="priority">
            <el-select v-model="formData.priority" placeholder="请选择优先级">
              <el-option label="低" value="low" />
              <el-option label="中等" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="超时设置" prop="timeout">
            <el-input-number 
              v-model="formData.timeout" 
              :min="30" 
              :max="3600" 
              placeholder="秒"
            />
            <span class="input-suffix">秒</span>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2: 创建方式 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="creation-methods">
          <el-radio-group v-model="formData.creationMethod" class="method-group">
            <div class="method-option">
              <el-radio value="blank" class="method-radio">
                <div class="method-content">
                  <div class="method-title">
                    <el-icon><DocumentAdd /></el-icon>
                    从空白开始
                  </div>
                  <div class="method-desc">创建全新的工作流，从零开始设计</div>
                </div>
              </el-radio>
            </div>
            
            <div class="method-option">
              <el-radio value="template" class="method-radio">
                <div class="method-content">
                  <div class="method-title">
                    <el-icon><Document /></el-icon>
                    从模板创建
                  </div>
                  <div class="method-desc">选择预定义模板快速创建</div>
                  <div v-if="formData.creationMethod === 'template'" class="template-selector">
                    <el-select v-model="formData.templateId" placeholder="请选择模板">
                      <el-option 
                        v-for="template in templates" 
                        :key="template.id" 
                        :label="template.name" 
                        :value="template.id" 
                      />
                    </el-select>
                  </div>
                </div>
              </el-radio>
            </div>
            
            <div class="method-option">
              <el-radio value="import" class="method-radio">
                <div class="method-content">
                  <div class="method-title">
                    <el-icon><Upload /></el-icon>
                    导入现有文件
                  </div>
                  <div class="method-desc">上传工作流配置文件 (JSON格式)</div>
                  <div v-if="formData.creationMethod === 'import'" class="file-upload">
                    <el-upload
                      ref="uploadRef"
                      :auto-upload="false"
                      :show-file-list="true"
                      :limit="1"
                      accept=".json"
                      @change="handleFileChange"
                    >
                      <el-button type="primary">选择文件</el-button>
                      <template #tip>
                        <div class="el-upload__tip">
                          只能上传JSON文件，且不超过2MB
                        </div>
                      </template>
                    </el-upload>
                  </div>
                </div>
              </el-radio>
            </div>
          </el-radio-group>
        </div>
      </div>

      <!-- 步骤3: 确认创建 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="confirmation-content">
          <div class="confirm-section">
            <h4>✓ 工作流信息确认</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">名称:</span>
                <span class="value">{{ formData.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">分类:</span>
                <span class="value">{{ getCategoryLabel(formData.category) }}</span>
              </div>
              <div class="info-item">
                <span class="label">关联应用:</span>
                <span class="value">{{ getAppName(formData.appId) || '无' }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建方式:</span>
                <span class="value">{{ getCreationMethodLabel(formData.creationMethod) }}</span>
              </div>
              <div class="info-item">
                <span class="label">优先级:</span>
                <span class="value">{{ getPriorityLabel(formData.priority) }}</span>
              </div>
              <div class="info-item">
                <span class="label">超时设置:</span>
                <span class="value">{{ formData.timeout }}秒</span>
              </div>
            </div>
          </div>

          <div v-if="formData.creationMethod === 'template' && selectedTemplate" class="confirm-section">
            <h4>✓ 模板预览</h4>
            <div class="template-preview">
              <div class="preview-item">
                <span class="label">包含节点:</span>
                <span class="value">{{ selectedTemplate.nodeDescription }}</span>
              </div>
              <div class="preview-item">
                <span class="label">预设参数:</span>
                <span class="value">{{ selectedTemplate.parameters }}</span>
              </div>
              <div class="preview-item">
                <span class="label">输出格式:</span>
                <span class="value">{{ selectedTemplate.outputFormat }}</span>
              </div>
            </div>
          </div>

          <div class="options-section">
            <el-checkbox v-model="formData.openDesigner">创建后立即打开设计器</el-checkbox>
            <el-checkbox v-model="formData.saveAsTemplate">保存为我的常用模板</el-checkbox>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="wizard-footer">
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="currentStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="currentStep === 2" type="primary" @click="createWorkflow" :loading="creating">
          创建工作流
        </el-button>
        <el-button @click="handleClose">取消</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentAdd, Document, Upload, Edit, Setting, Check } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'created'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const currentStep = ref(0)
const creating = ref(false)
const basicFormRef = ref()
const uploadRef = ref()

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  category: 'api_test',
  appId: '',
  tags: '',
  priority: 'medium',
  timeout: 300,
  creationMethod: 'blank',
  templateId: '',
  file: null,
  openDesigner: true,
  saveAsTemplate: false
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入工作流名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 模拟数据
const applications = ref([
  { id: '1', name: '前端管理系统' },
  { id: '2', name: '移动端应用' },
  { id: '3', name: '数据分析平台' }
])

const templates = ref([
  { 
    id: '1', 
    name: 'API接口测试',
    nodeDescription: '开始 → API调用 → 数据验证 → 结束',
    parameters: '请求超时30秒，重试3次',
    outputFormat: 'JSON响应数据'
  },
  { 
    id: '2', 
    name: '数据同步流程',
    nodeDescription: '开始 → 数据读取 → 数据转换 → 数据写入 → 结束',
    parameters: '批量处理1000条，失败重试',
    outputFormat: '同步结果报告'
  },
  { 
    id: '3', 
    name: '监控告警流程',
    nodeDescription: '开始 → 监控检查 → 条件判断 → 告警通知 → 结束',
    parameters: '检查间隔5分钟，告警阈值90%',
    outputFormat: '告警消息'
  }
])

const selectedTemplate = computed(() => {
  return templates.value.find(t => t.id === formData.templateId)
})

// 标签映射
const categoryLabels = {
  api_test: 'API测试',
  data_process: '数据处理',
  monitoring: '监控告警',
  deployment: '自动化部署',
  other: '其他'
}

const priorityLabels = {
  low: '低',
  medium: '中等',
  high: '高',
  urgent: '紧急'
}

const creationMethodLabels = {
  blank: '从空白开始',
  template: '从模板创建',
  import: '导入现有文件'
}

// 方法
const getCategoryLabel = (value) => categoryLabels[value] || value
const getPriorityLabel = (value) => priorityLabels[value] || value
const getCreationMethodLabel = (value) => creationMethodLabels[value] || value
const getAppName = (id) => applications.value.find(app => app.id === id)?.name

const nextStep = async () => {
  if (currentStep.value === 0) {
    // 验证基本信息
    if (!basicFormRef.value) return
    const valid = await basicFormRef.value.validate().catch(() => false)
    if (!valid) return
  }
  
  if (currentStep.value === 1) {
    // 验证创建方式
    if (formData.creationMethod === 'template' && !formData.templateId) {
      ElMessage.warning('请选择模板')
      return
    }
    if (formData.creationMethod === 'import' && !formData.file) {
      ElMessage.warning('请选择要导入的文件')
      return
    }
  }
  
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const handleFileChange = (file) => {
  formData.file = file.raw
}

const createWorkflow = async () => {
  creating.value = true
  
  try {
    // 模拟创建工作流
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const workflowData = {
      ...formData,
      id: Date.now().toString(),
      status: 'draft',
      createdAt: new Date().toISOString()
    }
    
    ElMessage.success('工作流创建成功！')
    emit('created', workflowData)
    handleClose()
    
    // 如果选择立即打开设计器
    if (formData.openDesigner) {
      // 这里可以跳转到设计器页面
      console.log('打开设计器:', workflowData)
    }
  } catch (error) {
    ElMessage.error('创建失败：' + error.message)
  } finally {
    creating.value = false
  }
}

const handleClose = () => {
  visible.value = false
  // 重置表单
  currentStep.value = 0
  Object.assign(formData, {
    name: '',
    description: '',
    category: 'api_test',
    appId: '',
    tags: '',
    priority: 'medium',
    timeout: 300,
    creationMethod: 'blank',
    templateId: '',
    file: null,
    openDesigner: true,
    saveAsTemplate: false
  })
}

// 监听创建方式变化，重置相关字段
watch(() => formData.creationMethod, (newValue) => {
  if (newValue !== 'template') {
    formData.templateId = ''
  }
  if (newValue !== 'import') {
    formData.file = null
  }
})
</script>

<style scoped>
.wizard-steps {
  margin-bottom: 30px;
}

.wizard-content {
  min-height: 400px;
  padding: 20px 0;
}

.step-content {
  max-width: 600px;
  margin: 0 auto;
}

.creation-methods {
  padding: 20px 0;
}

.method-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.method-option {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s;
}

.method-option:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.method-radio {
  width: 100%;
}

.method-content {
  margin-left: 30px;
}

.method-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.method-desc {
  color: #666;
  margin-bottom: 15px;
}

.template-selector,
.file-upload {
  margin-top: 15px;
}

.confirmation-content {
  padding: 20px 0;
}

.confirm-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.confirm-section h4 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-item,
.preview-item {
  display: flex;
  justify-content: space-between;
}

.label {
  font-weight: 600;
  color: #666;
}

.value {
  color: #333;
}

.template-preview {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.options-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px;
  background-color: #f0f9ff;
  border-radius: 8px;
}

.wizard-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.input-suffix {
  margin-left: 8px;
  color: #666;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #409eff;
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
  border-color: #409eff;
  background: #409eff;
}
</style>