<template>
  <div class="requirement-tree">
    <!-- 搜索框 -->
    <div class="tree-search">
      <el-input
        v-model="searchText"
        placeholder="搜索项目或需求..."
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <!-- 操作按钮 -->
    <div class="tree-actions">
      <el-button
        size="small"
        :icon="Plus"
        @click="handleAddProject"
      >
        新增项目
      </el-button>
      <el-button
        size="small"
        :icon="Refresh"
        @click="refreshTree"
      >
        刷新
      </el-button>
    </div>

    <!-- 树形结构 -->
    <div class="tree-container">
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="treeProps"
        :filter-node-method="filterNode"
        :expand-on-click-node="false"
        :highlight-current="true"
        node-key="id"
        @node-click="handleNodeClick"
        @node-contextmenu="handleNodeContextMenu"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <div class="node-content">
              <el-icon class="node-icon">
                <component :is="getNodeIcon(data)" />
              </el-icon>
              <span class="node-label">{{ node.label }}</span>
              <div
                v-if="data.type === 'requirement'"
                class="node-badges"
              >
                <el-tag
                  size="small"
                  :type="getPriorityType(data.priority)"
                >
                  {{ getPriorityText(data.priority) }}
                </el-tag>
                <el-tag
                  size="small"
                  :type="getStatusType(data.status)"
                >
                  {{ getStatusText(data.status) }}
                </el-tag>
              </div>
            </div>
            <div
              class="node-actions"
              @click.stop
            >
              <el-dropdown @command="(command) => handleNodeAction(command, data)">
                <el-button
                  size="small"
                  text
                  :icon="MoreFilled"
                />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-if="data.type === 'project'"
                      command="add-requirement"
                    >
                      <el-icon><Plus /></el-icon>添加需求
                    </el-dropdown-item>
                    <el-dropdown-item command="edit">
                      <el-icon><Edit /></el-icon>编辑
                    </el-dropdown-item>
                    <el-dropdown-item
                      command="delete"
                      divided
                    >
                      <el-icon><Delete /></el-icon>删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>
      </el-tree>
    </div>

    <!-- 项目表单对话框 -->
    <el-dialog
      v-model="projectDialogVisible"
      :title="projectDialogMode === 'create' ? '新增项目' : '编辑项目'"
      width="500px"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        :rules="projectFormRules"
        label-width="100px"
      >
        <el-form-item
          label="项目名称"
          prop="name"
        >
          <el-input
            v-model="projectForm.name"
            placeholder="请输入项目名称"
          />
        </el-form-item>
        <el-form-item
          label="项目描述"
          prop="description"
        >
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item
          label="项目负责人"
          prop="owner"
        >
          <el-input
            v-model="projectForm.owner"
            placeholder="请输入负责人"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          @click="handleProjectSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Refresh, MoreFilled, Edit, Delete,
  Folder, Document, FolderOpened
} from '@element-plus/icons-vue'
import { requirementApi } from '@/api/requirement-management'

// 组件事件定义
const emit = defineEmits(['node-click', 'node-select'])

// 响应式数据
const treeRef = ref()
const projectFormRef = ref()
const searchText = ref('')
const treeData = ref([])
const selectedNode = ref(null)

// 项目表单对话框
const projectDialogVisible = ref(false)
const projectDialogMode = ref('create') // create | edit
const projectForm = reactive({
  id: '',
  name: '',
  description: '',
  owner: ''
})

// 树形配置
const treeProps = {
  children: 'children',
  label: 'name',
  disabled: 'disabled'
}

// 表单验证规则
const projectFormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 事件处理函数
const handleNodeClick = (data, node) => {
  selectedNode.value = data
  emit('node-click', data, node)
}

const handleNodeContextMenu = (event, data, node) => {
  // 右键菜单处理
  event.preventDefault()
}

const handleNodeAction = async (command, data) => {
  switch (command) {
    case 'add-requirement':
      emit('node-click', { ...data, action: 'add-requirement' })
      break
    case 'edit':
      if (data.type === 'project') {
        handleEditProject(data)
      } else {
        emit('node-click', { ...data, action: 'edit' })
      }
      break
    case 'delete':
      await handleDeleteNode(data)
      break
  }
}

const handleAddProject = () => {
  projectDialogMode.value = 'create'
  resetProjectForm()
  projectDialogVisible.value = true
}

const handleEditProject = (project) => {
  projectDialogMode.value = 'edit'
  Object.assign(projectForm, project)
  projectDialogVisible.value = true
}

