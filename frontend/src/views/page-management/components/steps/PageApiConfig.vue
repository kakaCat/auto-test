<template>
  <div class="page-api-config">
    <div class="config-container">
      <!-- 左侧API选择区域 -->
      <div class="api-selection">
        <div class="selection-header">
          <h3>API选择</h3>
          <p>配置系统关联并选择API</p>
        </div>

        <!-- 系统关联配置 -->
        <div class="system-association">
          <div class="section-title">
            <h4>系统关联配置</h4>
            <p>设置页面所属的系统和模块</p>
          </div>
          <el-form label-width="80px" size="small">
            <el-form-item label="所属系统" required>
              <el-select
                v-model="apiConfigData.systemId"
                placeholder="请选择所属系统"
                style="width: 100%"
                @change="handleSystemAssociationChange"
              >
                <el-option
                  v-for="system in systemOptions"
                  :key="system.id"
                  :label="system.name"
                  :value="system.id"
                >
                  <div class="option-item">
                    <span class="option-label">{{ system.name }}</span>
                    <span class="option-desc">{{ system.description }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="所属模块">
              <el-select
                v-model="apiConfigData.moduleId"
                placeholder="请选择所属模块"
                style="width: 100%"
                :disabled="!apiConfigData.systemId"
                @change="handleModuleAssociationChange"
              >
                <el-option
                  v-for="module in moduleOptions"
                  :key="module.id"
                  :label="module.name"
                  :value="module.id"
                >
                  <div class="option-item">
                    <span class="option-label">{{ module.name }}</span>
                    <span class="option-desc">{{ module.description }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- API选择 -->
        <div class="api-selection-form">
          <div class="section-title">
            <h4>API选择</h4>
            <p>基于系统关联选择API接口</p>
          </div>
          <el-form label-width="80px" size="small">
            <el-form-item label="选择系统">
              <el-select
                v-model="selectedSystemId"
                placeholder="请选择系统"
                style="width: 100%"
                @change="handleSystemChange"
              >
                <el-option
                  v-for="system in systemOptions"
                  :key="system.id"
                  :label="system.name"
                  :value="system.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="选择模块">
              <el-select
                v-model="selectedModuleId"
                placeholder="请选择模块"
                style="width: 100%"
                :disabled="!selectedSystemId"
                @change="handleModuleChange"
              >
                <el-option
                  v-for="module in moduleOptions"
                  :key="module.id"
                  :label="module.name"
                  :value="module.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="选择API">
              <el-select
                v-model="selectedApiId"
                placeholder="请选择API"
                style="width: 100%"
                :disabled="!selectedModuleId"
              >
                <el-option
                  v-for="api in apiOptions"
                  :key="api.id"
                  :label="`${api.name} (${api.method})`"
                  :value="api.id"
                >
                  <div class="api-option">
                    <span class="api-name">{{ api.name }}</span>
                    <el-tag :type="getMethodTagType(api.method)" size="small">
                      {{ api.method }}
                    </el-tag>
                    <span class="api-path">{{ api.path }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="addApi" :disabled="!selectedApiId">
                添加API
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右侧API配置区域 -->
      <div class="api-configuration">
        <div class="config-header">
          <h3>API配置列表</h3>
          <p>配置API调用顺序和参数</p>
        </div>

        <div class="api-list">
          <div v-if="apiConfigData.apis.length === 0" class="empty-state">
            <el-empty description="暂无API配置" />
          </div>

          <div v-else class="api-items">
            <div
              v-for="(apiItem, index) in apiConfigData.apis"
              :key="apiItem.id"
              class="api-item"
              :class="{ active: selectedApiItem?.id === apiItem.id }"
              @click="selectApiItem(apiItem)"
            >
              <div class="api-item-header">
                <div class="api-info">
                  <span class="api-name">{{ apiItem.name }}</span>
                  <el-tag :type="getMethodTagType(apiItem.method)" size="small">
                    {{ apiItem.method }}
                  </el-tag>
                  <span class="api-path">{{ apiItem.path }}</span>
                </div>
                <div class="api-actions">
                  <el-button size="small" @click.stop="editApiItem(apiItem)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click.stop="removeApiItem(index)">
                    删除
                  </el-button>
                </div>
              </div>

              <div class="api-item-config">
                <div class="config-row">
                  <span class="config-label">调用类型:</span>
                  <el-select
                    v-model="apiItem.callType"
                    size="small"
                    style="width: 120px"
                  >
                    <el-option label="串行" value="serial" />
                    <el-option label="并行" value="parallel" />
                    <el-option label="条件" value="conditional" />
                  </el-select>
                </div>
                <div class="config-row">
                  <span class="config-label">执行顺序:</span>
                  <el-input-number
                    v-model="apiItem.order"
                    :min="1"
                    :max="100"
                    size="small"
                    controls-position="right"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- API流程图 -->
        <div v-if="apiConfigData.apis.length > 0" class="flow-chart">
          <div class="chart-header">
            <h4>API调用流程图</h4>
            <el-button size="small" @click="refreshFlowChart">
              刷新流程图
            </el-button>
          </div>
          <div class="chart-container">
            <div class="flow-nodes">
              <div
                v-for="(apiItem, index) in sortedApis"
                :key="apiItem.id"
                class="flow-node"
                :class="apiItem.callType"
              >
                <div class="node-content">
                  <span class="node-order">{{ apiItem.order }}</span>
                  <span class="node-name">{{ apiItem.name }}</span>
                  <span class="node-type">{{ getCallTypeLabel(apiItem.callType) }}</span>
                </div>
                <div v-if="index < sortedApis.length - 1" class="node-connector">
                  <el-icon><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- API详细配置对话框 -->
    <el-dialog
      v-model="showApiDetailDialog"
      title="API详细配置"
      width="800px"
    >
      <div v-if="editingApiItem" class="api-detail-config">
        <el-form :model="editingApiItem" label-width="120px">
          <el-form-item label="延迟时间(ms)">
            <el-input-number
              v-model="editingApiItem.delay"
              :min="0"
              :max="10000"
              placeholder="0"
            />
          </el-form-item>

          <el-form-item label="超时时间(ms)">
            <el-input-number
              v-model="editingApiItem.timeout"
              :min="1000"
              :max="60000"
              placeholder="5000"
            />
          </el-form-item>

          <el-form-item label="重试次数">
            <el-input-number
              v-model="editingApiItem.retry"
              :min="0"
              :max="5"
              placeholder="0"
            />
          </el-form-item>

          <el-form-item label="执行条件">
            <el-input
              v-model="editingApiItem.condition"
              type="textarea"
              placeholder="如：response.code === 200"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="参数映射">
            <el-input
              v-model="editingApiItem.params.transform"
              type="textarea"
              placeholder="参数转换规则"
              :rows="3"
            />
          </el-form-item>

          <el-form-item label="响应处理">
            <el-input
              v-model="editingApiItem.response.transform"
              type="textarea"
              placeholder="响应数据转换规则"
              :rows="3"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showApiDetailDialog = false">取消</el-button>
        <el-button type="primary" @click="saveApiDetail">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import type { PageApiConfig, ApiConfigItem } from '../../types/page-config'
import { systemApi, moduleApi } from '@/api/unified-api'

const props = defineProps<{
  modelValue: PageApiConfig
  systemId?: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: PageApiConfig]
  'validate': [stepIndex: number, isValid: boolean]
}>()

// 响应式数据
const selectedSystemId = ref<number | null>(props.systemId || null)
const selectedModuleId = ref<number | null>(null)
const selectedApiId = ref<number | null>(null)
const selectedApiItem = ref<ApiConfigItem | null>(null)
const editingApiItem = ref<ApiConfigItem | null>(null)
const showApiDetailDialog = ref(false)

const systemOptions = ref<any[]>([])
const moduleOptions = ref<any[]>([])
const apiOptions = ref<any[]>([])

// API配置数据
const defaultApiConfig: PageApiConfig = {
  systemId: null,
  moduleId: null,
  apis: [],
  flowChart: { nodes: [], edges: [] }
}
const apiConfigData = reactive<PageApiConfig>({ 
  ...defaultApiConfig,
  ...props.modelValue 
})

// 计算属性
const sortedApis = computed(() => {
  return [...apiConfigData.apis].sort((a, b) => a.order - b.order)
})

// 监听数据变化
watch(apiConfigData, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

watch(() => props.modelValue, (newVal) => {
  Object.assign(apiConfigData, newVal)
}, { deep: true })

// 组件挂载时加载数据
onMounted(() => {
  loadSystemOptions()
  if (selectedSystemId.value) {
    loadModuleOptions(selectedSystemId.value)
  }
})

// 加载系统选项
const loadSystemOptions = async () => {
  try {
    const response = await systemApi.getList()
    if (response.success) {
      systemOptions.value = response.data || []
    }
  } catch (error) {
    console.error('加载系统列表失败:', error)
  }
}

// 加载模块选项
const loadModuleOptions = async (systemId: number) => {
  try {
    const response = await moduleApi.getBySystem(systemId.toString())
    if (response.success) {
      moduleOptions.value = response.data || []
    }
  } catch (error) {
    console.error('加载模块列表失败:', error)
  }
}

// 加载API选项
const loadApiOptions = async (moduleId: number) => {
  try {
    // 暂时使用模拟数据
    apiOptions.value = [
      { id: 1, name: '获取用户列表', method: 'GET', path: '/api/users' },
      { id: 2, name: '创建用户', method: 'POST', path: '/api/users' },
      { id: 3, name: '更新用户', method: 'PUT', path: '/api/users/:id' },
      { id: 4, name: '删除用户', method: 'DELETE', path: '/api/users/:id' }
    ]
  } catch (error) {
    console.error('加载API列表失败:', error)
  }
}

// 处理系统关联变化
const handleSystemAssociationChange = (systemId: number) => {
  apiConfigData.moduleId = null
  moduleOptions.value = []
  if (systemId) {
    loadModuleOptions(systemId)
  }
  // 同时更新API选择的系统
  selectedSystemId.value = systemId
  handleSystemChange(systemId)
  handleValidate()
}

// 处理模块关联变化
const handleModuleAssociationChange = (moduleId: number) => {
  // 同时更新API选择的模块
  selectedModuleId.value = moduleId
  handleModuleChange(moduleId)
  handleValidate()
}

// 验证表单
const handleValidate = () => {
  // 验证系统关联
  if (!apiConfigData.systemId) {
    ElMessage.error('请选择所属系统')
    return false
  }
  if (!apiConfigData.moduleId) {
    ElMessage.error('请选择所属模块')
    return false
  }
  return true
}

// 处理系统变化
const handleSystemChange = (systemId: number) => {
  selectedModuleId.value = null
  selectedApiId.value = null
  moduleOptions.value = []
  apiOptions.value = []
  if (systemId) {
    loadModuleOptions(systemId)
  }
}

// 处理模块变化
const handleModuleChange = (moduleId: number) => {
  selectedApiId.value = null
  apiOptions.value = []
  if (moduleId) {
    loadApiOptions(moduleId)
  }
}

// 添加API
const addApi = () => {
  if (!selectedApiId.value) return

  const selectedApi = apiOptions.value.find(api => api.id === selectedApiId.value)
  if (!selectedApi) return

  // 检查是否已存在
  const exists = apiConfigData.apis.some(item => item.apiId === selectedApi.id)
  if (exists) {
    ElMessage.warning('该API已存在')
    return
  }

  const newApiItem: ApiConfigItem = {
    id: `api_${Date.now()}`,
    apiId: selectedApi.id,
    name: selectedApi.name,
    method: selectedApi.method,
    path: selectedApi.path,
    callType: 'serial',
    order: apiConfigData.apis.length + 1,
    delay: 0,
    timeout: 5000,
    retry: 0,
    condition: '',
    params: {
      static: {},
      dynamic: {},
      transform: ''
    },
    response: {
      extract: {},
      transform: '',
      target: ''
    },
    error: {
      message: '',
      retry: false,
      fallback: ''
    }
  }

  apiConfigData.apis.push(newApiItem)
  selectedApiId.value = null
  
  ElMessage.success('API添加成功')
}

// 选择API项
const selectApiItem = (apiItem: ApiConfigItem) => {
  selectedApiItem.value = apiItem
}

// 编辑API项
const editApiItem = (apiItem: ApiConfigItem) => {
  editingApiItem.value = { ...apiItem }
  showApiDetailDialog.value = true
}

// 删除API项
const removeApiItem = (index: number) => {
  apiConfigData.apis.splice(index, 1)
  // 重新排序
  apiConfigData.apis.forEach((item, idx) => {
    item.order = idx + 1
  })
  ElMessage.success('API删除成功')
}

// 保存API详细配置
const saveApiDetail = () => {
  if (editingApiItem.value) {
    const index = apiConfigData.apis.findIndex(item => item.id === editingApiItem.value!.id)
    if (index !== -1) {
      apiConfigData.apis[index] = { ...editingApiItem.value }
    }
  }
  showApiDetailDialog.value = false
  ElMessage.success('配置保存成功')
}

// 刷新流程图
const refreshFlowChart = () => {
  // 这里可以实现流程图的刷新逻辑
  ElMessage.info('流程图已刷新')
}

// 获取HTTP方法标签类型
const getMethodTagType = (method: string) => {
  const typeMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return typeMap[method] || 'info'
}

// 获取调用类型标签
const getCallTypeLabel = (callType: string) => {
  const labelMap: Record<string, string> = {
    serial: '串行',
    parallel: '并行',
    conditional: '条件'
  }
  return labelMap[callType] || callType
}

// 验证方法
const validate = async () => {
  // 验证系统关联
  if (!handleValidate()) {
    emit('validate', 2, false)
    return false
  }
  
  // 简单验证：至少有一个API配置
  const isValid = apiConfigData.apis.length > 0
  if (!isValid) {
    ElMessage.error('请至少添加一个API配置')
  }
  
  emit('validate', 2, isValid)
  return isValid
}

defineExpose({
  validate,
  handleSystemAssociationChange,
  handleModuleAssociationChange,
  handleValidate
})
</script>

<style lang="scss" scoped>
.page-api-config {
  .config-container {
    display: flex;
    gap: 24px;
    height: 600px;
  }

  .api-selection {
    width: 300px;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 16px;

    .selection-header {
      margin-bottom: 20px;

      h3 {
        margin: 0 0 5px 0;
        font-size: 16px;
        font-weight: 600;
      }

      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }

    .api-option {
      display: flex;
      align-items: center;
      gap: 8px;

      .api-name {
        font-weight: 500;
      }

      .api-path {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .api-configuration {
    flex: 1;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 16px;
    overflow-y: auto;

    .config-header {
      margin-bottom: 20px;

      h3 {
        margin: 0 0 5px 0;
        font-size: 16px;
        font-weight: 600;
      }

      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }

    .api-items {
      .api-item {
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        margin-bottom: 12px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: #409eff;
        }

        &.active {
          border-color: #409eff;
          background-color: #f0f9ff;
        }

        .api-item-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .api-info {
            display: flex;
            align-items: center;
            gap: 8px;

            .api-name {
              font-weight: 500;
            }

            .api-path {
              font-size: 12px;
              color: #909399;
            }
          }
        }

        .api-item-config {
          display: flex;
          gap: 16px;

          .config-row {
            display: flex;
            align-items: center;
            gap: 8px;

            .config-label {
              font-size: 12px;
              color: #606266;
              white-space: nowrap;
            }
          }
        }
      }
    }

    .flow-chart {
      margin-top: 24px;
      border-top: 1px solid #e4e7ed;
      padding-top: 16px;

      .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        h4 {
          margin: 0;
          font-size: 14px;
          font-weight: 600;
        }
      }

      .flow-nodes {
        display: flex;
        align-items: center;
        gap: 16px;
        overflow-x: auto;
        padding: 16px;
        background-color: #f8f9fa;
        border-radius: 4px;

        .flow-node {
          display: flex;
          align-items: center;
          gap: 12px;

          .node-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 12px;
            background-color: #fff;
            border: 1px solid #e4e7ed;
            border-radius: 4px;
            min-width: 80px;

            &.serial {
              border-color: #67c23a;
            }

            &.parallel {
              border-color: #409eff;
            }

            &.conditional {
              border-color: #e6a23c;
            }

            .node-order {
              font-size: 12px;
              font-weight: 600;
              color: #409eff;
            }

            .node-name {
              font-size: 12px;
              font-weight: 500;
              margin: 4px 0;
            }

            .node-type {
              font-size: 10px;
              color: #909399;
            }
          }

          .node-connector {
            color: #409eff;
          }
        }
      }
    }
  }

  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
  }
}

.api-detail-config {
  max-height: 400px;
  overflow-y: auto;
}
</style>