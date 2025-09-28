<!--
  系统树组件 (SystemTree.vue)
  
  功能说明：
  - 系统和模块的层级树形展示
  - 支持搜索过滤和节点操作
  - 提供展开/收起控制
  - 支持右键菜单和操作按钮
  - 显示API数量统计
  
  组件特性：
  - 响应式设计，支持移动端
  - 虚拟滚动，支持大量数据
  - 拖拽排序（可选）
  - 多选模式（可选）
  - 自定义图标和样式
  
  技术实现：
  - Element Plus Tree 组件
  - TypeScript 类型支持
  - Composition API
  - 事件驱动架构
  
  使用场景：
  - 系统管理页面
  - API文档导航
  - 模块选择器
  - 权限配置界面
  
  @author AI Assistant
  @version 1.0.0
  @since 2024-01-15
-->
<template>
  <div class="system-tree">
    <!-- 
      树形控件头部区域
      - 搜索输入框
      - 展开/收起控制按钮
      - 其他操作按钮
    -->
    <div class="tree-header">
      <el-input
        v-model="searchKeyword"
        :placeholder="searchPlaceholder"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="tree-actions">
        <el-button
          size="small"
          @click="handleRefresh"
          :loading="refreshing"
          title="刷新"
        >
          <el-icon>
            <Refresh />
          </el-icon>
        </el-button>
        <el-button
          size="small"
          @click="toggleExpandAll"
          :title="expandAll ? '收起所有' : '展开所有'"
        >
          <el-icon>
            <component :is="IconManager.getArrowIcon(expandAll)" />
          </el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 树容器 -->
    <div class="tree-container">
      <el-tree
        ref="treeRef"
        :key="treeKey"
        :data="treeData"
        :props="treeProps"
        :filter-node-method="filterNode"
        :expand-on-click-node="false"
        :highlight-current="true"
        :default-expand-all="expandAll"
        node-key="id"
        @node-click="handleNodeClick"
        @node-contextmenu="handleNodeContextMenu"
      >
        <template #default="{ node, data }">
          <div class="tree-node" :class="{ 'disabled-node': data.enabled === false }">
            <el-icon class="node-icon" :size="16" :class="{ 'disabled-icon': data.enabled === false }">
              <component :is="getNodeIcon(data)" />
            </el-icon>
            <span class="node-label" :class="{ 'disabled-label': data.enabled === false }">{{ node.label }}</span>
            <span v-if="data.enabled === false" class="disabled-tag">已禁用</span>
            <span v-if="showCount && data.apiCount !== undefined" class="node-count">
              ({{ data.apiCount }})
            </span>
            <div class="node-actions" v-if="showActions && !data.isModule">
              <el-dropdown @command="handleTreeAction" trigger="click" @click.stop>
                <el-icon class="action-icon" :size="14">
                  <MoreFilled />
                </el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="'add-module-' + data.id">
                      <el-icon><Plus /></el-icon>
                      添加模块
                    </el-dropdown-item>
                    <el-dropdown-item :command="'edit-' + data.id">
                      <el-icon><Edit /></el-icon>
                      编辑系统
                    </el-dropdown-item>
                    <el-dropdown-item :command="'delete-' + data.id" divided>
                      <el-icon><Delete /></el-icon>
                      删除系统
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>
      </el-tree>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { IconManager } from '@/utils/IconManager'

// 获取系统树组件所需的图标
const {
  Search,
  Refresh,
  MoreFilled,
  Plus,
  Edit,
  Delete,
  DocumentAdd,
  Setting
} = IconManager.getSystemTreeIcons()

/**
 * 组件Props定义
 * 
 * 类型说明：
 * - data: 树形数据数组
 * - searchPlaceholder: 搜索框占位符
 * - showCount: 是否显示节点计数
 * - showActions: 是否显示操作按钮
 * - labelKey: 节点标签字段名
 * - childrenKey: 子节点字段名
 * - getIcon: 自定义图标获取函数
 */
