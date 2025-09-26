# V4 极简架构设计 - 多入口统一业务处理

> **架构版本**: v4.0.0  
> **设计理念**: 极简控制器 + 防腐层架构 + 多入口统一业务处理  
> **适用场景**: 中小型项目，快速开发，AI友好架构

## 🎯 架构核心理念

### 极简控制器原则
- **控制器方法不超过5行代码**
- **只负责接收请求、调用服务、返回响应**
- **零业务逻辑，纯粹的接入层**

### 防腐层设计
- **Service作为业务逻辑防腐层**，隔离基础设施复杂性
- **Converter作为数据转换防腐层**，统一数据格式转换
- **Adapter作为外部服务防腐层**，封装第三方服务调用

## 🏗️ 多入口统一业务处理架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      接入层 (Access Layer)                       │
├─────────────────────┬─────────────────────┬─────────────────────┤
│     Controller      │       Facade        │    MQ Listener      │
│   (HTTP请求处理)    │   (服务间调用)      │   (消息队列监听)     │
│                     │                     │                     │
│  ┌───────────────┐  │  ┌───────────────┐  │  ┌───────────────┐  │
│  │   Request     │  │  │   RPC Call    │  │  │   Message     │  │
│  │   Response    │  │  │   DTO         │  │  │   Event       │  │
│  └───────────────┘  │  └───────────────┘  │  └───────────────┘  │
└─────────────────────┴─────────────────────┴─────────────────────┘
                │               │               │
                ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   防腐层 (Anti-Corruption Layer)                  │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│    Service      │   Converter     │    Wrapper      │   Rule    │
│ (业务逻辑防腐层) │ (数据转换防腐层) │ (权限包装工具类) │(业务规则中心)│
│ • 数据收集组装   │ • 业务数据转换   │ • 权限控制包装   │ • 业务规则  │
│ • 业务流程协调   │ • 格式标准化     │ • 敏感信息过滤   │ • 条件判断  │
│ • 基础设施封装   │ • 业务规则应用   │ • 缓存友好处理   │ • 权限验证  │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                │                               │
                ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    基础设施层 (Infrastructure Layer)              │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Service Adapter │   MQ Producer   │        Data Service         │
│ (外部服务防腐层) │   (消息发送)    │       (数据聚合层)          │
│                 │                 │                             │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌─────────────┬───────────┐ │
│ │Service Client│ │ │ RabbitMQ    │ │ │ Repository  │   Cache   │ │
│ │ HTTP Client │ │ │ RocketMQ    │ │ │ MyBatis     │   Redis   │ │
│ │ RPC Client  │ │ │ Kafka       │ │ │ Redis       │    ES     │ │
│ │ WebService  │ │ │             │ │ │ ES          │           │ │
│ └─────────────┘ │ └─────────────┘ │ └─────────────┴───────────┘ │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## 📁 项目结构

