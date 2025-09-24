<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    width="800px"
    :before-close="handleClose"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <el-form
      ref="formRef"
      :model="localFormData"
      :rules="rules"
      label-width="120px"
      label-position="left"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="API名称" prop="name">
            <el-input
              v-model="localFormData.name"
              placeholder="请输入API名称"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="请求方法" prop="method">
            <el-select
              v-model="localFormData.method"
              placeholder="选择请求方法"
              style="width: 100%"
            >
              <el-option
                v-for="method in httpMethods"
                :key="method.value"
                :label="method.label"
                :value="method.value"
              >
                <el-tag :type="method.type" size="small">{{ method.label }}</el-tag>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="URL路径" prop="url">
        <el-input
          v-model="localFormData.url"
          placeholder="请输入API路径，如：/api/users"
          clearable
        >
          <template #prepend>
            <span>{{ baseUrl }}</span>
          </template>
        </el-input>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="所属系统" prop="system_id">
            <el-select
              v-model="localFormData.system_id"
              placeholder="选择所属系统"
              style="width: 100%"
              @change="handleSystemChange"
            >
              <el-option
                v-for="system in systemList"
                :key="system.id"
                :label="system.name"
                :value="system.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="所属模块" prop="module_id">
            <el-select
              v-model="localFormData.module_id"
              placeholder="选择所属模块"
              style="width: 100%"
              :disabled="!localFormData.system_id"
            >
              <el-option
                v-for="module in availableModules"
                :key="module.id"
                :label="module.name"
                :value="module.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="API描述" prop="description">
        <el-input
          v-model="localFormData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入API功能描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="状态">
        <el-switch
          v-model="localFormData.enabled"
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>

      <!-- 请求参数配置 -->
      <el-form-item label="请求参数">
        <div class="params-section">
          <div class="params-header">
            <el-button
              type="primary"
              size="small"
              @click="addParameter"
            >
              <el-icon><Plus /></el-icon>
              添加参数
            </el-button>
          </div>
          
          <div v-if="localFormData.parameters && localFormData.parameters.length > 0" class="params-list">
            <div
              v-for="(param, index) in localFormData.parameters"
              :key="index"
              class="param-row"
            >
              <el-input
                v-model="param.name"
                placeholder="参数名"
                style="width: 150px"
              />
              <el-select
                v-model="param.type"
                placeholder="类型"
                style="width: 100px"
              >
                <el-option label="string" value="string" />
                <el-option label="number" value="number" />
                <el-option label="boolean" value="boolean" />
                <el-option label="object" value="object" />
                <el-option label="array" value="array" />
              </el-select>
              <el-switch
                v-model="param.required"
                active-text="必填"
                inactive-text="可选"
                size="small"
              />
              <el-input
                v-model="param.description"
                placeholder="参数描述"
                style="flex: 1"
              />
              <el-button
                type="danger"
                size="small"
                @click="removeParameter(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- 响应示例 -->
      <el-form-item label="响应示例">
        <el-input
          v-model="localFormData.response_example"
          type="textarea"
          :rows="4"
          placeholder="请输入响应示例（JSON格式）"
        />
      </el-form-item>

      <!-- 标签 -->
      <el-form-item label="标签">
        <el-select
          v-model="localFormData.tags"
          multiple
          filterable
          allow-create
          placeholder="选择或创建标签"
          style="width: 100%"
        >
          <el-option
            v-for="tag in predefinedTags"
            :key="tag"
            :label="tag"
            :value="tag"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import unifiedApi from '@/api/unified-api'

// 直接使用统一API
const apiProxy = unifiedApi

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '新增API'
  },
  formData: {
    type: Object,
    default: () => ({})
  },
  systemList: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

// 响应式数据
const formRef = ref()
const saving = ref(false)
const moduleList = ref([])

// 本地表单数据
const localFormData = reactive({
  id: '',
  name: '',
  description: '',
  url: '',
  method: 'GET',
  system_id: '',
  module_id: '',
  enabled: true,
  parameters: [],
  response_example: '',
  tags: []
})

// HTTP方法选项
const httpMethods = [
  { label: 'GET', value: 'GET', type: 'success' },
  { label: 'POST', value: 'POST', type: 'primary' },
  { label: 'PUT', value: 'PUT', type: 'warning' },
  { label: 'DELETE', value: 'DELETE', type: 'danger' },
  { label: 'PATCH', value: 'PATCH', type: 'info' }
]

// 预定义标签
const predefinedTags = [
  '用户管理', '订单管理', '商品管理', '支付管理',
  '系统管理', '日志管理', '通知管理', '报表管理',
  '认证授权', '数据查询', '数据更新', '文件上传'
]

// 基础URL
const baseUrl = computed(() => {
  return 'http://localhost:8000'
})

// 可用模块
const availableModules = computed(() => {
  if (!localFormData.system_id) return []
  return moduleList.value.filter(module => module.system_id === localFormData.system_id)
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入API名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入URL路径', trigger: 'blur' },
    { pattern: /^\//, message: 'URL路径必须以 / 开头', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  system_id: [
    { required: true, message: '请选择所属系统', trigger: 'change' }
  ],
  module_id: [
    { required: true, message: '请选择所属模块', trigger: 'change' }
  ]
}

// 监听表单数据变化
watch(() => props.formData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    const oldSystemId = localFormData.system_id
    Object.assign(localFormData, {
      id: newData.id || '',
      name: newData.name || '',
      description: newData.description || '',
      url: newData.url || '',
      method: newData.method || 'GET',
      system_id: newData.system_id || '',
      module_id: newData.module_id || '',
      enabled: newData.enabled !== undefined ? newData.enabled : true,
      parameters: newData.parameters || [],
      response_example: newData.response_example || '',
      tags: newData.tags || []
    })
    
    // 如果系统ID发生变化，重新加载模块列表
    if (localFormData.system_id && localFormData.system_id !== oldSystemId) {
      loadModuleList(localFormData.system_id)
    }
  } else {
    // 使用nextTick确保组件已挂载后再重置表单
    nextTick(() => {
      resetForm()
    })
  }
}, { immediate: true, deep: true })