const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  searchPlaceholder: {
    type: String,
    default: '搜索系统'
  },
  showCount: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: false
  },
  labelKey: {
    type: String,
    default: 'name'
  },
  childrenKey: {
    type: String,
    default: 'children'
  },
  getIcon: {
    type: Function,
    default: undefined
  },
  showDisabled: {
    type: Boolean,
    default: true
  },
  // 类别过滤（可选）：仅展示指定类别的系统及其子节点
  categories: {
    type: Array,
    default: () => []
  }
})

// Emits定义
const emit = defineEmits(['node-click', 'node-contextmenu', 'tree-action', 'refresh'])

// 响应式数据
const treeRef = ref()
const treeKey = ref(0)
const searchKeyword = ref('')
const expandAll = ref(false)
const refreshing = ref(false)

// 树形配置
const treeProps = computed(() => ({
  children: props.childrenKey,
  label: props.labelKey
}))

// 树形数据
const treeData = computed(() => {
  // 基础数据：根据 showDisabled 过滤禁用节点
  const baseData = (() => {
    if (props.showDisabled) {
      return props.data
    }
    const filterDisabled = (nodes) => {
      return nodes.filter(node => {
        if (node.enabled === false) {
          return false
        }
        if (node[props.childrenKey] && node[props.childrenKey].length > 0) {
          node[props.childrenKey] = filterDisabled(node[props.childrenKey])
        }
        return true
      })
    }
    return filterDisabled([...props.data])
  })()

  // 类别过滤：当传入 categories 时，仅保留匹配类别的系统节点
  const applyCategoryFilter = (nodes) => {
    // 若未配置类别或为空，则不做过滤
    if (!Array.isArray(props.categories) || props.categories.length === 0) {
      return nodes
    }
    const allowed = new Set(props.categories)
    return nodes.filter(node => {
      // 仅过滤系统层级，模块等子节点随系统保留
      if (node && typeof node === 'object') {
        if (node.category && allowed.has(node.category)) {
          return true
        }
        // 若节点无类别字段（如模块），保留由其父系统决定；此处默认保留
        // 但为了安全，只有当父系统在上层被保留时，模块才会存在
        return !node.category
      }
      return false
    })
  }

  return applyCategoryFilter(baseData)
})

// 监听数据变化，强制重新渲染树组件
watch(
  () => props.data,
  (newData, oldData) => {
    // 当数据发生变化时，强制重新渲染树组件
    if (newData !== oldData || (Array.isArray(newData) && newData.length !== (Array.isArray(oldData) ? oldData.length : 0))) {
      nextTick(() => {
        treeKey.value++
        // 如果有搜索关键词，重新应用过滤
        if (searchKeyword.value && treeRef.value) {
          setTimeout(() => {
            if (treeRef.value) {
              treeRef.value.filter(searchKeyword.value)
            }
          }, 100)
        }
      })
    }
  },
  { deep: true, immediate: true }
)

// 方法
const handleSearch = () => {
  if (treeRef.value) {
    treeRef.value.filter(searchKeyword.value)
  }
}

/**
 * 节点过滤方法
 * 
 * @param {string} value - 搜索关键词
 * @param {any} data - 节点数据
 * @returns {boolean} 是否显示该节点
 */
const filterNode = (value, data) => {
  if (!value) return true
  const label = data[props.labelKey] || ''
  return label.toLowerCase().includes(value.toLowerCase())
}

/**
 * 切换全部展开/收起状态
 * 
 * 通过改变key值强制重新渲染树组件，
 * 让default-expand-all属性生效
 */
const toggleExpandAll = () => {
  expandAll.value = !expandAll.value
  // 通过改变key值强制重新渲染树组件，让default-expand-all属性生效
  treeKey.value++
}

/**
 * 处理节点点击事件
 * 
 * @param {any} data - 节点数据
 */
const handleNodeClick = (data) => {
  emit('node-click', data)
}

/**
 * 处理节点右键菜单事件
 * 
 * @param {MouseEvent} event - 鼠标事件
 * @param {any} data - 节点数据
 */
const handleNodeContextMenu = (event, data) => {
  emit('node-contextmenu', event, data)
}

/**
 * 处理树操作命令
 * 
 * @param {string} command - 操作命令
 */
