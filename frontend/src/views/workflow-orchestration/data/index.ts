/**
 * 工作流编排页面配置统一导出
 */

// 表单配置
export {
  workflowStatusOptions,
  workflowCategoryOptions,
  defaultSearchForm,
  defaultPagination,
  defaultStats
} from './formConfig'

// 表格配置
export {
  workflowTableColumns,
  getStatusColor,
  getStatusLabel,
  getProgressColor,
  formatTime
} from './tableColumns'

// 模板配置
export {
  workflowTemplates
} from './templateConfig'

// 类型定义导出
export type {
  SelectOption,
  SearchForm,
  PaginationConfig,
  StatsData
} from './formConfig'

export type {
  WorkflowItem,
  TableHandlers,
  ColumnTemplateParams,
  TableColumn
} from './tableColumns'

export type {
  WorkflowTemplate
} from './templateConfig'