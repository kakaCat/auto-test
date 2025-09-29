/**
 * URL转换工具
 * 支持URL与参数表格的双向转换
 */

export interface ParamItem {
  id: number | string
  name: string
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'file' | 'null'
  required: boolean
  description?: string
  level: number
  parentId: number | string | null
  value?: any
}

export interface UrlConversionOptions {
  arrayFormat: 'brackets' | 'repeat' | 'comma' | 'indices' // 数组格式
  encoding: 'none' | 'component' | 'form' // 编码方式
  maxDepth: number // 最大嵌套深度
  autoInferTypes: boolean // 自动推断类型
  preserveOrder: boolean // 保持参数顺序
  handleDuplicates: 'first' | 'last' | 'array' // 重复参数处理
}

export interface UrlConversionResult {
  params: ParamItem[]
  conflicts: UrlConflictInfo[]
  stats: UrlConversionStats
}

export interface UrlConflictInfo {
  field: string
  type: 'duplicate' | 'type_conflict' | 'encoding_issue'
  values: string[]
  resolution: 'merged' | 'kept_first' | 'kept_last' | 'manual'
}

export interface UrlConversionStats {
  totalParams: number
  duplicateParams: number
  encodedParams: number
  arrayParams: number
  processingTime: number
}

export class UrlConverter {
  private static idCounter = 0

  /**
   * 生成唯一ID
   */
  private static generateId(): string {
    return `url_param_${++this.idCounter}_${Date.now()}`
  }

  /**
   * 推断参数类型
   */
  private static inferType(value: string): ParamItem['type'] {
    // 空值检查
    if (value === '' || value === 'null') return 'null'
    if (value === 'undefined') return 'null'

    // 布尔值检查
    if (value === 'true' || value === 'false') return 'boolean'

    // 数字检查
    if (/^\d+$/.test(value)) return 'number'
    if (/^\d*\.\d+$/.test(value)) return 'number'
    if (/^-?\d+(\.\d+)?$/.test(value)) return 'number'

    // 数组检查（逗号分隔）
    if (value.includes(',') && value.split(',').length > 1) return 'array'

    // 对象检查（JSON格式）
    try {
      const parsed = JSON.parse(value)
      if (typeof parsed === 'object' && parsed !== null) {
        return Array.isArray(parsed) ? 'array' : 'object'
      }
    } catch {
      // 不是有效JSON，继续其他检查
    }

    // 文件检查
    if (value.startsWith('data:') || /\.(jpg|jpeg|png|gif|pdf|doc|docx)$/i.test(value)) {
      return 'file'
    }

    return 'string'
  }

  /**
   * 从URL查询字符串转换为参数列表
   */
  static fromUrl(
    url: string,
    options: Partial<UrlConversionOptions> = {}
  ): UrlConversionResult {
    const startTime = performance.now()
    const opts: UrlConversionOptions = {
      arrayFormat: 'brackets',
      encoding: 'component',
      maxDepth: 5,
      autoInferTypes: true,
      preserveOrder: true,
      handleDuplicates: 'array',
      ...options
    }

    const params: ParamItem[] = []
    const conflicts: UrlConflictInfo[] = []
    const paramMap = new Map<string, string[]>()
    
    try {
      // 解析URL
      const urlObj = new URL(url)
      const searchParams = urlObj.searchParams

      // 收集所有参数值
      for (const [key, value] of searchParams.entries()) {
        const decodedKey = this.decodeParam(key, opts.encoding)
        const decodedValue = this.decodeParam(value, opts.encoding)
        
        if (!paramMap.has(decodedKey)) {
          paramMap.set(decodedKey, [])
        }
        paramMap.get(decodedKey)!.push(decodedValue)
      }

      // 处理参数
      let index = 0
      for (const [key, values] of paramMap.entries()) {
        const processedParam = this.processUrlParam(
          key, 
          values, 
          index++, 
          opts, 
          conflicts
        )
        if (processedParam) {
          params.push(processedParam)
        }
      }

      // 处理嵌套参数（如 user[name], user[age]）
      this.processNestedParams(params, opts)

    } catch (error) {
      console.error('URL解析失败:', error)
    }

    const processingTime = performance.now() - startTime
    const stats: UrlConversionStats = {
      totalParams: params.length,
      duplicateParams: conflicts.filter(c => c.type === 'duplicate').length,
      encodedParams: params.filter(p => p.description?.includes('encoded')).length,
      arrayParams: params.filter(p => p.type === 'array').length,
      processingTime
    }

    return { params, conflicts, stats }
  }

