<template>
  <el-dialog
    v-model="dialogVisible"
    title="批量执行结果"
    width="80%"
    :before-close="handleClose"
  >
    <!-- 执行统计 -->
    <el-card class="stats-card">
      <template #header>
        <span>执行统计</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">
              {{ totalCount }}
            </div>
            <div class="stat-label">
              总数
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item success">
            <div class="stat-value">
              {{ successCount }}
            </div>
            <div class="stat-label">
              成功
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item failure">
            <div class="stat-value">
              {{ failureCount }}
            </div>
            <div class="stat-label">
              失败
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">
              {{ successRate }}%
            </div>
            <div class="stat-label">
              成功率
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 执行结果列表 -->
    <el-table
      :data="executionResults"
      style="width: 100%; margin-top: 20px"
      max-height="400"
    >
      <el-table-column
        prop="testCase.name"
        label="场景名称"
        min-width="150"
      />
      <el-table-column
        label="执行状态"
        width="100"
      >
        <template #default="{ row }">
          <el-tag :type="row.success ? 'success' : 'danger'">
            {{ row.success ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="statusCode"
        label="状态码"
        width="100"
      />
      <el-table-column
        label="响应时间"
        width="120"
      >
        <template #default="{ row }">
          {{ row.responseTime }}ms
        </template>
      </el-table-column>
      <el-table-column
        prop="executedAt"
        label="执行时间"
        width="180"
      >
        <template #default="{ row }">
          {{ formatTime(row.executedAt) }}
        </template>
      </el-table-column>
      <el-table-column
        label="错误信息"
        min-width="200"
      >
        <template #default="{ row }">
          <span
            v-if="row.error"
            class="error-text"
          >{{ row.error }}</span>
          <span
            v-else
            class="success-text"
          >-</span>
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        width="120"
      >
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="viewDetails(row)"
          >
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleExport">
          导出结果
        </el-button>
        <el-button
          type="primary"
          @click="handleClose"
        >
          关闭
        </el-button>
      </div>
    </template>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="执行详情"
      width="60%"
      append-to-body
    >
      <div v-if="currentDetail">
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="场景名称">
            {{ currentDetail.testCase.name }}
          </el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="currentDetail.success ? 'success' : 'danger'">
              {{ currentDetail.success ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态码">
            {{ currentDetail.statusCode }}
          </el-descriptions-item>
          <el-descriptions-item label="响应时间">
            {{ currentDetail.responseTime }}ms
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatTime(currentDetail.executedAt) }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="currentDetail.error"
            label="错误信息"
          >
            <span class="error-text">{{ currentDetail.error }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 请求信息 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>请求信息</span>
          </template>
          <pre class="code-block">{{ formatJson(currentDetail.testCase.requestConfig) }}</pre>
        </el-card>

        <!-- 响应信息 -->
        <el-card
          v-if="currentDetail.response"
          style="margin-top: 20px"
        >
          <template #header>
            <span>响应信息</span>
          </template>
          <pre class="code-block">{{ formatJson(currentDetail.response) }}</pre>
        </el-card>
      </div>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 设置组件名称并使用类型化 Props
defineOptions({ name: 'ApiScenarioExecutionResultDialog' })

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  executionResults: {
    type: Array,
    required: true,
    default: () => []
  },
  apiInfo: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['update:visible'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const detailDialogVisible = ref(false)
const currentDetail = ref<any | null>(null)

// 统计数据
const executionResultsSafe = computed(() => (Array.isArray(props.executionResults) ? props.executionResults : []) as any[])
const totalCount = computed(() => executionResultsSafe.value.length)
function isSuccess(r: any) { return !!r?.success }
function isFailure(r: any) { return !r?.success }
const successCount = computed(() => executionResultsSafe.value.filter(isSuccess).length)
const failureCount = computed(() => executionResultsSafe.value.filter(isFailure).length)
const successRate = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((successCount.value / totalCount.value) * 100)
})

// 方法
const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

const formatJson = (obj: any) => {
  return JSON.stringify(obj, null, 2)
}

const viewDetails = (result: any) => {
  currentDetail.value = result
  detailDialogVisible.value = true
}

const handleExport = () => {
  try {
    const dataStr = JSON.stringify(props.executionResults, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `execution-results-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败，请重试')
  }
}

const handleClose = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.stats-card {
  margin-bottom: 16px;
}
.stat-item {
  text-align: center;
}
.stat-item.success .stat-value {
  color: #67C23A;
}
.stat-item.failure .stat-value {
  color: #F56C6C;
}
.code-block {
  background: #f8f8f8;
  padding: 12px;
  border-radius: 6px;
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
}
.error-text {
  color: #F56C6C;
}
.success-text {
  color: #67C23A;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>