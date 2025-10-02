/**
 * Mock服务 - 处理Mock匹配逻辑和API调用
 */
import type { MockConfig, MockMatchCondition, MockMatchResult, MockExecutionResult } from '@/types/mock'

export interface ApiRequest {
  url: string
  method: string
  headers?: Record<string, any>
  params?: Record<string, any>
  body?: any
}

export interface ApiResponse {
  statusCode: number
  data: any
  headers?: Record<string, any>
  responseTime: number
  isMocked: boolean
  mockId?: string
}

/**
 * Mock匹配服务类
 */
export class MockService {
  private static instance: MockService
  private mockConfigs: Map<string, MockConfig[]> = new Map()

  private constructor() {}

  public static getInstance(): MockService {
    if (!MockService.instance) {
      MockService.instance = new MockService()
    }
    return MockService.instance
  }

  /**
   * 注册API的Mock配置
   */
  public registerMocks(apiId: string, mocks: MockConfig[]): void {
    this.mockConfigs.set(apiId, mocks)
  }

  /**
   * 获取API的Mock配置
   */
  public getMocks(apiId: string): MockConfig[] {
    return this.mockConfigs.get(apiId) || []
  }

  /**
   * 执行API请求（带Mock匹配）
   */
  public async executeRequest(apiId: string, request: ApiRequest): Promise<ApiResponse> {
    const startTime = Date.now()
    
    try {
      // 获取启用的Mock配置
      const enabledMocks = this.getEnabledMocks(apiId)
      
      if (enabledMocks.length > 0) {
        // 尝试匹配Mock
        const matchResult = this.findMatchingMock(enabledMocks, request)
        
        if (matchResult.matched && matchResult.mockConfig) {
          // 使用Mock响应
          return await this.executeMockResponse(matchResult.mockConfig, request, startTime)
        }
      }
      
      // 没有匹配的Mock，调用真实接口
      return await this.executeRealRequest(request, startTime)
    } catch (error) {
      console.error('API请求执行失败:', error)
      throw error
    }
  }

  /**
   * 获取启用的Mock配置（按优先级排序）
   */
  private getEnabledMocks(apiId: string): MockConfig[] {
    const mocks = this.getMocks(apiId)
    return mocks
      .filter(mock => mock.enabled)
      .sort((a, b) => a.priority - b.priority) // 优先级数字越小越高
  }

  /**
   * 查找匹配的Mock配置
   */
  public findMatchingMock(mocks: MockConfig[], request: ApiRequest): MockMatchResult {
    for (const mock of mocks) {
      const matchResult = this.checkMockMatch(mock, request)
      if (matchResult.matched) {
        return {
          matched: true,
          mockConfig: mock,
          matchedConditions: matchResult.matchedConditions.map(c => c.id),
          reason: '匹配成功'
        }
      }
    }

    return {
      matched: false,
      mockConfig: undefined,
      matchedConditions: [],
      reason: '没有找到匹配的Mock配置'
    }
  }

  /**
   * 检查单个Mock是否匹配
   */
  public checkMockMatch(mock: MockConfig, request: ApiRequest): {
    matched: boolean
    matchedConditions: MockMatchCondition[]
    failedConditions: MockMatchCondition[]
  } {
    const matchedConditions: MockMatchCondition[] = []
    const failedConditions: MockMatchCondition[] = []

    // 如果没有匹配条件，默认匹配
    if (!mock.matchConditions || mock.matchConditions.length === 0) {
      return { matched: true, matchedConditions, failedConditions }
    }

    for (const condition of mock.matchConditions) {
      if (this.evaluateCondition(condition, request)) {
        matchedConditions.push(condition)
      } else {
        failedConditions.push(condition)
      }
    }

    // 所有条件都必须匹配
    const matched = failedConditions.length === 0

    return { matched, matchedConditions, failedConditions }
  }

  /**
   * 评估单个匹配条件
   */
  private evaluateCondition(condition: MockMatchCondition, request: ApiRequest): boolean {
    try {
      const actualValue = this.extractValueFromRequest(condition.field, request)
      return this.compareValues(actualValue, condition.operator, condition.value)
    } catch (error) {
      console.warn('条件评估失败:', condition, error)
      return false
    }
  }

