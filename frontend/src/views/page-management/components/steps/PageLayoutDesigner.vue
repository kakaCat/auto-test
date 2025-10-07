<template>
  <div class="page-layout-designer">
    <div class="designer-container">
      <!-- 左侧组件库 -->
      <div
        class="component-library"
        :class="{ collapsed: leftPanelCollapsed }"
      >
        <div class="library-header">
          <div class="header-content">
            <h3 v-show="!leftPanelCollapsed">
              组件库
            </h3>
            <el-button
              type="text"
              size="small"
              class="collapse-btn"
              @click="toggleLeftPanel"
            >
              <el-icon>
                <component :is="leftPanelCollapsed ? 'Expand' : 'Fold'" />
              </el-icon>
            </el-button>
          </div>
          <el-input
            v-show="!leftPanelCollapsed"
            v-model="searchKeyword"
            placeholder="搜索组件"
            size="small"
            clearable
          />
        </div>
        
        <div class="component-categories">
          <div
            v-for="category in componentCategories"
            :key="category.name"
            class="category-section"
          >
            <div class="category-title">
              {{ category.label }}
            </div>
            <div class="component-list">
              <div
                v-for="component in category.components"
                :key="component.type"
                class="component-item"
                draggable="true"
                @dragstart="handleDragStart($event, component)"
              >
                <el-icon :size="20">
                  <component :is="component.icon" />
                </el-icon>
                <span>{{ component.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间设计画布 -->
      <div class="design-canvas">
        <div class="canvas-toolbar">
          <div class="toolbar-left">
            <el-button-group>
              <el-button
                size="small"
                @click="zoomOut"
              >
                <el-icon><ZoomOut /></el-icon>
              </el-button>
              <el-button size="small">
                {{ Math.round(canvasScale * 100) }}%
              </el-button>
              <el-button
                size="small"
                @click="zoomIn"
              >
                <el-icon><ZoomIn /></el-icon>
              </el-button>
            </el-button-group>
            <el-divider direction="vertical" />
            <el-button
              size="small"
              @click="toggleGrid"
            >
              <el-icon><Grid /></el-icon>
              网格
            </el-button>
          </div>
          <div class="toolbar-right">
            <el-button-group>
              <el-button
                size="small"
                :type="previewMode === 'desktop' ? 'primary' : ''"
                @click="previewMode = 'desktop'"
              >
                <el-icon><Monitor /></el-icon>
              </el-button>
              <el-button
                size="small"
                :type="previewMode === 'tablet' ? 'primary' : ''"
                @click="previewMode = 'tablet'"
              >
                <el-icon><Monitor /></el-icon>
              </el-button>
              <el-button
                size="small"
                :type="previewMode === 'mobile' ? 'primary' : ''"
                @click="previewMode = 'mobile'"
              >
                <el-icon><Iphone /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>

        <div
          class="canvas-container"
          :style="canvasContainerStyle"
        >
          <div
            class="canvas"
            :class="{ 'show-grid': showGrid }"
            :style="canvasStyle"
            @drop="handleDrop"
            @dragover="handleDragOver"
          >
            <!-- 渲染组件 -->
            <div
              v-for="component in layoutData.components"
              :key="component.id"
              class="canvas-component"
              :style="getComponentStyle(component)"
              :class="{ selected: selectedComponent?.id === component.id }"
              @click="selectComponent(component)"
            >
              <component
                :is="getComponentRenderer(component.type)"
                :component-data="component"
              />
              
              <!-- 选中状态的控制点 -->
              <div
                v-if="selectedComponent?.id === component.id"
                class="resize-handles"
              >
                <div class="resize-handle nw" />
                <div class="resize-handle ne" />
                <div class="resize-handle sw" />
                <div class="resize-handle se" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧属性面板 -->
      <div
        class="property-panel"
        :class="{ collapsed: rightPanelCollapsed }"
      >
        <div class="panel-header">
          <div class="header-content">
            <h3 v-show="!rightPanelCollapsed">
              属性配置
            </h3>
            <el-button
              type="text"
              size="small"
              class="collapse-btn"
              @click="toggleRightPanel"
            >
              <el-icon>
                <component :is="rightPanelCollapsed ? 'Expand' : 'Fold'" />
              </el-icon>
            </el-button>
          </div>
        </div>
        
        <div
          v-if="!rightPanelCollapsed"
          class="property-content"
        >
          <div v-if="selectedComponent">
            <el-form
              label-width="80px"
              size="small"
            >
              <el-form-item label="组件名称">
                <el-input v-model="selectedComponent.name" />
              </el-form-item>
              
              <el-form-item label="宽度">
                <el-input-number
                  v-model="selectedComponent.position.width"
                  :min="10"
                  :max="1000"
                  controls-position="right"
                />
              </el-form-item>
              
              <el-form-item label="高度">
                <el-input-number
                  v-model="selectedComponent.position.height"
                  :min="10"
                  :max="1000"
                  controls-position="right"
                />
              </el-form-item>
              
              <el-form-item label="X坐标">
                <el-input-number
                  v-model="selectedComponent.position.x"
                  :min="0"
                  controls-position="right"
                />
              </el-form-item>
              
              <el-form-item label="Y坐标">
                <el-input-number
                  v-model="selectedComponent.position.y"
                  :min="0"
                  controls-position="right"
                />
              </el-form-item>
            </el-form>
          </div>
          
          <div
            v-else
            class="no-selection"
          >
            <p>请选择一个组件来编辑属性</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { 
  ZoomOut, ZoomIn, Grid, Monitor, Iphone, Expand, Fold,
  Plus, Edit, Document, Picture, ArrowDown, Check, CircleCheck, Folder
} from '@element-plus/icons-vue'
import type { PageLayout, PageComponent } from '../../types/page-config'
import { getComponentRenderer as getComponentRendererFromMap } from '../renderers/index.js'

const props = defineProps<{
  modelValue: PageLayout
}>()

const emit = defineEmits<{
  'update:modelValue': [value: PageLayout]
  'validate': [stepIndex: number, isValid: boolean]
}>()

// 响应式数据
const searchKeyword = ref('')
const canvasScale = ref(1)
const showGrid = ref(true)
const previewMode = ref<'desktop' | 'tablet' | 'mobile'>('desktop')
const selectedComponent = ref<PageComponent | null>(null)
const leftPanelCollapsed = ref(false)
const rightPanelCollapsed = ref(false)

// 布局数据
const layoutData = reactive<PageLayout>({ ...props.modelValue })

// 组件分类
const componentCategories = [
  {
    name: 'basic',
    label: '基础组件',
    components: [
      { type: 'button', label: '按钮', icon: Plus },
      { type: 'input', label: '输入框', icon: Edit },
      { type: 'text', label: '文本', icon: Document },
      { type: 'image', label: '图片', icon: Picture }
    ]
  },
  {
    name: 'form',
    label: '表单组件',
    components: [
      { type: 'form', label: '表单', icon: Document },
      { type: 'select', label: '选择器', icon: ArrowDown },
      { type: 'checkbox', label: '复选框', icon: Check },
      { type: 'radio', label: '单选框', icon: CircleCheck }
    ]
  },
  {
    name: 'layout',
    label: '布局组件',
    components: [
      { type: 'container', label: '容器', icon: Grid },
      { type: 'grid', label: '栅格', icon: Grid },
      { type: 'tabs', label: '标签页', icon: Folder }
    ]
  }
]

// 计算属性
const canvasStyle = computed(() => {
  const baseWidth = previewMode.value === 'desktop' ? 1200 : 
                    previewMode.value === 'tablet' ? 768 : 375
  const baseHeight = 800
  
  return {
    width: `${baseWidth}px`,
    height: `${baseHeight}px`,
    transform: `scale(${canvasScale.value})`,
    transformOrigin: 'top left',
    minHeight: '400px'
  }
})

// 画布容器样式
const canvasContainerStyle = computed(() => {
  const baseWidth = previewMode.value === 'desktop' ? 1200 : 
                    previewMode.value === 'tablet' ? 768 : 375
  const baseHeight = 800
  
  return {
    width: `${baseWidth * canvasScale.value + 40}px`,
    height: `${baseHeight * canvasScale.value + 40}px`,
    minWidth: '100%',
    minHeight: '100%'
  }
})

// 监听数据变化
watch(layoutData, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

watch(() => props.modelValue, (newVal) => {
  Object.assign(layoutData, newVal)
}, { deep: true })

// 拖拽开始
const handleDragStart = (event: DragEvent, component: any) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('component', JSON.stringify(component))
  }
}

// 拖拽悬停
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
}

