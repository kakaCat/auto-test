<template>
  <div class="integration-table">
    <el-table
      :data="data"
      :loading="loading"
      v-bind="config"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="config.selection"
        type="selection"
        width="55"
        align="center"
      />
      
      <!-- 数据列 -->
      <el-table-column
        v-for="column in config.columns.filter(col => col.prop !== 'actions')"
        :key="column.prop"
        v-bind="column"
      >
        <template #default="{ row }">
          <!-- 类型标签 -->
          <el-tag
            v-if="column.prop === 'type'"
            :type="getTypeColor(row.type)"
            size="small"
          >
            {{ getTypeLabel(row.type) }}
          </el-tag>
          
          <!-- 状态标签 -->
          <el-tag
            v-else-if="column.prop === 'status'"
            :type="getStatusColor(row.status)"
            size="small"
          >
            {{ getStatusLabel(row.status) }}
          </el-tag>
          
          <!-- 环境标签 -->
          <el-tag
            v-else-if="column.prop === 'environment'"
            :type="getEnvironmentColor(row.environment)"
            size="small"
          >
            {{ getEnvironmentLabel(row.environment) }}
          </el-tag>
          
          <!-- 时间格式化 -->
          <span v-else-if="column.prop === 'lastRunTime'">
            {{ formatTime(row.lastRunTime) }}
          </span>
          
          <!-- 默认显示 -->
          <span v-else>{{ row[column.prop] }}</span>
        </template>
      </el-table-column>
      
      <!-- 操作列 -->
      <el-table-column
        prop="actions"
        label="操作"
        width="200"
        align="center"
        fixed="right"
      >
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              v-for="action in getRowActions(row)"
              :key="action.action"
              :type="action.type"
              :icon="action.icon"
              size="small"
              @click="handleAction(action.action, row)"
            >
              {{ action.label }}
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div
      v-if="pagination"
      class="pagination-wrapper"
    >
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="pagination.pageSizes"
        :layout="pagination.layout"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  View,
  Edit,
  VideoPlay,
  VideoPause,
  Refresh,
  Delete
} from '@element-plus/icons-vue'
import type { Integration } from '../data/table-config'

interface TableConfig {
  columns: any[]
  selection?: boolean
  stripe?: boolean
  border?: boolean
  size?: 'large' | 'default' | 'small'
}

interface Pagination {
  currentPage: number
  pageSize: number
  total: number
  pageSizes: number[]
  layout: string
}

interface Props {
  data: Integration[]
  config: TableConfig
  loading?: boolean
  pagination?: Pagination
}

interface Emits {
  (e: 'selection-change', selection: Integration[]): void
  (e: 'action', action: string, row: Integration): void
  (e: 'size-change', size: number): void
  (e: 'current-change', page: number): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// 类型标签映射
const typeLabels: Record<Integration['type'], string> = {
  api: 'API接口',
  workflow: '工作流',
  sync: '数据同步',
  queue: '消息队列'
}

const typeColors: Record<Integration['type'], string> = {
  api: 'primary',
  workflow: 'success',
  sync: 'warning',
  queue: 'info'
}

// 状态标签映射
const statusLabels: Record<Integration['status'], string> = {
  running: '运行中',
  stopped: '已停止',
  error: '错误',
  pending: '待配置'
}

const statusColors: Record<Integration['status'], string> = {
  running: 'success',
  stopped: 'info',
  error: 'danger',
  pending: 'warning'
}

// 环境标签映射
const environmentLabels: Record<Integration['environment'], string> = {
  development: '开发环境',
  testing: '测试环境',
  production: '生产环境'
}

const environmentColors: Record<Integration['environment'], string> = {
  development: 'info',
  testing: 'warning',
  production: 'success'
}

const getTypeLabel = (type: Integration['type']): string => typeLabels[type]
const getTypeColor = (type: Integration['type']): string => typeColors[type]
const getStatusLabel = (status: Integration['status']): string => statusLabels[status]
const getStatusColor = (status: Integration['status']): string => statusColors[status]
const getEnvironmentLabel = (environment: Integration['environment']): string => environmentLabels[environment]
const getEnvironmentColor = (environment: Integration['environment']): string => environmentColors[environment]

const formatTime = (time: string | null | undefined): string => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

// 根据行状态获取可用操作
const getRowActions = (row: Integration) => {
  const baseActions = [
    { label: '查看', action: 'view', type: 'primary', icon: View },
    { label: '编辑', action: 'edit', type: 'primary', icon: Edit }
  ]
  
  if (row.status === 'running') {
    baseActions.push({ label: '停止', action: 'stop', type: 'warning', icon: VideoPause })
  } else if (row.status === 'stopped' || row.status === 'error') {
    baseActions.push({ label: '启动', action: 'start', type: 'success', icon: VideoPlay })
  }
  
  baseActions.push(
    { label: '同步', action: 'sync', type: 'info', icon: Refresh },
    { label: '删除', action: 'delete', type: 'danger', icon: Delete }
  )
  
  return baseActions
}

const handleSelectionChange = (selection: Integration[]): void => {
  emit('selection-change', selection)
}

const handleAction = (action: string, row: Integration): void => {
  emit('action', action, row)
}

const handleSizeChange = (size: number): void => {
  emit('size-change', size)
}

const handleCurrentChange = (page: number): void => {
  emit('current-change', page)
}
</script>

<style scoped>
.integration-table {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-table) {
  border-radius: 4px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background-color: #f5f7fa;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

@media (max-width: 768px) {
  .integration-table {
    padding: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  :deep(.el-button--small) {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>