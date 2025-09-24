-- ========================================
-- 服务管理系统SQLite数据库表结构 (简化版)
-- 创建时间: 2024-01-20
-- 描述: 使用自增ID作为主键，移除UUID字段
-- ========================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- ========================================
-- 1. 管理系统表 (management_systems) - 简化版
-- ========================================
DROP TABLE IF EXISTS management_systems;
CREATE TABLE management_systems (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
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
CREATE INDEX idx_systems_category ON management_systems(category);
CREATE INDEX idx_systems_enabled ON management_systems(enabled);
CREATE INDEX idx_systems_deleted ON management_systems(deleted);
CREATE INDEX idx_systems_order ON management_systems(order_index);
CREATE INDEX idx_systems_created_at ON management_systems(created_at);
CREATE INDEX idx_systems_deleted_at ON management_systems(deleted_at);

-- ========================================
-- 2. 服务模块表 (service_modules) - 简化版
-- ========================================
DROP TABLE IF EXISTS service_modules;
CREATE TABLE service_modules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
  system_id INTEGER NOT NULL,            -- 关联系统的自增ID
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
CREATE INDEX idx_modules_system_id ON service_modules(system_id);
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
-- 4. API接口表 (api_interfaces) - 简化版
-- ========================================
DROP TABLE IF EXISTS api_interfaces;
CREATE TABLE api_interfaces (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
  system_id INTEGER NOT NULL,            -- 关联系统ID
  module_id INTEGER NOT NULL,            -- 关联模块ID
  name TEXT NOT NULL,
  description TEXT,
  path TEXT NOT NULL,
  method TEXT NOT NULL DEFAULT 'GET',
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  version TEXT NOT NULL DEFAULT '1.0.0',
  request_headers TEXT, -- JSON格式
  request_params TEXT,  -- JSON格式
  request_body TEXT,    -- JSON格式
  response_example TEXT, -- JSON格式
  tags TEXT,            -- JSON数组格式
  metadata TEXT,        -- JSON格式
  order_index INTEGER NOT NULL DEFAULT 0,
  deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1)),
  deleted_at DATETIME DEFAULT NULL,
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
CREATE INDEX idx_apis_deleted ON api_interfaces(deleted);
CREATE INDEX idx_apis_path ON api_interfaces(path);
CREATE INDEX idx_apis_method ON api_interfaces(method);
CREATE INDEX idx_apis_version ON api_interfaces(version);
CREATE INDEX idx_apis_created_at ON api_interfaces(created_at);
CREATE INDEX idx_apis_deleted_at ON api_interfaces(deleted_at);

-- ========================================
-- 5. 测试场景表 (test_scenarios) - 简化版
-- ========================================
DROP TABLE IF EXISTS test_scenarios;
CREATE TABLE test_scenarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
  api_id INTEGER NOT NULL,               -- 关联API ID
  name TEXT NOT NULL,
  description TEXT,
  scenario_type TEXT NOT NULL DEFAULT 'functional',
  test_data TEXT,       -- JSON格式的测试数据
  expected_result TEXT, -- JSON格式的期望结果
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
  priority INTEGER NOT NULL DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
  tags TEXT,           -- JSON数组格式
  metadata TEXT,       -- JSON格式
  order_index INTEGER NOT NULL DEFAULT 0,
  deleted INTEGER NOT NULL DEFAULT 0 CHECK (deleted IN (0, 1)),
  deleted_at DATETIME DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  updated_by TEXT,
  FOREIGN KEY (api_id) REFERENCES api_interfaces(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建索引
CREATE INDEX idx_scenarios_api_id ON test_scenarios(api_id);
CREATE INDEX idx_scenarios_enabled ON test_scenarios(enabled);
CREATE INDEX idx_scenarios_deleted ON test_scenarios(deleted);
CREATE INDEX idx_scenarios_type ON test_scenarios(scenario_type);
CREATE INDEX idx_scenarios_priority ON test_scenarios(priority);
CREATE INDEX idx_scenarios_created_at ON test_scenarios(created_at);
CREATE INDEX idx_scenarios_deleted_at ON test_scenarios(deleted_at);

-- ========================================
-- 6. 测试执行记录表 (test_executions) - 简化版
-- ========================================
DROP TABLE IF EXISTS test_executions;
CREATE TABLE test_executions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
  scenario_id INTEGER NOT NULL,          -- 关联测试场景ID
  execution_status TEXT NOT NULL DEFAULT 'pending',
  start_time DATETIME,
  end_time DATETIME,
  duration INTEGER, -- 执行时长(毫秒)
  request_data TEXT,  -- JSON格式的实际请求数据
  response_data TEXT, -- JSON格式的实际响应数据
  error_message TEXT,
  logs TEXT,          -- 执行日志
  metadata TEXT,      -- JSON格式
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  updated_by TEXT,
  FOREIGN KEY (scenario_id) REFERENCES test_scenarios(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 创建索引
CREATE INDEX idx_executions_scenario_id ON test_executions(scenario_id);
CREATE INDEX idx_executions_status ON test_executions(execution_status);
CREATE INDEX idx_executions_start_time ON test_executions(start_time);
CREATE INDEX idx_executions_created_at ON test_executions(created_at);

-- ========================================
-- 初始化数据
-- ========================================

-- 插入系统分类
INSERT INTO system_categories (code, name, description, icon, color, order_index) VALUES
('backend', '后端服务', '后端API服务和业务逻辑', 'el-icon-s-platform', '#409EFF', 1),
('frontend', '前端应用', '前端用户界面和交互应用', 'el-icon-monitor', '#67C23A', 2);

-- 插入示例系统
INSERT INTO management_systems (name, description, icon, category, enabled, order_index, url, metadata) VALUES
('用户管理系统', '管理系统用户和权限', 'el-icon-user', 'backend', 1, 1, '/user-management', '{"version": "1.0.0", "author": "system"}'),
('API接口管理', '管理和测试API接口', 'el-icon-connection', 'backend', 1, 2, '/api-management', '{"version": "1.0.0", "author": "system"}'),
('系统监控', '监控系统运行状态', 'el-icon-monitor', 'frontend', 1, 3, '/system-monitor', '{"version": "1.0.0", "author": "system"}');

-- 插入示例模块
INSERT INTO service_modules (system_id, name, description, icon, path, method, enabled, version, module_type, tags, config, order_index) VALUES
(1, '用户列表', '查看和管理用户列表', 'el-icon-user', '/api/users', 'GET', 1, '1.0.0', '查询模块', '["用户", "列表"]', '{"pageSize": 20}', 1),
(1, '添加用户', '添加新用户', 'el-icon-plus', '/api/users', 'POST', 1, '1.0.0', '操作模块', '["用户", "添加"]', '{}', 2),
(2, 'API列表', '查看API接口列表', 'el-icon-menu', '/api/interfaces', 'GET', 1, '1.0.0', '查询模块', '["API", "列表"]', '{"pageSize": 50}', 1),
(2, '测试API', '测试API接口', 'el-icon-cpu', '/api/test', 'POST', 1, '1.0.0', '测试模块', '["API", "测试"]', '{}', 2);