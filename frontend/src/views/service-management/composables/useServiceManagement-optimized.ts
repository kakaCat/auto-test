import { ref, computed, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useServiceStoreOptimized } from '@/stores/service-optimized'

/**
 * 服务管理组合式函数 - 优化版
 * 适配新的数据库结构：自增ID主键 + UUID业务标识符
 */
export function useServiceManagementOptimized() {
  const store = useServiceStoreOptimized()
  
  // ==================== 响应式状态 ====================
  
  // 搜索表单
  const searchForm = reactive({
    keyword: '',
    category: '',
    enabled: null as boolean | null,
    system_id: null as number | null,
    module_type: '',
    tags: [] as string[]
  })
  
  // 分页配置
  const pagination = reactive({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    pageSizeOptions: ['10', '20', '50', '100']
  })
  
  // 表格选择
  const selectedRowKeys = ref<number[]>([])
  const selectedRows = ref<any[]>([])
  
  // 对话框状态
  const dialogVisible = ref(false)
  const dialogMode = ref<'create' | 'edit' | 'view'>('create')
  const dialogTitle = computed(() => {
    const modeMap = {
      create: '创建',
      edit: '编辑',
      view: '查看'
    }
    return `${modeMap[dialogMode.value]}${currentEntityType.value === 'system' ? '系统' : '模块'}`
  })
  
  // 当前操作的实体类型
  const currentEntityType = ref<'system' | 'module'>('system')
  
  // 当前编辑的实体
  const currentEntity = ref<any>(null)
  
  // 表单数据
  const systemFormData = reactive({
    id: null as string | null,
    name: '',
    description: '',
    icon: 'el-icon-menu',
    category: 'custom',
    enabled: true,
    order_index: 0,
    url: '',
    metadata: {}
  })
  
  const moduleFormData = reactive({
    id: null as string | null,
    system_id: null as string | null,
    name: '',
    description: '',
    icon: 'el-icon-service',
    path: '',
    method: 'GET',
    enabled: true,
    version: '1.0.0',
    module_type: 'GENERAL',
    tags: [] as string[],
    config: {},
    order_index: 0
  })
  
  // ==================== 计算属性 ====================
  
  // 过滤后的系统列表
  const filteredSystems = computed(() => {
    let systems = store.systemsList
    
    // 关键词搜索
    if (searchForm.keyword) {
      const keyword = searchForm.keyword.toLowerCase()
      systems = systems.filter((system: any) => 
        system.name.toLowerCase().includes(keyword) ||
        system.description?.toLowerCase().includes(keyword) ||
        system.uuid.toLowerCase().includes(keyword)
      )
    }
    
    // 分类过滤
    if (searchForm.category) {
      systems = systems.filter((system: any) => system.category === searchForm.category)
    }
    
    // 状态过滤
    if (searchForm.enabled !== null) {
      systems = systems.filter((system: any) => system.enabled === searchForm.enabled)
    }
    
    return systems
  })
  
  // 过滤后的模块列表
  const filteredModules = computed(() => {
    let modules = store.modulesList
    
    // 关键词搜索
    if (searchForm.keyword) {
      const keyword = searchForm.keyword.toLowerCase()
      modules = modules.filter((module: any) => 
        module.name.toLowerCase().includes(keyword) ||
        module.description?.toLowerCase().includes(keyword) ||
        module.uuid.toLowerCase().includes(keyword)
      )
    }
    
    // 系统过滤
    if (searchForm.system_id) {
      modules = modules.filter((module: any) => module.system_id === searchForm.system_id)
    }
    
    // 模块类型过滤
    if (searchForm.module_type) {
      modules = modules.filter((module: any) => module.module_type === searchForm.module_type)
    }
    
    // 状态过滤
    if (searchForm.enabled !== null) {
      modules = modules.filter((module: any) => module.enabled === searchForm.enabled)
    }
    
    return modules
  })
  
  // 分页后的数据
  const paginatedData = computed(() => {
    const data = currentEntityType.value === 'system' ? filteredSystems.value : filteredModules.value
    const start = (pagination.current - 1) * pagination.pageSize
    const end = start + pagination.pageSize
    
    pagination.total = data.length
    
    return data.slice(start, end)
  })
  
  // 系统选项（用于模块表单）
  const systemOptions = computed(() => 
    store.enabledSystems.map((system: any) => ({
      label: system.name,
      value: system.id,
      uuid: system.uuid
    }))
  )
  
  // ==================== 方法 ====================
  
  // 搜索
  const handleSearch = () => {
    pagination.current = 1
    loadData()
  }
  
  // 重置搜索
  const handleResetSearch = () => {
    Object.assign(searchForm, {
      keyword: '',
      category: '',
      enabled: null,
      system_id: null,
      module_type: '',
      tags: []
    })
    pagination.current = 1
    loadData()
  }
  
  // 分页变化
  const handlePageChange = (page: number, pageSize?: number) => {
    pagination.current = page
    if (pageSize) {
      pagination.pageSize = pageSize
    }
    loadData()
  }
  
  // 表格选择变化
  const handleSelectionChange = (keys: number[], rows: any[]) => {
    selectedRowKeys.value = keys
    selectedRows.value = rows
  }
  
  // 切换实体类型
  const switchEntityType = (type: 'system' | 'module') => {
    currentEntityType.value = type
    selectedRowKeys.value = []
    selectedRows.value = []
    pagination.current = 1
    loadData()
  }
  
  // 加载数据
  const loadData = async () => {
    try {
      if (currentEntityType.value === 'system') {
        await store.fetchSystems({
          page: pagination.current,
          page_size: pagination.pageSize,
          ...searchForm
        })
      } else {
        await store.fetchModules({
          page: pagination.current,
          page_size: pagination.pageSize,
          ...searchForm
        })
      }
    } catch (error) {
      console.error('加载数据失败:', error)
    }
  }
  
  // 刷新数据
  const refreshData = () => {
    loadData()
    store.fetchStatistics()
  }
  
  // ==================== 对话框操作 ====================
  
  // 打开创建对话框
  const openCreateDialog = (type: 'system' | 'module') => {
    currentEntityType.value = type
    dialogMode.value = 'create'
    currentEntity.value = null
    resetFormData()
    dialogVisible.value = true
  }
  
  // 打开编辑对话框
  const openEditDialog = (entity: any) => {
    currentEntityType.value = 'system_id' in entity ? 'module' : 'system'
    dialogMode.value = 'edit'
    currentEntity.value = entity
    fillFormData(entity)
    dialogVisible.value = true
  }
  
  // 打开查看对话框
  const openViewDialog = (entity: any) => {
    currentEntityType.value = 'system_id' in entity ? 'module' : 'system'
    dialogMode.value = 'view'
    currentEntity.value = entity
    fillFormData(entity)
    dialogVisible.value = true
  }
  
  // 关闭对话框
  const closeDialog = () => {
    dialogVisible.value = false
    currentEntity.value = null
    resetFormData()
  }
  
  // 重置表单数据
  const resetFormData = () => {
    if (currentEntityType.value === 'system') {
      Object.assign(systemFormData, {
        id: null,
        name: '',
        description: '',
        icon: 'el-icon-menu',
        category: 'custom',
        enabled: true,
        order_index: 0,
        url: '',
        metadata: {}
      })
    } else {
      Object.assign(moduleFormData, {
        id: null,
        system_id: null,
        name: '',
        description: '',
        icon: 'el-icon-service',
        path: '',
        method: 'GET',
        enabled: true,
        version: '1.0.0',
        module_type: 'GENERAL',
        tags: [],
        config: {},
        order_index: 0
      })
    }
  }
  
  // 填充表单数据
  const fillFormData = (entity: any) => {
    if (currentEntityType.value === 'system') {
      Object.assign(systemFormData, {
        id: entity.uuid,
        name: entity.name,
        description: entity.description || '',
        icon: entity.icon,
        category: entity.category,
        enabled: entity.enabled,
        order_index: entity.order_index,
        url: entity.url,
        metadata: entity.metadata || {}
      })
    } else {
      Object.assign(moduleFormData, {
        id: entity.uuid,
        system_id: entity.system_uuid,
        name: entity.name,
        description: entity.description || '',
        icon: entity.icon,
        path: entity.path,
        method: entity.method,
        enabled: entity.enabled,
        version: entity.version,
        module_type: entity.module_type,
        tags: entity.tags || [],
        config: entity.config || {},
        order_index: entity.order_index
      })
    }
  }
  
  // 提交表单
  const handleSubmit = async () => {
    try {
      if (dialogMode.value === 'create') {
        if (currentEntityType.value === 'system') {
          await store.createSystem(systemFormData)
        } else {
          await store.createModule(moduleFormData)
        }
      } else if (dialogMode.value === 'edit' && currentEntity.value) {
        if (currentEntityType.value === 'system') {
          await store.updateSystem(currentEntity.value.id, systemFormData)
        } else {
          await store.updateModule(currentEntity.value.id, moduleFormData)
        }
      }
      
      closeDialog()
      refreshData()
    } catch (error) {
      console.error('提交失败:', error)
    }
  }
  
  // ==================== 操作方法 ====================
  
  // 删除单个实体
  const handleDelete = async (entity: any) => {
    try {
      const entityType = 'system_id' in entity ? '模块' : '系统'
      
      await ElMessageBox.confirm(
        `确定要删除${entityType}"${entity.name}"吗？此操作不可恢复。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      if ('system_id' in entity) {
        await store.deleteModule(entity.id)
      } else {
        await store.deleteSystem(entity.id)
      }
      
      refreshData()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
      }
    }
  }
  
  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请选择要删除的项目')
      return
    }
    
    try {
      const entityType = currentEntityType.value === 'system' ? '系统' : '模块'
      
      await ElMessageBox.confirm(
        `确定要删除选中的 ${selectedRows.value.length} 个${entityType}吗？此操作不可恢复。`,
        '确认批量删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 并行删除
      const deletePromises = selectedRows.value.map((entity: any) => {
        if ('system_id' in entity) {
          return store.deleteModule(entity.id)
        } else {
          return store.deleteSystem(entity.id)
        }
      })
      
      await Promise.all(deletePromises)
      
      selectedRowKeys.value = []
      selectedRows.value = []
      refreshData()
      
      ElMessage.success(`成功删除 ${selectedRows.value.length} 个${entityType}`)
    } catch (error) {
      if (error !== 'cancel') {
        console.error('批量删除失败:', error)
      }
    }
  }
  
  // 切换状态
  const handleToggleStatus = async (entity: any) => {
    try {
      const newStatus = !entity.enabled
      
      if ('system_id' in entity) {
        await store.updateModuleStatus(entity.id, newStatus)
      } else {
        await store.updateSystemStatus(entity.id, newStatus)
      }
      
      // 更新本地状态
      entity.enabled = newStatus
    } catch (error) {
      console.error('切换状态失败:', error)
    }
  }
  
  // 批量切换状态
  const handleBatchToggleStatus = async (enabled: boolean) => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请选择要操作的项目')
      return
    }
    
    try {
      const entityType = currentEntityType.value === 'system' ? '系统' : '模块'
      const action = enabled ? '启用' : '禁用'
      
      // 并行更新状态
      const updatePromises = selectedRows.value.map((entity: any) => {
        if ('system_id' in entity) {
          return store.updateModuleStatus(entity.id, enabled)
        } else {
          return store.updateSystemStatus(entity.id, enabled)
        }
      })
      
      await Promise.all(updatePromises)
      
      // 更新本地状态
      selectedRows.value.forEach((entity: any) => {
        entity.enabled = enabled
      })
      
      ElMessage.success(`成功${action} ${selectedRows.value.length} 个${entityType}`)
    } catch (error) {
      console.error('批量切换状态失败:', error)
    }
  }
  
  // ==================== 生命周期 ====================
  
  onMounted(() => {
    // 初始化数据
    store.initialize()
    loadData()
  })
  
  // 监听搜索表单变化
  watch(
    () => searchForm,
    () => {
      pagination.current = 1
      loadData()
    },
    { deep: true }
  )
  
  // ==================== 返回接口 ====================
  
  return {
    // Store
    store,
    
    // 响应式状态
    searchForm,
    pagination,
    selectedRowKeys,
    selectedRows,
    dialogVisible,
    dialogMode,
    dialogTitle,
    currentEntityType,
    currentEntity,
    systemFormData,
    moduleFormData,
    
    // 计算属性
    filteredSystems,
    filteredModules,
    paginatedData,
    systemOptions,
    
    // 搜索和分页
    handleSearch,
    handleResetSearch,
    handlePageChange,
    handleSelectionChange,
    switchEntityType,
    loadData,
    refreshData,
    
    // 对话框操作
    openCreateDialog,
    openEditDialog,
    openViewDialog,
    closeDialog,
    resetFormData,
    fillFormData,
    handleSubmit,
    
    // 实体操作
    handleDelete,
    handleBatchDelete,
    handleToggleStatus,
    handleBatchToggleStatus
  }
}

// 兼容性函数 - 保持原有接口不变
export function useServiceManagement() {
  return useServiceManagementOptimized()
}