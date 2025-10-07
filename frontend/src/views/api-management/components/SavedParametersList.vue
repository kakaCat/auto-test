<template>
  <el-dialog
    v-model="visibleLocal"
    title="已保存参数"
    width="720px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="list-toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索场景名称/描述"
        clearable
        style="width: 300px"
        @input="loadSavedScenarios"
      />
      <el-button @click="loadSavedScenarios">
        刷新
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="savedList"
      height="420"
    >
      <el-table-column
        prop="name"
        label="场景名称"
        min-width="200"
      />
      <el-table-column
        prop="saved_parameters_id"
        label="参数ID"
        width="180"
      />
      <el-table-column
        prop="scenario_type"
        label="类型"
        width="120"
      />
      <el-table-column
        label="操作"
        width="140"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            @click="applyParameters(row)"
          >
            应用
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="visibleLocal = false">
        关闭
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { scenarioApi } from '@/api/unified-api'
import { normalizeList } from '@/utils/listNormalizer'

const props = defineProps({
  visible: { type: Boolean, default: false },
  apiId: { type: String, default: '' }
})
const emit = defineEmits(['update:visible', 'applied'])

const visibleLocal = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const loading = ref(false)
const savedList = ref<any[]>([])
const keyword = ref('')

const loadSavedScenarios = async () => {
  if (!props.apiId) return
  try {
    loading.value = true
    const params: any = { api_id: props.apiId, is_parameters_saved: true }
    if (keyword.value) params.keyword = keyword.value
    const resp = await scenarioApi.getList(params)
    const normalized = normalizeList(resp)
    const data = normalized.list
    savedList.value = Array.isArray(data) ? (data as any[]) : []
  } catch (err: any) {
    console.error('加载已保存参数列表失败:', err)
    ElMessage.error(`加载失败：${(err && err.message) || '网络错误'}`)
  } finally {
    loading.value = false
  }
}

const applyParameters = (row: any) => {
  emit('applied', row)
  ElMessage.success('已应用参数（示例占位）')
}

watch(() => props.visible, (val) => {
  if (val) loadSavedScenarios()
})
</script>

<style scoped>
.list-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
</style>