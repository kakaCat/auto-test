<template>
  <el-dialog v-model="visible" :title="`Mock管理 - ${apiInfo.name}`" width="90%" :before-close="handleClose" class="mock-management-dialog">
    <div class="mock-management">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="showAddMockDialog">
            <el-icon><Plus /></el-icon>
            新增Mock
          </el-button>
          <el-button @click="importMocks">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
          <el-button @click="exportMocks" :disabled="mockList.length === 0">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-input v-model="searchKeyword" placeholder="搜索Mock配置..." style="width: 250px" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>

      <!-- Mock列表 -->
      <div class="mock-list">
        <el-table :data="filteredMockList" stripe border height="500" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="Mock名称" min-width="150">
            <template #default="{ row }">
              <div class="mock-name">
                <span>{{ row.name }}</span>
                <el-tag v-if="!row.enabled" type="info" size="small">已禁用</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="priority" label="优先级" width="80" sortable>
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" size="small">
                {{ row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="匹配条件" min-width="200">
            <template #default="{ row }">
              <div class="match-conditions">
                <el-tag>
                  v-for="condition in row.matchConditions.slice(0, 2)"
                  :key="condition.id"
                  size="small"
                  style="margin-right: 4px; margin-bottom: 2px;"
                  {{ condition.field }} {{ condition.operator }} {{ condition.value }}
                </el-tag>
                <span v-if="row.matchConditions.length > 2" class="more-conditions">
                  +{{ row.matchConditions.length - 2 }}个条件
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="statusCode" label="状态码" width="80" />
          <el-table-column prop="delay" label="延迟(ms)" width="90" />
          <el-table-column label="启用状态" width="100">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" @change="toggleMockStatus(row)" :loading="row.updating" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="text" @click="testMock(row)">
                <el-icon><VideoPlay /></el-icon>
                测试
              </el-button>
              <el-button type="text" @click="editMock(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="text" @click="duplicateMock(row)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
              <el-button type="text" @click="deleteMock(row)" style="color: var(--el-color-danger)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 批量操作 -->
      <div v-if="selectedMocks.length > 0" class="batch-actions">
        <span>已选择 {{ selectedMocks.length }} 项</span>
        <el-button @click="batchEnable">批量启用</el-button>
        <el-button @click="batchDisable">批量禁用</el-button>
        <el-button type="danger" @click="batchDelete">批量删除</el-button>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- Mock编辑对话框 -->
  <MockEditDialog v-model="mockEditVisible" :mock-data="currentMock" :api-info="apiInfo" @save="handleMockSave" />

  <!-- Mock测试对话框 -->
  <MockTestDialog v-model="mockTestVisible" :mock-data="currentMock" :api-info="apiInfo" />
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Upload, Download, Search, VideoPlay, Edit, CopyDocument, Delete
} from '@element-plus/icons-vue'
import type { MockConfig } from '@/types/mock'
import type { ApiItem } from '../data/tableColumns'
import MockEditDialog from './MockEditDialog.vue'
import MockTestDialog from './MockTestDialog.vue'

// Props
interface Props {
  modelValue: boolean
  apiInfo: ApiItem
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'mock-updated': []
}>()

// 响应式数据
const visible = ref(props.modelValue)
const searchKeyword = ref('')
const selectedMocks = ref<MockConfig[]>([])
const mockEditVisible = ref(false)
const mockTestVisible = ref(false)
const currentMock = ref<MockConfig | null>(null)

// Mock列表数据
const mockList = ref<MockConfig[]>([
  {
    id: '1',
    apiId: props.apiInfo.id?.toString() || '',
    name: '成功响应Mock',
    description: '模拟正常的成功响应',
    enabled: true,
    priority: 1,
    matchConditions: [
      {
        id: '1',
        type: 'exact',
        field: 'body.type',
        operator: 'equals',
        value: 'success',
        description: '请求类型为success'
      }
    ],
    responseData: {
      code: 200,
      message: '操作成功',
      data: {
        id: 1,
        name: '测试数据',
        status: 'active'
      }
    },
    statusCode: 200,
    delay: 100,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '2',
    apiId: props.apiInfo.id?.toString() || '',
    name: '错误响应Mock',
    description: '模拟错误响应场景',
    enabled: false,
    priority: 2,
    matchConditions: [
      {
        id: '2',
        type: 'exact',
        field: 'body.type',
        operator: 'equals',
        value: 'error',
        description: '请求类型为error'
      }
    ],
    responseData: {
      code: 400,
      message: '请求参数错误',
      data: null
    },
    statusCode: 400,
    delay: 50,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
])

// 计算属性
const filteredMockList = computed(() => {
  if (!searchKeyword.value) return mockList.value
  
  const keyword = searchKeyword.value.toLowerCase()
  return mockList.value.filter(mock => 
    mock.name.toLowerCase().includes(keyword) ||
    mock.description?.toLowerCase().includes(keyword) ||
    mock.matchConditions.some(condition => 
      condition.field.toLowerCase().includes(keyword) ||
      String(condition.value).toLowerCase().includes(keyword)
    )
  )
})

// 监听visible变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 方法
const handleClose = () => {
  visible.value = false
}

const handleSelectionChange = (selection: MockConfig[]) => {
  selectedMocks.value = selection
}

const getPriorityType = (priority: number) => {
  if (priority <= 3) return 'danger'
  if (priority <= 6) return 'warning'
  return 'info'
}

const showAddMockDialog = () => {
  currentMock.value = null
  mockEditVisible.value = true
}

const editMock = (mock: MockConfig) => {
  currentMock.value = { ...mock }
  mockEditVisible.value = true
}

const duplicateMock = (mock: MockConfig) => {
  const newMock: MockConfig = {
    ...mock,
    id: Date.now().toString(),
    name: `${mock.name} - 副本`,
    enabled: false,
    priority: Math.max(...mockList.value.map(m => m.priority)) + 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
  mockList.value.push(newMock)
  ElMessage.success('Mock配置复制成功')
}

const deleteMock = async (mock: MockConfig) => {
  try {
    await ElMessageBox.confirm(`确定要删除Mock配置"${mock.name}"吗？`, '确认删除', {
      type: 'warning'
    })
    
    const index = mockList.value.findIndex(m => m.id === mock.id)
    if (index > -1) {
      mockList.value.splice(index, 1)
      ElMessage.success('删除成功')
      emit('mock-updated')
    }
  } catch (error) {
    // 用户取消删除
  }
}

const toggleMockStatus = async (mock: MockConfig) => {
  try {
    mock.updating = true
    // 这里应该调用API更新状态
    await new Promise(resolve => setTimeout(resolve, 500)) // 模拟API调用
    
    mock.updatedAt = new Date().toISOString()
    ElMessage.success(`Mock配置已${mock.enabled ? '启用' : '禁用'}`)
    emit('mock-updated')
  } catch (error) {
    // 恢复状态
    mock.enabled = !mock.enabled
    ElMessage.error('状态更新失败')
  } finally {
    mock.updating = false
  }
}

const testMock = (mock: MockConfig) => {
  currentMock.value = mock
  mockTestVisible.value = true
}

const handleMockSave = (mockData: MockConfig) => {
  if (mockData.id) {
    // 更新现有Mock
    const index = mockList.value.findIndex(m => m.id === mockData.id)
    if (index > -1) {
      mockList.value[index] = { ...mockData, updatedAt: new Date().toISOString() }
      ElMessage.success('Mock配置更新成功')
    }
  } else {
    // 新增Mock
    const newMock: MockConfig = {
      ...mockData,
      id: Date.now().toString(),
      apiId: props.apiInfo.id?.toString() || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    mockList.value.push(newMock)
    ElMessage.success('Mock配置创建成功')
  }
  
  mockEditVisible.value = false
  emit('mock-updated')
}

const batchEnable = async () => {
  try {
    selectedMocks.value.forEach(mock => {
      mock.enabled = true
      mock.updatedAt = new Date().toISOString()
    })
    ElMessage.success(`已启用 ${selectedMocks.value.length} 个Mock配置`)
    emit('mock-updated')
  } catch (error) {
    ElMessage.error('批量启用失败')
  }
}

const batchDisable = async () => {
  try {
    selectedMocks.value.forEach(mock => {
      mock.enabled = false
      mock.updatedAt = new Date().toISOString()
    })
    ElMessage.success(`已禁用 ${selectedMocks.value.length} 个Mock配置`)
    emit('mock-updated')
  } catch (error) {
    ElMessage.error('批量禁用失败')
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedMocks.value.length} 个Mock配置吗？`, '确认删除', {
      type: 'warning'
    })
    
    const idsToDelete = selectedMocks.value.map(m => m.id)
    mockList.value = mockList.value.filter(m => !idsToDelete.includes(m.id))
    selectedMocks.value = []
    
    ElMessage.success('批量删除成功')
    emit('mock-updated')
  } catch (error) {
    // 用户取消删除
  }
}

const importMocks = () => {
  // TODO: 实现Mock导入功能
  ElMessage.info('导入功能开发中...')
}

const exportMocks = () => {
  // TODO: 实现Mock导出功能
  ElMessage.info('导出功能开发中...')
}
</script>

<style scoped>
.mock-management-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.mock-management {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.mock-list {
  flex: 1;
  overflow: hidden;
}

.mock-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.match-conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.more-conditions {
  color: #909399;
  font-size: 12px;
}

.batch-actions {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 2000;
}

.dialog-footer {
  text-align: right;
}
</style>