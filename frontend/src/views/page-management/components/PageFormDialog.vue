<template>
  <el-dialog
    :model-value="visible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
  >
    <el-steps
      :active="currentStep"
      finish-status="success"
      align-center
      style="margin-bottom: 16px;"
    >
      <el-step title="基本信息" />
      <el-step title="API接口" />
      <el-step title="布局设计" />
      <el-step title="交互设计" />
    </el-steps>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent
    >
      <template v-if="currentStep === 1">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item
              label="所属系统"
              prop="system_id"
            >
              <el-select
                v-model="form.system_id"
                placeholder="请选择所属系统"
                style="width: 100%"
                :disabled="mode === 'edit'"
                @change="handleSystemChange"
              >
                <el-option
                  v-for="system in systems"
                  :key="system.id"
                  :label="system.name"
                  :value="system.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item
              label="所属模块"
              prop="module_id"
            >
              <el-select
                v-model="form.module_id"
                placeholder="请选择所属模块"
                style="width: 100%"
                :disabled="!form.system_id"
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

        <el-form-item
          label="页面名称"
          prop="name"
        >
          <el-input
            v-model="form.name"
            placeholder="请输入页面名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item
          label="页面描述"
          prop="description"
        >
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入页面描述"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item
          label="路由路径"
          prop="route_path"
        >
          <el-input
            v-model="form.route_path"
            placeholder="请输入路由路径，如：/users"
            maxlength="200"
          >
            <template #prepend>
              <span>/</span>
            </template>
          </el-input>
          <div class="form-tip">
            页面的访问路径，留空表示无独立路由（如弹框、抽屉等）
          </div>
        </el-form-item>

        <el-form-item
          label="页面类型"
          prop="page_type"
        >
          <el-radio-group v-model="form.page_type">
            <el-radio label="page">
              页面
            </el-radio>
            <el-radio label="modal">
              弹框
            </el-radio>
            <el-radio label="drawer">
              抽屉
            </el-radio>
            <el-radio label="tab">
              标签页
            </el-radio>
            <el-radio label="step">
              步骤页
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item
          label="状态"
          prop="status"
        >
          <el-radio-group v-model="form.status">
            <el-radio label="active">
              活跃
            </el-radio>
            <el-radio label="inactive">
              非活跃
            </el-radio>
            <el-radio label="draft">
              草稿
            </el-radio>
          </el-radio-group>
        </el-form-item>
      </template>

      <!-- API管理区域 -->
      <template v-if="currentStep === 2">
        <el-divider content-position="left">
          <span style="font-weight: 600; color: var(--el-color-primary);">API调用配置</span>
        </el-divider>

        <div class="api-management-section">
          <div class="api-header">
            <span class="api-title">关联API列表</span>
            <el-button
              type="primary"
              size="small"
              @click="showAddApiDialog"
            >
              <el-icon><Plus /></el-icon>
              添加API
            </el-button>
          </div>

          <!-- API列表 -->
          <div
            v-if="form.apis && form.apis.length > 0"
            class="api-list"
          >
            <div 
              v-for="(api, index) in form.apis" 
              :key="index"
              class="api-item"
            >
              <div class="api-info">
                <div class="api-name">
                  <el-icon class="api-icon">
                    <Link />
                  </el-icon>
                  <span>{{ api.name }}</span>
                  <el-tag
                    :type="getMethodTagType(api.method)"
                    size="small"
                  >
                    {{ api.method }}
                  </el-tag>
                </div>
                <div class="api-path">
                  {{ api.path }}
                </div>
              </div>
            
              <div class="api-relation">
                <el-select 
                  v-model="api.relation_type" 
                  size="small" 
                  style="width: 100px;"
                  @change="updateApiRelation(index)"
                >
                  <el-option
                    label="串行"
                    value="serial"
                  />
                  <el-option
                    label="并行"
                    value="parallel"
                  />
                </el-select>
              </div>
            
              <div class="api-actions">
                <el-button
                  type="text"
                  size="small"
                  @click="editApi(index)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button
                  type="text"
                  size="small"
                  style="color: var(--el-color-danger);"
                  @click="removeApi(index)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div
            v-else
            class="api-empty"
          >
            <el-empty
              description="暂无关联API"
              :image-size="80"
            >
              <el-button
                type="primary"
                @click="showAddApiDialog"
              >
                添加第一个API
              </el-button>
            </el-empty>
          </div>
        </div>
      </template>

      <template v-if="currentStep === 3">
        <el-empty
          description="布局设计占位（后续接入可视化编辑器）"
          :image-size="80"
        />
      </template>

      <template v-if="currentStep === 4">
        <el-empty
          description="交互设计占位（后续接入交互配置）"
          :image-size="80"
        />
      </template>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">
          取消
        </el-button>
        <el-button
          v-if="currentStep > 1"
          @click="prevStep"
        >
          上一步
        </el-button>
        <el-button
          v-if="currentStep < 4"
          type="primary"
          @click="nextStep"
        >
          下一步
        </el-button>
        <el-button
          v-else
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ mode === 'create' ? '完成创建' : '完成更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- API选择对话框 -->
  <el-dialog
    v-model="apiDialogVisible"
    title="选择API"
    width="800px"
    :close-on-click-modal="false"
  >
    <div class="api-selection">
      <!-- 搜索区域 -->
      <div class="search-section">
        <el-input
          v-model="apiSearchKeyword"
          placeholder="搜索API..."
          style="width: 300px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- API列表 -->
      <div class="api-table-container">
        <el-table
          :data="filteredAvailableApis"
          style="width: 100%"
          max-height="400px"
          @selection-change="handleApiSelection"
        >
          <el-table-column
            type="selection"
            width="55"
          />
          <el-table-column
            prop="name"
            label="API名称"
            min-width="150"
          />
          <el-table-column
            prop="method"
            label="方法"
            width="80"
          >
            <template #default="{ row }">
              <el-tag
                :type="getMethodTagType(row.method)"
                size="small"
              >
                {{ row.method }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="path"
            label="路径"
            min-width="200"
          />
          <el-table-column
            prop="system_name"
            label="所属系统"
            width="120"
          />
          <el-table-column
            prop="module_name"
            label="所属模块"
            width="120"
          />
        </el-table>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="apiDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :disabled="selectedApis.length === 0"
          @click="confirmAddApis"
        >
          添加选中的API ({{ selectedApis.length }})
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Link, Edit, Delete, Search } from '@element-plus/icons-vue'
import { pageApi } from '@/api/page-management'
import { apiManagementApi, moduleApi } from '@/api/unified-api'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  page: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create' // create, edit
  },
  systems: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const formRef = ref()
