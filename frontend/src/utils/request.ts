/**
 * HTTP请求工具模块
 * 
 * 功能说明：
 * - 基于axios封装的HTTP请求工具
 * - 提供统一的请求/响应拦截器
 * - 支持认证、错误处理、加载状态管理
 * - 提供文件上传下载功能
 * 
 * 技术特性：
 * - 自动token管理和认证
 * - 统一错误处理和用户提示
 * - 请求追踪和日志记录
 * - 文件操作支持
 * - 请求取消机制
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @since 2024
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, CancelTokenSource, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

/**
 * API响应数据结构
 */
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}

/**
 * 请求配置选项
 */
export interface RequestConfig extends AxiosRequestConfig {
  skipAuth?: boolean
  skipLoading?: boolean
  skipErrorHandler?: boolean
}

/**
 * 文件下载参数
 */
export interface DownloadParams {
  [key: string]: any
}

/**
 * 请求方法接口
 */
export interface RequestMethods {
  get<T = any>(url: string, params?: any, config?: RequestConfig): Promise<ApiResponse<T>>
  post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>
  put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>
  delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>>
  patch<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>>
  upload<T = any>(url: string, formData: FormData, config?: RequestConfig): Promise<ApiResponse<T>>
  download(url: string, params?: DownloadParams, filename?: string): Promise<void>
}

