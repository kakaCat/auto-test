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
  status: string
  tags: string[]
  createdBy: string
  createdTimeRange: string[]
  isParametersSaved: boolean
}

// 分页配置接口定义
// 已移除分页配置，按方案采用无分页列表

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
  scenario_type: 'normal' | 'exception' | 'boundary' | 'security' | 'performance'
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
export const scenarioTypeOptions: SelectOption[] = [
  { label: '常规', value: 'normal' },
  { label: '异常', value: 'exception' },
  { label: '边界', value: 'boundary' },
  { label: '安全', value: 'security' },
  { label: '性能', value: 'performance' }
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
  status: '',
  tags: [],
  createdBy: '',
  createdTimeRange: [],
  isParametersSaved: false
}

// 分页默认配置
// 无分页：删除默认分页配置

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
  scenario_type: 'normal',
  description: '',
  tags: []
}

// 创建表单验证规则
export const createFormRules: FormRules = {
  name: [
    { required: true, message: '请输入场景名称', trigger: 'blur' }
  ],
  scenario_type: [
    { required: true, message: '请选择场景类型', trigger: 'change' }
  ]
}