  /**
   * 处理单个URL参数
   */
  private static processUrlParam(
    key: string,
    values: string[],
    index: number,
    options: UrlConversionOptions,
    conflicts: UrlConflictInfo[]
  ): ParamItem | null {
    if (values.length === 0) return null

    let finalValue: string
    let paramType: ParamItem['type'] = 'string'

    // 处理重复参数
    if (values.length > 1) {
      const conflict: UrlConflictInfo = {
          field: key,
          type: 'duplicate',
          values,
          resolution: options.handleDuplicates === 'array' ? 'merged' : 
            options.handleDuplicates === 'first' ? 'kept_first' : 'kept_last'
        }
      conflicts.push(conflict)

      switch (options.handleDuplicates) {
        case 'first':
          finalValue = values[0]
          break
        case 'last':
          finalValue = values[values.length - 1]
          break
        case 'array':
          finalValue = values.join(',')
          paramType = 'array'
          break
      }
    } else {
      finalValue = values[0]
    }

    // 自动推断类型
    if (options.autoInferTypes && paramType !== 'array') {
      paramType = this.inferType(finalValue)
    }

    // 处理数组格式
    const { cleanKey, isArray } = this.parseArrayKey(key, options.arrayFormat)
    if (isArray) {
      paramType = 'array'
    }

    return {
      id: this.generateId(),
      name: cleanKey,
      type: paramType,
      required: false, // URL参数默认非必填
      description: this.generateDescription(key, finalValue, options),
      level: 0,
      parentId: null,
      value: this.convertValue(finalValue, paramType)
    }
  }

  /**
   * 解析数组键名
   */
  private static parseArrayKey(
    key: string, 
    arrayFormat: UrlConversionOptions['arrayFormat']
  ): { cleanKey: string; isArray: boolean } {
    switch (arrayFormat) {
      case 'brackets':
        if (key.endsWith('[]')) {
          return { cleanKey: key.slice(0, -2), isArray: true }
        }
        break
      case 'indices':
        const indexMatch = key.match(/^(.+)\[\d+\]$/)
        if (indexMatch) {
          return { cleanKey: indexMatch[1], isArray: true }
        }
        break
    }
    return { cleanKey: key, isArray: false }
  }

  /**
   * 处理嵌套参数
   */
  private static processNestedParams(
    params: ParamItem[], 
    options: UrlConversionOptions
  ): void {
    const nestedMap = new Map<string, any>()
    const toRemove: number[] = []

    // 识别嵌套参数并构建层次结构
    params.forEach((param, index) => {
      const keys = this.parseNestedKey(param.name)
      if (keys.length > 1) {
        this.buildNestedStructure(nestedMap, keys, param)
        toRemove.push(index)
      }
    })

    // 移除原始嵌套参数
    toRemove.reverse().forEach(index => params.splice(index, 1))

    // 将嵌套结构转换为参数列表
    this.convertNestedMapToParams(nestedMap, params, 0, null)
  }

  /**
   * 解析嵌套键名
   */
  private static parseNestedKey(key: string): string[] {
    const keys: string[] = []
    let current = ''
    let depth = 0
    
    for (let i = 0; i < key.length; i++) {
      const char = key[i]
      if (char === '[') {
        if (depth === 0 && current) {
          keys.push(current)
          current = ''
        }
        depth++
      } else if (char === ']') {
        depth--
        if (depth === 0 && current) {
          keys.push(current)
          current = ''
        }
      } else if (depth === 0) {
        current += char
      } else {
        current += char
      }
    }
    
    if (current) {
      keys.push(current)
    }
    
    return keys
  }

