<template>
  <div class="workflow-designer">
    <!-- 工具栏 -->
    <div class="designer-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="saveWorkflow">
          <el-icon><Document /></el-icon>
          保存
        </el-button>
        <el-button @click="loadWorkflow">
          <el-icon><FolderOpened /></el-icon>
          加载
        </el-button>
        <el-button @click="clearCanvas">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
          <el-button @click="loadTestWorkflow">
            <el-icon><Upload /></el-icon>
            加载测试
          </el-button>
      </div>
      
      <div class="toolbar-center">
        <el-button-group>
          <el-button 
            type="success" 
            @click="executeWorkflow"
            :disabled="isExecuting"
            :loading="isExecuting"
          >
            <el-icon><VideoPlay /></el-icon>
            {{ isExecuting ? '执行中...' : '执行' }}
          </el-button>
          <el-button 
            type="danger" 
            @click="stopWorkflow"
            :disabled="!isExecuting"
          >
            <el-icon><VideoPause /></el-icon>
            停止
          </el-button>
          <el-button @click="debugWorkflow" :disabled="isExecuting">
            <el-icon><Tools /></el-icon>
            调试
          </el-button>
          <el-button @click="showProgress = !showProgress">
            <el-icon><DataAnalysis /></el-icon>
            进度
          </el-button>
        </el-button-group>
        
        <!-- 执行状态显示 -->
        <div v-if="workflowState" class="execution-status">
          <span class="status-text">
            状态: {{ getStatusText(workflowState.status) }}
          </span>
          <span v-if="workflowState.startTime" class="execution-time">
            耗时: {{ getExecutionTime(workflowState) }}ms
          </span>
        </div>
      </div>
      
      <div class="toolbar-right">
        <el-select 
          v-model="selectedSystem" 
          placeholder="选择系统"
          style="width: 150px; margin-right: 10px;"
          @change="handleSystemSelect"
        >
          <el-option
            v-for="system in systemOptions"
            :key="system.value"
            :label="system.label"
            :value="system.value"
          />
        </el-select>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="designer-content">
      <!-- 节点面板 -->
      <div class="node-panel">
        <div class="panel-header">
          <h3>节点库</h3>
          <el-input
            v-model="nodeSearchKeyword"
            placeholder="搜索节点..."
            size="small"
            clearable
            style="margin-top: 8px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="node-categories">
          <div 
            v-for="category in filteredNodeCategories" 
            :key="category.name"
            class="node-category"
          >
            <div class="category-header">
              <h4>{{ category.title }}
                <el-tooltip :content="category.description" placement="right">
                  <el-icon class="category-info"><InfoFilled /></el-icon>
                </el-tooltip>
              </h4>
            </div>
            <div class="node-list">
              <el-tooltip
                v-for="node in category.nodes"
                :key="node.type"
                :content="node.description"
                placement="right"
                :show-after="500"
              >
                <div
                  class="node-item"
                  draggable="true"
                  @dragstart="onDragStart($event, node)"
                  :style="{ borderLeftColor: node.color }"
                >
                  <div class="node-content">
                    <el-icon class="node-icon" :style="{ color: node.color }">
                      <component :is="node.icon" />
                    </el-icon>
                    <span class="node-label">{{ node.label }}</span>
                  </div>
                  <div class="node-indicator" :style="{ backgroundColor: node.color }"></div>
                </div>
              </el-tooltip>
            </div>
          </div>
        </div>
        
        <div class="panel-tips">
          <el-alert
            title="操作提示"
            type="info"
            :closable="false"
            show-icon
            size="small"
          >
            <template #default>
              <ul>
                <li>拖拽节点到画布创建</li>
                <li>双击节点快速添加</li>
                <li>右键节点查看详情</li>
              </ul>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 画布区域 -->
      <div class="canvas-container">
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          @dragover="onDragOver"
          @drop="onDrop"
          @node-click="onNodeClick"
          @edge-click="onEdgeClick"
          @connect="onConnect"
          :snap-to-grid="true"
          :snap-grid="[15, 15]"
          class="vue-flow-container"
        >
          <Background />
          <Controls />
          <MiniMap />
          
          <!-- 数据流动画 -->
          <DataFlowAnimation 
            ref="dataFlowRef"
            :flows="[]"
            :edges="edges"
          />
          
          <!-- 自定义节点模板 -->
          <template #node-start="nodeProps">
            <StartNode v-bind="nodeProps" />
          </template>
          
          <template #node-end="nodeProps">
            <EndNode v-bind="nodeProps" />
          </template>
          
          <template #node-api-call="nodeProps">
            <ApiCallNode v-bind="nodeProps" />
          </template>
          
          <template #node-data-transform="nodeProps">
            <DataTransformNode v-bind="nodeProps" />
          </template>
          
          <template #node-condition="nodeProps">
            <ConditionNode v-bind="nodeProps" />
          </template>
          
          <template #node-parallel="nodeProps">
            <ParallelNode v-bind="nodeProps" />
          </template>
        </VueFlow>
      </div>


    </div>
    
    <!-- 执行进度面板 -->
    <ExecutionProgress
      :visible="showProgress"
      :node-states="nodeStates"
      :nodes="nodes"
      @close="showProgress = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Document, 
  VideoPlay, 
  VideoPause,
  RefreshLeft,
  FullScreen,
  Loading,
  Close,
  Select,
  Tools,
  FolderOpened,
  Delete,
  DataAnalysis,
  Search,
  InfoFilled,
  Connection,
  Coin,
  Grid,
  RefreshRight,
  Timer,
  Message,
  Link,
  Warning,
  Check,
  DataBoard,
  TrendCharts,
  Upload
} from '@element-plus/icons-vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

