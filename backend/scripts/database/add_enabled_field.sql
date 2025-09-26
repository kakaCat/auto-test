-- 添加enabled字段到api_interfaces表
-- 用于支持前后端兼容性

BEGIN TRANSACTION;

-- 添加enabled字段，默认值为1（启用）
ALTER TABLE api_interfaces ADD COLUMN enabled INTEGER DEFAULT 1;

-- 根据现有的status字段初始化enabled字段的值
-- active状态对应enabled=1，其他状态对应enabled=0
UPDATE api_interfaces 
SET enabled = CASE 
    WHEN status = 'active' THEN 1 
    ELSE 0 
END;

-- 创建索引以提高查询性能
CREATE INDEX idx_api_interfaces_enabled ON api_interfaces(enabled);

COMMIT;