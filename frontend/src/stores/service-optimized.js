import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  systemApiOptimized, 
  moduleApiOptimized, 
  statsApiOptimized,
  dataTransformUtils 
} from '@/api/service-optimized'

/**
 * 服务管理Store - 优化版
 * 适配新的数据库结构：自增ID主键 + UUID业务标识符
 */
export const useServiceStoreOptimized = defineStore('serviceOptimized', () => {
  // ==================== 状态管理 ====================
  
  // 系统列表
  const systemsList = ref([])
  
  // 模块列表
  const modulesList = ref([])
  
  // 加载状态
  const loading = ref(false)
  const systemsLoading = ref(false)
  const modulesLoading = ref(false)
  
  // 错误状态
  const error = ref(null)
  
  // 选中状态
  const selectedSystemId = ref(null)
  const selectedModuleId = ref(null)
  
  // 统计信息
  const statistics = ref({
    systems: {},
    modules: {},
    overview: {}
  })
  
  // ==================== 计算属性 ====================
  
  // 启用的系统列表
  const enabledSystems = computed(() => 
    systemsList.value.filter(system => system.enabled)
  )
  
  // 启用的模块列表
  const enabledModules = computed(() => 
    modulesList.value.filter(module => module.enabled)
  )
  
  // 当前选中的系统
  const currentSystem = computed(() => 
    systemsList.value.find(system => system.id === selectedSystemId.value)
  )
  
  // 当前选中的模块
  const currentModule = computed(() => 
    modulesList.value.find(module => module.id === selectedModuleId.value)
  )
  
  // 按分类分组的系统
  const systemsByCategory = computed(() => {
    const grouped = {}
    systemsList.value.forEach(system => {
      const category = system.category || 'custom'
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(system)
    })
    return grouped
  })
  
  // 按系统分组的模块
  const modulesBySystem = computed(() => {
    const grouped = {}
    modulesList.value.forEach(module => {
      const systemId = module.system_id
      if (!grouped[systemId]) {
        grouped[systemId] = []
      }
      grouped[systemId].push(module)
    })
    return grouped
  })
  
  // ==================== 工具函数 ====================
  
  const setLoading = (value) => {
    loading.value = value
  }
  
  const setError = (errorMessage) => {
    error.value = errorMessage
    if (errorMessage) {
      ElMessage.error(errorMessage)
    }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  // ==================== 系统管理方法 ====================
  
  // 获取系统列表
  const fetchSystems = async (params = {}) => {
    systemsLoading.value = true
    clearError()
    
    try {
      const response = await systemApiOptimized.getList(params)
      
      if (response.success) {
        // 转换数据格式
        systemsList.value = dataTransformUtils.transformSystemsFromBackend(response.data || [])
        return systemsList.value
      } else {
        throw new Error(response.message || '获取系统列表失败')
      }
    } catch (error) {
      console.error('获取系统列表失败:', error)
      setError(error.message || '获取系统列表失败')
      throw error
    } finally {
      systemsLoading.value = false
    }
  }
  
  // 获取系统详情
  const fetchSystemDetail = async (systemId) => {
    setLoading(true)
    clearError()
    
    try {
      const response = await systemApiOptimized.getDetail(systemId)
      
      if (response.success) {
        const system = dataTransformUtils.transformSystemFromBackend(response.data)
        
        // 更新系统列表中的对应项
        const index = systemsList.value.findIndex(s => s.id === systemId)
        if (index !== -1) {
          systemsList.value[index] = system
        } else {
          systemsList.value.push(system)
        }
        
        return system
      } else {
        throw new Error(response.message || '获取系统详情失败')
      }
    } catch (error) {
      console.error('获取系统详情失败:', error)
      setError(error.message || '获取系统详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 创建系统
  const createSystem = async (systemData) => {
    setLoading(true)
    clearError()
    
    try {
      const backendData = dataTransformUtils.transformSystemToBackend(systemData)
      const response = await systemApiOptimized.create(backendData)
      
      if (response.success) {
        // 重新获取系统列表以确保数据一致性
        await fetchSystems()
        ElMessage.success('创建系统成功')
        return response.data
      } else {
        throw new Error(response.message || '创建系统失败')
      }
    } catch (error) {
      console.error('创建系统失败:', error)
      setError(error.message || '创建系统失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 更新系统
  const updateSystem = async (systemId, systemData) => {
    setLoading(true)
    clearError()
    
    try {
      const backendData = dataTransformUtils.transformSystemToBackend(systemData)
      const response = await systemApiOptimized.update(systemId, backendData)
      
      if (response.success) {
        // 重新获取系统详情
        await fetchSystemDetail(systemId)
        ElMessage.success('更新系统成功')
        return true
      } else {
        throw new Error(response.message || '更新系统失败')
      }
    } catch (error) {
      console.error('更新系统失败:', error)
      setError(error.message || '更新系统失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 删除系统
  const deleteSystem = async (systemId) => {
    setLoading(true)
    clearError()
    
    try {
      const response = await systemApiOptimized.delete(systemId)
      
      if (response.success) {
        // 从列表中移除
        systemsList.value = systemsList.value.filter(system => system.id !== systemId)
        
        // 清除选中状态
        if (selectedSystemId.value === systemId) {
          selectedSystemId.value = null
        }
        
        ElMessage.success('删除系统成功')
        return true
      } else {
        throw new Error(response.message || '删除系统失败')
      }
    } catch (error) {
      console.error('删除系统失败:', error)
      setError(error.message || '删除系统失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 更新系统状态
  const updateSystemStatus = async (systemId, enabled) => {
    try {
      const response = await systemApiOptimized.updateStatus(systemId, enabled)
      
      if (response.success) {
        // 更新本地状态
        const system = systemsList.value.find(s => s.id === systemId)
        if (system) {
          system.enabled = enabled
        }
        
        ElMessage.success(`系统已${enabled ? '启用' : '禁用'}`)
        return true
      } else {
        throw new Error(response.message || '更新系统状态失败')
      }
    } catch (error) {
      console.error('更新系统状态失败:', error)
      setError(error.message || '更新系统状态失败')
      throw error
    }
  }
  
  // ==================== 模块管理方法 ====================
  
  // 获取模块列表
  const fetchModules = async (params = {}) => {
    modulesLoading.value = true
    clearError()
    
    try {
      const response = await moduleApiOptimized.getList(params)
      
      if (response.success) {
        // 转换数据格式
        modulesList.value = dataTransformUtils.transformModulesFromBackend(response.data || [])
        return modulesList.value
      } else {
        throw new Error(response.message || '获取模块列表失败')
      }
    } catch (error) {
      console.error('获取模块列表失败:', error)
      setError(error.message || '获取模块列表失败')
      throw error
    } finally {
      modulesLoading.value = false
    }
  }
  
  // 获取指定系统的模块列表
  const fetchModulesBySystem = async (systemId, params = {}) => {
    modulesLoading.value = true
    clearError()
    
    try {
      const response = await moduleApiOptimized.getBySystem(systemId, params)
      
      if (response.success) {
        const modules = dataTransformUtils.transformModulesFromBackend(response.data || [])
        
        // 更新系统的模块列表
        const system = systemsList.value.find(s => s.id === systemId)
        if (system) {
          system.modules = modules
        }
        
        return modules
      } else {
        throw new Error(response.message || '获取模块列表失败')
      }
    } catch (error) {
      console.error('获取模块列表失败:', error)
      setError(error.message || '获取模块列表失败')
      throw error
    } finally {
      modulesLoading.value = false
    }
  }
  
  // 获取模块详情
  const fetchModuleDetail = async (moduleId) => {
    setLoading(true)
    clearError()
    
    try {
      const response = await moduleApiOptimized.getDetail(moduleId)
      
      if (response.success) {
        const module = dataTransformUtils.transformModuleFromBackend(response.data)
        
        // 更新模块列表中的对应项
        const index = modulesList.value.findIndex(m => m.id === moduleId)
        if (index !== -1) {
          modulesList.value[index] = module
        } else {
          modulesList.value.push(module)
        }
        
        return module
      } else {
        throw new Error(response.message || '获取模块详情失败')
      }
    } catch (error) {
      console.error('获取模块详情失败:', error)
      setError(error.message || '获取模块详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 创建模块
  const createModule = async (moduleData) => {
    setLoading(true)
    clearError()
    
    try {
      const backendData = dataTransformUtils.transformModuleToBackend(moduleData)
      const response = await moduleApiOptimized.create(backendData)
      
      if (response.success) {
        // 重新获取对应系统的模块列表
        if (moduleData.system_id) {
          await fetchModulesBySystem(moduleData.system_id)
        }
        
        ElMessage.success('创建模块成功')
        return response.data
      } else {
        throw new Error(response.message || '创建模块失败')
      }
    } catch (error) {
      console.error('创建模块失败:', error)
      setError(error.message || '创建模块失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 更新模块
  const updateModule = async (moduleId, moduleData) => {
    setLoading(true)
    clearError()
    
    try {
      const backendData = dataTransformUtils.transformModuleToBackend(moduleData)
      const response = await moduleApiOptimized.update(moduleId, backendData)
      
      if (response.success) {
        // 重新获取模块详情
        await fetchModuleDetail(moduleId)
        ElMessage.success('更新模块成功')
        return true
      } else {
        throw new Error(response.message || '更新模块失败')
      }
    } catch (error) {
      console.error('更新模块失败:', error)
      setError(error.message || '更新模块失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 删除模块
  const deleteModule = async (moduleId) => {
    setLoading(true)
    clearError()
    
    try {
      const response = await moduleApiOptimized.delete(moduleId)
      
      if (response.success) {
        // 从列表中移除
        modulesList.value = modulesList.value.filter(module => module.id !== moduleId)
        
        // 从系统的模块列表中移除
        systemsList.value.forEach(system => {
          if (system.modules) {
            system.modules = system.modules.filter(module => module.id !== moduleId)
          }
        })
        
        // 清除选中状态
        if (selectedModuleId.value === moduleId) {
          selectedModuleId.value = null
        }
        
        ElMessage.success('删除模块成功')
        return true
      } else {
        throw new Error(response.message || '删除模块失败')
      }
    } catch (error) {
      console.error('删除模块失败:', error)
      setError(error.message || '删除模块失败')
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 更新模块状态
  const updateModuleStatus = async (moduleId, enabled) => {
    try {
      const response = await moduleApiOptimized.updateStatus(moduleId, enabled)
      
      if (response.success) {
        // 更新本地状态
        const module = modulesList.value.find(m => m.id === moduleId)
        if (module) {
          module.enabled = enabled
        }
        
        // 更新系统中的模块状态
        systemsList.value.forEach(system => {
          if (system.modules) {
            const systemModule = system.modules.find(m => m.id === moduleId)
            if (systemModule) {
              systemModule.enabled = enabled
            }
          }
        })
        
        ElMessage.success(`模块已${enabled ? '启用' : '禁用'}`)
        return true
      } else {
        throw new Error(response.message || '更新模块状态失败')
      }
    } catch (error) {
      console.error('更新模块状态失败:', error)
      setError(error.message || '更新模块状态失败')
      throw error
    }
  }
  
  // ==================== 统计信息方法 ====================
  
  // 获取统计信息
  const fetchStatistics = async () => {
    try {
      const response = await statsApiOptimized.getStats()
      
      if (response.success) {
        statistics.value = response.data || {}
        return statistics.value
      } else {
        throw new Error(response.message || '获取统计信息失败')
      }
    } catch (error) {
      console.error('获取统计信息失败:', error)
      setError(error.message || '获取统计信息失败')
      throw error
    }
  }
  
  // ==================== 选择状态管理 ====================
  
  const selectSystem = (systemId) => {
    selectedSystemId.value = systemId
    selectedModuleId.value = null // 清除模块选择
  }
  
  const selectModule = (moduleId) => {
    selectedModuleId.value = moduleId
  }
  
  const clearSelection = () => {
    selectedSystemId.value = null
    selectedModuleId.value = null
  }
  
  // ==================== 初始化方法 ====================
  
  const initialize = async () => {
    try {
      await Promise.all([
        fetchSystems(),
        fetchStatistics()
      ])
    } catch (error) {
      console.error('初始化失败:', error)
    }
  }
  
  // ==================== 重置方法 ====================
  
  const reset = () => {
    systemsList.value = []
    modulesList.value = []
    loading.value = false
    systemsLoading.value = false
    modulesLoading.value = false
    error.value = null
    selectedSystemId.value = null
    selectedModuleId.value = null
    statistics.value = {
      systems: {},
      modules: {},
      overview: {}
    }
  }
  
  // ==================== 返回Store接口 ====================
  
  return {
    // 状态
    systemsList,
    modulesList,
    loading,
    systemsLoading,
    modulesLoading,
    error,
    selectedSystemId,
    selectedModuleId,
    statistics,
    
    // 计算属性
    enabledSystems,
    enabledModules,
    currentSystem,
    currentModule,
    systemsByCategory,
    modulesBySystem,
    
    // 系统管理方法
    fetchSystems,
    fetchSystemDetail,
    createSystem,
    updateSystem,
    deleteSystem,
    updateSystemStatus,
    
    // 模块管理方法
    fetchModules,
    fetchModulesBySystem,
    fetchModuleDetail,
    createModule,
    updateModule,
    deleteModule,
    updateModuleStatus,
    
    // 统计信息方法
    fetchStatistics,
    
    // 选择状态管理
    selectSystem,
    selectModule,
    clearSelection,
    
    // 工具方法
    setLoading,
    setError,
    clearError,
    initialize,
    reset
  }
})

// 兼容性Store - 保持原有接口不变
export const useServiceStore = defineStore('service', () => {
  const optimizedStore = useServiceStoreOptimized()
  
  // 直接代理所有方法和属性
  return {
    ...optimizedStore
  }
})