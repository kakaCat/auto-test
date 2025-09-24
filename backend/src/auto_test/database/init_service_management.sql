-- ========================================
-- 服务管理系统数据库初始化脚本
-- 创建时间: 2024-01-20
-- 描述: 一键初始化服务管理相关的数据库表和数据
-- 使用方法: mysql -u username -p database_name < init_service_management.sql
-- ========================================

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS `auto_test_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE `auto_test_db`;

-- 执行表结构创建
SOURCE service_management_schema.sql;

-- 执行示例数据插入
SOURCE service_management_data.sql;

-- 显示创建结果
SELECT '========================================' as '';
SELECT '数据库初始化完成' as '状态';
SELECT '========================================' as '';

-- 显示统计信息
SELECT 
    '系统分类' as '表名',
    COUNT(*) as '记录数'
FROM system_categories
UNION ALL
SELECT 
    '管理系统' as '表名',
    COUNT(*) as '记录数'
FROM management_systems
UNION ALL
SELECT 
    '服务模块' as '表名',
    COUNT(*) as '记录数'
FROM service_modules
UNION ALL
SELECT 
    '模块标签' as '表名',
    COUNT(*) as '记录数'
FROM module_tags
UNION ALL
SELECT 
    '标签关联' as '表名',
    COUNT(*) as '记录数'
FROM module_tag_relations
UNION ALL
SELECT 
    '操作日志' as '表名',
    COUNT(*) as '记录数'
FROM system_operation_logs;

SELECT '========================================' as '';
SELECT '初始化完成，可以开始使用服务管理功能' as '提示';
SELECT '========================================' as '';