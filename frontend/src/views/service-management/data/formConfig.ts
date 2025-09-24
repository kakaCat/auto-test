/**
 * 表单配置和默认数据
 */

import {
  SystemCategory,
  ModuleType,
  HttpMethod
} from '../types'

import type {
  SelectOption,
  SearchFormData,
  PaginationConfig,
  SystemFormData,
  ModuleFormData,
  FormRules
} from '../types'

// 系统分类选项
export const systemCategoryOptions: SelectOption<SystemCategory>[] = [
  { value: SystemCategory.BACKEND, label: '后端服务' },
  { value: SystemCategory.FRONTEND, label: '前端应用' }
]

// 系统分类标签映射
export const SystemCategoryLabels: Record<SystemCategory, string> = {
  [SystemCategory.BACKEND]: '后端服务',
  [SystemCategory.FRONTEND]: '前端应用'
}

// 启用状态选项
export const enabledStatusOptions: SelectOption<boolean>[] = [
  { value: true, label: '已启用' },
  { value: false, label: '已禁用' }
]

// 模块类型选项
export const moduleTypeOptions: SelectOption<ModuleType>[] = [
  { value: ModuleType.GENERAL, label: '通用模块' },
  { value: ModuleType.API, label: 'API模块' },
  { value: ModuleType.FRONTEND, label: '前端模块' },
  { value: ModuleType.BACKEND, label: '后端模块' },
  { value: ModuleType.MONITORING, label: '监控模块' },
  { value: ModuleType.MANAGEMENT, label: '管理模块' }
]

// HTTP方法选项
export const httpMethodOptions: SelectOption<HttpMethod>[] = [
  { value: HttpMethod.GET, label: 'GET' },
  { value: HttpMethod.POST, label: 'POST' },
  { value: HttpMethod.PUT, label: 'PUT' },
  { value: HttpMethod.DELETE, label: 'DELETE' },
  { value: HttpMethod.PATCH, label: 'PATCH' }
]

// 搜索表单默认数据
export const defaultSearchForm: SearchFormData = {
  keyword: '',
  category: '',
  enabled: null
}

// 分页默认配置
export const defaultPagination: PaginationConfig = {
  currentPage: 1,
  pageSize: 10,
  total: 0,
  pageSizes: [10, 20, 50, 100]
}

// 系统表单默认数据
export const defaultSystemForm: SystemFormData = {
  id: null,
  name: '',
  description: '',
  icon: 'el-icon-menu',
  category: '',
  enabled: true,
  order_index: 0,
  url: 'http://localhost:8080',
  metadata: {}
}

// 模块表单默认数据
export const defaultModuleForm: ModuleFormData = {
  id: null,
  system_id: null,
  name: '',
  description: '',
  icon: 'el-icon-service',
  path: '/',
  method: HttpMethod.GET,
  enabled: true,
  version: '1.0.0',
  module_type: ModuleType.GENERAL,
  tags: [],
  config: {},
  order_index: 0
}

// 系统表单验证规则
export const systemFormRules: FormRules = {
  name: [
    { required: true, message: '请输入系统名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入系统描述', trigger: 'blur' },
    { max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择系统分类', trigger: 'change' }
  ],
  url: [
    { 
      pattern: /^https?:\/\/.+/, 
      message: 'URL格式不正确，必须以 http:// 或 https:// 开头', 
      trigger: 'blur' 
    }
  ]
}

// 模块表单验证规则
export const moduleFormRules: FormRules = {
  name: [
    { required: true, message: '请输入模块名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入模块描述', trigger: 'blur' },
    { max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入路由路径', trigger: 'blur' },
    { pattern: /^\//, message: '路由路径必须以 / 开头', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { 
      pattern: /^\d+\.\d+\.\d+$/, 
      message: '版本号格式不正确 (如: 1.0.0)', 
      trigger: 'blur' 
    }
  ],
  system_id: [
    { required: true, message: '请选择所属系统', trigger: 'change' }
  ]
}

// 常用标签
export const commonTags: string[] = [
  '用户', '订单', '支付', '权限', '监控', '日志', 
  '配置', '通知', '报表', '导入', '导出', '统计',
  '审核', '流程', '文档', '消息', '缓存', '搜索'
]

// 图标选项
export const iconOptions: SelectOption<string>[] = [
  { value: 'el-icon-menu', label: '菜单' },
  { value: 'el-icon-service', label: '服务' },
  { value: 'el-icon-setting', label: '设置' },
  { value: 'el-icon-user', label: '用户' },
  { value: 'el-icon-document', label: '文档' },
  { value: 'el-icon-connection', label: '连接' },
  { value: 'el-icon-monitor', label: '监控' },
  { value: 'el-icon-lock', label: '安全' },
  { value: 'el-icon-data-analysis', label: '分析' },
  { value: 'el-icon-folder', label: '文件夹' }
]

// 表单配置常量
export const FORM_CONFIG = {
  // 表单尺寸
  SIZE: 'default' as const,
  
  // 标签宽度
  LABEL_WIDTH: '100px',
  
  // 对话框宽度
  DIALOG_WIDTH: {
    SYSTEM: '600px',
    MODULE: '700px'
  },
  
  // 输入框最大长度
  MAX_LENGTH: {
    NAME: 50,
    DESCRIPTION: 200,
    URL: 500,
    PATH: 200,
    VERSION: 20
  },
  
  // 标签最大数量
  MAX_TAGS: 10
} as const