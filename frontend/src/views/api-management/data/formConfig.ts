/**
 * API管理页面表单配置
 */

// 选项接口定义
export interface SelectOption {
  label: string
  value: string
}

// 表单数据接口定义
export interface ApiFormData {
  id: number | null
  name: string
  serviceName: string
  moduleId: string
  version: string
  method: string
  protocol: string
  url: string
  description: string
  headers: HeaderItem[]
  parameters: ParameterItem[]
}

// 请求头接口定义
export interface HeaderItem {
  key: string
  value: string
}

// 参数接口定义
export interface ParameterItem {
  name: string
  type: string
  required: boolean
  description: string
}

// 表单验证规则接口定义
export interface FormRule {
  required?: boolean
  message: string
  trigger: string
}

export interface FormRules {
  [key: string]: FormRule[]
}

// HTTP方法选项
export const httpMethods: SelectOption[] = [
  { label: 'POST', value: 'POST' },
  { label: 'GET', value: 'GET' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' },
  { label: 'PATCH', value: 'PATCH' }
]

// 通信协议选项
export const protocolOptions: SelectOption[] = [
  { label: 'HTTPS', value: 'https' },
  { label: 'HTTP', value: 'http' }
]

// 参数类型选项
export const parameterTypes: SelectOption[] = [
  { label: 'String', value: 'string' },
  { label: 'Number', value: 'number' },
  { label: 'Boolean', value: 'boolean' },
  { label: 'Object', value: 'object' },
  { label: 'Array', value: 'array' }
]

// 表单验证规则
export const formRules: FormRules = {
  name: [
    { required: true, message: '请输入API名称', trigger: 'blur' }
  ],
  serviceName: [
    { required: true, message: '请输入服务名称', trigger: 'blur' }
  ],
  moduleId: [
    { required: true, message: '请选择服务模块', trigger: 'change' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  protocol: [
    { required: true, message: '请选择通信协议', trigger: 'change' }
  ],
  url: [
    { required: true, message: '请输入URL', trigger: 'blur' }
  ]
}

// 默认表单数据
export const defaultFormData: ApiFormData = {
  id: null,
  name: '',
  serviceName: '',
  moduleId: '',
  version: '1.0.0',
  method: 'POST',
  protocol: 'https',
  url: '',
  description: '',
  headers: [],
  parameters: []
}

// 默认请求头
export const defaultHeader: HeaderItem = {
  key: '',
  value: ''
}

// 默认参数
export const defaultParameter: ParameterItem = {
  name: '',
  type: 'string',
  required: false,
  description: ''
}