const submitting = ref(false)
const currentStep = ref(1)

// 模块和API相关数据
const moduleList = ref([])
const availableApis = ref([])
const apiDialogVisible = ref(false)
const apiSearchKeyword = ref('')
const selectedApis = ref([])

const form = reactive({
  system_id: null,
  module_id: null,
  name: '',
  description: '',
  route_path: '',
  page_type: 'page',
  status: 'active',
  apis: [] // API列表
})

// 表单验证规则
const rules = {
  system_id: [
    { required: true, message: '请选择所属系统', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入页面名称', trigger: 'blur' },
    { min: 1, max: 100, message: '页面名称长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  page_type: [
    { required: true, message: '请选择页面类型', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  return props.mode === 'create' ? '创建页面' : '编辑页面'
})

// 根据选中的系统筛选模块
const availableModules = computed(() => {
  if (!form.system_id) {
    return []
  }
  return moduleList.value.filter(module => module.system_id === form.system_id)
})

// 根据搜索关键词筛选可用API
const filteredAvailableApis = computed(() => {
  let apis = availableApis.value

  if (apiSearchKeyword.value.trim()) {
    const keyword = apiSearchKeyword.value.toLowerCase().trim()
    apis = apis.filter(api =>
      (api.name || '').toLowerCase().includes(keyword) ||
      ((api.url || api.path || '')).toLowerCase().includes(keyword) ||
      (api.method || '').toLowerCase().includes(keyword)
    )
  }

  return apis
})

// 监听器
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      resetForm()
      // 加载必要的数据
      loadModuleList()
      loadAvailableApis()
      
      if (props.page && props.mode === 'edit') {
        // 编辑模式，填充表单数据
        Object.assign(form, {
          system_id: props.page.system_id,
          name: props.page.name,
          description: props.page.description || '',
          route_path: props.page.route_path || '',
          page_type: props.page.page_type,
          status: props.page.status
        })
      } else if (props.page && props.mode === 'create') {
        // 复制模式，填充部分数据
        Object.assign(form, {
          system_id: props.page.system_id,
          name: props.page.name,
          description: props.page.description || '',
          route_path: props.page.route_path || '',
          page_type: props.page.page_type,
          status: 'draft' // 复制的页面默认为草稿状态
        })
      }
    }
  },
  { immediate: true }
)

// 系统/模块变化时刷新可用API
watch(() => form.system_id, () => {
  form.module_id = null
  loadAvailableApis()
})
watch(() => form.module_id, () => {
  loadAvailableApis()
})

