# 后端代码注释规范

## 1. 总体原则

### 1.1 注释目的
- **业务逻辑说明**：清晰解释业务规则和处理流程
- **API文档化**：为接口提供完整的文档说明
- **数据库操作说明**：解释复杂的SQL查询和数据处理逻辑
- **异常处理说明**：说明错误处理策略和异常情况
- **性能优化说明**：解释性能相关的设计决策

### 1.2 注释语言
- 统一使用中文注释
- 技术术语可保留英文，但需要中文解释
- 注释内容要准确、详细、专业

## 2. 文件级注释

### 2.1 模块文件头注释
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理服务模块

本模块提供用户相关的业务逻辑处理，包括：
- 用户信息的增删改查
- 用户权限验证
- 用户状态管理
- 用户数据统计

Author: 开发团队
Created: 2024-01-01
Updated: 2024-01-15
Version: 1.2.0

Dependencies:
    - FastAPI: Web框架
    - SQLAlchemy: ORM框架
    - Pydantic: 数据验证
    - bcrypt: 密码加密

Business Rules:
    - 用户名必须唯一
    - 密码必须符合安全策略
    - 删除用户时需要软删除
    - 用户状态变更需要记录日志
"""
```

### 2.2 配置文件注释
```python
"""
应用配置模块

定义应用运行所需的各种配置参数，包括：
- 数据库连接配置
- API服务配置
- 安全相关配置
- 第三方服务配置

配置优先级：
1. 环境变量
2. 配置文件
3. 默认值

注意事项：
- 敏感信息（如密码、密钥）必须通过环境变量配置
- 生产环境和开发环境使用不同的配置文件
- 配置变更需要重启服务才能生效
"""
```

## 3. 类注释

### 3.1 业务服务类
```python
class UserService:
    """
    用户业务服务类
    
    负责处理用户相关的业务逻辑，包括用户的创建、更新、删除、查询等操作。
    该类封装了用户管理的核心业务规则，确保数据的一致性和业务逻辑的正确性。
    
    主要功能：
        - 用户注册和登录验证
        - 用户信息管理（增删改查）
        - 用户权限验证和角色管理
        - 用户状态管理（启用/禁用）
        - 用户数据统计和分析
    
    业务规则：
        - 用户名和邮箱必须唯一
        - 密码必须符合安全策略（长度、复杂度）
        - 用户删除采用软删除方式
        - 重要操作需要记录操作日志
        - 用户状态变更需要权限验证
    
    依赖注入：
        - user_dao: 用户数据访问对象
        - logger: 日志记录器
        - cache: 缓存服务
    
    异常处理：
        - UserNotFoundError: 用户不存在
        - DuplicateUserError: 用户重复
        - InvalidPasswordError: 密码不符合要求
        - PermissionDeniedError: 权限不足
    
    Example:
        user_service = UserService(user_dao, logger, cache)
        user = await user_service.create_user({
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'SecurePass123!'
        })
    """
```

### 3.2 数据访问类（DAO）
```python
class UserDAO:
    """
    用户数据访问对象
    
    负责用户数据的数据库操作，提供对用户表的CRUD操作接口。
    该类封装了所有与用户数据相关的SQL操作，确保数据访问的一致性和安全性。
    
    数据表结构：
        - users: 用户基本信息表
        - user_roles: 用户角色关联表
        - user_permissions: 用户权限表
        - user_logs: 用户操作日志表
    
    主要方法：
        - create_user(): 创建新用户
        - get_user_by_id(): 根据ID获取用户
        - get_user_by_username(): 根据用户名获取用户
        - update_user(): 更新用户信息
        - delete_user(): 软删除用户
        - get_users_with_pagination(): 分页获取用户列表
    
    查询优化：
        - 使用索引优化常用查询
        - 分页查询避免全表扫描
        - 复杂查询使用预编译语句
        - 批量操作使用事务处理
    
    数据安全：
        - 密码字段自动加密存储
        - 敏感信息查询时自动脱敏
        - SQL注入防护
        - 数据访问权限控制
    
    缓存策略：
        - 用户基本信息缓存30分钟
        - 用户权限信息缓存15分钟
        - 缓存失效时自动刷新
    """
```

## 4. 函数/方法注释

### 4.1 API接口方法
```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    创建新用户接口
    
    该接口用于创建新的用户账户，需要管理员权限。
    创建成功后会自动发送欢迎邮件给新用户。
    
    Args:
        user_data (UserCreateRequest): 用户创建请求数据
            - username (str): 用户名，3-20个字符，只能包含字母、数字、下划线
            - email (str): 邮箱地址，必须是有效的邮箱格式
            - password (str): 密码，8-20个字符，必须包含大小写字母和数字
            - full_name (str): 真实姓名，2-50个字符
            - phone (str, optional): 手机号码，11位数字
            - role_ids (List[int], optional): 角色ID列表，默认为普通用户角色
        
        current_user (User): 当前登录用户，通过JWT token验证获得
        user_service (UserService): 用户服务实例，通过依赖注入获得
    
    Returns:
        UserResponse: 创建成功的用户信息
            - id (int): 用户ID
            - username (str): 用户名
            - email (str): 邮箱地址
            - full_name (str): 真实姓名
            - status (str): 用户状态（active/inactive）
            - created_at (datetime): 创建时间
            - roles (List[Role]): 用户角色列表
    
    Raises:
        HTTPException(400): 请求参数验证失败
            - 用户名已存在
            - 邮箱已被使用
            - 密码不符合安全要求
        HTTPException(403): 权限不足，需要管理员权限
        HTTPException(500): 服务器内部错误
            - 数据库连接失败
            - 邮件发送失败
    
    Business Logic:
        1. 验证当前用户是否有创建用户的权限
        2. 验证用户名和邮箱的唯一性
        3. 验证密码强度
        4. 加密存储密码
        5. 分配默认角色（如果未指定）
        6. 创建用户记录
        7. 发送欢迎邮件
        8. 记录操作日志
    
    Example:
        POST /api/users
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe",
            "phone": "13800138000",
            "role_ids": [2, 3]
        }
        
        Response:
        {
            "id": 123,
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "status": "active",
            "created_at": "2024-01-15T10:30:00Z",
            "roles": [
                {"id": 2, "name": "editor"},
                {"id": 3, "name": "viewer"}
            ]
        }
    """
