# 前端开发指南

## 概述

本文档提供前端开发的完整指南，包括项目结构、开发规范、最佳实践和最新的功能实现细节。

## 技术栈

### 核心技术
- **Vue 3**: 使用 Composition API
- **TypeScript**: 类型安全的开发
- **Vite**: 快速的构建工具
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **Vue Router**: 路由管理

### 工作流相关
- **Vue Flow**: 工作流图形库
- **@vue-flow/core**: 核心功能
- **@vue-flow/controls**: 控制组件
- **@vue-flow/minimap**: 小地图组件

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 通用组件
│   │   ├── common/         # 基础组件
│   │   ├── forms/          # 表单组件
│   │   └── workflow/       # 工作流组件
│   │       ├── Designer.vue           # 工作流设计器
│   │       ├── NodePropertyPanel.vue  # 节点属性配置面板
│   │       └── nodes/                 # 节点组件
│   │           ├── ApiCallNode.vue
│   │           ├── DataTransformNode.vue
│   │           └── ...
│   ├── views/              # 页面组件
│   ├── stores/             # Pinia状态管理
│   ├── utils/              # 工具函数
│   ├── types/              # TypeScript类型定义
│   └── styles/             # 样式文件
├── docs/                   # 文档
└── tests/                  # 测试文件
```

## 环境变量与本地代理（2025-09 更新）

为统一前后端联调配置、消除历史端口与变量分歧，前端仅保留统一端点变量，并让本地代理与之对齐：

### 统一端点变量
- 使用 `VITE_UNIFIED_API_BASE_URL` 表示后端基础地址。
- 开发环境默认回退：`http://127.0.0.1:8000`。

示例：`frontend/.env.development`
```bash
VITE_UNIFIED_API_BASE_URL=http://127.0.0.1:8000
```

其他环境：
```bash
# .env.staging
VITE_UNIFIED_API_BASE_URL=https://staging.api.company.com

# .env.production
VITE_UNIFIED_API_BASE_URL=https://api.company.com
```

### Vite 代理配置
- `vite.config.js` 读取 `VITE_UNIFIED_API_BASE_URL` 作为 `/api` 代理目标。
- 启动开发服务器后，通过该代理访问后端接口。

相关片段：
```ts
// vite.config.js（要点节选）
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const targetBase = env.VITE_UNIFIED_API_BASE_URL || 'http://127.0.0.1:8000'
  return {
    server: {
      proxy: {
        '/api': { target: targetBase, changeOrigin: true }
      }
    }
  }
})
```

### 代码中的调用规范
- 业务 API 端点请显式以 `'/api/...'` 开头或使用完整域名。
- 统一接口模块（`src/api/unified-api.ts`）仅使用 `VITE_UNIFIED_API_BASE_URL` 作为 `baseURL`。

### 历史变量与端口清理
- `VITE_API_BASE_URL` 已弃用，不再在文档与配置中使用。
- 移除硬编码 `http://localhost:8002`；如需本地默认值，使用 `127.0.0.1:8000`。

### 启动与验证
```bash
# 后端（默认 8000）
uvicorn src.auto_test.main:app --app-dir backend --host 127.0.0.1 --port 8000

# 前端
npm run dev -- --host
```
访问 `http://localhost:5173/`，在页面触发任一 `/api/...` 请求验证 200/业务正常。

## 开发规范

### 1. 代码风格

#### Vue组件规范
```vue
<template>
  <!-- 使用语义化的HTML结构 -->
  <div class="component-name">
    <header class="component-header">
      <!-- 头部内容 -->
    </header>
    <main class="component-content">
      <!-- 主要内容 -->
    </main>
  </div>
</template>

<script setup lang="ts">
// 导入顺序：Vue相关 -> 第三方库 -> 本地模块
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { ComponentProps } from '@/types'

// 接口定义
interface Props {
  title: string
  data?: any[]
}

// Props定义
const props = withDefaults(defineProps<Props>(), {
  data: () => []
})

// 响应式数据
const loading = ref(false)
const items = ref<any[]>([])

// 计算属性
const filteredItems = computed(() => {
  return items.value.filter(item => item.visible)
})

// 方法
const handleSubmit = async () => {
  loading.value = true
  try {
    // 处理逻辑
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped>
.component-name {
  /* 使用CSS变量 */
  --primary-color: #409eff;
  --border-radius: 4px;
}

.component-header {
  /* 使用Flexbox或Grid布局 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
```