```
src/auto_test/
├── main.py                          # FastAPI应用入口
├── api/                             # 接入层
│   ├── __init__.py
│   ├── controllers/                 # HTTP控制器
│   │   ├── __init__.py
│   │   ├── system_controller.py     # 系统管理控制器
│   │   └── module_controller.py     # 模块管理控制器
│   ├── facades/                     # RPC接口
│   │   ├── __init__.py
│   │   └── system_facade.py         # 系统服务接口
│   └── listeners/                   # 消息监听器
│       ├── __init__.py
│       └── system_listener.py       # 系统事件监听器
├── services/                        # 防腐层 - 业务逻辑
│   ├── __init__.py
│   ├── system_service.py            # 系统业务服务
│   └── module_service.py            # 模块业务服务
├── converters/                      # 防腐层 - 数据转换
│   ├── __init__.py
│   ├── system_converter.py          # 系统数据转换
│   └── module_converter.py          # 模块数据转换
├── rules/                           # 防腐层 - 业务规则
│   ├── __init__.py
│   ├── system_rules.py              # 系统业务规则
│   └── module_rules.py              # 模块业务规则
├── wrappers/                        # 防腐层 - 权限包装
│   ├── __init__.py
│   ├── system_wrapper.py            # 系统权限包装
│   └── module_wrapper.py            # 模块权限包装
├── infrastructure/                  # 基础设施层
│   ├── __init__.py
│   ├── adapters/                    # 外部服务适配器
│   │   ├── __init__.py
│   │   └── notification_adapter.py  # 通知服务适配器
│   ├── producers/                   # 消息生产者
│   │   ├── __init__.py
│   │   └── system_producer.py       # 系统消息生产者
│   ├── data_services/               # 数据聚合服务
│   │   ├── __init__.py
│   │   ├── system_data_service.py   # 系统数据服务
│   │   └── module_data_service.py   # 模块数据服务
│   └── repositories/                # 数据访问层
│       ├── __init__.py
│       ├── system_repository.py     # 系统数据访问
│       └── module_repository.py     # 模块数据访问
├── models/                          # 数据模型
│   ├── __init__.py
│   ├── entities/                    # 实体模型
│   │   ├── __init__.py
│   │   ├── system.py                # 系统实体
│   │   └── module.py                # 模块实体
│   ├── requests/                    # 请求模型
│   │   ├── __init__.py
│   │   ├── system_request.py        # 系统请求
│   │   └── module_request.py        # 模块请求
│   ├── responses/                   # 响应模型
│   │   ├── __init__.py
│   │   ├── system_response.py       # 系统响应
│   │   └── module_response.py       # 模块响应
│   ├── data/                        # 业务数据模型
│   │   ├── __init__.py
│   │   ├── system_data.py           # 系统业务数据
│   │   └── module_data.py           # 模块业务数据
│   └── vos/                         # 值对象
│       ├── __init__.py
│       ├── system_vo.py             # 系统值对象
│       └── module_vo.py             # 模块值对象
├── exceptions/                      # 异常定义
│   ├── __init__.py
│   └── business_exception.py        # 业务异常
└── utils/                           # 工具类
    ├── __init__.py
    ├── response.py                  # 响应工具
    └── database.py                  # 数据库工具
```

## 🎯 分层职责定义

| 层级 | 职责 | 禁止事项 |
|------|------|----------|
| **Controller** | 接收HTTP请求，调用Service，返回响应 | 业务逻辑、数据处理、复杂验证 |
| **Facade** | 其他服务调用本服务的接口，协议转换 | 业务逻辑、状态管理 |
| **MQ Listener** | 消息队列监听器，处理异步消息，调用Service | 业务逻辑、数据转换 |
| **Service** | **业务逻辑防腐层**，数据收集与组装，业务流程协调，基础设施调用封装 | 直接调用基础设施、协议相关处理 |
| **Converter** | **数据转换防腐层**，业务数据转换，格式标准化，调用Rule进行验证 | 数据收集、外部调用 |
| **Rule** | **业务规则中心**，为Service和Converter提供业务规则验证和计算逻辑 | 数据收集、外部调用、数据转换 |
| **Wrapper** | **权限包装工具类**，权限控制、敏感信息过滤、缓存友好处理 | 数据收集、外部调用、业务流程 |
| **Service Adapter** | **外部服务防腐层**，协议适配，数据转换，异常处理，重试机制 | 业务逻辑、业务规则 |
| **MQ Producer** | **基础设施层**，负责发送消息到消息队列，消息格式化 | 业务逻辑、业务规则 |
| **Data Service** | **基础设施层**，数据聚合层，统一管理Repository、Redis、ES等多种数据源 | 业务逻辑、业务规则 |
| **Repository** | **基础设施层**，数据库访问，SQL执行，事务管理 | 业务逻辑、业务规则 |

## 📝 代码示例

### Controller 极简实现

```python
from fastapi import APIRouter, Depends
from ..services.system_service import SystemService
from ..converters.system_converter import SystemConverter
from ..models.requests.system_request import SystemRequest
from ..models.responses.system_response import SystemResponse
from ..utils.response import WebResponse

router = APIRouter(prefix="/api/systems", tags=["systems"])

@router.get("/{system_id}", response_model=WebResponse[SystemResponse])
async def get_system(
    system_id: int,
    service: SystemService = Depends(),
    converter: SystemConverter = Depends()
):
    data = await service.collect_system_data(system_id)
    response = converter.to_response(data)
    return WebResponse.success(response)

@router.post("/", response_model=WebResponse[SystemResponse])
async def create_system(
    request: SystemRequest,
    service: SystemService = Depends(),
    converter: SystemConverter = Depends()
):
    data = await service.create_system(request)
    response = converter.to_response(data)
    return WebResponse.success(response)
```

