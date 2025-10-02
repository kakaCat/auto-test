# 极简控制器编码标准

> **重要说明**：本规范专门为AI代码生成设计，支持**Java、Python、Go**三种主流编程语言，包含明确的执行规则、约束条件和标准代码模板。

## 🎯 核心设计原则

### ⚡ 强制约束条件
1. **控制器方法不得超过5行代码**
2. **控制器不得包含任何业务逻辑**
3. **必须使用统一的多入口架构模式**
4. **必须使用Converter进行数据转换**
5. **必须遵循防腐层设计原则**

### 📋 代码生成检查清单
- [ ] 控制器是否只有接收参数、调用服务、返回结果三个步骤
- [ ] 是否使用了统一的Service层进行数据收集
- [ ] 是否通过Converter进行数据转换
- [ ] 是否遵循了命名规范
- [ ] 是否包含了必要的异常处理

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

## 🎯 分层职责定义

| 层级 | 职责 | 禁止事项 |
|------|------|----------|
| **Controller** | 接收HTTP请求，调用Service，返回响应 | 业务逻辑、数据处理、复杂验证 |
| **Facade** | 其他服务调用本服务的接口，协议转换 | 业务逻辑、状态管理 |
| **MQ Listener** | 消息队列监听器，处理异步消息，调用Service | 业务逻辑、数据转换 |
| **Service** | **业务逻辑防腐层**，数据收集与组装，业务流程协调，基础设施调用封装，数据转换适配 | 直接调用基础设施、协议相关处理 |
| **Converter** | **防腐层**，业务数据转换，格式标准化，调用Rule进行验证 | 数据收集、外部调用 |
| **Rule** | **中心**，为Service和Converter提供业务规则验证和计算逻辑 | 数据收集、外部调用、数据转换 |
| **Service Adapter** | **外部服务防腐层**，协议适配，数据转换，异常处理，重试机制，监控埋点 | 业务逻辑、业务规则 |
| **MQ Producer** | **基础设施层**，负责发送消息到消息队列，消息格式化 | 业务逻辑、业务规则 |
| **Data Service** | **基础设施层**，数据聚合层，统一管理Repository、Redis、ES等多种数据源 | 业务逻辑、业务规则 |
| **Repository** | **基础设施层**，数据库访问，SQL执行，事务管理 | 业务逻辑、业务规则 |
| **Wrapper** | **防腐层**，权限包装静态工具类，权限控制、敏感信息过滤、缓存友好处理 | 数据收集、外部调用、业务流程 |

## 📦 响应数据与分页规范（强制）

为统一前后端契约、降低页面适配成本，所有“列表型”接口的响应必须遵循以下命名与结构规范：

- 列表字段：使用 `list`（不使用 `items`/`apis`/`data` 等混合命名）
- 统计字段：使用 `total` 表示总条数
- 分页字段：使用 `page` 表示当前页码，使用 `size` 表示每页数量
- 推荐包装：统一使用通用响应包装 `WebResponse[T]`/`ApiResponseGeneric[T]`

示例（FastAPI）：

```python
from pydantic import BaseModel
from typing import List

class User(BaseModel):
    id: int
    name: str

class ListResponse(BaseModel):
    list: List[User] = []
    total: int = 0
    page: int = 1
    size: int = 20

@router.get("/users", response_model=WebResponse[ListResponse])
async def list_users(page: int = 1, size: int = 20):
    users = await service.list_users(page, size)
    resp = ListResponse(list=[User(**u) for u in users], total=len(users), page=page, size=size)
    return WebResponse.success(resp)
```

### 迁移与兼容建议
- 旧接口若已返回 `items`/`apis` 等字段，应在控制器或 Converter 层添加兼容映射，额外填充 `list` 字段，逐步废弃旧命名。
- 文档与类型定义必须以 `list/total/page/size` 为准，变更需在 `docs/backend/changelogs/` 中记录并关联前端文档映射。
- 前端建议在统一的 `apiHandler` 适配层只消费 `list/total/page/size`，避免页面出现多格式判断。

