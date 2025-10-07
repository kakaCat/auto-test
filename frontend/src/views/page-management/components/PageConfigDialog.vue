<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑页面配置' : '新增页面配置'"
    width="90%"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="page-config-dialog"
    @close="handleClose"
  >
    <!-- 步骤导航 -->
    <div class="step-navigation">
      <el-steps
        :active="currentStep"
        align-center
        finish-status="success"
      >
        <el-step
          title="页面基本信息"
          description="配置页面基础信息"
        >
          <template #icon>
            <el-icon
              v-if="stepSaveStatus.basic === 'completed'"
              color="#67c23a"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else-if="stepSaveStatus.basic === 'draft'"
              color="#e6a23c"
            >
              <Edit />
            </el-icon>
          </template>
        </el-step>
        <el-step
          title="页面布局设计"
          description="设计页面布局和组件"
        >
          <template #icon>
            <el-icon
              v-if="stepSaveStatus.layout === 'completed'"
              color="#67c23a"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else-if="stepSaveStatus.layout === 'draft'"
              color="#e6a23c"
            >
              <Edit />
            </el-icon>
          </template>
        </el-step>
        <el-step
          title="API配置"
          description="配置API调用和参数"
        >
          <template #icon>
            <el-icon
              v-if="stepSaveStatus.api === 'completed'"
              color="#67c23a"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else-if="stepSaveStatus.api === 'draft'"
              color="#e6a23c"
            >
              <Edit />
            </el-icon>
          </template>
        </el-step>
        <el-step
          title="页面交互设置"
          description="设置交互事件和流程"
        >
          <template #icon>
            <el-icon
              v-if="stepSaveStatus.interaction === 'completed'"
              color="#67c23a"
            >
              <Check />
            </el-icon>
            <el-icon
              v-else-if="stepSaveStatus.interaction === 'draft'"
              color="#e6a23c"
            >
              <Edit />
            </el-icon>
          </template>
        </el-step>
      </el-steps>
      
      <!-- 保存状态提示 -->
      <div
        v-if="lastSavedAt"
        class="save-status"
      >
        <el-text
          size="small"
          type="info"
        >
          <el-icon><Clock /></el-icon>
          最后保存时间：{{ lastSavedAt }}
        </el-text>
      </div>
      
      <!-- 自动保存提示 -->
      <div
        v-if="autoSaving"
        class="auto-saving"
      >
        <el-text
          size="small"
          type="primary"
        >
          <el-icon class="is-loading">
            <Loading />
          </el-icon>
          正在保存...
        </el-text>
      </div>
    </div>

    <!-- 步骤内容区域 -->
    <div class="step-content">
      <!-- 步骤1: 页面基本信息 -->
      <div
        v-show="currentStep === 0"
        class="step-panel"
      >
        <PageBasicInfo
          ref="basicInfoRef"
          v-model="formData.basicInfo"
          :is-edit="isEdit"
          @validate="handleStepValidate"
        />
      </div>

      <!-- 步骤2: 页面布局设计 -->
      <div
        v-show="currentStep === 1"
        class="step-panel"
      >
        <PageLayoutDesigner
          ref="layoutRef"
          v-model="formData.layout"
          @validate="handleStepValidate"
        />
      </div>

      <!-- 步骤3: API配置 -->
      <div
        v-show="currentStep === 2"
        class="step-panel"
      >
        <PageApiConfig
          ref="apiConfigRef"
          v-model="formData.apiConfig"
          :system-id="formData.basicInfo.systemId"
          @validate="handleStepValidate"
        />
      </div>

      <!-- 步骤4: 页面交互设置 -->
      <div
        v-show="currentStep === 3"
        class="step-panel"
      >
        <PageInteractionConfig
          ref="interactionRef"
          v-model="formData.interaction"
          :layout-components="formData.layout.components"
          :api-list="formData.apiConfig.apis"
          @validate="handleStepValidate"
        />
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <el-button @click="handleClose">
            取消
          </el-button>
          <el-button 
            v-if="currentStep > 0" 
            @click="prevStep"
          >
            上一步
          </el-button>
        </div>
        <div class="footer-right">
          <el-button 
            v-if="currentStep < 3" 
            type="primary" 
            :disabled="!stepValidated[currentStep]"
            @click="nextStep"
          >
            下一步
          </el-button>
          <el-button 
            v-else 
            type="primary" 
            :loading="saving"
            :disabled="!allStepsValid"
            @click="handleSave"
          >
            确认保存
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Edit, Clock, Loading } from '@element-plus/icons-vue'
import PageBasicInfo from './steps/PageBasicInfo.vue'
import PageLayoutDesigner from './steps/PageLayoutDesigner.vue'
import PageApiConfig from './steps/PageApiConfig.vue'
import PageInteractionConfig from './steps/PageInteractionConfig.vue'
import type { PageConfigData } from '../types/page-config'