/**
 * 创建axios实例
 * 
 * 配置说明：
 * - baseURL: API基础路径，支持环境变量配置
 * - timeout: 请求超时时间（30秒）
 * - headers: 默认请求头，设置JSON内容类型
 */
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 
 * 功能职责：
 * - 在请求发送前进行统一处理
 * - 添加认证信息和请求追踪
 * - 管理全局加载状态
 * - 处理请求错误
 */
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const appStore = useAppStore()
    
    /**
     * 显示全局加载状态
     * 用于在请求期间显示loading指示器
     */
    if (!(config as RequestConfig).skipLoading) {
      appStore.setLoading(true)
    }
    
    /**
     * 添加认证token
     * 从本地存储获取token并添加到请求头
     * 使用Bearer Token认证方式
     */
    if (!(config as RequestConfig).skipAuth) {
      const token = localStorage.getItem('token')
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    /**
     * 添加请求ID用于追踪
     * 生成唯一请求标识，便于日志追踪和调试
     */
    if (config.headers) {
      config.headers['X-Request-ID'] = generateRequestId()
    }
    
    return config
  },
  /**
   * 请求错误处理
   * 在请求发送失败时执行
   * 
   * @param {AxiosError} error - 请求错误对象
   * @returns {Promise} 拒绝的Promise
   */
  (error: AxiosError) => {
    const appStore = useAppStore()
    // 关闭加载状态
    appStore.setLoading(false)
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 
 * 功能职责：
 * - 统一处理响应数据
 * - 管理加载状态
 * - 处理业务错误
 * - 支持文件下载响应
 */
service.interceptors.response.use(
  /**
   * 响应成功处理
   * 
   * @param {AxiosResponse} response - axios响应对象
   * @returns {any|Promise} 处理后的数据或原始响应
   */
  (response: AxiosResponse) => {
    const appStore = useAppStore()
    // 关闭全局加载状态
    if (!(response.config as RequestConfig).skipLoading) {
      appStore.setLoading(false)
    }
    
    const { data } = response
    
    /**
     * 文件下载响应处理
     * 对于blob类型的响应（文件下载），直接返回原始响应
     */
    if (response.config.responseType === 'blob') {
      return response
    }
    
    /**
     * 业务状态码检查
     * 检查API返回的业务状态，处理业务层面的错误
     */
    if (data.success === false) {
      if (!(response.config as RequestConfig).skipErrorHandler) {
        ElMessage.error(data.message || '请求失败')
      }
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    
    // 返回业务数据
    return data
  },
  /**
   * 响应错误处理
   * 统一处理HTTP错误和网络错误
   * 
   * @param {AxiosError} error - 错误对象
   * @returns {Promise} 拒绝的Promise
   */
  (error: AxiosError) => {
    const appStore = useAppStore()
    // 关闭全局加载状态
    if (!(error.config as RequestConfig)?.skipLoading) {
      appStore.setLoading(false)
    }
    
    console.error('Response error:', error)
    
    let message = '网络错误'
    
    /**
     * HTTP响应错误处理
     * 根据不同的HTTP状态码提供相应的错误信息
     */
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
      case 400:
        message = (data as any)?.message || '请求参数错误'
        break
      case 401:
        message = '未授权，请重新登录'
        /**
         * 认证失效处理
         * 清除本地认证信息并重定向到登录页
         */
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        // 清除用户信息
        window.location.href = '/login'
        break
      case 403:
        message = '拒绝访问'
        break
      case 404:
        message = '请求的资源不存在'
        break
      case 500:
        message = '服务器内部错误'
        break
      case 502:
        message = '网关错误'
        break
      case 503:
        message = '服务不可用'
        break
      case 504:
        message = '网关超时'
        break
      default:
        message = (data as any)?.message || `连接错误${status}`
      }
    } else if (error.code === 'ECONNABORTED') {
      // 请求超时错误
      message = '请求超时'
    } else if (error.message) {
      // 其他网络错误
      message = error.message
    }
    
    // 显示错误提示
    if (!(error.config as RequestConfig)?.skipErrorHandler) {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

/**
 * 生成请求ID
 * 用于请求追踪和日志记录
 * 
 * 算法说明：
 * - 使用时间戳转36进制 + 随机数转36进制
 * - 确保在短时间内生成的ID具有唯一性
 * 
 * @returns {string} 唯一的请求ID
 */
function generateRequestId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 封装常用请求方法
 * 提供简化的API调用接口
 * 
 * 特性说明：
 * - 支持所有标准HTTP方法
 * - 统一的参数格式
 * - 自动应用拦截器
 * - 支持文件操作
 */
export const request: RequestMethods = {
  /**
   * GET请求
   * 用于数据查询和获取
   * 
   * @param {string} url - 请求URL
   * @param {any} params - 查询参数
   * @param {RequestConfig} config - axios配置选项
   * @returns {Promise} 请求Promise
   */
  get<T = any>(url: string, params: any = {}, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return service.get(url, { params, ...config })
  },
  
  /**
   * POST请求
   * 用于数据创建和提交
   * 
   * @param {string} url - 请求URL
   * @param {any} data - 请求体数据
   * @param {RequestConfig} config - axios配置选项
   * @returns {Promise} 请求Promise
   */
  post<T = any>(url: string, data: any = {}, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return service.post(url, data, config)
  },
  
  /**
   * PUT请求
   * 用于数据更新（完整替换）
   * 
   * @param {string} url - 请求URL
   * @param {any} data - 请求体数据
   * @param {RequestConfig} config - axios配置选项
   * @returns {Promise} 请求Promise
   */
  put<T = any>(url: string, data: any = {}, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return service.put(url, data, config)
  },
  
  /**
   * DELETE请求
   * 用于数据删除
   * 
   * @param {string} url - 请求URL
   * @param {RequestConfig} config - axios配置选项
   * @returns {Promise} 请求Promise
   */
  delete<T = any>(url: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return service.delete(url, config)
  },
  
  /**
   * PATCH请求
   * 用于数据部分更新
   * 
   * @param {string} url - 请求URL
   * @param {any} data - 请求体数据
   * @param {RequestConfig} config - axios配置选项
   * @returns {Promise} 请求Promise
   */
  patch<T = any>(url: string, data: any = {}, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return service.patch(url, data, config)
  },
  
  /**
   * 文件上传
   * 支持单文件和多文件上传
   * 
   * @param {string} url - 上传URL
   * @param {FormData} formData - 包含文件的FormData对象
   * @param {RequestConfig} config - axios配置选项
   * @returns {Promise} 上传Promise
   */
  upload<T = any>(url: string, formData: FormData, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return service.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  /**
   * 文件下载
   * 支持各种文件类型的下载
   * 
   * 实现原理：
   * 1. 发送blob类型请求获取文件数据
   * 2. 创建临时下载链接
   * 3. 触发浏览器下载
   * 4. 清理临时资源
   * 
   * @param {string} url - 下载URL
   * @param {DownloadParams} params - 查询参数
   * @param {string} filename - 指定文件名（可选）
   * @returns {Promise} 下载Promise
   */
  download(url: string, params: DownloadParams = {}, filename: string = ''): Promise<void> {
    return service.get(url, {
      params,
      responseType: 'blob'
    }).then((response: AxiosResponse) => {
      // 创建Blob对象
      const blob = new Blob([response.data])
      // 创建临时下载URL
      const downloadUrl = window.URL.createObjectURL(blob)
      // 创建隐藏的下载链接
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || getFilenameFromResponse(response)
      // 触发下载
      document.body.appendChild(link)
      link.click()
      // 清理DOM和内存
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

/**
 * 从响应头获取文件名
 * 解析Content-Disposition头部获取服务器指定的文件名
 * 
 * @param {AxiosResponse} response - axios响应对象
 * @returns {string} 文件名，默认为'download'
 */
function getFilenameFromResponse(response: AxiosResponse): string {
  const contentDisposition = response.headers['content-disposition']
  if (contentDisposition) {
    // 匹配filename参数
    const matches = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (matches && matches[1]) {
      // 移除引号
      return matches[1].replace(/['"]/g, '')
    }
  }
  return 'download'
}

/**
 * 请求取消token管理
 * 用于取消正在进行的请求
 * 
 * 使用示例：
 * const source = cancelTokenSource()
 * request.get('/api/data', {}, { cancelToken: source.token })
 * source.cancel('操作被用户取消')
 */
export const cancelTokenSource: () => CancelTokenSource = axios.CancelToken.source

export default service