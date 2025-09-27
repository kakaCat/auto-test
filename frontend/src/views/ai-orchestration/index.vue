<template>
  <div class="orchestration-page">
    <div class="page-header">
      <h1>AI API编排</h1>
      <p>通过自然语言描述，让AI自动编排和执行API测试</p>
    </div>
    
    <div class="main-content">
      <!-- 输入区域 -->
      <div class="input-section">
        <el-card>
          <template #header>
            <span>描述您的测试需求</span>
          </template>
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="4"
            placeholder="例如：创建一个新用户，然后给他发送欢迎邮件，最后验证邮件是否发送成功"
          />
          <div class="input-actions">
            <el-button type="primary" @click="executeOrchestration" :loading="executing">
<el-icon><VideoPlay /></el-icon>
              执行编排
            </el-button>
            <el-button @click="generatePlan" :loading="generating">
              <el-icon><Document /></el-icon>
              生成计划
            </el-button>
            <el-button @click="clearInput">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 计划预览（Step3） -->
      <div class="plan-preview" v-if="executionPlan">
        <el-card>
          <template #header>
            <span>计划预览（Step3）</span>
            <el-tag :type="planValidation?.ok ? 'success' : 'danger'" style="margin-left: 10px">
              {{ planValidation?.ok ? '校验通过' : '校验失败' }}
            </el-tag>
          </template>
          
          <!-- 计划摘要 -->
          <div class="plan-summary" v-if="planSummary">
            <el-descriptions :column="3" border size="small">
              <el-descriptions-item label="总步骤数">{{ planSummary.total_steps }}</el-descriptions-item>
              <el-descriptions-item label="预估时长">{{ planSummary.estimated_duration }}秒</el-descriptions-item>
              <el-descriptions-item label="涉及系统">{{ planSummary.involved_systems }}</el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- 步骤列表 -->
          <el-table :data="executionPlan.steps" style="margin-top: 15px;">
            <el-table-column prop="step_id" label="步骤ID" width="100" />
            <el-table-column prop="step_name" label="步骤名称" />
            <el-table-column prop="step_type" label="类型" width="120" />
            <el-table-column prop="tool_name" label="工具" width="120" />
            <el-table-column label="参数" width="200">
              <template #default="{ row }">
                <el-popover placement="top" :width="400" trigger="hover">
                  <template #reference>
                    <el-button size="small" type="text">查看参数</el-button>
                  </template>
                  <pre>{{ JSON.stringify(row.parameters, null, 2) }}</pre>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column prop="timeout" label="超时(秒)" width="100" />
          </el-table>
          
          <!-- 校验结果 -->
          <div class="validation-result" v-if="planValidation && !planValidation.ok">
            <el-alert
              title="计划校验问题"
              type="warning"
              :closable="false"
              style="margin-top: 15px;"
            >
              <div v-if="planValidation.issues?.length">
                <p><strong>错误：</strong></p>
                <ul>
                  <li v-for="issue in planValidation.issues" :key="issue">{{ issue }}</li>
                </ul>
              </div>
              <div v-if="planValidation.warnings?.length">
                <p><strong>警告：</strong></p>
                <ul>
                  <li v-for="warning in planValidation.warnings" :key="warning">{{ warning }}</li>
                </ul>
              </div>
            </el-alert>
          </div>
          
          <div class="plan-actions" style="margin-top: 15px;">
            <el-button @click="validatePlan" type="primary" :loading="validating">校验计划</el-button>
            <el-button @click="executePlan" type="success" :loading="executing" :disabled="!planValidation?.ok">执行计划</el-button>
          </div>
        </el-card>
      </div>

      <!-- 执行结果区域（Run 视图） -->
      <div class="result-section" v-if="executionResult">
        <el-card>
          <template #header>
            <span>执行结果</span>
            <el-tag :type="getStatusType(executionResult.status)" style="margin-left: 10px;">
              {{ executionResult.status }}
            </el-tag>
          </template>
          
          <!-- 执行统计 -->
          <div class="execution-stats" v-if="executionStatus">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="总步骤" :value="executionStatus.steps?.total || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="已完成" :value="executionStatus.steps?.completed || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="失败" :value="executionStatus.steps?.failed || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="进度" :value="Math.round((executionStatus.progress || 0) * 100)" suffix="%" />
              </el-col>
            </el-row>
          </div>
          
          <!-- 执行步骤（DAG简化渲染） -->
          <div class="execution-steps" style="margin-top: 20px;">
            <h4>执行步骤</h4>
            <el-timeline>
              <el-timeline-item
                v-for="step in executionStatus?.step_details || []"
                :key="step.step_id"
                :type="getStepStatusType(step.status)"
                :icon="getStepIcon(step.status)"
              >
                <div class="step-content">
                  <div class="step-header">
                    <strong>{{ step.step_name }}</strong>
                    <el-tag :type="getStepStatusType(step.status)" size="small">{{ step.status }}</el-tag>
                  </div>
                  <p>类型: {{ step.step_type }} | 工具: {{ step.tool_name || 'N/A' }}</p>
                  <div v-if="step.error_message" class="step-error">
                    <el-alert :title="step.error_message" type="error" :closable="false" />
                  </div>
                  <div v-if="step.output_data" class="step-output">
                    <el-button size="small" type="text" @click="showStepOutput(step)">查看输出</el-button>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </div>
      
      <!-- 实时日志 -->
      <div class="logs-section" v-if="executionLogs.length > 0">
        <el-card>
          <template #header>
            <span>实时日志</span>
            <el-button size="small" @click="clearLogs" style="float: right;">清空日志</el-button>
          </template>
          <div class="logs-container">
            <div 
              v-for="(log, index) in executionLogs" 
              :key="index" 
              class="log-entry"
              :class="log.event_type"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-type">{{ log.event_type }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 步骤输出对话框 -->
    <el-dialog v-model="outputDialogVisible" title="步骤输出" width="60%">
      <pre>{{ selectedStepOutput }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Delete, Document } from '@element-plus/icons-vue'