```

### 4.2 业务逻辑方法
```python
async def validate_user_permissions(
    self, 
    user_id: int, 
    required_permissions: List[str]
) -> bool:
    """
    验证用户权限
    
    检查指定用户是否具有所需的权限。该方法会检查用户的直接权限
    以及通过角色继承的权限，支持权限的层级验证。
    
    Args:
        user_id (int): 用户ID，必须是有效的用户标识
        required_permissions (List[str]): 所需权限列表
            权限格式：'resource:action'，例如：
            - 'user:create' - 创建用户权限
            - 'user:read' - 查看用户权限
            - 'user:update' - 更新用户权限
            - 'user:delete' - 删除用户权限
    
    Returns:
        bool: 权限验证结果
            - True: 用户具有所有所需权限
            - False: 用户缺少部分或全部权限
    
    Raises:
        UserNotFoundError: 用户不存在
        DatabaseError: 数据库查询失败
    
    Business Logic:
        1. 验证用户是否存在且状态为活跃
        2. 获取用户的直接权限
        3. 获取用户角色的权限
        4. 合并权限列表并去重
        5. 检查是否包含所有所需权限
        6. 记录权限验证日志（用于审计）
    
    Performance:
        - 使用缓存减少数据库查询
        - 权限数据缓存15分钟
        - 批量查询优化性能
    
    Security:
        - 权限验证失败时记录安全日志
        - 防止权限提升攻击
        - 支持权限的时效性验证
    
    Example:
        # 验证用户是否有创建和编辑用户的权限
        has_permission = await user_service.validate_user_permissions(
            user_id=123,
            required_permissions=['user:create', 'user:update']
        )
        
        if has_permission:
            # 执行需要权限的操作
            pass
        else:
            # 权限不足，返回错误
            raise PermissionDeniedError("权限不足")
    """
```

### 4.3 数据库操作方法
```python
async def get_users_with_pagination(
    self,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    role_ids: Optional[List[int]] = None,
    sort_by: str = 'created_at',
    sort_order: str = 'desc'
) -> Tuple[List[User], int]:
    """
    分页获取用户列表
    
    根据指定条件分页查询用户列表，支持多种筛选和排序选项。
    该方法优化了查询性能，避免了大数据量时的性能问题。
    
    Args:
        page (int): 页码，从1开始，默认为1
        page_size (int): 每页记录数，范围1-100，默认为20
        keyword (Optional[str]): 搜索关键词，支持用户名、邮箱、姓名模糊搜索
        status (Optional[str]): 用户状态筛选
            - 'active': 活跃用户
            - 'inactive': 非活跃用户
            - None: 所有状态
        role_ids (Optional[List[int]]): 角色ID列表，筛选具有指定角色的用户
        sort_by (str): 排序字段，默认为'created_at'
            支持字段：'id', 'username', 'email', 'created_at', 'updated_at'
        sort_order (str): 排序方向，'asc'或'desc'，默认为'desc'
    
    Returns:
        Tuple[List[User], int]: 返回元组
            - List[User]: 用户列表，包含用户基本信息和角色信息
            - int: 符合条件的总记录数（用于分页计算）
    
    Raises:
        ValueError: 参数验证失败
            - 页码小于1
            - 每页记录数超出范围
            - 排序字段不支持
        DatabaseError: 数据库查询失败
    
    SQL Query Optimization:
        - 使用索引优化WHERE条件查询
        - LIMIT/OFFSET实现分页，避免全表扫描
        - LEFT JOIN获取角色信息，减少N+1查询问题
        - 使用COUNT(*)单独查询总数，提高性能
    
    Query Structure:
        SELECT u.*, r.name as role_name
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE u.deleted_at IS NULL
        [AND u.status = :status]
        [AND (u.username LIKE :keyword OR u.email LIKE :keyword OR u.full_name LIKE :keyword)]
        [AND ur.role_id IN :role_ids]
        ORDER BY u.{sort_by} {sort_order}
        LIMIT :page_size OFFSET :offset
    
    Caching Strategy:
        - 查询结果缓存5分钟（用户列表变化不频繁）
        - 缓存键包含所有查询参数
        - 用户数据变更时清除相关缓存
    
    Example:
        # 获取第2页的活跃用户，每页10条，按创建时间倒序
        users, total = await user_dao.get_users_with_pagination(
            page=2,
            page_size=10,
            status='active',
            sort_by='created_at',
            sort_order='desc'
        )
        
        # 搜索包含"张"的用户
        users, total = await user_dao.get_users_with_pagination(
            keyword='张',
            page=1,
            page_size=20
        )
    """
