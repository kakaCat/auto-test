# 后端编码规范

## 📖 概述

本文档定义了AI自动化测试平台后端项目的编码规范和最佳实践，采用**极简控制器 + 防腐层架构**设计，支持多语言开发。

### 🎯 核心设计原则

1. **极简控制器**: 控制器只负责接收请求、调用服务、返回响应，不超过5行代码
2. **防腐层架构**: 使用Service作为业务逻辑防腐层，隔离基础设施复杂性
3. **多入口统一**: 支持HTTP、RPC、MQ等多种接入方式的统一业务处理
4. **分层职责**: 清晰的分层结构，每层职责单一
5. **依赖倒置**: 高层模块不依赖低层模块，都依赖抽象

### ⚡ 强制约束条件

1. **控制器方法不得超过5行代码**
2. **控制器不得包含任何业务逻辑**
3. **必须使用统一的多入口架构模式**
4. **必须使用Converter进行数据转换**
5. **必须遵循防腐层设计原则**

## 🏗️ 架构分层

### 1. 表现层 (Presentation Layer)
**位置**: `src/auto_test/api/`
**职责**: 处理HTTP请求，数据转换，用户界面交互

```python
# 示例: API控制器
from fastapi import APIRouter, Depends
from ..application.services.api_service import ApiService
from ..application.dto.api_dto import CreateApiRequest, ApiResponse

router = APIRouter(prefix="/api/v1/apis")

@router.post("/", response_model=ApiResponse)
async def create_api(
    request: CreateApiRequest,
    service: ApiService = Depends()
):
    """创建API接口"""
    return await service.create_api(request)
```

### 2. 应用层 (Application Layer)
**位置**: `src/auto_test/application/`
**职责**: 编排领域对象，处理用例，事务管理

```python
# 示例: 应用服务
from ..domain.services.api_domain_service import ApiDomainService
from ..domain.repositories.api_repository import ApiRepository
from ..infrastructure.persistence.unit_of_work import UnitOfWork

class ApiService:
    def __init__(
        self,
        api_repository: ApiRepository,
        domain_service: ApiDomainService,
        uow: UnitOfWork
    ):
        self._api_repository = api_repository
        self._domain_service = domain_service
        self._uow = uow
    
    async def create_api(self, request: CreateApiRequest) -> ApiResponse:
        async with self._uow:
            # 领域逻辑验证
            api = self._domain_service.create_api(
                name=request.name,
                path=request.path,
                method=request.method
            )
            
            # 持久化
            await self._api_repository.save(api)
            await self._uow.commit()
            
            return ApiResponse.from_domain(api)
```

### 3. 领域层 (Domain Layer)
**位置**: `src/auto_test/domain/`
**职责**: 核心业务逻辑，领域模型，业务规则

```python
# 示例: 领域实体
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4
from .value_objects import ApiPath, HttpMethod
from .events import ApiCreatedEvent

@dataclass
class Api:
    """API领域实体"""
    id: UUID
    name: str
    path: ApiPath
    method: HttpMethod
    system_id: UUID
    module_id: UUID
    enabled: bool = True
    version: str = "1.0.0"
    
    @classmethod
    def create(
        cls,
        name: str,
        path: str,
        method: str,
        system_id: UUID,
        module_id: UUID
    ) -> "Api":
        """创建API实体"""
        api = cls(
            id=uuid4(),
            name=name,
            path=ApiPath(path),
            method=HttpMethod(method),
            system_id=system_id,
            module_id=module_id
        )
        
        # 发布领域事件
        api._events.append(ApiCreatedEvent(api.id, api.name))
        return api
    
    def update_path(self, new_path: str) -> None:
        """更新API路径"""
        if not new_path.startswith('/'):
            raise ValueError("API路径必须以'/'开头")
        self.path = ApiPath(new_path)
```

### 4. 基础设施层 (Infrastructure Layer)
**位置**: `src/auto_test/infrastructure/`
**职责**: 数据持久化，外部服务集成，技术实现

