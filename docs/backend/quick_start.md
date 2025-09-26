# 快速开始指南

> **架构版本**: v4.0.0  
> **设计理念**: 极简控制器 + 防腐层架构 + 多入口统一业务处理  
> **编码规范**: [极简控制器编码标准](standards/controller_standards.md)

## 🚀 环境准备

### 1. 系统要求
- Python 3.8+
- SQLite 3
- Git

### 2. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动服务
```bash
cd backend
python -m uvicorn src.auto_test.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 快速测试

### 1. 创建系统
```bash
curl -X POST "http://localhost:8000/api/systems/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的测试系统",
    "description": "这是一个测试系统",
    "status": "active"
  }'
```

### 2. 获取系统列表
```bash
curl -X GET "http://localhost:8000/api/systems/"
```

### 3. 创建模块
```bash
curl -X POST "http://localhost:8000/api/modules/" \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": 1,
    "name": "测试模块",
    "description": "这是一个测试模块",
    "status": "active",
    "tags": "test,demo"
  }'
```

### 4. 获取模块列表
```bash
curl -X GET "http://localhost:8000/api/modules/"
```

## 📁 项目结构 - 多入口统一业务处理架构

```
backend/
├── src/auto_test/
│   ├── main.py                          # FastAPI应用入口
│   ├── api/                             # 接入层 (Access Layer)
│   │   ├── __init__.py
│   │   ├── controllers/                 # HTTP控制器 (极简控制器)
│   │   │   ├── __init__.py
│   │   │   ├── system_controller.py     # 系统管理控制器
│   │   │   └── module_controller.py     # 模块管理控制器
│   │   ├── facades/                     # RPC接口 (服务间调用)
│   │   │   ├── __init__.py
│   │   │   └── system_facade.py         # 系统服务接口
│   │   └── listeners/                   # 消息监听器 (异步处理)
│   │       ├── __init__.py
│   │       └── system_listener.py       # 系统事件监听器
│   ├── services/                        # 防腐层 - 业务逻辑
│   │   ├── __init__.py
│   │   ├── system_service.py            # 系统业务服务
│   │   └── module_service.py            # 模块业务服务
│   ├── converters/                      # 防腐层 - 数据转换
│   │   ├── __init__.py
│   │   ├── system_converter.py          # 系统数据转换
│   │   └── module_converter.py          # 模块数据转换
│   ├── rules/                           # 防腐层 - 业务规则
│   │   ├── __init__.py
│   │   ├── system_rules.py              # 系统业务规则
│   │   └── module_rules.py              # 模块业务规则
│   ├── wrappers/                        # 防腐层 - 权限包装
│   │   ├── __init__.py
│   │   ├── system_wrapper.py            # 系统权限包装
│   │   └── module_wrapper.py            # 模块权限包装
│   ├── infrastructure/                  # 基础设施层
│   │   ├── __init__.py
│   │   ├── adapters/                    # 外部服务适配器
│   │   │   ├── __init__.py
│   │   │   └── notification_adapter.py  # 通知服务适配器
│   │   ├── producers/                   # 消息生产者
│   │   │   ├── __init__.py
│   │   │   └── system_producer.py       # 系统消息生产者
│   │   ├── data_services/               # 数据聚合服务
│   │   │   ├── __init__.py
│   │   │   ├── system_data_service.py   # 系统数据服务
│   │   │   └── module_data_service.py   # 模块数据服务
│   │   └── repositories/                # 数据访问层
│   │       ├── __init__.py
│   │       ├── system_repository.py     # 系统数据访问
│   │       └── module_repository.py     # 模块数据访问
│   ├── models/                          # 数据模型
│   │   ├── __init__.py
│   │   ├── entities/                    # 实体模型
│   │   │   ├── __init__.py
│   │   │   ├── system.py                # 系统实体
│   │   │   └── module.py                # 模块实体
│   │   ├── requests/                    # 请求模型
│   │   │   ├── __init__.py
│   │   │   ├── system_request.py        # 系统请求
│   │   │   └── module_request.py        # 模块请求
│   │   ├── responses/                   # 响应模型
│   │   │   ├── __init__.py
│   │   │   ├── system_response.py       # 系统响应
│   │   │   └── module_response.py       # 模块响应
│   │   ├── data/                        # 业务数据模型
│   │   │   ├── __init__.py
│   │   │   ├── system_data.py           # 系统业务数据
│   │   │   └── module_data.py           # 模块业务数据
│   │   └── vos/                         # 值对象
│   │       ├── __init__.py
│   │       ├── system_vo.py             # 系统值对象
│   │       └── module_vo.py             # 模块值对象
│   ├── exceptions/                      # 异常定义
│   │   ├── __init__.py
│   │   └── business_exception.py        # 业务异常
│   └── utils/                           # 工具类
│       ├── __init__.py
│       ├── response.py                  # 响应工具
│       └── database.py                  # 数据库工具
├── requirements.txt                     # 依赖包列表
└── README.md                           # 项目说明
```

## 🛠️ 开发流程 - 极简控制器 + 防腐层架构

### 1. 添加新功能 (遵循极简控制器编码规范)

#### 步骤1: 定义数据模型
```bash
# 在 models/ 中定义各层数据模型
models/entities/new_feature.py      # 实体模型
models/requests/new_feature_request.py   # 请求模型
models/responses/new_feature_response.py # 响应模型
models/data/new_feature_data.py     # 业务数据模型
models/vos/new_feature_vo.py        # 值对象
```

#### 步骤2: 实现基础设施层
```bash
# 数据访问和外部服务
infrastructure/repositories/new_feature_repository.py  # 数据访问
infrastructure/data_services/new_feature_data_service.py  # 数据聚合
infrastructure/adapters/new_feature_adapter.py  # 外部服务适配器
```

#### 步骤3: 实现防腐层
```bash
# 防腐层组件 (核心业务逻辑)
services/new_feature_service.py     # 业务逻辑防腐层
converters/new_feature_converter.py # 数据转换防腐层
rules/new_feature_rules.py          # 业务规则中心
wrappers/new_feature_wrapper.py     # 权限包装工具
```

#### 步骤4: 实现接入层 (极简控制器)
```bash
# 多入口接入层 (每个方法不超过5行)
api/controllers/new_feature_controller.py  # HTTP控制器
api/facades/new_feature_facade.py          # RPC接口
api/listeners/new_feature_listener.py      # 消息监听器
```

#### 步骤5: 注册路由
```python
# 在 main.py 中注册路由
from api.controllers.new_feature_controller import router as new_feature_router
app.include_router(new_feature_router, prefix="/api/new-features", tags=["新功能"])
```

### 2. 极简控制器编码示例

#### Controller 实现 (不超过5行)
```python
@router.get("/{feature_id}", response_model=WebResponse[NewFeatureResponse])
async def get_feature(
    feature_id: int,
    service: NewFeatureService = Depends(),
    converter: NewFeatureConverter = Depends()
):
    data = await service.collect_feature_data(feature_id)
    response = converter.to_response(data)
    return WebResponse.success(response)
