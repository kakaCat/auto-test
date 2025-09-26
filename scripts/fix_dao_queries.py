#!/usr/bin/env python3
"""
修复DAO查询脚本 - 移除uuid字段引用
"""
import os
import re

def fix_system_dao_queries(file_path):
    """修复系统DAO查询"""
    print(f"正在修复 {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复所有SELECT查询中的uuid字段引用
    # 将 "s.id, s.uuid, s.name" 替换为 "s.id, s.name"
    content = re.sub(
        r'SELECT\s+s\.id,\s*s\.uuid,\s*s\.name',
        'SELECT s.id, s.name',
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    # 修复完整的SELECT语句
    content = re.sub(
        r'SELECT\s+s\.id,\s*s\.uuid,\s*s\.name,\s*s\.description,\s*s\.icon,\s*\n\s*s\.category,\s*s\.enabled,\s*s\.order_index,\s*s\.url,\s*s\.metadata,\s*\n\s*s\.created_at,\s*s\.updated_at,\s*s\.created_by,\s*s\.updated_by',
        'SELECT s.id, s.name, s.description, s.icon, \n                       s.category, s.enabled, s.order_index, s.url, s.metadata,\n                       s.created_at, s.updated_at, s.created_by, s.updated_by',
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复 {file_path}")

def fix_module_dao_queries(file_path):
    """修复模块DAO查询"""
    print(f"正在修复 {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复模块查询中的uuid字段引用
    # 将 "m.id, m.uuid, m.name" 替换为 "m.id, m.name"
    content = re.sub(
        r'm\.id,\s*m\.uuid,\s*m\.name',
        'm.id, m.name',
        content,
        flags=re.IGNORECASE
    )
    
    # 保留系统表的uuid引用（因为这些是正确的）
    # 但移除模块表的uuid引用
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复 {file_path}")

def main():
    """主函数"""
    backend_dir = "/Users/mac/Documents/ai/auto-test/backend"
    
    # 修复系统DAO
    system_dao_path = os.path.join(backend_dir, "src/auto_test/database/dao/system_dao_optimized.py")
    if os.path.exists(system_dao_path):
        fix_system_dao_queries(system_dao_path)
    
    # 修复模块DAO
    module_dao_path = os.path.join(backend_dir, "src/auto_test/database/dao/module_dao_optimized.py")
    if os.path.exists(module_dao_path):
        fix_module_dao_queries(module_dao_path)
    
    print("所有DAO查询修复完成！")

if __name__ == "__main__":
    main()