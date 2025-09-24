import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  createManagementSystem, 
  createServiceModule, 
  SystemCategory,
  SystemCategoryLabels 
} from '@/types/service'
import { systemApi, moduleApi } from '@/api/service'

export const useServiceStore = defineStore('service', () => {
  // 状态
  const systemsList = ref([])
  const loading = ref(false)
  const selectedSystemId = ref(null)
  const searchKeyword = ref('')
  const filterCategory = ref('')
  const filterEnabled = ref(null)
  
  // 计算属性
  const filteredSystems = computed(() => {
    let filtered = systemsList.value
    
    // 关键词搜索
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      filtered = filtered.filter(system => 
        (system.name || '').toLowerCase().includes(keyword) ||
        (system.description || '').toLowerCase().includes(keyword) ||
        (system.modules || []).some(module => 
          (module.name || '').toLowerCase().includes(keyword) ||
          (module.description || '').toLowerCase().includes(keyword) ||
          (module.tags && Array.isArray(module.tags) && module.tags.some(tag => (tag || '').toLowerCase().includes(keyword)))
        )
      )
    }
    
    // 分类筛选
    if (filterCategory.value) {
      filtered = filtered.filter(system => system.category === filterCategory.value)
    }
    
    // 启用状态筛选
    if (filterEnabled.value !== null) {
      filtered = filtered.filter(system => system.enabled === filterEnabled.value)
    }
    
    return filtered.sort((a, b) => a.order - b.order)
  })
  
  const selectedSystem = computed(() => {
    return systemsList.value.find(system => system.id === selectedSystemId.value)
  })
  
  const systemsCount = computed(() => systemsList.value.length)
  
  const modulesCount = computed(() => {
    return systemsList.value.reduce((total, system) => total + system.modules.length, 0)
  })
  
  const enabledSystemsCount = computed(() => {
    return systemsList.value.filter(system => system.enabled).length
  })
  
  const enabledModulesCount = computed(() => {
    return systemsList.value.reduce((total, system) => 
      total + system.modules.filter(module => module.enabled).length, 0
    )
  })
  
  // 方法
  const setLoading = (status) => {
    loading.value = status
  }
  
  const setSearchKeyword = (keyword) => {
    searchKeyword.value = keyword
  }
  
  const setFilterCategory = (category) => {
    filterCategory.value = category
  }
  
  const setFilterEnabled = (enabled) => {
    filterEnabled.value = enabled
  }
  
  const selectSystem = (systemId) => {
    selectedSystemId.value = selectedSystemId.value === systemId ? null : systemId
  }
  
  const clearSelection = () => {
    selectedSystemId.value = null
  }
  
  const clearFilters = () => {
    searchKeyword.value = ''
    filterCategory.value = ''
    filterEnabled.value = null
  }
  
  // 系统管理方法
  const addSystem = async (systemData) => {
    setLoading(true)
    try {
      const response = await systemApi.create(systemData)
      const newSystem = {
        id: response.data?.id || Date.now().toString(),
        ...systemData,
        modules: []
      }
      systemsList.value.push(newSystem)
      return newSystem
    } catch (error) {
      console.error('创建系统失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const updateSystem = async (systemId, systemData) => {
    setLoading(true)
    try {
      const response = await systemApi.update(systemId, systemData)
      const index = systemsList.value.findIndex(system => system.id === systemId)
      if (index !== -1) {
        Object.assign(systemsList.value[index], response.data)
        return systemsList.value[index]
      }
      return response.data
    } catch (error) {
      console.error('更新系统失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const deleteSystem = async (systemId) => {
    setLoading(true)
    try {
      await systemApi.delete(systemId)
      const index = systemsList.value.findIndex(system => system.id === systemId)
      if (index !== -1) {
        const deletedSystem = systemsList.value.splice(index, 1)[0]
        if (selectedSystemId.value === systemId) {
          selectedSystemId.value = null
        }
        return deletedSystem
      }
      return null
    } catch (error) {
      console.error('删除系统失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const toggleSystemEnabled = async (systemId) => {
    setLoading(true)
    try {
      const response = await systemApi.toggleEnabled(systemId)
      const system = systemsList.value.find(s => s.id === systemId)
      if (system) {
        system.enabled = response.data.enabled
        return system
      }
      return response.data
    } catch (error) {
      console.error('切换系统状态失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  // 模块管理方法
  const addModule = async (systemId, moduleData) => {
    setLoading(true)
    try {
      const response = await moduleApi.create({
        ...moduleData,
        system_id: systemId
      })
      const system = systemsList.value.find(s => s.id === systemId)
      if (system) {
        const newModule = {
          id: response.data?.id || Date.now().toString(),
          ...moduleData,
          system_id: systemId,
          tags: moduleData.tags || []
        }
        system.modules.push(newModule)
        return newModule
      }
      return {
        id: response.data?.id || Date.now().toString(),
        ...moduleData,
        system_id: systemId
      }
    } catch (error) {
      console.error('创建模块失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const updateModule = async (moduleId, moduleData) => {
    setLoading(true)
    try {
      const response = await moduleApi.update(moduleId, moduleData)
      for (const system of systemsList.value) {
        const moduleIndex = system.modules.findIndex(m => m.id === moduleId)
        if (moduleIndex !== -1) {
          Object.assign(system.modules[moduleIndex], {
            ...moduleData,
            id: system.modules[moduleIndex].id,
            system_id: system.modules[moduleIndex].system_id,
            tags: moduleData.tags || system.modules[moduleIndex].tags || []
          })
          return system.modules[moduleIndex]
        }
      }
      return {
        id: moduleId,
        ...moduleData
      }
    } catch (error) {
      console.error('更新模块失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const deleteModule = async (systemId, moduleId) => {
    setLoading(true)
    try {
      await moduleApi.delete(moduleId)
      const system = systemsList.value.find(s => s.id === systemId)
      if (system) {
        const index = system.modules.findIndex(m => m.id === moduleId)
        if (index > -1) {
          system.modules.splice(index, 1)
        }
      }
    } catch (error) {
      console.error('删除模块失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const toggleModuleEnabled = async (systemId, moduleId) => {
    setLoading(true)
    try {
      const response = await moduleApi.toggleEnabled(moduleId)
      const system = systemsList.value.find(s => s.id === systemId)
      if (system) {
        const module = system.modules.find(m => m.id === moduleId)
        if (module) {
          module.enabled = response.data.enabled
        }
      }
      return response.data
    } catch (error) {
      console.error('切换模块状态失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const findModule = (moduleId) => {
    for (const system of systemsList.value) {
      const module = system.modules.find(m => m.id === moduleId)
      if (module) {
        return { module, system }
      }
    }
    return null
  }
  
  // 数据加载方法
  const loadSystems = async () => {
    setLoading(true)
    try {
      // 获取系统列表
      const systemsResponse = await systemApi.getList({ enabled_only: false })
      const systems = systemsResponse.data || []
      
      // 为每个系统获取模块列表
      const systemsWithModules = await Promise.all(
        systems.map(async (system) => {
          try {
            const modulesResponse = await moduleApi.getBySystem(system.id)
            const modules = modulesResponse.data || []
            
            return {
              ...system,
              modules: modules.map(module => ({
                ...module,
                tags: module.tags || []
              }))
            }
          } catch (error) {
            console.error(`获取系统 ${system.id} 的模块失败:`, error)
            return {
              ...system,
              modules: []
            }
          }
        })
      )
      
      systemsList.value = systemsWithModules
    } catch (error) {
      console.error('加载系统列表失败:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }
  
  const refreshSystems = () => {
    return loadSystems()
  }
  
  // 初始化
  const initialize = () => {
    return loadSystems()
  }
  
  return {
    // 状态
    systemsList,
    loading,
    selectedSystemId,
    searchKeyword,
    filterCategory,
    filterEnabled,
    
    // 计算属性
    filteredSystems,
    selectedSystem,
    systemsCount,
    modulesCount,
    enabledSystemsCount,
    enabledModulesCount,
    
    // 基础方法
    setLoading,
    setSearchKeyword,
    setFilterCategory,
    setFilterEnabled,
    selectSystem,
    clearSelection,
    clearFilters,
    
    // 系统管理
    addSystem,
    updateSystem,
    deleteSystem,
    toggleSystemEnabled,
    
    // 模块管理
    addModule,
    updateModule,
    deleteModule,
    toggleModuleEnabled,
    findModule,
    
    // 数据加载
    loadSystems,
    refreshSystems,
    initialize
  }
})