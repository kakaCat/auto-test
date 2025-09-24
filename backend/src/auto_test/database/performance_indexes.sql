-- 数据库性能优化索引脚本
-- 为常用查询字段创建索引，提高查询性能

-- API接口表索引
CREATE INDEX IF NOT EXISTS idx_api_system_id ON api_interfaces(system_id);
CREATE INDEX IF NOT EXISTS idx_api_module_id ON api_interfaces(module_id);
CREATE INDEX IF NOT EXISTS idx_api_enabled ON api_interfaces(enabled);
CREATE INDEX IF NOT EXISTS idx_api_method ON api_interfaces(method);
CREATE INDEX IF NOT EXISTS idx_api_name ON api_interfaces(name);
CREATE INDEX IF NOT EXISTS idx_api_path ON api_interfaces(path);
CREATE INDEX IF NOT EXISTS idx_api_created_at ON api_interfaces(created_at);
CREATE INDEX IF NOT EXISTS idx_api_order_index ON api_interfaces(order_index);

-- 复合索引优化常用查询组合
CREATE INDEX IF NOT EXISTS idx_api_system_enabled ON api_interfaces(system_id, enabled);
CREATE INDEX IF NOT EXISTS idx_api_module_enabled ON api_interfaces(module_id, enabled);
CREATE INDEX IF NOT EXISTS idx_api_system_module ON api_interfaces(system_id, module_id);

-- 服务模块表索引
CREATE INDEX IF NOT EXISTS idx_module_system_id ON service_modules(system_id);
CREATE INDEX IF NOT EXISTS idx_module_enabled ON service_modules(enabled);
CREATE INDEX IF NOT EXISTS idx_module_name ON service_modules(name);
CREATE INDEX IF NOT EXISTS idx_module_created_at ON service_modules(created_at);
CREATE INDEX IF NOT EXISTS idx_module_order_index ON service_modules(order_index);

-- 复合索引
CREATE INDEX IF NOT EXISTS idx_module_system_enabled ON service_modules(system_id, enabled);

-- 管理系统表索引
CREATE INDEX IF NOT EXISTS idx_system_enabled ON management_systems(enabled);
CREATE INDEX IF NOT EXISTS idx_system_name ON management_systems(name);
CREATE INDEX IF NOT EXISTS idx_system_created_at ON management_systems(created_at);

-- 工作流表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_workflow_system_id ON workflows(system_id);
CREATE INDEX IF NOT EXISTS idx_workflow_enabled ON workflows(enabled);
CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflow_created_at ON workflows(created_at);

-- 工作流节点表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_workflow_node_workflow_id ON workflow_nodes(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_node_type ON workflow_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_workflow_node_order ON workflow_nodes(order_index);

-- 执行记录表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_execution_workflow_id ON execution_records(workflow_id);
CREATE INDEX IF NOT EXISTS idx_execution_status ON execution_records(status);
CREATE INDEX IF NOT EXISTS idx_execution_created_at ON execution_records(created_at);
CREATE INDEX IF NOT EXISTS idx_execution_start_time ON execution_records(start_time);
CREATE INDEX IF NOT EXISTS idx_execution_end_time ON execution_records(end_time);

-- 日志表索引（如果存在）
CREATE INDEX IF NOT EXISTS idx_log_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_log_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS idx_log_source ON logs(source);

-- 全文搜索索引（SQLite FTS5，如果支持）
-- 为API接口创建全文搜索索引
CREATE VIRTUAL TABLE IF NOT EXISTS api_search USING fts5(
    id UNINDEXED,
    name,
    description,
    path,
    content='api_interfaces',
    content_rowid='rowid'
);

-- 为服务模块创建全文搜索索引
CREATE VIRTUAL TABLE IF NOT EXISTS module_search USING fts5(
    id UNINDEXED,
    name,
    description,
    content='service_modules',
    content_rowid='rowid'
);

-- 触发器：保持全文搜索索引同步
CREATE TRIGGER IF NOT EXISTS api_search_insert AFTER INSERT ON api_interfaces BEGIN
    INSERT INTO api_search(rowid, id, name, description, path) 
    VALUES (new.rowid, new.id, new.name, new.description, new.path);
END;

CREATE TRIGGER IF NOT EXISTS api_search_delete AFTER DELETE ON api_interfaces BEGIN
    INSERT INTO api_search(api_search, rowid, id, name, description, path) 
    VALUES('delete', old.rowid, old.id, old.name, old.description, old.path);
END;

CREATE TRIGGER IF NOT EXISTS api_search_update AFTER UPDATE ON api_interfaces BEGIN
    INSERT INTO api_search(api_search, rowid, id, name, description, path) 
    VALUES('delete', old.rowid, old.id, old.name, old.description, old.path);
    INSERT INTO api_search(rowid, id, name, description, path) 
    VALUES (new.rowid, new.id, new.name, new.description, new.path);
END;

-- 模块搜索触发器
CREATE TRIGGER IF NOT EXISTS module_search_insert AFTER INSERT ON service_modules BEGIN
    INSERT INTO module_search(rowid, id, name, description) 
    VALUES (new.rowid, new.id, new.name, new.description);
END;

CREATE TRIGGER IF NOT EXISTS module_search_delete AFTER DELETE ON service_modules BEGIN
    INSERT INTO module_search(module_search, rowid, id, name, description) 
    VALUES('delete', old.rowid, old.id, old.name, old.description);
END;

CREATE TRIGGER IF NOT EXISTS module_search_update AFTER UPDATE ON service_modules BEGIN
    INSERT INTO module_search(module_search, rowid, id, name, description) 
    VALUES('delete', old.rowid, old.id, old.name, old.description);
    INSERT INTO module_search(rowid, id, name, description) 
    VALUES (new.rowid, new.id, new.name, new.description);
END;

-- 分析表统计信息，优化查询计划
ANALYZE;

-- 优化数据库
PRAGMA optimize;