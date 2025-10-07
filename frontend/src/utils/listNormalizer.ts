import type { ApiResponse } from '@/types'

export interface NormalizedListResult<T = unknown> {
  success: boolean
  message?: string
  code: number
  list: T[]
  total: number
  page: number
  size: number
}

function asNumber(val: unknown, fallback: number): number {
  if (typeof val === 'number' && Number.isFinite(val)) return val
  if (typeof val === 'string') {
    const n = Number(val)
    if (Number.isFinite(n)) return n
  }
  return fallback
}

export function normalizeList<T = unknown>(resp: ApiResponse<unknown> | unknown[]): NormalizedListResult<T> {
  // 支持两种返回结构：
  // 1) ApiResponse<{ list/items/apis: T[]; total: number; page: number; size/pageSize: number }>
  // 2) 直接返回数组 T[]
  const raw = Array.isArray(resp) ? resp : (resp?.data ?? [])
  const dataObj = (!Array.isArray(raw) && raw ? (raw as Record<string, unknown>) : {})
  const listValue = dataObj['list']
  const itemsValue = dataObj['items']
  const listArr: unknown[] = Array.isArray(raw)
    ? (raw as unknown[])
    : (Array.isArray(listValue)
        ? (listValue as unknown[])
        : (Array.isArray(itemsValue)
            ? (itemsValue as unknown[])
            : []))
  const pageRaw = dataObj['page']
  const sizeRaw = dataObj['size']
  const pageSizeRaw = dataObj['pageSize']
  const totalRaw = dataObj['total']

  const pageVal: number = asNumber(pageRaw, 1)
  const defaultSize = Array.isArray(listArr) ? listArr.length : 0
  const sizeVal: number = asNumber(sizeRaw ?? pageSizeRaw, defaultSize)
  const totalVal: number = asNumber(totalRaw, defaultSize)

  const successVal: boolean = Array.isArray(resp) ? true : !!(resp as ApiResponse<unknown>)?.success
  const messageVal: string | undefined = Array.isArray(resp) ? undefined : (resp as ApiResponse<unknown>)?.message
  const codeVal: number = Array.isArray(resp) ? 0 : asNumber((resp as ApiResponse<unknown>)?.code, 0)

  return {
    success: successVal,
    message: messageVal,
    code: codeVal,
    list: listArr as T[],
    total: totalVal,
    page: pageVal,
    size: sizeVal
  }
}