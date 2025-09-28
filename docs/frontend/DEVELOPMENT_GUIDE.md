# 前端开发指南

## 📋 概述

本文档提供前端开发的完整指南，包括技术栈、项目结构、开发规范和环境配置。

## 🛠️ 技术栈

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

## 📁 项目结构

```
frontend/
├── src/
│   ├── api/                # API接口层
│   │   ├── core/          # 核心基础设施
│   │   ├── modules/       # 业务模块API
│   │   ├── converters/    # 数据转换层
│   │   ├── rules/         # 业务规则层
│   │   └── wrappers/      # 权限包装层
│   ├── components/        # 通用组件
│   │   ├── SystemTree.vue # 系统树组件
│   │   └── WorkflowWizard.vue # 工作流向导
│   ├── composables/       # 组合式函数
│   ├── views/             # 页面组件
│   │   ├── dashboard/     # 仪表板
│   │   ├── service-management/ # 系统管理
│   │   ├── api-management/ # API管理
│   │   ├── page-management/ # 页面管理
│   │   ├── workflow-orchestration/ # 工作流编排
│   │   ├── scenario-management/ # 场景管理
│   │   └── requirement-management/ # 需求管理
│   ├── stores/            # Pinia状态管理
│   ├── utils/             # 工具函数
│   ├── types/             # TypeScript类型定义
│   ├── styles/            # 样式文件
│   └── router/            # 路由配置
├── docs/                  # 文档
└── tests/                 # 测试文件
```

## 🔧 环境配置

### 环境变量配置
为统一前后端联调配置，前端使用统一端点变量：

#### 开发环境 (`.env.development`)
```bash
VITE_UNIFIED_API_BASE_URL=http://127.0.0.1:8000
```

#### 其他环境
```bash
# .env.staging
VITE_UNIFIED_API_BASE_URL=https://staging.api.company.com

# .env.production
VITE_UNIFIED_API_BASE_URL=https://api.company.com
```

### Vite 代理配置
```typescript
// vite.config.js
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const targetBase = env.VITE_UNIFIED_API_BASE_URL || 'http://127.0.0.1:8000'
  
  return {
    server: {
      proxy: {
        '/api': { 
          target: targetBase, 
          changeOrigin: true 
        }
      }
    }
  }
})
```

## 📝 开发规范

### 代码规范
- **组件命名**: 使用 PascalCase
- **文件命名**: 使用 kebab-case
- **变量命名**: 使用 camelCase
- **常量命名**: 使用 UPPER_SNAKE_CASE

### TypeScript 规范
- 优先使用接口而非类型别名
- 避免使用 `any` 类型，优先使用 `unknown`
- 为异步函数返回 `Promise<T>`
- 使用严格模式 (`strict: true`)

### Vue 3 规范
- 优先使用 Composition API
- 使用 `<script setup>` 语法
- 合理使用响应式 API (`ref`, `reactive`, `computed`)
- 正确处理生命周期钩子

### API 调用规范
- 业务API端点以 `/api/...` 开头
- 使用统一的错误处理机制
- 实现适当的加载状态管理
- 添加必要的缓存策略

## 🏗️ 架构设计原则

### 防腐层设计
- **API防腐层**: 封装HTTP请求，统一错误处理
- **数据转换防腐层**: 标准化数据格式，屏蔽后端差异
- **业务逻辑防腐层**: 封装业务规则，协调数据流

### 分层职责
- **组件层**: 用户交互，数据展示
- **Composable层**: 状态管理，业务逻辑协调
- **API层**: 数据获取，接口封装
- **工具层**: 通用功能，辅助方法

### 命名规范
- **API类**: `{Domain}Api` (如 `SystemApi`)
- **数据对象**: `{Domain}Data` (如 `SystemData`)
- **Composable**: `use{Domain}Data` (如 `useSystemData`)
- **组件**: `{Function}Component` (如 `SystemTree`)

## 🚀 开发流程

### 1. 环境准备
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

### 2. 新功能开发
1. **创建分支**: `feature/功能名称`
2. **设计API**: 遵循统一的API设计规范
3. **实现组件**: 遵循组件开发规范
4. **编写测试**: 确保功能正确性
5. **更新文档**: 同步更新用户指南

### 3. 代码提交
```bash
# 代码检查
npm run lint:fix

# 类型检查
npm run type-check

# 运行测试
npm run test

# 提交代码
git commit -m "feat: 功能描述"
```

## 🧪 测试策略

### 单元测试
- 使用 Vitest 进行单元测试
- 测试覆盖率目标: 80%+
- 重点测试业务逻辑和工具函数

### 集成测试
- 测试组件间的交互
- 验证API调用的正确性
- 确保数据流的完整性

### E2E测试
- 使用 Playwright 进行端到端测试
- 覆盖主要用户操作流程
- 验证系统的整体功能

## 📊 性能优化

### 代码分割
- 路由级别的代码分割
- 组件级别的懒加载
- 第三方库的按需引入

### 缓存策略
- API响应缓存
- 组件状态缓存
- 静态资源缓存

### 打包优化
- Tree shaking
- 压缩和混淆
- 资源优化

## 🔍 调试指南

### 开发工具
- Vue DevTools
- TypeScript 语言服务
- ESLint 和 Prettier

### 常见问题
- 组件状态不更新
- API调用失败
- 路由跳转异常
- 性能问题定位

## 📚 参考资源

### 官方文档
- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Element Plus 官方文档](https://element-plus.org/)
- [Vite 官方文档](https://vitejs.dev/)

### 内部文档
- [用户指南](./user-guides/) - 系统功能使用指南
- [API重构文档](./API_REFACTORING_*.md) - API层重构方案
- [问题解决指南](./TROUBLESHOOTING.md) - 常见问题解决

---

**文档版本**: v2.0  
**最后更新**: 2024年1月  
**维护者**: 前端开发团队