import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'
import { mockService } from './mockService'
import type { TestCase, TestExecutionResult, TestRequestConfig, TestExpectedResponse, TestExecutionConfig } from '@/types/test-case'
import type { MockConfig, MockMatchResult } from '@/types/mock'
import type { ApiRequest, ApiResponse } from './mockService'

export interface ApiTestRequest {
  method: string
  url: string
  headers?: Record<string, string>
  body?: any
  timeout?: number
}

export interface ApiTestResponse {
  statusCode: number
  headers: Record<string, string>
  body: any
  responseTime: number
  isMocked: boolean
  mockConfig?: MockConfig
}

export interface BatchTestResult {
  testCase: TestCase
  success: boolean
  result?: ApiTestResponse
  error?: string
  executedAt: string
  executionTime: number
}

export interface SimpleTestExecutionResult {
  testCaseId: string
  success: boolean
  statusCode: number
  responseTime: number
  executedAt: string
  executionTime: number
  isMocked: boolean
  mockConfig?: MockConfig
  response?: any
  error?: string
  validationErrors?: string[]
}

export class ApiTestService {
  constructor() {
    // 使用单例实例
  }

  /**
   * 执行单个API测试
   */
  async executeApiTest(
    request: ApiTestRequest,
    expectedResponse?: TestExpectedResponse,
    enableMock: boolean = true
  ): Promise<ApiTestResponse> {
    const startTime = Date.now()
    
    try {
      // 检查是否有匹配的Mock配置
      let mockResponse = null
      if (enableMock) {
        const apiRequest: ApiRequest = {
          method: request.method,
          url: request.url,
          headers: request.headers || {},
          body: request.body
        }
        
        // 使用mockService执行请求，它会自动处理Mock匹配
        mockResponse = await mockService.executeRequest('default', apiRequest)
        
        if (mockResponse.isMocked) {
          return {
            statusCode: mockResponse.statusCode,
            headers: mockResponse.headers || {},
            body: mockResponse.data,
            responseTime: mockResponse.responseTime,
            isMocked: true,
            mockConfig: undefined // mockService不直接返回mockConfig
          }
        }
      }

      // 执行真实API调用
      const axiosConfig: AxiosRequestConfig = {
        method: request.method.toLowerCase() as any,
        url: request.url,
        headers: request.headers,
        data: request.body,
        timeout: request.timeout || 30000,
        validateStatus: () => true // 不抛出状态码错误
      }

      const response: AxiosResponse = await axios(axiosConfig)
      
      return {
        statusCode: response.status,
        headers: response.headers as Record<string, string>,
        body: response.data,
        responseTime: Date.now() - startTime,
        isMocked: false
      }
    } catch (error: any) {
      throw new Error(`API测试执行失败: ${error.message}`)
    }
  }

  /**
   * 执行测试用例
   */
  async executeTestCase(testCase: TestCase, enableMock: boolean = true): Promise<SimpleTestExecutionResult> {
    const startTime = Date.now()
    
    try {
      // 构建请求
      const request: ApiTestRequest = {
        method: testCase.requestConfig.method,
        url: testCase.requestConfig.url,
        headers: testCase.requestConfig.headers,
        body: testCase.requestConfig.body,
        timeout: 30000 // 默认30秒超时
      }

      // 执行API测试
      const response = await this.executeApiTest(request, testCase.expectedResponse, enableMock)

      // 验证响应
      const validationResult = this.validateResponse(response, testCase.expectedResponse)

      const result: SimpleTestExecutionResult = {
        testCaseId: testCase.id,
        success: validationResult.success,
        statusCode: response.statusCode,
        responseTime: response.responseTime,
        executedAt: new Date().toISOString(),
        executionTime: Date.now() - startTime,
        isMocked: response.isMocked,
        mockConfig: response.mockConfig,
        response: response.body,
        validationErrors: validationResult.errors
      }

      return result
    } catch (error: any) {
      return {
        testCaseId: testCase.id,
        success: false,
        statusCode: 0,
        responseTime: 0,
        executedAt: new Date().toISOString(),
        executionTime: Date.now() - startTime,
        isMocked: false,
        error: error.message
      }
    }
  }

  /**
   * 批量执行测试用例
   */
  async executeBatchTests(
    testCases: TestCase[],
    enableMock: boolean = true,
    onProgress?: (completed: number, total: number) => void
  ): Promise<BatchTestResult[]> {
    const results: BatchTestResult[] = []
    
    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i]
      const startTime = Date.now()
      