const handleDeleteNode = async (data) => {
  try {
    const message = data.type === 'project' 
      ? `确定要删除项目"${data.name}"及其所有需求吗？`
      : `确定要删除需求"${data.name}"吗？`
    
    await ElMessageBox.confirm(message, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    if (data.type === 'project') {
      await requirementApi.deleteProject(data.id)
    } else {
      await requirementApi.deleteRequirement(data.id)
    }
    
    ElMessage.success('删除成功')
    refreshTree()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

const handleProjectSubmit = async () => {
  try {
    await projectFormRef.value.validate()
    
    if (projectDialogMode.value === 'create') {
      await requirementApi.createProject(projectForm)
      ElMessage.success('项目创建成功')
    } else {
      await requirementApi.updateProject(projectForm.id, projectForm)
      ElMessage.success('项目更新成功')
    }
    
    projectDialogVisible.value = false
    refreshTree()
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  }
}

const handleSearch = () => {
  nextTick(() => {
    treeRef.value?.filter(searchText.value)
  })
}

const filterNode = (value, data) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

// 数据加载函数
const loadTreeData = async () => {
  try {
    const response = await requirementApi.getRequirementTree()
    treeData.value = response.data || []
  } catch (error) {
    console.error('加载需求树失败：', error)
    // 使用模拟数据
    treeData.value = getMockTreeData()
  }
}

const refreshTree = () => {
  loadTreeData()
}

// 辅助函数
const getNodeIcon = (data) => {
  switch (data.type) {
    case 'project':
      return data.expanded ? FolderOpened : Folder
    case 'epic':
      return Folder
    case 'feature':
      return Document
    case 'requirement':
      return Document
    default:
      return Document
  }
}

const getPriorityType = (priority) => {
  const typeMap = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    critical: '关键',
    high: '高',
    medium: '中',
    low: '低'
  }
  return textMap[priority] || '未设置'
}

const getStatusType = (status) => {
  const typeMap = {
    draft: 'info',
    in_development: 'warning',
    in_testing: 'primary',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    in_development: '开发中',
    in_testing: '测试中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || '未知'
}

const resetProjectForm = () => {
  Object.assign(projectForm, {
    id: '',
    name: '',
    description: '',
    owner: ''
  })
}

// 模拟数据（开发阶段使用）
const getMockTreeData = () => {
  return [
    {
      id: 'proj-001',
      name: '用户管理系统',
      type: 'project',
      children: [
        {
          id: 'epic-001',
          name: '用户认证模块',
          type: 'epic',
          children: [
            {
              id: 'req-001',
              name: '用户登录功能',
              type: 'requirement',
              priority: 'high',
              status: 'in_development'
            },
            {
              id: 'req-002',
              name: '用户注册功能',
              type: 'requirement',
              priority: 'high',
              status: 'in_testing'
            }
          ]
        },
        {
          id: 'epic-002',
          name: '权限管理模块',
          type: 'epic',
          children: [
            {
              id: 'req-003',
              name: '角色权限配置',
              type: 'requirement',
              priority: 'medium',
              status: 'draft'
            }
          ]
        }
      ]
    },
    {
      id: 'proj-002',
      name: '订单管理系统',
      type: 'project',
      children: [
        {
          id: 'req-004',
          name: '订单创建功能',
          type: 'requirement',
          priority: 'high',
          status: 'completed'
        },
        {
          id: 'req-005',
          name: '订单查询功能',
          type: 'requirement',
          priority: 'medium',
          status: 'in_development'
        }
      ]
    }
  ]
}

// 暴露方法给父组件
defineExpose({
  refreshTree,
  getSelectedNode: () => selectedNode.value
})

// 组件挂载
onMounted(() => {
  loadTreeData()
})

// 监听搜索文本变化
watch(searchText, (val) => {
  treeRef.value?.filter(val)
})
</script>

<style scoped>
.requirement-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.tree-search {
  margin-bottom: 12px;
}

.tree-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tree-container {
  flex: 1;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}

.node-content {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.node-icon {
  margin-right: 8px;
  color: #606266;
}

.node-label {
  flex: 1;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-badges {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

/* 树节点样式优化 */
:deep(.el-tree-node__content) {
  height: auto;
  padding: 8px 0;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #e6f7ff;
  color: #1890ff;
}

:deep(.el-tree-node__expand-icon) {
  color: #606266;
}

:deep(.el-tree-node__expand-icon.expanded) {
  transform: rotate(90deg);
}

/* 标签样式 */
.el-tag {
  font-size: 11px;
  height: 18px;
  line-height: 16px;
}
</style>