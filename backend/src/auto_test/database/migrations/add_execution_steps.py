#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加执行步骤记录表

创建时间：2024-01-01
作者：AI Assistant
描述：为AI代理执行系统添加详细的步骤记录功能
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scenario_management.models import (
    Base,
    ScenarioExecution,
    ScenarioExecutionStep,
    ScenarioExecutionLog
)

def get_database_url():
    """获取数据库连接URL"""
    # 这里可以从配置文件或环境变量读取
    # 默认使用SQLite数据库
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'auto_test.db'
    )
    return f'sqlite:///{db_path}'

def create_tables(engine):
    """创建数据库表"""
    print("正在创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(engine)
    
    print("数据库表创建完成！")

def add_sample_data(session):
    """添加示例数据（可选）"""
    print("添加示例数据...")
    
    try:
        # 检查是否已有数据
        existing_execution = session.query(ScenarioExecution).first()
        if existing_execution:
            print("数据库中已有执行记录，跳过示例数据添加")
            return
        
        # 创建示例执行记录
        sample_execution = ScenarioExecution(
            scenario_id=1,
            execution_id='sample_execution_001',
            user_description='示例场景执行',
            original_parameters={'test_param': 'test_value'},
            ai_enhanced_parameters={'enhanced_param': 'enhanced_value'},
            ai_reasoning='这是一个示例AI推理过程',
            status='completed',
            progress=100.0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_steps=2,
            completed_steps=2,
            failed_steps=0,
            execution_context={'context': 'sample'},
            environment_info={'env': 'development'},
            input_data={'input': 'sample'},
            output_data={'output': 'sample'},
            error_info=None,
            performance_metrics={'duration_ms': 1000}
        )
        
        session.add(sample_execution)
        session.flush()  # 获取ID
        
        # 创建示例步骤记录
        sample_steps = [
            ScenarioExecutionStep(
                execution_id=sample_execution.id,
                step_order=1,
                api_id=1,
                step_name='示例API调用1',
                original_description='用户原始描述',
                ai_enhanced_params={'param1': 'value1'},
                ai_reasoning='AI参数增强推理',
                input_parameters={'input': 'test1'},
                enhanced_parameters={'enhanced': 'test1'},
                status='completed',
                request_url='https://api.example.com/test1',
                request_method='GET',
                request_headers={'Content-Type': 'application/json'},
                request_body=None,
                response_status_code=200,
                response_headers={'Content-Type': 'application/json'},
                response_body={'result': 'success'},
                response_time_ms=500.0,
                output_parameters={'output': 'result1'},
                extracted_data={'extracted': 'data1'},
                mapped_variables={'var1': 'value1'},
                execution_context={'step_context': 'test1'},
                environment_info={'step_env': 'dev1'},
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=500.0
            ),
            ScenarioExecutionStep(
                execution_id=sample_execution.id,
                step_order=2,
                api_id=2,
                step_name='示例API调用2',
                original_description='用户原始描述',
                ai_enhanced_params={'param2': 'value2'},
                ai_reasoning='AI参数增强推理',
                input_parameters={'input': 'test2'},
                enhanced_parameters={'enhanced': 'test2'},
                status='completed',
                request_url='https://api.example.com/test2',
                request_method='POST',
                request_headers={'Content-Type': 'application/json'},
                request_body={'data': 'test2'},
                response_status_code=201,
                response_headers={'Content-Type': 'application/json'},
                response_body={'result': 'created'},
                response_time_ms=300.0,
                output_parameters={'output': 'result2'},
                extracted_data={'extracted': 'data2'},
                mapped_variables={'var2': 'value2'},
                execution_context={'step_context': 'test2'},
                environment_info={'step_env': 'dev2'},
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=300.0
            )
        ]
        
        for step in sample_steps:
            session.add(step)
        
        session.commit()
        print("示例数据添加完成！")
        
    except Exception as e:
        session.rollback()
        print(f"添加示例数据失败: {e}")

def main():
    """主函数"""
    print("开始数据库迁移：添加执行步骤记录表")
    print("=" * 50)
    
    try:
        # 创建数据库引擎
        database_url = get_database_url()
        print(f"数据库URL: {database_url}")
        
        engine = create_engine(database_url, echo=True)
        
        # 创建表
        create_tables(engine)
        
        # 创建会话
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # 添加示例数据（可选）
            add_sample_data(session)
            
        finally:
            session.close()
        
        print("=" * 50)
        print("数据库迁移完成！")
        print("\n新增的表：")
        print("- scenario_execution_steps: 场景执行步骤记录表")
        print("- 扩展了 scenario_executions 表的关联关系")
        print("- 扩展了 scenario_execution_logs 表的关联关系")
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()