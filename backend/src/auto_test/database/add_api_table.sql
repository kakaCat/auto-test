-- ========================================
-- 添加API接口表
-- 创建时间: 2024-01-20
-- 描述: 为系统管理添加独立的API接口表
-- ========================================

-- ========================================
-- API接口表 (api_interfaces)
-- ========================================
DROP TABLE IF EXISTS api_interfaces;
CREATE TABLE api_interfaces (
  id TEXT PRIMARY KEY NOT NULL,
  system_id TEXT NOT NULL,
  module_id TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  path TEXT NOT NULL,
  method TEXT NOT NULL DEFAULT 'GET',
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  version TEXT NOT NULL DEFAULT '1.0.0',
  request_headers TEXT, -- JSON格式的字符串
  request_params TEXT, -- JSON格式的字符串
  request_body TEXT, -- JSON格式的字符串
  response_example TEXT, -- JSON格式的字符串
  tags TEXT, -- JSON数组格式的字符串
  metadata TEXT, -- JSON格式的字符串
  order_index INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  updated_by TEXT,
  FOREIGN KEY (system_id) REFERENCES management_systems(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (module_id) REFERENCES service_modules(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建索引
CREATE INDEX idx_apis_system_id ON api_interfaces(system_id);
CREATE INDEX idx_apis_module_id ON api_interfaces(module_id);
CREATE INDEX idx_apis_enabled ON api_interfaces(enabled);
CREATE INDEX idx_apis_path ON api_interfaces(path);
CREATE INDEX idx_apis_method ON api_interfaces(method);
CREATE INDEX idx_apis_version ON api_interfaces(version);
CREATE INDEX idx_apis_created_at ON api_interfaces(created_at);

-- API接口表更新触发器
CREATE TRIGGER update_apis_timestamp 
AFTER UPDATE ON api_interfaces
BEGIN
  UPDATE api_interfaces SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;