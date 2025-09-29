/**
 * Schema转换与类型推断工具
 * 支持JSON Schema、示例JSON与参数表格之间的相互转换
 * 包含合并/覆盖策略与冲突检测功能
 */

export interface ParamItem {
  id: number | string
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'file' | 'null'
  required: boolean
  description?: string
  level: number
  parentId: number | string | null
  value?: any // 示例值
  children?: ParamItem[] // 子参数（用于树形结构）
}

export interface ConversionOptions {
  mode: 'merge' | 'override' // 合并模式或覆盖模式
  arrayStyle: 'expand' | 'type-only' | 'first-item' // 数组处理方式
  nullHandling: 'keep' | 'string' | 'skip' // 空值处理
  maxDepth: number // 最大层级
  autoInferTypes: boolean // 自动推断类型
  defaultRequired: boolean // 默认必填
  preserveIds: boolean // 保留现有ID
}

export interface ConversionResult {
  params: ParamItem[]
  conflicts: ConflictInfo[]
  stats: ConversionStats
}

export interface ConflictInfo {
  id: string // 冲突ID
  paramId: string // 参数ID
  path: string // 参数路径
  field: string // 冲突字段名
  type: 'type' | 'required' | 'duplicate'
  existing: ParamItem
  incoming: ParamItem
  resolution?: 'keep_existing' | 'use_incoming' | 'manual'
}

export interface ConversionStats {
  totalParams: number
  addedParams: number
  updatedParams: number
  conflictCount: number
  maxDepth: number
  processingTime: number
}

export class SchemaConverter {
  private static idCounter = 0

  /**
   * 生成唯一ID
   */
  private static generateId(): string {
    return `param_${++this.idCounter}_${Date.now()}`
  }

  /**
   * 类型推断
   */
  static inferType(value: unknown): ParamItem['type'] {
    if (value === null || value === undefined) return 'null'
    if (Array.isArray(value)) return 'array'
    
    const type = typeof value
    switch (type) {
      case 'string': return 'string'
      case 'number': return 'number'
      case 'boolean': return 'boolean'
      case 'object': return 'object'
      default: return 'string'
    }
  }

  /**
   * 从JSON示例转换为参数列表
   */
  static fromExample(
    example: unknown, 
    options: Partial<ConversionOptions> = {}
  ): ConversionResult {
    const startTime = performance.now()
    const opts: ConversionOptions = {
      mode: 'override',
      arrayStyle: 'expand',
      nullHandling: 'keep',
      maxDepth: 5,
      autoInferTypes: true,
      defaultRequired: false,
      preserveIds: false,
      ...options
    }

    const params: ParamItem[] = []
    const conflicts: ConflictInfo[] = []
    let maxDepth = 0

    const walk = (
      obj: unknown, 
      level = 0, 
      parentId: string | null = null,
      parentPath = ''
    ): void => {
      if (level > opts.maxDepth) return
      maxDepth = Math.max(maxDepth, level)

      if (typeof obj !== 'object' || obj === null) return

      Object.entries(obj as Record<string, unknown>).forEach(([key, value]) => {
        const currentPath = parentPath ? `${parentPath}.${key}` : key
        const type = opts.autoInferTypes ? this.inferType(value) : 'string'
        
        // 处理空值
        if (value === null || value === undefined) {
          if (opts.nullHandling === 'skip') return
          if (opts.nullHandling === 'string') {
            value = ''
          }
        }

        const param: ParamItem = {
          id: this.generateId(),
          name: key,
          type,
          required: opts.defaultRequired,
          description: '',
          level,
          parentId: parentId,
          value: this.getExampleValue(value, type)
        }

        params.push(param)

        // 递归处理对象和数组
        if (type === 'object' && value && typeof value === 'object') {
          walk(value, level + 1, param.id, currentPath)
        } else if (type === 'array' && Array.isArray(value)) {
          this.handleArrayConversion(value, param, level + 1, currentPath, opts, walk)
        }
      })
    }

    walk(example)

    const processingTime = performance.now() - startTime
    const stats: ConversionStats = {
      totalParams: params.length,
      addedParams: params.length,
      updatedParams: 0,
      conflictCount: conflicts.length,
      maxDepth,
      processingTime
    }

    return { params, conflicts, stats }
  }

