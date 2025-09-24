-- ========================================
-- 数据库迁移脚本：优化表结构
-- 创建时间: 2024-01-20
-- 描述: 将UUID主键改为自增ID主键，UUID作为业务标识符
-- ========================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- ========================================
-- 第一步：备份现有数据
-- ========================================

-- 备份管理系统表
CREATE TABLE management_systems_backup AS 
SELECT * FROM management_systems;

-- 备份服务模块表
CREATE TABLE service_modules_backup AS 
SELECT * FROM service_modules;

-- ========================================
-- 第二步：创建新的表结构
-- ========================================

-- 删除旧表（注意：外键约束会自动处理级联删除）
DROP TABLE IF EXISTS service_modules;
DROP TABLE IF EXISTS management_systems;

-- 创建新的管理系统表
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

-- 创建新的服务模块表
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

-- ========================================
-- 第三步：迁移数据
-- ========================================

-- 迁移管理系统数据
INSERT INTO management_systems (
  uuid, name, description, icon, category, enabled, order_index, url, metadata,
  deleted, deleted_at, created_at, updated_at, created_by, updated_by
)
SELECT 
  id as uuid, name, description, icon, category, enabled, order_index, url, metadata,
  COALESCE(deleted, 0) as deleted, deleted_at, created_at, updated_at, created_by, updated_by
FROM management_systems_backup
ORDER BY created_at;

-- 迁移服务模块数据（需要关联新的system_id）
INSERT INTO service_modules (
  uuid, system_id, system_uuid, name, description, icon, path, method, enabled, version,
  module_type, tags, config, order_index, deleted, deleted_at, created_at, updated_at, created_by, updated_by
)
SELECT 
  smb.id as uuid,
  ms.id as system_id,
  smb.system_id as system_uuid,
  smb.name, smb.description, smb.icon, smb.path, smb.method, smb.enabled, smb.version,
  smb.module_type, smb.tags, smb.config, smb.order_index, 
  COALESCE(smb.deleted, 0) as deleted, smb.deleted_at, smb.created_at, smb.updated_at, smb.created_by, smb.updated_by
FROM service_modules_backup smb
JOIN management_systems ms ON ms.uuid = smb.system_id
ORDER BY smb.created_at;

-- ========================================
-- 第四步：创建索引
-- ========================================

-- 管理系统表索引
CREATE UNIQUE INDEX idx_systems_uuid ON management_systems(uuid);
CREATE INDEX idx_systems_category ON management_systems(category);
CREATE INDEX idx_systems_enabled ON management_systems(enabled);
CREATE INDEX idx_systems_deleted ON management_systems(deleted);
CREATE INDEX idx_systems_order ON management_systems(order_index);
CREATE INDEX idx_systems_created_at ON management_systems(created_at);
CREATE INDEX idx_systems_deleted_at ON management_systems(deleted_at);

-- 服务模块表索引
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
-- 第五步：创建触发器
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

-- ========================================
-- 第六步：创建兼容性视图
-- ========================================

-- 系统视图（UUID作为主键，保持向后兼容）
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

-- 模块视图（UUID作为主键，保持向后兼容）
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

-- ========================================
-- 第七步：验证迁移结果
-- ========================================

-- 验证数据完整性
SELECT 
  'Systems Migration' as table_name,
  (SELECT COUNT(*) FROM management_systems_backup) as original_count,
  (SELECT COUNT(*) FROM management_systems) as migrated_count,
  CASE 
    WHEN (SELECT COUNT(*) FROM management_systems_backup) = (SELECT COUNT(*) FROM management_systems) 
    THEN 'SUCCESS' 
    ELSE 'FAILED' 
  END as status;

SELECT 
  'Modules Migration' as table_name,
  (SELECT COUNT(*) FROM service_modules_backup) as original_count,
  (SELECT COUNT(*) FROM service_modules) as migrated_count,
  CASE 
    WHEN (SELECT COUNT(*) FROM service_modules_backup) = (SELECT COUNT(*) FROM service_modules) 
    THEN 'SUCCESS' 
    ELSE 'FAILED' 
  END as status;

-- 验证外键关联
SELECT 
  'Foreign Key Check' as check_name,
  COUNT(*) as orphaned_modules,
  CASE 
    WHEN COUNT(*) = 0 
    THEN 'SUCCESS' 
    ELSE 'FAILED' 
  END as status
FROM service_modules sm
LEFT JOIN management_systems ms ON sm.system_id = ms.id
WHERE ms.id IS NULL;

-- ========================================
-- 第八步：清理备份表（可选，建议保留一段时间）
-- ========================================

-- 注释掉以下语句，建议手动执行清理
-- DROP TABLE IF EXISTS management_systems_backup;
-- DROP TABLE IF EXISTS service_modules_backup;

SELECT 'Migration completed successfully. Please verify the data and manually drop backup tables when ready.' as message;