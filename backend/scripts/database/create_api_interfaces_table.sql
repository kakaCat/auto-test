-- 创建API接口表
CREATE TABLE IF NOT EXISTS api_interfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER NOT NULL,
    module_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    method TEXT NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    path TEXT NOT NULL,
    version TEXT DEFAULT 'v1',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deprecated')),
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

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_api_interfaces_system_id ON api_interfaces(system_id);
CREATE INDEX IF NOT EXISTS idx_api_interfaces_module_id ON api_interfaces(module_id);
CREATE INDEX IF NOT EXISTS idx_api_interfaces_method ON api_interfaces(method);
CREATE INDEX IF NOT EXISTS idx_api_interfaces_status ON api_interfaces(status);
CREATE INDEX IF NOT EXISTS idx_api_interfaces_path ON api_interfaces(path);
CREATE INDEX IF NOT EXISTS idx_api_interfaces_version ON api_interfaces(version);

-- 插入示例数据
INSERT OR IGNORE INTO api_interfaces (
    system_id, module_id, name, description, method, path, version, status,
    request_format, response_format, auth_required, rate_limit, timeout, tags,
    request_schema, response_schema, example_request, example_response
) VALUES 
(1, 1, '用户注册', '用户注册接口', 'POST', '/api/users/register', 'v1', 'active',
 'json', 'json', 0, 100, 30, 'user,auth,register',
 '{"username": "string", "password": "string", "email": "string"}',
 '{"code": 200, "message": "success", "data": {"user_id": "integer", "token": "string"}}',
 '{"username": "testuser", "password": "123456", "email": "test@example.com"}',
 '{"code": 200, "message": "注册成功", "data": {"user_id": 1, "token": "abc123"}}'),

(1, 1, '用户登录', '用户登录接口', 'POST', '/api/users/login', 'v1', 'active',
 'json', 'json', 0, 200, 30, 'user,auth,login',
 '{"username": "string", "password": "string"}',
 '{"code": 200, "message": "success", "data": {"token": "string", "user_info": "object"}}',
 '{"username": "testuser", "password": "123456"}',
 '{"code": 200, "message": "登录成功", "data": {"token": "abc123", "user_info": {"id": 1, "username": "testuser"}}}'),

(1, 1, '获取用户信息', '根据用户ID获取用户详细信息', 'GET', '/api/users/{id}', 'v1', 'active',
 'json', 'json', 1, 1000, 30, 'user,profile',
 '{}',
 '{"code": 200, "message": "success", "data": {"user": "object"}}',
 '{}',
 '{"code": 200, "message": "获取成功", "data": {"user": {"id": 1, "username": "testuser", "email": "test@example.com"}}}'),

(2, 2, '创建订单', '创建新订单', 'POST', '/api/orders', 'v1', 'active',
 'json', 'json', 1, 500, 60, 'order,create',
 '{"product_id": "integer", "quantity": "integer", "customer_info": "object"}',
 '{"code": 200, "message": "success", "data": {"order_id": "integer"}}',
 '{"product_id": 1, "quantity": 2, "customer_info": {"name": "张三", "phone": "13800138000"}}',
 '{"code": 200, "message": "订单创建成功", "data": {"order_id": 1001}}'),

(2, 2, '查询订单', '根据订单ID查询订单详情', 'GET', '/api/orders/{id}', 'v1', 'active',
 'json', 'json', 1, 1000, 30, 'order,query',
 '{}',
 '{"code": 200, "message": "success", "data": {"order": "object"}}',
 '{}',
 '{"code": 200, "message": "查询成功", "data": {"order": {"id": 1001, "status": "pending", "total": 299.99}}}'),

(3, 3, '查询库存', '查询商品库存信息', 'GET', '/api/inventory/{product_id}', 'v1', 'active',
 'json', 'json', 1, 2000, 30, 'inventory,query',
 '{}',
 '{"code": 200, "message": "success", "data": {"inventory": "object"}}',
 '{}',
 '{"code": 200, "message": "查询成功", "data": {"inventory": {"product_id": 1, "quantity": 100, "reserved": 10}}}'),

(3, 4, '更新库存', '更新商品库存数量', 'PUT', '/api/inventory/{product_id}', 'v1', 'active',
 'json', 'json', 1, 100, 30, 'inventory,update',
 '{"quantity": "integer", "operation": "string"}',
 '{"code": 200, "message": "success", "data": {"new_quantity": "integer"}}',
 '{"quantity": 50, "operation": "add"}',
 '{"code": 200, "message": "库存更新成功", "data": {"new_quantity": 150}}');