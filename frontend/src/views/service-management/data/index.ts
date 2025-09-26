/**
 * 数据配置统一导出
 */

// 表单配置
export {
  systemCategoryOptions,
  enabledStatusOptions,
  moduleTypeOptions,
  httpMethodOptions,
  defaultSearchForm,
  defaultPagination,
  defaultSystemForm,
  defaultModuleForm,
  systemFormRules,
  moduleFormRules,
  commonTags,
  iconOptions
} from './formConfig'

// 工具函数
export {
  getSystemIcon,
  getModuleIcon,
  getCategoryTagType,
  formatFileSize,
  formatDate,
  generateId,
  deepClone,
  debounce,
  throttle,
  isValidUrl,
  isValidVersion,
  compareVersions
} from './utils'

// 类型定义
export type {
  BaseEntity,
  System,
  Module,
  SearchFormData,
  PaginationConfig,
  SystemFormData,
  ModuleFormData,
  FormRules,
  SelectOption,
  IconMap,
  TagTypeMap
} from '../types/index'

// 枚举导出
export {
  SystemCategory,
  ModuleType,
  HttpMethod
} from '../types/index'