```

## 5. 异常处理注释

### 5.1 自定义异常类
```python
class UserServiceError(Exception):
    """
    用户服务异常基类
    
    所有用户服务相关的异常都应该继承此类。
    提供统一的异常处理机制和错误信息格式。
    
    Attributes:
        message (str): 错误消息
        error_code (str): 错误代码，用于前端国际化
        details (dict): 详细错误信息，包含调试信息
    """
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        初始化异常
        
        Args:
            message (str): 用户友好的错误消息
            error_code (str): 错误代码，格式为'USER_ERROR_XXX'
            details (dict): 详细错误信息，仅用于调试
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'USER_ERROR_UNKNOWN'
        self.details = details or {}


class UserNotFoundError(UserServiceError):
    """
    用户不存在异常
    
    当尝试访问不存在的用户时抛出此异常。
    通常发生在根据ID或用户名查询用户时。
    
    Usage:
        if not user:
            raise UserNotFoundError(
                message=f"用户不存在: {user_id}",
                error_code="USER_NOT_FOUND",
                details={"user_id": user_id, "query_time": datetime.now()}
            )
    """
    pass


class DuplicateUserError(UserServiceError):
    """
    用户重复异常
    
    当尝试创建已存在的用户时抛出此异常。
    检查用户名、邮箱等唯一字段的重复性。
    
    Usage:
        if existing_user:
            raise DuplicateUserError(
                message=f"用户名已存在: {username}",
                error_code="USER_DUPLICATE",
                details={"field": "username", "value": username}
            )
    """
    pass