```python
# 示例: 仓储实现
from sqlalchemy.ext.asyncio import AsyncSession
from ..domain.repositories.api_repository import ApiRepository
from ..domain.entities.api import Api

class SqlAlchemyApiRepository(ApiRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, api: Api) -> None:
        """保存API实体"""
        api_model = ApiModel.from_domain(api)
        self._session.add(api_model)
    
    async def find_by_id(self, api_id: UUID) -> Optional[Api]:
        """根据ID查找API"""
        result = await self._session.get(ApiModel, api_id)
        return result.to_domain() if result else None
```

## 📁 目录结构规范

```
src/auto_test/
├── api/                       # 表现层 (API层)
│   ├── __init__.py
│   ├── v1/                    # API版本控制
│   │   ├── __init__.py
│   │   ├── system_api.py      # 系统管理API
│   │   ├── agent_api.py       # 智能代理API
│   │   └── test_api.py        # 测试执行API
│   ├── middleware/            # 中间件
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   └── validation_middleware.py
│   └── schemas/               # API请求/响应模式
│       ├── __init__.py
│       ├── system_schemas.py
│       └── common_schemas.py
├── application/               # 应用层 (业务层)
│   ├── services/              # 业务服务
│   │   ├── __init__.py
│   │   ├── system_service.py  # 系统管理业务逻辑
│   │   ├── agent_service.py   # 代理管理业务逻辑
│   │   └── test_service.py    # 测试执行业务逻辑
│   ├── converters/            # 静态转换器
│   │   ├── __init__.py
│   │   ├── system_converter.py # 系统数据转换
│   │   ├── agent_converter.py  # 代理数据转换
│   │   └── base_converter.py   # 基础转换器
│   ├── dto/                   # 数据传输对象
│   │   ├── __init__.py
│   │   ├── system_dto.py
│   │   └── common_dto.py
│   └── use_cases/             # 用例编排
│       ├── __init__.py
│       └── system_use_cases.py
├── domain/                    # 领域层
│   ├── entities/              # 实体
│   │   ├── __init__.py
│   │   ├── system.py          # 系统实体
│   │   ├── agent.py           # 代理实体
│   │   └── test_execution.py  # 测试执行实体
│   ├── value_objects/         # 值对象
│   │   ├── __init__.py
│   │   ├── system_config.py
│   │   └── test_result.py
│   ├── aggregates/            # 聚合根
│   │   ├── __init__.py
│   │   ├── system_aggregate.py
│   │   └── test_aggregate.py
│   ├── repositories/          # 仓储接口
│   │   ├── __init__.py
│   │   ├── system_repository.py
│   │   └── base_repository.py
│   ├── services/              # 领域服务
│   │   ├── __init__.py
│   │   └── system_domain_service.py
│   └── events/                # 领域事件
│       ├── __init__.py
│       └── system_events.py
├── infrastructure/            # 基础设施层
│   ├── persistence/           # 数据持久化
│   │   ├── __init__.py
│   │   ├── models/            # 数据库模型 (单表操作)
│   │   │   ├── __init__.py
│   │   │   ├── system_model.py
│   │   │   ├── agent_model.py
│   │   │   └── base_model.py
│   │   ├── repositories/      # 仓储实现 (单表查询)
│   │   │   ├── __init__.py
│   │   │   ├── system_repository_impl.py
│   │   │   └── base_repository_impl.py
│   │   ├── dao/               # 数据访问对象 (单表CRUD)
│   │   │   ├── __init__.py
│   │   │   ├── system_dao.py
│   │   │   └── base_dao.py
│   │   └── unit_of_work.py    # 工作单元
│   ├── external/              # 外部服务
│   │   ├── __init__.py
│   │   └── http_client.py
│   └── messaging/             # 消息传递
│       ├── __init__.py
│       └── event_bus.py
└── api/                       # 表现层
    ├── __init__.py
    ├── controllers/
    ├── middleware/
    └── serializers/
```

## 🔧 编码规范

### 1. API层 (表现层) 职责规范

