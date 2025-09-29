<template>
  <div class="conflict-highlight">
    <!-- 冲突总览 -->
    <div v-if="conflicts.length > 0" class="conflict-summary">
      <el-alert
        :title="`发现 ${conflicts.length} 个冲突`"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #default>
          <div class="conflict-summary-content">
            <p>在合并参数时发现以下冲突，请选择处理方式：</p>
            <div class="conflict-stats">
              <el-tag v-if="typeConflicts > 0" type="warning" size="small">
                类型冲突: {{ typeConflicts }}
              </el-tag>
              <el-tag v-if="requiredConflicts > 0" type="info" size="small">
                必填冲突: {{ requiredConflicts }}
              </el-tag>
              <el-tag v-if="duplicateConflicts > 0" type="danger" size="small">
                重复名称: {{ duplicateConflicts }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 冲突列表 -->
    <div v-if="conflicts.length > 0" class="conflict-list">
      <div
        v-for="(conflict, index) in conflicts"
        :key="`conflict-${index}`"
        class="conflict-item"
        :class="`conflict-${conflict.type}`"
      >
        <div class="conflict-header">
          <div class="conflict-info">
            <el-icon class="conflict-icon">
              <Warning v-if="conflict.type === 'type_mismatch'" />
              <InfoFilled v-else-if="conflict.type === 'required_conflict'" />
              <Close v-else />
            </el-icon>
            <span class="conflict-path">{{ conflict.path }}</span>
            <el-tag
              :type="getConflictTagType(conflict.type)"
              size="small"
              class="conflict-type-tag"
            >
              {{ getConflictTypeText(conflict.type) }}
            </el-tag>
          </div>
          
          <div class="conflict-actions">
            <el-button-group>
              <el-button
                size="small"
                :type="conflict.resolution === 'keep_existing' ? 'primary' : 'default'"
                @click="resolveConflict(index, 'keep_existing')"
              >
                保留现有
              </el-button>
              <el-button
                size="small"
                :type="conflict.resolution === 'use_incoming' ? 'primary' : 'default'"
                @click="resolveConflict(index, 'use_incoming')"
              >
                使用新值
              </el-button>
              <el-button
                v-if="conflict.type === 'type_mismatch'"
                size="small"
                :type="conflict.resolution === 'manual' ? 'primary' : 'default'"
                @click="resolveConflict(index, 'manual')"
              >
                手动处理
              </el-button>
            </el-button-group>
          </div>
        </div>

        <div class="conflict-details">
          <div class="conflict-comparison">
            <div class="existing-value">
              <div class="value-label">现有值</div>
              <div class="value-content">
                <ParamValueDisplay :param="conflict.existing" />
              </div>
            </div>
            
            <div class="arrow-separator">
              <el-icon><Right /></el-icon>
            </div>
            
            <div class="incoming-value">
              <div class="value-label">新值</div>
              <div class="value-content">
                <ParamValueDisplay :param="conflict.incoming" />
              </div>
            </div>
          </div>

          <!-- 手动处理区域 -->
          <div v-if="conflict.resolution === 'manual'" class="manual-resolution">
            <el-divider content-position="left">手动编辑</el-divider>
            <div class="manual-form">
              <el-form :model="conflict.manualValue" label-width="80px" size="small">
                <el-form-item label="参数名">
                  <el-input v-model="conflict.manualValue.name" />
                </el-form-item>
                <el-form-item label="类型">
                  <el-select v-model="conflict.manualValue.type">
                    <el-option label="字符串" value="string" />
                    <el-option label="数字" value="number" />
                    <el-option label="布尔值" value="boolean" />
                    <el-option label="对象" value="object" />
                    <el-option label="数组" value="array" />
                    <el-option label="文件" value="file" />
                    <el-option label="空值" value="null" />
                  </el-select>
                </el-form-item>
                <el-form-item label="必填">
                  <el-switch v-model="conflict.manualValue.required" />
                </el-form-item>
                <el-form-item label="描述">
                  <el-input v-model="conflict.manualValue.description" type="textarea" :rows="2" />
                </el-form-item>
                <el-form-item label="示例值">
                  <el-input v-model="conflict.manualValue.value" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量操作 -->
    <div v-if="conflicts.length > 1" class="batch-actions">
      <el-divider content-position="left">批量操作</el-divider>
      <div class="batch-buttons">
        <el-button size="small" @click="resolveAllConflicts('keep_existing')">
          全部保留现有
        </el-button>
        <el-button size="small" @click="resolveAllConflicts('use_incoming')">
          全部使用新值
        </el-button>
        <el-button size="small" type="danger" @click="clearAllResolutions">
          清除所有选择
        </el-button>
      </div>
    </div>

    <!-- 解决状态 -->
    <div v-if="conflicts.length > 0" class="resolution-status">
      <el-progress
        :percentage="resolutionProgress"
        :status="resolutionProgress === 100 ? 'success' : 'warning'"
        :stroke-width="6"
      >
        <template #default="{ percentage }">
          <span class="progress-text">
            已解决 {{ resolvedCount }}/{{ conflicts.length }} 个冲突 ({{ percentage }}%)
          </span>
        </template>
      </el-progress>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Warning, InfoFilled, Close, Right } from '@element-plus/icons-vue'