// 导入自定义节点组件
import StartNode from './components/nodes/StartNode.vue'
import EndNode from './components/nodes/EndNode.vue'
import ApiCallNode from './components/nodes/ApiCallNode.vue'
import DataFlowAnimation from './components/DataFlowAnimation.vue'
import ExecutionProgress from './components/ExecutionProgress.vue'
import DataTransformNode from './components/nodes/DataTransformNode.vue'
import ConditionNode from './components/nodes/ConditionNode.vue'
import ParallelNode from './components/nodes/ParallelNode.vue'

// 导入执行引擎
import { WorkflowExecutionEngine, ExecutionStatus } from './utils/executionEngine'

// 导入工具函数
// import { isValidConnection } from './utils/nodeUtils' // 已移除，使用简化的验证逻辑

// 导入API
import { unifiedSystemApi, unifiedModuleApi, unifiedApiManagementApi } from '@/api/unified-api'

// 响应式数据
const elements = ref<any[]>([])
const nodes = ref<any[]>([])
const edges = ref<any[]>([])
const selectedNode = ref<any>(null)
const selectedEdge = ref<any>(null)
const selectedSystem = ref<string>('')
const nodeSearchKeyword = ref<string>('')

// 执行引擎相关
const executionEngine = ref<WorkflowExecutionEngine | null>(null)
const isExecuting = ref<boolean>(false)
const nodeStates = ref<Map<string, any>>(new Map())
const workflowState = ref<any>(null)
const dataFlowRef = ref<any>(null)
const showProgress = ref<boolean>(false)

// API数据相关
const systemOptions = ref<any[]>([])
const moduleOptions = ref<any[]>([])
const apiOptions = ref<any[]>([])

const loadingStates = ref({
  systems: false,
  modules: false,
  apis: false
})

