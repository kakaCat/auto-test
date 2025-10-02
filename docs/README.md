# AI自动化测试系统 · 文档索引

本页是 `docs/` 顶层索引与治理总览，面向全体协作者（产品/后端/前端/设计/测试/文档维护者）。目标是在 1 分钟内完成“从要做的事到对应规范/设计/实现”的定位。

概述
- 覆盖范围：仅针对 `docs/` 目录的文档、标准与索引，不涉及代码实现细节。
- 内容构成：统一入口、目录总览、常见任务导航、创建/维护规范、版本与归档策略。
- 使用方式：从“快速入口”进入子目录 `README.md`；跨域内容回到此页或访问 `standards/README.md`。
- 命名与链接：统一相对路径与 `README.md` 为索引；废弃文档迁移至域内 `archived/`。
- 适用角色：产品、研发、设计、测试、运维、文档维护者与 AI 助手。
- 变更规则：新增顶层域或重大设计需先提交简短 RFC，经评审通过后更新索引。

## ⏩ 快速入口
- 后端入口 → [backend/README.md](./backend/README.md)
- 前端入口 → [frontend/README.md](./frontend/README.md)
- 设计入口 → [design/ai-platform/README.md](./design/ai-platform/README.md)
- 规范入口 → [standards/README.md](./standards/README.md)

## 🧰 如何使用本索引
- 先看“目录总览”确定归属域（后端、前端、设计、规范）。
- 做具体事情时，直接用“常用任务”里的直达链接与命令。
- 查跨域方案与专题设计，进入 `design/`；查现状实现与接口，进入 `backend/` 或 `frontend/`；查协作与规范，进入 `standards/`。

## 🔎 目录总览（快速定位）
- `backend/` — 后端现状与实现：接口、架构、指南、变更。
  - 入口：
    - [backend/README.md](./backend/README.md)
    - [backend/api/README.md](./backend/api/README.md)
    - [backend/architecture/README.md](./backend/architecture/README.md)
    - [backend/quick_start.md](./backend/quick_start.md)
- `frontend/` — 前端现状与实现：架构、开发指南、用户手册与兼容策略。
  - 入口：
    - [frontend/README.md](./frontend/README.md)
    - [frontend/guides/ARCHITECTURE_GUIDE.md](./frontend/guides/ARCHITECTURE_GUIDE.md)
    - [frontend/guides/DEVELOPMENT_GUIDE.md](./frontend/guides/DEVELOPMENT_GUIDE.md)
- [frontend/user-manuals/README.md](./frontend/user-manuals/README.md)
- `design/` — 新增/修改/删除的方案设计与跨域专题，按项目归档。
  - 项目入口：
    - [design/ai-platform/README.md](./design/ai-platform/README.md)
  - 变更索引：
    - [design/changelogs/CHANGELOG.md](./design/changelogs/CHANGELOG.md)
- `standards/` — 通用规范与协作指南：
  - 入口：
    - [standards/README.md](./standards/README.md)

## 🧭 常用任务（一键直达）
- 启动后端服务 → [backend/quick_start.md](./backend/quick_start.md)
  - 命令：
    - `cd backend && pip install -r requirements.txt && python -m uvicorn src.auto_test.main:app --reload --host 0.0.0.0 --port 8000`
- 启动前端开发环境 → [frontend/guides/DEVELOPMENT_GUIDE.md](./frontend/guides/DEVELOPMENT_GUIDE.md)
  - 命令：
    - `cd frontend && npm install && npm run dev`
- 查看后端 API → [backend/api/README.md](./backend/api/README.md)
- 查数据库设计（现状） → [backend/architecture/DATABASE_DESIGN.md](./backend/architecture/DATABASE_DESIGN.md)
- 查跨项目变更记录 → [design/changelogs/CHANGELOG.md](./design/changelogs/CHANGELOG.md)
- 查看平台设计方案 → [design/ai-platform/README.md](./design/ai-platform/README.md)
- 查看通用规范与协作指南 → [standards/README.md](./standards/README.md)