import ParamValueDisplay from './ParamValueDisplay.vue'

// Props
const props = defineProps({
  conflicts: {
    type: Array,
    default: () => []
  },
  autoResolve: {
    type: Boolean,
    default: false
  },
  defaultResolution: {
    type: String,
    default: 'keep_existing',
    validator: (value) => ['keep_existing', 'use_incoming', 'manual'].includes(value)
  }
})

// Emits
const emit = defineEmits(['resolve', 'resolve-all', 'update:conflicts'])

// 计算属性
const typeConflicts = computed(() => 
  props.conflicts.filter(c => c.type === 'type_mismatch').length
)

const requiredConflicts = computed(() => 
  props.conflicts.filter(c => c.type === 'required_conflict').length
)

const duplicateConflicts = computed(() => 
  props.conflicts.filter(c => c.type === 'duplicate_name').length
)

const resolvedCount = computed(() => 
  props.conflicts.filter(c => c.resolution && c.resolution !== 'manual' || 
    (c.resolution === 'manual' && c.manualValue)).length
)

const resolutionProgress = computed(() => 
  props.conflicts.length === 0 ? 100 : Math.round((resolvedCount.value / props.conflicts.length) * 100)
)

// 方法
const getConflictTagType = (type) => {
  switch (type) {
    case 'type_mismatch': return 'warning'
    case 'required_conflict': return 'info'
    case 'duplicate_name': return 'danger'
    default: return 'default'
  }
}

const getConflictTypeText = (type) => {
  switch (type) {
    case 'type_mismatch': return '类型冲突'
    case 'required_conflict': return '必填冲突'
    case 'duplicate_name': return '重复名称'
    default: return '未知冲突'
  }
}

const resolveConflict = (index, resolution) => {
  const conflict = props.conflicts[index]
  conflict.resolution = resolution
  
  // 如果是手动处理，初始化手动值
  if (resolution === 'manual' && !conflict.manualValue) {
    conflict.manualValue = {
      name: conflict.existing.name,
      type: conflict.existing.type,
      required: conflict.existing.required,
      description: conflict.existing.description || '',
      value: conflict.existing.value
    }
  }
  
  emit('resolve', { index, conflict, resolution })
}

const resolveAllConflicts = (resolution) => {
  props.conflicts.forEach((conflict, index) => {
    resolveConflict(index, resolution)
  })
  emit('resolve-all', { resolution, conflicts: props.conflicts })
}

const clearAllResolutions = () => {
  props.conflicts.forEach(conflict => {
    delete conflict.resolution
    delete conflict.manualValue
  })
  emit('update:conflicts', props.conflicts)
}

// 自动解决冲突
watch(() => props.conflicts, (newConflicts) => {
  if (props.autoResolve && newConflicts.length > 0) {
    resolveAllConflicts(props.defaultResolution)
  }
}, { immediate: true })
</script>

<style scoped>
.conflict-highlight {
  margin: 16px 0;
}

.conflict-summary {
  margin-bottom: 16px;
}

.conflict-summary-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.conflict-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.conflict-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  transition: all 0.3s ease;
}

.conflict-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.conflict-item.conflict-type_mismatch {
  border-left: 4px solid #e6a23c;
}

.conflict-item.conflict-required_conflict {
  border-left: 4px solid #409eff;
}

.conflict-item.conflict-duplicate_name {
  border-left: 4px solid #f56c6c;
}

.conflict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.conflict-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.conflict-icon {
  font-size: 16px;
}

.conflict-path {
  font-weight: 600;
  color: #303133;
}

.conflict-type-tag {
  margin-left: 8px;
}

.conflict-details {
  margin-top: 12px;
}

.conflict-comparison {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.existing-value,
.incoming-value {
  flex: 1;
  min-width: 0;
}

.value-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
}

.value-content {
  padding: 8px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  font-size: 13px;
}

.arrow-separator {
  color: #909399;
  font-size: 16px;
}

.manual-resolution {
  margin-top: 16px;
  padding: 16px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
}

.manual-form {
  max-width: 500px;
}

.batch-actions {
  margin: 20px 0;
}

.batch-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.resolution-status {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.progress-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .conflict-comparison {
    flex-direction: column;
    gap: 12px;
  }
  
  .arrow-separator {
    transform: rotate(90deg);
  }
  
  .batch-buttons {
    flex-direction: column;
  }
  
  .conflict-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>