// 节点分类
const nodeCategories = ref([
  {
    name: 'basic',
    title: '基础节点',
    description: '工作流的起始和结束节点',
    nodes: [
      { 
        type: 'start', 
        label: '开始', 
        icon: 'VideoPlay',
        description: '工作流的起始点，定义输入参数和触发条件',
        color: '#67C23A'
      },
      { 
        type: 'end', 
        label: '结束', 
        icon: 'VideoPause',
        description: '工作流的结束点，定义输出结果和清理操作',
        color: '#F56C6C'
      }
    ]
  },
  {
    name: 'api',
    title: 'API节点',
    description: '用于API调用和数据处理的节点',
    nodes: [
      { 
        type: 'api-call', 
        label: 'API调用', 
        icon: 'Connection',
        description: 'HTTP API调用，支持GET/POST/PUT/DELETE等方法',
        color: '#409EFF'
      },
      { 
        type: 'data-transform', 
        label: '数据转换', 
        icon: 'RefreshLeft',
        description: '数据格式转换、字段映射和数据清洗',
        color: '#E6A23C'
      },
      { 
        type: 'database', 
        label: '数据库操作', 
        icon: 'Coin',
        description: '数据库查询、插入、更新和删除操作',
        color: '#909399'
      },
      { 
        type: 'file-operation', 
        label: '文件操作', 
        icon: 'Document',
        description: '文件读取、写入、上传和下载操作',
        color: '#67C23A'
      }
    ]
  },
  {
    name: 'control',
    title: '控制节点',
    description: '用于流程控制和逻辑判断的节点',
    nodes: [
      { 
        type: 'condition', 
        label: '条件分支', 
        icon: 'Select',
        description: '基于条件表达式进行分支判断',
        color: '#E6A23C'
      },
      { 
        type: 'parallel', 
        label: '并行执行', 
        icon: 'Grid',
        description: '多个任务并行执行，提高处理效率',
        color: '#409EFF'
      },
      { 
        type: 'loop', 
        label: '循环执行', 
        icon: 'RefreshRight',
        description: '重复执行指定的操作，支持条件循环',
        color: '#F56C6C'
      },
      { 
        type: 'delay', 
        label: '延时等待', 
        icon: 'Timer',
        description: '延时等待指定时间后继续执行',
        color: '#909399'
      }
    ]
  },
  {
    name: 'notification',
    title: '通知节点',
    description: '用于消息通知和告警的节点',
    nodes: [
      { 
        type: 'email', 
        label: '邮件通知', 
        icon: 'Message',
        description: '发送邮件通知，支持HTML格式和附件',
        color: '#67C23A'
      },
      { 
        type: 'webhook', 
        label: 'Webhook', 
        icon: 'Link',
        description: '发送Webhook通知到指定URL',
        color: '#409EFF'
      },
      { 
        type: 'alert', 
        label: '告警通知', 
        icon: 'Warning',
        description: '系统告警通知，支持多种告警级别',
        color: '#F56C6C'
      }
    ]
  },
  {
    name: 'testing',
    title: '测试节点',
    description: '用于自动化测试的专用节点',
    nodes: [
      { 
        type: 'assertion', 
        label: '断言验证', 
        icon: 'Check',
        description: '验证数据是否符合预期条件',
        color: '#67C23A'
      },
      { 
        type: 'mock-data', 
        label: '模拟数据', 
        icon: 'DataBoard',
        description: '生成测试用的模拟数据',
        color: '#E6A23C'
      },
      { 
        type: 'performance', 
        label: '性能测试', 
        icon: 'TrendCharts',
        description: '执行性能测试并收集指标',
        color: '#409EFF'
      }
    ]
  }
])

// 过滤节点分类
const filteredNodeCategories = computed(() => {
  if (!nodeSearchKeyword.value) {
    return nodeCategories.value
  }
  
  const keyword = nodeSearchKeyword.value.toLowerCase()
  return nodeCategories.value.map(category => ({
    ...category,
    nodes: category.nodes.filter(node => 
      node.label.toLowerCase().includes(keyword) ||
      node.description.toLowerCase().includes(keyword) ||
      node.type.toLowerCase().includes(keyword)
    )
  })).filter(category => category.nodes.length > 0)
})

// 加载系统列表
const loadSystems = async () => {
  try {
    loadingStates.value.systems = true
    const response = await unifiedSystemApi.getEnabledList()
    if (response.success && response.data) {
      systemOptions.value = response.data.map((system: any) => ({
        label: system.name,
        value: system.id,
        ...system
      }))
    }
  } catch (error) {
    console.error('加载系统列表失败:', error)
    ElMessage.error('加载系统列表失败')
  } finally {
    loadingStates.value.systems = false
  }
}