> 说明：该规范为强制项，任何新增列表接口必须按此命名；存量接口需在迭代中完成迁移，以减少技术债。

## 📝 Python FastAPI 控制器模板

### 基础控制器模板

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..services.{domain}_service import {Domain}Service
from ..converters.{domain}_converter import {Domain}Converter
from ..models.requests import {Domain}Request
from ..models.responses import {Domain}Response, WebResponse

router = APIRouter(prefix="/api/{domain}", tags=["{domain}"])

# 依赖注入
def get_{domain}_service() -> {Domain}Service:
    return {Domain}Service()

def get_{domain}_converter() -> {Domain}Converter:
    return {Domain}Converter()

@router.get("/{id}", response_model=WebResponse[{Domain}Response])
async def get_{domain}(
    id: int,
    service: {Domain}Service = Depends(get_{domain}_service),
    converter: {Domain}Converter = Depends(get_{domain}_converter)
):
    data = await service.collect_{domain}_data(id)
    response = converter.to_response(data)
    return WebResponse.success(response)

@router.post("/", response_model=WebResponse[{Domain}Response])
async def create_{domain}(
    request: {Domain}Request,
    service: {Domain}Service = Depends(get_{domain}_service),
    converter: {Domain}Converter = Depends(get_{domain}_converter)
):
    data = await service.create_{domain}(request)
    response = converter.to_response(data)
    return WebResponse.success(response)

@router.put("/{id}", response_model=WebResponse[{Domain}Response])
async def update_{domain}(
    id: int,
    request: {Domain}Request,
    service: {Domain}Service = Depends(get_{domain}_service),
    converter: {Domain}Converter = Depends(get_{domain}_converter)
):
    data = await service.update_{domain}(id, request)
    response = converter.to_response(data)
    return WebResponse.success(response)

@router.delete("/{id}", response_model=WebResponse[None])
async def delete_{domain}(
    id: int,
    service: {Domain}Service = Depends(get_{domain}_service)
):
    await service.delete_{domain}(id)
    return WebResponse.success(None)

@router.get("/", response_model=WebResponse[List[{Domain}Response]])
async def list_{domain}s(
    page: int = 1,
    size: int = 10,
    service: {Domain}Service = Depends(get_{domain}_service),
    converter: {Domain}Converter = Depends(get_{domain}_converter)
):
    data_list = await service.list_{domain}s(page, size)
    response_list = [converter.to_response(data) for data in data_list]
    return WebResponse.success(response_list)
```

### 实际应用示例（系统管理）

```python
from fastapi import APIRouter, Depends
from typing import List
from ..services.system_service import SystemService
from ..converters.system_converter import SystemConverter
from ..models.requests import SystemRequest
from ..models.responses import SystemResponse, WebResponse

router = APIRouter(prefix="/api/systems", tags=["systems"])

def get_system_service() -> SystemService:
    return SystemService()

def get_system_converter() -> SystemConverter:
    return SystemConverter()

@router.get("/{system_id}", response_model=WebResponse[SystemResponse])
async def get_system(
    system_id: int,
    service: SystemService = Depends(get_system_service),
    converter: SystemConverter = Depends(get_system_converter)
):
    data = await service.collect_system_data(system_id)
    response = converter.to_response(data)
    return WebResponse.success(response)

@router.post("/", response_model=WebResponse[SystemResponse])
async def create_system(
    request: SystemRequest,
    service: SystemService = Depends(get_system_service),
    converter: SystemConverter = Depends(get_system_converter)
):
    data = await service.create_system(request)
    response = converter.to_response(data)
    return WebResponse.success(response)
```

## 📝 Service 防腐层模板

### Python Service 模板

```python
from typing import List, Optional
from ..data_services.{domain}_data_service import {Domain}DataService
from ..adapters.{external}_adapter import {External}Adapter
from ..producers.{domain}_producer import {Domain}Producer
from ..rules.{domain}_rules import {Domain}Rules
from ..wrappers.{domain}_wrapper import {Domain}Wrapper
from ..converters.{domain}_converter import {Domain}Converter
from ..models.entities import {Domain}Entity
from ..models.requests import {Domain}Request
from ..models.data import {Domain}Data
from ..exceptions import BusinessException

