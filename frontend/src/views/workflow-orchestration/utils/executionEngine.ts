import { ElMessage } from 'element-plus'

// 执行状态枚举
export enum ExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  SUCCESS = 'success',
  ERROR = 'error',
  CANCELLED = 'cancelled'
}

// 节点执行状态
export interface NodeExecutionState {
  id: string
  status: ExecutionStatus
  startTime?: number
  endTime?: number
  error?: string
  result?: any
  progress?: number
}

// 工作流执行状态
export interface WorkflowExecutionState {
  id: string
  status: ExecutionStatus
  startTime?: number
  endTime?: number
  nodes: Map<string, NodeExecutionState>
  currentNodes: Set<string>
  completedNodes: Set<string>
  failedNodes: Set<string>
}

// 执行引擎类
export class WorkflowExecutionEngine {
  private nodes: any[]
  private edges: any[]
  private executionState: WorkflowExecutionState
  private onNodeStatusChange?: (nodeId: string, status: NodeExecutionState) => void
  private onWorkflowStatusChange?: (status: WorkflowExecutionState) => void

  constructor(
    nodes: any[], 
    edges: any[],
    onNodeStatusChange?: (nodeId: string, status: NodeExecutionState) => void,
    onWorkflowStatusChange?: (status: WorkflowExecutionState) => void
  ) {
    this.nodes = nodes
    this.edges = edges
    this.onNodeStatusChange = onNodeStatusChange
    this.onWorkflowStatusChange = onWorkflowStatusChange
    
    this.executionState = {
      id: `execution_${Date.now()}`,
      status: ExecutionStatus.PENDING,
      nodes: new Map(),
      currentNodes: new Set(),
      completedNodes: new Set(),
      failedNodes: new Set()
    }

    // 初始化节点状态
    this.initializeNodeStates()
  }

  // 初始化节点状态
  private initializeNodeStates() {
    this.nodes.forEach(node => {
      this.executionState.nodes.set(node.id, {
        id: node.id,
        status: ExecutionStatus.PENDING
      })
    })
  }

  // 开始执行工作流
  async execute(): Promise<void> {
    try {
      this.executionState.status = ExecutionStatus.RUNNING
      this.executionState.startTime = Date.now()
      this.notifyWorkflowStatusChange()

      ElMessage.info('开始执行工作流')

      // 找到起始节点
      const startNodes = this.findStartNodes()
      if (startNodes.length === 0) {
        throw new Error('未找到起始节点')
      }

      // 执行起始节点
      await this.executeNodes(startNodes)

      // 检查执行结果
      if (this.executionState.failedNodes.size > 0) {
        this.executionState.status = ExecutionStatus.ERROR
        ElMessage.error('工作流执行失败')
      } else {
        this.executionState.status = ExecutionStatus.SUCCESS
        ElMessage.success('工作流执行成功')
      }

      this.executionState.endTime = Date.now()
      this.notifyWorkflowStatusChange()

    } catch (error) {
      this.executionState.status = ExecutionStatus.ERROR
      this.executionState.endTime = Date.now()
      ElMessage.error(`工作流执行错误: ${error}`)
      this.notifyWorkflowStatusChange()
    }
  }

  // 找到起始节点
  private findStartNodes(): any[] {
    return this.nodes.filter(node => 
      node.type === 'start' || 
      !this.edges.some(edge => edge.target === node.id)
    )
  }

  // 执行节点列表
  private async executeNodes(nodes: any[]): Promise<void> {
    const promises = nodes.map(node => this.executeNode(node))
    await Promise.all(promises)
  }

  // 执行单个节点
  private async executeNode(node: any): Promise<void> {
    const nodeState = this.executionState.nodes.get(node.id)!
    
    try {
      // 更新节点状态为运行中
      nodeState.status = ExecutionStatus.RUNNING
      nodeState.startTime = Date.now()
      this.executionState.currentNodes.add(node.id)
      this.notifyNodeStatusChange(node.id, nodeState)

      // 根据节点类型执行不同逻辑
      await this.executeNodeByType(node)

      // 更新节点状态为成功
      nodeState.status = ExecutionStatus.SUCCESS
      nodeState.endTime = Date.now()
      this.executionState.currentNodes.delete(node.id)
      this.executionState.completedNodes.add(node.id)
      this.notifyNodeStatusChange(node.id, nodeState)

      // 执行后续节点
      await this.executeNextNodes(node.id)

    } catch (error) {
      // 更新节点状态为失败
      nodeState.status = ExecutionStatus.ERROR
      nodeState.error = String(error)
      nodeState.endTime = Date.now()
      this.executionState.currentNodes.delete(node.id)
      this.executionState.failedNodes.add(node.id)
      this.notifyNodeStatusChange(node.id, nodeState)
      
      throw error
    }
  }

  // 根据节点类型执行
  private async executeNodeByType(node: any): Promise<void> {
    switch (node.type) {
      case 'start':
        await this.executeStartNode(node)
        break
      case 'end':
        await this.executeEndNode(node)
        break
      case 'api-call':
        await this.executeApiCallNode(node)
        break
      case 'data-transform':
        await this.executeDataTransformNode(node)
        break
      case 'condition':
        await this.executeConditionNode(node)
        break
      case 'parallel':
        await this.executeParallelNode(node)
        break
      default:
        throw new Error(`未知的节点类型: ${node.type}`)
    }
  }

  // 执行开始节点
  private async executeStartNode(node: any): Promise<void> {
    // 模拟执行时间
    await this.delay(500)
    console.log(`执行开始节点: ${node.id}`)
  }