// 加载模块列表
const loadModules = async (systemId: string) => {
  if (!systemId) {
    moduleOptions.value = []
    return
  }
  
  try {
    loadingStates.value.modules = true
    const response = await unifiedModuleApi.getEnabledBySystem(systemId)
    if (response.success && response.data) {
      moduleOptions.value = response.data.map((module: any) => ({
        label: module.name,
        value: module.id,
        ...module
      }))
    }
  } catch (error) {
    console.error('加载模块列表失败:', error)
    ElMessage.error('加载模块列表失败')
  } finally {
    loadingStates.value.modules = false
  }
}

// 加载API列表
const loadApis = async (systemId: string, moduleId: string) => {
  if (!systemId || !moduleId) {
    apiOptions.value = []
    return
  }
  
  try {
    loadingStates.value.apis = true
    // 使用统一API获取接口列表
    const response = await unifiedApiManagementApi.getApis({
      system_id: systemId,
      module_id: moduleId
    })
    if (response.success && response.data) {
      apiOptions.value = response.data.map((api: any) => ({
        label: `${api.name} (${api.method})`,
        value: api.id,
        ...api
      }))
    }
  } catch (error) {
    console.error('加载API列表失败:', error)
    ElMessage.error('加载API列表失败')
  } finally {
    loadingStates.value.apis = false
  }
}








// 方法定义
const saveWorkflow = () => {
  ElMessage.info('保存工作流功能待实现')
}

const loadWorkflow = () => {
  ElMessage.info('加载工作流功能待实现')
}

const clearCanvas = () => {
  nodes.value = []
  edges.value = []
  selectedNode.value = null
  selectedEdge.value = null
  ElMessage.success('画布已清空')
}

const executeWorkflow = async () => {
  if (nodes.value.length === 0) {
    ElMessage.warning('请先添加节点')
    return
  }

  if (isExecuting.value) {
    ElMessage.warning('工作流正在执行中')
    return
  }

  try {
    isExecuting.value = true
    showProgress.value = true
    
    // 清空之前的状态
    nodeStates.value.clear()
    
    // 创建执行引擎
    executionEngine.value = new WorkflowExecutionEngine(
      nodes.value,
      edges.value,
      onNodeStatusChange,
      onWorkflowStatusChange
    )
    
    // 开始执行
    await executionEngine.value.execute()
    
    ElMessage.success('工作流执行完成')
    
  } catch (error) {
    ElMessage.error(`执行失败: ${error}`)
  } finally {
    isExecuting.value = false
  }
}

const debugWorkflow = () => {
  if (nodes.value.length === 0) {
    ElMessage.warning('请先添加节点')
    return
  }
  
  ElMessage.info('调试模式启动')
  // TODO: 实现调试功能
}

// 节点状态变化回调
const onNodeStatusChange = (nodeId: string, status: any) => {
  nodeStates.value.set(nodeId, status)
  
  // 更新节点的视觉状态
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    if (!node.data.style) {
      node.data.style = {}
    }
    
    // 根据状态设置节点样式
    switch (status.status) {
      case ExecutionStatus.RUNNING:
        node.data.style.border = '2px solid #409eff'
        node.data.style.boxShadow = '0 0 10px rgba(64, 158, 255, 0.5)'
        break
      case ExecutionStatus.SUCCESS:
        node.data.style.border = '2px solid #67c23a'
        node.data.style.boxShadow = '0 0 10px rgba(103, 194, 58, 0.5)'
        
        // 触发数据流动画到下一个节点
        if (dataFlowRef.value) {
          const outgoingEdges = edges.value.filter(edge => edge.source === nodeId)
          outgoingEdges.forEach(edge => {
            dataFlowRef.value.startFlow(nodeId, edge.target, status.output)
          })
        }
        break
      case ExecutionStatus.ERROR:
        node.data.style.border = '2px solid #f56c6c'
        node.data.style.boxShadow = '0 0 10px rgba(245, 108, 108, 0.5)'
        break
      default:
        node.data.style.border = '2px solid #e4e7ed'
        node.data.style.boxShadow = 'none'
    }
  }
}

// 工作流状态变化回调
const onWorkflowStatusChange = (state: any) => {
  workflowState.value = state
  console.log('工作流状态变化:', state)
}