      try {
        const executionResult = await this.executeTestCase(testCase, enableMock)
        
        results.push({
          testCase,
          success: executionResult.success,
          result: {
            statusCode: executionResult.statusCode,
            headers: {},
            body: executionResult.response,
            responseTime: executionResult.responseTime,
            isMocked: executionResult.isMocked,
            mockConfig: executionResult.mockConfig
          },
          executedAt: executionResult.executedAt,
          executionTime: executionResult.executionTime
        })
      } catch (error: any) {
        results.push({
          testCase,
          success: false,
          error: error.message,
          executedAt: new Date().toISOString(),
          executionTime: Date.now() - startTime
        })
      }

      // 报告进度
      if (onProgress) {
        onProgress(i + 1, testCases.length)
      }

      // 添加延迟避免过快请求
      if (i < testCases.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }

    return results
  }

  /**
   * 验证响应是否符合预期
   */
  private validateResponse(
    response: ApiTestResponse,
    expected: TestExpectedResponse
  ): { success: boolean; errors: string[] } {
    const errors: string[] = []

    // 验证状态码
    if (expected.statusCode && response.statusCode !== expected.statusCode) {
      errors.push(`状态码不匹配: 期望 ${expected.statusCode}, 实际 ${response.statusCode}`)
    }

    // 验证响应体
    if (expected.body) {
      try {
        const expectedBody = typeof expected.body === 'string' 
          ? JSON.parse(expected.body) 
          : expected.body
        
        const actualBody = typeof response.body === 'string'
          ? JSON.parse(response.body)
          : response.body

        const bodyValidation = this.validateJsonStructure(actualBody, expectedBody)
        if (!bodyValidation.success) {
          errors.push(...bodyValidation.errors)
        }
      } catch (error) {
        errors.push('响应体格式验证失败')
      }
    }

    return {
      success: errors.length === 0,
      errors
    }
  }

  /**
   * 验证JSON结构
   */
  private validateJsonStructure(
    actual: any,
    expected: any,
    path: string = 'root'
  ): { success: boolean; errors: string[] } {
    const errors: string[] = []

    if (typeof expected !== typeof actual) {
      errors.push(`${path}: 类型不匹配, 期望 ${typeof expected}, 实际 ${typeof actual}`)
      return { success: false, errors }
    }

    if (expected === null || actual === null) {
      if (expected !== actual) {
        errors.push(`${path}: 值不匹配, 期望 ${expected}, 实际 ${actual}`)
      }
      return { success: errors.length === 0, errors }
    }

    if (typeof expected === 'object' && !Array.isArray(expected)) {
      for (const key in expected) {
        if (!(key in actual)) {
          errors.push(`${path}.${key}: 缺少必需字段`)
        } else {
          const nestedValidation = this.validateJsonStructure(
            actual[key],
            expected[key],
            `${path}.${key}`
          )
          errors.push(...nestedValidation.errors)
        }
      }
    } else if (Array.isArray(expected) && Array.isArray(actual)) {
      if (expected.length > 0 && actual.length > 0) {
        // 验证数组第一个元素的结构
        const nestedValidation = this.validateJsonStructure(
          actual[0],
          expected[0],
          `${path}[0]`
        )
        errors.push(...nestedValidation.errors)
      }
    } else if (expected !== actual) {
      errors.push(`${path}: 值不匹配, 期望 ${expected}, 实际 ${actual}`)
    }

    return { success: errors.length === 0, errors }
  }

  /**
   * 保存测试结果
   */
  async saveTestResults(results: SimpleTestExecutionResult[]): Promise<void> {
    try {
      // 这里可以实现保存到本地存储或发送到后端
      const savedResults = localStorage.getItem('test-execution-results') || '[]'
      const existingResults = JSON.parse(savedResults)
      
      const newResults = [...existingResults, ...results]
      localStorage.setItem('test-execution-results', JSON.stringify(newResults))
    } catch (error) {
      console.error('保存测试结果失败:', error)
      throw new Error('保存测试结果失败')
    }
  }

  /**
   * 获取历史测试结果
   */
  getTestHistory(): SimpleTestExecutionResult[] {
    try {
      const savedResults = localStorage.getItem('test-execution-results') || '[]'
      return JSON.parse(savedResults)
    } catch (error) {
      console.error('获取测试历史失败:', error)
      return []
    }
  }

  /**
   * 清除测试历史
   */
  clearTestHistory(): void {
    localStorage.removeItem('test-execution-results')
  }
}

// 导出单例实例
export const apiTestService = new ApiTestService()