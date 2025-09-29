/**
 * usePageRuntimeExecutor
 * 
 * 职责：
 * - 以“页面配置（PageApiConfig）”为输入，顺序执行其中的API（按order升序）
 * - 每次调用后将响应根据 api.response.extract 映射到 PageRuntime Store
 * - 返回执行结果列表，便于展示和调试
 */

import { computed, ref } from 'vue'
import type { ApiConfigItem, PageApiConfig } from '@/views/page-management/types/page-config'
import { RuntimeExecutor } from '@/utils/runtimeExecutor'
import { usePageRuntimeStore } from '@/stores/pageRuntime'

export interface ApiExecutionRecord {
  id: string
  name: string
  method: string
  path: string
  success: boolean
  message?: string
  data?: unknown
  startedAt: number
  endedAt: number
  durationMs: number
}

export function usePageRuntimeExecutor() {
  const running = ref(false)
  const records = ref<ApiExecutionRecord[]>([])
  const pageRuntime = usePageRuntimeStore()

  const lastResult = computed(() => records.value[records.value.length - 1])

  function sortApisSerial(apis: ApiConfigItem[]): ApiConfigItem[] {
    return [...apis].sort((a, b) => a.order - b.order)
  }

  async function runSerial(config: PageApiConfig): Promise<ApiExecutionRecord[]> {
    if (!config || !Array.isArray(config.apis)) {
      throw new Error('页面配置为空或无可执行API')
    }
    running.value = true
    records.value = []
    try {
      const sorted = sortApisSerial(config.apis)
      for (const api of sorted) {
        const start = performance.now()
        try {
          const resp = await RuntimeExecutor.execute(api)
          const end = performance.now()
          const rec: ApiExecutionRecord = {
            id: api.id,
            name: api.name,
            method: api.method,
            path: api.path,
            success: resp.success,
            message: resp.message,
            data: resp.data,
            startedAt: start,
            endedAt: end,
            durationMs: Math.round(end - start)
          }
          records.value.push(rec)
          // 将响应应用映射到运行时Store（传入data作为响应主体）
          if (api.response && api.response.extract) {
            pageRuntime.applyMapping(resp.data, api.response)
          }
        } catch (err: unknown) {
          const end = performance.now()
          const rec: ApiExecutionRecord = {
            id: api.id,
            name: api.name,
            method: api.method,
            path: api.path,
            success: false,
            message: err instanceof Error ? err.message : '执行失败',
            data: undefined,
            startedAt: start,
            endedAt: end,
            durationMs: Math.round(end - start)
          }
          records.value.push(rec)
          // 可根据需求中断或继续，这里选择继续执行后续API
        }
      }
      return records.value
    } finally {
      running.value = false
    }
  }

  function clear(): void {
    records.value = []
  }

  return {
    running,
    records,
    lastResult,
    runSerial,
    clear
  }
}