// 停止工作流执行
const stopWorkflow = () => {
  if (executionEngine.value) {
    // TODO: 实现停止逻辑
    isExecuting.value = false
    ElMessage.info('工作流已停止')
  }
}

// 获取状态文本
const getStatusText = (status: any) => {
  switch (status) {
    case ExecutionStatus.PENDING:
      return '待执行'
    case ExecutionStatus.RUNNING:
      return '执行中'
    case ExecutionStatus.SUCCESS:
      return '成功'
    case ExecutionStatus.ERROR:
      return '失败'
    default:
      return '未知'
  }
}

// 获取执行时间
const getExecutionTime = (state: any) => {
  if (state.startTime) {
    const endTime = state.endTime || Date.now()
    return endTime - state.startTime
  }
  return 0
}

// 加载测试工作流
const loadTestWorkflow = () => {
  // 简单的测试工作流
  const testNodes = [
    {
      id: 'start-1',
      type: 'start',
      position: { x: 100, y: 100 },
      data: {
        label: '开始',
        description: '工作流开始节点'
      }
    },
    {
      id: 'api-1',
      type: 'api-call',
      position: { x: 300, y: 100 },
      data: {
        label: '获取数据',
        description: 'API调用节点',
        config: {
          url: 'https://jsonplaceholder.typicode.com/users/1',
          method: 'GET'
        }
      }
    },
    {
      id: 'transform-1',
      type: 'data-transform',
      position: { x: 500, y: 100 },
      data: {
        label: '数据转换',
        description: '提取用户信息',
        config: {
          script: 'return { name: input.name, email: input.email }'
        }
      }
    },
    {
      id: 'end-1',
      type: 'end',
      position: { x: 700, y: 100 },
      data: {
        label: '结束',
        description: '工作流结束节点'
      }
    }
  ]
  
  const testEdges = [
    {
      id: 'e1',
      source: 'start-1',
      target: 'api-1',
      sourceHandle: null,
      targetHandle: 'input',
      type: 'default',
      animated: true,
      style: { stroke: '#409eff', strokeWidth: 2 },
      markerEnd: {
        type: 'arrowclosed',
        width: 20,
        height: 20,
        color: '#409eff'
      }
    },
    {
      id: 'e2',
      source: 'api-1',
      target: 'transform-1',
      sourceHandle: 'output',
      targetHandle: 'input',
      type: 'default',
      animated: true,
      style: { stroke: '#409eff', strokeWidth: 2 },
      markerEnd: {
        type: 'arrowclosed',
        width: 20,
        height: 20,
        color: '#409eff'
      }
    },
    {
      id: 'e3',
      source: 'transform-1',
      target: 'end-1',
      sourceHandle: 'output',
      targetHandle: null,
      type: 'default',
      animated: true,
      style: { stroke: '#409eff', strokeWidth: 2 },
      markerEnd: {
        type: 'arrowclosed',
        width: 20,
        height: 20,
        color: '#409eff'
      }
    }
  ]
  
  nodes.value = testNodes
  edges.value = testEdges
  
  ElMessage.success('测试工作流已加载')
}

const handleSystemSelect = (value: string) => {
  selectedSystem.value = value
  ElMessage.info(`已选择系统: ${value}`)
}

// VueFlow 事件处理
const onDragStart = (event: DragEvent, nodeType: any) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/json', JSON.stringify(nodeType))
    event.dataTransfer.effectAllowed = 'move'
  }
}

const onDragOver = (event: DragEvent) => {
  event.preventDefault()
  event.dataTransfer!.dropEffect = 'move'
}

const onDrop = (event: DragEvent) => {
  event.preventDefault()
  
  if (event.dataTransfer) {
    const nodeType = JSON.parse(event.dataTransfer.getData('application/json'))
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    
    const newNode = {
      id: `${nodeType.type}_${Date.now()}`,
      type: nodeType.type,
      position: {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      },
      data: {
        label: nodeType.label,
        config: {}
      }
    }
    
    nodes.value.push(newNode)
    ElMessage.success(`已添加${nodeType.label}节点`)
  }
}

