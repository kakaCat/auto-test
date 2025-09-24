-- ========================================
-- 数据库迁移脚本：添加逻辑删除字段
-- 创建时间: 2024-01-20
-- 描述: 为管理系统表和服务模块表添加deleted字段，支持逻辑删除
-- ========================================

-- 为管理系统表添加deleted字段
ALTER TABLE management_systems 
ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1));

-- 为服务模块表添加deleted字段
ALTER TABLE service_modules 
ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1));

-- 创建索引以提高查询性能
CREATE INDEX idx_systems_deleted ON management_systems(deleted);
CREATE INDEX idx_modules_deleted ON service_modules(deleted);

-- 添加deleted_at字段记录删除时间
ALTER TABLE management_systems 
ADD COLUMN deleted_at DATETIME DEFAULT NULL;

ALTER TABLE service_modules 
ADD COLUMN deleted_at DATETIME DEFAULT NULL;

-- 创建索引
CREATE INDEX idx_systems_deleted_at ON management_systems(deleted_at);
CREATE INDEX idx_modules_deleted_at ON service_modules(deleted_at);

-- 验证字段添加成功
SELECT 'Migration completed successfully' as status;