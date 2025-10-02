# 通用规范与协作指南索引

本目录聚合跨项目的通用标准与协作指南，作为规范入口。

## 目录
- 文档组织规范 → `DOCUMENTATION_STANDARDS.md`
- AI 协作标准 → `AI_ASSISTANT_STANDARD.md`
- 文档映射关系标准 → `DOCUMENT_MAPPING_STANDARD.md`
- 临时文件夹使用标准 → `TEMP_FOLDER_USAGE_STANDARD.md`

## 使用说明
- 所有规范为跨域通用，适用于 `backend/` 与 `frontend/` 文档与代码。
- 变更规范时，请在提交信息中标注影响范围，并在相关域的 README 做必要提示。

## 文档元信息模板（统一状态标识）
为避免“GUIDE 命名但内容为标准”的混淆，所有标准/指南文件顶部推荐加入元信息块：

```
> Status: Standard | Guide
> Scope: project | frontend | backend
> Version: x.y
> Last Updated: YYYY-MM-DD
```

- 若为“项目级治理标准”，即使文件名为 `*_GUIDE.md`，也应设置 `Status: Standard` 并在本索引处列出。
- 若为“实施方案/模板/重构计划”，设置 `Status: Guide`，并归档在对应的 `guides/` 目录。
- 变更时保持索引与互链更新，确保唯一来源和导航清晰。