  // 执行结束节点
  private async executeEndNode(node: any): Promise<void> {
    // 模拟执行时间
    await this.delay(500)
    console.log(`执行结束节点: ${node.id}`)
  }

  // 执行API调用节点
  private async executeApiCallNode(node: any): Promise<void> {
    // 模拟API调用
    await this.delay(1000 + Math.random() * 2000)
    
    const config = node.data.config || {}
    console.log(`执行API调用节点: ${node.id}`, config)
    
    // 模拟API调用结果
    const nodeState = this.executionState.nodes.get(node.id)!
    nodeState.result = {
      status: 'success',
      data: { message: 'API调用成功', timestamp: Date.now() }
    }
  }

  // 执行数据转换节点
  private async executeDataTransformNode(node: any): Promise<void> {
    // 模拟数据转换
    await this.delay(800)
    
    const config = node.data.config || {}
    console.log(`执行数据转换节点: ${node.id}`, config)
    
    // 模拟转换结果
    const nodeState = this.executionState.nodes.get(node.id)!
    nodeState.result = {
      transformedData: { processed: true, timestamp: Date.now() }
    }
  }

  // 执行条件分支节点
  private async executeConditionNode(node: any): Promise<void> {
    // 模拟条件判断
    await this.delay(300)
    
    const config = node.data.config || {}
    console.log(`执行条件分支节点: ${node.id}`, config)
    
    // 模拟条件结果（随机true/false）
    const conditionResult = Math.random() > 0.5
    const nodeState = this.executionState.nodes.get(node.id)!
    nodeState.result = { conditionResult }
    
    // 根据条件结果执行不同的后续节点
    await this.executeConditionalNextNodes(node.id, conditionResult)
  }

  // 执行并行节点
  private async executeParallelNode(node: any): Promise<void> {
    // 模拟并行处理
    await this.delay(500)
    
    const config = node.data.config || {}
    const maxConcurrency = config.maxConcurrency || 3
    console.log(`执行并行节点: ${node.id}`, { maxConcurrency })
    
    // 获取所有后续节点
    const nextNodes = this.getNextNodes(node.id)
    
    // 并行执行后续节点（限制并发数）
    await this.executeNodesInParallel(nextNodes, maxConcurrency)
  }

  // 并行执行节点（限制并发数）
  private async executeNodesInParallel(nodes: any[], maxConcurrency: number): Promise<void> {
    const executing: Promise<void>[] = []
    
    for (const node of nodes) {
      // 如果达到最大并发数，等待一个完成
      if (executing.length >= maxConcurrency) {
        await Promise.race(executing)
        // 移除已完成的promise
        const completedIndex = executing.findIndex(p => p === Promise.resolve())
        if (completedIndex !== -1) {
          executing.splice(completedIndex, 1)
        }
      }
      
      // 添加新的执行任务
      const promise = this.executeNode(node)
      executing.push(promise)
    }
    
    // 等待所有任务完成
    await Promise.all(executing)
  }

  // 执行后续节点
  private async executeNextNodes(nodeId: string): Promise<void> {
    const nextNodes = this.getNextNodes(nodeId)
    
    if (nextNodes.length > 0) {
      // 检查所有前置节点是否都已完成
      const readyNodes = nextNodes.filter(node => this.areAllPredecessorsCompleted(node.id))
      
      if (readyNodes.length > 0) {
        await this.executeNodes(readyNodes)
      }
    }
  }

  // 执行条件分支的后续节点
  private async executeConditionalNextNodes(nodeId: string, conditionResult: boolean): Promise<void> {
    const outgoingEdges = this.edges.filter(edge => edge.source === nodeId)
    
    // 根据条件结果选择对应的边
    const targetEdges = outgoingEdges.filter(edge => {
      const sourceHandle = edge.sourceHandle
      return conditionResult ? 
        (sourceHandle === 'true' || sourceHandle === 'output') : 
        (sourceHandle === 'false' || sourceHandle === 'output')
    })
    
    const nextNodes = targetEdges.map(edge => 
      this.nodes.find(node => node.id === edge.target)
    ).filter(Boolean)
    
    if (nextNodes.length > 0) {
      await this.executeNodes(nextNodes)
    }
  }

  // 获取后续节点
  private getNextNodes(nodeId: string): any[] {
    const outgoingEdges = this.edges.filter(edge => edge.source === nodeId)
    return outgoingEdges.map(edge => 
      this.nodes.find(node => node.id === edge.target)
    ).filter(Boolean)
  }

  // 检查所有前置节点是否都已完成
  private areAllPredecessorsCompleted(nodeId: string): boolean {
    const incomingEdges = this.edges.filter(edge => edge.target === nodeId)
    return incomingEdges.every(edge => 
      this.executionState.completedNodes.has(edge.source)
    )
  }

  // 延迟函数
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // 通知节点状态变化
  private notifyNodeStatusChange(nodeId: string, status: NodeExecutionState) {
    if (this.onNodeStatusChange) {
      this.onNodeStatusChange(nodeId, status)
    }
  }

  // 通知工作流状态变化
  private notifyWorkflowStatusChange() {
    if (this.onWorkflowStatusChange) {
      this.onWorkflowStatusChange(this.executionState)
    }
  }

  // 停止执行
  stop(): void {
    this.executionState.status = ExecutionStatus.CANCELLED
    this.executionState.endTime = Date.now()
    this.notifyWorkflowStatusChange()
    ElMessage.warning('工作流执行已停止')
  }

  // 获取执行状态
  getExecutionState(): WorkflowExecutionState {
    return this.executionState
  }

  // 获取节点状态
  getNodeState(nodeId: string): NodeExecutionState | undefined {
    return this.executionState.nodes.get(nodeId)
  }
}