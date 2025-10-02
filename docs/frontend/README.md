# 前端文档索引（docs/frontend）

本页是前端文档入口与导航，面向前端开发、测试与协作伙伴。目标是在 1 分钟内完成“从任务到对应指南/方案”的定位，并保持与 `docs/` 总纲领一致。

## 🚀 快速入口
- 架构指南 → `./guides/ARCHITECTURE_GUIDE.md`
- 开发指南 → `./guides/DEVELOPMENT_GUIDE.md`
- 用户手册索引 → `./user-manuals/README.md`
- 技术方案与计划 → `./guides/README.md`
- 故障排查 → `./guides/TROUBLESHOOTING_GUIDE.md`
- 标准规范 → `../standards/README.md`（通用）与 `./standards/README.md`（前端专项）
- UI页面文档结构规范 → `./standards/DOCUMENTATION_STANDARDS.md`

## 📁 目录总览
- `user-manuals/`：面向用户的操作说明与功能使用路径
 - `guides/`：前端技术方案、兼容策略与重构计划
- `guides/ARCHITECTURE_GUIDE.md`：前端架构设计与模块说明
- `guides/DEVELOPMENT_GUIDE.md`：前端开发流程、规范与最佳实践
- `TROUBLESHOOTING_GUIDE.md`：常见问题定位与解决
- `standards/`：前端专项标准索引与文档
 - `guides/API_MANAGEMENT_TEMPLATE.md`：API管理示例与模板（非标准）

## ✅ 常见任务
- 新人入门 → `./user-manuals/02-getting-started.md`
- 了解架构 → `./guides/ARCHITECTURE_GUIDE.md`
- API层重构与兼容策略 → `./guides/README.md`
- 文档规范与贡献 → `./standards/README.md` 与 `../standards/README.md`

## 🧑‍⚖️ 维护与规范
- 索引与链接：各子目录以 `README.md` 为索引，统一使用相对路径。
- 归档与清理：过时或不维护文档移至所属域的 `archived/`（如使用），并从索引移除。
- 变更治理：新增顶层域或重大设计需先提交简短 RFC，经评审通过后更新。
- 参考总纲领：见 `../README.md` 的“维护与治理（总纲领）”与“目录与文件创建原则”。
- 前端专项标准索引 → `./standards/README.md`

### 🧩 文档元信息模板（建议粘贴到文档开头）
```
> Status: Draft | Stable | Deprecated
> Version: 1.0
> Last Updated: 2025-10-01
> Owner: @frontend-team
> Tags: frontend, architecture, guides
```