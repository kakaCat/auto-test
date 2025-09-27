# AI驱动自动化测试平台 - 文档索引

## 文档结构说明

本平台采用"1个主PRD + N个专项详细设计文档"的结构，确保既有整体视野又有实施细节。

**文档组织结构**：
```
docs/
├── ai-platform/                    # AI平台相关文档
│   ├── 01_AI_DRIVEN_TESTING_PLATFORM_PRD.md
│   ├── 02_SYSTEM_REFACTORING_DESIGN.md
│   ├── 03_PHASE1_API_ORCHESTRATION_DESIGN.md
│   ├── 04_PHASE1_IMPLEMENTATION_GUIDE.md
│   ├── 05_PHASE2_UI_AUTOMATION_DESIGN.md
│   └── 06_PHASE3_REQUIREMENT_MANAGEMENT_DESIGN.md
├── backend/                         # 后端相关文档
├── frontend/                        # 前端相关文档
└── AI_PLATFORM_DOCUMENTATION_INDEX.md  # 本索引文件
```

## 核心文档清单

### 🎯 主要文档

| 文档名称 | 文件路径 | 描述 | 状态 |
|---------|---------|------|------|
| **主PRD** | [AI_DRIVEN_TESTING_PLATFORM_PRD.md](./ai-platform/01_AI_DRIVEN_TESTING_PLATFORM_PRD.md) | 平台整体架构、愿景和三阶段演进路径 | ✅ 已完成 |

### 📋 专项设计文档

| 阶段 | 文档名称 | 文件路径 | 描述 | 状态 |
|------|---------|---------|------|------|
| **系统重构** | 系统重构设计 | [SYSTEM_REFACTORING_DESIGN.md](./ai-platform/02_SYSTEM_REFACTORING_DESIGN.md) | 现有系统向AI驱动平台的重构方案 | ✅ 已完成 |
| **第一阶段** | API编排模块设计 | [PHASE1_API_ORCHESTRATION_DESIGN.md](./ai-platform/03_PHASE1_API_ORCHESTRATION_DESIGN.md) | 基于现有系统的API编排详细设计 | ✅ 已更新 |
| **第一阶段** | 实施指南 | [PHASE1_IMPLEMENTATION_GUIDE.md](./ai-platform/04_PHASE1_IMPLEMENTATION_GUIDE.md) | 第一阶段的详细开发指南和代码示例 | ✅ 已更新 |
| **第二阶段** | UI自动化测试设计 | [PHASE2_UI_AUTOMATION_DESIGN.md](./ai-platform/05_PHASE2_UI_AUTOMATION_DESIGN.md) | 多端UI测试的AI驱动设计和自适应机制 | ✅ 已更新 |
| **第三阶段** | 需求管理模块设计 | [PHASE3_REQUIREMENT_MANAGEMENT_DESIGN.md](./ai-platform/06_PHASE3_REQUIREMENT_MANAGEMENT_DESIGN.md) | 需求到测试闭环的完整设计 | ✅ 已更新 |

### 📚 现有文档

| 类别 | 文档名称 | 文件路径 | 描述 |
|------|---------|---------|------|
| 错误分析 | 详细错误分析记录 | [log_error_analysis_detailed.md](./log_error_analysis_detailed.md) | 项目开发过程中的错误复盘和预防措施 |
| 架构设计 | 系统架构与逻辑 | [system_architecture_and_logic.md](./system_architecture_and_logic.md) | 现有系统的架构设计 |
| 页面设计 | 页面配置实现总结 | [page_configuration_implementation_summary.md](./page_configuration_implementation_summary.md) | 页面配置功能的实现总结 |

## 阅读指南

### 🚀 快速开始
1. **了解整体愿景**：先阅读 [主PRD](./ai-platform/01_AI_DRIVEN_TESTING_PLATFORM_PRD.md)
2. **理解技术架构**：重点关注ASCII架构图和MCP工具层设计
3. **掌握演进路径**：理解三个阶段的依赖关系和技术共性

### 🔧 开发人员
1. **第一阶段开发**：详细阅读 [API编排模块设计](./ai-platform/03_PHASE1_API_ORCHESTRATION_DESIGN.md)
2. **第二阶段开发**：详细阅读 [UI自动化测试设计](./ai-platform/05_PHASE2_UI_AUTOMATION_DESIGN.md)  
3. **第三阶段开发**：详细阅读 [需求管理模块设计](./ai-platform/06_PHASE3_REQUIREMENT_MANAGEMENT_DESIGN.md)

### 📊 产品经理
1. **业务价值理解**：主PRD中的成功指标和业务指标
2. **用户体验设计**：第三阶段文档中的界面设计部分
3. **验收标准**：各专项文档中的验收标准部分

### 🧪 测试工程师
1. **测试策略**：各阶段文档中的测试设计部分
2. **验收标准**：功能验收、性能验收、稳定性验收
3. **错误预防**：[错误分析文档](./log_error_analysis_detailed.md)中的预防措施

## 核心概念速查

### 🧠 AI Agent
- **定位**：平台的"大脑"，负责理解、规划和决策
- **能力**：需求理解、策略规划、执行协调
- **技术**：基于LLM的自然语言处理和推理

### 🔧 MCP工具层
- **定位**：平台的"手脚"，负责执行具体动作
- **原则**：万物皆可MCP工具
- **标准**：统一的schema定义，便于AI理解和调用

### 🔄 三阶段演进
```
阶段1: API编排 (技术原型)
    ↓ 提供基础能力
阶段2: 页面自动化测试 (核心价值)  
    ↓ 提供执行能力
阶段3: 需求管理 (最终集成)
```

## 技术栈概览

### 后端技术栈
- **框架**：Python FastAPI
- **AI引擎**：支持GPT-4、Claude等主流LLM
- **MCP协议**：标准MCP客户端实现
- **数据库**：PostgreSQL/MySQL

### 前端技术栈
- **框架**：Vue 3 + Element Plus
- **构建工具**：Vite
- **状态管理**：Pinia
- **UI组件**：Element Plus

### 测试工具栈
- **Web测试**：Playwright
- **移动端测试**：Appium
- **API测试**：基于现有API管理模块
- **性能测试**：集成性能监控工具

## 更新日志

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2024-01-15 | 创建完整的PRD和三个专项设计文档 | AI Assistant |
| 2024-01-15 | 创建文档索引和阅读指南 | AI Assistant |
| 2025-09-27 | 同步03文档变更至04/05/06，统一事件协议与审计字段 | AI Assistant |

## 反馈与贡献

### 📝 文档反馈
- 如发现文档内容不清晰或有遗漏，请及时反馈
- 实现过程中的调整请及时更新相应文档

### 🔄 版本管理
- 重大变更请更新文档版本号
- 保持文档与实际实现的一致性

### 📞 联系方式
- 技术问题：请在项目issue中提出
- 文档问题：请直接修改并提交PR

---

*本索引文档将随着项目进展持续更新，请定期查看最新版本。*