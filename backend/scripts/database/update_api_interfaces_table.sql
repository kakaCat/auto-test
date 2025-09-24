-- 更新API接口表，添加testing状态支持
-- Update API interfaces table to support testing status

-- 由于SQLite不支持直接修改CHECK约束，需要重建表
-- Since SQLite doesn't support modifying CHECK constraints directly, we need to rebuild the table

BEGIN TRANSACTION;

-- 创建新的临时表
CREATE TABLE api_interfaces_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    module_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    method TEXT NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')),
    path TEXT NOT NULL,
    version TEXT DEFAULT 'v1',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deprecated', 'testing')),
    request_format TEXT DEFAULT 'json' CHECK (request_format IN ('json', 'form', 'xml')),
    response_format TEXT DEFAULT 'json' CHECK (response_format IN ('json', 'xml', 'text')),
    auth_required INTEGER DEFAULT 1 CHECK (auth_required IN (0, 1)),
    rate_limit INTEGER DEFAULT 1000,
    timeout INTEGER DEFAULT 30,
    tags TEXT,
    request_schema TEXT,
    response_schema TEXT,
    example_request TEXT,
    example_response TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems (id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE SET NULL,
    UNIQUE(system_id, method, path, version)
);

-- 复制数据
INSERT INTO api_interfaces_new 
SELECT * FROM api_interfaces;

-- 删除旧表
DROP TABLE api_interfaces;

-- 重命名新表
ALTER TABLE api_interfaces_new RENAME TO api_interfaces;

-- 重新创建索引
CREATE INDEX idx_api_interfaces_system_id ON api_interfaces(system_id);
CREATE INDEX idx_api_interfaces_module_id ON api_interfaces(module_id);
CREATE INDEX idx_api_interfaces_method ON api_interfaces(method);
CREATE INDEX idx_api_interfaces_status ON api_interfaces(status);
CREATE INDEX idx_api_interfaces_path ON api_interfaces(path);
CREATE INDEX idx_api_interfaces_version ON api_interfaces(version);

COMMIT;