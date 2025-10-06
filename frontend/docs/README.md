# 前端项目文档

## 📋 项目概述

本项目是基于Vue 3 + TypeScript + Vite的现代化前端应用，提供自动化测试平台的用户界面。

## 📁 文档结构

### 🔧 API文档
- [API重构总结](./api/refactor-summary.md)
  - [API重构计划](./api/refactor-plan.md)

### 📖 开发指南
- **[guides/](./guides/)** - 开发指南和最佳实践
  - [内联配置测试](./guides/inline-config-test.md)

### 🧩 组件文档
- **[components/](./components/)** - 组件文档（待完善）

### 📝 变更记录
- **[changelogs/](./changelogs/)** - 项目变更记录（待完善）

## 🚀 快速开始

1. **环境准备**
   ```bash
   npm install
   npm run dev
   ```

2. **开发规范**
   - 阅读 [API架构](./api/README.md) 与 [API重构计划](./api/refactor-plan.md)

3. **项目结构**
   ```
   src/
   ├── api/          # API接口层
   ├── components/   # 通用组件
   ├── views/        # 页面组件
   ├── stores/       # 状态管理
   └── utils/        # 工具函数
   ```

## 🔗 相关链接

- [项目根目录](../)
- [源码目录](../src/)
- [系统文档](../../docs/)

## 📞 技术支持

如有问题，请：
1. 查看相关文档
2. 检查控制台错误
3. 联系开发团队

---

**技术栈**: Vue 3 + TypeScript + Vite + Element Plus  
**最后更新**: 2024年1月15日

## 🧪 参数保存与应用集成

- 新增组件：`ParameterSaveDialog.vue` 支持批量将选中场景标记为“已保存参数”。
- 新增组件：`SavedParametersList.vue` 列出当前 API 下标记为“已保存参数”的场景，支持筛选与“应用参数”。
- 抽屉页面：`ApiTestScenarioDrawer.vue` 集成以上组件，并在“应用参数”时：
  - 拉取场景详情，提取 `variables` 与 `config`。
  - 通过事件 `params-applied` 抛给父组件，包含 `{ scenarioId, variables, config, detail }`。
- 页面接入：`views/api-management/index.vue` 监听 `@params-applied`，将参数保存到本页的 `appliedParams`，用于后续测试或编排。

使用提示：
- 在 API 列表中打开“场景测试”抽屉，批量选择场景，点击“保存参数”。
- 在“已保存参数”列表中选择某一场景，点击“应用参数”，父页面会收到参数并提示成功。

## 🔤 类型声明与Vite环境

- 合并 TypeScript SFC 声明：将 `declare module '*.vue'` 合到 `src/vite-env.d.ts`，避免分散声明文件。
- 作用：解决 `Cannot find module './X.vue'` 或缺少类型声明的诊断，提供 `.vue` 导入的类型识别与提示。
- 注意：`auto-imports.d.ts` 与 `components.d.ts` 由插件自动生成，仅用于类型提示，不建议手动编辑。