interface Props {
  modelValue: boolean
  pageData?: any
  isEdit?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', data: PageConfigData): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  pageData: null,
  isEdit: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const dialogVisible = ref(false)
const currentStep = ref(0)
const saving = ref(false)
const autoSaving = ref(false)

// 步骤验证状态
const stepValidated = reactive([false, false, false, false])

// 分步保存状态
const pageId = ref<number | null>(null)
const stepSaveStatus = reactive({
  basic: 'pending' as 'pending' | 'draft' | 'completed',
  layout: 'pending' as 'pending' | 'draft' | 'completed',
  api: 'pending' as 'pending' | 'draft' | 'completed',
  interaction: 'pending' as 'pending' | 'draft' | 'completed'
})
const lastSavedAt = ref<string>('')

// 表单数据
const formData = reactive<PageConfigData>({
  basicInfo: {
    name: '',
    path: '',
    description: '',
    type: 'normal',
    icon: '',
    enabled: true,
    systemId: null,
    moduleId: null
  },
  layout: {
    components: [],
    canvas: {
      width: 1200,
      height: 800,
      scale: 1,
      grid: true
    }
  },
  apiConfig: {
    apis: [],
    flowChart: {
      nodes: [],
      edges: []
    }
  },
  interaction: {
    events: [],
    flowChart: {
      nodes: [],
      edges: []
    }
  }
})

// 组件引用
const basicInfoRef = ref()
const layoutRef = ref()
const apiConfigRef = ref()
const interactionRef = ref()

// 计算属性
const allStepsValid = computed(() => {
  return stepValidated.every(valid => valid)
})

// 监听对话框显示状态
watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    initDialog()
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 初始化对话框
const initDialog = async () => {
  // 重置状态
  stepValidated.fill(false)
  pageId.value = null
  stepSaveStatus.basic = 'pending'
  stepSaveStatus.layout = 'pending'
  stepSaveStatus.api = 'pending'
  stepSaveStatus.interaction = 'pending'
  lastSavedAt.value = ''
  
  if (props.isEdit && props.pageData) {
    // 编辑模式：填充现有数据和加载进度
    pageId.value = props.pageData.id
    await loadPageData(props.pageData)
    
    // 加载保存进度
    if (pageId.value) {
      const progress = await loadPageProgress(pageId.value)
      if (progress) {
        currentStep.value = progress.current_step || 0
      } else {
        currentStep.value = 0
      }
    } else {
      currentStep.value = 0
    }
  } else {
    // 新增模式：重置表单
    currentStep.value = 0
    resetFormData()
  }
}

// 加载页面数据（编辑模式）
const loadPageData = async (pageData: any) => {
  try {
    // 填充基本信息
    formData.basicInfo = {
      name: pageData.name || '',
      path: pageData.path || '',
      description: pageData.description || '',
      type: pageData.type || 'normal',
      icon: pageData.icon || '',
      enabled: pageData.enabled !== false,
      systemId: pageData.system_id || null,
      moduleId: pageData.module_id || null
    }

    // 填充布局数据
    if (pageData.layout) {
      formData.layout = pageData.layout
    }

    // 填充API配置
    if (pageData.apiConfig) {
      formData.apiConfig = pageData.apiConfig
    }

    // 填充交互配置
    if (pageData.interaction) {
      formData.interaction = pageData.interaction
    }

    // 等待组件渲染完成后验证
    await nextTick()
    validateAllSteps()
  } catch (error) {
    console.error('加载页面数据失败:', error)
    ElMessage.error('加载页面数据失败')
  }
}

// 重置表单数据
const resetFormData = () => {
  formData.basicInfo = {
    name: '',
    path: '',
    description: '',
    type: 'normal',
    icon: '',
    enabled: true,
    systemId: null,
    moduleId: null
  }
  formData.layout = {
    components: [],
    canvas: {
      width: 1200,
      height: 800,
      scale: 1,
      grid: true
    }
  }
  formData.apiConfig = {
    systemId: null,
    moduleId: null,
    apis: [],
    flowChart: {
      nodes: [],
      edges: []
    }
  }
  formData.interaction = {
    events: [],
    flowChart: {
      nodes: [],
      edges: []
    }
  }
}

// 步骤验证处理
const handleStepValidate = (stepIndex: number, isValid: boolean) => {
  stepValidated[stepIndex] = isValid
}

// 验证所有步骤
const validateAllSteps = async () => {
  const refs = [basicInfoRef, layoutRef, apiConfigRef, interactionRef]
  
  for (let i = 0; i < refs.length; i++) {
    if (refs[i].value && typeof refs[i].value.validate === 'function') {
      try {
        const isValid = await refs[i].value.validate()
        stepValidated[i] = isValid
      } catch (error) {
        stepValidated[i] = false
      }
    }
  }
}

// 下一步
const nextStep = async () => {
  // 验证当前步骤
  const currentRef = getCurrentStepRef()
  if (currentRef && typeof currentRef.validate === 'function') {
    try {
      const isValid = await currentRef.validate()
      if (!isValid) {
        ElMessage.warning('请完善当前步骤的配置')
        return
      }
    } catch (error) {
      ElMessage.error('验证失败，请检查配置')
      return
    }
  }

  // 保存当前步骤数据
  await saveCurrentStep()

  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 获取当前步骤的组件引用
const getCurrentStepRef = () => {
  const refs = [basicInfoRef, layoutRef, apiConfigRef, interactionRef]
  return refs[currentStep.value]?.value
}

// 分步保存方法
const saveCurrentStep = async () => {
  try {
    autoSaving.value = true
    const stepNames = ['basic', 'layout', 'api', 'interaction']
    const currentStepName = stepNames[currentStep.value]
    
    let stepData: any = {}
    let apiEndpoint = ''
    
    // 根据当前步骤准备数据和API端点
    switch (currentStep.value) {
      case 0: // 基本信息
        stepData = formData.basicInfo
        apiEndpoint = pageId.value ? `/api/pages/${pageId.value}/basic` : '/api/pages/basic'
        break
      case 1: // 布局设计
        stepData = formData.layout
        apiEndpoint = `/api/pages/${pageId.value}/layout`
        break
      case 2: // API配置
        stepData = formData.apiConfig
        apiEndpoint = `/api/pages/${pageId.value}/api-config`
        break
      case 3: // 交互设置
        stepData = formData.interaction
        apiEndpoint = `/api/pages/${pageId.value}/interaction`
        break
    }

    // 调用API保存步骤数据
    const response = await fetch(apiEndpoint, {
      method: pageId.value ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(stepData)
    })

    if (response.ok) {
      const result = await response.json()
      
      // 如果是新建页面，保存页面ID
      if (!pageId.value && result.page_id) {
        pageId.value = result.page_id
      }
      
      // 更新步骤状态
      stepSaveStatus[currentStepName as keyof typeof stepSaveStatus] = 'completed'
      lastSavedAt.value = new Date().toLocaleString()
      
      ElMessage.success(`${getStepTitle(currentStep.value)}已保存`)
    } else {
      throw new Error('保存失败')
    }
  } catch (error) {
    console.error('分步保存失败:', error)
    ElMessage.error('保存失败，请重试')
    
    // 标记为草稿状态
    const stepNames = ['basic', 'layout', 'api', 'interaction']
    const currentStepName = stepNames[currentStep.value]
    stepSaveStatus[currentStepName as keyof typeof stepSaveStatus] = 'draft'
  } finally {
    autoSaving.value = false
  }
}

// 获取步骤标题
const getStepTitle = (step: number) => {
  const titles = ['页面基本信息', '页面布局设计', 'API配置', '页面交互设置']
  return titles[step] || ''
}

// 加载页面进度
const loadPageProgress = async (pageId: number) => {
  try {
    const response = await fetch(`/api/pages/${pageId}/progress`)
    if (response.ok) {
      const progress = await response.json()
      
      // 更新步骤状态
      Object.assign(stepSaveStatus, progress.step_status)
      currentStep.value = progress.current_step || 0
      lastSavedAt.value = progress.last_saved_at || ''
      
      return progress
    }
  } catch (error) {
    console.error('加载页面进度失败:', error)
  }
  return null
}

// 保存配置
const handleSave = async () => {
  try {
    saving.value = true
    
    // 验证所有步骤
    await validateAllSteps()
    
    if (!allStepsValid.value) {
      ElMessage.warning('请完善所有步骤的配置')
      return
    }

    // 保存当前步骤（如果还没保存）
    if (stepSaveStatus.interaction !== 'completed') {
      await saveCurrentStep()
    }

    // 完成页面配置
    if (pageId.value) {
      const response = await fetch(`/api/pages/${pageId.value}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        ElMessage.success('页面配置已完成')
        
        // 发送保存事件
        emit('save', { ...formData, id: pageId.value })
        
        // 关闭对话框
        handleClose()
      } else {
        throw new Error('完成配置失败')
      }
    } else {
      // 如果没有pageId，直接发送保存事件（兼容旧逻辑）
      emit('save', formData)
    }
    
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  emit('close')
}

// 暴露方法给父组件
defineExpose({
  open: () => {
    dialogVisible.value = true
  },
  close: () => {
    dialogVisible.value = false
  }
})
</script>

<style lang="scss" scoped>
.page-config-dialog {
  .step-navigation {
    margin-bottom: 30px;
    padding: 0 20px;
    
    .save-status {
      margin-top: 16px;
      text-align: center;
      
      .el-icon {
        margin-right: 4px;
      }
    }
    
    .auto-saving {
      margin-top: 12px;
      text-align: center;
      
      .el-icon {
        margin-right: 4px;
      }
    }
  }

  .step-content {
    min-height: 500px;
    max-height: 70vh;
    overflow-y: auto;
    padding: 0 20px;
  }

  .step-panel {
    width: 100%;
  }

  .dialog-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 0 0;
    border-top: 1px solid #e4e7ed;

    .footer-left,
    .footer-right {
      display: flex;
      gap: 12px;
    }
  }
}

:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 0;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 0 20px 20px;
}

:deep(.el-steps) {
  .el-step__title {
    font-size: 14px;
    font-weight: 500;
  }
  
  .el-step__description {
    font-size: 12px;
    color: #909399;
  }
}
</style>