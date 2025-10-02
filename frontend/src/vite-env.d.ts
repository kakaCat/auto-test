/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_UNIFIED_API_BASE_URL: string
  readonly VITE_API_VERSION: string
  readonly VITE_USE_UNIFIED_API: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 让 TypeScript 认识 .vue 单文件组件的导入
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}