const onNodeClick = (event: any) => {
  selectedNode.value = event.node
  selectedEdge.value = null
}

const onEdgeClick = (event: any) => {
  selectedEdge.value = event.edge
  selectedNode.value = null
}

// 连接处理
const onConnect = (params: any) => {
  // 查找源节点和目标节点
  const sourceNode = nodes.value.find(node => node.id === params.source)
  const targetNode = nodes.value.find(node => node.id === params.target)
  
  if (!sourceNode || !targetNode) {
    ElMessage.error('连接失败：找不到节点')
    return
  }
  
  // 简化的连接验证逻辑
  // 1. 不能连接到自己
  if (params.source === params.target) {
    ElMessage.error('连接失败：不能连接到自己')
    return
  }
  
  // 2. 检查是否已经存在相同的连接
  const existingConnection = edges.value.find(edge => 
    edge.source === params.source && 
    edge.target === params.target &&
    edge.sourceHandle === params.sourceHandle &&
    edge.targetHandle === params.targetHandle
  )
  
  if (existingConnection) {
    ElMessage.error('连接失败：连接已存在')
    return
  }
  
  // 3. 检查是否会形成循环（简化版本）
  if (wouldCreateCycle(params.source, params.target, edges.value)) {
    ElMessage.error('连接失败：不能形成循环连接')
    return
  }
  
  const newEdge = {
    id: `edge_${Date.now()}`,
    source: params.source,
    target: params.target,
    sourceHandle: params.sourceHandle || 'output',
    targetHandle: params.targetHandle || 'input',
    type: 'default',
    animated: true,
    style: { stroke: '#409eff', strokeWidth: 2 },
    markerEnd: {
      type: 'arrowclosed',
      width: 20,
      height: 20,
      color: '#409eff'
    }
  }
  
  edges.value.push(newEdge)
  ElMessage.success('节点连接成功')
}

// 简化的循环检测函数
const wouldCreateCycle = (fromNodeId: string, toNodeId: string, existingEdges: any[]): boolean => {
  const visited = new Set<string>()
  const stack = [toNodeId]

  while (stack.length > 0) {
    const currentNodeId = stack.pop()!
    
    if (currentNodeId === fromNodeId) {
      return true
    }

    if (visited.has(currentNodeId)) {
      continue
    }

    visited.add(currentNodeId)

    // 找到所有从当前节点出发的连接
    const outgoingConnections = existingEdges.filter(edge => edge.source === currentNodeId)
    for (const edge of outgoingConnections) {
      stack.push(edge.target)
    }
  }

  return false
}

// 删除连接
const onEdgeDelete = (edgeId: string) => {
  const index = edges.value.findIndex(edge => edge.id === edgeId)
  if (index > -1) {
    edges.value.splice(index, 1)
    ElMessage.success('连接已删除')
  }
}

// 处理系统选择变化
const onSystemChange = (systemId: string) => {
  if (selectedNode.value) {
    // 清空模块和API选择
    selectedNode.value.data.config.moduleId = ''
    selectedNode.value.data.config.apiId = ''
    selectedNode.value.data.config.method = ''
    
    // 清空选项
    moduleOptions.value = []
    apiOptions.value = []
    
    // 加载模块列表
    if (systemId) {
      loadModules(systemId)
    }
  }
}

// 处理模块选择变化
const onModuleChange = (moduleId: string) => {
  if (selectedNode.value) {
    // 清空API选择
    selectedNode.value.data.config.apiId = ''
    selectedNode.value.data.config.method = ''
    
    // 清空API选项
    apiOptions.value = []
    
    // 加载API列表
    if (moduleId && selectedNode.value.data.config.systemId) {
      loadApis(selectedNode.value.data.config.systemId, moduleId)
    }
  }
}

// 处理API选择变化
const onApiChange = (apiId: string) => {
  if (selectedNode.value && apiId) {
    // 根据选择的API设置请求方法
    const selectedApi = apiOptions.value.find(api => api.value === apiId)
    if (selectedApi) {
      selectedNode.value.data.config.method = selectedApi.method || 'GET'
      selectedNode.value.data.config.url = selectedApi.path || selectedApi.url || ''
      selectedNode.value.data.config.apiName = selectedApi.name || selectedApi.label || ''
      
      // 自动生成参数模板
      generateApiParameterTemplate(selectedApi)
    }
  }
}







