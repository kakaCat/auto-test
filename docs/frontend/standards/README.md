# 前端标准索引（docs/frontend/standards）

本目录包含前端范围内“稳定且可强制执行”的约束与规范，用于保障一致性与可维护性。

- 适用范围：仅限前端（视图、状态、路由、组件、样式、文档等）。
- 关系说明：`guides/` 提供方案与模板，`standards/` 提供强约束；当指南稳定时再提炼为标准。
- 设计关联：这些标准作为“设计约束”，涉及到设计推导或背景可在 `../user-manuals/` 与 `../../design/` 中查阅。

## 索引
- 文档规范 → `./DOCUMENTATION_STANDARDS.md`
- 前端编码规范 → `./FRONTEND_CODING_STANDARDS.md`
- 路由与导航规范 → `./ROUTING_NAVIGATION_STANDARDS.md`
- 状态管理（Pinia）规范 → `./PINIA_STATE_MANAGEMENT_STANDARDS.md`
- 组件文档规范 → `./COMPONENT_DOCUMENTATION_STANDARDS.md`
- 样式与主题规范 → `./STYLE_THEME_STANDARDS.md`
- API 管理标准 → `./API_MANAGEMENT_STANDARDS.md`

## 互链与落地
- 实施时优先遵循标准；如需临时偏离，须在方案中记录理由与回退。
- 实施模板参考 → `../guides/API_MANAGEMENT_TEMPLATE.md`
- 通用协作与跨域规范参考 → `../../standards/README.md`

## 分类速查表（Standard vs Guide）
- 写强约束（MUST/SHOULD），跨页面/模块通用，需审计与评审 → 放 `standards/`。
- 写解决方案/实施步骤/模板/重构计划，迭代快、可试错 → 放 `guides/`。
- 是否迁移为标准的判断：
  - 连续两个版本仍稳定；
  - 能用条款表达并配检查清单；
  - 执行需要门禁（评审/CI 规则/代码风格检查）。
- 迁移方式：在指南中冻结稳定条目 → 提炼为标准；在两侧索引互链并标注“已迁移”。
## 命名与存放约定（提示）

- 标准文件统一使用 `*_STANDARD.md`，归档在 `docs/frontend/standards/` 或 `docs/standards/`（跨域）。
- 指南/模板/实施方案使用 `*_GUIDE.md`，归档在 `docs/frontend/guides/` 或对应域的 `guides/`。
- 指南稳定后可“冻结→提炼为标准”，并在两侧索引互链标注“已迁移”。
- 重命名或迁移后，及时更新相关 README 索引与交叉链接，保持唯一来源。