  /**
   * 处理数组转换
   */
  private static handleArrayConversion(
    array: unknown[],
    parentParam: ParamItem,
    level: number,
    parentPath: string,
    options: ConversionOptions,
    walkFn: Function
  ): void {
    if (array.length === 0) return

    switch (options.arrayStyle) {
      case 'expand':
        // 展开所有数组项
        array.forEach((item, index) => {
          if (typeof item === 'object' && item !== null) {
            walkFn(item, level, parentParam.id, `${parentPath}[${index}]`)
          }
        })
        break
      
      case 'first-item':
        // 仅处理第一项
        const firstItem = array[0]
        if (typeof firstItem === 'object' && firstItem !== null) {
          walkFn(firstItem, level, parentParam.id, `${parentPath}[0]`)
        }
        break
      
      case 'type-only':
        // 仅标记为数组类型，不展开内容
        break
    }
  }

  /**
   * 获取示例值
   */
  private static getExampleValue(value: unknown, type: ParamItem['type']): any {
    switch (type) {
      case 'string': return typeof value === 'string' ? value : ''
      case 'number': return typeof value === 'number' ? value : 0
      case 'boolean': return typeof value === 'boolean' ? value : false
      case 'null': return null
      case 'array': return Array.isArray(value) ? value : []
      case 'object': return typeof value === 'object' ? value : {}
      default: return value
    }
  }

  /**
   * 合并参数列表
   */
  static mergeParams(
    existingParams: ParamItem[],
    newParams: ParamItem[],
    options: Partial<ConversionOptions> & { detectConflicts?: boolean } = {}
  ): ConversionResult {
    const startTime = performance.now()
    const opts: ConversionOptions = {
      mode: 'merge',
      arrayStyle: 'expand',
      nullHandling: 'keep',
      maxDepth: 10,
      autoInferTypes: true,
      defaultRequired: false,
      preserveIds: true,
      ...options
    }
    const detectConflicts = options.detectConflicts ?? false

    const conflicts: ConflictInfo[] = []
    const mergedParams: ParamItem[] = []
    const existingMap = new Map<string, ParamItem>()
    
    // 构建现有参数的映射
    existingParams.forEach(param => {
      const key = this.getParamKey(param)
      existingMap.set(key, param)
    })

    let addedCount = 0
    let updatedCount = 0

    if (opts.mode === 'override') {
      // 覆盖模式：完全替换
      mergedParams.push(...newParams.map(param => ({
        ...param,
        id: opts.preserveIds ? param.id : this.generateId()
      })))
      addedCount = newParams.length
    } else {
      // 合并模式：智能合并
      // 1. 保留现有参数
      mergedParams.push(...existingParams)

      // 2. 处理新参数
      newParams.forEach(newParam => {
        const key = this.getParamKey(newParam)
        const existing = existingMap.get(key)

        if (existing) {
          // 检测冲突（仅在启用时）
          if (detectConflicts) {
            const conflict = this.detectConflict(existing, newParam)
            if (conflict) {
              conflicts.push(conflict)
            }
          }

          // 更新现有参数
          const index = mergedParams.findIndex(p => this.getParamKey(p) === key)
          if (index >= 0) {
            mergedParams[index] = {
              ...existing,
              ...newParam,
              id: opts.preserveIds ? existing.id : newParam.id
            }
            updatedCount++
          }
        } else {
          // 添加新参数
          mergedParams.push({
            ...newParam,
            id: opts.preserveIds ? newParam.id : this.generateId()
          })
          addedCount++
        }
      })
    }

    const processingTime = performance.now() - startTime
    const stats: ConversionStats = {
      totalParams: mergedParams.length,
      addedParams: addedCount,
      updatedParams: updatedCount,
      conflictCount: conflicts.length,
      maxDepth: Math.max(...mergedParams.map(p => p.level), 0),
      processingTime
    }

    return { params: mergedParams, conflicts, stats }
  }

  /**
   * 生成参数唯一键
   */
  private static getParamKey(param: ParamItem): string {
    return `${param.level}_${param.parentId || 'root'}_${param.name}`
  }