// 验证JSON参数
const validateJsonParams = (event: any) => {
  const value = event.target.value
  if (value && value.trim()) {
    try {
      JSON.parse(value)
      ElMessage.success('JSON格式验证通过')
    } catch (error) {
      ElMessage.error('JSON格式错误，请检查语法')
    }
  }
}

// 验证JSON请求头
const validateJsonHeaders = (event: any) => {
  const value = event.target.value
  if (value && value.trim()) {
    try {
      JSON.parse(value)
      ElMessage.success('JSON格式验证通过')
    } catch (error) {
      ElMessage.error('JSON格式错误，请检查语法')
    }
  }
}

// 生成API参数模板
const generateApiParameterTemplate = (apiInfo: any) => {
  if (!selectedNode.value) return
  
  try {
    // 初始化参数配置
    const config = selectedNode.value.data.config
    
    // 设置请求头模板
    if (apiInfo.headers || apiInfo.auth_required) {
      config.headers = {
        'Content-Type': 'application/json',
        ...(apiInfo.auth_required && { 'Authorization': 'Bearer ${token}' }),
        ...(apiInfo.headers && typeof apiInfo.headers === 'object' ? apiInfo.headers : {})
      }
    }
    
    // 设置请求参数模板
    if (apiInfo.request_schema) {
      try {
        const requestSchema = typeof apiInfo.request_schema === 'string' 
          ? JSON.parse(apiInfo.request_schema) 
          : apiInfo.request_schema
        config.requestParams = generateParametersFromSchema(requestSchema)
      } catch (e) {
        console.warn('解析请求参数模板失败:', e)
      }
    } else if (apiInfo.example_request) {
      try {
        const exampleRequest = typeof apiInfo.example_request === 'string'
          ? JSON.parse(apiInfo.example_request)
          : apiInfo.example_request
        config.requestParams = exampleRequest
      } catch (e) {
        console.warn('解析示例请求失败:', e)
      }
    }
    
    // 设置响应模板（用于参考）
    if (apiInfo.response_schema) {
      try {
        const responseSchema = typeof apiInfo.response_schema === 'string'
          ? JSON.parse(apiInfo.response_schema)
          : apiInfo.response_schema
        config.responseTemplate = responseSchema
      } catch (e) {
        console.warn('解析响应模板失败:', e)
      }
    } else if (apiInfo.example_response) {
      try {
        const exampleResponse = typeof apiInfo.example_response === 'string'
          ? JSON.parse(apiInfo.example_response)
          : apiInfo.example_response
        config.responseTemplate = exampleResponse
      } catch (e) {
        console.warn('解析示例响应失败:', e)
      }
    }
    
    // 设置其他配置
    config.timeout = apiInfo.timeout || 30000
    config.rateLimit = apiInfo.rate_limit || 1000
    config.description = apiInfo.description || ''
    
    ElMessage.success('API参数模板已自动生成')
  } catch (error) {
    console.error('生成API参数模板失败:', error)
    ElMessage.warning('生成API参数模板失败，请手动配置')
  }
}

// 从Schema生成参数模板
const generateParametersFromSchema = (schema: any): any => {
  if (!schema || typeof schema !== 'object') return {}
  
  const result: any = {}
  
  if (schema.properties) {
    // JSON Schema格式
    for (const [key, prop] of Object.entries(schema.properties)) {
      const property = prop as any
      result[key] = generateValueFromProperty(property)
    }
  } else {
    // 简单对象格式
    for (const [key, value] of Object.entries(schema)) {
      result[key] = generateValueFromProperty({ type: typeof value, example: value })
    }
  }
  
  return result
}

// 根据属性类型生成默认值
const generateValueFromProperty = (property: any): any => {
  if (property.example !== undefined) {
    return property.example
  }
  
  switch (property.type) {
    case 'string':
      return property.enum ? property.enum[0] : ''
    case 'number':
    case 'integer':
      return property.minimum || 0
    case 'boolean':
      return false
    case 'array':
      return []
    case 'object':
      return property.properties ? generateParametersFromSchema(property) : {}
    default:
      return ''
  }
}

