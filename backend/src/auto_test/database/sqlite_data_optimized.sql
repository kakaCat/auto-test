-- ========================================
-- 服务管理系统SQLite示例数据 (优化版)
-- 创建时间: 2024-01-20
-- 描述: 适配新表结构的示例数据，使用自增ID和UUID
-- ========================================

-- ========================================
-- 1. 插入系统分类数据
-- ========================================
INSERT INTO system_categories (code, name, description, icon, color, enabled, order_index) VALUES
('backend', '后端服务', '后端API服务和业务逻辑', 'el-icon-s-platform', '#409EFF', 1, 1),
('frontend', '前端应用', '前端用户界面和交互应用', 'el-icon-monitor', '#67C23A', 1, 2);

-- ========================================
-- 2. 插入管理系统数据
-- ========================================
INSERT INTO management_systems (uuid, name, description, icon, category, enabled, order_index, metadata, created_by) VALUES
('550e8400-e29b-41d4-a716-446655440001', '用户管理系统', '负责用户注册、登录、权限管理等功能', 'el-icon-user', 'backend', 1, 1, 
 '{"version": "1.2.0", "maintainer": "admin", "last_updated": "2024-01-20"}', 'system'),

('550e8400-e29b-41d4-a716-446655440002', '订单管理系统', '处理订单创建、支付、发货等业务逻辑', 'el-icon-shopping-cart-2', 'backend', 1, 2,
 '{"version": "2.1.0", "maintainer": "admin", "last_updated": "2024-01-20"}', 'system'),

('550e8400-e29b-41d4-a716-446655440003', '系统监控', '系统性能监控和日志管理', 'el-icon-monitor', 'frontend', 1, 3,
 '{"version": "1.0.0", "maintainer": "admin", "last_updated": "2024-01-20"}', 'system'),

('550e8400-e29b-41d4-a716-446655440004', 'API网关', 'API接口管理和路由控制', 'el-icon-connection', 'backend', 0, 4,
 '{"version": "1.5.0", "maintainer": "admin", "last_updated": "2024-01-20"}', 'system'),

('550e8400-e29b-41d4-a716-446655440005', '工作流引擎', '业务流程自动化处理', 'el-icon-share', 'backend', 1, 5,
 '{"version": "2.0.0", "maintainer": "admin", "last_updated": "2024-01-20"}', 'system');

-- ========================================
-- 3. 插入模块标签数据
-- ========================================
INSERT INTO module_tags (name, color, description, usage_count) VALUES
('用户', '#409EFF', '用户相关功能', 3),
('注册', '#67C23A', '用户注册功能', 1),
('登录', '#E6A23C', '用户登录功能', 1),
('权限', '#F56C6C', '权限管理功能', 1),
('管理', '#909399', '管理类功能', 2),
('订单', '#606266', '订单相关功能', 2),
('创建', '#303133', '创建类功能', 2),
('支付', '#C0C4CC', '支付相关功能', 1),
('处理', '#17A2B8', '处理类功能', 1),
('监控', '#28A745', '监控相关功能', 2),
('性能', '#FFC107', '性能相关功能', 1),
('API', '#DC3545', 'API相关功能', 2),
('网关', '#6F42C1', '网关功能', 1),
('路由', '#FD7E14', '路由功能', 1),
('工作流', '#20C997', '工作流功能', 2),
('自动化', '#6610F2', '自动化功能', 1);

-- ========================================
-- 4. 插入服务模块数据
-- ========================================

-- 获取系统ID的临时变量（SQLite不支持变量，使用子查询）

-- 用户管理系统模块
INSERT INTO service_modules (uuid, system_id, system_uuid, name, description, icon, path, method, enabled, version, tags, config, order_index, created_by) VALUES
('650e8400-e29b-41d4-a716-446655440001', 
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440001'), 
 '550e8400-e29b-41d4-a716-446655440001',
 '用户注册', '用户注册功能模块', 'el-icon-user-solid', '/user/register', 'POST', 1, '1.2.0', 
 '["用户", "注册"]', 
 '{"timeout": 30, "retry_count": 3, "validation": {"email_required": true, "phone_required": false}}', 1, 'system'),

