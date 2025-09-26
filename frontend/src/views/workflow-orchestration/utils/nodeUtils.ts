/**
 * 节点工具函数
 * 
 * 提供节点创建、转换、验证等工具函数
 */

import { 
  NodeType, 
  NodeStatus, 
  ConnectionType,
  WorkflowNode, 
  NodeConnection,
  NODE_TEMPLATES,
  type StartNode,
  type EndNode,
  type ApiCallNode,
  type DataTransformNode,
  type ConditionNode,
  type ParallelNode
} from '../types'

// 生成唯一ID
export function generateId(): string {
  return `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 生成连接ID
export function generateConnectionId(): string {
  return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 创建新节点
export function createNode(type: NodeType, position: { x: number; y: number }): WorkflowNode {
  const id = generateId()
  const now = new Date().toISOString()
  const template = NODE_TEMPLATES.find(t => t.type === type)
  
  if (!template) {
    throw new Error(`Unknown node type: ${type}`)
  }

  const baseNode = {
    id,
    name: template.name,
    description: template.description,
    position,
    status: NodeStatus.IDLE,
    inputs: template.inputs,
    outputs: template.outputs,
    createdAt: now,
    updatedAt: now
  }

  switch (type) {
    case NodeType.START:
      return {
        ...baseNode,
        type: NodeType.START,
        config: template.defaultConfig
      } as StartNode

    case NodeType.END:
      return {
        ...baseNode,
        type: NodeType.END,
        config: template.defaultConfig
      } as EndNode

    case NodeType.API_CALL:
      return {
        ...baseNode,
        type: NodeType.API_CALL,
        config: {
          systemId: '',
          moduleId: '',
          apiId: '',
          method: 'GET',
          url: '',
          headers: {},
          parameters: {},
          timeout: 30000,
          retryCount: 3,
          retryDelay: 1000,
          ...template.defaultConfig
        }
      } as ApiCallNode

    case NodeType.DATA_TRANSFORM:
      return {
        ...baseNode,
        type: NodeType.DATA_TRANSFORM,
        config: {
          transformType: 'MAPPING',
          mappingRules: [],
          ...template.defaultConfig
        }
      } as DataTransformNode

    case NodeType.CONDITION:
      return {
        ...baseNode,
        type: NodeType.CONDITION,
        config: {
          conditions: [],
          defaultBranch: '',
          ...template.defaultConfig
        }
      } as ConditionNode

    case NodeType.PARALLEL:
      return {
        ...baseNode,
        type: NodeType.PARALLEL,
        config: {
          maxConcurrency: 5,
          waitForAll: true,
          timeoutMs: 300000,
          ...template.defaultConfig
        }
      } as ParallelNode

    default:
      throw new Error(`Unsupported node type: ${type}`)
  }
}

// 创建连接
export function createConnection(
  fromNodeId: string,
  toNodeId: string,
  fromOutputId: string,
  toInputId: string,
  type: ConnectionType = ConnectionType.SEQUENCE
): NodeConnection {
  return {
    id: generateConnectionId(),
    fromNodeId,
    toNodeId,
    fromOutputId,
    toInputId,
    type,
    config: {
      delay: 0,
      retryOnFailure: false
    }
  }
}

// 验证节点配置
export function validateNode(node: WorkflowNode): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  // 基础验证
  if (!node.id) {
    errors.push('节点ID不能为空')
  }
  if (!node.name) {
    errors.push('节点名称不能为空')
  }

  // 类型特定验证
  switch (node.type) {
    case NodeType.API_CALL:
      const apiNode = node as ApiCallNode
      if (!apiNode.config.systemId) {
        errors.push('系统ID不能为空')
      }
      if (!apiNode.config.moduleId) {
        errors.push('模块ID不能为空')
      }
      if (!apiNode.config.apiId) {
        errors.push('API ID不能为空')
      }
      break

    case NodeType.DATA_TRANSFORM:
      const transformNode = node as DataTransformNode
      if (!transformNode.config.transformType) {
        errors.push('转换类型不能为空')
      }
      break

    case NodeType.CONDITION:
      const conditionNode = node as ConditionNode
      if (conditionNode.config.conditions.length === 0) {
        errors.push('至少需要一个条件规则')
      }
      break
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

// 获取节点状态颜色
export function getNodeStatusColor(status: NodeStatus): string {
  switch (status) {
    case NodeStatus.IDLE:
      return '#909399'
    case NodeStatus.WAITING:
      return '#E6A23C'
    case NodeStatus.RUNNING:
      return '#409EFF'
    case NodeStatus.SUCCESS:
      return '#67C23A'
    case NodeStatus.FAILED:
      return '#F56C6C'
    case NodeStatus.SKIPPED:
      return '#C0C4CC'
    default:
      return '#909399'
  }
}

// 获取节点类型图标
export function getNodeTypeIcon(type: NodeType): string {
  switch (type) {
    case NodeType.START:
      return 'Play'
    case NodeType.END:
      return 'Stop'
    case NodeType.API_CALL:
      return 'Connection'
    case NodeType.DATA_TRANSFORM:
      return 'Refresh'
    case NodeType.CONDITION:
      return 'Share'
    case NodeType.PARALLEL:
      return 'Grid'
    case NodeType.MERGE:
      return 'Merge'
    default:
      return 'Document'
  }
}

// 计算连接路径
export function calculateConnectionPath(
  fromNode: WorkflowNode,
  toNode: WorkflowNode,
  fromOutputId: string,
  toInputId: string
): string {
  const fromX = fromNode.position.x + 120 // 节点宽度的一半
  const fromY = fromNode.position.y + 40  // 节点高度的一半
  const toX = toNode.position.x
  const toY = toNode.position.y + 40

  // 计算控制点
  const controlX1 = fromX + (toX - fromX) / 3
  const controlY1 = fromY
  const controlX2 = fromX + (toX - fromX) * 2 / 3
  const controlY2 = toY

  return `M ${fromX} ${fromY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${toX} ${toY}`
}

// 检查连接是否有效
export function isValidConnection(
  fromNode: WorkflowNode,
  toNode: WorkflowNode,
  fromOutputId: string,
  toInputId: string,
  existingConnections: NodeConnection[]
): { valid: boolean; error?: string } {
  // 不能连接到自己
  if (fromNode.id === toNode.id) {
    return { valid: false, error: '不能连接到自己' }
  }

  // 检查输出是否存在
  const fromOutput = fromNode.outputs.find(o => o.id === fromOutputId)
  if (!fromOutput) {
    return { valid: false, error: '输出端口不存在' }
  }

  // 检查输入是否存在
  const toInput = toNode.inputs.find(i => i.id === toInputId)
  if (!toInput) {
    return { valid: false, error: '输入端口不存在' }
  }

  // 检查是否已经存在相同的连接
  const existingConnection = existingConnections.find(
    c => c.fromNodeId === fromNode.id && 
         c.toNodeId === toNode.id && 
         c.fromOutputId === fromOutputId && 
         c.toInputId === toInputId
  )
  if (existingConnection) {
    return { valid: false, error: '连接已存在' }
  }

  // 检查是否会形成循环
  if (wouldCreateCycle(fromNode.id, toNode.id, existingConnections)) {
    return { valid: false, error: '不能形成循环连接' }
  }

  return { valid: true }
}

// 检查是否会形成循环
function wouldCreateCycle(
  fromNodeId: string,
  toNodeId: string,
  connections: NodeConnection[]
): boolean {
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
    const outgoingConnections = connections.filter(c => c.fromNodeId === currentNodeId)
    for (const connection of outgoingConnections) {
      stack.push(connection.toNodeId)
    }
  }

  return false
}

// 获取节点的执行顺序
export function getExecutionOrder(
  nodes: WorkflowNode[],
  connections: NodeConnection[]
): string[][] {
  const nodeMap = new Map(nodes.map(n => [n.id, n]))
  const inDegree = new Map<string, number>()
  const outgoing = new Map<string, string[]>()

  // 初始化
  nodes.forEach(node => {
    inDegree.set(node.id, 0)
    outgoing.set(node.id, [])
  })

  // 计算入度和出度
  connections.forEach(conn => {
    const fromDegree = inDegree.get(conn.toNodeId) || 0
    inDegree.set(conn.toNodeId, fromDegree + 1)
    
    const outList = outgoing.get(conn.fromNodeId) || []
    outList.push(conn.toNodeId)
    outgoing.set(conn.fromNodeId, outList)
  })

  const result: string[][] = []
  const queue: string[] = []

  // 找到所有入度为0的节点
  inDegree.forEach((degree, nodeId) => {
    if (degree === 0) {
      queue.push(nodeId)
    }
  })

  while (queue.length > 0) {
    const currentLevel: string[] = []
    const nextQueue: string[] = []

    // 处理当前层级的所有节点
    while (queue.length > 0) {
      const nodeId = queue.shift()!
      currentLevel.push(nodeId)

      // 更新相邻节点的入度
      const neighbors = outgoing.get(nodeId) || []
      neighbors.forEach(neighborId => {
        const newDegree = (inDegree.get(neighborId) || 0) - 1
        inDegree.set(neighborId, newDegree)
        
        if (newDegree === 0) {
          nextQueue.push(neighborId)
        }
      })
    }

    if (currentLevel.length > 0) {
      result.push(currentLevel)
    }

    // 准备下一轮
    queue.push(...nextQueue)
  }

  return result
}