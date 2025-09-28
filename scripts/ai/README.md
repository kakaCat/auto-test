# AI 脚本管理中心

这个目录专门用于存储和管理 AI 助手使用的各类脚本，提高脚本复用效率，避免重复编写相同功能的代码。

## 目录结构

```
scripts/ai/
├── README.md                 # 本文档
├── INDEX.md                  # 脚本索引和快速查找
├── database/                 # 数据库相关脚本
│   ├── query_tables.py      # 查询数据库表结构
│   ├── create_tables.py     # 创建数据库表
│   ├── migrate_data.py      # 数据迁移脚本
│   └── backup_restore.py    # 数据备份恢复
├── file_processing/         # 文件处理脚本
│   ├── batch_rename.py      # 批量重命名文件
│   ├── content_search.py    # 内容搜索和替换
│   ├── format_converter.py  # 格式转换工具
│   └── file_organizer.py    # 文件整理工具
├── deployment/              # 部署相关脚本
│   ├── server_start.py      # 服务启动脚本
│   ├── health_check.py      # 健康检查脚本
│   ├── env_setup.py         # 环境配置脚本
│   └── docker_manager.py    # Docker 管理脚本
├── testing/                 # 测试相关脚本
│   ├── api_test.py          # API 测试脚本
│   ├── load_test.py         # 负载测试脚本
│   ├── integration_test.py  # 集成测试脚本
│   └── test_data_gen.py     # 测试数据生成
├── monitoring/              # 监控相关脚本
│   ├── log_analyzer.py      # 日志分析脚本
│   ├── performance_check.py # 性能检查脚本
│   ├── error_tracker.py     # 错误追踪脚本
│   └── metrics_collector.py # 指标收集脚本
├── analysis/                # 分析相关脚本
│   ├── code_analyzer.py     # 代码分析脚本
│   ├── dependency_check.py  # 依赖检查脚本
│   ├── security_scan.py     # 安全扫描脚本
│   └── report_generator.py  # 报告生成脚本
└── utilities/               # 通用工具脚本
    ├── json_processor.py    # JSON 处理工具
    ├── config_manager.py    # 配置管理工具
    ├── string_utils.py      # 字符串处理工具
    └── date_utils.py        # 日期处理工具
```

## 脚本命名规范

### 文件命名
- 使用小写字母和下划线：`query_database_tables.py`
- 功能描述要清晰：`migrate_old_to_new_schema.py`
- 包含版本信息（如需要）：`backup_v2.py`

### 脚本内部规范
- 每个脚本必须包含文档字符串说明用途
- 包含使用示例和参数说明
- 添加错误处理和日志记录
- 支持命令行参数（如适用）

## 使用指南

### 1. 查找脚本
- 查看 `INDEX.md` 获取脚本列表和功能说明
- 按分类目录浏览相关脚本
- 使用文件名关键词搜索

### 2. 执行脚本
```bash
# 进入项目根目录
cd /Users/mac/Documents/ai/auto-test

# 执行数据库查询脚本
python scripts/ai/database/query_tables.py

# 执行文件处理脚本
python scripts/ai/file_processing/batch_rename.py --pattern "*.txt" --prefix "backup_"
```

### 3. 添加新脚本
1. 选择合适的分类目录
2. 遵循命名规范
3. 添加完整的文档说明
4. 更新 `INDEX.md` 索引文件
5. 测试脚本功能

## 脚本模板

每个新脚本应该包含以下基本结构：

```python
#!/usr/bin/env python3
"""
脚本名称：[脚本功能简述]
创建时间：[YYYY-MM-DD]
用途：[详细说明脚本的用途和使用场景]
参数：[命令行参数说明]
示例：[使用示例]
"""

import sys
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='脚本功能描述')
    parser.add_argument('--param', help='参数说明')
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

## 维护说明

- 定期清理不再使用的脚本
- 更新脚本文档和索引
- 优化常用脚本的性能
- 收集使用反馈，改进脚本功能

## 贡献指南

1. 新增脚本前先检查是否已有类似功能
2. 遵循项目的代码规范和文档标准
3. 添加充分的测试和错误处理
4. 更新相关文档和索引文件