import { defineStore } from 'pinia'
import type { ApiResponseMapping } from '@/views/page-management/types/page-config'
import { ResponseMappingConverter } from '@/utils/responseMapping'

export interface PageRuntimeState {
  data: Record<string, unknown>
  lastResponse: unknown | null
}

export const usePageRuntimeStore = defineStore('pageRuntime', {
  state: (): PageRuntimeState => ({
    data: {},
    lastResponse: null
  }),
  getters: {
    getDataByKey: (state) => {
      return (key: string): unknown => state.data[key]
    }
  },
  actions: {
    setData(key: string, value: unknown): void {
      if (!key || !key.trim()) {
        throw new Error('目标键不能为空')
      }
      this.data[key] = value
    },
    clear(): void {
      this.data = {}
      this.lastResponse = null
    },
    applyMapping(response: unknown, mapping: ApiResponseMapping): void {
      this.lastResponse = response
      const result = ResponseMappingConverter.apply(response, mapping, this.data)
      // 合并更新（不可变赋值以利于调试和追踪）
      this.data = { ...result.updates }
    }
  }
})