('650e8400-e29b-41d4-a716-446655440002',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440001'), 
 '550e8400-e29b-41d4-a716-446655440001',
 '用户登录', '用户登录功能模块', 'el-icon-key', '/user/login', 'POST', 1, '1.2.0',
 '["用户", "登录"]',
 '{"timeout": 15, "retry_count": 5, "session_timeout": 3600}', 2, 'system'),

('650e8400-e29b-41d4-a716-446655440003',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440001'), 
 '550e8400-e29b-41d4-a716-446655440001',
 '权限管理', '用户权限管理模块', 'el-icon-lock', '/user/permissions', 'GET', 0, '1.1.0',
 '["权限", "管理"]',
 '{"cache_enabled": true, "cache_ttl": 300}', 3, 'system'),

-- 订单管理系统模块
('650e8400-e29b-41d4-a716-446655440004',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440002'), 
 '550e8400-e29b-41d4-a716-446655440002',
 '订单创建', '订单创建功能模块', 'el-icon-plus', '/order/create', 'POST', 1, '2.1.0',
 '["订单", "创建"]',
 '{"auto_confirm": false, "inventory_check": true}', 1, 'system'),

('650e8400-e29b-41d4-a716-446655440005',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440002'), 
 '550e8400-e29b-41d4-a716-446655440002',
 '支付处理', '订单支付处理模块', 'el-icon-money', '/order/payment', 'POST', 1, '2.0.5',
 '["支付", "处理"]',
 '{"payment_timeout": 900, "supported_methods": ["alipay", "wechat", "bank"]}', 2, 'system'),

('650e8400-e29b-41d4-a716-446655440006',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440002'), 
 '550e8400-e29b-41d4-a716-446655440002',
 '订单查询', '订单信息查询模块', 'el-icon-search', '/order/query', 'GET', 1, '2.0.0',
 '["订单", "查询"]',
 '{"page_size": 20, "max_query_range": 90}', 3, 'system'),

-- 系统监控模块
('650e8400-e29b-41d4-a716-446655440007',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440003'), 
 '550e8400-e29b-41d4-a716-446655440003',
 '性能监控', '系统性能实时监控', 'el-icon-odometer', '/monitor/performance', 'GET', 1, '1.0.0',
 '["监控", "性能"]',
 '{"refresh_interval": 5, "alert_threshold": 80}', 1, 'system'),

('650e8400-e29b-41d4-a716-446655440008',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440003'), 
 '550e8400-e29b-41d4-a716-446655440003',
 '日志管理', '系统日志收集和分析', 'el-icon-document-copy', '/monitor/logs', 'GET', 1, '1.0.0',
 '["监控", "日志"]',
 '{"log_level": "INFO", "retention_days": 30}', 2, 'system'),

-- API网关模块
('650e8400-e29b-41d4-a716-446655440009',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440004'), 
 '550e8400-e29b-41d4-a716-446655440004',
 'API路由', 'API请求路由管理', 'el-icon-guide', '/api/routes', 'GET', 0, '1.5.0',
 '["API", "路由"]',
 '{"load_balancing": true, "timeout": 30}', 1, 'system'),

('650e8400-e29b-41d4-a716-446655440010',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440004'), 
 '550e8400-e29b-41d4-a716-446655440004',
 'API文档', 'API接口文档管理', 'el-icon-document', '/api/docs', 'GET', 0, '1.4.0',
 '["API", "文档"]',
 '{"auto_generate": true, "format": "swagger"}', 2, 'system'),

-- 工作流引擎模块
('650e8400-e29b-41d4-a716-446655440011',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440005'), 
 '550e8400-e29b-41d4-a716-446655440005',
 '流程设计', '工作流程设计器', 'el-icon-edit', '/workflow/design', 'GET', 1, '2.0.0',
 '["工作流", "设计"]',
 '{"drag_drop": true, "version_control": true}', 1, 'system'),

('650e8400-e29b-41d4-a716-446655440012',
 (SELECT id FROM management_systems WHERE uuid = '550e8400-e29b-41d4-a716-446655440005'), 
 '550e8400-e29b-41d4-a716-446655440005',
 '流程执行', '工作流程执行引擎', 'el-icon-video-play', '/workflow/execute', 'POST', 1, '2.0.0',
 '["工作流", "自动化"]',
 '{"parallel_execution": true, "error_handling": "retry"}', 2, 'system');