  /**
   * 从请求中提取字段值
   */
  private extractValueFromRequest(fieldPath: string, request: ApiRequest): any {
    const requestData = {
      url: request.url,
      method: request.method,
      headers: request.headers || {},
      params: request.params || {},
      body: request.body || {}
    }

    return this.getValueByPath(requestData, fieldPath)
  }

  /**
   * 通过路径获取对象值
   */
  private getValueByPath(obj: any, path: string): any {
    if (!path) return obj
    
    const keys = path.split('.')
    let current = obj

    for (const key of keys) {
      if (current === null || current === undefined) {
        return undefined
      }
      current = current[key]
    }

    return current
  }

  /**
   * 比较值
   */
  private compareValues(actualValue: any, operator: string, expectedValue: any): boolean {
    switch (operator) {
      case 'equals':
        return actualValue === expectedValue
      
      case 'not_equals':
        return actualValue !== expectedValue
      
      case 'contains':
        if (typeof actualValue === 'string' && typeof expectedValue === 'string') {
          return actualValue.includes(expectedValue)
        }
        if (Array.isArray(actualValue)) {
          return actualValue.includes(expectedValue)
        }
        return false
      
      case 'not_contains':
        if (typeof actualValue === 'string' && typeof expectedValue === 'string') {
          return !actualValue.includes(expectedValue)
        }
        if (Array.isArray(actualValue)) {
          return !actualValue.includes(expectedValue)
        }
        return true
      
      case 'greater_than':
        return Number(actualValue) > Number(expectedValue)
      
      case 'less_than':
        return Number(actualValue) < Number(expectedValue)
      
      case 'greater_equal':
        return Number(actualValue) >= Number(expectedValue)
      
      case 'less_equal':
        return Number(actualValue) <= Number(expectedValue)
      
      case 'regex':
        try {
          const regex = new RegExp(expectedValue)
          return regex.test(String(actualValue))
        } catch (error) {
          console.warn('正则表达式无效:', expectedValue)
          return false
        }
      
      case 'exists':
        return actualValue !== undefined && actualValue !== null
      
      case 'not_exists':
        return actualValue === undefined || actualValue === null
      
      case 'empty':
        if (typeof actualValue === 'string') return actualValue === ''
        if (Array.isArray(actualValue)) return actualValue.length === 0
        if (typeof actualValue === 'object') return Object.keys(actualValue || {}).length === 0
        return actualValue === null || actualValue === undefined
      
      case 'not_empty':
        if (typeof actualValue === 'string') return actualValue !== ''
        if (Array.isArray(actualValue)) return actualValue.length > 0
        if (typeof actualValue === 'object') return Object.keys(actualValue || {}).length > 0
        return actualValue !== null && actualValue !== undefined
      
      default:
        console.warn('未知的操作符:', operator)
        return false
    }
  }

  /**
   * 执行Mock响应
   */
  private async executeMockResponse(
    mock: MockConfig, 
    request: ApiRequest, 
    startTime: number
  ): Promise<ApiResponse> {
    // 模拟延迟
    if (mock.delay && mock.delay > 0) {
      await new Promise(resolve => setTimeout(resolve, mock.delay))
    }

    const endTime = Date.now()

    return {
      statusCode: mock.statusCode || 200,
      data: mock.responseData,
      headers: {
        'Content-Type': 'application/json',
        'X-Mock-Id': mock.id,
        'X-Mock-Name': mock.name
      },
      responseTime: endTime - startTime,
      isMocked: true,
      mockId: mock.id
    }
  }