### Service 防腐层实现

```python
from ..infrastructure.data_services.system_data_service import SystemDataService
from ..infrastructure.adapters.notification_adapter import NotificationAdapter
from ..infrastructure.producers.system_producer import SystemProducer
from ..rules.system_rules import SystemRules
from ..wrappers.system_wrapper import SystemWrapper
from ..converters.system_converter import SystemConverter

class SystemService:
    def __init__(self):
        self.data_service = SystemDataService()
        self.notification_adapter = NotificationAdapter()
        self.producer = SystemProducer()
        self.rules = SystemRules()
        self.wrapper = SystemWrapper()
        self.converter = SystemConverter()
    
    async def collect_system_data(self, system_id: int):
        """统一数据收集方法 - 防腐层数据组装"""
        # 1. 基础设施数据收集
        system_vo = await self.data_service.find_by_id(system_id)
        if not system_vo:
            raise BusinessException("系统不存在")
        
        # 2. 业务规则验证
        self.rules.validate_access(system_vo)
        
        # 3. 权限包装
        system_wrapped = self.wrapper.wrap_with_permissions(system_vo)
        
        # 4. 外部服务数据收集
        notification_info = await self.notification_adapter.get_system_notifications(system_id)
        
        # 5. 访问事件发送
        await self.producer.send_access_event(system_id, "view")
        
        # 6. 数据转换并返回
        return self.converter.to_data(system_wrapped, notification_info)
    
    async def create_system(self, request):
        """创建系统"""
        # 1. 业务规则验证
        self.rules.validate_create(request)
        
        # 2. 数据转换
        system_entity = self.converter.request_to_entity(request)
        
        # 3. 基础设施保存
        system_id = await self.data_service.save(system_entity)
        
        # 4. 创建事件发送
        await self.producer.send_created_event(system_id)
        
        # 5. 返回完整数据
        return await self.collect_system_data(system_id)
```

### Converter 数据转换实现

```python
from ..rules.system_rules import SystemRules

class SystemConverter:
    def __init__(self):
        self.rules = SystemRules()
    
    def to_response(self, data):
        """业务数据转换为响应数据"""
        return SystemResponse(
            id=data.id,
            name=data.name,
            description=data.description,
            status=data.status,
            create_time=data.create_time
        )
    
    def request_to_entity(self, request):
        """请求数据转换为实体"""
        # 调用Rule进行验证
        self.rules.validate_request_data(request)
        
        return SystemEntity(
            name=request.name,
            description=request.description,
            tags=request.tags
        )
    
    def to_data(self, wrapped_vo, external_info=None):
        """包装VO转换为业务数据"""
        data = SystemData(
            id=wrapped_vo.id,
            name=wrapped_vo.name,
            description=wrapped_vo.description,
            status=wrapped_vo.status,
            create_time=wrapped_vo.create_time
        )
        
        # 融合外部信息
        if external_info:
            data.notification_count = external_info.get('count', 0)
        
        return data
```

## 🔧 架构优势

### 1. 极简性
- **控制器超薄**：每个方法不超过5行，易于理解和维护
- **职责单一**：每层只负责自己的核心职责
- **代码简洁**：减少样板代码，提高开发效率

### 2. 可扩展性
- **多入口支持**：HTTP、RPC、MQ等多种接入方式
- **防腐层设计**：隔离外部依赖，易于替换和扩展
- **组件化**：各组件独立，便于单独测试和替换

### 3. 可维护性
- **分层清晰**：每层职责明确，便于定位问题
- **统一规范**：标准化的代码结构和命名规范
- **易于测试**：每层都可以独立进行单元测试

### 4. AI友好
- **模板化**：标准化的代码模板，便于AI生成
- **规则明确**：清晰的约束条件和设计规则
- **可预测**：统一的架构模式，便于AI理解和应用

## 📚 相关文档

- [控制器编码标准](../standards/controller_standards.md)
- [编码规范](../standards/coding.md)
- [API文档](../api/api_documentation.md)
- [快速开始指南](../quick_start.md)