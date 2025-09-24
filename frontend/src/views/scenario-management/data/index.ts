/**
 * 用例场景管理页面配置统一导出
 */

// 表单配置
export {
  executionTypeOptions,
  scenarioStatusOptions,
  defaultSearchForm,
  defaultPagination,
  defaultStats,
  defaultCreateForm,
  createFormRules
} from './formConfig'

// 表格配置
export {
  scenarioTableColumns,
  getTypeLabel,
  getTypeColor,
  getStatusLabel,
  getStatusColor,
  getProgressColor,
  formatTime
} from './tableColumns'

// 类型定义导出
export type {
  SelectOption,
  SearchForm,
  PaginationConfig,
  StatsData,
  CreateForm,
  FormRule,
  FormRules
} from './formConfig'

export type {
  ScenarioItem,
  TableHandlers,
  ColumnTemplateParams,
  TableColumn
} from './tableColumns'