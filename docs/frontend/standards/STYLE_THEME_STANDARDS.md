# 样式与主题化规范（Style & Theming Standards）

> Status: Stable
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Tags: frontend, standards, style, theme

## 适用范围
- 适用于 `frontend/` 项目的样式系统与主题化实现（CSS Variables、SCSS、Element Plus）。
- 与组件文档规范、编码规范协同；示例与实践位于 `frontend/src/styles/` 与各组件目录。

## 基本原则
- Token化：颜色/间距/字号等统一使用 CSS 变量管理（如 `--color-primary`）。
- 主题隔离：将主题切换实现为变量集切换，避免在组件内硬编码主题值。
- 层级清晰：全局样式 → 组件局部样式 → 页面特定样式，避免全局污染。

## 命名与组织
- CSS 变量命名：`--color-*`、`--spacing-*`、`--font-size-*`、`--radius-*`。
- 类名规范：优先使用 CSS Modules 或 BEM；避免深层选择器与 `!important`。
- 文件组织：`src/styles/tokens.css`（变量）、`src/styles/global.scss`（全局），组件内 `*.module.scss`。

## 主题切换
- 使用 `data-theme="light|dark"` 挂载在 `html/body`，通过切换变量集合实现主题切换。
- 组件对比度与可达性：保证暗色与浅色主题对比度达到 WCAG AA。
- 动态切换：避免强制重绘；仅切换变量，提升性能。

## 组件样式
- 组件局部样式与状态类限定在组件作用域；禁用全局覆盖除非在 `global.scss` 中集中声明。
- Element Plus 主题覆盖：在 tokens 层映射统一主色、副色、提示色。

## 可达性（A11y）
- 焦点样式可见且一致；禁用移除焦点环的做法。
- 颜色对比度与字体大小符合规范；为图标与图形元素提供可替代文本说明。

## 示例：变量与主题
```css
/* tokens.css */
:root {
  --color-primary: #409eff;
  --color-success: #67c23a;
  --color-warning: #e6a23c;
  --color-error: #f56c6c;
  --spacing-2: 2px; /* 以8px为基准倍数 */
  --spacing-4: 4px;
  --radius-sm: 4px;
}

:root[data-theme="dark"] {
  --color-primary: #66b1ff;
  /* 其他暗色主题变量 */
}
```

---
本规范旨在统一样式与主题化策略，保证一致性与可维护性。