# Scripts 目录说明

这个目录包含了项目中的各种脚本文件，按功能分类组织。

## 目录结构

### startup/ - 启动脚本
包含各种服务启动脚本：
- `start_api_v2.py` - API管理模块 v2 启动脚本
- `start_service_api.py` - 服务API启动脚本
- `start_unified_api.py` - 统一API启动脚本

### tests/ - 测试脚本
包含各种测试脚本：
- `test_dao.py` - DAO层测试脚本
- `test_new_apis.py` - 新API测试脚本
- `test_refactored_api.py` - 重构API测试脚本
- `test_simplified_api.py` - 简化API测试脚本

### database/ - 数据库脚本
包含数据库相关的脚本：
- `create_api_interfaces_table.sql` - 创建API接口表的SQL脚本
- `update_api_interfaces_table.sql` - 更新API接口表的SQL脚本
- `insert_api_data.py` - 插入API数据的Python脚本

## 使用说明

### 启动服务
```bash
# 启动API v2服务
python scripts/startup/start_api_v2.py

# 启动服务API
python scripts/startup/start_service_api.py

# 启动统一API
python scripts/startup/start_unified_api.py
```

### 运行测试
```bash
# 运行DAO测试
python scripts/tests/test_dao.py

# 运行API测试
python scripts/tests/test_new_apis.py
```

### 数据库操作
```bash
# 执行SQL脚本
sqlite3 auto_test.db < scripts/database/create_api_interfaces_table.sql

# 插入测试数据
python scripts/database/insert_api_data.py
```

## 注意事项

1. 所有脚本都应该从项目根目录（backend/）运行
2. 确保在运行脚本前已经安装了所需的依赖
3. 数据库脚本需要确保数据库文件存在