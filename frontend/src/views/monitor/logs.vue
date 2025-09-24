<template>
  <div class="monitor-logs">
    <div class="page-header">
      <div>
        <h1 class="page-title">日志管理</h1>
        <p class="page-description">系统日志收集和分析</p>
      </div>
      <div class="header-actions">
        <el-button @click="refreshLogs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="clearLogs" type="danger" plain>
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>
    </div>

    <!-- 过滤器 -->
    <div class="filter-section">
      <el-form :model="filterForm" inline>
        <el-form-item label="日志级别">
          <el-select v-model="filterForm.level" placeholder="选择日志级别" clearable>
            <el-option label="全部" value="" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
            <el-option label="DEBUG" value="DEBUG" />
          </el-select>
        </el-form-item>
        <el-form-item label="显示条数">
          <el-select v-model="filterForm.limit" placeholder="选择显示条数">
            <el-option label="5条" :value="5" />
            <el-option label="10条" :value="10" />
            <el-option label="20条" :value="20" />
            <el-option label="50条" :value="50" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLogs">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-value">{{ logStats.total }}</div>
        <div class="stat-label">总日志数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ logStats.info }}</div>
        <div class="stat-label">信息日志</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ logStats.warning }}</div>
        <div class="stat-label">警告日志</div>
      </div>
      <div class="stat-card error">
        <div class="stat-value">{{ logStats.error }}</div>
        <div class="stat-label">错误日志</div>
      </div>
      <div class="stat-card debug">
        <div class="stat-value">{{ logStats.debug }}</div>
        <div class="stat-label">调试日志</div>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="logs-section">
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载日志中...</span>
      </div>
      
      <div v-else-if="logs.length === 0" class="empty-container">
        <el-empty description="暂无日志数据" />
      </div>
      
      <div v-else class="log-list">
        <div
          v-for="log in logs"
          :key="log.id"
          :class="['log-item', log.level.toLowerCase()]"
        >
          <div class="log-header">
            <div class="log-meta">
              <el-tag :type="getLogLevelType(log.level)" size="small">
                {{ log.level }}
              </el-tag>
              <span class="log-module">{{ log.module }}</span>
              <span class="log-time">{{ log.timestamp }}</span>
            </div>
            <div class="log-actions">
              <el-button
                size="small"
                text
                @click="toggleLogDetails(log.id)"
              >
                <el-icon><View /></el-icon>
                {{ expandedLogs.includes(log.id) ? '收起' : '详情' }}
              </el-button>
            </div>
          </div>
          
          <div class="log-message">{{ log.message }}</div>
          
          <div v-if="expandedLogs.includes(log.id)" class="log-details">
            <el-descriptions title="详细信息" :column="2" size="small" border>
              <el-descriptions-item
                v-for="(value, key) in log.details"
                :key="key"
                :label="formatDetailKey(key)"
              >
                {{ formatDetailValue(value) }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete, Search, Loading, View } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const logs = ref([])
const expandedLogs = ref([])

// 过滤表单
const filterForm = reactive({
  level: '',
  limit: 5
})

// 统计信息 - 使用后端返回的统计数据
const logStats = ref({ total: 0, info: 0, warning: 0, error: 0, debug: 0 })

// 获取日志级别对应的标签类型
const getLogLevelType = (level) => {
  const typeMap = {
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'DEBUG': 'info'
  }
  return typeMap[level] || 'info'
}

// 格式化详情键名
const formatDetailKey = (key) => {
  const keyMap = {
    'cpu_usage': 'CPU使用率',
    'memory_usage': '内存使用率',
    'disk_usage': '磁盘使用率',
    'api_path': 'API路径',
    'response_time': '响应时间',
    'status_code': '状态码',
    'pool_size': '连接池大小',
    'active_connections': '活跃连接',
    'waiting_requests': '等待请求',
    'user_id': '用户ID',
    'ip_address': 'IP地址',
    'user_agent': '用户代理',
    'port': '端口',
    'version': '版本',
    'startup_time': '启动时间'
  }
  return keyMap[key] || key
}

// 格式化详情值
const formatDetailValue = (value) => {
  if (typeof value === 'number') {
    if (value > 1000) {
      return `${(value / 1000).toFixed(1)}k`
    }
    return value.toString()
  }
  return value
}

// 切换日志详情显示
const toggleLogDetails = (logId) => {
  const index = expandedLogs.value.indexOf(logId)
  if (index > -1) {
    expandedLogs.value.splice(index, 1)
  } else {
    expandedLogs.value.push(logId)
  }
}

// 加载日志数据
const loadLogs = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('limit', filterForm.limit)
    if (filterForm.level) {
      params.append('level', filterForm.level)
    }
    
    const response = await fetch(`http://localhost:8000/api/logs/v1?${params}`)
    const result = await response.json()
    
    if (result.success) {
      logs.value = result.data.logs
      // 更新统计数据
      logStats.value = result.data.stats
      ElMessage.success(`加载成功，共${result.data.total}条日志`)
    } else {
      ElMessage.error(result.message || '加载日志失败')
    }
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 刷新日志
const refreshLogs = () => {
  loadLogs()
}

// 清空日志
const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    logs.value = []
    expandedLogs.value = []
    ElMessage.success('日志已清空')
  } catch {
    // 用户取消操作
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.monitor-logs {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 8px 0;
}

.page-description {
  color: var(--el-text-color-regular);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  background: var(--el-bg-color-page);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--el-bg-color);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid var(--el-border-color-light);
}

.stat-card.error {
  border-color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
}

.stat-card.debug {
  border-color: var(--el-color-info);
  background: var(--el-color-info-light-9);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.stat-card.error .stat-value {
  color: var(--el-color-danger);
}

.stat-card.debug .stat-value {
  color: var(--el-color-info);
}

.stat-label {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.logs-section {
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--el-text-color-regular);
}

.loading-container .el-icon {
  font-size: 24px;
  margin-bottom: 12px;
}

.log-list {
  padding: 0;
}

.log-item {
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.info {
  border-left: 4px solid var(--el-color-success);
}

.log-item.warning {
  border-left: 4px solid var(--el-color-warning);
}

.log-item.error {
  border-left: 4px solid var(--el-color-danger);
  background: var(--el-color-danger-light-9);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.log-module {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.log-time {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.log-message {
  color: var(--el-text-color-primary);
  line-height: 1.5;
  margin-bottom: 8px;
}

.log-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>