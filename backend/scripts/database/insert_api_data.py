import sqlite3
import json
import uuid

# 连接数据库
db_path = 'src/auto_test/database/service_management.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取现有的系统和模块
cursor.execute('SELECT id, name FROM management_systems LIMIT 2')
systems = cursor.fetchall()

cursor.execute('SELECT id, name, system_id FROM service_modules LIMIT 5')
modules = cursor.fetchall()

# 为每个模块创建几个API接口
api_templates = [
    {'name': '获取列表', 'path': '/list', 'method': 'GET', 'description': '获取数据列表'},
    {'name': '创建数据', 'path': '/create', 'method': 'POST', 'description': '创建新数据'},
    {'name': '更新数据', 'path': '/update/{id}', 'method': 'PUT', 'description': '更新指定数据'}
]

for module in modules:
    module_id, module_name, system_id = module
    
    # 为每个模块创建2-3个API
    for i, template in enumerate(api_templates):
        api_id = str(uuid.uuid4())
        
        api_data = {
            'id': api_id,
            'system_id': system_id,
            'module_id': module_id,
            'name': f'{module_name} - {template["name"]}',
            'description': f'{module_name}模块的{template["description"]}接口',
            'path': f'/api/{module_name.lower()}{template["path"]}',
            'method': template['method'],
            'enabled': 1,
            'version': '1.0.0',
            'request_headers': json.dumps({'Content-Type': 'application/json'}),
            'request_params': json.dumps({}),
            'request_body': json.dumps({}),
            'response_example': json.dumps({'success': True, 'data': {}, 'message': '操作成功'}),
            'tags': json.dumps([template['method'], module_name]),
            'metadata': json.dumps({}),
            'order_index': i
        }
        
        columns = ', '.join(api_data.keys())
        placeholders = ', '.join(['?' for _ in api_data])
        sql = f'INSERT INTO api_interfaces ({columns}) VALUES ({placeholders})'
        
        cursor.execute(sql, list(api_data.values()))

conn.commit()
conn.close()

print('示例API数据插入成功')