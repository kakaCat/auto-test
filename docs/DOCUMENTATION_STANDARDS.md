# 文档组织规范

本文档定义了项目文档的组织原则、分类标准和维护规范。

## 核心原则

### 文件夹分类隔离 ⭐ **核心偏好**
- **原则**: 使用文件夹对不同类型的内容进行分类隔离
- **目的**: 便于查找、维护和扩展
- **实施**: 每个文件夹都有明确的职责边界

### 临时文件夹策略 ⭐ **重要规范**
- **使用场景**: 当生成的文件与现有项目约定不一致时
- **命名规范**: `temp-{功能名}-{日期}` (如: `temp-api-refactor-20240115`)
- **工作流程**:
  1. 创建临时文件夹
  2. 在临时文件夹中生成和验证文件
  3. 确认无误后移动到正确位置或重构现有结构
  4. 清理临时文件夹
- **避免混乱**: 不直接在现有目录中生成不符合约定的文件

### 统一结构标准
- 前后端文档采用相同的分类结构
- 保持目录层次的一致性
- 使用统一的命名规范

## 前端用户文档写作方式（07 体例）

前端“用户指南”（`docs/frontend/user-guides/*.md`）统一采用“07方式”。该体例来源于《07 - 工作流设计器》，用于保证可读、可维护与一致性：

- 章节顺序（推荐）
  - 架构定位 → 功能概述 → 界面布局 → 交互与操作 → 页面弹框与抽屉 → 状态与数据流 → 事件与契约 → 数据模型 → 自测清单 → 常见问题

- 关键要点
  - 标题编号规范：`# {编号} - {模块名}`（如 `# 04 - API管理`）
  - 架构定位首节＋6层ASCII图，明确上下游与作用
  - 界面布局采用ASCII结构图，区域职责清晰
  - 弹框/抽屉集中成章，描述字段、校验、禁用/加载与事件契约
  - 归属规则：页面内触发的所有弹框/抽屉归属于该页面文档，不单独成文；跨页复用的通用弹框需在本页完整描述，并在共享组件文档登记且建立互链；若具独立路由，可在组件文档扩展，但本页保留概述与链接
  - 状态与数据流、事件与契约明确字段归一化与错误语义
  - 自测清单覆盖主干流程与边界场景

更多细则见：`/docs/frontend/DOCUMENTATION_STANDARDS.md` 的“07 文档写作方式（设计原则/规范/要求）”章节。

## 标准目录结构

### 一级分类 (前后端通用)
```
docs/
├── README.md                    # 总体文档说明
├── DOCUMENTATION_STANDARDS.md  # 本规范文档
├── backend/                     # 后端文档
└── frontend/                    # 前端文档
```

### 二级分类 (前后端统一)
```
{backend|frontend}/
├── README.md                    # 模块文档总览
├── api/                         # API相关文档
├── architecture/                # 架构设计文档
├── examples/                    # 示例代码
├── guides/                      # 开发指南
├── pages/                       # 页面/模块文档
└── standards/                   # 编码规范
```

### 三级分类示例
```
guides/
├── README.md                    # 指南总览
├── modules/                     # 模块指南 (后端)
├── components/                  # 组件指南 (前端)
├── development.md               # 开发指南
├── project.md                   # 项目指南
└── routing.md                   # 路由指南 (前端)
```

## 三级文档目录职责边界 ⭐ **核心规范**

### 🎯 `/docs/` - 项目级文档中心
**定位**: 项目整体文档导航和跨模块文档

**主要职责**:
- **项目总览**: 系统架构、技术选型、部署指南
- **文档导航**: 统一的文档入口和索引
- **跨模块文档**: AI平台设计、数据库设计、集成方案
- **历史文档**: 保留的历史版本文档

**服务对象**:
- **项目经理**: 了解项目整体情况
- **架构师**: 系统设计和技术决策
- **新团队成员**: 快速了解项目全貌
- **外部合作方**: 项目对接和集成

**核心内容**:
```
docs/
├── README.md                    # 项目文档导航中心
├── AI_PLATFORM_DOCUMENTATION_INDEX.md  # AI平台文档索引
├── DOCUMENTATION_STANDARDS.md  # 文档规范
├── ai-platform/                # AI平台设计文档
├── database_schema_diagram.svg # 数据库设计
└── [历史文档目录]              # 保留的历史文档
```

### 🐍 `/backend/docs/` - 后端开发文档
**定位**: 后端开发者专用技术文档

**主要职责**:
- **API文档**: 接口规范、数据模型、认证授权
- **架构文档**: 后端服务架构、模块设计、数据库设计
- **开发指南**: 环境搭建、编码规范、测试指南
- **技术文档**: Python/FastAPI 相关的技术实现

