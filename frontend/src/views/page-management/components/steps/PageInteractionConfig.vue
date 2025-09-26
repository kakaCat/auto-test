<template>
  <div class="page-interaction-config">
    <div class="config-container">
      <!-- 左侧事件配置 -->
      <div class="event-configuration">
        <div class="config-header">
          <h3>交互事件配置</h3>
          <p>配置页面的交互事件和触发条件</p>
          <el-button type="primary" size="small" @click="addEvent">
            添加事件
          </el-button>
        </div>

        <div class="event-list">
          <div v-if="interactionData.events.length === 0" class="empty-state">
            <el-empty description="暂无交互事件" />
          </div>

          <div v-else class="event-items">
            <div
              v-for="(event, index) in interactionData.events"
              :key="event.id"
              class="event-item"
              :class="{ active: selectedEvent?.id === event.id }"
              @click="selectEvent(event)"
            >
              <div class="event-header">
                <div class="event-info">
                  <span class="event-name">{{ event.name }}</span>
                  <el-tag :type="getEventTypeTag(event.trigger.type)" size="small">
                    {{ getEventTypeLabel(event.trigger.type) }}
                  </el-tag>
                  <el-switch
                    v-model="event.enabled"
                    size="small"
                    @click.stop
                  />
                </div>
                <div class="event-actions">
                  <el-button size="small" @click.stop="editEvent(event)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click.stop="removeEvent(index)">
                    删除
                  </el-button>
                </div>
              </div>

              <div class="event-details">
                <div class="detail-row">
                  <span class="detail-label">触发目标:</span>
                  <span class="detail-value">{{ event.trigger.target || '全局' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">动作数量:</span>
                  <span class="detail-value">{{ event.actions.length }} 个</span>
                </div>
                <div v-if="event.condition" class="detail-row">
                  <span class="detail-label">触发条件:</span>
                  <span class="detail-value">{{ event.condition }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧流程图 -->
      <div class="flow-chart-panel">
        <div class="panel-header">
          <h3>交互流程图</h3>
          <p>可视化展示交互事件的执行流程</p>
          <el-button size="small" @click="refreshFlowChart">
            刷新流程图
          </el-button>
        </div>

        <div class="flow-chart-container">
          <div v-if="interactionData.events.length === 0" class="empty-chart">
            <el-empty description="暂无交互流程" />
          </div>

          <div v-else class="flow-chart">
            <div class="chart-canvas">
              <div
                v-for="event in interactionData.events"
                :key="event.id"
                class="flow-event-node"
                :class="{ disabled: !event.enabled }"
              >
                <div class="node-header">
                  <span class="node-title">{{ event.name }}</span>
                  <el-tag :type="getEventTypeTag(event.trigger.type)" size="small">
                    {{ getEventTypeLabel(event.trigger.type) }}
                  </el-tag>
                </div>
                
                <div class="node-content">
                  <div class="trigger-info">
                    <span class="info-label">触发:</span>
                    <span class="info-value">{{ event.trigger.event }}</span>
                  </div>
                  
                  <div class="actions-list">
                    <div
                      v-for="action in event.actions"
                      :key="action.id"
                      class="action-item"
                    >
                      <span class="action-type">{{ getActionTypeLabel(action.type) }}</span>
                      <span class="action-target">{{ action.target || '默认' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 事件配置对话框 -->
    <el-dialog
      v-model="showEventDialog"
      :title="isEditMode ? '编辑交互事件' : '添加交互事件'"
      width="800px"
    >
      <div v-if="editingEvent" class="event-config-form">
        <el-form :model="editingEvent" label-width="120px">
          <el-form-item label="事件名称" required>
            <el-input v-model="editingEvent.name" placeholder="请输入事件名称" />
          </el-form-item>

          <el-form-item label="触发类型" required>
            <el-select v-model="editingEvent.trigger.type" style="width: 100%">
              <el-option
                v-for="type in eventTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="触发目标">
            <el-select
              v-model="editingEvent.trigger.target"
              placeholder="选择触发目标组件"
              style="width: 100%"
              clearable
            >
              <el-option
                v-for="component in layoutComponents"
                :key="component.id"
                :label="component.name"
                :value="component.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="具体事件">
            <el-input
              v-model="editingEvent.trigger.event"
              placeholder="如：click、change、submit等"
            />
          </el-form-item>

          <el-form-item label="触发条件">
            <el-input
              v-model="editingEvent.condition"
              type="textarea"
              placeholder="JavaScript表达式，如：data.status === 'active'"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="执行动作">
            <div class="actions-config">
              <div
                v-for="(action, index) in editingEvent.actions"
                :key="action.id"
                class="action-config-item"
              >
                <div class="action-header">
                  <span class="action-index">{{ index + 1 }}</span>
                  <el-select v-model="action.type" style="width: 150px">
                    <el-option
                      v-for="type in actionTypes"
                      :key="type.value"
                      :label="type.label"
                      :value="type.value"
                    />
                  </el-select>
                  <el-input
                    v-model="action.target"
                    placeholder="目标对象"
                    style="width: 150px"
                  />
                  <el-button size="small" type="danger" @click="removeAction(index)">
                    删除
                  </el-button>
                </div>
                
                <div class="action-params">
                  <el-input
                    v-model="action.params.value"
                    type="textarea"
                    placeholder="动作参数 (JSON格式)"
                    :rows="2"
                  />
                </div>
              </div>
              
              <el-button @click="addAction" style="width: 100%">
                添加动作
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="是否启用">
            <el-switch v-model="editingEvent.enabled" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showEventDialog = false">取消</el-button>
        <el-button type="primary" @click="saveEvent">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { PageInteractionConfig, InteractionEvent, InteractionAction, PageComponent } from '../../types/page-config'

const props = defineProps<{
  modelValue: PageInteractionConfig
  layoutComponents?: PageComponent[]
  apiList?: any[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: PageInteractionConfig]
  'validate': [stepIndex: number, isValid: boolean]
}>()

// 响应式数据
const selectedEvent = ref<InteractionEvent | null>(null)
const editingEvent = ref<InteractionEvent | null>(null)
const showEventDialog = ref(false)
const isEditMode = ref(false)

// 交互配置数据
const interactionData = reactive<PageInteractionConfig>({ ...props.modelValue })

// 事件类型选项
const eventTypes = [
  { value: 'click', label: '点击事件' },
  { value: 'hover', label: '悬停事件' },
  { value: 'change', label: '数据变化' },
  { value: 'load', label: '页面加载' },
  { value: 'submit', label: '表单提交' },
  { value: 'custom', label: '自定义事件' }
]

// 动作类型选项
const actionTypes = [
  { value: 'navigate', label: '页面跳转' },
  { value: 'refresh', label: '刷新页面' },
  { value: 'show', label: '显示元素' },
  { value: 'hide', label: '隐藏元素' },
  { value: 'api-call', label: 'API调用' },
  { value: 'message', label: '显示消息' },
  { value: 'save', label: '保存数据' },
  { value: 'validate', label: '数据验证' }
]

// 监听数据变化
watch(interactionData, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

watch(() => props.modelValue, (newVal) => {
  Object.assign(interactionData, newVal)
}, { deep: true })

// 添加事件
const addEvent = () => {
  editingEvent.value = {
    id: `event_${Date.now()}`,
    name: '',
    trigger: {
      type: 'click',
      target: '',
      event: 'click',
      config: {}
    },
    condition: '',
    actions: [],
    enabled: true
  }
  isEditMode.value = false
  showEventDialog.value = true
}

// 编辑事件
const editEvent = (event: InteractionEvent) => {
  editingEvent.value = { ...event }
  isEditMode.value = true
  showEventDialog.value = true
}

// 选择事件
const selectEvent = (event: InteractionEvent) => {
  selectedEvent.value = event
}

// 删除事件
const removeEvent = (index: number) => {
  interactionData.events.splice(index, 1)
  ElMessage.success('事件删除成功')
}

// 保存事件
const saveEvent = () => {
  if (!editingEvent.value) return

  if (!editingEvent.value.name) {
    ElMessage.warning('请输入事件名称')
    return
  }

  if (isEditMode.value) {
    const index = interactionData.events.findIndex(e => e.id === editingEvent.value!.id)
    if (index !== -1) {
      interactionData.events[index] = { ...editingEvent.value }
    }
  } else {
    interactionData.events.push({ ...editingEvent.value })
  }

  showEventDialog.value = false
  ElMessage.success('事件保存成功')
}

// 添加动作
const addAction = () => {
  if (!editingEvent.value) return

  const newAction: InteractionAction = {
    id: `action_${Date.now()}`,
    type: 'message',
    target: '',
    params: { value: '' },
    delay: 0
  }

  editingEvent.value.actions.push(newAction)
}

// 删除动作
const removeAction = (index: number) => {
  if (editingEvent.value) {
    editingEvent.value.actions.splice(index, 1)
  }
}

// 刷新流程图
const refreshFlowChart = () => {
  ElMessage.info('流程图已刷新')
}

// 获取事件类型标签
const getEventTypeTag = (type: string) => {
  const tagMap: Record<string, string> = {
    click: 'primary',
    hover: 'success',
    change: 'warning',
    load: 'info',
    submit: 'danger',
    custom: 'info'
  }
  return tagMap[type] || 'info'
}

// 获取事件类型标签文本
const getEventTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    click: '点击',
    hover: '悬停',
    change: '变化',
    load: '加载',
    submit: '提交',
    custom: '自定义'
  }
  return labelMap[type] || type
}

// 获取动作类型标签文本
const getActionTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    navigate: '跳转',
    refresh: '刷新',
    show: '显示',
    hide: '隐藏',
    'api-call': 'API',
    message: '消息',
    save: '保存',
    validate: '验证'
  }
  return labelMap[type] || type
}

// 验证方法
const validate = async () => {
  // 简单验证：可以没有交互事件
  const isValid = true
  emit('validate', 3, isValid)
  return isValid
}

defineExpose({
  validate
})
</script>

<style lang="scss" scoped>
.page-interaction-config {
  .config-container {
    display: flex;
    gap: 24px;
    height: 600px;
  }

  .event-configuration {
    width: 400px;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 16px;
    overflow-y: auto;

    .config-header {
      margin-bottom: 20px;

      h3 {
        margin: 0 0 5px 0;
        font-size: 16px;
        font-weight: 600;
      }

      p {
        margin: 0 0 12px 0;
        font-size: 12px;
        color: #909399;
      }
    }

    .event-items {
      .event-item {
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        margin-bottom: 12px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: #409eff;
        }

        &.active {
          border-color: #409eff;
          background-color: #f0f9ff;
        }

        .event-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .event-info {
            display: flex;
            align-items: center;
            gap: 8px;

            .event-name {
              font-weight: 500;
            }
          }
        }

        .event-details {
          .detail-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            font-size: 12px;

            .detail-label {
              color: #909399;
            }

            .detail-value {
              color: #606266;
            }
          }
        }
      }
    }

    .empty-state {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
    }
  }

  .flow-chart-panel {
    flex: 1;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 16px;
    overflow-y: auto;

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }

    .flow-chart-container {
      height: calc(100% - 60px);

      .empty-chart {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
      }

      .flow-chart {
        height: 100%;
        overflow: auto;

        .chart-canvas {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 16px;
          background-color: #f8f9fa;
          border-radius: 4px;
          min-height: 100%;

          .flow-event-node {
            background-color: #fff;
            border: 1px solid #e4e7ed;
            border-radius: 4px;
            padding: 12px;

            &.disabled {
              opacity: 0.6;
              background-color: #f5f5f5;
            }

            .node-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 8px;

              .node-title {
                font-weight: 500;
              }
            }

            .node-content {
              .trigger-info {
                display: flex;
                gap: 8px;
                margin-bottom: 8px;
                font-size: 12px;

                .info-label {
                  color: #909399;
                }

                .info-value {
                  color: #606266;
                }
              }

              .actions-list {
                .action-item {
                  display: flex;
                  justify-content: space-between;
                  padding: 4px 8px;
                  background-color: #f0f9ff;
                  border-radius: 2px;
                  margin-bottom: 4px;
                  font-size: 12px;

                  .action-type {
                    font-weight: 500;
                    color: #409eff;
                  }

                  .action-target {
                    color: #909399;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

.event-config-form {
  max-height: 500px;
  overflow-y: auto;

  .actions-config {
    .action-config-item {
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      padding: 12px;
      margin-bottom: 12px;

      .action-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .action-index {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          background-color: #409eff;
          color: white;
          border-radius: 50%;
          font-size: 12px;
          font-weight: 500;
        }
      }

      .action-params {
        margin-top: 8px;
      }
    }
  }
}
</style>