// 响应式数据
const userInput = ref('')
const executing = ref(false)
const generating = ref(false)
const validating = ref(false)
const executionResult = ref(null)
const executionPlan = ref(null)
const planSummary = ref(null)
const planValidation = ref(null)
const executionStatus = ref(null)
const executionLogs = ref([])
const outputDialogVisible = ref(false)
const selectedStepOutput = ref('')

// WebSocket连接
let websocket = null

// 方法定义
const executeOrchestration = async () => {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入测试需求描述')
    return
  }
  
  executing.value = true
  
  try {
    const response = await fetch('/api/orchestration/v1/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_input: userInput.value,
        context: {}
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      executionResult.value = result.data
      executionPlan.value = result.data.execution_plan
      planSummary.value = result.data.plan_summary
      planValidation.value = result.data.validation_result
      
      ElMessage.success('编排执行成功')
      
      // 开始监控执行状态
      if (result.data.execution_id) {
        startMonitoring(result.data.execution_id)
      }
    } else {
      ElMessage.error(result.message || '编排执行失败')
    }
  } catch (error) {
    ElMessage.error('编排执行失败: ' + error.message)
  } finally {
    executing.value = false
  }
}

const generatePlan = async () => {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入测试需求描述')
    return
  }
  
  generating.value = true
  
  try {
    const response = await fetch('/api/orchestration/plan/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        intent_text: userInput.value,
        context: {}
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      executionPlan.value = result.data.plan
      planSummary.value = result.data.plan_summary
      ElMessage.success('计划生成成功')
    } else {
      ElMessage.error(result.message || '计划生成失败')
    }
  } catch (error) {
    ElMessage.error('计划生成失败: ' + error.message)
  } finally {
    generating.value = false
  }
}

const validatePlan = async () => {
  if (!executionPlan.value) {
    ElMessage.warning('请先生成执行计划')
    return
  }
  
  validating.value = true
  
  try {
    const response = await fetch('/api/orchestration/plan/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        plan: executionPlan.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      planValidation.value = result.data
      if (result.data.ok) {
        ElMessage.success('计划校验通过')
      } else {
        ElMessage.warning('计划校验发现问题')
      }
    } else {
      ElMessage.error(result.message || '计划校验失败')
    }
  } catch (error) {
    ElMessage.error('计划校验失败: ' + error.message)
  } finally {
    validating.value = false
  }
}