#### 1.1 API控制器职责
- **接收请求数据**: 处理HTTP请求，解析参数
- **返回响应数据**: 格式化响应，设置状态码
- **登录信息获取**: 从请求中提取用户认证信息
- **参数校验**: 基础的请求参数验证

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, validator
from typing import Optional, List
from ..application.services.system_service import SystemService
from ..application.dto.system_dto import SystemCreateDTO, SystemResponseDTO
from ..middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/v1/systems", tags=["systems"])
security = HTTPBearer()

class SystemCreateRequest(BaseModel):
    """系统创建请求模型"""
    name: str
    description: Optional[str] = None
    base_url: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('系统名称不能为空')
        return v.strip()
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('基础URL必须以http://或https://开头')
        return v

@router.post("/", response_model=SystemResponseDTO)
async def create_system(
    request: SystemCreateRequest,
    current_user: dict = Depends(get_current_user),
    system_service: SystemService = Depends()
):
    """创建系统 - API层只负责请求处理和响应"""
    try:
        # 1. 参数校验 (Pydantic自动处理)
        # 2. 获取登录用户信息
        user_id = current_user.get("user_id")
        
        # 3. 转换为DTO
        create_dto = SystemCreateDTO(
            name=request.name,
            description=request.description,
            base_url=request.base_url,
            created_by=user_id
        )
        
        # 4. 调用业务层
        result = await system_service.create_system(create_dto)
        
        # 5. 返回响应
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统创建失败"
        )

@router.get("/", response_model=List[SystemResponseDTO])
async def list_systems(
    page: int = 1,
    size: int = 10,
    current_user: dict = Depends(get_current_user),
    system_service: SystemService = Depends()
):
    """获取系统列表"""
    return await system_service.list_systems(page, size, current_user["user_id"])
```

### 2. 业务层 (应用层) 职责规范

#### 2.1 业务服务职责
- **多表查询处理**: 协调多个仓储进行复杂查询
- **业务逻辑编排**: 处理跨聚合的业务流程
- **数据转换协调**: 调用转换器进行数据格式转换

```python
from typing import List, Optional
from ..domain.repositories.system_repository import SystemRepository
from ..domain.repositories.agent_repository import AgentRepository
from ..infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl
from ..dto.system_dto import SystemCreateDTO, SystemResponseDTO
from ..converters.system_converter import SystemConverter
from ..domain.entities.system import System
from ..domain.value_objects.system_config import SystemConfig

class SystemService:
    """系统管理业务服务 - 处理多表业务逻辑"""
    
    def __init__(
        self,
        system_repo: SystemRepository,
        agent_repo: AgentRepository,
        user_repo: UserRepositoryImpl,
        converter: SystemConverter
    ):
        self._system_repo = system_repo
        self._agent_repo = agent_repo
        self._user_repo = user_repo
        self._converter = converter
    
    async def create_system(self, dto: SystemCreateDTO) -> SystemResponseDTO:
        """创建系统 - 多表业务逻辑处理"""
        
        # 1. 验证用户存在 (单表查询)
        user = await self._user_repo.find_by_id(dto.created_by)
        if not user:
            raise ValueError("用户不存在")
        
        # 2. 检查系统名称唯一性 (单表查询)
        existing_system = await self._system_repo.find_by_name(dto.name)
        if existing_system:
            raise ValueError("系统名称已存在")
        
        # 3. 创建系统实体
        system_config = SystemConfig(
            base_url=dto.base_url,
            timeout=30,
            retry_count=3
        )
        
        system = System.create(
            name=dto.name,
            description=dto.description,
            config=system_config,
            created_by=dto.created_by
        )
        
        # 4. 保存系统 (单表操作)
        saved_system = await self._system_repo.save(system)
        
        # 5. 创建默认代理 (跨表业务逻辑)
        default_agent = await self._create_default_agent(saved_system.id)
        
        # 6. 使用转换器转换数据
        return self._converter.to_response_dto(saved_system, user, default_agent)
    
    async def get_system_with_details(self, system_id: str, user_id: str) -> SystemResponseDTO:
        """获取系统详情 - 多表关联查询业务逻辑"""
        
        # 1. 获取系统信息 (单表查询)
        system = await self._system_repo.find_by_id(system_id)
        if not system:
            raise ValueError("系统不存在")
        
        # 2. 获取创建者信息 (单表查询)
        creator = await self._user_repo.find_by_id(system.created_by)
        
        # 3. 获取关联的代理列表 (单表查询)
        agents = await self._agent_repo.find_by_system_id(system_id)
        
        # 4. 检查用户权限 (业务逻辑)
        if not self._check_user_permission(system, user_id):
            raise ValueError("无权限访问该系统")
        
        # 5. 使用转换器组装返回数据
        return self._converter.to_detailed_response_dto(system, creator, agents)
    
    async def _create_default_agent(self, system_id: str):
        """创建默认代理 - 内部业务逻辑"""
        # 业务逻辑实现...
        pass
    
    def _check_user_permission(self, system: System, user_id: str) -> bool:
        """检查用户权限 - 业务规则"""
        return system.created_by == user_id or system.is_public
