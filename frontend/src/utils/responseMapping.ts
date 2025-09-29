/**
 * 响应映射工具（Converter）
 * 
 * 作用：
 * - 将接口响应数据根据映射配置提取并输出成页面状态更新对象
 * - 支持点号路径（dot-notation），例如：data.items[0].name（数组索引仅基础支持）
 * - 提供纯函数静态方法，便于在不同场景复用
 */

import type { ApiResponseMapping } from '@/views/page-management/types/page-config'

// 路径解析结果
interface PathToken {
  key: string
  index?: number
}

export interface ResponseApplyResult {
  updates: Record<string, unknown>
}

export class ResponseMappingConverter {
  /**
   * 将响应数据根据映射配置应用，生成页面状态更新对象
   */
  static apply(response: unknown, mapping: ApiResponseMapping, prevState?: Record<string, unknown>): ResponseApplyResult {
    if (!mapping || !mapping.extract) {
      return { updates: {} }
    }
    const updates: Record<string, unknown> = {}
    const extract = mapping.extract
    const srcKeys = Object.keys(extract)
    for (const src of srcKeys) {
      const target = String(extract[src] ?? '')
      if (!target.trim()) {
        // 跳过空目标键
        continue
      }
      const value = this.getByPath(response, src)
      updates[target] = value
    }
    // 可选：应用 transform（预留，当前直接透传）
    // 如果需要在此执行 mapping.transform，可在此处扩展
    const result: ResponseApplyResult = { updates }
    if (prevState) {
      // 兼容返回旧状态合并后的对象（不直接修改 prevState）
      result.updates = { ...prevState, ...updates }
    }
    return result
  }

  /**
   * 根据点号路径从对象中安全获取值
   * 支持基本的数组索引访问，如 items[0].name
   */
  static getByPath(obj: unknown, path: string): unknown {
    if (!path || typeof path !== 'string') return undefined
    const tokens = this.parsePath(path)
    let current: unknown = obj
    for (const tk of tokens) {
      if (current === null || current === undefined) return undefined
      if (typeof current !== 'object') return undefined
      const container = current as Record<string, unknown>
      const next = container[tk.key]
      if (tk.index !== undefined) {
        if (!Array.isArray(next)) return undefined
        current = next[tk.index]
      } else {
        current = next
      }
    }
    return current
  }

  /**
   * 解析路径为令牌序列
   */
  static parsePath(path: string): PathToken[] {
    const segments = path.split('.').map(s => s.trim()).filter(Boolean)
    const tokens: PathToken[] = []
    for (const seg of segments) {
      const match = seg.match(/^(\w+)(?:\[(\d+)\])?$/)
      if (!match) {
        // 不可解析的片段，抛出明确错误
        throw new Error(`无效的路径片段: ${seg}`)
      }
      const key = match[1]
      const indexStr = match[2]
      const token: PathToken = { key }
      if (indexStr !== undefined) {
        token.index = Number(indexStr)
      }
      tokens.push(token)
    }
    return tokens
  }
}

export default ResponseMappingConverter