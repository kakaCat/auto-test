# 组件开发指南

## 📋 目录

1. [组件设计原则](#组件设计原则)
2. [组件分类与职责](#组件分类与职责)
3. [组件开发流程](#组件开发流程)
4. [组件通信模式](#组件通信模式)
5. [组件测试策略](#组件测试策略)
6. [组件文档规范](#组件文档规范)
7. [实际案例分析](#实际案例分析)

## 🎯 组件设计原则

### 1. 单一职责原则 (SRP)
每个组件应该只有一个明确的职责，避免功能过于复杂。

```vue
<!-- ❌ 错误：一个组件承担太多职责 -->
<template>
  <div class="user-management">
    <!-- 搜索表单 -->
    <form>...</form>
    <!-- 数据表格 -->
    <table>...</table>
    <!-- 分页组件 -->
    <pagination>...</pagination>
    <!-- 新增/编辑弹框 -->
    <dialog>...</dialog>
  </div>
</template>

<!-- ✅ 正确：拆分为多个专职组件 -->
<template>
  <div class="user-management">
    <UserSearchForm @search="handleSearch" />
    <UserDataTable :data="users" @edit="handleEdit" />
    <UserPagination @change="handlePageChange" />
    <UserFormDialog v-model:visible="dialogVisible" />
  </div>
</template>
```

### 2. 开放封闭原则 (OCP)
组件应该对扩展开放，对修改封闭。

```vue
<!-- 基础表格组件 - 对扩展开放 -->
<template>
  <el-table :data="data" v-bind="$attrs">
    <el-table-column
      v-for="column in columns"
      :key="column.prop"
      v-bind="column"
    >
      <template #default="scope" v-if="column.slot">
        <slot :name="column.slot" :row="scope.row" :index="scope.$index" />
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
// 通过 props 和 slots 实现扩展
defineProps<{
  data: any[]
  columns: TableColumn[]
}>()
</script>
```

### 3. 依赖倒置原则 (DIP)
组件应该依赖抽象而不是具体实现。

```typescript
// ❌ 错误：直接依赖具体的 API 实现
const UserList = defineComponent({
  setup() {
    const users = ref([])
    
    const loadUsers = async () => {
      // 直接调用具体的 API
      const response = await axios.get('/api/users')
      users.value = response.data
    }
    
    return { users, loadUsers }
  }
})

// ✅ 正确：依赖抽象的服务接口
const UserList = defineComponent({
  props: {
    userService: {
      type: Object as PropType<UserService>,
      required: true
    }
  },
  setup(props) {
    const users = ref([])
    
    const loadUsers = async () => {
      // 通过抽象接口调用
      users.value = await props.userService.getUsers()
    }
    
    return { users, loadUsers }
  }
})
```

## 🏗️ 组件分类与职责

### 1. 基础组件 (Base Components)
提供最基本的 UI 元素，高度可复用。

```vue
<!-- BaseButton.vue -->
<template>
  <button 
    :class="buttonClass"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup>
interface Props {
  type?: 'primary' | 'secondary' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClass = computed(() => [
  'base-button',
  `base-button--${props.type}`,
  `base-button--${props.size}`,
  {
    'base-button--disabled': props.disabled,
    'base-button--loading': props.loading
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
```

### 2. 业务组件 (Business Components)
封装特定业务逻辑的组件。

```vue
<!-- ApiFormDialog.vue -->
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="600px"
    @close="handleClose"
  >
    <ApiForm
      ref="formRef"
      :form-data="localFormData"
      :available-modules="availableModules"
      @update:form-data="updateFormData"
    />
    
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
// 业务组件专注于业务逻辑和数据流转
interface Props {
  visible: boolean
  title: string
  formData: ApiFormData
  availableModules: Module[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  save: [data: ApiFormData]
  cancel: []
}>()

// 内部状态管理
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const localFormData = ref({ ...props.formData })

// 业务逻辑处理
const handleSave = async () => {
  try {
    await formRef.value?.validate()
    emit('save', localFormData.value)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}
</script>
```

### 3. 布局组件 (Layout Components)
负责页面结构和布局。

```vue
<!-- PageLayout.vue -->
<template>
  <div class="page-layout">
    <header class="page-layout__header">
      <slot name="header" />
    </header>
    
    <aside class="page-layout__sidebar" v-if="$slots.sidebar">
      <slot name="sidebar" />
    </aside>
    
    <main class="page-layout__content">
      <slot />
    </main>
    
    <footer class="page-layout__footer" v-if="$slots.footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup>
// 布局组件通常只处理结构，不包含业务逻辑
interface Props {
  sidebarWidth?: string
  headerHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  sidebarWidth: '240px',
  headerHeight: '60px'
})
</script>

<style scoped>
.page-layout {
  display: grid;
  grid-template-areas: 
    "header header"
    "sidebar content"
    "footer footer";
  grid-template-rows: v-bind(headerHeight) 1fr auto;
  grid-template-columns: v-bind(sidebarWidth) 1fr;
  min-height: 100vh;
}

.page-layout__header {
  grid-area: header;
}

.page-layout__sidebar {
  grid-area: sidebar;
}

.page-layout__content {
  grid-area: content;
}

.page-layout__footer {
  grid-area: footer;
}
</style>
```

## 🔄 组件开发流程

### 1. 需求分析阶段
```markdown
## 组件需求分析模板

### 组件名称
ApiFormDialog

### 功能描述
用于新增和编辑API信息的弹框组件

### 使用场景
- API管理页面的新增API功能
- API管理页面的编辑API功能
- 其他需要API表单输入的场景

### 输入输出
**输入 (Props):**
- visible: boolean - 控制弹框显示
- title: string - 弹框标题
- formData: ApiFormData - 表单数据
- availableModules: Module[] - 可选模块列表

**输出 (Events):**
- save: (data: ApiFormData) => void - 保存事件
- cancel: () => void - 取消事件

### 依赖组件
- ApiForm - 表单组件
- el-dialog - Element Plus 弹框

### 状态管理
- 内部状态：表单验证状态、加载状态
- 外部状态：弹框显示状态、表单数据
```

### 2. 设计阶段
```typescript
// 组件接口设计
interface ApiFormDialogProps {
  visible: boolean
  title: string
  formData: ApiFormData
  availableModules: Module[]
}

interface ApiFormDialogEmits {
  'update:visible': [value: boolean]
  save: [data: ApiFormData]
  cancel: []
}

// 组件内部状态设计
interface ComponentState {
  loading: boolean
  validating: boolean
  localFormData: ApiFormData
}

// 组件方法设计
interface ComponentMethods {
  validate(): Promise<boolean>
  resetForm(): void
  handleSave(): Promise<void>
  handleCancel(): void
}
```

### 3. 实现阶段
```vue
<template>
  <!-- 模板实现 -->
</template>

<script setup lang="ts">
// 1. 类型定义
// 2. Props 和 Emits 定义
// 3. 响应式数据
// 4. 计算属性
// 5. 方法实现
// 6. 生命周期钩子
// 7. 暴露的方法
</script>

<style scoped>
/* 样式实现 */
</style>
```

### 4. 测试阶段
```typescript
// 组件测试
describe('ApiFormDialog', () => {
  it('应该正确显示弹框', () => {
    // 测试显示逻辑
  })
  
  it('应该正确处理表单提交', async () => {
    // 测试提交逻辑
  })
  
  it('应该正确处理取消操作', () => {
    // 测试取消逻辑
  })
})
```

## 📡 组件通信模式

### 1. Props Down, Events Up
最基本的父子组件通信模式。

```vue
<!-- 父组件 -->
<template>
  <UserForm
    :user-data="userData"
    :loading="loading"
    @save="handleSave"
    @cancel="handleCancel"
  />
</template>

<!-- 子组件 -->
<script setup>
const props = defineProps<{
  userData: UserData
  loading: boolean
}>()

const emit = defineEmits<{
  save: [data: UserData]
  cancel: []
}>()
</script>
```

### 2. v-model 双向绑定
用于表单组件的双向数据绑定。

```vue
<!-- 自定义输入组件 -->
<template>
  <input
    :value="modelValue"
    @input="updateValue"
    @blur="handleBlur"
  />
</template>

<script setup>
const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const updateValue = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<!-- 使用组件 -->
<template>
  <CustomInput v-model="inputValue" />
</template>
```

### 3. Provide/Inject 依赖注入
用于跨层级组件通信。

```vue
<!-- 祖先组件 -->
<script setup>
import { provide } from 'vue'

const userService = new UserService()
const themeConfig = reactive({
  primaryColor: '#409eff',
  fontSize: '14px'
})

provide('userService', userService)
provide('themeConfig', themeConfig)
</script>

<!-- 后代组件 -->
<script setup>
import { inject } from 'vue'

const userService = inject<UserService>('userService')
const themeConfig = inject<ThemeConfig>('themeConfig')

if (!userService) {
  throw new Error('userService not provided')
}
</script>
```

### 4. 组合式函数 (Composables)
封装可复用的逻辑。

```typescript
// composables/useApiForm.ts
export function useApiForm(initialData?: ApiFormData) {
  const form = reactive<ApiFormData>({
    ...defaultFormData,
    ...initialData
  })
  
  const loading = ref(false)
  const errors = ref<Record<string, string>>({})
  
  const validate = async (): Promise<boolean> => {
    errors.value = {}
    
    if (!form.name) {
      errors.value.name = 'API名称不能为空'
    }
    
    if (!form.url) {
      errors.value.url = 'URL不能为空'
    }
    
    return Object.keys(errors.value).length === 0
  }
  
  const reset = () => {
    Object.assign(form, defaultFormData)
    errors.value = {}
  }
  
  const save = async (apiService: ApiService) => {
    if (!(await validate())) {
      throw new Error('表单验证失败')
    }
    
    loading.value = true
    try {
      if (form.id) {
        return await apiService.updateApi(form.id, form)
      } else {
        return await apiService.createApi(form)
      }
    } finally {
      loading.value = false
    }
  }
  
  return {
    form,
    loading,
    errors,
    validate,
    reset,
    save
  }
}

// 在组件中使用
<script setup>
const { form, loading, errors, validate, reset, save } = useApiForm()
</script>
```

## 🧪 组件测试策略

### 1. 单元测试
测试组件的独立功能。

```typescript
// tests/components/ApiForm.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import ApiForm from '@/components/ApiForm.vue'

describe('ApiForm', () => {
  const defaultProps = {
    formData: {
      name: '',
      version: '1.0',
      method: 'GET',
      url: '',
      description: ''
    },
    availableModules: [
      { id: '1', name: 'User Module' },
      { id: '2', name: 'Order Module' }
    ]
  }
  
  it('应该正确渲染表单字段', () => {
    const wrapper = mount(ApiForm, {
      props: defaultProps
    })
    
    expect(wrapper.find('[data-test="api-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="api-version"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="api-method"]').exists()).toBe(true)
  })
  
  it('应该正确验证必填字段', async () => {
    const wrapper = mount(ApiForm, {
      props: defaultProps
    })
    
    const result = await wrapper.vm.validate()
    expect(result).toBe(false)
    
    // 设置必填字段
    await wrapper.setProps({
      formData: {
        ...defaultProps.formData,
        name: 'Test API',
        url: '/api/test'
      }
    })
    
    const result2 = await wrapper.vm.validate()
    expect(result2).toBe(true)
  })
  
  it('应该正确触发数据更新事件', async () => {
    const wrapper = mount(ApiForm, {
      props: defaultProps
    })
    
    const nameInput = wrapper.find('[data-test="api-name"]')
    await nameInput.setValue('New API Name')
    
    expect(wrapper.emitted('update:form-data')).toBeTruthy()
    expect(wrapper.emitted('update:form-data')[0][0]).toMatchObject({
      name: 'New API Name'
    })
  })
})
```

### 2. 集成测试
测试组件之间的协作。

```typescript
// tests/integration/ApiManagement.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import ApiManagement from '@/views/api-management/index.vue'

describe('ApiManagement Integration', () => {
  it('应该正确处理新增API流程', async () => {
    const mockApiService = {
      createApi: vi.fn().mockResolvedValue({ id: '1', name: 'Test API' })
    }
    
    const wrapper = mount(ApiManagement, {
      global: {
        provide: {
          apiService: mockApiService
        }
      }
    })
    
    // 点击新增按钮
    await wrapper.find('[data-test="add-api-btn"]').trigger('click')
    
    // 弹框应该显示
    expect(wrapper.find('[data-test="api-form-dialog"]').isVisible()).toBe(true)
    
    // 填写表单
    const dialog = wrapper.findComponent({ name: 'ApiFormDialog' })
    await dialog.vm.updateFormData({
      name: 'Test API',
      version: '1.0',
      method: 'GET',
      url: '/api/test'
    })
    
    // 提交表单
    await dialog.find('[data-test="save-btn"]').trigger('click')
    
    // 验证API调用
    expect(mockApiService.createApi).toHaveBeenCalledWith({
      name: 'Test API',
      version: '1.0',
      method: 'GET',
      url: '/api/test'
    })
  })
})
```

### 3. 视觉回归测试
确保组件样式的一致性。

```typescript
// tests/visual/ApiForm.visual.test.ts
import { mount } from '@vue/test-utils'
import { describe, it } from 'vitest'
import ApiForm from '@/components/ApiForm.vue'

describe('ApiForm Visual Tests', () => {
  it('应该匹配默认状态的快照', () => {
    const wrapper = mount(ApiForm, {
      props: {
        formData: defaultFormData,
        availableModules: mockModules
      }
    })
    
    expect(wrapper.html()).toMatchSnapshot()
  })
  
  it('应该匹配错误状态的快照', async () => {
    const wrapper = mount(ApiForm, {
      props: {
        formData: defaultFormData,
        availableModules: mockModules
      }
    })
    
    // 触发验证错误
    await wrapper.vm.validate()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.html()).toMatchSnapshot()
  })
})
```

## 📚 组件文档规范

### 1. 组件头部注释
```vue
<!--
@component ApiFormDialog
@description API表单弹框组件，用于新增和编辑API信息
@author 开发者姓名
@since 2024-01-20
@version 1.0.0

@example
<ApiFormDialog
  v-model:visible="dialogVisible"
  :title="dialogTitle"
  :form-data="formData"
  :available-modules="modules"
  @save="handleSave"
  @cancel="handleCancel"
/>
-->
```

### 2. Props 文档
```typescript
interface Props {
  /** 控制弹框显示/隐藏 */
  visible: boolean
  
  /** 弹框标题 */
  title: string
  
  /** 
   * 表单数据
   * @default defaultFormData
   */
  formData?: ApiFormData
  
  /** 
   * 可选模块列表
   * @required
   */
  availableModules: Module[]
  
  /**
   * 弹框宽度
   * @default "600px"
   */
  width?: string
}
```

### 3. Events 文档
```typescript
interface Emits {
  /**
   * 弹框显示状态变更事件
   * @param value 新的显示状态
   */
  'update:visible': [value: boolean]
  
  /**
   * 保存事件
   * @param data 表单数据
   */
  save: [data: ApiFormData]
  
  /**
   * 取消事件
   */
  cancel: []
}
```

### 4. Slots 文档
```vue
<template>
  <div class="api-form-dialog">
    <!-- 
      @slot header
      @description 自定义弹框头部内容
      @binding {string} title - 弹框标题
    -->
    <slot name="header" :title="title">
      <h3>{{ title }}</h3>
    </slot>
    
    <!-- 
      @slot default
      @description 弹框主体内容
    -->
    <slot />
    
    <!-- 
      @slot footer
      @description 自定义弹框底部内容
      @binding {Function} save - 保存方法
      @binding {Function} cancel - 取消方法
    -->
    <slot name="footer" :save="handleSave" :cancel="handleCancel">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </slot>
  </div>
</template>
```

## 🎯 实际案例分析

### 案例：API管理页面组件化重构

#### 重构前的问题
```vue
<!-- 重构前：所有功能都在一个组件中 -->
<template>
  <div class="api-management">
    <!-- 搜索表单 -->
    <el-form>
      <!-- 大量表单字段 -->
    </el-form>
    
    <!-- 数据表格 -->
    <el-table>
      <!-- 大量表格列定义 -->
    </el-table>
    
    <!-- 新增/编辑弹框 -->
    <el-dialog>
      <el-form>
        <!-- 大量表单字段 -->
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
// 数百行代码混合在一起
// 搜索逻辑
// 表格逻辑  
// 表单逻辑
// API调用逻辑
</script>
```

#### 重构后的结构
```
api-management/
├── components/
│   ├── ApiForm.vue          # 表单组件
│   ├── ApiFormDialog.vue    # 弹框组件
│   ├── ApiSearchForm.vue    # 搜索组件
│   ├── ApiDataTable.vue     # 表格组件
│   └── index.js            # 组件入口
├── data/
│   ├── formConfig.js       # 表单配置
│   ├── tableColumns.js     # 表格配置
│   └── index.js           # 数据入口
├── composables/
│   ├── useApiForm.js       # 表单逻辑
│   ├── useApiTable.js      # 表格逻辑
│   └── useApiSearch.js     # 搜索逻辑
└── index.vue              # 主页面
```

#### 重构后的主页面
```vue
<template>
  <div class="api-management">
    <PageHeader title="API管理" />
    
    <ApiSearchForm 
      @search="handleSearch"
      @reset="handleReset"
    />
    
    <ApiDataTable
      :data="tableData"
      :loading="loading"
      @edit="handleEdit"
      @delete="handleDelete"
    />
    
    <ApiFormDialog
      v-model:visible="dialogVisible"
      :title="dialogTitle"
      :form-data="formData"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup>
// 主页面只负责协调各个组件
import { useApiManagement } from './composables/useApiManagement'

const {
  // 数据
  tableData,
  loading,
  dialogVisible,
  dialogTitle,
  formData,
  
  // 方法
  handleSearch,
  handleReset,
  handleEdit,
  handleDelete,
  handleSave,
  handleCancel
} = useApiManagement()
</script>
```

#### 重构收益
1. **可维护性提升**: 每个组件职责单一，易于维护
2. **可复用性增强**: 组件可以在其他页面复用
3. **可测试性改善**: 独立组件更容易编写测试
4. **开发效率提高**: 多人可以并行开发不同组件
5. **代码质量提升**: 代码结构更清晰，逻辑更分明

---

*本指南提供了组件开发的完整流程和最佳实践，请在实际开发中参考使用。*