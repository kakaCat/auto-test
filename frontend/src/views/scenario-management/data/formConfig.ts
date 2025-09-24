/**
 * 用例场景管理页面表单配置
 */

// 选项接口定义
export interface SelectOption {
  label: string
  value: string
}

// 搜索表单接口定义
export interface SearchForm {
  keyword: string
  type: string
  status: string
}

// 分页配置接口定义
export interface PaginationConfig {
  page: number
  size: number
  total: number
}

// 统计数据接口定义
export interface StatsData {
  total: number
  active: number
  success: number
  failed: number
}

// 创建表单接口定义
export interface CreateForm {
  name: string
  type: string
  description: string
  tags: string[]
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

// 执行类型选项
export const executionTypeOptions: SelectOption[] = [
  { label: '顺序执行', value: 'sequential' },
  { label: '并行执行', value: 'parallel' },
  { label: '混合执行', value: 'mixed' }
]

// 场景状态选项
export const scenarioStatusOptions: SelectOption[] = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' },
  { label: '草稿', value: 'draft' }
]

// 搜索表单默认数据
export const defaultSearchForm: SearchForm = {
  keyword: '',
  type: '',
  status: ''
}

// 分页默认配置
export const defaultPagination: PaginationConfig = {
  page: 1,
  size: 20,
  total: 0
}

// 统计数据默认值
export const defaultStats: StatsData = {
  total: 0,
  active: 0,
  success: 0,
  failed: 0
}

// 创建表单默认数据
export const defaultCreateForm: CreateForm = {
  name: '',
  type: 'sequential',
  description: '',
  tags: []
}

// 创建表单验证规则
export const createFormRules: FormRules = {
  name: [
    { required: true, message: '请输入场景名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择执行类型', trigger: 'change' }
  ]
}