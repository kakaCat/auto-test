import ButtonRenderer from './ButtonRenderer.vue'
import InputRenderer from './InputRenderer.vue'
import TextRenderer from './TextRenderer.vue'
import ImageRenderer from './ImageRenderer.vue'
import FormRenderer from './FormRenderer.vue'
import SelectRenderer from './SelectRenderer.vue'
import CheckboxRenderer from './CheckboxRenderer.vue'
import RadioRenderer from './RadioRenderer.vue'
import ContainerRenderer from './ContainerRenderer.vue'
import GridRenderer from './GridRenderer.vue'
import TabsRenderer from './TabsRenderer.vue'

// 组件渲染器映射
export const componentRenderers = {
  // 基础组件
  button: ButtonRenderer,
  input: InputRenderer,
  text: TextRenderer,
  image: ImageRenderer,
  // 表单组件
  form: FormRenderer,
  select: SelectRenderer,
  checkbox: CheckboxRenderer,
  radio: RadioRenderer,
  // 布局组件
  container: ContainerRenderer,
  grid: GridRenderer,
  tabs: TabsRenderer
}

// 获取组件渲染器
export function getComponentRenderer(type) {
  return componentRenderers[type] || 'div'
}

export {
  ButtonRenderer,
  InputRenderer,
  TextRenderer,
  ImageRenderer,
  FormRenderer,
  SelectRenderer,
  CheckboxRenderer,
  RadioRenderer,
  ContainerRenderer,
  GridRenderer,
  TabsRenderer
}