  /**
   * 执行真实接口请求
   */
  private async executeRealRequest(request: ApiRequest, startTime: number): Promise<ApiResponse> {
    try {
      // 构建请求配置
      const fetchConfig: RequestInit = {
        method: request.method,
        headers: {
          'Content-Type': 'application/json',
          ...request.headers
        }
      }

      // 添加请求体
      if (request.body && ['POST', 'PUT', 'PATCH'].includes(request.method.toUpperCase())) {
        fetchConfig.body = typeof request.body === 'string' 
          ? request.body 
          : JSON.stringify(request.body)
      }

      // 构建URL（包含查询参数）
      let url = request.url
      if (request.params && Object.keys(request.params).length > 0) {
        const searchParams = new URLSearchParams()
        Object.entries(request.params).forEach(([key, value]) => {
          searchParams.append(key, String(value))
        })
        url += (url.includes('?') ? '&' : '?') + searchParams.toString()
      }

      // 发送请求
      const response = await fetch(url, fetchConfig)
      const data = await response.json()
      const endTime = Date.now()

      return {
        statusCode: response.status,
        data,
        headers: Object.fromEntries(response.headers.entries()),
        responseTime: endTime - startTime,
        isMocked: false
      }
    } catch (error) {
      console.error('真实接口请求失败:', error)
      throw error
    }
  }

  /**
   * 批量测试Mock匹配
   */
  public testMockMatching(apiId: string, testRequests: ApiRequest[]): Array<{
    request: ApiRequest
    matchResult: MockMatchResult
    timestamp: string
    executionTime: number
  }> {
    const mocks = this.getEnabledMocks(apiId)
    
    return testRequests.map(request => {
      const matchResult = this.findMatchingMock(mocks, request)
      
      return {
        request,
        matchResult,
        timestamp: new Date().toISOString(),
        executionTime: 0 // 这里只是匹配测试，不实际执行
      }
    })
  }

  /**
   * 清除API的Mock配置
   */
  public clearMocks(apiId: string): void {
    this.mockConfigs.delete(apiId)
  }

  /**
   * 清除所有Mock配置
   */
  public clearAllMocks(): void {
    this.mockConfigs.clear()
  }

  /**
   * 获取Mock统计信息
   */
  public getMockStats(apiId: string): {
    totalMocks: number
    enabledMocks: number
    disabledMocks: number
    mocksByPriority: Record<number, number>
  } {
    const mocks = this.getMocks(apiId)
    const enabled = mocks.filter(m => m.enabled)
    const disabled = mocks.filter(m => !m.enabled)
    
    const mocksByPriority: Record<number, number> = {}
    mocks.forEach(mock => {
      mocksByPriority[mock.priority] = (mocksByPriority[mock.priority] || 0) + 1
    })

    return {
      totalMocks: mocks.length,
      enabledMocks: enabled.length,
      disabledMocks: disabled.length,
      mocksByPriority
    }
  }
}

// 导出单例实例
export const mockService = MockService.getInstance()

// 导出工具函数
export const MockUtils = {
  /**
   * 验证Mock配置
   */
  validateMockConfig(mock: MockConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!mock.name || mock.name.trim() === '') {
      errors.push('Mock名称不能为空')
    }

    if (mock.priority < 1 || mock.priority > 100) {
      errors.push('优先级必须在1-100之间')
    }

    if (mock.statusCode !== undefined && (mock.statusCode < 100 || mock.statusCode > 599)) {
      errors.push('状态码必须在100-599之间')
    }

    if (mock.delay && (mock.delay < 0 || mock.delay > 30000)) {
      errors.push('延迟时间必须在0-30000ms之间')
    }

    // 验证匹配条件
    if (mock.matchConditions) {
      mock.matchConditions.forEach((condition, index) => {
        if (!condition.field || condition.field.trim() === '') {
          errors.push(`匹配条件${index + 1}的字段路径不能为空`)
        }
        if (!condition.operator) {
          errors.push(`匹配条件${index + 1}的操作符不能为空`)
        }
        if (condition.value === undefined || condition.value === null) {
          errors.push(`匹配条件${index + 1}的期望值不能为空`)
        }
      })
    }

    return {
      valid: errors.length === 0,
      errors
    }
  },

  /**
   * 生成Mock配置模板
   */
  generateMockTemplate(apiInfo: { method: string; url: string }): Partial<MockConfig> {
    return {
      name: `${apiInfo.method} ${apiInfo.url} Mock`,
      description: '自动生成的Mock配置模板',
      enabled: true,
      priority: 1,
      statusCode: 200,
      delay: 100,
      matchConditions: [],
      responseData: {
        code: 200,
        message: '操作成功',
        data: {}
      }
    }
  }
}