#### TypeScript规范
```typescript
// 接口定义
interface UserData {
  id: string
  name: string
  email: string
  createdAt: Date
}

// 类型别名
type Status = 'pending' | 'success' | 'error'

// 泛型使用
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 函数类型
type EventHandler = (event: Event) => void
```

### 2. 命名规范

#### 文件命名
- **组件文件**: PascalCase (如 `UserProfile.vue`)
- **工具文件**: camelCase (如 `formatDate.ts`)
- **常量文件**: UPPER_SNAKE_CASE (如 `API_ENDPOINTS.ts`)

#### 变量命名
- **变量/函数**: camelCase (如 `userName`, `handleClick`)
- **常量**: UPPER_SNAKE_CASE (如 `MAX_RETRY_COUNT`)
- **组件**: PascalCase (如 `UserProfile`)

### 3. Element Plus 图标使用规范

#### 图标导入和使用
```vue
<template>
  <el-button>
    <el-icon><Plus /></el-icon>
    添加
  </el-button>
</template>

<script setup lang="ts">
// 正确的图标导入方式
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
</script>
```

#### 常用图标列表
```typescript
// 推荐使用的常用图标
const COMMON_ICONS = {
  // 操作类
  Plus: 'Plus',           // 添加
  Edit: 'Edit',           // 编辑  
  Delete: 'Delete',       // 删除
  Search: 'Search',       // 搜索
  Refresh: 'Refresh',     // 刷新
  
  // 状态类
  Check: 'Check',         // 成功/确认
  Close: 'Close',         // 关闭
  Warning: 'Warning',     // 警告
  InfoFilled: 'InfoFilled', // 信息
  
  // 导航类
  ArrowLeft: 'ArrowLeft',   // 左箭头
  ArrowRight: 'ArrowRight', // 右箭头
  Back: 'Back',             // 返回
  
  // 功能类
  Setting: 'Setting',     // 设置
  Tools: 'Tools',         // 工具
  Aim: 'Aim',            // 瞄准/测试
  View: 'View',          // 查看
  Hide: 'Hide'           // 隐藏
} as const
```

#### 常见错误和解决方案

**❌ 错误示例**
```vue
<!-- 使用不存在的图标 -->
<el-icon><Experiment /></el-icon>  <!-- Experiment 图标不存在 -->
<el-icon><Test /></el-icon>        <!-- Test 图标不存在 -->

<script setup lang="ts">
// 导入不存在的图标会导致运行时错误
import { Experiment, Test } from '@element-plus/icons-vue'
</script>
```

**✅ 正确示例**
```vue
<!-- 使用存在的替代图标 -->
<el-icon><Aim /></el-icon>      <!-- 用 Aim 替代 Experiment -->
<el-icon><Tools /></el-icon>    <!-- 用 Tools 替代 Test -->

<script setup lang="ts">
// 导入存在的图标
import { Aim, Tools } from '@element-plus/icons-vue'
</script>
```

#### 图标验证清单

在使用 Element Plus 图标前，请确认：

