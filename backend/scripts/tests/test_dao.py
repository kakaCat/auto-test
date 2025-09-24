#!/usr/bin/env python3
"""
测试DAO方法
"""
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auto_test.database.dao.system_dao_optimized import SystemDAOOptimized

def test_system_dao():
    """测试系统DAO"""
    try:
        dao = SystemDAOOptimized()
        print("正在测试get_all_systems方法...")
        systems = dao.get_all_systems()
        print(f"成功获取到 {len(systems)} 个系统")
        if systems:
            print(f"第一个系统: {systems[0]}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system_dao()