```

### 3. 静态转换器规范

#### 3.1 转换器职责
- **数据格式转换**: 将查询的数据转换成返回数据
- **DTO转换**: 实体与DTO之间的转换
- **数据组装**: 将多个数据源组装成完整的响应对象

```python
from typing import List, Optional
from ..dto.system_dto import SystemResponseDTO, SystemDetailDTO
from ..domain.entities.system import System
from ..infrastructure.persistence.models.user_model import UserModel
from ..infrastructure.persistence.models.agent_model import AgentModel

class SystemConverter:
    """系统数据转换器 - 静态转换方法"""
    
    @staticmethod
    def to_response_dto(
        system: System, 
        creator: Optional[UserModel] = None,
        default_agent: Optional[AgentModel] = None
    ) -> SystemResponseDTO:
        """将系统实体转换为响应DTO"""
        return SystemResponseDTO(
            id=str(system.id),
            name=system.name,
            description=system.description,
            base_url=system.config.base_url,
            status=system.status.value,
            created_by=str(system.created_by),
            creator_name=creator.username if creator else None,
            created_at=system.created_at,
            updated_at=system.updated_at,
            agent_count=1 if default_agent else 0
        )
    
    @staticmethod
    def to_detailed_response_dto(
        system: System,
        creator: UserModel,
        agents: List[AgentModel]
    ) -> SystemDetailDTO:
        """将多表数据转换为详细响应DTO"""
        return SystemDetailDTO(
            id=str(system.id),
            name=system.name,
            description=system.description,
            base_url=system.config.base_url,
            timeout=system.config.timeout,
            retry_count=system.config.retry_count,
            status=system.status.value,
            created_by=str(system.created_by),
            creator_info={
                "id": str(creator.id),
                "username": creator.username,
                "email": creator.email
            },
            agents=[
                {
                    "id": str(agent.id),
                    "name": agent.name,
                    "type": agent.type,
                    "status": agent.status
                }
                for agent in agents
            ],
            created_at=system.created_at,
            updated_at=system.updated_at
        )
    
    @staticmethod
    def from_create_dto(dto: SystemCreateDTO) -> System:
        """从创建DTO转换为系统实体"""
        return System.create(
            name=dto.name,
            description=dto.description,
            base_url=dto.base_url,
            created_by=dto.created_by
        )
    
    @staticmethod
    def to_list_dto(systems: List[System], creators: dict) -> List[SystemResponseDTO]:
        """批量转换系统列表"""
        return [
            SystemConverter.to_response_dto(
                system, 
                creators.get(str(system.created_by))
            )
            for system in systems
        ]
