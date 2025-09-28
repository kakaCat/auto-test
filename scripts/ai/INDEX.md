# AI 脚本索引

这个文件提供了所有AI脚本的快速索引和使用指南。

## 数据库脚本 (database/)

### query_tables.py
**功能**: 查询SQLite数据库中的所有表信息
**用途**: 快速了解数据库结构，支持表名过滤和详细信息显示
**常用命令**:
```bash
# 查询所有表
python scripts/ai/database/query_tables.py

# 查询特定模式的表
python scripts/ai/database/query_tables.py --filter "api_*"

# 显示表结构详情
python scripts/ai/database/query_tables.py --details

# 表格格式输出
python scripts/ai/database/query_tables.py --format table
```

### execute_sql.py
**功能**: 执行SQL文件或SQL语句
**用途**: 数据库操作、数据查询、表创建等
**常用命令**:
```bash
# 执行SQL文件
python scripts/ai/database/execute_sql.py --sql-file backend/scripts/database/create_tables.sql

# 执行单条SQL
python scripts/ai/database/execute_sql.py --sql "SELECT COUNT(*) FROM systems"

# 表格格式输出查询结果
python scripts/ai/database/execute_sql.py --sql "SELECT * FROM api_interfaces LIMIT 5" --output table

# 不使用事务执行
python scripts/ai/database/execute_sql.py --sql-file script.sql --no-transaction
```

## 文件处理脚本 (file_processing/)

### search_replace.py
**功能**: 文件内容搜索和替换
**用途**: 批量修改代码、重构变量名、更新配置等
**常用命令**:
```bash
# 搜索特定内容
python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_function" --file-pattern "*.py"

# 替换内容（预览模式）
python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_function" --replacement "new_function" --file-pattern "*.py" --dry-run

# 实际替换并创建备份
python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_function" --replacement "new_function" --file-pattern "*.py" --backup

# 正则表达式替换
python scripts/ai/file_processing/search_replace.py --directory frontend/src --pattern "console\.log\(.*\)" --replacement "logger.info" --file-pattern "*.js"
```

## 部署脚本 (deployment/)

### server_health_check.py
**功能**: 服务健康检查
**用途**: 检查后端和前端服务状态
**常用命令**:
```bash
# 检查所有服务
python scripts/ai/deployment/server_health_check.py

# 检查特定服务
python scripts/ai/deployment/server_health_check.py --service backend
```

## 测试脚本 (testing/)

### api_test.py
**功能**: API接口测试
**用途**: 自动化API测试、接口验证
**常用命令**:
```bash
# 测试所有API
python scripts/ai/testing/api_test.py

# 测试特定模块API
python scripts/ai/testing/api_test.py --module systems
```

## 监控脚本 (monitoring/)

### log_analyzer.py
**功能**: 日志分析工具
**用途**: 分析应用日志、错误统计、性能监控
**常用命令**:
```bash
# 分析最近的日志
python scripts/ai/monitoring/log_analyzer.py --log-dir logs --hours 24

# 错误统计
python scripts/ai/monitoring/log_analyzer.py --log-dir logs --error-only
```

## 分析脚本 (analysis/)

### code_analyzer.py
**功能**: 代码分析工具
**用途**: 代码质量检查、依赖分析、复杂度统计
**常用命令**:
```bash
# 分析代码质量
python scripts/ai/analysis/code_analyzer.py --directory src

# 依赖分析
python scripts/ai/analysis/code_analyzer.py --directory src --check-dependencies
```

## 工具脚本 (utilities/)

### json_processor.py
**功能**: JSON数据处理工具
**用途**: JSON格式化、验证、转换
**常用命令**:
```bash
# 格式化JSON文件
python scripts/ai/utilities/json_processor.py --file config.json --format

# 验证JSON格式
python scripts/ai/utilities/json_processor.py --file config.json --validate
```

## 快速使用指南

### 1. 常见任务快速命令

**查看数据库表结构**:
```bash
python scripts/ai/database/query_tables.py --details --format table
```

**批量重命名函数**:
```bash
python scripts/ai/file_processing/search_replace.py --directory src --pattern "oldFunctionName" --replacement "newFunctionName" --file-pattern "*.py" --backup
```

**检查服务状态**:
```bash
python scripts/ai/deployment/server_health_check.py
```

### 2. 脚本组合使用

**数据库迁移流程**:
```bash
# 1. 备份当前数据
python scripts/ai/database/execute_sql.py --sql "SELECT * FROM important_table" --output csv > backup.csv

# 2. 执行迁移脚本
python scripts/ai/database/execute_sql.py --sql-file migration.sql

# 3. 验证结果
python scripts/ai/database/query_tables.py --details
```

**代码重构流程**:
```bash
# 1. 搜索需要修改的代码
python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_pattern" --file-pattern "*.py"

# 2. 预览替换效果
python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_pattern" --replacement "new_pattern" --file-pattern "*.py" --dry-run

# 3. 执行替换
python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_pattern" --replacement "new_pattern" --file-pattern "*.py" --backup
```

### 3. 脚本开发规范

- 所有脚本都支持 `--help` 参数查看详细用法
- 使用 `--dry-run` 参数预览操作结果
- 重要操作使用 `--backup` 参数创建备份
- 使用 `--verbose` 参数获取详细日志输出

### 4. 故障排除

**脚本执行失败**:
1. 检查Python环境和依赖
2. 确认文件路径和权限
3. 查看详细错误日志
4. 使用预览模式测试

**数据库连接问题**:
1. 确认数据库文件存在
2. 检查文件权限
3. 验证数据库路径配置

**文件处理问题**:
1. 确认目录和文件存在
2. 检查文件编码格式
3. 验证正则表达式语法