```

### 5.2 异常处理装饰器
```python
def handle_user_service_errors(func):
    """
    用户服务异常处理装饰器
    
    统一处理用户服务中的异常，将内部异常转换为HTTP异常。
    记录错误日志，并返回标准化的错误响应。
    
    该装饰器会捕获以下异常类型：
    - UserServiceError及其子类：业务逻辑异常
    - DatabaseError：数据库操作异常
    - ValidationError：数据验证异常
    - Exception：其他未预期异常
    
    Error Response Format:
        {
            "success": false,
            "message": "用户友好的错误消息",
            "error_code": "ERROR_CODE",
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "uuid-string"
        }
    
    Logging:
        - 业务异常记录为WARNING级别
        - 系统异常记录为ERROR级别
        - 包含请求ID用于问题追踪
        - 敏感信息自动脱敏
    
    Usage:
        @handle_user_service_errors
        async def create_user(user_data: UserCreateRequest):
            # 业务逻辑代码
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request_id = str(uuid.uuid4())
        try:
            return await func(*args, **kwargs)
        except UserNotFoundError as e:
            # 用户不存在 - 404错误
            logger.warning(f"用户不存在: {e.message}", extra={
                "request_id": request_id,
                "error_code": e.error_code,
                "details": e.details
            })
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "message": e.message,
                    "error_code": e.error_code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            )
        except DuplicateUserError as e:
            # 用户重复 - 400错误
            logger.warning(f"用户重复: {e.message}", extra={
                "request_id": request_id,
                "error_code": e.error_code,
                "details": e.details
            })
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": e.message,
                    "error_code": e.error_code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            )
        except Exception as e:
            # 未预期异常 - 500错误
            logger.error(f"未预期异常: {str(e)}", extra={
                "request_id": request_id,
                "exception_type": type(e).__name__,
                "traceback": traceback.format_exc()
            })
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "message": "服务器内部错误",
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id
                }
            )
    return wrapper
```

## 6. 数据模型注释

### 6.1 Pydantic模型
```python
class UserCreateRequest(BaseModel):
    """
    用户创建请求模型
    
    定义创建用户时需要的数据结构和验证规则。
    该模型用于API接口的请求参数验证。
    
    Validation Rules:
        - username: 3-20个字符，只能包含字母、数字、下划线
        - email: 必须是有效的邮箱格式
        - password: 8-20个字符，必须包含大小写字母和数字
        - full_name: 2-50个字符，不能包含特殊字符
        - phone: 11位数字，可选
    
    Business Rules:
        - 用户名和邮箱必须在系统中唯一
        - 密码会在存储前自动加密
        - 手机号码支持中国大陆格式
    
    Example:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe",
            "phone": "13800138000"
        }
    """
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        regex=r'^[a-zA-Z0-9_]+$',
        description="用户名，3-20个字符，只能包含字母、数字、下划线"
    )
    
    email: EmailStr = Field(
        ...,
        description="邮箱地址，必须是有效的邮箱格式"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=20,
        regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]+$',
        description="密码，8-20个字符，必须包含大小写字母和数字"
    )
    
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        regex=r'^[\u4e00-\u9fa5a-zA-Z\s]+$',
        description="真实姓名，2-50个字符，支持中文、英文和空格"
    )
    
    phone: Optional[str] = Field(
        None,
        regex=r'^1[3-9]\d{9}$',
        description="手机号码，11位数字，可选"
    )
    
    class Config:
        """Pydantic配置"""
        # 生成JSON Schema示例
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "phone": "13800138000"
            }
        }
```

### 6.2 SQLAlchemy模型
```python
class User(Base):
    """
    用户数据模型
    
    对应数据库中的users表，存储用户的基本信息。
    该模型定义了用户数据的结构、约束和关系。
    
    Table Structure:
        - 主键：id (自增整数)
        - 唯一约束：username, email
        - 索引：username, email, created_at
        - 软删除：deleted_at字段
    
    Relationships:
        - roles: 多对多关系，通过user_roles表关联
        - permissions: 多对多关系，通过user_permissions表关联
        - logs: 一对多关系，用户操作日志
    
    Business Rules:
        - 用户名和邮箱必须唯一
        - 密码存储时自动加密
        - 删除用户时使用软删除
        - 创建和更新时间自动维护
    
    Security:
        - 密码字段不会在序列化时输出
        - 敏感信息查询时自动脱敏
        - 支持数据访问权限控制
    """
    
    __tablename__ = 'users'
    
    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID，主键"
    )
    
    # 基本信息
    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名，3-20个字符，唯一"
    )
    
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="邮箱地址，唯一"
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希值，使用bcrypt加密"
    )
    
    full_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="真实姓名"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="手机号码，可选"
    )
    
    # 状态信息
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='active',
        comment="用户状态：active-活跃，inactive-非活跃"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="创建时间"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="删除时间，软删除标记"
    )
    
    # 关系定义
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
        doc="用户角色列表，多对多关系"
    )
    
    logs: Mapped[List["UserLog"]] = relationship(
        "UserLog",
        back_populates="user",
        lazy="dynamic",
        doc="用户操作日志，一对多关系"
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典格式
        
        Args:
            include_sensitive (bool): 是否包含敏感信息（如密码哈希）
        
        Returns:
            dict: 用户信息字典
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            data['deleted_at'] = self.deleted_at.isoformat() if self.deleted_at else None
        
        return data
```

## 7. 配置和常量注释

### 7.1 配置类
```python
class DatabaseConfig:
    """
    数据库配置类
    
    管理数据库连接相关的配置参数。
    支持多环境配置（开发、测试、生产）。
    
    Environment Variables:
        - DB_HOST: 数据库主机地址
        - DB_PORT: 数据库端口
        - DB_NAME: 数据库名称
        - DB_USER: 数据库用户名
        - DB_PASSWORD: 数据库密码
        - DB_POOL_SIZE: 连接池大小
        - DB_MAX_OVERFLOW: 连接池最大溢出数
    
    Connection Pool:
        - 默认连接池大小：10
        - 最大溢出连接：20
        - 连接超时：30秒
        - 连接回收时间：3600秒
    
    Security:
        - 密码通过环境变量配置
        - 支持SSL连接
        - 连接字符串不记录敏感信息
    """
    
    def __init__(self):
        """初始化数据库配置"""
        # 基本连接参数
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'auto_test')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        
        # 连接池配置
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))
        
        # SSL配置
        self.ssl_mode = os.getenv('DB_SSL_MODE', 'prefer')
        
    @property
    def database_url(self) -> str:
        """
        获取数据库连接URL
        
        Returns:
            str: 数据库连接字符串，密码部分会被脱敏
        """
        return f"postgresql://{self.username}:***@{self.host}:{self.port}/{self.database}"
    
    @property
    def sqlalchemy_database_url(self) -> str:
        """
        获取SQLAlchemy数据库连接URL
        
        Returns:
            str: 完整的数据库连接字符串
        """
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
```

### 7.2 常量定义
```python
class UserConstants:
    """
    用户相关常量定义
    
    集中管理用户模块中使用的常量值，便于维护和修改。
    所有常量都应该有明确的业务含义和使用场景说明。
    """
    
    # 用户状态常量
    STATUS_ACTIVE = 'active'          # 活跃状态：用户可以正常登录和使用系统
    STATUS_INACTIVE = 'inactive'      # 非活跃状态：用户被暂时禁用，无法登录
    STATUS_PENDING = 'pending'        # 待激活状态：新注册用户，等待邮箱验证
    STATUS_SUSPENDED = 'suspended'    # 暂停状态：用户因违规被暂停使用
    
    # 用户状态列表（用于验证）
    VALID_STATUSES = [STATUS_ACTIVE, STATUS_INACTIVE, STATUS_PENDING, STATUS_SUSPENDED]
    
    # 密码相关常量
    PASSWORD_MIN_LENGTH = 8           # 密码最小长度
    PASSWORD_MAX_LENGTH = 20          # 密码最大长度
    PASSWORD_HASH_ROUNDS = 12         # bcrypt加密轮数，平衡安全性和性能
    
    # 用户名相关常量
    USERNAME_MIN_LENGTH = 3           # 用户名最小长度
    USERNAME_MAX_LENGTH = 20          # 用户名最大长度
    USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'  # 用户名格式：字母、数字、下划线
    
    # 分页相关常量
    DEFAULT_PAGE_SIZE = 20            # 默认每页记录数
    MAX_PAGE_SIZE = 100               # 最大每页记录数，防止性能问题
    
    # 缓存相关常量
    CACHE_USER_INFO_TTL = 1800        # 用户信息缓存时间（30分钟）
    CACHE_USER_PERMISSIONS_TTL = 900  # 用户权限缓存时间（15分钟）
    
    # 业务规则常量
    MAX_LOGIN_ATTEMPTS = 5            # 最大登录尝试次数
    LOGIN_LOCKOUT_DURATION = 900      # 登录锁定时间（15分钟）
    PASSWORD_RESET_TOKEN_TTL = 3600   # 密码重置令牌有效期（1小时）
    
    # 错误代码常量
    ERROR_USER_NOT_FOUND = 'USER_NOT_FOUND'
    ERROR_USER_DUPLICATE = 'USER_DUPLICATE'
    ERROR_INVALID_PASSWORD = 'INVALID_PASSWORD'
    ERROR_PERMISSION_DENIED = 'PERMISSION_DENIED'
    ERROR_USER_LOCKED = 'USER_LOCKED'
    ERROR_TOKEN_EXPIRED = 'TOKEN_EXPIRED'


class APIConstants:
    """
    API相关常量定义
    
    定义API接口中使用的常量，包括响应码、消息模板等。
    """
    
    # HTTP状态码对应的业务消息
    HTTP_STATUS_MESSAGES = {
        200: '操作成功',
        201: '创建成功',
        400: '请求参数错误',
        401: '未授权访问',
        403: '权限不足',
        404: '资源不存在',
        409: '资源冲突',
        422: '数据验证失败',
        500: '服务器内部错误'
    }
    
    # API响应格式
    RESPONSE_SUCCESS_FORMAT = {
        'success': True,
        'message': '',
        'data': None,
        'timestamp': None
    }
    
    RESPONSE_ERROR_FORMAT = {
        'success': False,
        'message': '',
        'error_code': '',
        'timestamp': None,
        'request_id': None
    }
    
    # 请求头常量
    HEADER_REQUEST_ID = 'X-Request-ID'
    HEADER_USER_AGENT = 'User-Agent'
    HEADER_AUTHORIZATION = 'Authorization'
    HEADER_CONTENT_TYPE = 'Content-Type'
    
    # 内容类型常量
    CONTENT_TYPE_JSON = 'application/json'
    CONTENT_TYPE_FORM = 'application/x-www-form-urlencoded'
    CONTENT_TYPE_MULTIPART = 'multipart/form-data'
```

## 8. 工具和实用函数注释

### 8.1 工具函数
```python
def generate_password_hash(password: str) -> str:
    """
    生成密码哈希值
    
    使用bcrypt算法对密码进行加密，提供安全的密码存储方案。
    该函数会自动生成盐值，确保相同密码产生不同的哈希值。
    
    Args:
        password (str): 原始密码，长度应在8-20个字符之间
    
    Returns:
        str: 加密后的密码哈希值，包含盐值信息
    
    Raises:
        ValueError: 密码为空或长度不符合要求
        
    Security Features:
        - 使用bcrypt算法，抗彩虹表攻击
        - 自动生成随机盐值
        - 可配置的加密轮数（默认12轮）
        - 时间复杂度随轮数指数增长
    
    Performance:
        - 12轮加密大约需要100-200ms
        - 加密时间会随硬件性能变化
        - 建议在异步环境中使用
    
    Example:
        password = "SecurePass123!"
        hash_value = generate_password_hash(password)
        # 输出类似：$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.FG6
    """
    if not password or len(password) < UserConstants.PASSWORD_MIN_LENGTH:
        raise ValueError(f"密码长度必须至少{UserConstants.PASSWORD_MIN_LENGTH}个字符")
    
    if len(password) > UserConstants.PASSWORD_MAX_LENGTH:
        raise ValueError(f"密码长度不能超过{UserConstants.PASSWORD_MAX_LENGTH}个字符")
    
    # 使用bcrypt生成密码哈希
    salt = bcrypt.gensalt(rounds=UserConstants.PASSWORD_HASH_ROUNDS)
    password_bytes = password.encode('utf-8')
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    
    return hash_bytes.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码是否正确
    
    将用户输入的密码与存储的哈希值进行比较，验证密码的正确性。
    该函数使用常量时间比较，防止时序攻击。
    
    Args:
        password (str): 用户输入的原始密码
        password_hash (str): 存储在数据库中的密码哈希值
    
    Returns:
        bool: 密码验证结果
            - True: 密码正确
            - False: 密码错误或哈希值格式不正确
    
    Security Features:
        - 常量时间比较，防止时序攻击
        - 自动处理盐值提取
        - 异常安全，不会泄露敏感信息
    
    Performance:
        - 验证时间与加密时间相当
        - 错误的哈希格式会快速返回False
        - 建议在异步环境中使用
    
    Example:
        stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.FG6"
        user_input = "SecurePass123!"
        
        if verify_password(user_input, stored_hash):
            print("密码正确")
        else:
            print("密码错误")
    """
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (ValueError, TypeError):
        # 哈希格式错误或其他异常，返回False
        return False


