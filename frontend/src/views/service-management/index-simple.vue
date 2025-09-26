<template>
  <div class="service-management">
    <div class="header">
      <h2>服务管理</h2>
      <div class="actions">
        <el-button type="primary" @click="showSystemDialog">
          新增系统
        </el-button>
      </div>
    </div>

    <!-- 系统列表 -->
    <div class="systems-container">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else>
        <div v-for="system in systems" :key="system.id" class="system-card">
          <div class="system-header">
            <h3>{{ system.name }}</h3>
            <div class="system-actions">
              <el-button size="small" @click="editSystem(system)">编辑</el-button>
              <el-button size="small" type="primary" @click="showModuleDialog(system.id)">
                新增模块
              </el-button>
              <el-button size="small" type="danger" @click="deleteSystem(system.id)">
                删除
              </el-button>
            </div>
          </div>
          <div class="system-info">
            <p>{{ system.description }}</p>
            <p>URL: {{ system.url }}</p>
            <p>状态: {{ system.enabled ? '启用' : '禁用' }}</p>
          </div>

          <!-- 模块列表 -->
          <div class="modules-container">
            <h4>模块列表</h4>
            <div v-if="system.modules && system.modules.length > 0">
              <div v-for="module in system.modules" :key="module.id" class="module-item">
                <div class="module-info">
                  <strong>{{ module.name }}</strong>
                  <p>{{ module.description }}</p>
                  <p>URL: {{ module.url }}</p>
                  <p>状态: {{ module.enabled ? '启用' : '禁用' }}</p>
                </div>
                <div class="module-actions">
                  <el-button size="small" @click="editModule(module)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteModule(module.id)">
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            <div v-else class="no-modules">暂无模块</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统表单对话框 -->
    <el-dialog
      v-model="systemDialogVisible"
      :title="isEditingSystem ? '编辑系统' : '新增系统'"
      width="500px"
    >
      <el-form :model="systemFormData" label-width="80px">
        <el-form-item label="系统名称" required>
          <el-input v-model="systemFormData.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="systemFormData.description" type="textarea" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="systemFormData.url" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="systemFormData.category">
            <el-option label="内容管理" value="CONTENT_MANAGEMENT" />
            <el-option label="用户管理" value="USER_MANAGEMENT" />
            <el-option label="系统管理" value="SYSTEM_MANAGEMENT" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="systemFormData.icon" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="systemFormData.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="systemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSystemSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 模块表单对话框 -->
    <el-dialog
      v-model="moduleDialogVisible"
      :title="isEditingModule ? '编辑模块' : '新增模块'"
      width="500px"
    >
      <el-form :model="moduleFormData" label-width="80px">
        <el-form-item label="模块名称" required>
          <el-input v-model="moduleFormData.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="moduleFormData.description" type="textarea" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="moduleFormData.url" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="moduleFormData.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleModuleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiManagementApi } from '@/api/api-management-simple'

// 类型定义
interface System {
  id: number
  name: string
  description?: string
  url?: string
  enabled: boolean
  modules?: Module[]
}

interface Module {
  id: number
  system_id: number
  name: string
  description?: string
  url?: string
  enabled: boolean
  version?: string
}

type SystemFormData = {
  id?: number
  name: string
  description: string
  url: string
  category: string
  icon: string
  enabled: boolean
}

type ModuleFormData = {
  id?: number
  system_id?: number
  name: string
  description: string
  url: string
  enabled: boolean
  tags: any[]
}

// 响应式数据
const error = ref('')
const loading = ref(false)
const systems = ref<System[]>([])

// 对话框状态
const systemDialogVisible = ref(false)
const moduleDialogVisible = ref(false)
const isEditingSystem = ref(false)
const isEditingModule = ref(false)

// 默认表单数据
const defaultSystemFormData: SystemFormData = {
  name: '',
  description: '',
  url: '',
  category: 'CONTENT_MANAGEMENT',
  icon: 'system',
  enabled: true
}

const defaultModuleFormData: ModuleFormData = {
  name: '',
  description: '',
  url: '',
  enabled: true,
  tags: []
}

// 表单数据
const systemFormData = ref<SystemFormData>({ ...defaultSystemFormData })
const moduleFormData = ref<ModuleFormData>({ ...defaultModuleFormData })

