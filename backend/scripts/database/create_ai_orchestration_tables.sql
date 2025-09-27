-- ========================================
-- AI编排模块数据库表结构
-- 创建时间: 2024-01-20
-- 描述: 为AI编排模块创建必要的数据库表
-- ========================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- ========================================
-- 1. AI执行记录表 (ai_executions)
-- ========================================
DROP TABLE IF EXISTS ai_executions;
CREATE TABLE ai_executions (
    id INTEGER PRIMARY KEY,
    execution_id TEXT UNIQUE NOT NULL,
    agent_type TEXT NOT NULL,
    input_data TEXT NOT NULL,
    output_data TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_ai_executions_execution_id ON ai_executions(execution_id);
CREATE INDEX idx_ai_executions_status ON ai_executions(status);
CREATE INDEX idx_ai_executions_agent_type ON ai_executions(agent_type);
CREATE INDEX idx_ai_executions_start_time ON ai_executions(start_time);

-- ========================================
-- 2. MCP工具配置表 (mcp_tool_configs)
-- ========================================
DROP TABLE IF EXISTS mcp_tool_configs;
CREATE TABLE mcp_tool_configs (
    id INTEGER PRIMARY KEY,
    tool_name TEXT NOT NULL,
    tool_type TEXT NOT NULL,
    schema_definition TEXT NOT NULL,
    is_enabled INTEGER DEFAULT 1 CHECK (is_enabled IN (0, 1)),
    config_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE UNIQUE INDEX idx_mcp_tool_configs_tool_name ON mcp_tool_configs(tool_name);
CREATE INDEX idx_mcp_tool_configs_tool_type ON mcp_tool_configs(tool_type);
CREATE INDEX idx_mcp_tool_configs_enabled ON mcp_tool_configs(is_enabled);

-- ========================================
-- 3. API编排计划表 (api_orchestration_plans)
-- ========================================
DROP TABLE IF EXISTS api_orchestration_plans;
CREATE TABLE api_orchestration_plans (
    id INTEGER PRIMARY KEY,
    plan_name TEXT NOT NULL,
    description TEXT,
    intent_text TEXT NOT NULL,
    execution_plan TEXT NOT NULL,
    graph_json TEXT NULL,
    metadata TEXT NULL,          -- 包含 involved_system_ids、involved_module_ids、tags、owner_team 等
    preferences TEXT NULL,       -- 包含 prefer_system_id、prefer_module_id，仅用于推荐上下文
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft','published','archived')),
    tags TEXT NULL,
    created_by TEXT,
    is_template INTEGER DEFAULT 0 CHECK (is_template IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_executed_at DATETIME NULL,
    last_execution_status TEXT DEFAULT 'never' CHECK (last_execution_status IN ('success','failed','running','never'))
);

-- 创建索引
CREATE INDEX idx_orchestration_plans_plan_name ON api_orchestration_plans(plan_name);
CREATE INDEX idx_orchestration_plans_created_by ON api_orchestration_plans(created_by);
CREATE INDEX idx_orchestration_plans_is_template ON api_orchestration_plans(is_template);
CREATE INDEX idx_orchestration_plans_status ON api_orchestration_plans(status);
CREATE INDEX idx_orchestration_plans_last_execution_status ON api_orchestration_plans(last_execution_status);

-- ========================================
-- 4. 执行步骤详情表 (execution_steps)
-- ========================================
DROP TABLE IF EXISTS execution_steps;
CREATE TABLE execution_steps (
    id INTEGER PRIMARY KEY,
    execution_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    step_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    start_time DATETIME NULL,
    end_time DATETIME NULL,
    input_data TEXT,
    output_data TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    system_id INTEGER NULL,
    module_id INTEGER NULL,
    api_interface_id INTEGER NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_execution_steps_execution_id ON execution_steps(execution_id);
CREATE INDEX idx_execution_steps_step_id ON execution_steps(step_id);
CREATE INDEX idx_execution_steps_status ON execution_steps(status);
CREATE INDEX idx_execution_steps_step_type ON execution_steps(step_type);
CREATE INDEX idx_execution_steps_system_id ON execution_steps(system_id);
CREATE INDEX idx_execution_steps_module_id ON execution_steps(module_id);
CREATE INDEX idx_execution_steps_api_interface_id ON execution_steps(api_interface_id);

-- ========================================
-- 5. 执行日志表 (execution_logs)
-- ========================================
DROP TABLE IF EXISTS execution_logs;
CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY,
    execution_id TEXT NOT NULL,
    step_id TEXT NULL,
    log_level TEXT NOT NULL DEFAULT 'INFO',
    message TEXT NOT NULL,
    details TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_step_id ON execution_logs(step_id);
CREATE INDEX idx_execution_logs_log_level ON execution_logs(log_level);
CREATE INDEX idx_execution_logs_timestamp ON execution_logs(timestamp);

-- ========================================
-- 6. 执行指标表 (execution_metrics)
-- ========================================
DROP TABLE IF EXISTS execution_metrics;
CREATE TABLE execution_metrics (
    id INTEGER PRIMARY KEY,
    execution_id TEXT NOT NULL,
    step_id TEXT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_execution_metrics_execution_id ON execution_metrics(execution_id);
CREATE INDEX idx_execution_metrics_step_id ON execution_metrics(step_id);
CREATE INDEX idx_execution_metrics_metric_name ON execution_metrics(metric_name);
CREATE INDEX idx_execution_metrics_timestamp ON execution_metrics(timestamp);

-- ========================================
-- 初始化MCP工具配置数据
-- ========================================
INSERT INTO mcp_tool_configs (id, tool_name, tool_type, schema_definition, is_enabled, config_data) VALUES
(1, 'http_request', 'http', '{
    "name": "http_request",
    "description": "执行HTTP请求",
    "inputSchema": {
        "type": "object",
        "properties": {
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
            "url": {"type": "string"},
            "headers": {"type": "object"},
            "body": {"type": "object"},
            "timeout": {"type": "number", "default": 30}
        },
        "required": ["method", "url"]
    }
}', 1, '{"timeout": 30, "retry_count": 3}'),

(2, 'wait_for', 'utility', '{
    "name": "wait_for",
    "description": "等待指定时间",
    "inputSchema": {
        "type": "object",
        "properties": {
            "duration": {"type": "number", "description": "等待时间(秒)"},
            "condition": {"type": "string", "description": "等待条件"}
        },
        "required": ["duration"]
    }
}', 1, '{"max_wait_time": 300}'),

(3, 'validate_response', 'validation', '{
    "name": "validate_response",
    "description": "验证响应结果",
    "inputSchema": {
        "type": "object",
        "properties": {
            "response": {"type": "object"},
            "rules": {"type": "array"},
            "strict": {"type": "boolean", "default": false}
        },
        "required": ["response", "rules"]
    }
}', 1, '{"strict_mode": false}');

-- ========================================
-- 创建视图：执行概览
-- ========================================
CREATE VIEW v_execution_overview AS
SELECT 
    e.execution_id,
    e.agent_type,
    e.status as execution_status,
    e.start_time,
    e.end_time,
    CASE 
        WHEN e.end_time IS NOT NULL THEN 
            ROUND((JULIANDAY(e.end_time) - JULIANDAY(e.start_time)) * 86400, 2)
        ELSE NULL 
    END as duration_seconds,
    COUNT(s.id) as total_steps,
    COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as completed_steps,
    COUNT(CASE WHEN s.status = 'failed' THEN 1 END) as failed_steps,
    COUNT(DISTINCT s.system_id) as involved_systems,
    COUNT(DISTINCT s.module_id) as involved_modules
FROM ai_executions e
LEFT JOIN execution_steps s ON e.execution_id = s.execution_id
GROUP BY e.execution_id, e.agent_type, e.status, e.start_time, e.end_time;

-- ========================================
-- 创建视图：系统模块执行统计
-- ========================================
CREATE VIEW v_system_execution_stats AS
SELECT 
    sys.id as system_id,
    sys.name as system_name,
    mod.id as module_id,
    mod.name as module_name,
    COUNT(s.id) as total_executions,
    COUNT(CASE WHEN s.status = 'completed' THEN 1 END) as success_count,
    COUNT(CASE WHEN s.status = 'failed' THEN 1 END) as failure_count,
    ROUND(AVG(CASE 
        WHEN s.end_time IS NOT NULL AND s.start_time IS NOT NULL THEN 
            (JULIANDAY(s.end_time) - JULIANDAY(s.start_time)) * 86400
        ELSE NULL 
    END), 2) as avg_duration_seconds
FROM execution_steps s
LEFT JOIN management_systems sys ON s.system_id = sys.id
LEFT JOIN service_modules mod ON s.module_id = mod.id
WHERE s.system_id IS NOT NULL
GROUP BY sys.id, sys.name, mod.id, mod.name;