## 🚀 快速开始
### 前端开发
```bash
cd frontend
npm install
npm run dev
```
📖 详细指南: [frontend/guides/DEVELOPMENT_GUIDE.md](./frontend/guides/DEVELOPMENT_GUIDE.md)

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.auto_test.main:app --reload --host 0.0.0.0 --port 8000
```
📖 详细指南: [backend/quick_start.md](./backend/quick_start.md)

## 🎯 项目级入口（当前目录）
- 数据库设计 → [backend/architecture/DATABASE_DESIGN.md](./backend/architecture/DATABASE_DESIGN.md)
- 变更记录 → [design/changelogs/CHANGELOG.md](./design/changelogs/CHANGELOG.md)
- 文档规范 → [standards/DOCUMENTATION_STANDARDS.md](./standards/DOCUMENTATION_STANDARDS.md)
- 前端页面文档结构规范 → [frontend/standards/DOCUMENTATION_STANDARDS.md](./frontend/standards/DOCUMENTATION_STANDARDS.md)
- AI协作习惯 → [standards/AI_ASSISTANT_STANDARD.md](./standards/AI_ASSISTANT_STANDARD.md)
- 临时文件夹使用 → [standards/TEMP_FOLDER_USAGE_STANDARD.md](./standards/TEMP_FOLDER_USAGE_STANDARD.md)
- 文档映射关系 → [standards/DOCUMENT_MAPPING_STANDARD.md](./standards/DOCUMENT_MAPPING_STANDARD.md)

## 📐 文档操作原则（/docs 下）
- 职责分域：实现类→`backend/`、`frontend/`；方案/设计→`design/`；协作/规范→`standards/`。
- 就近归档：文档靠近其所有者与落地代码，降低维护成本。
- 入口统一：各目录入口文件一律为 `README.md`。
- 链接健康：文件移动/重命名后，立即更新索引与所有引用。
- 原子改动：每次只做一种类型变更，便于回溯与审阅。
- 变更可追踪：在变更摘要中说明来源→去向与理由。
- 主题单一：一个文档只聚焦一个主题，避免混装。
- 粒度管理：`design/` 中如含需求/计划/待办，按需细分 `requirements/`、`planning/`、`todos/`。
- 索引职责：`docs/README.md` 提供“目录总览/快速链接/常用任务/场景导航”。
- 收尾清理：删除空目录、去重冗余段落，保持结构干净。
- 术语一致：统一使用“入口/索引/规范”等术语，路径风格一致。

### 📁 目录与文件创建原则（如何新增/维护）
- 放置规则：
  - 实现与接口说明 → 放到 `docs/backend/` 或 `docs/frontend/` 相应子目录。
  - 方案/专题设计 → 放到 `docs/design/`，按项目建立子目录（如 `design/ai-platform/`）。
  - 通用规范/协作流程 → 放到 `docs/standards/`。
- 目录要求：
  - 新建任何目录必须包含 `README.md`，说明目的、范围、结构与出口链接。
  - 目录层级不超过 3 层；新增顶层域需经评审与简短 RFC。
- 命名规范：
  - 主题文档用 `kebab-case`（例：`frontend-proxy-normalization-design.md`）。
  - 标准/规范类用 `UPPER_SNAKE_CASE`，统一以 `*_STANDARD.md` 结尾（例：`AI_ASSISTANT_STANDARD.md`、`TEMP_FOLDER_USAGE_STANDARD.md`）。
  - 连载/阶段性文档在项目目录中用数字前缀（例：`01_...`, `02_...`）。
  - 文件名避免空格与非 ASCII；中文作为文内标题，不用于文件名。

#### 🏷️ 命名约定补充（标准 vs 指南）
- 标准（强约束、稳定执行）：
  - 位置：`docs/standards/` 或各域 `*/standards/`
  - 命名：`UPPER_SNAKE_CASE + _STANDARD.md`
  - 示例：`AI_ASSISTANT_STANDARD.md`、`DOCUMENT_MAPPING_STANDARD.md`
- 指南/模板（可演进、提供方法）：
  - 位置：域内 `*/guides/`（如 `docs/frontend/guides/`、`docs/backend/guides/`）
  - 命名：`UPPER_SNAKE_CASE + _GUIDE.md` 或 `*_TEMPLATE.md`
  - 示例：`ARCHITECTURE_GUIDE.md`、`DEVELOPMENT_GUIDE.md`、`API_MANAGEMENT_TEMPLATE.md`
- 用户手册（面向终端用户）：
- 位置：`docs/frontend/user-manuals/`
  - 命名：`两位编号 + kebab-case`（例：`02-getting-started.md`、`10-ai-orchestration-and-execution.md`）
- 链接与索引：
  - 所有目录的入口文件为 `README.md`；跨文件引用使用相对路径。
  - 文件重命名或迁移后，需同步更新索引页与所有引用链接。
- 创建流程（四步走）：
  1) 选择归属域并创建（或复用）目录；补上目录 `README.md`。
  2) 按命名规范创建文档，内容聚焦单一主题。
  3) 在 `docs/README.md` 更新入口与导航（如适用）。
  4) 若涉及跨文件引用，统一更新所有链接并自测。
- 禁止事项：
  - 随意新增顶层平行目录；不在无 `README.md` 的目录中堆文档。
  - 一个文件混装多主题；命名风格混乱（大小写/分隔不一致）。
- 提交前自检：
  - 新目录是否有 `README.md` 且写明目的/范围/结构？
  - 新文档是否命名规范、聚焦单主题、包含上下文链接？
  - 主索引是否已更新并正确跳转？
  - 是否清理了空目录、重复链接或过时引用？


## 📞 支持与贡献
- 问题反馈：先查对应文档与示例；若仍有问题，创建 Issue 说明复现步骤。
- 文档贡献：补充示例、最佳实践、常见问题；改进结构、修正错误、增加图表。

— 本索引将持续更新，保障团队在 `docs/` 下的高效协作与维护 —