// 方法
const loadSystems = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await apiManagementApi.getServiceList()
    systems.value = response.data || []
    
    // 为每个系统加载模块
     for (const system of systems.value) {
       const moduleResponse = await apiManagementApi.getModuleList({ 
         system_id: system.id,
         keyword: '',
         method: '',
         status: ''
       })
       system.modules = moduleResponse.data || []
     }
  } catch (err: any) {
    error.value = err.message || '加载系统列表失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const showSystemDialog = () => {
  isEditingSystem.value = false
  systemFormData.value = { ...defaultSystemFormData }
  systemDialogVisible.value = true
}

const editSystem = (system: System) => {
  isEditingSystem.value = true
  systemFormData.value = {
    id: system.id,
    name: system.name,
    description: system.description || '',
    url: system.url || '',
    category: 'CONTENT_MANAGEMENT',
    icon: 'system',
    enabled: system.enabled
  }
  systemDialogVisible.value = true
}

const showModuleDialog = (systemId: number) => {
  isEditingModule.value = false
  moduleFormData.value = { 
    ...defaultModuleFormData,
    system_id: systemId
  }
  moduleDialogVisible.value = true
}

const editModule = (module: Module) => {
  isEditingModule.value = true
  moduleFormData.value = {
    id: module.id,
    system_id: module.system_id,
    name: module.name,
    description: module.description || '',
    url: module.url || '',
    enabled: module.enabled,
    tags: []
  }
  moduleDialogVisible.value = true
}

const handleSystemSubmit = async () => {
  try {
    if (isEditingSystem.value && systemFormData.value.id) {
      await apiManagementApi.updateService(systemFormData.value.id, systemFormData.value)
      ElMessage.success('系统更新成功')
    } else {
      await apiManagementApi.createService(systemFormData.value)
      ElMessage.success('系统创建成功')
    }
    systemDialogVisible.value = false
    await loadSystems()
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  }
}

const handleModuleSubmit = async () => {
  try {
    if (isEditingModule.value && moduleFormData.value.id) {
      if (!moduleFormData.value.system_id) {
        ElMessage.error('请选择所属系统')
        return
      }
      const updateData = {
        system_id: moduleFormData.value.system_id,
        name: moduleFormData.value.name,
        description: moduleFormData.value.description,
        url: moduleFormData.value.url,
        enabled: moduleFormData.value.enabled,
        tags: moduleFormData.value.tags || []
      }
      await apiManagementApi.updateApi(moduleFormData.value.id, updateData)
      ElMessage.success('模块更新成功')
    } else {
      if (!moduleFormData.value.system_id) {
        ElMessage.error('请选择所属系统')
        return
      }
      const createData = {
        system_id: moduleFormData.value.system_id,
        name: moduleFormData.value.name,
        description: moduleFormData.value.description,
        url: moduleFormData.value.url,
        enabled: moduleFormData.value.enabled,
        tags: moduleFormData.value.tags
      }
      await apiManagementApi.createApi(createData)
      ElMessage.success('模块创建成功')
    }
    moduleDialogVisible.value = false
    await loadSystems()
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  }
}

const deleteSystem = async (systemId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个系统吗？', '确认删除', {
      type: 'warning'
    })
    await apiManagementApi.deleteService(systemId)
    ElMessage.success('系统删除成功')
    await loadSystems()
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除失败')
    }
  }
}

const deleteModule = async (moduleId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模块吗？', '确认删除', {
      type: 'warning'
    })
    await apiManagementApi.deleteApi(moduleId)
    ElMessage.success('模块删除成功')
    await loadSystems()
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  loadSystems()
})
</script>

<style scoped>
.service-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.systems-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.system-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.system-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.system-header h3 {
  margin: 0;
  color: #303133;
}

.system-actions {
  display: flex;
  gap: 10px;
}

.system-info {
  margin-bottom: 20px;
  color: #606266;
}

.system-info p {
  margin: 5px 0;
}

.modules-container {
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.modules-container h4 {
  margin: 0 0 15px 0;
  color: #409eff;
}

.module-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 10px;
  background: #fafafa;
}

.module-info {
  flex: 1;
}

.module-info strong {
  color: #303133;
  display: block;
  margin-bottom: 5px;
}

.module-info p {
  margin: 3px 0;
  color: #606266;
  font-size: 14px;
}

.module-actions {
  display: flex;
  gap: 10px;
}

.no-modules {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.error {
  color: #f56c6c;
}
</style>