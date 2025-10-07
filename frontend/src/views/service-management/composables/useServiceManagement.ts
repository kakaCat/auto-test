/**
 * 服务管理业务逻辑组合式函数
 */

import { ref, reactive, computed, watch, nextTick } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { debounce } from '../data'
import { useServiceStore } from '@/stores/service'
import { systemApi, moduleApi } from '@/api/unified-api'

// 直接使用统一API
const systemApiProxy = systemApi
const moduleApiProxy = moduleApi

import type {
  System,
  Module,
  SystemFormData,
  ModuleFormData,
  PaginationConfig,
  TreeTableNode,
  SystemCategory
} from '../types/index'

import {
  defaultSearchForm,
  defaultPagination,
  defaultSystemForm,
  defaultModuleForm
} from '../data'

// 其他导入
interface ExtendedSearchFormData {
  name: string
  category: SystemCategory | undefined
  enabled: boolean | undefined
}

export interface UseServiceManagementReturn {
  // 状态
  systems: Ref<System[]>
  loading: Ref<boolean>
  expandedRows: Ref<string[]>
  selectedSystemId: Ref<number | null>
  error: Ref<string | null>
  
  // 对话框状态
  systemDialogVisible: Ref<boolean>
  moduleDialogVisible: Ref<boolean>
  systemDialogTitle: Ref<string>
  moduleDialogTitle: Ref<string>
  
  // 表单数据
  searchForm: ExtendedSearchFormData
  systemForm: SystemFormData
  moduleForm: ModuleFormData
  pagination: PaginationConfig
  
  // 计算属性
  filteredSystems: ComputedRef<System[]>
  treeTableData: ComputedRef<TreeTableNode[]>
  paginatedData: ComputedRef<TreeTableNode[]>
  
  // 方法
  handleExpandChange: (row: TreeTableNode, expandedRows: string[]) => void
  selectSystem: (systemId: number) => void
  showAddSystemDialog: () => void
  showAddModuleDialog: (systemId?: number) => void
  resetSystemForm: () => void
  resetModuleForm: () => void
  saveSystem: () => Promise<void>
  saveModule: () => Promise<void>
  handleSystemAction: (command: string) => Promise<void>
  handleModuleAction: (command: string) => Promise<any | void>
  handleCurrentChange: (page: number) => void
  handleSizeChange: (size: number) => void
  refreshData: () => Promise<void>
  clearError: () => void
  debouncedSearch: () => void
}

