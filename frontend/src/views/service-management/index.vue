<template>
  <div class="service-management">
    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="clearError"
      style="margin-bottom: 16px"
    />
    
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">系统列表</h1>
        <p class="page-description">管理系统和模块的配置信息</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="showAddSystemDialog">
          新增系统
        </el-button>
        <el-button :icon="Refresh" @click="refreshData">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧树形结构 -->
      <div class="left-panel">
        <SystemTree
          ref="treeRef"
          :data="treeData"
          search-placeholder="搜索系统或模块"
          :show-actions="true"
          label-key="label"
          children-key="children"
          :get-icon="getNodeIcon"
          @node-click="handleNodeClick"
          @node-contextmenu="handleNodeContextMenu"
          @tree-action="handleTreeAction"
        />
      </div>

      <!-- 右侧详情面板 -->
      <div class="right-panel">
        <div v-if="!selectedNode" class="empty-detail">
          <el-empty description="请选择左侧的系统或模块查看详情">
            <el-button type="primary" @click="showAddSystemDialog">
              <el-icon><Plus /></el-icon>
              新增系统
            </el-button>
          </el-empty>
        </div>

        <!-- 系统详情 -->
        <div v-else-if="!selectedNode.isModule" class="system-detail">
          <div class="detail-header">
            <div class="detail-title">
              <el-icon class="title-icon" :size="24">
                <component :is="getSystemIcon(selectedNode.category)" />
              </el-icon>
              <div>
                <h2>{{ selectedNode.name }}</h2>
                <p class="detail-subtitle">{{ selectedNode.description || '暂无描述' }}</p>
              </div>
            </div>
            <div class="detail-actions">
              <el-button type="primary" :icon="Edit" @click="editSystem(selectedNode)">
                编辑
              </el-button>
              <el-button :icon="Plus" @click="showAddModuleDialog(selectedNode.id)">
                添加模块
              </el-button>
            </div>
          </div>

          <div class="detail-content">
            <!-- 基本信息 -->
            <el-card class="info-card" shadow="never">
              <template #header>
                <span class="card-title">基本信息</span>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="系统名称">{{ selectedNode.name }}</el-descriptions-item>
                <el-descriptions-item label="系统分类">
                   <el-tag :type="getCategoryTagType(selectedNode.category)" size="small">
                     {{ SystemCategoryLabels[selectedNode.category as SystemCategory] }}
                   </el-tag>
                 </el-descriptions-item>
                <el-descriptions-item label="访问地址">
                  <el-link v-if="selectedNode.url" :href="selectedNode.url" target="_blank" type="primary">
                    {{ selectedNode.url }}
                  </el-link>
                  <span v-else class="text-placeholder">未设置</span>
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="selectedNode.enabled ? 'success' : 'danger'" size="small">
                    {{ selectedNode.enabled ? '启用' : '禁用' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="创建时间" :span="2">
                  {{ formatTime(selectedNode.created_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>

            <!-- 模块列表 -->
            <el-card class="modules-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span class="card-title">模块列表 ({{ selectedNode.modules?.length || 0 }})</span>
                  <el-button type="primary" size="small" :icon="Plus" @click="showAddModuleDialog(selectedNode.id)">
                    添加模块
                  </el-button>
                </div>
              </template>
              
              <div v-if="selectedNode.modules && selectedNode.modules.length > 0" class="modules-grid">
                <div
                  v-for="module in selectedNode.modules"
                  :key="module.id"
                  class="module-card"
                  @click="selectModule(module)"
                >
                  <div class="module-header">
                    <el-icon class="module-icon" :size="20">
                      <component :is="getModuleIcon(module.tags)" />
                    </el-icon>
                    <div class="module-info">
                      <h4 class="module-name">{{ module.name }}</h4>
                      <p class="module-desc">{{ module.description || '暂无描述' }}</p>
                    </div>
                    <el-dropdown @command="handleModuleAction" trigger="click" @click.stop>
                      <el-icon class="module-action" :size="16">
                        <MoreFilled />
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item :command="`edit-${module.id}`">
                            <el-icon><Edit /></el-icon>
                            编辑
                          </el-dropdown-item>
                          <el-dropdown-item :command="`toggle-${module.id}`">
                            <el-icon><Switch /></el-icon>
                            {{ module.enabled ? '禁用' : '启用' }}
                          </el-dropdown-item>
                          <el-dropdown-item :command="`delete-${module.id}`" divided>
                            <el-icon><Delete /></el-icon>
                            删除
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                  <div class="module-footer">
                    <div class="module-tags">
                      <el-tag
                        v-for="tag in (module.tags || []).slice(0, 2)"
                        :key="tag"
                        size="small"
                        type="info"
                      >
                        {{ tag }}
                      </el-tag>
                      <span v-if="(module.tags || []).length > 2" class="more-tags">
                        +{{ (module.tags || []).length - 2 }}
                      </span>
                    </div>
                    <el-tag :type="module.enabled ? 'success' : 'danger'" size="small">
                      {{ module.enabled ? '启用' : '禁用' }}
                    </el-tag>
                  </div>
                </div>
              </div>
              
              <el-empty v-else description="暂无模块" :image-size="80">
                <el-button type="primary" size="small" @click="showAddModuleDialog(selectedNode.id)">
                  添加第一个模块
                </el-button>
              </el-empty>
            </el-card>
          </div>
        </div>

        <!-- 模块详情 -->
        <div v-else class="module-detail">
          <div class="detail-header">
            <div class="detail-title">
              <el-icon class="title-icon" :size="24">
                <component :is="getModuleIcon(selectedNode.tags)" />
              </el-icon>
              <div>
                <h2>{{ selectedNode.name }}</h2>
                <p class="detail-subtitle">{{ selectedNode.description || '暂无描述' }}</p>
              </div>
            </div>
            <div class="detail-actions">
              <el-button type="primary" :icon="Edit" @click="editModule(selectedNode)">
                编辑
              </el-button>
              <el-button :icon="Switch" @click="toggleModuleStatus(selectedNode)">
                {{ selectedNode.enabled ? '禁用' : '启用' }}
              </el-button>
              <el-button type="danger" :icon="Delete" @click="deleteModule(selectedNode.id)">
                删除
              </el-button>
            </div>
          </div>

          <div class="detail-content">
            <el-card class="info-card" shadow="never">
              <template #header>
                <span class="card-title">模块信息</span>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="模块名称">{{ selectedNode.name }}</el-descriptions-item>
                <el-descriptions-item label="版本号">{{ selectedNode.version || '未设置' }}</el-descriptions-item>
                <el-descriptions-item label="路由路径">{{ selectedNode.path || '未设置' }}</el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="selectedNode.enabled ? 'success' : 'danger'" size="small">
                    {{ selectedNode.enabled ? '启用' : '禁用' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="标签" :span="2">
                  <div v-if="selectedNode.tags && selectedNode.tags.length > 0" class="tag-list">
                    <el-tag
                      v-for="tag in selectedNode.tags"
                      :key="tag"
                      size="small"
                      type="info"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                  <span v-else class="text-placeholder">暂无标签</span>
                </el-descriptions-item>
                <el-descriptions-item label="创建时间" :span="2">
                  {{ formatTime(selectedNode.created_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑系统对话框 -->
    <el-dialog
      v-model="systemDialogVisible"
      :title="systemDialogTitle"
      width="600px"
      @close="resetSystemForm"
    >
      <el-form
        ref="systemFormRef"
        :model="systemForm"
        :rules="systemRules"
        label-width="100px"
      >
        <el-form-item label="系统名称" prop="name">
          <el-input v-model="systemForm.name" placeholder="请输入系统名称" />
        </el-form-item>
        <el-form-item label="系统描述" prop="description">
          <el-input v-model="systemForm.description" type="textarea" placeholder="请输入系统描述" />
        </el-form-item>
        <el-form-item label="系统分类" prop="category">
          <el-select v-model="systemForm.category" placeholder="请选择系统分类" style="width: 100%">
            <el-option 
              v-for="option in systemCategoryOptions" 
              :key="option.value" 
              :label="option.label" 
              :value="option.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="访问地址" prop="url">
          <el-input v-model="systemForm.url" placeholder="例如：https://api.example.com 或 http://localhost:8080" />
        </el-form-item>
        <el-form-item label="启用状态" prop="enabled">
          <el-switch v-model="systemForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="systemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSystem">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑模块对话框 -->
    <el-dialog
      v-model="moduleDialogVisible"
      :title="moduleDialogTitle"
      width="600px"
      @close="resetModuleForm"
    >
      <el-form
        ref="moduleFormRef"
        :model="moduleForm"
        :rules="moduleRules"
        label-width="100px"
      >
        <el-form-item label="模块名称" prop="name">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称" />
        </el-form-item>
        <el-form-item label="模块描述" prop="description">
          <el-input v-model="moduleForm.description" type="textarea" placeholder="请输入模块描述" />
        </el-form-item>
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="moduleForm.path" placeholder="请输入路由路径，如：/user-management" />
        </el-form-item>
        <el-form-item label="版本号" prop="version">
          <el-input v-model="moduleForm.version" placeholder="请输入版本号" />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="moduleForm.tags"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in commonTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态" prop="enabled">
          <el-switch v-model="moduleForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Search,
  Edit,
  Delete,
  Setting,
  FolderOpened,
  Document,
  Switch,
  MoreFilled,
  ArrowDown,
  ArrowRight,
  Monitor
} from '@element-plus/icons-vue'

// 导入类型定义
import type { SystemCategory, System, Module } from './types'
import { SystemCategoryLabels } from './types'

// 导入API
import { systemApi, moduleApi } from '@/api/service'

// 导入数据配置
import {
  systemCategoryOptions,
  commonTags,
  getSystemIcon,
  getModuleIcon,
  getCategoryTagType
} from './data'

// 导入组合式函数
import { useServiceManagement, useFormValidation } from './composables'
import SystemTree from '@/components/SystemTree.vue'

// 使用组合式函数
const {
  // 状态
  loading,
  error,
  
  // 对话框状态
  systemDialogVisible,
  moduleDialogVisible,
  systemDialogTitle,
  moduleDialogTitle,
  
  // 表单数据
  systemForm,
  moduleForm,
  
  // 数据
  filteredSystems,
  
  // 方法
  showAddSystemDialog,
  showAddModuleDialog,
  resetSystemForm,
  resetModuleForm,
  saveSystem,
  saveModule,
  refreshData,
  clearError
} = useServiceManagement()

// 使用表单验证
const {
  systemFormRef,
  moduleFormRef,
  systemRules,
  moduleRules
} = useFormValidation()

// 树形组件相关
const treeRef = ref()
const selectedNode = ref<any>(null)

// 树形数据
const treeData = computed(() => {
  return filteredSystems.value.map((system: System) => ({
    ...system,
    label: system.name,
    type: 'system',
    children: system.modules?.map((module: Module) => ({
      ...module,
      label: module.name,
      type: 'module',
      isModule: true
    })) || []
  }))
})



// SystemTree组件事件处理
const handleSystemTreeNodeClick = (data: any) => {
  selectedNode.value = data
}

const handleSystemTreeNodeAdd = (data: any) => {
  if (data.isModule) {
    // 添加模块逻辑
    showAddModuleDialog(data.id)
  } else {
    // 添加系统逻辑
    showAddSystemDialog()
  }
}

const handleSystemTreeNodeEdit = (data: any) => {
  if (data.isModule) {
    // 编辑模块逻辑
    editModule(data)
  } else {
    // 编辑系统逻辑
    editSystem(data)
  }
}

const handleSystemTreeNodeDelete = (data: any) => {
  if (data.isModule) {
    // 删除模块逻辑
    deleteModule(data.id)
  } else {
    // 删除系统逻辑
    deleteSystem(data.id)
  }
}

// 节点点击
const handleNodeClick = (data: any) => {
  selectedNode.value = data
}

// 右键菜单
const handleNodeContextMenu = (event: MouseEvent, data: any) => {
  event.preventDefault()
  // 可以在这里实现右键菜单
}

// 获取节点图标
const getNodeIcon = (data: any) => {
  if (data.isModule || data.type === 'module') {
    return Document  // 模块使用文件图标
  } else if (data.type === 'system') {
    return Monitor   // 系统使用电脑图标
  } else {
    return getSystemIcon(data.category)
  }
}

// 树形操作
const handleTreeAction = (command: string) => {
  const firstDashIndex = command.indexOf('-')
  if (firstDashIndex === -1) return
  
  const action = command.substring(0, firstDashIndex)
  const id = command.substring(firstDashIndex + 1)
  
  switch (action) {
    case 'add':
      if (command.startsWith('add-module')) {
        showAddModuleDialog(id)
      }
      break
    case 'edit':
      const system = filteredSystems.value.find((s: System) => s.id === id)
      if (system) {
        editSystem(system)
      }
      break
    case 'delete':
      deleteSystem(id)
      break
  }
}

// 模块操作
const handleModuleAction = (command: string) => {
  const firstDashIndex = command.indexOf('-')
  if (firstDashIndex === -1) return
  
  const action = command.substring(0, firstDashIndex)
  const id = command.substring(firstDashIndex + 1)
  
  // 查找模块
  let targetModule: Module | null = null
  for (const system of filteredSystems.value) {
    const module = system.modules?.find((m: Module) => m.id === id)
    if (module) {
      targetModule = module
      break
    }
  }
  
  if (!targetModule) return
  
  switch (action) {
    case 'edit':
      editModule(targetModule)
      break
    case 'toggle':
      toggleModuleStatus(targetModule)
      break
    case 'delete':
      deleteModule(id)
      break
  }
}

// 编辑系统
const editSystem = (system: System) => {
  Object.assign(systemForm, system)
  systemDialogTitle.value = '编辑系统'
  systemDialogVisible.value = true
}

// 编辑模块
const editModule = (module: Module) => {
  Object.assign(moduleForm, module)
  moduleDialogTitle.value = '编辑模块'
  moduleDialogVisible.value = true
}

// 选择模块
const selectModule = (module: Module) => {
  selectedNode.value = { ...module, isModule: true }
}

// 切换模块状态
const toggleModuleStatus = (module: Module) => {
  module.enabled = !module.enabled
  ElMessage.success(`模块已${module.enabled ? '启用' : '禁用'}`)
}

// 删除系统
const deleteSystem = async (systemId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该系统吗？这将同时删除该系统下的所有模块。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 调用API删除系统
    await systemApi.delete(systemId)
    ElMessage.success('系统删除成功')
    refreshData()
    
    // 如果删除的是当前选中的系统，清空选择
    if (selectedNode.value && !selectedNode.value.isModule && selectedNode.value.id === systemId) {
      selectedNode.value = null
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除系统失败: ' + (error?.message || error))
    }
  }
}

// 删除模块
const deleteModule = async (moduleId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该模块吗？删除后将无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 调用API删除模块
    await moduleApi.delete(moduleId)
    ElMessage.success('模块删除成功')
    refreshData()
    
    // 如果删除的是当前选中的模块，清空选择
    if (selectedNode.value && selectedNode.value.isModule && selectedNode.value.id === moduleId) {
      selectedNode.value = null
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除模块失败: ' + (error?.message || error))
    }
  }
}

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return '未知'
  return new Date(time).toLocaleString()
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.service-management {
  padding: 24px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.page-description {
  color: var(--text-color-regular);
  margin: 8px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

/* 左侧面板 */
.left-panel {
  width: 320px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.tree-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color-light);
  display: flex;
  align-items: center;
  gap: 8px;
}

.tree-actions {
  flex-shrink: 0;
}

.tree-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tree-node:hover {
  background-color: var(--fill-color-light);
}

.node-icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.node-label {
  flex: 1;
  font-size: 14px;
  color: var(--text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.action-icon {
  color: var(--text-color-secondary);
  cursor: pointer;
  padding: 2px;
  border-radius: 2px;
}

.action-icon:hover {
  background-color: var(--fill-color);
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.empty-detail {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.system-detail,
.module-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--border-color-light);
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  color: var(--color-primary);
}

.detail-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
}

.detail-subtitle {
  margin: 4px 0 0 0;
  color: var(--text-color-regular);
  font-size: 14px;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.info-card {
  margin-bottom: 20px;
}

.card-title {
  font-weight: 600;
  color: var(--text-color-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-placeholder {
  color: var(--text-color-placeholder);
  font-style: italic;
}

/* 模块网格 */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.module-card {
  border: 1px solid var(--border-color-light);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.module-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.module-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.module-icon {
  flex-shrink: 0;
  color: var(--color-primary);
  margin-top: 2px;
}

.module-info {
  flex: 1;
  min-width: 0;
}

.module-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
}

.module-desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-color-regular);
  line-height: 1.4;
}

.module-action {
  color: var(--text-color-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.module-action:hover {
  background-color: var(--fill-color);
}

.module-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.module-tags {
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-tags {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .left-panel {
    width: 280px;
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    height: 300px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
}
</style>