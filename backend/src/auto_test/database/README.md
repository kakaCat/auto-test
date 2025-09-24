# 服务管理系统数据库文档

## 概述

本目录包含服务管理系统的MySQL数据库表结构和示例数据，与前端Vue组件完全对应。

## 文件说明

### 核心文件

- **`service_management_schema.sql`** - 数据库表结构定义
- **`service_management_data.sql`** - 示例数据插入脚本
- **`init_service_management.sql`** - 一键初始化脚本

### 数据库表结构

#### 1. 主要表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `management_systems` | 管理系统表 | id, name, description, category, enabled, order_index |
| `service_modules` | 服务模块表 | id, system_id, name, path, method, version, tags, enabled |

#### 2. 辅助表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `system_categories` | 系统分类表 | code, name, description, icon, color |
| `module_tags` | 模块标签表 | id, name, color, usage_count |
| `module_tag_relations` | 模块标签关联表 | module_id, tag_id |
| `system_operation_logs` | 操作日志表 | operation_type, operation_desc, operator_id |

## 快速开始

### 1. 数据库初始化

```bash
# 方法1: 使用一键初始化脚本
mysql -u username -p database_name < init_service_management.sql

# 方法2: 分步执行
mysql -u username -p database_name < service_management_schema.sql
mysql -u username -p database_name < service_management_data.sql
```

### 2. 验证安装

```sql
-- 检查表是否创建成功
SHOW TABLES LIKE '%management%' OR LIKE '%service%' OR LIKE '%module%';

-- 检查数据是否插入成功
SELECT COUNT(*) as system_count FROM management_systems;
SELECT COUNT(*) as module_count FROM service_modules;
```

## 数据结构详解

### 管理系统表 (management_systems)

```sql
CREATE TABLE `management_systems` (
  `id` varchar(50) NOT NULL COMMENT '系统唯一标识',
  `name` varchar(100) NOT NULL COMMENT '系统名称',
  `description` text COMMENT '系统描述',
  `category` varchar(50) NOT NULL DEFAULT 'custom' COMMENT '系统分类',
  `enabled` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `order_index` int(11) NOT NULL DEFAULT 0 COMMENT '排序权重',
  `metadata` json DEFAULT NULL COMMENT '系统元数据',
  -- 时间戳和审计字段
  PRIMARY KEY (`id`)
);
```

**字段说明:**
- `id`: 系统唯一标识，对应前端的 system.id
- `category`: 系统分类，对应前端的 SystemCategory 枚举
- `metadata`: JSON格式的元数据，存储版本、维护者等信息
- `order_index`: 排序权重，控制前端显示顺序

### 服务模块表 (service_modules)

```sql
CREATE TABLE `service_modules` (
  `id` varchar(50) NOT NULL COMMENT '模块唯一标识',
  `system_id` varchar(50) NOT NULL COMMENT '所属系统ID',
  `name` varchar(100) NOT NULL COMMENT '模块名称',
  `path` varchar(255) NOT NULL COMMENT '路由路径',
  `method` varchar(10) DEFAULT 'GET' COMMENT 'HTTP方法',
  `version` varchar(20) NOT NULL DEFAULT '1.0.0' COMMENT '版本号',
  `tags` json DEFAULT NULL COMMENT '标签列表',
  `config` json DEFAULT NULL COMMENT '模块配置',
  -- 外键约束
  CONSTRAINT `fk_service_modules_system` FOREIGN KEY (`system_id`) 
    REFERENCES `management_systems` (`id`) ON DELETE CASCADE
);
```

**字段说明:**
- `system_id`: 外键，关联到 management_systems.id
- `tags`: JSON数组，存储模块标签
- `config`: JSON对象，存储模块特定配置
- `method`: HTTP方法，支持 GET、POST、PUT、DELETE、ALL

## 示例数据

### 系统分类

| 代码 | 名称 | 描述 |
|------|------|------|
| user-management | 用户管理 | 用户注册、登录、权限管理等功能 |
| content-management | 内容管理 | 内容创建、编辑、发布等功能 |
| api-management | API管理 | API接口管理和文档维护 |
| monitoring | 监控管理 | 系统监控和性能管理 |

### 管理系统示例

1. **用户管理系统** (id: 1)
   - 用户注册模块 (1-1): `/user/register`
   - 用户登录模块 (1-2): `/user/login`
   - 权限管理模块 (1-3): `/user/permissions`

2. **订单管理系统** (id: 2)
   - 订单创建模块 (2-1): `/order/create`
   - 支付处理模块 (2-2): `/order/payment`
   - 订单查询模块 (2-3): `/order/query`

## API集成建议

### Python/FastAPI 示例

```python
from sqlalchemy import create_engine, Column, String, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class ManagementSystem(Base):
    __tablename__ = 'management_systems'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    category = Column(String(50), nullable=False, default='custom')
    enabled = Column(Boolean, nullable=False, default=True)
    order_index = Column(Integer, nullable=False, default=0)
    metadata = Column(JSON)
    
    # 关联关系
    modules = relationship("ServiceModule", back_populates="system")

class ServiceModule(Base):
    __tablename__ = 'service_modules'
    
    id = Column(String(50), primary_key=True)
    system_id = Column(String(50), ForeignKey('management_systems.id'))
    name = Column(String(100), nullable=False)
    path = Column(String(255), nullable=False)
    method = Column(String(10), default='GET')
    version = Column(String(20), nullable=False, default='1.0.0')
    enabled = Column(Boolean, nullable=False, default=True)
    tags = Column(JSON)
    config = Column(JSON)
    
    # 关联关系
    system = relationship("ManagementSystem", back_populates="modules")
```

## 维护和扩展

### 添加新的系统分类

```sql
INSERT INTO system_categories (code, name, description, icon, color) 
VALUES ('new-category', '新分类', '新分类描述', 'el-icon-new', '#FF6B6B');
```

### 添加新的管理系统

```sql
INSERT INTO management_systems (id, name, description, category, enabled, order_index)
VALUES ('new-sys', '新系统', '新系统描述', 'new-category', 1, 10);
```

### 性能优化建议

1. **索引优化**: 已为常用查询字段添加索引
2. **分页查询**: 建议使用 LIMIT 和 OFFSET 进行分页
3. **JSON字段查询**: 使用 JSON_EXTRACT 函数查询 JSON 字段
4. **缓存策略**: 对于不经常变化的分类数据，建议使用缓存

## 注意事项

1. **字符集**: 使用 utf8mb4 支持完整的 Unicode 字符
2. **外键约束**: 启用了外键约束，删除系统时会级联删除相关模块
3. **JSON字段**: tags 和 config 字段使用 JSON 格式，需要 MySQL 5.7+ 支持
4. **时间戳**: 所有表都包含 created_at 和 updated_at 字段用于审计

## 故障排除

### 常见问题

1. **外键约束错误**: 确保在插入模块前先插入对应的系统
2. **JSON格式错误**: 确保 tags 和 config 字段使用正确的 JSON 格式
3. **字符集问题**: 确保数据库和表都使用 utf8mb4 字符集

### 数据备份

```bash
# 备份结构和数据
mysqldump -u username -p database_name management_systems service_modules > backup.sql

# 仅备份结构
mysqldump -u username -p --no-data database_name management_systems service_modules > schema_backup.sql
```