// 处理节点更新
const handleUpdateNode = (nodeId: string, updates: any) => {
  const nodeIndex = nodes.value.findIndex(node => node.id === nodeId)
  if (nodeIndex !== -1) {
    const node = nodes.value[nodeIndex]
    // 更新节点数据
    nodes.value[nodeIndex] = {
      ...node,
      data: {
        ...node.data,
        ...updates
      }
    }
    
    // 如果选中的节点被更新，同步更新selectedNode
    if (selectedNode.value && selectedNode.value.id === nodeId) {
      selectedNode.value = nodes.value[nodeIndex]
    }
  }
}

// 生命周期
onMounted(() => {
  // 加载系统列表
  loadSystems()
  
  // 初始化示例节点
  nextTick(() => {
    nodes.value = [
      {
        id: 'start_1',
        type: 'start',
        position: { x: 100, y: 100 },
        data: { label: '开始节点' }
      },
      {
        id: 'api_1',
        type: 'api-call',
        position: { x: 300, y: 100 },
        data: { 
          label: 'API调用', 
          config: {
            systemId: '',
            moduleId: '',
            apiId: '',
            method: '',
            url: '',
            apiName: ''
          }
        }
      },
      {
        id: 'end_1',
        type: 'end',
        position: { x: 500, y: 100 },
        data: { label: '结束节点' }
      }
    ]
  })
})
</script>

<style scoped>
.workflow-designer {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.designer-toolbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.execution-status {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 16px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
}

.status-text {
  color: #606266;
  font-weight: 500;
}

.execution-time {
  color: #909399;
}

.designer-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.node-panel {
  width: 200px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.node-categories {
  padding: 10px;
}

.node-category {
  margin-bottom: 20px;
}

.category-header {
  margin-bottom: 8px;
}

.category-header h4 {
  margin: 0;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.category-info {
  color: #909399;
  cursor: help;
  font-size: 12px;
}

.category-info:hover {
  color: #409eff;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 6px;
  align-items: flex-start;
}

.node-item {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid transparent;
  cursor: grab;
  transition: all 0.2s;
  width: fit-content;
  min-width: 100px;
  max-width: 180px;
  height: auto;
  min-height: 40px;
  margin: 0;
  align-self: flex-start;
}

.node-item:hover {
  background: #e6f7ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.node-item:active {
  cursor: grabbing;
}

.node-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  text-align: left;
  flex: 1;
  width: 100%;
  gap: 8px;
}

.node-content .node-icon {
  font-size: 16px;
  color: #409eff;
  flex-shrink: 0;
}

.node-content .node-label {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  line-height: 1.2;
  word-wrap: break-word;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-left: 8px;
}

.panel-tips {
  margin-top: 16px;
}

.panel-tips ul {
  margin: 0;
  padding-left: 16px;
}

.panel-tips li {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  line-height: 1.4;
}

.canvas-container {
  flex: 1;
  position: relative;
  background: #fafafa;
}

.vue-flow-container {
  width: 100%;
  height: 100%;
}



.config-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}

.config-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* VueFlow 样式覆盖 */
:deep(.vue-flow__background) {
  background-color: #fafafa;
}

/* 箭头标记样式 */
:deep(.vue-flow__edge-path) {
  stroke: #409eff;
  stroke-width: 2;
}

:deep(.vue-flow__arrowhead) {
  fill: #409eff;
}

:deep(.vue-flow__edge.selected .vue-flow__edge-path) {
  stroke: #67c23a;
}

:deep(.vue-flow__edge.selected .vue-flow__arrowhead) {
  fill: #67c23a;
}

:deep(.vue-flow__node) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.vue-flow__edge) {
  stroke-width: 2px;
}

:deep(.vue-flow__edge.selected) {
  stroke: #409eff;
}

:deep(.vue-flow__controls) {
  bottom: 20px;
  left: 20px;
}

:deep(.vue-flow__minimap) {
  bottom: 20px;
  right: 20px;
}
</style>