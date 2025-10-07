export interface ParamItem {
  id: number
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'file' | 'null'
  required: boolean
  description?: string
  level: number
  parentId: number | null
  // 可选位置元数据：用于区分 Query/Path/JSON/Form
  location?: 'query' | 'path' | 'json' | 'form'
}

// 允许嵌套的 Schema（支持 JSON Schema 风格：properties/items）
export type SchemaObject = Record<string, any>

export class ParamsConverter {
  // 生成嵌套 JSON Schema（修复：包含对象/数组的子字段，如 data 下的字段）
  static toSchema(params: ParamItem[]): SchemaObject {
    const schema: Record<string, any> = {
      type: 'object',
      properties: {},
      required: [] as string[]
    }

    const topLevel = params.filter(p => p && p.level === 0 && (p.name || '').trim())
    topLevel.forEach(p => {
      const name = (p.name || '').trim()
      if (!name) return
      const prop: Record<string, any> = {
        type: p.type === 'null' ? 'string' : p.type
      }
      if (p.description) prop.description = p.description

      if (p.type === 'object') {
        prop.type = 'object'
        prop.properties = {}
        // 构建嵌套对象属性
        this.buildNestedSchema(params, p.id, prop)
      } else if (p.type === 'array') {
        prop.type = 'array'
        const children = params.filter(c => c.parentId === p.id)
        if (children.length > 0) {
          // 数组项为对象，构建 items.properties
          prop.items = { type: 'object', properties: {} }
          this.buildNestedSchema(params, p.id, prop.items)
        } else {
          // 简化为元素类型占位
          prop.items = { type: 'string' }
        }
      }

      (schema.properties as Record<string, any>)[name] = prop
      if (p.required) (schema.required as string[]).push(name)
    })

    return schema
  }

  // 新增：根据 location 分组生成复合请求 Schema
  // 输出结构：{ query_params?: Schema, path_params?: Schema, body?: Schema }
  static toRequestSchema(params: ParamItem[]): SchemaObject | null {
    if (!Array.isArray(params) || params.length === 0) return null
    const byLoc = (loc: ParamItem['location']) => params.filter(p => (p.location || '') === loc)
    const queryParams = byLoc('query')
    const pathParams = byLoc('path')
    const jsonBodyParams = byLoc('json')
    const formBodyParams = byLoc('form')

    const result: Record<string, any> = {}
    if (queryParams.length > 0) result.query_params = this.toSchema(queryParams)
    if (pathParams.length > 0) result.path_params = this.toSchema(pathParams)
    // 统一 body，无论 JSON 或 Form，在后端按 request_format 区分
    const bodyParams = jsonBodyParams.length > 0 ? jsonBodyParams : formBodyParams
    if (bodyParams.length > 0) result.body = this.toSchema(bodyParams)

    // 若没有任何分组命中，回退为单体Schema（兼容旧逻辑）
    if (Object.keys(result).length === 0) return this.toSchema(params)
    return result
  }

  // 辅助：为指定父节点构建嵌套属性（对象/数组项）
  private static buildNestedSchema(params: ParamItem[], parentId: number, targetSchema: Record<string, any>): void {
    const children = params.filter(p => p.parentId === parentId)
    targetSchema.properties = targetSchema.properties || {}

    children.forEach(child => {
      if (!child.name) return
      const property: Record<string, any> = {
        type: child.type === 'null' ? 'string' : child.type
      }
      if (child.description) property.description = child.description

      if (child.type === 'object') {
        property.properties = {}
        this.buildNestedSchema(params, child.id, property)
      } else if (child.type === 'array') {
        // 若数组子项为对象，尝试构建 items.properties
        const grandChildren = params.filter(p => p.parentId === child.id)
        if (grandChildren.length > 0) {
          property.items = { type: 'object', properties: {} }
          this.buildNestedSchema(params, child.id, property.items)
        } else {
          property.items = { type: 'string' }
        }
      }

      targetSchema.properties[child.name] = property
      if (child.required) {
        targetSchema.required = targetSchema.required || []
        targetSchema.required.push(child.name)
      }
    })
  }

