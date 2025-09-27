<template>
  <div class="api-call-node" :class="{ selected: data.selected, running: data.status === 'running', expanded: isExpanded }">
    <div class="node-header" @click="toggleExpanded">
      <el-icon class="node-icon"><Connection /></el-icon>
      <span class="node-title">{{ data.config?.api || 'API调用' }}</span>
      <div class="node-controls">
        <el-icon class="expand-icon" :class="{ rotated: isExpanded }"><ArrowDown /></el-icon>
        <div class="node-status">
          <el-icon v-if="data.status === 'running'" class="rotating"><Loading /></el-icon>
          <el-icon v-else-if="data.status === 'success'" style="color: #67c23a"><Check /></el-icon>
          <el-icon v-else-if="data.status === 'error'" style="color: #f56c6c"><Close /></el-icon>
        </div>
      </div>
    </div>
    
    <!-- 折叠状态下的简要信息 -->
    <div v-if="!isExpanded" class="node-summary">
      <div v-if="data.config?.method" class="method-tag">
        <el-tag :type="getMethodTagType(data.config.method)" size="small">
          {{ data.config.method }}
        </el-tag>
      </div>
      <div v-if="data.config?.system" class="summary-text">
        {{ data.config.system }} > {{ data.config.module }}
      </div>
    </div>

    <!-- 展开状态下的完整配置界面 -->
    <div v-if="isExpanded" class="node-config">
      <!-- 系统选择 -->
      <div class="config-section">
        <label class="config-label">选择系统:</label>
        <el-select 
          v-model="selectedSystem" 
          placeholder="请选择系统"
          size="small"
          @change="onSystemChange"
          class="config-select"
        >
          <el-option
            v-for="system in systemOptions"
            :key="system.id"
            :label="system.name"
            :value="system.id"
          />
        </el-select>
      </div>

      <!-- 模块选择 -->
      <div class="config-section" v-if="selectedSystem">
        <label class="config-label">选择模块:</label>
        <el-select 
          v-model="selectedModule" 
          placeholder="请选择模块"
          size="small"
          @change="onModuleChange"
          class="config-select"
        >
          <el-option
            v-for="module in moduleOptions"
            :key="module.id"
            :label="module.name"
            :value="module.id"
          />
        </el-select>
      </div>

      <!-- API选择 -->
      <div class="config-section" v-if="selectedModule">
        <label class="config-label">选择API:</label>
        <el-select 
          v-model="selectedApi" 
          placeholder="请选择API"
          size="small"
          @change="onApiChange"
          class="config-select"
        >
          <el-option
            v-for="api in apiOptions"
            :key="api.id"
            :label="api.name"
            :value="api.id"
          >
            <div class="api-option">
              <span class="api-name">{{ api.name }}</span>
              <el-tag :type="getMethodTagType(api.method)" size="small">{{ api.method }}</el-tag>
            </div>
          </el-option>
        </el-select>
      </div>

      <!-- API详细信息 -->
      <div v-if="selectedApiInfo" class="api-info">
        <div class="api-basic-info">
          <div class="info-row">
            <el-tag :type="getMethodTagType(selectedApiInfo.method)" size="small">
              {{ selectedApiInfo.method }}
            </el-tag>
            <code class="api-path">{{ selectedApiInfo.path }}</code>
          </div>
          <div v-if="selectedApiInfo.description" class="api-description">
            {{ selectedApiInfo.description }}
          </div>
        </div>

        <!-- 请求参数配置 -->
        <div class="params-config">
          <label class="config-label">请求参数:</label>
          <el-input
            v-model="requestParams"
            type="textarea"
            :rows="3"
            placeholder='{"key": "value"}'
            size="small"
            class="params-input"
          />
        </div>

        <!-- 请求头配置 -->
        <div class="params-config">
          <label class="config-label">请求头:</label>
          <el-input
            v-model="requestHeaders"
            type="textarea"
            :rows="2"
            placeholder='{"Content-Type": "application/json"}'
            size="small"
            class="params-input"
          />
        </div>

        <!-- 高级配置 -->
        <div class="advanced-config">
          <el-collapse v-model="activeAdvanced" size="small">
            <el-collapse-item title="高级配置" name="advanced">
              <!-- 超时设置 -->
              <div class="config-section">
                <label class="config-label">超时时间 (秒):</label>
                <el-input-number
                  v-model="timeout"
                  :min="1"
                  :max="300"
                  size="small"
                  style="width: 100%"
                />
              </div>

              <!-- 重试配置 -->
              <div class="config-section">
                <label class="config-label">重试次数:</label>
                <el-input-number
                  v-model="retryCount"
                  :min="0"
                  :max="5"
                  size="small"
                  style="width: 100%"
                />
              </div>

              <!-- 错误处理 -->
              <div class="config-section">
                <label class="config-label">错误处理:</label>
                <el-select v-model="errorHandling" size="small" style="width: 100%">
                  <el-option label="停止执行" value="stop" />
                  <el-option label="继续执行" value="continue" />
                  <el-option label="重试后停止" value="retry_stop" />
                </el-select>
              </div>

              <!-- 缓存配置 -->
              <div class="config-section">
                <el-checkbox v-model="enableCache" size="small">
                  启用响应缓存
                </el-checkbox>
                <div v-if="enableCache" style="margin-top: 8px;">
                  <label class="config-label">缓存时间 (分钟):</label>
                  <el-input-number
                    v-model="cacheTime"
                    :min="1"
                    :max="1440"
                    size="small"
                    style="width: 100%"
                  />
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>

    <!-- 输入端口 -->
    <Handle
      id="input"
      type="target"
      :position="Position.Left"
      :style="{ top: isExpanded ? '30px' : '50%' }"
      class="node-handle input-handle"
    />

    <!-- 输出端口 -->
    <Handle
      id="output"
      type="source"
      :position="Position.Right"
      :style="{ top: isExpanded ? '30px' : '50%' }"
      class="node-handle output-handle"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { Connection, Loading, Check, Close, ArrowDown } from '@element-plus/icons-vue'