1. **图标存在性检查**
   - 访问 [Element Plus 图标库](https://element-plus.org/zh-CN/component/icon.html) 确认图标名称
   - 在 IDE 中检查导入是否有错误提示

2. **命名规范检查**
   - 图标名称使用 PascalCase (如 `ArrowLeft`, `InfoFilled`)
   - 避免使用自定义或不存在的图标名称

3. **替代方案**
   - `Experiment` → `Aim` (瞄准/测试相关)
   - `Test` → `Tools` (工具/测试相关)
   - `Config` → `Setting` (配置相关)

#### 错误排查步骤

当遇到图标导入错误时：

1. **检查控制台错误**
   ```
   SyntaxError: The requested module does not provide an export named 'Experiment'
   ```

2. **定位问题文件**
   ```bash
   # 搜索使用了错误图标的文件
   grep -r "Experiment" src/
   ```

3. **替换为正确图标**
   - 更新导入语句
   - 更新模板中的图标引用

## 最新功能实现

### 节点显示优化 (2024年)

#### 1. 节点库布局优化

**实现目标**
- 紧凑的网格布局，提升空间利用率
- 支持文字自动换行，避免文字截断
- 响应式设计，适配不同屏幕尺寸

**技术实现**
```scss
// 节点库紧凑水平布局
.node-library {
  display: grid;
  grid-template-columns: 1fr;
  gap: 4px;
  padding: 0 4px;
}

.node-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  }
}

.node-title {
  font-size: 13px;
  line-height: 1.2;
  word-wrap: break-word;
  flex: 1;
}
```

**关键特性**
- **紧凑水平排列**: 节点库采用水平布局，图标和标题在同一行
- **空间优化**: 大幅节省垂直空间，提升浏览效率
- **悬停效果**: 提供视觉反馈，提升交互体验

#### 2. 节点属性配置系统

**NodePropertyPanel组件设计**
```vue
<template>
  <div class="node-property-panel">
    <div class="panel-header">
      <h3>节点配置</h3>
      <el-button @click="$emit('close')" type="text" size="small">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    
    <div class="panel-content">
      <!-- 通用配置 -->
      <div class="config-section">
        <h4>基础配置</h4>
        <el-form :model="nodeData" label-width="80px">
          <el-form-item label="节点名称">
            <el-input v-model="nodeData.label" @input="handleUpdate" />
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 类型特定配置 -->
      <component 
        :is="configComponent" 
        :node-data="nodeData"
        @update="handleUpdate"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ApiCallConfig from './configs/ApiCallConfig.vue'
import DataTransformConfig from './configs/DataTransformConfig.vue'

interface Props {
  nodeData: any
  nodeType: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  update: [nodeId: string, updates: any]
  close: []
}>()

// 动态配置组件映射
const configComponent = computed(() => {
  const componentMap = {
    'api-call': ApiCallConfig,
    'data-transform': DataTransformConfig,
    // 其他节点类型...
  }
  return componentMap[props.nodeType] || null
})

const handleUpdate = (updates: any) => {
  emit('update', props.nodeData.id, updates)
}
</script>
```

**配置功能特性**
- **模块化设计**: 通用配置 + 类型特定配置
- **动态组件**: 根据节点类型加载对应配置组件
- **实时更新**: 配置变更立即同步到画布节点
- **类型安全**: 完整的TypeScript类型定义

#### 3. 长方形节点支持

**灵活尺寸设计**
```scss
.node-container {
  min-width: 150px;
  max-width: 300px; // 支持长方形布局
  min-height: 60px;
  padding: 12px 16px;
  border-radius: 8px;
  background: #fff;
  border: 2px solid #e4e7ed;
  
  &.selected {
    border-color: #409eff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
  }
}

.node-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  
  .node-title {
    font-weight: 500;
    font-size: 14px;
    color: #303133;
  }
  
  .node-description {
    font-size: 12px;
    color: #909399;
    line-height: 1.4;
  }
}
```

**自适应内容布局**
- **弹性宽度**: 根据内容自动调整，支持150px-300px范围
- **垂直布局**: 标题和描述垂直排列，充分利用空间
- **内容溢出**: 长文本自动换行，避免内容截断

### 技术实现细节

#### 1. CSS Grid vs Flexbox选择

**节点库布局 - CSS Grid**
```scss
.node-library {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}
```
- **优势**: 自动计算列数，均匀分布
- **适用**: 网格状布局，等宽元素

**节点内容布局 - Flexbox**
```scss
.node-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
```
- **优势**: 灵活的一维布局，内容自适应
- **适用**: 垂直或水平排列，动态内容

#### 2. Vue 3 Composition API应用

**响应式数据管理**
```typescript
// 节点数据响应式管理
const nodeData = ref<NodeData>({
  id: '',
  type: '',
  label: '',
  config: {}
})

// 计算属性优化
const nodeStyle = computed(() => ({
  width: `${nodeData.value.width || 200}px`,
  height: `${nodeData.value.height || 100}px`
}))

// 事件处理
const handleNodeUpdate = (nodeId: string, updates: Partial<NodeData>) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    Object.assign(node, updates)
  }
}
```

#### 3. TypeScript类型安全

**完整类型定义**
```typescript
interface NodeData {
  id: string
  type: string
  label: string
  position: { x: number; y: number }
  config?: Record<string, any>
  width?: number
  height?: number
}

interface NodeUpdateEvent {
  nodeId: string
  updates: Partial<NodeData>
}

interface ConfigComponent {
  nodeData: NodeData
  onUpdate: (updates: any) => void
}
```

## 性能优化

### 1. 组件优化

**懒加载配置组件**
```typescript
const configComponents = {
  'api-call': () => import('./configs/ApiCallConfig.vue'),
  'data-transform': () => import('./configs/DataTransformConfig.vue')
}
```

**防抖处理**
```typescript
import { debounce } from 'lodash-es'

const debouncedUpdate = debounce((updates: any) => {
  emit('update', props.nodeData.id, updates)
}, 300)
```

### 2. 渲染优化

**虚拟滚动 (大量节点)**
```vue
<template>
  <virtual-list
    :data-key="'id'"
    :data-sources="nodes"
    :data-component="NodeComponent"
    :estimate-size="100"
  />
</template>
```

**条件渲染**
```vue
<template>
  <div v-if="visible" class="node-container">
    <!-- 节点内容 -->
  </div>
</template>
```

## 测试策略

### 1. 单元测试

**组件测试**
```typescript
import { mount } from '@vue/test-utils'
import NodePropertyPanel from '@/components/workflow/NodePropertyPanel.vue'

describe('NodePropertyPanel', () => {
  it('should render correctly', () => {
    const wrapper = mount(NodePropertyPanel, {
      props: {
        nodeData: { id: '1', type: 'api-call', label: 'Test' },
        nodeType: 'api-call'
      }
    })
    expect(wrapper.find('.node-property-panel').exists()).toBe(true)
  })
  
  it('should emit update event', async () => {
    const wrapper = mount(NodePropertyPanel, {
      props: {
        nodeData: { id: '1', type: 'api-call', label: 'Test' },
        nodeType: 'api-call'
      }
    })
    
    await wrapper.find('input').setValue('New Label')
    expect(wrapper.emitted('update')).toBeTruthy()
  })
})
```

### 2. 集成测试

**工作流设计器测试**
```typescript
describe('Workflow Designer Integration', () => {
  it('should create and configure node', async () => {
    const wrapper = mount(Designer)
    
    // 创建节点
    await wrapper.find('.node-item[data-type="api-call"]').trigger('click')
    
    // 配置节点
    await wrapper.find('.node-container').trigger('click')
    expect(wrapper.find('.node-property-panel').exists()).toBe(true)
    
    // 更新配置
    await wrapper.find('.node-property-panel input').setValue('API Call')
    expect(wrapper.find('.node-title').text()).toBe('API Call')
  })
})
```

## 最佳实践

### 1. 组件设计

**单一职责原则**
- 每个组件专注于特定功能
- 避免组件过于复杂

**可复用性**
- 提取公共组件和工具函数
- 使用插槽支持内容定制

**可测试性**
- 组件逻辑清晰，便于测试
- 避免复杂的副作用

### 2. 状态管理

**响应式设计**
```typescript
// 使用Pinia进行状态管理
export const useWorkflowStore = defineStore('workflow', () => {
  const nodes = ref<NodeData[]>([])
  const selectedNode = ref<NodeData | null>(null)
  
  const updateNode = (nodeId: string, updates: Partial<NodeData>) => {
    const node = nodes.value.find(n => n.id === nodeId)
    if (node) {
      Object.assign(node, updates)
    }
  }
  
  return {
    nodes,
    selectedNode,
    updateNode
  }
})
```

### 3. 错误处理

**统一错误处理**
```typescript
const handleError = (error: Error, context: string) => {
  console.error(`Error in ${context}:`, error)
  ElMessage.error(`操作失败: ${error.message}`)
}

// 在组件中使用
try {
  await updateNodeConfig(nodeId, config)
} catch (error) {
  handleError(error as Error, 'updateNodeConfig')
}
```

## 总结

前端开发指南涵盖了项目的核心技术栈、开发规范和最新的功能实现。通过遵循这些指南，可以确保：

### 主要成果
1. **统一的开发规范**: 代码风格一致，易于维护
2. **现代化的技术栈**: Vue 3 + TypeScript + Vite
3. **优化的用户体验**: 节点库优化、属性配置、长方形节点支持
4. **完善的测试策略**: 单元测试和集成测试覆盖

### 技术亮点
- **响应式设计**: CSS Grid + Flexbox混合布局
- **组件化架构**: 高度模块化的组件设计
- **类型安全**: 完整的TypeScript类型定义
- **性能优化**: 懒加载、防抖、虚拟滚动等优化策略

这些改进显著提升了开发效率和用户体验，为后续功能扩展奠定了坚实基础。