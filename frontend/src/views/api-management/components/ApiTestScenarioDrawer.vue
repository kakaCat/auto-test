<template>
  <el-drawer v-model="visibleLocal" :title="drawerTitle" size="70%" :close-on-click-modal="false" destroy-on-close>
    <div class="scenario-drawer">
      <!-- 工具栏 -->
      <div class="tool-bar">
        <el-button type="primary" :disabled="selectedRows.length === 0" @click="parameterSaveDialogVisible = true">
          保存参数
        </el-button>
        <el-button @click="savedParametersListVisible = true">已保存参数</el-button>
      </div>

      <!-- 筛选区域 -->
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="搜索场景名称/描述" clearable style="width: 280px" @input="loadScenarios">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filters.status" placeholder="状态" clearable style="width: 140px" @change="loadScenarios">
          <el-option label="active" value="active" />
          <el-option label="inactive" value="inactive" />
        </el-select>

        <el-checkbox v-model="filters.is_parameters_saved" @change="loadScenarios">仅显示已保存参数</el-checkbox>

        <el-button @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>

      <!-- 内容区域：左侧列表，右侧创建 -->
      <div class="content-grid">
        <div class="left-panel">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span>场景列表</span>
                <el-button type="primary" link @click="loadScenarios">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>

            <el-table :data="scenarioList" v-loading="loading" stripe>
              <el-table-column type="selection" width="55" @selection-change="handleSelectionChange" />
              <el-table-column prop="name" label="名称" min-width="180" />
              <el-table-column prop="scenario_type" label="类型" width="120" />
              <el-table-column prop="status" label="状态" width="120" />
              <el-table-column label="标签" min-width="200">
                <template #default="{ row }">
                  <el-tag v-for="tag in (row.tags || [])" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <div class="right-panel">
          <el-card shadow="never">
            <template #header>
              <span>新建场景</span>
            </template>

            <el-form :model="createForm" label-width="96px">
              <el-form-item label="名称">
                <el-input v-model="createForm.name" placeholder="请输入场景名称" />
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="createForm.scenario_type" placeholder="选择类型" style="width: 180px">
                  <el-option label="normal" value="normal" />
                  <el-option label="exception" value="exception" />
                  <el-option label="boundary" value="boundary" />
                  <el-option label="security" value="security" />
                  <el-option label="performance" value="performance" />
                </el-select>
              </el-form-item>
              <el-form-item label="描述">
                <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="选填：场景描述" />
              </el-form-item>

              <div class="form-actions">
                <el-button type="primary" :disabled="!canCreate" @click="handleCreate">创建场景</el-button>
              </div>
            </el-form>
          </el-card>
        </div>
      </div>
    </div>
  </el-drawer>

  <!-- 参数保存对话框 -->
  <ParameterSaveDialog
    v-model:visible="parameterSaveDialogVisible"
    :selected="selectedRows"
    :api-id="String(props.apiInfo?.id || '')"
    @saved="handleParamsSaved"
  />

  <!-- 已保存参数列表 -->
  <SavedParametersList
    v-model:visible="savedParametersListVisible"
    :api-id="String(props.apiInfo?.id || '')"
    @applied="handleParamsApplied"
  />
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import unifiedApi from '@/api/unified-api'
import ParameterSaveDialog from './ParameterSaveDialog.vue'
import SavedParametersList from './SavedParametersList.vue'
import type { ScenarioListParams, ScenarioData, ScenarioCreateData } from '@/api/scenario'

const props = defineProps({
  visible: { type: Boolean, default: false },
  apiInfo: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:visible', 'params-applied'])

const visibleLocal = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const drawerTitle = computed(() => {
  return props.apiInfo?.name ? `场景测试 - ${props.apiInfo.name}` : '场景测试'
})

const loading = ref(false)
const scenarioList = ref([] as ScenarioData[])
const selectedRows = ref([] as any[])
const parameterSaveDialogVisible = ref(false)
const savedParametersListVisible = ref(false)

const filters = reactive({
  keyword: '',
  status: '',
  is_parameters_saved: false
})

const createForm = reactive({
  name: '',
  description: '',
  scenario_type: 'normal'
})

const canCreate = computed(() => !!createForm.name && !!props.apiInfo?.id)

const loadScenarios = async () => {
  if (!props.apiInfo?.id) return
  try {
    loading.value = true
    const params: ScenarioListParams = { api_id: String(props.apiInfo.id) }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.status) params.status = filters.status
    if (filters.is_parameters_saved) params.is_parameters_saved = true

    const resp: any = await unifiedApi.scenario.getList(params)
    const data = Array.isArray(resp) ? resp : (resp?.data ?? [])
    scenarioList.value = Array.isArray(data) ? (data as ScenarioData[]) : []
  } catch (err: any) {
    console.error('加载场景列表失败:', err)
    ElMessage.error(`加载场景失败：${(err && err.message) || '网络错误'}`)
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = Array.isArray(rows) ? rows : []
}

const handleCreate = async () => {
  if (!props.apiInfo?.id) return
  try {
    const payload = {
      name: createForm.name,
      description: createForm.description,
      scenario_type: createForm.scenario_type as ScenarioCreateData['scenario_type'],
      api_id: String(props.apiInfo.id)
    }
    await unifiedApi.scenario.create(payload)
    ElMessage.success('创建成功')
    createForm.name = ''
    createForm.description = ''
    createForm.scenario_type = 'normal'
    await loadScenarios()
  } catch (err: any) {
    console.error('创建场景失败:', err)
    ElMessage.error(`创建失败：${(err && err.message) || '网络错误'}`)
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.is_parameters_saved = false
  loadScenarios()
}

watch(() => props.visible, (val) => {
  if (val) {
    loadScenarios()
  }
})

const handleParamsSaved = async () => {
  parameterSaveDialogVisible.value = false
  await loadScenarios()
}

const handleParamsApplied = async (row: any) => {
  try {
    // 关闭列表对话框
    savedParametersListVisible.value = false
    if (!row?.id && !row?.scenario_id) {
      ElMessage.warning('缺少场景ID，无法应用参数')
      return
    }
    const scenarioId = String(row.id || row.scenario_id)
    const resp: any = await unifiedApi.scenario.getDetail(scenarioId)
    const detail = resp?.data ?? resp
    const variables = detail?.variables || {}
    const config = detail?.config || {}

    // 向父级抛出参数应用事件
    emit('params-applied', { scenarioId, variables, config, detail })
    const varCount = Object.keys(variables || {}).length
    const cfgCount = Object.keys(config || {}).length
    ElMessage.success(`已应用参数：变量${varCount}项，配置${cfgCount}项`)
  } catch (err: any) {
    console.error('应用参数失败:', err)
    ElMessage.error(`应用失败：${(err && err.message) || '网络错误'}`)
  }
}

</script>

<style scoped>
.scenario-drawer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tool-bar {
  display: flex;
  gap: 8px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-actions {
  margin-top: 12px;
}

.left-panel, .right-panel { min-height: 420px; }
</style>