import { apiManagementApi } from '@/api/api-management'

const props = defineProps<{
  data: {
    id: string
    label?: string
    selected?: boolean
    status?: 'idle' | 'running' | 'success' | 'error'
    config?: {
      system?: string
      module?: string
      api?: string
      method?: string
      path?: string
      systemId?: number
      moduleId?: number
      apiId?: number
      requestParams?: string
      requestHeaders?: string
      timeout?: number
      retryCount?: number
      errorHandling?: string
      enableCache?: boolean
      cacheTime?: number
    }
  }
}>()

const emit = defineEmits<{
  updateNode: [nodeId: string, updates: any]
}>()

// 响应式数据
const isExpanded = ref(false)
const selectedSystem = ref(props.data.config?.systemId || null)
const selectedModule = ref(props.data.config?.moduleId || null)
const selectedApi = ref(props.data.config?.apiId || null)
const requestParams = ref('{}')
const requestHeaders = ref('{"Content-Type": "application/json"}')

// 高级配置
const activeAdvanced = ref<string[]>([])
const timeout = ref(30)
const retryCount = ref(0)
const errorHandling = ref('stop')
const enableCache = ref(false)
const cacheTime = ref(5)

// 数据选项
const systemOptions = ref<any[]>([])
const moduleOptions = ref<any[]>([])
const apiOptions = ref<any[]>([])
const selectedApiInfo = ref<any>(null)

// 方法
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const getMethodTagType = (method: string) => {
  const types: Record<string, string> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'info'
}

const onSystemChange = async (systemId: number) => {
  selectedModule.value = null
  selectedApi.value = null
  selectedApiInfo.value = null
  
  try {
    const response = await apiManagementApi.getModuleList({ system_id: systemId.toString() })
    moduleOptions.value = response.data
  } catch (error) {
    console.error('加载模块失败:', error)
    moduleOptions.value = []
  }
  
  updateNodeConfig()
}

const onModuleChange = async (moduleId: number) => {
  selectedApi.value = null
  selectedApiInfo.value = null
  
  try {
    const response = await apiManagementApi.getApis({ module_id: moduleId.toString() })
    apiOptions.value = response.data
  } catch (error) {
    console.error('加载API失败:', error)
    apiOptions.value = []
  }
  
  updateNodeConfig()
}

const onApiChange = async (apiId: number) => {
  try {
    const response = await apiManagementApi.getApiDetail(apiId.toString())
    selectedApiInfo.value = response.data
  } catch (error) {
    console.error('加载API详情失败:', error)
    selectedApiInfo.value = null
  }
  
  updateNodeConfig()
}