```

### 4. 数据访问层规范

#### 4.1 单表操作原则
- **DAO层**: 只处理单个表的CRUD操作
- **Repository层**: 基于DAO实现领域仓储接口
- **多表关联**: 在业务层处理，不在数据层处理

```python
# DAO层 - 单表操作
class SystemDAO:
    """系统数据访问对象 - 只处理system表"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, system_data: dict) -> SystemModel:
        """创建系统记录"""
        system = SystemModel(**system_data)
        self._session.add(system)
        await self._session.commit()
        await self._session.refresh(system)
        return system
    
    async def find_by_id(self, system_id: str) -> Optional[SystemModel]:
        """根据ID查询系统"""
        result = await self._session.execute(
            select(SystemModel).where(SystemModel.id == system_id)
        )
        return result.scalar_one_or_none()
    
    async def find_by_name(self, name: str) -> Optional[SystemModel]:
        """根据名称查询系统"""
        result = await self._session.execute(
            select(SystemModel).where(SystemModel.name == name)
        )
        return result.scalar_one_or_none()
    
    async def find_by_creator(self, creator_id: str) -> List[SystemModel]:
        """根据创建者查询系统列表"""
        result = await self._session.execute(
            select(SystemModel).where(SystemModel.created_by == creator_id)
        )
        return result.scalars().all()

# Repository实现 - 基于DAO
class SystemRepositoryImpl(SystemRepository):
    """系统仓储实现"""
    
    def __init__(self, dao: SystemDAO, converter: SystemConverter):
        self._dao = dao
        self._converter = converter
    
    async def save(self, system: System) -> System:
        """保存系统实体"""
        system_data = {
            "id": str(system.id),
            "name": system.name,
            "description": system.description,
            "base_url": system.config.base_url,
            "created_by": str(system.created_by),
            "status": system.status.value
        }
        
        model = await self._dao.create(system_data)
        return self._converter.from_model(model)
    
    async def find_by_id(self, system_id: str) -> Optional[System]:
        """根据ID查找系统"""
        model = await self._dao.find_by_id(system_id)
        return self._converter.from_model(model) if model else None
```

## 🎯 DDD分层最佳实践总结

### 核心原则

#### 1. API层 (表现层) - 轻薄原则
```
✅ 应该做的:
- 接收HTTP请求，解析参数
- 基础参数校验 (格式、必填项)
- 获取登录用户信息
- 调用业务层服务
- 格式化响应数据
- 异常处理和状态码设置

❌ 不应该做的:
- 复杂业务逻辑处理
- 直接操作数据库
- 多表关联查询
- 复杂数据转换
```

#### 2. 业务层 (应用层) - 编排原则
```
✅ 应该做的:
- 多表业务逻辑编排
- 跨聚合的业务流程
- 调用多个仓储进行数据查询
- 业务规则验证
- 调用转换器进行数据转换
- 事务管理

❌ 不应该做的:
- 直接处理HTTP请求
- 单表的简单CRUD (应委托给仓储)
- 复杂的数据格式转换 (应委托给转换器)
```

#### 3. 转换器 - 专一原则
```
✅ 应该做的:
- 实体与DTO之间的转换
- 数据库模型与领域实体的转换
- 多个数据源的组装
- 数据格式标准化
- 静态转换方法

❌ 不应该做的:
- 业务逻辑处理
- 数据库查询
- 复杂的业务规则验证
```

#### 4. 数据访问层 - 单一原则
```
✅ 应该做的:
- 单表的CRUD操作
- 简单的查询条件
- 数据库事务管理
- 数据持久化

❌ 不应该做的:
- 复杂的多表关联查询
- 业务逻辑处理
- 数据格式转换
```

### 实际应用流程

#### 典型的请求处理流程:
```
1. API层接收请求 → 参数校验 → 获取用户信息
2. 调用业务层服务 → 传递DTO参数
3. 业务层协调多个仓储 → 执行业务逻辑
4. 各仓储执行单表查询 → 返回领域实体
5. 业务层调用转换器 → 组装响应数据
6. API层返回格式化响应
```

#### 数据查询策略:
```
- 单表查询: 直接使用对应的Repository
- 多表关联: 在业务层分别查询，然后组装
- 复杂查询: 拆分为多个简单查询，业务层处理
- 数据转换: 统一使用静态转换器
```

### 命名规范

```python
# API层
- 文件: {domain}_api.py (如: system_api.py)
- 类: {Domain}Controller (如: SystemController)
- 方法: HTTP动词 + 业务含义 (如: create_system, list_systems)

# 业务层
- 文件: {domain}_service.py (如: system_service.py)
- 类: {Domain}Service (如: SystemService)
- 方法: 业务动作 (如: create_system, get_system_with_details)

# 转换器
- 文件: {domain}_converter.py (如: system_converter.py)
- 类: {Domain}Converter (如: SystemConverter)
- 方法: to_{target}_dto, from_{source}_dto

# 数据访问层
- DAO文件: {domain}_dao.py (如: system_dao.py)
- Repository文件: {domain}_repository_impl.py
- 类: {Domain}DAO, {Domain}RepositoryImpl
```

### 依赖注入配置

```python
# 推荐的依赖注入配置
def configure_dependencies():
    # DAO层
    container.bind(SystemDAO, SystemDAO)
    container.bind(AgentDAO, AgentDAO)
    
    # Repository层
    container.bind(SystemRepository, SystemRepositoryImpl)
    container.bind(AgentRepository, AgentRepositoryImpl)
    
    # 转换器
    container.bind(SystemConverter, SystemConverter)
    
    # 业务层
    container.bind(SystemService, SystemService)
```

这种分层架构确保了:
- **职责清晰**: 每层只关注自己的职责
- **易于测试**: 各层可以独立测试
- **易于维护**: 修改某层不影响其他层
- **可扩展性**: 新增功能时遵循相同模式

### 5. 实体 (Entities)

```python
from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4
from .events import DomainEvent

@dataclass
class Entity:
    """基础实体类"""
    id: UUID = field(default_factory=uuid4)
    _events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def clear_events(self) -> List[DomainEvent]:
        """清空并返回领域事件"""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def add_event(self, event: DomainEvent) -> None:
        """添加领域事件"""
        self._events.append(event)
```

### 2. 值对象 (Value Objects)

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ValueObject:
    """基础值对象类"""
    
    def __post_init__(self):
        """值对象创建后验证"""
        self._validate()
    
    def _validate(self) -> None:
        """子类实现具体验证逻辑"""
        pass

@dataclass(frozen=True)
class ApiPath(ValueObject):
    """API路径值对象"""
    value: str
    
    def _validate(self) -> None:
        if not self.value.startswith('/'):
            raise ValueError("API路径必须以'/'开头")
        if len(self.value) > 255:
            raise ValueError("API路径长度不能超过255个字符")
```

### 3. 聚合根 (Aggregate Root)

```python
from typing import List, Optional
from .entities import Entity
from .value_objects import ApiPath, HttpMethod

class ApiAggregate(Entity):
    """API聚合根"""
    
    def __init__(self, name: str, path: str, method: str):
        super().__init__()
        self.name = name
        self.path = ApiPath(path)
        self.method = HttpMethod(method)
        self._modules: List[Module] = []
    
    def add_module(self, module: "Module") -> None:
        """添加模块"""
        if self._is_module_exists(module.name):
            raise ValueError(f"模块 {module.name} 已存在")
        
        self._modules.append(module)
        self.add_event(ModuleAddedEvent(self.id, module.id))
    
    def _is_module_exists(self, name: str) -> bool:
        """检查模块是否存在"""
        return any(m.name == name for m in self._modules)
```

### 4. 仓储接口 (Repository Interface)

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.api import Api

class ApiRepository(ABC):
    """API仓储接口"""
    
    @abstractmethod
    async def save(self, api: Api) -> None:
        """保存API"""
        pass
    
    @abstractmethod
    async def find_by_id(self, api_id: UUID) -> Optional[Api]:
        """根据ID查找API"""
        pass
    
    @abstractmethod
    async def find_by_system_id(self, system_id: UUID) -> List[Api]:
        """根据系统ID查找API列表"""
        pass
    
    @abstractmethod
    async def delete(self, api: Api) -> None:
        """删除API"""
        pass
```

### 5. 领域服务 (Domain Service)

```python
from typing import List
from ..entities.api import Api
from ..repositories.api_repository import ApiRepository

class ApiDomainService:
    """API领域服务"""
    
    def __init__(self, api_repository: ApiRepository):
        self._api_repository = api_repository
    
    async def validate_unique_path(
        self, 
        system_id: UUID, 
        path: str, 
        method: str,
        exclude_id: Optional[UUID] = None
    ) -> None:
        """验证API路径唯一性"""
        existing_apis = await self._api_repository.find_by_system_id(system_id)
        
        for api in existing_apis:
            if (api.id != exclude_id and 
                api.path.value == path and 
                api.method.value == method):
                raise ValueError(f"路径 {path} 和方法 {method} 的组合已存在")
    
    def create_api(
        self,
        name: str,
        path: str,
        method: str,
        system_id: UUID,
        module_id: UUID
    ) -> Api:
        """创建API实体"""
        # 业务规则验证
        if not name.strip():
            raise ValueError("API名称不能为空")
        
        return Api.create(
            name=name.strip(),
            path=path,
            method=method,
            system_id=system_id,
            module_id=module_id
        )
```

## 🎯 最佳实践

### 1. 依赖注入

```python
# 使用dependency-injector
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class Container(containers.DeclarativeContainer):
    # 配置
    config = providers.Configuration()
    
    # 数据库
    database = providers.Singleton(Database, config.database.url)
    
    # 仓储
    api_repository = providers.Factory(
        SqlAlchemyApiRepository,
        session=database.provided.session
    )
    
    # 领域服务
    api_domain_service = providers.Factory(
        ApiDomainService,
        api_repository=api_repository
    )
    
    # 应用服务
    api_service = providers.Factory(
        ApiService,
        api_repository=api_repository,
        domain_service=api_domain_service
    )

# 在API控制器中使用
@inject
async def create_api(
    request: CreateApiRequest,
    service: ApiService = Depends(Provide[Container.api_service])
):
    return await service.create_api(request)
```

### 2. 工作单元模式

```python
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

class UnitOfWork:
    """工作单元"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self) -> None:
        """提交事务"""
        await self._session.commit()
    
    async def rollback(self) -> None:
        """回滚事务"""
        await self._session.rollback()
