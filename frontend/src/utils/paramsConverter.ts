export interface ParamItem {
  id: number
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'file' | 'null'
  required: boolean
  description?: string
  level: number
  parentId: number | null
}

export type SchemaObject = Record<string, {
  type: string
  required: boolean
  description: string
}>

export class ParamsConverter {
  static toSchema(params: ParamItem[]): SchemaObject {
    const schema: SchemaObject = {}
    params
      .filter(p => p && p.level === 0 && (p.name || '').trim())
      .forEach(p => {
        const name = (p.name || '').trim()
        schema[name] = {
          type: p.type || 'string',
          required: !!p.required,
          description: p.description || ''
        }
      })
    return schema
  }

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

  static fromSchema(schema: SchemaObject | unknown): ParamItem[] {
    if (!schema || typeof schema !== 'object') return []
    let id = 0
    const genId = () => ++id
    const result: ParamItem[] = []
    Object.entries(schema as SchemaObject).forEach(([name, def]) => {
      const type = (def && typeof def.type === 'string') ? def.type as ParamItem['type'] : 'string'
      result.push({
        id: genId(),
        name: name || '',
        type,
        required: !!(def && (def as any).required),
        description: (def && (def as any).description) || '',
        level: 0,
        parentId: null
      })
    })
    return result
  }
}