// 监听弹框显示状态
watch(() => props.modelValue, (newValue) => {
  if (newValue && localFormData.system_id) {
    // 弹框打开且有系统ID时，立即加载该系统的模块列表
    loadModuleList(localFormData.system_id)
  }
})

// 方法
const loadModuleList = async (systemId = null) => {
  try {
    const params = {}
    if (systemId) {
      params.system_id = systemId
    }
    
    const response = await apiProxy.getModuleList(params)
    if (response.success && Array.isArray(response.data)) {
      moduleList.value = response.data.map(module => ({
        id: module.id,
        name: module.name,
        system_id: module.system_uuid || module.system_id,
        description: module.description,
        enabled: module.enabled
      }))
    } else {
      moduleList.value = []
    }
  } catch (error) {
    console.error('加载模块列表失败:', error)
    moduleList.value = []
  }
}

const handleSystemChange = () => {
  // 清空模块选择
  localFormData.module_id = ''
  // 重新加载该系统下的模块数据
  if (localFormData.system_id) {
    loadModuleList(localFormData.system_id)
  } else {
    moduleList.value = []
  }
}

const addParameter = () => {
  localFormData.parameters.push({
    name: '',
    type: 'string',
    required: false,
    description: ''
  })
}

const removeParameter = (index) => {
  localFormData.parameters.splice(index, 1)
}

const resetForm = () => {
  try {
    // 安全重置表单数据
    Object.assign(localFormData, {
      id: '',
      name: '',
      description: '',
      url: '',
      method: 'GET',
      system_id: '',
      module_id: '',
      enabled: true,
      parameters: [],
      response_example: '',
      tags: []
    })
  } catch (error) {
    console.warn('重置表单数据失败:', error)
    // 逐个赋值作为备选方案
    localFormData.id = ''
    localFormData.name = ''
    localFormData.description = ''
    localFormData.url = ''
    localFormData.method = 'GET'
    localFormData.system_id = ''
    localFormData.module_id = ''
    localFormData.enabled = true
    localFormData.parameters = []
    localFormData.response_example = ''
    localFormData.tags = []
  }
  
  // 使用nextTick确保DOM更新完成后再清除验证
  nextTick(() => {
    try {
      // 多重检查确保formRef存在且有效
      if (formRef.value && 
          typeof formRef.value === 'object' && 
          formRef.value.clearValidate && 
          typeof formRef.value.clearValidate === 'function') {
        formRef.value.clearValidate()
      }
    } catch (error) {
      console.warn('清除表单验证失败:', error)
    }
  })
}

const handleClose = () => {
  emit('update:modelValue', false)
  emit('cancel')
}

const handleSave = async () => {
  if (!formRef.value || !formRef.value.validate) {
    ElMessage.error('表单未初始化，请稍后重试')
    return
  }

  try {
    // 表单验证
    const valid = await formRef.value.validate()
    if (!valid) {
      ElMessage.warning('请检查表单填写是否正确')
      return
    }

    saving.value = true

    // 验证URL格式
    if (localFormData.url && !localFormData.url.startsWith('/')) {
      ElMessage.warning('URL路径应以 / 开头')
      saving.value = false
      return
    }

    // 验证响应示例JSON格式
    if (localFormData.response_example) {
      try {
        JSON.parse(localFormData.response_example)
      } catch (error) {
        ElMessage.warning('响应示例必须是有效的JSON格式')
        saving.value = false
        return
      }
    }

    // 准备保存数据
    const saveData = {
      ...localFormData,
      // 字段映射：前端url字段映射为后端path字段
      path: localFormData.url,
      // 添加后端期望的默认字段
      version: localFormData.version || '1.0.0',
      order_index: localFormData.order_index || 0,
      // 处理参数数据
      request_params: localFormData.parameters ? 
        localFormData.parameters.filter(param => param.name.trim()).reduce((acc, param) => {
          acc[param.name] = {
            type: param.type || 'string',
            required: param.required || false,
            description: param.description || ''
          }
          return acc
        }, {}) : {},
      // 解析响应示例
      response_example: localFormData.response_example ? 
        (() => {
          try {
            return JSON.parse(localFormData.response_example)
          } catch {
            return localFormData.response_example
          }
        })() : null
    }
    
    // 删除前端专用字段，避免后端接收到不期望的字段
    delete saveData.url
    delete saveData.parameters

    emit('save', saveData)
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
    saving.value = false
  }
}

// 生命周期
onMounted(() => {
  // 初始加载所有模块列表
  loadModuleList()
})
</script>

<style scoped>
.params-section {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.params-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.params-header {
  margin-bottom: 16px;
  font-weight: 600;
  color: #303133;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.param-row:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
  margin-top: 20px;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  padding: 24px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

:deep(.el-dialog__body) {
  padding: 24px;
  background: #fafbfc;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.el-textarea__inner:hover) {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  padding: 12px 24px;
  transition: all 0.2s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-tag) {
  border-radius: 16px;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}
</style>