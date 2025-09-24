-- 页面管理相关表结构

-- 页面表
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    route_path VARCHAR(200),
    page_type VARCHAR(50) DEFAULT 'page',  -- page, modal, drawer等
    status VARCHAR(20) DEFAULT 'active',   -- active, inactive, draft
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

-- 页面API关联表
CREATE TABLE IF NOT EXISTS page_apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    api_id INTEGER NOT NULL,
    execution_type VARCHAR(20) DEFAULT 'parallel',  -- parallel(并行), serial(串行)
    execution_order INTEGER DEFAULT 0,              -- 执行顺序，用于串行执行
    trigger_action VARCHAR(50),                     -- 触发动作：load, click, submit, change等
    api_purpose VARCHAR(100),                       -- API作用描述：获取数据、提交表单、跳转等
    success_action VARCHAR(100),                    -- 成功后的动作：跳转、弹框、刷新等
    error_action VARCHAR(100),                      -- 失败后的动作：提示、重试等
    conditions TEXT,                                -- 执行条件（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
    FOREIGN KEY (api_id) REFERENCES api_interfaces(id) ON DELETE CASCADE,
    UNIQUE(page_id, api_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_pages_system_id ON pages(system_id);
CREATE INDEX IF NOT EXISTS idx_pages_status ON pages(status);
CREATE INDEX IF NOT EXISTS idx_page_apis_page_id ON page_apis(page_id);
CREATE INDEX IF NOT EXISTS idx_page_apis_api_id ON page_apis(api_id);
CREATE INDEX IF NOT EXISTS idx_page_apis_execution_order ON page_apis(page_id, execution_order);

-- 插入示例数据
INSERT OR IGNORE INTO pages (id, system_id, name, description, route_path, page_type, status) VALUES
(1, 1, '用户登录页', '用户登录界面，包含登录表单和验证', '/login', 'page', 'active'),
(2, 1, '用户注册页', '用户注册界面，包含注册表单和验证', '/register', 'page', 'active'),
(3, 1, '用户列表页', '显示用户列表，支持搜索和分页', '/users', 'page', 'active'),
(4, 1, '用户详情弹框', '显示用户详细信息的弹框', '', 'modal', 'active'),
(5, 2, '商品列表页', '显示商品列表，支持筛选和排序', '/products', 'page', 'active');

INSERT OR IGNORE INTO page_apis (page_id, api_id, execution_type, execution_order, trigger_action, api_purpose, success_action, error_action) VALUES
-- 用户登录页的API调用
(1, 1, 'serial', 1, 'submit', '验证用户登录信息', '跳转到首页', '显示错误提示'),
(1, 2, 'serial', 2, 'success', '获取用户权限信息', '设置用户状态', '使用默认权限'),

-- 用户注册页的API调用  
(2, 3, 'parallel', 1, 'load', '获取注册配置信息', '初始化表单', '使用默认配置'),
(2, 4, 'serial', 1, 'submit', '提交注册信息', '跳转到登录页', '显示错误提示'),

-- 用户列表页的API调用
(3, 5, 'parallel', 1, 'load', '获取用户列表数据', '渲染用户列表', '显示加载失败'),
(3, 6, 'parallel', 2, 'load', '获取用户统计信息', '显示统计数据', '隐藏统计区域'),
(3, 7, 'serial', 1, 'search', '搜索用户', '更新列表显示', '显示搜索失败'),

-- 用户详情弹框的API调用
(4, 8, 'serial', 1, 'open', '获取用户详细信息', '显示用户详情', '显示获取失败'),
(4, 9, 'serial', 1, 'edit', '更新用户信息', '关闭弹框并刷新列表', '显示更新失败');