// 拖拽放置
const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  
  if (event.dataTransfer) {
    const componentData = JSON.parse(event.dataTransfer.getData('component'))
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    
    const newComponent: PageComponent = {
      id: `component_${Date.now()}`,
      type: componentData.type,
      name: componentData.label,
      props: {},
      style: {},
      position: {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
        z: layoutData.components.length,
        width: 100,
        height: 40
      }
    }
    
    layoutData.components.push(newComponent)
  }
}

// 选择组件
const selectComponent = (component: PageComponent) => {
  selectedComponent.value = component
}

// 获取组件样式
const getComponentStyle = (component: PageComponent) => {
  return {
    position: 'absolute' as const,
    left: `${component.position.x}px`,
    top: `${component.position.y}px`,
    width: `${component.position.width}px`,
    height: `${component.position.height}px`,
    zIndex: component.position.z
  }
}

// 获取组件渲染器
const getComponentRenderer = (type: string) => {
  return getComponentRendererFromMap(type)
}

// 缩放操作
const zoomIn = () => {
  if (canvasScale.value < 2) {
    canvasScale.value += 0.1
  }
}

const zoomOut = () => {
  if (canvasScale.value > 0.3) {
    canvasScale.value -= 0.1
  }
}

// 切换网格
const toggleGrid = () => {
  showGrid.value = !showGrid.value
}