  /**
   * 检测参数冲突
   */
  private static detectConflict(existing: ParamItem, incoming: ParamItem): ConflictInfo | null {
    const path = this.getParamPath(existing)

    // 类型冲突
    if (existing.type !== incoming.type) {
      return {
        id: `conflict_${existing.id}_type`,
        paramId: String(existing.id),
        path,
        field: existing.name,
        type: 'type',
        existing,
        incoming,
        resolution: 'manual'
      }
    }

    // 必填状态冲突
    if (existing.required !== incoming.required) {
      return {
        id: `conflict_${existing.id}_required`,
        paramId: String(existing.id),
        path,
        field: existing.name,
        type: 'required',
        existing,
        incoming,
        resolution: 'use_incoming' // 默认使用新值
      }
    }

    return null
  }

  /**
   * 获取参数路径
   */
  private static getParamPath(param: ParamItem): string {
    // 这里可以实现完整的路径追踪逻辑
    return param.name
  }

  /**
   * 导出为JSON Schema
   */
  static toJsonSchema(params: ParamItem[]): Record<string, any> {
    const schema: Record<string, any> = {
      type: 'object',
      properties: {},
      required: []
    }

    const topLevelParams = params.filter(p => p.level === 0)
    
    topLevelParams.forEach(param => {
      if (!param.name) return

      const property: Record<string, any> = {
        type: param.type === 'null' ? 'string' : param.type
      }

      if (param.description) {
        property.description = param.description
      }

      if (param.type === 'object') {
        const childParams = params.filter(p => p.parentId === param.id)
        if (childParams.length > 0) {
          property.type = 'object'
          property.properties = {}
          // 递归处理子属性
          this.buildNestedSchema(params, param.id, property)
        }
      } else if (param.type === 'array') {
        property.type = 'array'
        const childParams = params.filter(p => p.parentId === param.id)
        if (childParams.length > 0) {
          property.items = {
            type: 'object',
            properties: {}
          }
          // 处理数组项的属性
          this.buildNestedSchema(params, param.id, property.items)
        }
      }

      schema.properties[param.name] = property

      if (param.required) {
        schema.required.push(param.name)
      }
    })

    return schema
  }

  /**
   * 构建嵌套Schema
   */
  private static buildNestedSchema(
    params: ParamItem[], 
    parentId: string | number, 
    schema: Record<string, any>
  ): void {
    const childParams = params.filter(p => p.parentId === parentId)
    
    childParams.forEach(child => {
      if (!child.name) return

      const property: Record<string, any> = {
        type: child.type === 'null' ? 'string' : child.type
      }

      if (child.description) {
        property.description = child.description
      }

      if (child.type === 'object') {
        property.properties = {}
        this.buildNestedSchema(params, child.id, property)
      } else if (child.type === 'array') {
        property.items = { type: 'string' } // 简化处理
      }

      schema.properties[child.name] = property

      if (child.required) {
        if (!schema.required) schema.required = []
        schema.required.push(child.name)
      }
    })
  }

  /**
   * 导出为示例JSON
   */
  static toExampleJson(params: ParamItem[]): Record<string, any> {
    const result: Record<string, any> = {}
    
    const topLevelParams = params.filter(p => p.level === 0)
    
    topLevelParams.forEach(param => {
      if (!param.name) return
      
      result[param.name] = this.buildExampleValue(params, param)
    })

    return result
  }

  /**
   * 构建示例值
   */
  private static buildExampleValue(params: ParamItem[], param: ParamItem): any {
    switch (param.type) {
      case 'string':
        return param.value || param.description || 'string'
      case 'number':
        return param.value || 0
      case 'boolean':
        return param.value || false
      case 'null':
        return null
      case 'object':
        const obj: Record<string, any> = {}
        const children = params.filter(p => p.parentId === param.id)
        children.forEach(child => {
          if (child.name) {
            obj[child.name] = this.buildExampleValue(params, child)
          }
        })
        return obj
      case 'array':
        const arrayChildren = params.filter(p => p.parentId === param.id)
        if (arrayChildren.length > 0) {
          const item: Record<string, any> = {}
          arrayChildren.forEach(child => {
            if (child.name) {
              item[child.name] = this.buildExampleValue(params, child)
            }
          })
          return [item]
        }
        return []
      default:
        return param.value || null
    }
  }
}

export default SchemaConverter