  /**
   * 构建嵌套结构
   */
  private static buildNestedStructure(nestedMap: Map<string, any>, keys: string[], param: ParamItem): void {
    let current = nestedMap
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i]
      if (!current.has(key)) {
        current.set(key, new Map<string, any>())
      }
      current = current.get(key)
    }
    
    const lastKey = keys[keys.length - 1]
    current.set(lastKey, param)
  }

  /**
   * 将嵌套Map转换为参数列表
   */
  private static convertNestedMapToParams(
    nestedMap: Map<string, any>, 
    params: ParamItem[], 
    level: number, 
    parentId: string | null
  ): void {
    for (const [key, value] of nestedMap.entries()) {
      if (value instanceof Map) {
        // 创建对象参数
        const objectParam: ParamItem = {
          id: `nested_${key}_${level}`,
          name: key,
          type: 'object',
          required: false,
          level,
          parentId,
          value: {}
        }
        params.push(objectParam)
        
        // 递归处理子参数
        this.convertNestedMapToParams(value, params, level + 1, objectParam.id)
      } else {
        // 创建叶子参数
         const leafParam: ParamItem = {
           ...value,
           name: key,
           level,
           parentId: parentId
         }
        params.push(leafParam)
      }
    }
  }

  /**
   * 参数解码
   */
  private static decodeParam(value: string, encoding: UrlConversionOptions['encoding']): string {
    switch (encoding) {
      case 'component':
        try {
          return decodeURIComponent(value)
        } catch {
          return value
        }
      case 'form':
        return value.replace(/\+/g, ' ')
      case 'none':
      default:
        return value
    }
  }

  /**
   * 转换值类型
   */
  private static convertValue(value: string, type: ParamItem['type']): any {
    switch (type) {
      case 'number':
        const num = Number(value)
        return isNaN(num) ? value : num
      case 'boolean':
        return value === 'true'
      case 'null':
        return null
      case 'array':
        return value.split(',').map(v => v.trim())
      case 'object':
        try {
          return JSON.parse(value)
        } catch {
          return value
        }
      default:
        return value
    }
  }

  /**
   * 生成参数描述
   */
  private static generateDescription(
    originalKey: string, 
    value: string, 
    options: UrlConversionOptions
  ): string {
    const descriptions: string[] = []
    
    if (originalKey !== this.decodeParam(originalKey, options.encoding)) {
      descriptions.push('URL encoded')
    }
    
    if (originalKey.includes('[') && originalKey.includes(']')) {
      descriptions.push('Nested parameter')
    }
    
    if (value.length > 100) {
      descriptions.push('Long value')
    }
    
    return descriptions.join(', ')
  }

  /**
   * 从参数列表转换为URL查询字符串
   */
  static toUrl(
    params: ParamItem[],
    baseUrl = '',
    options: Partial<UrlConversionOptions> = {}
  ): string {
    const opts: UrlConversionOptions = {
      arrayFormat: 'brackets',
      encoding: 'component',
      maxDepth: 5,
      autoInferTypes: false,
      preserveOrder: true,
      handleDuplicates: 'array',
      ...options
    }

    const searchParams = new URLSearchParams()
    
    // 处理顶级参数
    const topLevelParams = params.filter(p => p.level === 0)
    
    topLevelParams.forEach(param => {
      this.addParamToUrl(param, params, searchParams, opts)
    })

    const queryString = searchParams.toString()
    if (!queryString) return baseUrl

    const separator = baseUrl.includes('?') ? '&' : '?'
    return `${baseUrl}${separator}${queryString}`
  }

  /**
   * 添加参数到URL
   */
  private static addParamToUrl(
    param: ParamItem,
    allParams: ParamItem[],
    searchParams: URLSearchParams,
    options: UrlConversionOptions
  ): void {
    const children = allParams.filter(p => p.parentId === param.id)
    
    if (children.length > 0) {
      // 处理嵌套对象
      children.forEach(child => {
        const key = `${param.name}[${child.name}]`
        const value = this.formatParamValue(child.value, child.type, options)
        searchParams.append(key, value)
      })
    } else {
      // 处理普通参数
      let key = param.name
      let value = this.formatParamValue(param.value, param.type, options)

      // 处理数组格式
      if (param.type === 'array' && Array.isArray(param.value)) {
        switch (options.arrayFormat) {
          case 'brackets':
            key = `${param.name}[]`
            param.value.forEach((item: any) => {
              searchParams.append(key, String(item))
            })
            return
          case 'repeat':
            param.value.forEach((item: any) => {
              searchParams.append(param.name, String(item))
            })
            return
          case 'comma':
            value = param.value.join(',')
            break
          case 'indices':
            param.value.forEach((item: any, index: number) => {
              searchParams.append(`${param.name}[${index}]`, String(item))
            })
            return
        }
      }

      searchParams.append(key, value)
    }
  }

  /**
   * 格式化参数值
   */
  private static formatParamValue(
    value: any, 
    type: ParamItem['type'], 
    options: UrlConversionOptions
  ): string {
    let stringValue: string

    switch (type) {
      case 'object':
        stringValue = JSON.stringify(value)
        break
      case 'array':
        if (Array.isArray(value)) {
          stringValue = value.join(',')
        } else {
          stringValue = String(value)
        }
        break
      case 'null':
        stringValue = ''
        break
      default:
        stringValue = String(value ?? '')
    }

    // 应用编码
    switch (options.encoding) {
      case 'component':
        return encodeURIComponent(stringValue)
      case 'form':
        return stringValue.replace(/ /g, '+')
      case 'none':
      default:
        return stringValue
    }
  }

  /**
   * 验证URL格式
   */
  static validateUrl(url: string): boolean {
    try {
      const urlObj = new URL(url)
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
    } catch {
      return false
    }
  }

  /**
   * 获取URL统计信息
   */
  static getUrlStats(url: string): {
    paramCount: number
    duplicateParams: string[]
    encodedParams: string[]
    nestedParams: string[]
  } {
    const stats = {
      paramCount: 0,
      duplicateParams: [] as string[],
      encodedParams: [] as string[],
      nestedParams: [] as string[]
    }

    try {
      const urlObj = new URL(url)
      const paramCounts = new Map<string, number>()

      for (const [key, value] of urlObj.searchParams.entries()) {
        stats.paramCount++
        
        // 检查重复参数
        const count = paramCounts.get(key) || 0
        paramCounts.set(key, count + 1)
        if (count === 1) {
          stats.duplicateParams.push(key)
        }

        // 检查编码参数
        if (key !== decodeURIComponent(key) || value !== decodeURIComponent(value)) {
          stats.encodedParams.push(key)
        }

        // 检查嵌套参数
        if (key.includes('[') && key.includes(']')) {
          stats.nestedParams.push(key)
        }
      }
    } catch (error) {
      console.error('URL统计失败:', error)
    }

    return stats
  }
}

export default UrlConverter