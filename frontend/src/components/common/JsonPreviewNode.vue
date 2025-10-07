<template>
  <div class="json-preview-node">
    <!-- 当前节点 -->
    <div 
      :class="['node-row', { 'is-child': param.level > 0 }]"
      :style="{ paddingLeft: `${(param.level || 0) * 20}px` }"
    >
      <div class="row-content">
        <!-- 参数名 -->
        <div class="cell name">
          <!-- 展开/收起按钮 -->
          <el-button
            v-if="hasChildren"
            class="expand-toggle"
            text
            size="small"
            :aria-expanded="isExpanded"
            @click="toggleExpand"
          >
            <el-icon>
              <component :is="isExpanded ? 'CaretBottom' : 'CaretRight'" />
            </el-icon>
          </el-button>
          <span
            v-else
            class="expand-placeholder"
          />
          
          <!-- 参数名称 -->
          <span class="param-name">{{ param.name }}</span>
          
          <!-- 层级指示器 -->
          <el-tag
            v-if="param.level > 0"
            size="small"
            type="info"
            class="level-tag"
          >
            L{{ param.level }}
          </el-tag>
        </div>
        
        <!-- 类型 -->
        <div class="cell type">
          <el-tag 
            :type="getTypeTagType(param.type)" 
            size="small"
            class="type-tag"
          >
            {{ param.type }}
          </el-tag>
        </div>
        
        <!-- 必填 -->
        <div class="cell required">
          <el-icon
            v-if="param.required"
            class="required-icon"
            color="#f56c6c"
          >
            <Star />
          </el-icon>
          <span
            v-else
            class="optional-text"
          >可选</span>
        </div>
        
        <!-- 描述 -->
        <div class="cell description">
          <span
            v-if="param.description"
            class="description-text"
          >
            {{ param.description }}
          </span>
          <span
            v-else
            class="no-description"
          >
            {{ getDefaultDescription(param.type) }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 子节点 -->
    <div
      v-if="hasChildren && isExpanded"
      class="children-container"
    >
      <JsonPreviewNode
        v-for="child in children"
        :key="child.id"
        :param="child"
        :all-params="allParams"
        :expanded-keys="expandedKeys"
        @toggle-expand="$emit('toggle-expand', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CaretBottom, CaretRight, Star } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  param: {
    type: Object,
    required: true
  },
  allParams: {
    type: Array,
    required: true
  },
  expandedKeys: {
    type: Set,
    required: true
  }
})

// Emits
const emit = defineEmits(['toggle-expand'])

// 计算属性
const children = computed(() => {
  return props.allParams.filter(p => p.parentId === props.param.id)
})

const hasChildren = computed(() => {
  return children.value.length > 0
})

const isExpanded = computed(() => {
  return props.expandedKeys.has(props.param.id)
})

// 方法
const toggleExpand = () => {
  emit('toggle-expand', props.param.id)
}

const getTypeTagType = (type) => {
  const typeMap = {
    'string': '',
    'number': 'warning',
    'boolean': 'success',
    'object': 'primary',
    'array': 'info',
    'file': 'danger'
  }
  return typeMap[type] || ''
}

const getDefaultDescription = (type) => {
  const descriptionMap = {
    'string': '字符串类型参数',
    'number': '数值类型参数',
    'boolean': '布尔类型参数',
    'object': '对象类型参数',
    'array': '数组类型参数',
    'file': '文件类型参数'
  }
  return descriptionMap[type] || '参数'
}
</script>

<style scoped>
.json-preview-node {
  width: 100%;
}

.node-row {
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.2s;
}

.node-row:hover {
  background-color: #f8f9fa;
}

.row-content {
  display: flex;
  align-items: center;
  min-height: 40px;
}

.cell {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  border-right: 1px solid #f0f2f5;
}

.cell:last-child {
  border-right: none;
}

.cell.name {
  flex: 2;
  gap: 8px;
}

.cell.type {
  flex: 1;
}

.cell.required {
  width: 60px;
  justify-content: center;
}

.cell.description {
  flex: 1.5;
}

.expand-toggle {
  width: 20px;
  height: 20px;
  padding: 0;
  margin-right: 4px;
}

.expand-placeholder {
  width: 20px;
  height: 20px;
  margin-right: 4px;
}

.param-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.level-tag {
  margin-left: 8px;
  font-size: 10px;
  height: 16px;
  line-height: 14px;
}

.type-tag {
  font-size: 12px;
  font-weight: 500;
}

.required-icon {
  font-size: 14px;
}

.optional-text {
  font-size: 12px;
  color: #909399;
}

.description-text {
  font-size: 13px;
  color: #606266;
}

.no-description {
  font-size: 13px;
  color: #c0c4cc;
  font-style: italic;
}

.children-container {
  background-color: #fafbfc;
}

.is-child .row-content {
  background: linear-gradient(90deg, transparent 0%, transparent calc(var(--level) * 20px - 1px), #e4e7ed calc(var(--level) * 20px), transparent calc(var(--level) * 20px + 1px));
}
</style>