**服务对象**:
- **后端开发者**: 日常开发和维护
- **API集成者**: 接口对接和调用
- **运维人员**: 部署和监控
- **测试人员**: API测试和验证

**核心内容**:
```
backend/docs/
├── api/           # API接口文档
├── architecture/  # 后端架构设计
├── guides/        # 开发指南
└── changelogs/    # 后端变更记录
```

### 🎨 `/frontend/docs/` - 前端开发文档
**定位**: 前端开发者和用户操作文档

**主要职责**:
- **开发文档**: Vue.js 技术栈、组件开发、构建部署
- **用户指南**: 系统使用教程、功能操作说明
- **AI提示词**: AI助手工作指南和系统分析
- **组件文档**: UI组件库和业务组件

**服务对象**:
- **前端开发者**: 技术开发和维护
- **系统用户**: 功能使用和操作指南
- **AI助手**: 系统理解和用户协助
- **产品经理**: 功能验收和用户体验

**核心内容**:
```
frontend/docs/
├── api/           # 前端API层文档
├── guides/        # 前端开发指南
├── components/    # 组件文档
├── user-guides/   # 用户操作指南 ⭐
├── ai-prompts/    # AI工作指南 ⭐
└── changelogs/    # 前端变更记录
```

### 🔍 关键区别与边界

**服务层次不同**:
- **`/docs/`**: 项目级 → 整体视角
- **`/backend/docs/`**: 模块级 → 技术实现
- **`/frontend/docs/`**: 模块级 + 用户级 → 开发+使用

**内容深度不同**:
- **`/docs/`**: 广度优先，概览性文档
- **`/backend/docs/`**: 深度优先，技术细节
- **`/frontend/docs/`**: 双重深度，技术+用户

**更新频率不同**:
- **`/docs/`**: 低频更新，架构变更时
- **`/backend/docs/`**: 中频更新，功能迭代时
- **`/frontend/docs/`**: 高频更新，UI和功能变更时

**独特价值**:
- **`/docs/`**: 唯一的项目导航中心和AI平台设计
- **`/backend/docs/`**: 唯一的后端技术实现文档
- **`/frontend/docs/`**: 唯一的用户操作指南和AI提示词

### 📊 文档流转关系
```
用户需求 → /frontend/docs/user-guides/ (如何使用)
    ↓
开发需求 → /backend/docs/ + /frontend/docs/guides/ (如何实现)
    ↓
架构决策 → /docs/ (为什么这样设计)
```

## 分类职责定义

### 📁 api/ - API文档
**职责**: API接口相关的所有文档
- `reference.md` - API参考文档
- `guide.md` - API使用指南
- `switcher.md` - API切换器指南 (前端)

### 📁 architecture/ - 架构设计
**职责**: 系统架构和设计文档
- `v2.md`, `v3_ddd.md` - 架构版本文档
- `components.md` - 组件架构 (前端)

### 📁 guides/ - 开发指南
**职责**: 开发流程和使用指南
- `modules/` - 模块指南子目录 (后端)
- `components/` - 组件指南子目录 (前端)
- `development.md` - 开发指南
- `project.md` - 项目指南
- `routing.md` - 路由指南

### 📁 standards/ - 编码规范
**职责**: 编码标准和规范文档
- `coding.md` - 编码规范
- `comments.md` - 注释规范

## 命名规范

### 文件夹命名
- 使用小写字母
- 多个单词用下划线分隔
- 名称要简洁明确

### 文件命名
- **一般文件**: 使用小写字母，多个单词用下划线分隔
- **特殊文件例外**: 
  - `README.md` - 项目约定俗成的大写格式
  - `DOCUMENTATION_STANDARDS.md` - 重要标准文档可使用大写
- 避免使用特殊字符（除下划线和连字符）
- 文件名要能体现内容
- **推荐格式**: `module_name.md`, `api_guide.md`, `quick_start.md`

### README文件
- 每个文件夹都必须有 `README.md`
- README 要包含该目录的说明和导航
- 使用统一的格式和结构

## 内容组织原则

### 层次结构
- 最多3级目录深度
- 避免过深的嵌套
- 保持结构的扁平化

### 内容分离
- 不同类型的内容严格分离
- 避免内容重复
- 相关内容通过链接关联

### 导航设计
- 每个README都要提供清晰的导航
- 使用相对路径链接
- 提供快速访问入口

## 维护规范

### 文档更新
- 代码变更时同步更新文档
- 定期检查文档的准确性
- 及时删除过时的文档

### 版本管理
- 重要文档变更要记录版本
- 保留历史版本的访问方式
- 标注最后更新时间

### 质量控制
- 文档审查纳入代码审查流程
- 保持文档的一致性和准确性
- 定期整理和优化文档结构