// 方法
const resetForm = () => {
  Object.assign(form, {
    system_id: null,
    module_id: null,
    name: '',
    description: '',
    route_path: '',
    page_type: 'page',
    status: 'active',
    apis: []
  })
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 加载模块列表
const loadModuleList = async () => {
  try {
    const response = await moduleApi.getList()
    if (response.success) {
      moduleList.value = response.data
    }
  } catch (error) {
    console.error('加载模块列表失败:', error)
  }
}

// 系统变化处理
const handleSystemChange = () => {
  form.module_id = null // 清空模块选择
}

// 获取HTTP方法标签类型
const getMethodTagType = (method) => {
  const typeMap = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return typeMap[method] || 'info'
}

// 显示添加API对话框
const showAddApiDialog = () => {
  apiDialogVisible.value = true
}

// 更新API关系
const updateApiRelation = (index) => {
  // API关系变化时的处理逻辑
  console.log('API关系更新:', form.apis[index])
}

// 编辑API
const editApi = (index) => {
  // 编辑API的逻辑
  console.log('编辑API:', form.apis[index])
}

// 移除API
const removeApi = (index) => {
  form.apis.splice(index, 1)
}

// 处理API选择
const handleApiSelection = (selection) => {
  selectedApis.value = selection
}

// 确认添加API
const confirmAddApis = () => {
  selectedApis.value.forEach(api => {
    // 检查是否已经添加过
    const exists = form.apis.some(existingApi => existingApi.id === api.id)
    if (!exists) {
      form.apis.push({
        id: api.id,
        name: api.name,
        method: api.method,
        path: api.url || api.path,
        system_name: api.system_name,
        module_name: api.module_name,
        relation_type: 'serial', // 默认串行调用
        order: form.apis.length + 1 // 调用顺序
      })
    }
  })
  
  apiDialogVisible.value = false
  selectedApis.value = []
  apiSearchKeyword.value = ''
}

// 加载可用API列表（按系统/模块过滤，并统一映射path→url）
const loadAvailableApis = async () => {
  try {
    const params = {}
    if (form.system_id) params.system_id = form.system_id
    if (form.module_id) params.module_id = form.module_id

    const response = await apiManagementApi.getApis(params)
    if (response.success) {
      const data = Array.isArray(response.data) ? response.data : (response.data?.list ?? [])
      availableApis.value = data.map(api => ({
        ...api,
        url: api.url ?? api.path ?? ''
      }))
    }
  } catch (error) {
    console.error('加载API列表失败:', error)
  }
}

const handleCancel = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  try {
    // 表单验证
    await formRef.value.validate()
    
    submitting.value = true
    
    // 处理路由路径
    let routePath = form.route_path.trim()
    if (routePath && !routePath.startsWith('/')) {
      routePath = '/' + routePath
    }
    
    const submitData = {
      ...form,
      route_path: routePath || null
    }
    
    let response
    if (props.mode === 'create') {
      // 创建页面
      response = await pageApi.createPage(submitData)
    } else {
      // 更新页面
      response = await pageApi.updatePage(props.page.id, submitData)
    }
    
    if (!response.success) {
      throw new Error(response.message || '操作失败')
    }
    
    emit('success')
    
  } catch (error) {
    if (error.message) {
      console.error('提交失败:', error)
      ElMessage.error('提交失败: ' + error.message)
    }
  } finally {
    submitting.value = false
  }
}

// 步骤切换
const nextStep = async () => {
  if (currentStep.value === 1) {
    await formRef.value.validateField(['system_id', 'name'])
    // 进入API步骤前刷新可用API
    await loadAvailableApis()
  }
  currentStep.value = Math.min(currentStep.value + 1, 4)
}

const prevStep = () => {
  currentStep.value = Math.max(currentStep.value - 1, 1)
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-input-group__prepend) {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #606266;
}

/* API管理区域样式 */
.api-management-section {
  margin-top: 16px;
}

.api-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.api-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.api-list {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
}

.api-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background-color 0.3s;
}

.api-item:last-child {
  border-bottom: none;
}

.api-item:hover {
  background-color: var(--el-fill-color-light);
}

.api-info {
  flex: 1;
}

.api-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.api-icon {
  color: var(--el-color-primary);
}

.api-path {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.api-relation {
  margin: 0 16px;
}

.api-actions {
  display: flex;
  gap: 4px;
}

.api-empty {
  padding: 20px;
  text-align: center;
}

/* API选择对话框样式 */
.api-selection {
  padding: 0;
}

.search-section {
  margin-bottom: 16px;
}

.api-table-container {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
}
</style>