const updateNodeConfig = () => {
  const systemName = systemOptions.value.find(s => s.id === selectedSystem.value)?.name
  const moduleName = moduleOptions.value.find(m => m.id === selectedModule.value)?.name
  const apiInfo = apiOptions.value.find(a => a.id === selectedApi.value)
  
  emit('updateNode', props.data.id, {
    config: {
      systemId: selectedSystem.value,
      moduleId: selectedModule.value,
      apiId: selectedApi.value,
      system: systemName,
      module: moduleName,
      api: apiInfo?.name,
      method: apiInfo?.method,
      path: apiInfo?.path,
      requestParams: requestParams.value,
      requestHeaders: requestHeaders.value,
      timeout: timeout.value,
      retryCount: retryCount.value,
      errorHandling: errorHandling.value,
      enableCache: enableCache.value,
      cacheTime: cacheTime.value
    }
  })
}

// 加载系统列表
const loadSystems = async () => {
  try {
    const response = await apiManagementApi.getServiceList()
    systemOptions.value = response.data
  } catch (error) {
    console.error('加载系统列表失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadSystems()
})

// 监听props变化
watch(() => props.data.config, async (newConfig) => {
  if (newConfig) {
    selectedSystem.value = newConfig.systemId || null
    selectedModule.value = newConfig.moduleId || null
    selectedApi.value = newConfig.apiId || null
    requestParams.value = newConfig.requestParams || '{}'
    requestHeaders.value = newConfig.requestHeaders || '{"Content-Type": "application/json"}'
    timeout.value = newConfig.timeout || 30
    retryCount.value = newConfig.retryCount || 0
    errorHandling.value = newConfig.errorHandling || 'stop'
    enableCache.value = newConfig.enableCache || false
    cacheTime.value = newConfig.cacheTime || 5
    
    // 如果有配置的系统ID，加载对应的模块
    if (newConfig.systemId) {
      await onSystemChange(newConfig.systemId)
      
      // 如果有配置的模块ID，加载对应的API
      if (newConfig.moduleId) {
        await onModuleChange(newConfig.moduleId)
        
        // 如果有配置的API ID，加载API详情
        if (newConfig.apiId) {
          await onApiChange(newConfig.apiId)
        }
      }
    }
  }
}, { immediate: true })
</script>

<style scoped>
.api-call-node {
  min-width: 200px;
  max-width: 350px;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.api-call-node.expanded {
  max-width: 400px;
  min-height: 300px;
}

.api-call-node:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.api-call-node.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.api-call-node.running {
  border-color: #409eff;
  animation: nodeRunning 2s ease-in-out infinite;
}

.node-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  user-select: none;
}

.node-header:hover {
  background: #f0f9ff;
}

.node-icon {
  font-size: 16px;
  margin-right: 8px;
  color: #409eff;
}

.node-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.node-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  font-size: 14px;
  color: #909399;
  transition: transform 0.3s;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.node-status {
  font-size: 16px;
}

.node-summary {
  padding: 8px 10px;
  font-size: 12px;
}

.method-tag {
  margin-bottom: 4px;
}

.summary-text {
  color: #606266;
  font-size: 11px;
}

.node-config {
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.config-section {
  margin-bottom: 12px;
}

.config-label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  font-weight: 500;
}

.config-select {
  width: 100%;
}

.api-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.api-name {
  flex: 1;
  margin-right: 8px;
}

.api-info {
  margin-top: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.api-basic-info {
  margin-bottom: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.api-path {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #409eff;
  flex: 1;
}

.api-description {
  font-size: 11px;
  color: #606266;
  line-height: 1.4;
}

.params-config {
  margin-top: 8px;
}

.params-input {
  width: 100%;
}

.advanced-config {
  margin-top: 12px;
}

.advanced-config :deep(.el-collapse-item__header) {
  font-size: 12px;
  padding: 8px 0;
  background: #f8f9fa;
  border-radius: 4px;
  padding-left: 8px;
}

.advanced-config :deep(.el-collapse-item__content) {
  padding: 8px 0;
}

.node-handle {
  width: 12px;
  height: 12px;
  background: #409eff;
  border: 2px solid white;
  border-radius: 50%;
  transition: all 0.2s;
}

.input-handle {
  background: #67c23a;
}

.output-handle {
  background: #e6a23c;
}

.node-handle:hover {
  transform: scale(1.2);
}

@keyframes nodeRunning {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 滚动条样式 */
.node-config::-webkit-scrollbar {
  width: 4px;
}

.node-config::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.node-config::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.node-config::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>