## AI 脚本管理规范

### 脚本组织结构
AI助手使用的脚本统一存放在 `scripts/ai/` 目录下，按功能分类组织：

```
scripts/ai/
├── README.md                 # 脚本管理说明
├── INDEX.md                  # 脚本索引和快速查找
├── database/                 # 数据库相关脚本
├── file_processing/         # 文件处理脚本
├── deployment/              # 部署相关脚本
├── testing/                 # 测试相关脚本
├── monitoring/              # 监控相关脚本
├── analysis/                # 分析相关脚本
└── utilities/               # 通用工具脚本
```

### 脚本开发规范

#### 命名规范
- 使用小写字母和下划线：`query_database_tables.py`
- 功能描述要清晰：`migrate_old_to_new_schema.py`
- 包含版本信息（如需要）：`backup_v2.py`

#### 代码规范
- 每个脚本必须包含完整的文档字符串
- 支持命令行参数和帮助信息
- 包含错误处理和日志记录
- 提供使用示例和参数说明

#### 脚本模板
```python
#!/usr/bin/env python3
"""
脚本名称：[功能简述]
创建时间：[YYYY-MM-DD]
用途：[详细说明]
参数：[参数说明]
示例：[使用示例]
"""

import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='脚本功能描述')
    # 添加参数定义
    args = parser.parse_args()
    
    try:
        # 脚本主要逻辑
        logger.info("脚本开始执行")
        # TODO: 实现具体功能
        logger.info("脚本执行完成")
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 脚本分类说明

#### database/ - 数据库脚本
- `query_tables.py` - 查询数据库表结构
- `execute_sql.py` - 执行SQL文件或语句
- `migrate_data.py` - 数据迁移脚本
- `backup_restore.py` - 数据备份恢复

#### file_processing/ - 文件处理脚本
- `search_replace.py` - 文件内容搜索替换
- `batch_rename.py` - 批量重命名文件
- `format_converter.py` - 格式转换工具
- `file_organizer.py` - 文件整理工具

#### deployment/ - 部署脚本
- `server_start.py` - 服务启动脚本
- `health_check.py` - 健康检查脚本
- `env_setup.py` - 环境配置脚本

#### testing/ - 测试脚本
- `api_test.py` - API测试脚本
- `load_test.py` - 负载测试脚本
- `integration_test.py` - 集成测试脚本

#### monitoring/ - 监控脚本
- `log_analyzer.py` - 日志分析脚本
- `performance_check.py` - 性能检查脚本
- `error_tracker.py` - 错误追踪脚本

#### analysis/ - 分析脚本
- `code_analyzer.py` - 代码分析脚本
- `dependency_check.py` - 依赖检查脚本
- `security_scan.py` - 安全扫描脚本

#### utilities/ - 工具脚本
- `json_processor.py` - JSON处理工具
- `config_manager.py` - 配置管理工具
- `string_utils.py` - 字符串处理工具

### 使用指南

#### 脚本查找
1. 查看 `scripts/ai/INDEX.md` 获取完整脚本列表
2. 按分类目录浏览相关脚本
3. 使用文件名关键词搜索

#### 脚本执行
```bash
# 基本执行格式
python scripts/ai/{category}/{script_name}.py [参数]

# 查看帮助信息
python scripts/ai/{category}/{script_name}.py --help

# 预览模式（如支持）
python scripts/ai/{category}/{script_name}.py --dry-run
```

#### 脚本维护
- 新增脚本时更新 `INDEX.md` 索引
- 定期清理不再使用的脚本
- 优化常用脚本的性能和功能
- 收集使用反馈，改进脚本设计

### AI助手使用规范

#### 脚本复用原则
- 优先使用现有脚本，避免重复开发
- 新功能先检查是否可扩展现有脚本
- 通用功能开发为独立脚本供复用

#### 脚本开发流程
1. 确定功能需求和分类
2. 检查现有脚本是否满足需求
3. 选择合适的脚本模板
4. 实现功能并添加文档
5. 更新索引文件
6. 测试脚本功能

#### 质量要求
- 所有脚本必须包含完整文档
- 支持命令行参数和帮助信息
- 包含错误处理和日志记录
- 提供使用示例和测试用例

## 实施指南

### 新建文档
1. 确定文档类型和归属
2. 选择合适的目录位置
3. 遵循命名规范
4. 更新相关的README文件

### 重构现有文档
1. 分析现有文档结构
2. 按照新规范重新分类
3. 更新所有相关链接
4. 验证导航的完整性

### 团队协作
1. 团队成员都要了解本规范
2. 新成员要接受文档规范培训
3. 定期回顾和改进规范

---

**制定时间**: 2024年
**适用范围**: 整个项目的文档组织
**维护责任**: 全体开发团队