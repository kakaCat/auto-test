-- ========================================
-- 服务管理系统SQLite数据库表结构 (优化版)
-- 创建时间: 2024-01-20
-- 描述: 使用自增ID作为主键，UUID作为业务标识符，优化聚簇索引性能
-- ========================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- ========================================
-- 1. 管理系统表 (management_systems) - 优化版
-- ========================================
DROP TABLE IF EXISTS management_systems;
CREATE TABLE management_systems (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键，聚簇索引
  uuid TEXT NOT NULL UNIQUE,             -- UUID业务标识符，对外接口使用
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT DEFAULT 'el-icon-menu',
  category TEXT NOT NULL DEFAULT 'custom',
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  order_index INTEGER NOT NULL DEFAULT 0,
  url TEXT,
  metadata TEXT, -- JSON格式的字符串
  deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1)),
  deleted_at DATETIME DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  updated_by TEXT
);

-- 创建索引
CREATE UNIQUE INDEX idx_systems_uuid ON management_systems(uuid);
CREATE INDEX idx_systems_category ON management_systems(category);
CREATE INDEX idx_systems_enabled ON management_systems(enabled);
CREATE INDEX idx_systems_deleted ON management_systems(deleted);
CREATE INDEX idx_systems_order ON management_systems(order_index);
CREATE INDEX idx_systems_created_at ON management_systems(created_at);
CREATE INDEX idx_systems_deleted_at ON management_systems(deleted_at);

-- ========================================
-- 2. 服务模块表 (service_modules) - 优化版
-- ========================================
DROP TABLE IF EXISTS service_modules;
CREATE TABLE service_modules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键，聚簇索引
  uuid TEXT NOT NULL UNIQUE,             -- UUID业务标识符，对外接口使用
  system_id INTEGER NOT NULL,            -- 关联系统的自增ID
  system_uuid TEXT NOT NULL,             -- 关联系统的UUID（冗余字段，便于查询）
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT DEFAULT 'el-icon-service',
  path TEXT NOT NULL,
  method TEXT DEFAULT 'GET',
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  version TEXT NOT NULL DEFAULT '1.0.0',
  module_type TEXT DEFAULT '通用模块',
  tags TEXT, -- JSON数组格式的字符串
  config TEXT, -- JSON格式的字符串
  order_index INTEGER NOT NULL DEFAULT 0,
  deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1)),
  deleted_at DATETIME DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  updated_by TEXT,
  FOREIGN KEY (system_id) REFERENCES management_systems(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建索引
CREATE UNIQUE INDEX idx_modules_uuid ON service_modules(uuid);
CREATE INDEX idx_modules_system_id ON service_modules(system_id);
CREATE INDEX idx_modules_system_uuid ON service_modules(system_uuid);
CREATE INDEX idx_modules_enabled ON service_modules(enabled);
CREATE INDEX idx_modules_deleted ON service_modules(deleted);
CREATE INDEX idx_modules_path ON service_modules(path);
CREATE INDEX idx_modules_version ON service_modules(version);
CREATE INDEX idx_modules_created_at ON service_modules(created_at);
CREATE INDEX idx_modules_deleted_at ON service_modules(deleted_at);

-- ========================================
-- 3. 系统分类枚举表 (system_categories)
-- ========================================
DROP TABLE IF EXISTS system_categories;
CREATE TABLE system_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
  code TEXT NOT NULL UNIQUE,             -- 分类代码，业务标识符
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  color TEXT,
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  order_index INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE UNIQUE INDEX idx_categories_code ON system_categories(code);
CREATE INDEX idx_categories_enabled ON system_categories(enabled);
CREATE INDEX idx_categories_order ON system_categories(order_index);

-- ========================================
-- 4. 模块标签表 (module_tags) - 已经是自增主键
-- ========================================
DROP TABLE IF EXISTS module_tags;
CREATE TABLE module_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  color TEXT DEFAULT '#409EFF',
  description TEXT,
  usage_count INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_tags_usage_count ON module_tags(usage_count);

-- ========================================
-- 5. 系统操作日志表 (system_operation_logs) - 已经是自增主键
-- ========================================
DROP TABLE IF EXISTS system_operation_logs;
CREATE TABLE system_operation_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  system_id INTEGER,                     -- 关联系统的自增ID
  system_uuid TEXT,                      -- 关联系统的UUID
  module_id INTEGER,                     -- 关联模块的自增ID
  module_uuid TEXT,                      -- 关联模块的UUID
  operation_type TEXT NOT NULL,
  operation_desc TEXT NOT NULL,
  old_data TEXT, -- JSON格式
  new_data TEXT, -- JSON格式
  operator_id TEXT,
  operator_name TEXT,
  ip_address TEXT,
  user_agent TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_logs_system_id ON system_operation_logs(system_id);
CREATE INDEX idx_logs_system_uuid ON system_operation_logs(system_uuid);
CREATE INDEX idx_logs_module_id ON system_operation_logs(module_id);
CREATE INDEX idx_logs_module_uuid ON system_operation_logs(module_uuid);
CREATE INDEX idx_logs_operation_type ON system_operation_logs(operation_type);
CREATE INDEX idx_logs_operator_id ON system_operation_logs(operator_id);
CREATE INDEX idx_logs_created_at ON system_operation_logs(created_at);

-- ========================================
-- 触发器：自动更新 updated_at 字段
-- ========================================

-- 管理系统表更新触发器
CREATE TRIGGER update_systems_timestamp 
AFTER UPDATE ON management_systems
BEGIN
  UPDATE management_systems SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 服务模块表更新触发器
CREATE TRIGGER update_modules_timestamp 
AFTER UPDATE ON service_modules
BEGIN
  UPDATE service_modules SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 系统分类表更新触发器
CREATE TRIGGER update_categories_timestamp 
AFTER UPDATE ON system_categories
BEGIN
  UPDATE system_categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 模块标签表更新触发器
CREATE TRIGGER update_tags_timestamp 
AFTER UPDATE ON module_tags
BEGIN
  UPDATE module_tags SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ========================================
-- 视图：为了向后兼容，创建视图映射UUID到ID
-- ========================================

-- 系统视图（UUID作为主键）
CREATE VIEW v_management_systems AS
SELECT 
  uuid as id,
  id as internal_id,
  name,
  description,
  icon,
  category,
  enabled,
  order_index,
  url,
  metadata,
  deleted,
  deleted_at,
  created_at,
  updated_at,
  created_by,
  updated_by
FROM management_systems
WHERE deleted = 0;

-- 模块视图（UUID作为主键）
CREATE VIEW v_service_modules AS
SELECT 
  uuid as id,
  id as internal_id,
  system_uuid as system_id,
  system_id as internal_system_id,
  name,
  description,
  icon,
  path,
  method,
  enabled,
  version,
  module_type,
  tags,
  config,
  order_index,
  deleted,
  deleted_at,
  created_at,
  updated_at,
  created_by,
  updated_by
FROM service_modules
WHERE deleted = 0;