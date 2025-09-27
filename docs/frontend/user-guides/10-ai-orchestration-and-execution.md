---
title: "AI编排与执行指南"
id: "ai-orchestration-and-execution"
lang: "zh-CN"
encoding: "UTF-8"
status: "✅ 已实现"
last_updated: "2025-09-27"
related:
  - "./07-workflow-designer.md"
  - "./04-api-management.md"
---

# AI编排与执行指南

本页采用“07方式”体例，聚焦运行侧：计划生成与校验、入参校验、执行启动、实时监控（WebSocket）、跨系统追踪与统计、审计导出。与《07 - 工作流设计器》形成“设计 → 运行”的闭环。

## 架构定位

位于6层架构的第4层（调用流程 · 运行侧），向上支撑用例场景与需求追溯，向下对接资源管理（API/页面）与基础设施（日志、追踪、权限）。

```
┌─────────────────────────────────────────────────────────────────┐
│ 第6层: 需求管理                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 第5层: 用例场景管理                                             │
├─────────────────────────────────────────────────────────────────┤
│ 第4层: 调用流程（本页：执行/监控/追踪） ← 🎯                    │
├─────────────────────────────────────────────────────────────────┤
│ 第3层: 资源管理（API/页面）                                     │
├─────────────────────────────────────────────────────────────────┤
│ 第2层: 系统管理                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 第1层: 仪表板                                                   │
└─────────────────────────────────────────────────────────────────┘
```

- 依赖下层：使用第3层的API/页面资源与元数据
- 服务上层：为第5/6层提供统一的执行、追踪、审计能力
- 核心作用：收敛执行计划 → 校验参数 → 编排运行 → 推送事件 → 聚合追踪

## 功能概述

- 计划生成与校验：自然语言或既有流程生成可执行计划，结构/依赖校验
- 入参校验：启动前校对必填项与类型，快速失败
- 实时监控：WebSocket推送步骤级事件与进度
- 追踪与统计：系统/模块聚合、跨系统分析、执行轨迹
- 审计导出：按筛选条件导出JSON/CSV等格式审计报告

## 界面布局

