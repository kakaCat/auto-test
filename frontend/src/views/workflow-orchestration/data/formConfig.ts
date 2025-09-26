/**
 * 工作流编排页面表单配置
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
  category: string
}

// 分页配置接口定义
export interface PaginationConfig {
  page: number
  size: number
  total: number
}



// 工作流状态选项
export const workflowStatusOptions: SelectOption[] = [
  { label: '运行中', value: 'running' },
  { label: '已停止', value: 'stopped' },
  { label: '草稿', value: 'draft' },
  { label: '已发布', value: 'published' }
]

// 工作流分类选项
export const workflowCategoryOptions: SelectOption[] = [
  { label: 'API测试', value: 'api-test' },
  { label: '数据处理', value: 'data-processing' },
  { label: '自动化部署', value: 'auto-deploy' },
  { label: '监控告警', value: 'monitoring' },
  { label: '数据同步', value: 'data-sync' },
  { label: '其他', value: 'other' }
]

// 搜索表单默认数据
export const defaultSearchForm: SearchForm = {
  keyword: '',
  status: '',
  category: ''
}

// 分页默认配置
export const defaultPagination: PaginationConfig = {
  page: 1,
  size: 20,
  total: 0
}