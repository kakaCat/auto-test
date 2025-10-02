# 临时文件夹使用指南
> Status: Standard
> Scope: project
> Version: 1.0
> Last Updated: 2025-10-01

## 📋 概述

本文档详细说明了在AI助手生成文件时如何使用临时文件夹策略，避免与现有项目约定冲突，保持代码库的整洁性。

## 🎯 使用场景

### 1. **大量新文件生成**
当需要生成多个相关文件时，先在临时文件夹中组织，避免污染现有目录结构。

**示例场景**:
- API重构时生成多个新的API模块文件
- 组件库重构时生成多个组件文件
- 新功能开发时生成相关的文档和代码文件

### 2. **文件结构与约定不一致**
当生成的文件结构与现有项目约定不符时，使用临时文件夹进行缓冲。

**示例场景**:
- 生成的API文件不符合现有的分层架构
- 组件文件的组织方式与现有规范不一致
- 文档结构与既定的文档标准不符

### 3. **实验性功能开发**
在开发实验性功能时，使用临时文件夹避免影响主代码库。

**示例场景**:
- 新的架构模式验证
- 第三方库集成测试
- 性能优化方案验证

### 4. **重构现有文件组织**
在重构现有文件组织时，使用临时文件夹作为过渡。

**示例场景**:
- API层重构
- 组件架构重构
- 文档结构重组

## 🛠️ 使用规范

### 命名规范
```
temp-{功能名}-{日期}

示例:
- temp-api-refactor-20240115
- temp-components-20240115
- temp-docs-cleanup-20240115
- temp-architecture-20240115
```

### 目录结构
```
temp-{功能名}-{日期}/
├── README.md                    # 临时文件夹说明
├── MIGRATION_PLAN.md           # 迁移计划
├── {生成的文件和目录}
└── CLEANUP_CHECKLIST.md       # 清理检查清单
```

### 必需文件
每个临时文件夹必须包含以下文件：

#### 1. README.md
```markdown
# Temp-{功能名} 临时文件夹

## 目的
说明创建这个临时文件夹的原因和目标

## 内容
列出包含的文件和目录

## 迁移计划
说明如何将文件迁移到正确位置

## 清理计划
说明完成后如何清理临时文件夹
```

#### 2. MIGRATION_PLAN.md
```markdown
# 迁移计划

## 文件迁移映射
- temp-folder/file1.ts → src/api/modules/file1.ts
- temp-folder/file2.ts → src/api/core/file2.ts

## 迁移步骤
1. 验证文件内容正确性
2. 检查目标位置是否存在冲突
3. 执行文件移动
4. 更新相关引用和导入
5. 测试功能正常性

## 风险评估
列出可能的风险和应对措施
```

#### 3. CLEANUP_CHECKLIST.md
```markdown
# 清理检查清单

## 迁移完成检查
- [ ] 所有文件已移动到正确位置
- [ ] 相关引用已更新
- [ ] 功能测试通过
- [ ] 文档链接已更新

## 清理操作
- [ ] 删除临时文件夹
- [ ] 更新相关文档
- [ ] 提交代码变更
```

## 📝 使用流程

### 步骤1: 创建临时文件夹
```bash
# 创建临时文件夹
mkdir temp-api-refactor-20240115
cd temp-api-refactor-20240115

# 创建必需文件
touch README.md MIGRATION_PLAN.md CLEANUP_CHECKLIST.md
```

### 步骤2: 生成和验证文件
```bash
# 在临时文件夹中生成文件
# 验证文件内容和结构
# 测试文件的正确性
```

### 步骤3: 制定迁移计划
```markdown
# 在MIGRATION_PLAN.md中详细规划
- 分析目标位置
- 检查潜在冲突
- 制定迁移步骤
- 评估风险
```

### 步骤4: 执行迁移
```bash
# 按照迁移计划执行文件移动
# 更新相关引用和导入
# 测试功能正常性
```

### 步骤5: 清理临时文件夹
```bash
# 确认迁移完成
# 删除临时文件夹
rm -rf temp-api-refactor-20240115
```

## 🚨 注意事项

### 1. **安全考虑**
- 临时文件夹不应包含敏感信息
- 及时清理临时文件夹，避免信息泄露
- 不要在临时文件夹中存储重要的唯一文件

### 2. **版本控制**
- 临时文件夹通常不应提交到版本控制
- 在.gitignore中添加临时文件夹模式: `temp-*`
- 如需版本控制，使用专门的分支

### 3. **团队协作**
- 临时文件夹的创建和使用应通知团队
- 避免多人同时使用相同名称的临时文件夹
- 及时清理，避免影响其他团队成员

### 4. **文档同步**
- 临时文件夹的使用应记录在相关文档中
- 迁移完成后更新相关的文档链接
- 保持文档与实际文件结构的一致性

## 📊 最佳实践

### 1. **命名最佳实践**
```
✅ 好的命名:
- temp-api-refactor-20240115
- temp-components-restructure-20240115
- temp-docs-cleanup-20240115

❌ 避免的命名:
- temp
- temp-files
- new-files
- test
```

### 2. **结构最佳实践**
```
✅ 好的结构:
temp-api-refactor-20240115/
├── README.md
├── MIGRATION_PLAN.md
├── CLEANUP_CHECKLIST.md
├── core/
│   ├── http-client.ts
│   └── types.ts
└── modules/
    ├── system-api.ts
    └── module-api.ts

❌ 避免的结构:
temp-api-refactor-20240115/
├── file1.ts
├── file2.ts
├── file3.ts
└── file4.ts
```

### 3. **迁移最佳实践**
- **分批迁移**: 大量文件分批次迁移，降低风险
- **测试验证**: 每次迁移后进行功能测试
- **回滚准备**: 保留迁移前的备份，便于回滚
- **文档同步**: 迁移过程中同步更新相关文档

## 🔍 示例场景

### 场景1: API重构
```bash
# 1. 创建临时文件夹
mkdir temp-api-refactor-20240115

# 2. 生成新的API文件结构
temp-api-refactor-20240115/
├── README.md
├── MIGRATION_PLAN.md
├── core/
│   ├── http-client.ts
│   ├── types.ts
│   └── constants.ts
├── modules/
│   ├── system-api.ts
│   ├── module-api.ts
│   └── page-api.ts
└── converters/
    ├── SystemConverter.ts
    └── ModuleConverter.ts

# 3. 验证和测试
# 4. 按计划迁移到 src/api/
# 5. 清理临时文件夹
```

### 场景2: 组件重构
```bash
# 1. 创建临时文件夹
mkdir temp-components-20240115

# 2. 生成新的组件结构
temp-components-20240115/
├── README.md
├── MIGRATION_PLAN.md
├── common/
│   ├── BaseButton.vue
│   └── BaseInput.vue
├── business/
│   ├── SystemTree.vue
│   └── ApiCard.vue
└── layout/
    ├── PageHeader.vue
    └── PageFooter.vue

# 3. 验证和测试
# 4. 按计划迁移到 src/components/
# 5. 清理临时文件夹
```

## 📝 总结

临时文件夹策略是保持代码库整洁性和约定一致性的重要工具。通过合理使用临时文件夹，我们可以：

1. **避免混乱**: 防止不符合约定的文件污染现有目录
2. **降低风险**: 在安全的环境中验证新文件的正确性
3. **渐进式重构**: 实现平滑的文件组织和架构重构
4. **提升质量**: 确保最终的文件组织符合项目标准

---

**文档版本**: v1.0  
**创建时间**: 2024年1月  
**维护者**: 开发团队