// 切换左侧面板
const toggleLeftPanel = () => {
  leftPanelCollapsed.value = !leftPanelCollapsed.value
}

// 切换右侧面板
const toggleRightPanel = () => {
  rightPanelCollapsed.value = !rightPanelCollapsed.value
}

// 验证方法
const validate = async () => {
  // 简单验证：至少有一个组件
  const isValid = layoutData.components.length > 0
  emit('validate', 1, isValid)
  return isValid
}

defineExpose({
  validate
})
</script>

<style lang="scss" scoped>
.page-layout-designer {
  height: calc(100vh - 200px);
  min-height: 600px;
  
  .designer-container {
    display: flex;
    height: 100%;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    overflow: hidden;
  }

  .component-library {
    width: 250px;
    min-width: 250px;
    background-color: #f8f9fa;
    border-right: 1px solid #e4e7ed;
    overflow-y: auto;
    transition: width 0.3s ease;

    &.collapsed {
      width: 48px;
      min-width: 48px;
    }

    .library-header {
      padding: 16px;
      border-bottom: 1px solid #e4e7ed;

      .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
      }

      h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
      }

      .collapse-btn {
        padding: 4px;
        min-height: auto;
      }
    }

    .category-section {
      .category-title {
        padding: 12px 16px 8px;
        font-size: 12px;
        font-weight: 600;
        color: #909399;
        background-color: #f0f0f0;
      }

      .component-list {
        .component-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          cursor: grab;
          transition: background-color 0.2s;
          color: #303133;

          &:hover {
            background-color: #e6f7ff;
          }

          &:active {
            cursor: grabbing;
          }

          .el-icon {
            color: #606266;
            font-size: 16px;
          }

          span {
            font-size: 12px;
            color: #303133;
          }
        }
      }
    }
  }

  .design-canvas {
    flex: 1;
    min-width: 400px;
    display: flex;
    flex-direction: column;

    .canvas-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 16px;
      background-color: #fff;
      border-bottom: 1px solid #e4e7ed;
      flex-shrink: 0;

      .toolbar-left,
      .toolbar-right {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .canvas-container {
      flex: 1;
      overflow: auto;
      background-color: #f5f5f5;
      position: relative;
      min-height: 400px;

      .canvas {
        background-color: #fff;
        margin: 20px;
        min-height: calc(100% - 40px);
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        &.show-grid {
          background-image: 
            linear-gradient(to right, #f0f0f0 1px, transparent 1px),
            linear-gradient(to bottom, #f0f0f0 1px, transparent 1px);
          background-size: 20px 20px;
        }

        .canvas-component {
          border: 1px dashed transparent;
          cursor: pointer;

          &.selected {
            border-color: #409eff;
          }

          &:hover {
            border-color: #409eff;
          }

          .resize-handles {
            .resize-handle {
              position: absolute;
              width: 8px;
              height: 8px;
              background-color: #409eff;
              border: 1px solid #fff;
              cursor: nw-resize;

              &.nw { top: -4px; left: -4px; }
              &.ne { top: -4px; right: -4px; cursor: ne-resize; }
              &.sw { bottom: -4px; left: -4px; cursor: sw-resize; }
              &.se { bottom: -4px; right: -4px; cursor: se-resize; }
            }
          }
        }
      }
    }
  }

  .property-panel {
    width: 280px;
    min-width: 280px;
    background-color: #f8f9fa;
    border-left: 1px solid #e4e7ed;
    overflow-y: auto;
    transition: width 0.3s ease;

    &.collapsed {
      width: 48px;
      min-width: 48px;
    }

    .panel-header {
      padding: 16px;
      border-bottom: 1px solid #e4e7ed;

      .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
      }

      .collapse-btn {
        padding: 4px;
        min-height: auto;
      }
    }

    .property-content {
      padding: 16px;
    }

    .no-selection {
      padding: 40px 16px;
      text-align: center;
      color: #909399;
      font-size: 12px;
    }
  }

  // 响应式设计
  @media (max-width: 1200px) {
    .component-library {
      width: 200px;
      min-width: 200px;
      
      &.collapsed {
        width: 48px;
        min-width: 48px;
      }
    }

    .property-panel {
      width: 240px;
      min-width: 240px;
      
      &.collapsed {
        width: 48px;
        min-width: 48px;
      }
    }
  }

  @media (max-width: 768px) {
    .page-layout-designer {
      height: calc(100vh - 120px);
    }

    .component-library {
      width: 48px;
      min-width: 48px;
    }

    .property-panel {
      width: 48px;
      min-width: 48px;
    }

    .design-canvas {
      min-width: 300px;
    }
  }
}
</style>