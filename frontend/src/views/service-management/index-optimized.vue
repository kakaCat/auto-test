<template>
  <div class="service-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">服务管理</h1>
        <p class="page-description">管理系统和模块的配置信息</p>
      </div>
      <div class="header-right">
        <el-button-group>
          <el-button 
            :type="currentEntityType === 'system' ? 'primary' : 'default'"
            @click="switchEntityType('system')"
          >
            系统管理
          </el-button>
          <el-button 
            :type="currentEntityType === 'module' ? 'primary' : 'default'"
            @click="switchEntityType('module')"
          >
            模块管理
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon system">
                <el-icon><Setting /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ (store.statistics as any).overview?.total_systems || 0 }}</div>
                <div class="stats-label">总系统数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon module">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ (store.statistics as any).overview?.total_modules || 0 }}</div>
                <div class="stats-label">总模块数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon enabled">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ (store.statistics as any).overview?.enabled_systems || 0 }}</div>
                <div class="stats-label">已启用系统</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon disabled">
                <el-icon><Close /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ (store.statistics as any).overview?.enabled_modules || 0 }}</div>
                <div class="stats-label">已启用模块</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <div class="search-form">
        <el-form :model="searchForm" inline>
          <el-form-item label="关键词">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索名称、描述或UUID"
              clearable
              style="width: 200px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          
          <el-form-item v-if="currentEntityType === 'system'" label="分类">
            <el-select v-model="searchForm.category" placeholder="选择分类" clearable style="width: 150px">
              <el-option label="自定义" value="custom" />
              <el-option label="内置" value="builtin" />
              <el-option label="第三方" value="third_party" />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="currentEntityType === 'module'" label="所属系统">
            <el-select v-model="searchForm.system_id" placeholder="选择系统" clearable style="width: 150px">
              <el-option
                v-for="option in systemOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="currentEntityType === 'module'" label="模块类型">
            <el-select v-model="searchForm.module_type" placeholder="选择类型" clearable style="width: 150px">
              <el-option label="通用" value="GENERAL" />
              <el-option label="API" value="API" />
              <el-option label="数据库" value="DATABASE" />
              <el-option label="文件" value="FILE" />
              <el-option label="消息" value="MESSAGE" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="状态">
            <el-select v-model="searchForm.enabled" placeholder="选择状态" clearable style="width: 120px">
              <el-option label="已启用" :value="true" />
              <el-option label="已禁用" :value="false" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleResetSearch">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="action-bar">
        <div class="action-left">
          <el-button type="primary" @click="openCreateDialog(currentEntityType)">
            <el-icon><Plus /></el-icon>
            新建{{ currentEntityType === 'system' ? '系统' : '模块' }}
          </el-button>
          <el-button 
            type="success" 
            :disabled="selectedRows.length === 0"
            @click="handleBatchToggleStatus(true)"
          >
            <el-icon><Check /></el-icon>
            批量启用
          </el-button>
          <el-button 
            type="warning" 
            :disabled="selectedRows.length === 0"
            @click="handleBatchToggleStatus(false)"
          >
            <el-icon><Close /></el-icon>
            批量禁用
          </el-button>
          <el-button 
            type="danger" 
            :disabled="selectedRows.length === 0"
            @click="handleBatchDelete"
          >
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </div>
        <div class="action-right">
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        :data="paginatedData"
        row-key="id"
        :loading="store.loading"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="uuid" label="UUID" width="280">
          <template #default="{ row }">
            <el-text class="uuid-text" size="small">{{ row.uuid }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="名称" min-width="150">
          <template #default="{ row }">
            <div class="name-cell">
              <el-icon class="name-icon">
                <component :is="row.icon || (currentEntityType === 'system' ? 'Setting' : 'Grid')" />
              </el-icon>
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column v-if="currentEntityType === 'system'" prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column v-if="currentEntityType === 'module'" prop="system_name" label="所属系统" width="150" />
        
        <el-table-column v-if="currentEntityType === 'module'" prop="module_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getModuleTypeColor(row.module_type)" size="small">
              {{ getModuleTypeLabel(row.module_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column v-if="currentEntityType === 'module'" prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodColor(row.method)" size="small">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="handleToggleStatus(row)"
              active-text="启用"
              inactive-text="禁用"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openViewDialog(row)">
              查看
            </el-button>
            <el-button type="success" size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :width="dialogMode === 'view' ? '800px' : '600px'"
      :close-on-click-modal="false"
    >
      <!-- 系统表单 -->
      <el-form
        v-if="currentEntityType === 'system'"
        :model="systemFormData"
        label-width="100px"
        :disabled="dialogMode === 'view'"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="系统名称" required>
              <el-input v-model="systemFormData.name" placeholder="请输入系统名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="systemFormData.category" placeholder="选择分类">
                <el-option label="自定义" value="custom" />
                <el-option label="内置" value="builtin" />
                <el-option label="第三方" value="third_party" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input
            v-model="systemFormData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入系统描述"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="图标">
              <el-input v-model="systemFormData.icon" placeholder="图标类名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="systemFormData.order_index" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="URL">
          <el-input v-model="systemFormData.url" placeholder="系统访问URL" />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="systemFormData.enabled" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>

      <!-- 模块表单 -->
      <el-form
        v-if="currentEntityType === 'module'"
        :model="moduleFormData"
        label-width="100px"
        :disabled="dialogMode === 'view'"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模块名称" required>
              <el-input v-model="moduleFormData.name" placeholder="请输入模块名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属系统" required>
              <el-select v-model="moduleFormData.system_id" placeholder="选择系统">
                <el-option
                  v-for="option in systemOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.uuid"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input
            v-model="moduleFormData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模块描述"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="模块类型">
              <el-select v-model="moduleFormData.module_type" placeholder="选择类型">
                <el-option label="通用" value="GENERAL" />
                <el-option label="API" value="API" />
                <el-option label="数据库" value="DATABASE" />
                <el-option label="文件" value="FILE" />
                <el-option label="消息" value="MESSAGE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="请求方法">
              <el-select v-model="moduleFormData.method" placeholder="选择方法">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="版本">
              <el-input v-model="moduleFormData.version" placeholder="版本号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="路径">
              <el-input v-model="moduleFormData.path" placeholder="模块路径" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="moduleFormData.order_index" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="标签">
          <el-select
            v-model="moduleFormData.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签"
          >
            <el-option
              v-for="tag in ['API', '数据库', '文件', '消息', '缓存', '日志']"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="moduleFormData.enabled" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDialog">取消</el-button>
          <el-button v-if="dialogMode !== 'view'" type="primary" @click="handleSubmit">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { 
  Setting, Grid, Check, Close, Search, Refresh, Plus, Delete 
} from '@element-plus/icons-vue'
import { useServiceManagementOptimized } from './composables/useServiceManagement-optimized'

// 使用组合式函数
const {
  // Store
  store,
  
  // 响应式状态
  searchForm,
  pagination,
  selectedRows,
  dialogVisible,
  dialogMode,
  dialogTitle,
  currentEntityType,
  systemFormData,
  moduleFormData,
  
  // 计算属性
  paginatedData,
  systemOptions,
  
  // 方法
  handleSearch,
  handleResetSearch,
  handlePageChange,
  handleSelectionChange,
  switchEntityType,
  refreshData,
  openCreateDialog,
  openEditDialog,
  openViewDialog,
  closeDialog,
  handleSubmit,
  handleDelete,
  handleBatchDelete,
  handleToggleStatus,
  handleBatchToggleStatus
} = useServiceManagementOptimized()

// 工具函数
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

const getCategoryType = (category: string) => {
  const typeMap: Record<string, string> = {
    custom: 'primary',
    builtin: 'success',
    third_party: 'warning'
  }
  return typeMap[category] || 'info'
}

const getCategoryLabel = (category: string) => {
  const labelMap: Record<string, string> = {
    custom: '自定义',
    builtin: '内置',
    third_party: '第三方'
  }
  return labelMap[category] || category
}

const getModuleTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    GENERAL: 'info',
    API: 'primary',
    DATABASE: 'success',
    FILE: 'warning',
    MESSAGE: 'danger'
  }
  return colorMap[type] || 'info'
}

const getModuleTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    GENERAL: '通用',
    API: 'API',
    DATABASE: '数据库',
    FILE: '文件',
    MESSAGE: '消息'
  }
  return labelMap[type] || type
}

const getMethodColor = (method: string) => {
  const colorMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return colorMap[method] || 'info'
}
</script>

<style scoped>
.service-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stats-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-content {
  display: flex;
  align-items: center;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stats-icon.system {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.module {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.enabled {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.disabled {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 16px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-card {
  margin-bottom: 20px;
}

.uuid-text {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #909399;
}

.name-cell {
  display: flex;
  align-items: center;
}

.name-icon {
  margin-right: 8px;
  color: #409eff;
}

.name-text {
  font-weight: 500;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  text-align: right;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-pagination) {
  justify-content: center;
}
</style>