```

#### Service 防腐层实现
```python
class NewFeatureService:
    async def collect_feature_data(self, feature_id: int):
        """统一数据收集方法 - 防腐层数据组装"""
        # 1. 基础设施数据收集
        feature_vo = await self.data_service.find_by_id(feature_id)
        
        # 2. 业务规则验证
        self.rules.validate_access(feature_vo)
        
        # 3. 权限包装
        feature_wrapped = self.wrapper.wrap_with_permissions(feature_vo)
        
        # 4. 数据转换并返回
        return self.converter.to_data(feature_wrapped)
```

### 3. 测试流程
1. 启动开发服务器
2. 使用 cURL 或 Postman 测试API
3. 检查响应格式和数据正确性
4. 验证错误处理逻辑
5. 测试多入口访问 (HTTP、RPC、MQ)

### 4. 编码规范 (强制约束)

#### 🚫 禁止事项
- **控制器方法超过5行代码**
- **控制器包含业务逻辑**
- **直接调用基础设施组件**
- **跨层调用 (如Controller直接调用Repository)**

#### ✅ 必须遵循
- **极简控制器原则**: 只负责接收请求、调用服务、返回响应
- **防腐层设计**: Service、Converter、Rule、Wrapper分层防腐
- **多入口统一架构**: 支持HTTP、RPC、MQ多种接入方式
- **统一数据转换**: 使用Converter进行所有数据格式转换

#### 📋 代码检查清单
- [ ] Controller方法是否不超过5行？
- [ ] 是否使用了统一的多入口架构模式？
- [ ] 是否通过Converter进行数据转换？
- [ ] 是否遵循防腐层设计原则？
- [ ] 是否使用了业务规则中心(Rule)？

## ❓ 常见问题

### Q: 如何遵循极简控制器编码规范？
A: 确保控制器方法不超过5行，只负责接收请求、调用Service、返回响应。业务逻辑必须放在Service防腐层中。

### Q: 什么是防腐层架构？
A: 防腐层是隔离外部复杂性的设计模式，包括Service(业务逻辑防腐层)、Converter(数据转换防腐层)、Rule(业务规则中心)、Wrapper(权限包装工具)。

### Q: 如何实现多入口统一业务处理？
A: 通过Controller(HTTP)、Facade(RPC)、Listener(MQ)三种接入方式，统一调用Service防腐层处理业务逻辑。

### Q: 如何添加新的API端点？
A: 按照5步流程：定义数据模型 → 实现基础设施层 → 实现防腐层 → 实现接入层 → 注册路由。

### Q: 控制器方法超过5行怎么办？
A: 将业务逻辑移到Service中，数据转换移到Converter中，权限控制移到Wrapper中，确保控制器只做接入处理。

### Q: 如何处理跨域请求？
A: 在 `main.py` 中配置CORS中间件。

### Q: 如何部署到生产环境？
A: 使用 Gunicorn 或 uWSGI 作为WSGI服务器，配置反向代理。

### Q: 如何进行数据转换？
A: 统一使用Converter进行数据转换，包括请求数据转实体、业务数据转响应数据、VO转业务数据等。

## 📚 下一步

### 📖 深入学习
- 查看 [极简控制器编码标准](standards/controller_standards.md) 了解详细编码规范
- 查看 [V4极简架构设计](architecture/v4_simplified.md) 了解多入口统一业务处理架构
- 查看 [编码规范](standards/coding.md) 了解防腐层设计原则

### 🔧 实践指南
- 查看 [API文档](api/api_documentation.md) 了解详细的接口说明
- 查看 [架构示例](examples/architecture_examples.md) 了解代码结构和最佳实践
- 根据需求扩展功能模块

### 🎯 核心原则
- **极简控制器**: 每个方法不超过5行代码
- **防腐层设计**: Service、Converter、Rule、Wrapper分层防腐
- **多入口统一**: HTTP、RPC、MQ统一业务处理
- **AI友好**: 标准化模板，便于AI代码生成