```

### 3. 领域事件处理

```python
from typing import List
from ..domain.events import DomainEvent, ApiCreatedEvent

class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._handlers = {}
    
    def register(self, event_type: type, handler):
        """注册事件处理器"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, events: List[DomainEvent]) -> None:
        """发布事件"""
        for event in events:
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                await handler.handle(event)

# 事件处理器
class ApiCreatedEventHandler:
    async def handle(self, event: ApiCreatedEvent) -> None:
        """处理API创建事件"""
        # 发送通知、更新缓存等
        pass
```

## 📝 命名约定

### 1. 文件和目录命名
- 使用小写字母和下划线: `api_service.py`
- 目录名使用复数形式: `entities/`, `repositories/`

### 2. 类命名
- 实体: `Api`, `System`, `Module`
- 值对象: `ApiPath`, `HttpMethod`
- 服务: `ApiService`, `ApiDomainService`
- 仓储: `ApiRepository`, `SqlAlchemyApiRepository`

### 3. 方法命名
- 使用动词开头: `create_api()`, `find_by_id()`
- 布尔方法使用 `is_` 或 `has_` 前缀: `is_valid()`, `has_permission()`

## ✅ 代码检查清单

### 领域层检查
- [ ] 实体包含业务逻辑，不包含技术细节
- [ ] 值对象是不可变的
- [ ] 聚合根维护内部一致性
- [ ] 仓储接口定义在领域层
- [ ] 领域服务只包含不属于单个实体的业务逻辑

### 应用层检查
- [ ] 应用服务编排领域对象
- [ ] 事务边界在应用层管理
- [ ] DTO只用于数据传输
- [ ] 不包含业务逻辑

### 基础设施层检查
- [ ] 仓储实现在基础设施层
- [ ] 数据库模型与领域模型分离
- [ ] 外部服务集成在基础设施层

### 表现层检查
- [ ] 控制器只处理HTTP相关逻辑
- [ ] 数据验证和转换
- [ ] 不包含业务逻辑

## 📚 参考资源

- [Domain-Driven Design: Tackling Complexity in the Heart of Software](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215)
- [Implementing Domain-Driven Design](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)