class {Domain}Service:
    def __init__(self):
        self.data_service = {Domain}DataService()
        self.external_adapter = {External}Adapter()
        self.producer = {Domain}Producer()
        self.rules = {Domain}Rules()
        self.wrapper = {Domain}Wrapper()
        self.converter = {Domain}Converter()
    
    async def collect_{domain}_data(self, id: int) -> {Domain}Data:
        """统一数据收集方法 - 防腐层数据组装"""
        # 1. 基础设施数据收集与转换（通过DataService聚合多数据源）
        {domain}_vo = await self.data_service.find_by_id(id)
        if not {domain}_vo:
            raise BusinessException(f"{Domain}不存在")
        
        # 2. 验证（助手组件调用）
        self.rules.validate_user({domain}_vo)
        
        # 3. 包装（权限、缓存等 - 助手组件调用）
        {domain}_wrapped = self.wrapper.wrap_with_permissions({domain}_vo)
        
        # 4. 外部服务数据收集与转换（通过防腐层适配）
        external_info = await self.external_adapter.get_external_info(id)
        
        # 5. 访问事件发送（异步处理）
        await self._send_access_event(id, "view")
        
        # 6. 转换并返回（助手组件调用）
        return self.converter.to_data({domain}_wrapped, external_info)
    
    async def create_{domain}(self, request: {Domain}Request) -> {Domain}Data:
        """创建{Domain}"""
        # 1. 业务规则验证（助手组件调用）
        self.rules.validate_create(request)
        
        # 2. 请求数据转换为实体（助手组件调用）
        {domain}_entity = self.converter.request_to_entity(request)
        {domain}_entity.status = "{Domain}Status.ACTIVE"
        {domain}_entity.create_time = datetime.now()
        
        # 3. 基础设施保存操作（通过DataService）
        id = await self.data_service.save({domain}_entity)
        
        # 4. 创建事件发送（异步处理）
        await self._send_created_event(id)
        
        # 5. 返回完整业务数据
        return await self.collect_{domain}_data(id)
    
    async def update_{domain}(self, id: int, request: {Domain}Request) -> {Domain}Data:
        """更新{Domain}"""
        # 1. 基础设施数据获取（通过DataService）
        {domain}_vo = await self.data_service.find_by_id(id)
        if not {domain}_vo:
            raise BusinessException(f"{Domain}不存在")
        
        # 2. 业务规则验证（助手组件调用）
        self.rules.validate_update(id, request, {domain}_vo)
        
        # 3. 请求数据转换并更新实体（助手组件调用）
        {domain}_entity = self.converter.request_to_entity(request)
        {domain}_entity.id = id
        {domain}_entity.update_time = datetime.now()
        
        # 4. 基础设施保存操作（通过DataService）
        await self.data_service.update({domain}_entity)
        
        # 5. 更新事件发送（异步处理）
        await self._send_updated_event(id)
        
        # 6. 返回完整业务数据
        return await self.collect_{domain}_data(id)
    
    async def delete_{domain}(self, id: int) -> None:
        """删除{Domain}"""
        # 1. 基础设施数据获取（通过DataService）
        {domain}_vo = await self.data_service.find_by_id(id)
        if not {domain}_vo:
            raise BusinessException(f"{Domain}不存在")
        
        # 2. 业务规则验证（助手组件调用）
        self.rules.validate_delete(id, {domain}_vo)
        
        # 3. 基础设施删除操作（通过DataService）
        await self.data_service.delete(id)
        
        # 4. 删除事件发送（异步处理）
        await self._send_deleted_event(id)
    
    async def list_{domain}s(self, page: int, size: int) -> List[{Domain}Data]:
        """列表查询{Domain}"""
        # 1. 基础设施数据获取（通过DataService）
        {domain}_list = await self.data_service.find_page(page, size)
        
        # 2. 批量转换并返回
        return [self.converter.vo_to_data(vo) for vo in {domain}_list]
    
    async def _send_access_event(self, id: int, action: str):
        """发送访问事件"""
        await self.producer.send_access_event(id, action)
    
    async def _send_created_event(self, id: int):
        """发送创建事件"""
        await self.producer.send_created_event(id)
    
    async def _send_updated_event(self, id: int):
        """发送更新事件"""
        await self.producer.send_updated_event(id)
    
    async def _send_deleted_event(self, id: int):
        """发送删除事件"""
        await self.producer.send_deleted_event(id)
