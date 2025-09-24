/**
 * API管理页面数据配置统一导出
 */

// 导出表单配置
export {
  httpMethods,
  protocolOptions,
  parameterTypes,
  formRules,
  defaultFormData,
  defaultHeader,
  defaultParameter,
  type SelectOption,
  type ApiFormData,
  type HeaderItem,
  type ParameterItem,
  type FormRule,
  type FormRules
} from './formConfig'

// 导出表格配置
export {
  apiTableColumns,
  getMethodType,
  formatTime,
  type ApiItem,
  type TableHandlers,
  type ColumnTemplateParams,
  type TableColumn
} from './tableColumns'