async def send_welcome_email(user_email: str, user_name: str) -> bool:
    """
    发送欢迎邮件
    
    向新注册的用户发送欢迎邮件，包含账户激活链接和使用指南。
    该函数支持HTML格式邮件，提供良好的用户体验。
    
    Args:
        user_email (str): 用户邮箱地址，必须是有效的邮箱格式
        user_name (str): 用户姓名，用于个性化邮件内容
    
    Returns:
        bool: 邮件发送结果
            - True: 邮件发送成功
            - False: 邮件发送失败
    
    Raises:
        ValueError: 邮箱地址格式不正确
        SMTPException: SMTP服务器连接或发送失败
    
    Email Content:
        - 个性化问候语
        - 账户激活链接（如果需要）
        - 系统使用指南链接
        - 联系方式和技术支持信息
        - 公司品牌信息
    
    Configuration:
        - SMTP服务器配置通过环境变量设置
        - 支持SSL/TLS加密连接
        - 邮件模板支持多语言
        - 发送失败时自动重试3次
    
    Template Variables:
        - {{user_name}}: 用户姓名
        - {{activation_link}}: 激活链接
        - {{support_email}}: 技术支持邮箱
        - {{company_name}}: 公司名称
        - {{current_year}}: 当前年份
    
    Example:
        success = await send_welcome_email(
            user_email="john@example.com",
            user_name="John Doe"
        )
        
        if success:
            logger.info("欢迎邮件发送成功")
        else:
            logger.error("欢迎邮件发送失败")
    """
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, user_email):
        raise ValueError(f"邮箱格式不正确: {user_email}")
    
    try:
        # 获取邮件配置
        smtp_config = get_smtp_config()
        
        # 生成激活链接
        activation_token = generate_activation_token(user_email)
        activation_link = f"{smtp_config.base_url}/activate?token={activation_token}"
        
        # 渲染邮件模板
        email_content = render_email_template('welcome.html', {
            'user_name': user_name,
            'activation_link': activation_link,
            'support_email': smtp_config.support_email,
            'company_name': smtp_config.company_name,
            'current_year': datetime.now().year
        })
        
        # 发送邮件
        await send_email(
            to_email=user_email,
            subject=f"欢迎加入{smtp_config.company_name}",
            html_content=email_content,
            retry_count=3
        )
        
        logger.info(f"欢迎邮件发送成功: {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"欢迎邮件发送失败: {user_email}, 错误: {str(e)}")
        return False
```

## 9. 测试代码注释

### 9.1 单元测试
```python
class TestUserService:
    """
    用户服务单元测试类
    
    测试用户服务的各种业务逻辑，确保功能的正确性和稳定性。
    使用pytest框架和mock技术进行隔离测试。
    
    Test Coverage:
        - 用户创建功能（正常流程和异常情况）
        - 用户查询功能（各种查询条件）
        - 用户更新功能（部分更新和完整更新）
        - 用户删除功能（软删除和权限验证）
        - 权限验证功能（角色权限和直接权限）
        - 异常处理（各种业务异常和系统异常）
    
    Test Data:
        - 使用工厂模式生成测试数据
        - 测试数据与生产数据隔离
        - 每个测试用例使用独立的数据
    
    Mock Strategy:
        - 数据库操作使用mock，避免依赖真实数据库
        - 外部服务（邮件、缓存）使用mock
        - 时间相关功能使用固定时间
    """
    
    @pytest.fixture
    def user_service(self):
        """
        用户服务测试夹具
        
        创建用于测试的用户服务实例，包含所有必要的依赖mock。
        每个测试方法都会获得一个全新的服务实例。
        
        Returns:
            UserService: 配置好的用户服务实例
        """
        # 创建mock依赖
        mock_user_dao = Mock(spec=UserDAO)
        mock_logger = Mock(spec=logging.Logger)
        mock_cache = Mock(spec=CacheService)
        mock_email_service = Mock(spec=EmailService)
        
        # 创建服务实例
        service = UserService(
            user_dao=mock_user_dao,
            logger=mock_logger,
            cache=mock_cache,
            email_service=mock_email_service
        )
        
        return service
    
    @pytest.fixture
    def sample_user_data(self):
        """
        示例用户数据夹具
        
        提供标准的测试用户数据，用于各种测试场景。
        数据符合业务规则和验证要求。
        
        Returns:
            dict: 用户创建请求数据
        """
        return {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'full_name': '测试用户',
            'phone': '13800138000'
        }
    
    async def test_create_user_success(self, user_service, sample_user_data):
        """
        测试用户创建成功场景
        
        验证在正常情况下用户创建功能的正确性，包括：
        - 数据验证通过
        - 密码正确加密
        - 数据库保存成功
        - 欢迎邮件发送
        - 返回正确的用户信息
        
        Test Steps:
            1. 准备有效的用户数据
            2. Mock数据库操作返回成功
            3. Mock邮件服务返回成功
            4. 调用创建用户方法
            5. 验证返回结果
            6. 验证依赖服务的调用
        
        Expected Results:
            - 返回创建的用户信息
            - 密码已加密存储
            - 数据库保存方法被调用
            - 欢迎邮件发送方法被调用
            - 操作日志被记录
        """
        # Arrange - 准备测试数据
        expected_user_id = 123
        user_service.user_dao.create_user.return_value = expected_user_id
        user_service.user_dao.get_user_by_id.return_value = User(
            id=expected_user_id,
            username=sample_user_data['username'],
            email=sample_user_data['email'],
            full_name=sample_user_data['full_name'],
            phone=sample_user_data['phone'],
            status='active'
        )
        user_service.email_service.send_welcome_email.return_value = True
        
        # Act - 执行测试操作
        result = await user_service.create_user(sample_user_data)
        
        # Assert - 验证结果
        assert result is not None
        assert result.id == expected_user_id
        assert result.username == sample_user_data['username']
        assert result.email == sample_user_data['email']
        assert result.status == 'active'
        
        # 验证依赖服务的调用
        user_service.user_dao.create_user.assert_called_once()
        user_service.email_service.send_welcome_email.assert_called_once_with(
            user_email=sample_user_data['email'],
            user_name=sample_user_data['full_name']
        )
        user_service.logger.info.assert_called()
    
    async def test_create_user_duplicate_username(self, user_service, sample_user_data):
        """
        测试用户名重复的异常情况
        
        验证当尝试创建已存在用户名的用户时，系统能正确处理并抛出异常。
        
        Test Scenario:
            - 用户名已存在于系统中
            - 其他数据都是有效的
            - 应该抛出DuplicateUserError异常
        
        Expected Behavior:
            - 抛出DuplicateUserError异常
            - 异常消息包含具体的错误信息
            - 不会调用数据库创建操作
            - 不会发送欢迎邮件
            - 记录警告日志
        """
        # Arrange - 模拟用户名已存在
        user_service.user_dao.get_user_by_username.return_value = User(
            id=1,
            username=sample_user_data['username'],
            email='existing@example.com'
        )
        
        # Act & Assert - 执行操作并验证异常
        with pytest.raises(DuplicateUserError) as exc_info:
            await user_service.create_user(sample_user_data)
        
        # 验证异常信息
        assert "用户名已存在" in str(exc_info.value)
        assert sample_user_data['username'] in str(exc_info.value)
        
        # 验证不会执行后续操作
        user_service.user_dao.create_user.assert_not_called()
        user_service.email_service.send_welcome_email.assert_not_called()
        
        # 验证日志记录
        user_service.logger.warning.assert_called()
    
    @pytest.mark.parametrize("invalid_data,expected_error", [
        # 测试各种无效数据的情况
        ({'username': 'ab'}, "用户名长度不符合要求"),  # 用户名太短
        ({'username': 'a' * 25}, "用户名长度不符合要求"),  # 用户名太长
        ({'email': 'invalid-email'}, "邮箱格式不正确"),  # 邮箱格式错误
        ({'password': '123'}, "密码不符合安全要求"),  # 密码太简单
        ({'full_name': ''}, "姓名不能为空"),  # 姓名为空
        ({'phone': '123'}, "手机号格式不正确"),  # 手机号格式错误
    ])
    async def test_create_user_invalid_data(
        self, 
        user_service, 
        sample_user_data, 
        invalid_data, 
        expected_error
    ):
        """
        测试无效数据的参数化测试
        
        使用参数化测试验证各种无效输入数据的处理情况。
        确保数据验证逻辑的完整性和正确性。
        
        Args:
            invalid_data (dict): 无效的数据字段
            expected_error (str): 期望的错误消息关键词
        
        Test Strategy:
            - 使用pytest.mark.parametrize装饰器
            - 覆盖所有可能的无效数据情况
            - 验证每种情况都能正确抛出异常
            - 确保错误消息准确描述问题
        """
        # Arrange - 准备无效数据
        test_data = {**sample_user_data, **invalid_data}
        
        # Act & Assert - 执行操作并验证异常
        with pytest.raises(ValidationError) as exc_info:
            await user_service.create_user(test_data)
        
        # 验证异常消息包含期望的错误信息
        assert expected_error in str(exc_info.value)
        
        # 验证不会执行数据库操作
        user_service.user_dao.create_user.assert_not_called()
```

## 10. 日志和监控注释

### 10.1 日志配置
```python
def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    配置应用日志系统
    
    设置统一的日志格式、级别和输出目标。
    支持控制台输出和文件输出，便于开发和生产环境使用。
    
    Args:
        log_level (str): 日志级别，支持DEBUG、INFO、WARNING、ERROR、CRITICAL
        log_file (str, optional): 日志文件路径，如果不指定则只输出到控制台
    
    Returns:
        logging.Logger: 配置好的日志记录器
    
    Log Format:
        时间戳 - 模块名 - 日志级别 - 消息内容 - [请求ID] - [用户ID]
        
        Example:
        2024-01-15 10:30:00,123 - user_service - INFO - 用户创建成功 - [req-123] - [user-456]
    
    Log Levels:
        - DEBUG: 详细的调试信息，仅在开发环境使用
        - INFO: 一般信息，记录重要的业务操作
        - WARNING: 警告信息，记录可能的问题但不影响功能
        - ERROR: 错误信息，记录业务异常和系统错误
        - CRITICAL: 严重错误，记录系统崩溃级别的问题
    
    Log Rotation:
        - 日志文件大小限制：100MB
        - 保留历史文件数量：10个
        - 自动压缩历史文件
        - 按日期和大小轮转
    
    Security:
        - 自动脱敏敏感信息（密码、令牌等）
        - 记录用户操作审计日志
        - 支持日志加密存储
    
    Performance:
        - 异步日志写入，不阻塞主线程
        - 批量写入优化性能
        - 内存缓冲区大小：1MB
    
    Example:
        # 开发环境配置
        logger = setup_logging(log_level="DEBUG")
        
        # 生产环境配置
        logger = setup_logging(
            log_level="INFO",
            log_file="/var/log/auto-test/app.log"
        )
        
        # 使用日志记录器
        logger.info("应用启动成功", extra={
            "request_id": "req-123",
            "user_id": "user-456"
        })
    """
    # 创建日志记录器
    logger = logging.getLogger('auto_test')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器，避免重复配置
    logger.handlers.clear()
    
    # 定义日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(request_id)s] - [%(user_id)s]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())  # 添加敏感数据过滤器
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建轮转文件处理器
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(file_handler)
    
    return logger


class SensitiveDataFilter(logging.Filter):
    """
    敏感数据过滤器
    
    自动检测和脱敏日志中的敏感信息，防止敏感数据泄露。
    支持多种敏感数据类型的识别和脱敏处理。
    
    Sensitive Data Types:
        - 密码字段：password, passwd, pwd
        - 令牌字段：token, access_token, refresh_token
        - 密钥字段：key, secret, api_key
        - 身份证号：18位数字
        - 手机号：11位数字
        - 邮箱地址：部分脱敏
    
    Masking Rules:
        - 短字符串（<8字符）：完全替换为***
        - 长字符串（>=8字符）：保留前2位和后2位，中间替换为***
        - 数字：保留前3位和后4位，中间替换为***
        - 邮箱：保留用户名首字母和域名，其他替换为***
    """
    
    # 敏感字段名称模式
    SENSITIVE_PATTERNS = [
        r'password', r'passwd', r'pwd',
        r'token', r'access_token', r'refresh_token',
        r'key', r'secret', r'api_key',
        r'authorization'
    ]
    
    def filter(self, record):
        """过滤敏感数据"""
        if hasattr(record, 'msg'):
            record.msg = self._mask_sensitive_data(str(record.msg))
        return True
    
    def _mask_sensitive_data(self, message: str) -> str:
        """脱敏敏感数据"""
        # 实现脱敏逻辑
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(
                rf'{pattern}["\']?\s*[:=]\s*["\']?([^"\'\s,}}]+)',
                rf'{pattern}: ***',
                message,
                flags=re.IGNORECASE
            )
        return message


## 11. 性能优化注释

### 11.1 缓存策略注释
```python
@lru_cache(maxsize=1000)
def get_user_permissions_cached(user_id: int) -> List[str]:
    """
    获取用户权限（带缓存）
    
    使用LRU缓存优化用户权限查询性能。
    权限数据变化不频繁，适合缓存优化。
    
    Cache Strategy:
        - 缓存大小：1000个用户
        - 缓存算法：LRU（最近最少使用）
        - 缓存时效：通过版本号控制
        - 缓存失效：用户权限变更时清除
    
    Performance Benefits:
        - 减少数据库查询次数
        - 提高权限验证速度
        - 降低数据库负载
        - 改善用户体验
    
    Memory Usage:
        - 每个缓存项约1KB
        - 最大内存占用约1MB
        - 自动清理过期数据
    """
    pass


async def batch_update_users(user_updates: List[Dict]) -> List[int]:
    """
    批量更新用户信息
    
    使用批量操作优化大量用户数据更新的性能。
    减少数据库连接次数和事务开销。
    
    Performance Optimization:
        - 批量SQL操作，减少网络往返
        - 单个事务处理，保证数据一致性
        - 预编译SQL语句，提高执行效率
        - 分批处理，避免内存溢出
    
    Batch Size:
        - 默认批次大小：100条记录
        - 最大批次大小：1000条记录
        - 根据数据大小自动调整
    
    Error Handling:
        - 部分失败时回滚整个批次
        - 记录失败的具体记录
        - 支持重试机制
    
    Example:
        updates = [
            {"id": 1, "status": "active"},
            {"id": 2, "status": "inactive"},
            # ... 更多更新数据
        ]
        updated_ids = await batch_update_users(updates)
    """
    pass
```

## 12. 安全相关注释

### 12.1 权限验证注释
```python
def require_permissions(*permissions: str):
    """
    权限验证装饰器
    
    验证当前用户是否具有指定权限，用于保护需要特定权限的API接口。
    支持多权限验证和权限继承。
    
    Args:
        *permissions: 所需权限列表，格式为'resource:action'
    
    Security Features:
        - JWT令牌验证
        - 权限层级验证
        - 会话有效性检查
        - 防止权限提升攻击
    
    Usage:
        @require_permissions('user:create', 'user:update')
        async def create_user_endpoint():
            pass
    """
    pass


async def validate_input_data(data: dict, schema: dict) -> dict:
    """
    输入数据验证和清理
    
    验证和清理用户输入数据，防止注入攻击和数据污染。
    使用白名单策略，只允许预期的数据字段。
    
    Security Measures:
        - SQL注入防护
        - XSS攻击防护
        - 数据类型验证
        - 长度限制检查
        - 特殊字符过滤
    
    Validation Rules:
        - 字符串：长度限制、格式验证、特殊字符过滤
        - 数字：范围验证、类型转换
        - 邮箱：格式验证、域名白名单
        - 文件：类型验证、大小限制、病毒扫描
    
    Example:
        schema = {
            'username': {'type': 'string', 'min_length': 3, 'max_length': 20},
            'email': {'type': 'email', 'required': True},
            'age': {'type': 'integer', 'min': 0, 'max': 150}
        }
        
        clean_data = await validate_input_data(user_input, schema)
    """
    pass
```

## 13. 部署和运维注释

### 13.1 健康检查注释
```python
@router.get("/health")
async def health_check() -> dict:
    """
    系统健康检查接口
    
    检查系统各组件的运行状态，用于负载均衡器和监控系统。
    返回详细的健康状态信息，便于问题诊断。
    
    Check Items:
        - 数据库连接状态
        - 缓存服务状态
        - 外部API连接状态
        - 磁盘空间使用情况
        - 内存使用情况
        - CPU负载情况
    
    Response Format:
        {
            "status": "healthy|degraded|unhealthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "version": "1.0.0",
            "uptime": 3600,
            "checks": {
                "database": {"status": "healthy", "response_time": 10},
                "cache": {"status": "healthy", "response_time": 5},
                "disk": {"status": "healthy", "usage": "45%"},
                "memory": {"status": "healthy", "usage": "60%"}
            }
        }
    
    Status Levels:
        - healthy: 所有组件正常
        - degraded: 部分组件异常但不影响核心功能
        - unhealthy: 核心组件异常，服务不可用
    
    Monitoring Integration:
        - Prometheus指标导出
        - 告警规则配置
        - 日志聚合
        - 性能指标收集
    """
    pass
```

## 14. 注释维护和审查

### 14.1 注释质量检查清单
```python
"""
注释质量检查清单

文件级注释：
□ 包含文件用途说明
□ 列出主要功能特性
□ 说明依赖关系
□ 包含作者和版本信息
□ 说明业务规则

类注释：
□ 说明类的职责和用途
□ 列出主要方法和属性
□ 说明设计模式和架构
□ 包含使用示例
□ 说明异常处理策略

方法注释：
□ 使用标准docstring格式
□ 包含参数说明和类型
□ 包含返回值说明
□ 列出可能的异常
□ 包含使用示例
□ 说明业务逻辑
□ 说明性能考虑
□ 说明安全注意事项

代码注释：
□ 解释复杂的业务逻辑
□ 说明算法实现思路
□ 标注性能优化点
□ 说明安全考虑
□ 标注TODO和FIXME
□ 解释魔法数字和常量

注释维护：
□ 代码变更时同步更新注释
□ 删除过时和无用注释
□ 保持注释与代码一致
□ 定期审查注释质量
□ 使用工具检查注释覆盖率
"""
```

这个后端注释规范涵盖了Python后端开发的各个方面，将帮助团队编写高质量、易维护的后端代码。