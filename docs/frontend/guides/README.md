# 前端技术指南（docs/frontend/guides）

本目录用于存放前端的技术方案、兼容策略、重构计划与模板示例。内容旨在指导具体实施与演进，不具有“强约束”的标准效力。

- 角色定位：解决问题与落地实现的“方法库”，相较于 `./standards/` 更灵活、更可演进。
- 更新频率：随需求与实现变更而迭代，允许临时性与实验性内容。
- 标准关系：当指南内容稳定到可强制执行时，再提炼/迁移到 `./standards/`。

## 索引
- API 管理模板 → `./API_MANAGEMENT_TEMPLATE.md`
- 开发指南 → `./DEVELOPMENT_GUIDE.md`
- 架构指南 → `./ARCHITECTURE_GUIDE.md`
- 故障排查 → `./TROUBLESHOOTING_GUIDE.md`
- UI 设计系统与规范 → `./UI_DESIGN_SYSTEM.md`

## 使用建议
- 在模板或方案内记录前提条件、边界与适用范围，避免误用。
- 链接到相关标准文件（如 API 管理标准）以保持上下游一致性。
- 当指南升级为标准时，在本页与原文件处留下迁移指引。