```

## 📝 Converter 数据转换模板

### Python Converter 模板

```python
from typing import Optional
from ..models.entities import {Domain}Entity
from ..models.requests import {Domain}Request
from ..models.responses import {Domain}Response
from ..models.data import {Domain}Data
from ..models.vos import {Domain}VO
from ..rules.{domain}_rules import {Domain}Rules

class {Domain}Converter:
    """静态工具类设计 - 数据转换防腐层"""
    
    def __init__(self):
        self.rules = {Domain}Rules()
    
    def to_response(self, data: {Domain}Data) -> {Domain}Response:
        """业务数据转换为响应数据"""
        if not data:
            return None
        
        return {Domain}Response(
            id=data.id,
            name=data.name,
            description=data.description,
            status=data.status,
            create_time=data.create_time,
            update_time=data.update_time
        )
    
    def request_to_entity(self, request: {Domain}Request) -> {Domain}Entity:
        """请求数据转换为实体"""
        if not request:
            return None
        
        # 调用Rule进行业务规则验证
        self.rules.validate_request_data(request)
        
        return {Domain}Entity(
            name=request.name,
            description=request.description,
            tags=request.tags
        )
    
    def vo_to_data(self, vo: {Domain}VO) -> {Domain}Data:
        """VO转换为业务数据"""
        if not vo:
            return None
        
        return {Domain}Data(
            id=vo.id,
            name=vo.name,
            description=vo.description,
            status=vo.status,
            create_time=vo.create_time,
            update_time=vo.update_time
        )
    
    def to_data(self, wrapped_vo: {Domain}VO, external_info: Optional[dict] = None) -> {Domain}Data:
        """包装VO和外部信息转换为业务数据"""
        if not wrapped_vo:
            return None
        
        data = self.vo_to_data(wrapped_vo)
        
        # 融合外部服务信息
        if external_info:
            data.external_status = external_info.get('status')
            data.external_score = external_info.get('score')
        
        return data
```

## 🔧 最佳实践

### 1. 控制器设计原则
- **薄控制器**：只负责接收请求、调用服务、返回响应
- **无业务逻辑**：所有业务逻辑都在Service层处理
- **统一异常处理**：使用全局异常处理器
- **依赖注入**：使用FastAPI的依赖注入系统

### 2. Service防腐层设计
- **数据收集组装**：从多个基础设施获取数据并进行业务组装
- **业务流程协调**：协调多个基础设施组件完成复杂业务流程
- **基础设施封装**：封装对外部服务、数据库、消息队列的调用
- **异常统一处理**：统一处理基础设施层抛出的异常

### 3. 命名规范
- **Controller**: `{Domain}Controller`
- **Service**: `{Domain}Service`
- **Converter**: `{Domain}Converter`
- **Rules**: `{Domain}Rules`
- **Wrapper**: `{Domain}Wrapper`

### 4. 错误处理
- 使用业务异常类 `BusinessException`
- 全局异常处理器统一处理
- 返回标准化的错误响应格式

### 5. 性能优化
- 使用异步编程 `async/await`
- 合理使用缓存
- 批量操作优化
- 数据库连接池管理

## 📚 相关文档

- [架构设计文档](../architecture/v4_simplified.md)
- [API文档](../api/api_documentation.md)
- [快速开始指南](../quick_start.md)
- [编码规范](./coding.md)