const executePlan = async () => {
  if (!executionPlan.value) {
    ElMessage.warning('请先生成执行计划')
    return
  }
  
  executing.value = true
  
  try {
    // 这里应该调用执行计划的API
    ElMessage.info('计划执行功能开发中...')
  } catch (error) {
    ElMessage.error('计划执行失败: ' + error.message)
  } finally {
    executing.value = false
  }
}

const startMonitoring = (executionId) => {
  // 建立WebSocket连接监控执行过程
  const wsUrl = `ws://localhost:8002/api/orchestration/v1/monitor/${executionId}`
  websocket = new WebSocket(wsUrl)
  
  websocket.onopen = () => {
    console.log('WebSocket连接已建立')
  }
  
  websocket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    // 添加到日志
    executionLogs.value.push(data)
    
    // 更新执行状态
    if (data.event_type === 'execution_completed' || data.event_type === 'execution_failed') {
      refreshExecutionStatus(executionId)
    }
  }
  
  websocket.onerror = (error) => {
    console.error('WebSocket错误:', error)
  }
  
  websocket.onclose = () => {
    console.log('WebSocket连接已关闭')
  }
  
  // 定期刷新执行状态
  const statusInterval = setInterval(async () => {
    await refreshExecutionStatus(executionId)
    
    // 如果执行完成，停止刷新
    if (executionStatus.value?.status === 'completed' || executionStatus.value?.status === 'failed') {
      clearInterval(statusInterval)
    }
  }, 2000)
}

const refreshExecutionStatus = async (executionId) => {
  try {
    const response = await fetch(`/api/orchestration/v1/executions/${executionId}`)
    const result = await response.json()
    
    if (result.success) {
      executionStatus.value = result.data
    }
  } catch (error) {
    console.error('刷新执行状态失败:', error)
  }
}

const clearInput = () => {
  userInput.value = ''
  executionResult.value = null
  executionPlan.value = null
  planSummary.value = null
  planValidation.value = null
  executionStatus.value = null
  executionLogs.value = []
}

const clearLogs = () => {
  executionLogs.value = []
}

const showStepOutput = (step) => {
  selectedStepOutput.value = JSON.stringify(step.output_data, null, 2)
  outputDialogVisible.value = true
}

const getStatusType = (status) => {
  const typeMap = {
    'running': 'warning',
    'completed': 'success', 
    'failed': 'danger',
    'pending': 'info'
  }
  return typeMap[status] || 'info'
}

const getStepStatusType = (status) => {
  const typeMap = {
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info',
    'skipped': 'info'
  }
  return typeMap[status] || 'info'
}

const getStepIcon = (status) => {
  const iconMap = {
    'running': 'Loading',
    'completed': 'Check',
    'failed': 'Close',
    'pending': 'Clock',
    'skipped': 'Minus'
  }
  return iconMap[status] || 'Clock'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

// 生命周期
onMounted(() => {
  // 组件挂载时的初始化
})

onUnmounted(() => {
  // 清理WebSocket连接
  if (websocket) {
    websocket.close()
  }
})
</script>

<style scoped>
.orchestration-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.plan-summary {
  margin-bottom: 15px;
}

.execution-stats {
  margin-bottom: 20px;
}

.step-content {
  padding: 10px 0;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.step-error {
  margin-top: 10px;
}

.step-output {
  margin-top: 10px;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.log-entry {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
  font-family: monospace;
  font-size: 12px;
}

.log-time {
  color: #909399;
  min-width: 80px;
}

.log-type {
  color: #409eff;
  min-width: 120px;
}

.log-message {
  color: #303133;
}

.log-entry.step_failed .log-type {
  color: #f56c6c;
}

.log-entry.step_succeeded .log-type {
  color: #67c23a;
}

.log-entry.execution_completed .log-type {
  color: #67c23a;
  font-weight: bold;
}

.log-entry.execution_failed .log-type {
  color: #f56c6c;
  font-weight: bold;
}
</style>