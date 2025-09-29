<template>
  <div class="json-preview-tree">
    <div v-if="data.length === 0" class="empty-tree">
      <el-empty description="暂无预览数据" />
    </div>
    
    <div v-else class="tree-content">
      <!-- 树形结构头部 -->
      <div class="tree-header">
        <div class="header-cell name">参数名</div>
        <div class="header-cell type">类型</div>
        <div class="header-cell required">必填</div>
        <div class="header-cell description">描述</div>
      </div>
      
      <!-- 树形结构内容 -->
      <div class="tree-body">
        <JsonPreviewNode
          v-for="param in rootParams"
          :key="param.id"
          :param="param"
          :all-params="data"
          :expanded-keys="expandedKeys"
          @toggle-expand="handleToggleExpand"
        />
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div v-if="data.length > 0" class="tree-stats">
      <el-tag size="small" type="info">
        <el-icon><DataLine /></el-icon>
        总计 {{ data.length }} 个参数
      </el-tag>
      <el-tag size="small" type="success">
        <el-icon><Folder /></el-icon>
        最大 {{ maxDepth }} 层深度
      </el-tag>
      <el-tag size="small" type="warning">
        <el-icon><Key /></el-icon>
        {{ requiredCount }} 个必填
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { DataLine, Folder, Key } from '@element-plus/icons-vue'
import JsonPreviewNode from './JsonPreviewNode.vue'

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  defaultExpanded: {
    type: Boolean,
    default: true
  }
})

// 响应式状态
const expandedKeys = ref(new Set())

// 计算属性
const rootParams = computed(() => {
  return props.data.filter(param => param.level === 0)
})

const maxDepth = computed(() => {
  return props.data.reduce((max, param) => Math.max(max, param.level || 0), 0)
})

const requiredCount = computed(() => {
  return props.data.filter(param => param.required).length
})

// 初始化展开状态
const initializeExpandedState = () => {
  if (props.defaultExpanded) {
    // 默认展开前两层
    const keysToExpand = props.data
      .filter(param => (param.level || 0) < 2 && (param.type === 'object' || param.type === 'array'))
      .map(param => param.id)
    
    expandedKeys.value = new Set(keysToExpand)
  }
}

// 事件处理
const handleToggleExpand = (paramId) => {
  if (expandedKeys.value.has(paramId)) {
    expandedKeys.value.delete(paramId)
  } else {
    expandedKeys.value.add(paramId)
  }
}

// 监听数据变化，重新初始化展开状态
watch(() => props.data, () => {
  initializeExpandedState()
}, { immediate: true })
</script>

<style scoped>
.json-preview-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-tree {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tree-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.tree-header {
  display: flex;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px 6px 0 0;
  font-weight: 500;
  color: #606266;
  font-size: 13px;
}

.header-cell {
  padding: 8px 12px;
  border-right: 1px solid #e4e7ed;
}

.header-cell:last-child {
  border-right: none;
}

.header-cell.name {
  flex: 2;
}

.header-cell.type {
  flex: 1;
}

.header-cell.required {
  width: 60px;
  text-align: center;
}

.header-cell.description {
  flex: 1.5;
}

.tree-body {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-top: none;
  border-radius: 0 0 6px 6px;
  overflow: auto;
  background: #fff;
}

.tree-stats {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}
</style>