<template>
  <el-dialog v-model="visibleLocal" title="保存参数" width="520px" :close-on-click-modal="false" destroy-on-close>
    <el-form :model="form" label-width="96px">
      <el-form-item label="模板名称">
        <el-input v-model="form.name" placeholder="请输入名称" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="选填：描述" />
      </el-form-item>
      <el-form-item label="标签">
        <el-select v-model="form.tags" multiple collapse-tags placeholder="选择或输入标签">
          <el-option v-for="tag in form.tags" :key="tag" :label="tag" :value="tag" />
        </el-select>
      </el-form-item>
      <el-form-item label="保存范围">
        <el-radio-group v-model="form.scope">
          <el-radio label="request">请求参数</el-radio>
          <el-radio label="expected">期望结果</el-radio>
          <el-radio label="all">全部</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visibleLocal = false">取消</el-button>
      <el-button type="primary" :disabled="!canSave" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { scenarioApi } from '@/api/unified-api'

const props = defineProps({
  visible: { type: Boolean, default: false },
  selected: { type: Array, default: () => [] },
  apiId: { type: String, default: '' }
})

const emit = defineEmits(['update:visible', 'saved'])

const visibleLocal = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const form = reactive({
  name: '',
  description: '',
  tags: [] as string[],
  scope: 'all'
})

const canSave = computed(() => props.selected.length > 0 && !!form.name)

const handleSave = async () => {
  if (!props.apiId) {
    ElMessage.error('缺少 API 上下文')
    return
  }
  try {
    const savedId = `param-${Date.now()}`
    const updates = props.selected.map((row: any) =>
      scenarioApi.update(String(row.id || row.scenario_id || ''), {
        is_parameters_saved: true,
        saved_parameters_id: savedId,
        tags: form.tags
      })
    )
    await Promise.all(updates)
    ElMessage.success('参数保存成功')
    emit('saved')
  } catch (err: any) {
    console.error('保存参数失败:', err)
    ElMessage.error(`保存失败：${(err && err.message) || '网络错误'}`)
  }
}
</script>

<style scoped>
</style>