export const useServiceManagement = (): UseServiceManagementReturn => {
  const serviceStore = useServiceStore()
  
  // 状态管理
  const systems = ref<System[]>([])
  const loading = ref(false)
  const expandedRows = ref<string[]>([])
  const selectedSystemId = ref<number | null>(null)
  const error = ref<string | null>(null)
  
  // 对话框状态
  const systemDialogVisible = ref(false)
  const moduleDialogVisible = ref(false)
  const systemDialogTitle = ref('')
  const moduleDialogTitle = ref('')
  
  // 表单数据
  const searchForm = reactive({
    name: '',
    category: undefined,
    enabled: undefined
  })
  
  const systemForm = reactive(defaultSystemForm)
  const moduleForm = reactive(defaultModuleForm)
  const pagination = reactive(defaultPagination)
  
  // 防抖搜索
  const debouncedSearch = debounce(() => {
    // 搜索逻辑在计算属性中处理，这里可以添加额外的搜索逻辑
    pagination.currentPage = 1
    // 同步统一字段
    ;(pagination as any).page = 1
  }, 300)
  
  // 监听搜索表单变化
  watch(
    () => [searchForm.name, searchForm.category, searchForm.enabled],
    () => {
      debouncedSearch()
    },
    { deep: true }
  )
  
  // 计算属性
  const filteredSystems = computed(() => {
    let filtered = serviceStore.systemsList
    
    // 按名称过滤
    if (searchForm.name) {
      filtered = filtered.filter((system: System) => 
        (system.name || '').toLowerCase().includes(searchForm.name.toLowerCase())
      )
    }
    
    // 按分类过滤
    if (searchForm.category) {
      filtered = filtered.filter((system: System) => system.category === searchForm.category)
    }
    
    // 按启用状态过滤
    if (searchForm.enabled !== undefined) {
      filtered = filtered.filter((system: System) => system.enabled === searchForm.enabled)
    }
    
    return filtered
  })
  
  const treeTableData = computed(() => {
    return filteredSystems.value.map((system: System) => {
      const systemNode: TreeTableNode = {
        ...system,
        type: 'system',
        hasChildren: system.modules ? system.modules.length > 0 : false,
        children: []
      }
      
      // 如果系统有模块，添加模块作为子节点
      if (system.modules && system.modules.length > 0) {
        systemNode.children = system.modules.map((module: Module) => ({
          ...module,
          type: 'module',
          id: `module-${module.id}`,
          parentId: system.id,
          hasChildren: false
        }))
      }
      
      return systemNode
    })
  })
  
  const paginatedData = computed(() => {
    const data = treeTableData.value
    pagination.total = data.length
    // 兼容统一分页字段 page/size
    const page = (pagination as any).page ?? pagination.currentPage
    const size = (pagination as any).size ?? pagination.pageSize
    const start = (page - 1) * size
    const end = start + size
    
    return data.slice(start, end)
  })
  
  // 方法
  const handleExpandChange = (row: TreeTableNode, expandedRows: string[]): void => {
    if (row.type === 'system') {
      const isExpanded = expandedRows.includes(String(row.id))
      selectedSystemId.value = isExpanded ? row.id : null
    }
  }
  
  const selectSystem = (systemId: number): void => {
    selectedSystemId.value = systemId
  }
  
  const showAddSystemDialog = (): void => {
    systemDialogTitle.value = '新增管理系统'
    resetSystemForm()
    systemDialogVisible.value = true
  }
  
  const showAddModuleDialog = (systemId?: number): void => {
    moduleDialogTitle.value = '新增模块'
    resetModuleForm()
    if (systemId) {
      moduleForm.system_id = systemId
    } else if (selectedSystemId.value) {
      moduleForm.system_id = selectedSystemId.value
    }
    moduleDialogVisible.value = true
  }
  
  const resetSystemForm = (): void => {
    Object.assign(systemForm, defaultSystemForm)
  }
  
  const resetModuleForm = (): void => {
    Object.assign(moduleForm, defaultModuleForm)
  }
  
  const saveSystem = async (): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      // 准备保存数据
      const saveData = {
        name: systemForm.name,
        description: systemForm.description,
        icon: systemForm.icon,
        category: systemForm.category,
        enabled: systemForm.enabled,
        order_index: systemForm.order_index || 0,
        url: systemForm.url,
        metadata: systemForm.metadata || {}
      }
      
      if (systemForm.id) {
        // 编辑模式（后端期望数字ID，进行转换）
        const systemIdNum = Number(systemForm.id)
        await systemApiProxy.update(systemIdNum, saveData)
        ElMessage.success('系统更新成功')
      } else {
        // 新增模式
        await systemApiProxy.create(saveData)
        ElMessage.success('系统创建成功')
      }
      
      // 刷新数据
      await refreshData()
      
      systemDialogVisible.value = false
      resetSystemForm()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存系统失败'
      ElMessage.error('保存系统失败')
    } finally {
      loading.value = false
    }
  }
  
  const saveModule = async (): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      
      if (moduleForm.id) {
        // 编辑模式 - 不发送system_id字段
        const updateData: any = {
          name: moduleForm.name,
          description: moduleForm.description,
          path: moduleForm.path || '/'
        }
        
        // 处理tags字段 - 后端期望字符串，前端可能是数组
        if (moduleForm.tags) {
          const tagsUnknown: unknown = moduleForm.tags as unknown
          if (Array.isArray(tagsUnknown)) {
            updateData.tags = (tagsUnknown as string[]).join(',')
          } else if (typeof tagsUnknown === 'string') {
            updateData.tags = (tagsUnknown as string).split(',').map((s: string) => s.trim()).filter(Boolean).join(',')
          } else {
            updateData.tags = ''
          }
        }
        
        // 后端期望数字ID，进行转换
        const moduleIdNum = Number(moduleForm.id)
        await moduleApiProxy.update(moduleIdNum, updateData)
        ElMessage.success('模块更新成功')
      } else {
        // 新增模式 - 需要发送system_id字段
        const createData: any = {
          system_id: moduleForm.system_id,
          name: moduleForm.name,
          description: moduleForm.description,
          path: moduleForm.path || '/'
        }
        
        // 处理system_id - 后端期望数字，前端可能是字符串
        if (moduleForm.system_id) {
          createData.system_id = moduleForm.system_id
        }
        
        // 处理tags字段 - 后端期望字符串，前端可能是数组
        if (moduleForm.tags) {
          const tagsUnknown: unknown = moduleForm.tags as unknown
          if (Array.isArray(tagsUnknown)) {
            createData.tags = (tagsUnknown as string[]).join(',')
          } else if (typeof tagsUnknown === 'string') {
            createData.tags = (tagsUnknown as string).split(',').map((s: string) => s.trim()).filter(Boolean).join(',')
          } else {
            createData.tags = ''
          }
        }
        
        await moduleApiProxy.create(createData)
        ElMessage.success('模块创建成功')
      }
      
      // 刷新数据
      await refreshData()
      
      moduleDialogVisible.value = false
      resetModuleForm()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存模块失败'
      ElMessage.error('保存模块失败')
    } finally {
      loading.value = false
    }
  }
  
  const handleSystemAction = async (command: string): Promise<void> => {
    const [action, systemId] = command.split('-')
    const system = (serviceStore.systemsList as any[]).find((s: any) => s.id === systemId)
    
    if (!system) return
    
    switch (action) {
      case 'add':
        if (action === 'add' && command.includes('module')) {
          showAddModuleDialog(systemId)
        }
        break
      case 'edit':
        systemDialogTitle.value = '编辑管理系统'
        Object.assign(systemForm, {
          id: system.id,
          name: system.name,
          description: system.description,
          icon: system.icon,
          category: system.category,
          enabled: system.enabled,
          order_index: system.order_index,
          url: system.url,
          metadata: system.metadata
        })
        systemDialogVisible.value = true
        break
      case 'toggle':
        try {
          const newStatus = !system.enabled
          // 后端期望数字ID，进行转换
          const systemIdNum = Number(systemId)
          await systemApiProxy.toggleEnabled(systemIdNum, newStatus)
          
          // 更新本地状态
          system.enabled = newStatus
          
          ElMessage.success(`系统已${newStatus ? '启用' : '禁用'}`)
          
          // 刷新数据以确保状态同步
          await refreshData()
        } catch (error) {
          ElMessage.error('操作失败: ' + (error as Error).message)
        }
        break
      case 'delete':
        ElMessageBox.confirm(
          `确定要删除系统 "${system.name}" 吗？这将同时删除该系统下的所有模块。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          try {
            // TODO: 实现系统删除功能
            ElMessage.info('系统删除功能待实现')
          } catch (error) {
            ElMessage.error('删除失败: ' + (error as Error).message)
          }
        })
        break
    }
  }
  
  const handleModuleAction = async (command: string): Promise<any> => {
    const [action, moduleId] = command.split('-')
    let targetModule: Module | null = null
    let targetSystemId: string | null = null
    
    // 查找模块
    for (const system of (serviceStore.systemsList as any[])) {
      const module = system.modules?.find((m: any) => m.id === moduleId)
      if (module) {
        targetModule = module
        targetSystemId = system.id
        break
      }
    }
    
    if (!targetModule || !targetSystemId) return
    
    switch (action) {
      case 'view':
        ElMessage.info(`查看模块: ${targetModule.name}`)
        break
      case 'edit':
        moduleDialogTitle.value = '编辑模块'
        Object.assign(moduleForm, {
          id: targetModule.id,
          system_id: targetModule.system_id || targetSystemId,
          name: targetModule.name,
          description: targetModule.description,
          icon: targetModule.icon,
          path: targetModule.path,
          method: targetModule.method,
          enabled: targetModule.enabled,
          version: targetModule.version,
          module_type: targetModule.module_type,
          tags: targetModule.tags,
          config: targetModule.config,
          order_index: targetModule.order_index
        })
        moduleDialogVisible.value = true
        break
      case 'toggle':
        try {
          const newStatus = !targetModule.enabled
          // 后端期望数字ID，进行转换
          const moduleIdNum = Number(moduleId)
          const response = await moduleApiProxy.toggleEnabled(moduleIdNum, newStatus)
          
          // 更新本地状态
          targetModule.enabled = newStatus
          
          ElMessage.success(`模块已${newStatus ? '启用' : '禁用'}`)
          
          // 刷新数据以确保状态同步
          await refreshData()
          
          // 返回更新后的模块数据，供调用方更新selectedNode
          return response.data
        } catch (error) {
          ElMessage.error('操作失败: ' + (error as Error).message)
          throw error
        }
        break
      case 'delete':
        ElMessageBox.confirm(
          `确定要删除模块 "${targetModule.name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          try {
            // TODO: 实现模块删除功能
            ElMessage.info('模块删除功能待实现')
          } catch (error) {
            ElMessage.error('删除失败: ' + (error as Error).message)
          }
        })
        break
    }
  }
  
  const handleCurrentChange = (page: number): void => {
    pagination.currentPage = page
    // 同步统一字段
    ;(pagination as any).page = page
  }
  
  const handleSizeChange = (size: number): void => {
    pagination.pageSize = size
    pagination.currentPage = 1
    // 同步统一字段
    ;(pagination as any).size = size
    ;(pagination as any).page = 1
  }
  
  const refreshData = async (): Promise<void> => {
    try {
      loading.value = true
      error.value = null
      await serviceStore.loadSystems()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载数据失败'
      ElMessage.error('加载系统列表失败')
    } finally {
      loading.value = false
    }
  }
  
  const clearError = (): void => {
    error.value = null
  }
  
  return {
    // 状态
    systems,
    loading,
    expandedRows,
    selectedSystemId,
    error,
    
    // 对话框状态
    systemDialogVisible,
    moduleDialogVisible,
    systemDialogTitle,
    moduleDialogTitle,
    
    // 表单数据
    searchForm,
    systemForm,
    moduleForm,
    pagination,
    
    // 计算属性
    filteredSystems,
    treeTableData,
    paginatedData,
    
    // 方法
    handleExpandChange,
    selectSystem,
    showAddSystemDialog,
    showAddModuleDialog,
    resetSystemForm,
    resetModuleForm,
    saveSystem,
    saveModule,
    handleSystemAction,
    handleModuleAction,
    handleCurrentChange,
    handleSizeChange,
    refreshData,
    clearError,
    debouncedSearch
  }
}