  // 从示例 JSON 生成参数列表（保持不变）
  static fromExample(example: unknown): ParamItem[] {
    let id = 0
    const genId = () => ++id
    const inferType = (value: unknown): ParamItem['type'] => {
      if (value === null) return 'null'
      if (Array.isArray(value)) return 'array'
      const t = typeof value
      if (t === 'string') return 'string'
      if (t === 'number') return 'number'
      if (t === 'boolean') return 'boolean'
      if (t === 'object') return 'object'
      return 'string'
    }
    const walk = (obj: unknown, level = 0, parentId: number | null = null): ParamItem[] => {
      const items: ParamItem[] = []
      if (typeof obj !== 'object' || obj === null) return items
      Object.entries(obj as Record<string, unknown>).forEach(([key, value]) => {
        const type = inferType(value)
        const idVal = genId()
        items.push({ id: idVal, name: key, type, required: true, description: '', level, parentId })
        if (type === 'object') items.push(...walk(value as object, level + 1, idVal))
        else if (type === 'array') {
          const first = Array.isArray(value) && value.length > 0 ? value[0] : null
          if (inferType(first) === 'object') items.push(...walk((first ?? {}) as object, level + 1, idVal))
        }
      })
      return items
    }
    return walk(example)
  }

  // 新增：解析复合请求 Schema（含 query_params/path_params/body），并注入 location
  static fromRequestSchema(schema: SchemaObject | unknown): ParamItem[] {
    if (!schema || typeof schema !== 'object') return []
    const root = schema as Record<string, any>

    const assemble = (sub: any, loc: ParamItem['location']): ParamItem[] => {
      const arr = this.fromSchema(sub)
      return arr.map(p => ({ ...p, location: loc }))
    }

    const hasComposite = (
      'query_params' in root || 'path_params' in root || 'params' in root || 'body' in root
    )
    if (!hasComposite) return this.fromSchema(schema)

    let result: ParamItem[] = []
    if (root.query_params) result = result.concat(assemble(root.query_params, 'query'))
    // 兼容旧 key
    else if (root.params) result = result.concat(assemble(root.params, 'query'))

    if (root.path_params) result = result.concat(assemble(root.path_params, 'path'))
    if (root.body) result = result.concat(assemble(root.body, 'json'))
    return result
  }

  // 从 JSON Schema 解析为参数列表（增强：支持 properties/items/required）
  static fromSchema(schema: SchemaObject | unknown): ParamItem[] {
    if (!schema || typeof schema !== 'object') return []

    // 若是复合结构（包含 query_params/path_params/body），转交专用解析
    const root = schema as Record<string, any>
    if ('query_params' in root || 'path_params' in root || 'params' in root || 'body' in root) {
      return this.fromRequestSchema(schema)
    }

    let idCounter = 0
    const genId = () => ++idCounter
    const params: ParamItem[] = []

    // 解析普通（旧版扁平）格式：{ field: { type, required, description } }
    const tryFlatFormat = (): boolean => {
      const entries = Object.entries(schema as SchemaObject)
      // 如果存在显式的 JSON Schema 根（含 properties），不走扁平
      if ((schema as any).properties) return false
      let used = false
      for (const [name, def] of entries) {
        if (def && typeof def === 'object' && 'type' in (def as any)) {
          const type = (def as any).type as ParamItem['type']
          params.push({
            id: genId(),
            name: name || '',
            type: typeof type === 'string' ? type : 'string',
            required: !!(def as any).required,
            description: (def as any).description || '',
            level: 0,
            parentId: null
          })
          used = true
        }
      }
      return used
    }

    if (tryFlatFormat()) return params

    // JSON Schema 解析
    const rootProps = (root.properties && typeof root.properties === 'object') ? root.properties as Record<string, any> : {}
    const rootRequired: string[] = Array.isArray(root.required) ? (root.required as string[]) : []

    const parseProperties = (
      properties: Record<string, any>,
      requiredList: string[],
      level: number,
      parentId: number | null
    ): void => {
      for (const [name, def] of Object.entries(properties || {})) {
        if (!name) continue
        const typeRaw = typeof def?.type === 'string' ? (def.type as string) : 'string'
        const type: ParamItem['type'] = typeRaw === 'integer' ? 'number' : (typeRaw as ParamItem['type'])
        const id = genId()
        const required = Array.isArray(requiredList) ? requiredList.includes(name) : false
        params.push({
          id,
          name,
          type,
          required,
          description: typeof def?.description === 'string' ? def.description : '',
          level,
          parentId
        })

        // 嵌套对象
        if (type === 'object' && def && typeof def.properties === 'object') {
          const childRequired: string[] = Array.isArray(def.required) ? (def.required as string[]) : []
          parseProperties(def.properties as Record<string, any>, childRequired, level + 1, id)
        }
        // 数组项
        else if (type === 'array' && def && def.items) {
          const items = def.items
          if (items && typeof items.properties === 'object') {
            const childRequired: string[] = Array.isArray(items.required) ? (items.required as string[]) : []
            parseProperties(items.properties as Record<string, any>, childRequired, level + 1, id)
          }
        }
      }
    }

    parseProperties(rootProps, rootRequired, 0, null)
    return params
  }
}