运行侧典型布局（可嵌入工作流设计器右侧/下方，或独立页签“执行中心”）：

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ 🛠️ 执行中心（运行 & 监控）                                                   │
├───────────────────────────────────────────────────────────────────────────────┤
│  顶部工具栏: [▶️运行] [🐛调试] [⏹️停止] [🔌订阅执行ID] [📤导出审计] [🧭过滤]      │
├───────────────┬───────────────────────────────────────────┬───────────────────┤
│  📋 计划与入参  │  ⏱️ 事件流与时间线                        │  📊 指标与统计     │
│  ┌───────────┐ │  ┌───────────────────────────────────┐   │  ┌─────────────┐ │
│  │plan摘要   │ │  │exec_123  step_1 started …        │   │  │总计划/系统/模│ │
│  │必填入参   │ │  │step_1 succeeded (120ms)          │   │  │块/失败率等   │ │
│  │校验结果   │ │  │step_2 failed (原因…)             │   │  └─────────────┘ │
│  └───────────┘ │  └───────────────────────────────────┘   │  🔍 追踪明细链接 │
├───────────────┴───────────────────────────────────────────┴───────────────────┤
│  📜 实时日志（可折叠）                                                                     │
└───────────────────────────────────────────────────────────────────────────────┘
```

- 顶部工具栏：执行/调试/停止、订阅当前`execution_id`、导出审计、过滤条件
- 中区：按时间线展示事件（开始/成功/失败/完成），支持跳转到对应步骤
- 右栏：指标卡片（总计划、系统数、模块数、跨系统比率、平均耗时等）

## 交互与操作

### 执行（计划 → 校验 → 运行）
1. 生成计划：`POST /api/orchestration/plan/generate`
2. 校验计划：`POST /api/orchestration/plan/validate`
3. 入参校验：`POST /api/orchestration/execute/validate-inputs`
4. 订阅监控：连接 `GET /api/orchestration/v1/monitor/{execution_id}`
5. 跳转追踪：查看详情与统计（见“追踪与统计”）

### 调试
- 单步或断点模式（UI层实现）：每步暂停、展示上下文、可继续/重跑
- 失败重试：可选对失败步骤重试，保留前置上下文（实现建议）

### 停止
- 主动停止当前执行；展示“已停止于步骤X”的提示与可重跑入口

### 订阅执行ID
- 手动输入或从最近执行列表选择`execution_id`后，建立WebSocket订阅
- 支持切换订阅目标并自动断开旧连接

### 导出审计
- 按当前筛选条件导出JSON/CSV，下载文件或生成链接

## 页面弹框与抽屉

> 归属规则：下述弹框/抽屉均归属于本页，不单独成文；若在其他页复用，请在 `docs/frontend/shared-components.md` 登记并建立互链。

### 执行参数配置弹框（ExecuteParamsDialog）
- 触发：点击`▶️运行`/`🐛调试`
- 字段：
  - `environment`（必填，选择：dev/test/stage/prod）
  - `inputs`（必填，键值对；支持JSON模式）
  - `timeoutSec`（选填，默认30-300）
- 校验：必填项、类型校验、超时范围
- 提交：通过入参校验接口成功后关闭弹框并启动监控
- 事件契约：`onSubmit(params)`、`onCancel()`、`onValidate(result)`

### 订阅执行ID弹框（SubscribeExecutionDialog）
- 字段：`execution_id`（必填，字符串）
- 校验：非空、格式（前端可选实现）
- 提交：连接WebSocket并在右上角显示连接指示灯（🟢/🔴）

### 审计导出抽屉（AuditExportDrawer）
- 字段：`filters`（时间范围/系统/模块/标签）、`format`（`json`/`csv`）
- 提交：`POST /api/orchestration/tracking/export`
- 回调：`onExported({ url | blob })`

## 状态与数据流

- 关键对象：
  - `Plan`：计划数据（id、steps、estimated_duration…）
  - `Inputs`：执行入参（字典），前端以类型化对象管理
  - `Execution`：执行实例（execution_id、status、startedAt…）
  - `Event`：事件流（event_type、step_id、message、timestamp、data）
  - `TrackingRecord`：追踪明细（步骤耗时、系统/模块、状态、错误）
  - `Stats`：聚合指标（总计划数、系统数、模块数、跨系统比率…）
- 来源与触发：
  - 计划/校验/入参 → HTTP调用后入库本地状态
  - 运行事件 → WebSocket流式写入、去重合并、按`step_id`归并
  - 追踪与统计 → HTTP拉取汇总，或基于事件流增量计算
- 状态机：`pending → running → (succeeded | failed | stopped)`
- 缓存与清理：按`execution_id`分片存储，页面卸载时释放；日志面板支持“最多N条”滚动窗口

## 事件与契约

### WebSocket
- 路径：`GET /api/orchestration/v1/monitor/{execution_id}`
- 事件类型（`event_type`）：
  - `execution_started`、`execution_completed`
  - `step_started`、`step_succeeded`、`step_failed`
  - `log`（级别：info/warn/error）、`metric`（耗时/计数）
  - `heartbeat`（保活）
- 事件载荷（示例）：
```json
{
  "execution_id": "exec_123",
  "event_type": "step_succeeded",
  "step_id": "normalize_inputs",
  "timestamp": "2025-09-01T10:20:30.456Z",
  "message": "Inputs normalized",
  "data": { "duration_ms": 120 }
}
```

### HTTP接口（运行侧）
- 计划生成：`POST /api/orchestration/plan/generate`
- 计划校验：`POST /api/orchestration/plan/validate`
- 入参校验：`POST /api/orchestration/execute/validate-inputs`
- 启动执行：`POST /api/orchestration/execute`
- 追踪汇总：`GET /api/orchestration/tracking/summary?execution_id=...`
- 追踪明细：`GET /api/orchestration/tracking/records?execution_id=...`
- 审计导出：`POST /api/orchestration/tracking/export`

> 统一响应：遵循后端约定的`success/data/error`三段式结构；错误返回`code`与`message`，前端按`code`分类处理。

## 数据模型

### Plan（最小子集）
```json
{
  "id": "plan_001",
  "name": "跨系统对账",
  "steps": [
    {
      "id": "fetch_a",
      "type": "api",
      "system": "ERP",
      "module": "Orders",
      "inputsSpec": { "date": "string" },
      "dependsOn": []
    }
  ],
  "estimated_duration_ms": 3500
}
```

### Inputs（示例）
```json
{
  "environment": "test",
  "date": "2025-09-01",
  "retry": 0
}
```

### Event（统一事件）
```json
{
  "execution_id": "exec_123",
  "event_type": "log",
  "step_id": "fetch_a",
  "timestamp": "2025-09-01T10:20:30.456Z",
  "message": "HTTP 200",
  "data": { "status": 200, "duration_ms": 120 }
}
```

### TrackingSummary（示例）
```json
{
  "execution_id": "exec_123",
  "systems": 3,
  "modules": 7,
  "plans": 12,
  "cross_system_ratio": 0.58,
  "avg_duration_ms": 4210,
  "failed_steps": 1
}
```

## 自测清单

- 计划生成后可视化展示且字段与后台契约一致
- 计划、入参校验失败时前端快速失败并给出定位信息
- WebSocket断线自动重连且不重复渲染事件
- 事件时间线跳转可定位到对应步骤卡片/日志
- 停止执行后状态一致（按钮禁用、指示灯变更、计时停止）
- 重试仅作用于失败步骤，保持前置上下文读写一致
- 审计导出遵守筛选条件，文件名包含时间戳与`execution_id`
- 深色模式与缩放下布局不抖动
- 国际化：文案可提取与切换（如有i18n支持）
- 错误码分类渲染（校验类/网络类/权限类）

## 常见问题（FAQ）

- WebSocket连接失败？检查`execution_id`是否有效、网络代理与权限；允许退化到轮询
- 计划校验与入参校验何区别？前者校验步骤结构与依赖，后者校验运行时入参完整性与类型
- 如何重试失败步骤？提供“仅重试失败步骤”入口，保持依赖步骤只读
- 跨系统统计口径？以事件归档数据为准，维度：系统/模块/步骤/执行
- 与《工作流设计器》的关系？设计产出计划，本页负责计划运行与可观测性
- 权限与脱敏？敏感字段经Wrapper处理后再落UI，导出前执行再脱敏

## 相关文档与互链

- 《07 - 工作流设计器》：`./07-workflow-designer.md`
- 《04 - API管理》：`./04-api-management.md`
- 用户指南索引：`./README.md`

> 备注：本页仅覆盖“运行侧”。关于计划建模、节点说明与设计规范，请参见《07 - 工作流设计器》。