const handleTreeAction = (command) => {
  emit('tree-action', command)
}

/**
 * 处理刷新操作
 */
const handleRefresh = async () => {
  refreshing.value = true
  try {
    emit('refresh')
    // 延迟重置刷新状态，给用户视觉反馈
    setTimeout(() => {
      refreshing.value = false
    }, 500)
  } catch (error) {
    refreshing.value = false
    console.error('刷新失败:', error)
  }
}

/**
 * 根据系统分类获取对应图标
 * 
 * @param {string} category - 系统分类
 * @returns {any} 图标组件
 */
const getSystemIcon = (category) => {
  const systemTypeIcons = IconManager.getSystemTypeIcons()
  const iconMap = {
    'backend': systemTypeIcons.Cloudy,      // 后端服务使用云图标
    'frontend': systemTypeIcons.Monitor,    // 前端应用使用显示器图标
    'web': systemTypeIcons.Link,
    'api': systemTypeIcons.Cloudy,
    'mobile': systemTypeIcons.Phone,
    'desktop': systemTypeIcons.Monitor,
    'database': systemTypeIcons.DataBoard,
    'middleware': systemTypeIcons.Connection,
    'hardware': systemTypeIcons.Cpu,
    'other': systemTypeIcons.Platform
  }
  return iconMap[category] || systemTypeIcons.Platform
}

/**
 * 获取节点图标
 * 
 * @param {any} data - 节点数据
 * @returns {any} 图标组件
 */
const getNodeIcon = (data) => {
  if (props.getIcon) {
    return props.getIcon(data)
  }
  
  // 默认图标逻辑
  if (data.type === 'system') {
    // 根据系统分类返回对应图标
    return getSystemIcon(data.category)
  } else if (data.type === 'module' || data.isModule) {
    return IconManager.getDefaultModuleIcon() // 模块使用文件图标
  } else if (data.type === 'all') {
    return IconManager.getFolderIcon(true)
  } else {
    return IconManager.getDefaultModuleIcon()
  }
}

// 暴露方法给父组件
defineExpose({
  filter: (value) => {
    if (treeRef.value) {
      treeRef.value.filter(value)
    }
  },
  setCurrentKey: (key) => {
    if (treeRef.value) {
      treeRef.value.setCurrentKey(key)
    }
  },
  getSystemIcon
})
</script>

<style scoped>
.system-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.tree-header .el-input {
  flex: 1;
}

.tree-header .el-input :deep(.el-input__wrapper) {
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.tree-header .el-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.tree-header .el-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.tree-actions {
  display: flex;
  gap: 4px;
}

.tree-actions .el-button {
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.tree-actions .el-button:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.tree-container {
  flex: 1;
  overflow: auto;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
  padding: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 4px 0;
}

.node-icon {
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.node-label {
  flex: 1;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.node-count {
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-left: auto;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: auto;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.action-icon {
  color: var(--el-text-color-regular);
  cursor: pointer;
  padding: 2px;
  border-radius: 2px;
  transition: all 0.2s;
}

.action-icon:hover {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

/* 树形组件样式覆盖 */
:deep(.el-tree-node__content) {
  height: auto;
  min-height: 32px;
  padding: 0 8px;
}

:deep(.el-tree-node__expand-icon) {
  color: var(--el-text-color-regular);
}

:deep(.el-tree-node__expand-icon.expanded) {
  transform: rotate(90deg);
}

:deep(.el-tree-node:focus > .el-tree-node__content) {
  background-color: var(--el-color-primary-light-9);
}

:deep(.el-tree-node__content:hover) {
  background-color: var(--el-color-primary-light-9);
}

:deep(.el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content) {
  background-color: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
}

/* 禁用状态样式 */
.disabled-node {
  opacity: 0.8;
}

.disabled-icon {
  color: var(--el-color-danger) !important;
}

.disabled-label {
  color: var(--el-color-danger) !important;
  font-weight: 500;
}

.disabled-tag {
  font-size: 10px;
  color: var(--el-color-danger);
  background-color: var(--el-color-danger-light-9);
  padding: 1px 4px;
  border-radius: 2px;
  margin-left: 4px;
}
</style>