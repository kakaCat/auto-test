# 后端编程流程指南

## 概述

本文档详细描述了后端开发的标准编程流程，采用 **API → Service → Transform → DAO** 的分层架构，确保代码的可维护性、可测试性和可扩展性。

## 核心理念

### 函数式编程思想
- **数据转换**：采用函数式编程风格，通过纯函数进行数据转换
- **不可变性**：数据在转换过程中保持不可变，避免副作用
- **组合性**：通过函数组合实现复杂的数据处理逻辑
- **可预测性**：相同输入始终产生相同输出

### 分层职责
1. **API层**：接收请求，调用Service层，返回响应
2. **Service层**：处理业务逻辑，调用DAO获取数据，使用Transform转换数据
3. **Transform层**：纯函数式数据转换，将原始数据转换为响应格式
4. **DAO层**：封装数据访问逻辑，提供数据查询接口

## 编程流程详解

### 第一步：API层接收请求

```python
# api/systems.py
@router.get("/systems", response_model=List[SystemResponse])
async def get_systems(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """获取系统列表"""
    try:
        # 调用Service层处理业务逻辑
        systems = SystemService.get_systems(skip=skip, limit=limit)
        return systems
    except Exception as e:
        logger.error(f"获取系统列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统列表失败")
```

**API层职责：**
- 参数验证和类型转换
- 调用对应的Service方法
- 异常处理和错误响应
- 返回标准化的HTTP响应

### 第二步：Service层处理业务逻辑

```python
# services/system_service.py
class SystemService:
    @staticmethod
    def get_systems(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取系统列表"""
        try:
            # 1. 调用DAO层获取原始数据
            raw_systems = SystemDAO.get_all(skip=skip, limit=limit)
            
            # 2. 使用Transform层转换数据
            transformed_systems = SystemTransform.to_list_response(raw_systems)
            
            # 3. 应用业务规则
            processed_systems = []
            for system in transformed_systems:
                # 添加模块数量统计
                module_count = ModuleDAO.count_by_system_id(system['id'])
                system_with_count = SystemTransform.with_module_count(system, module_count)
                
                # 应用业务规则
                final_system = cls._apply_business_rules(system_with_count)
                processed_systems.append(final_system)
            
            return processed_systems
            
        except Exception as e:
            logger.error(f"获取系统列表失败: {e}")
            raise
```

**Service层职责：**
- 协调DAO层和Transform层
- 实现复杂的业务逻辑
- 处理多个数据源的组合
- 应用业务规则和验证
- 记录业务日志

### 第三步：Transform层数据转换

```python
# transforms/system_transform.py
class SystemTransform:
    """系统数据转换器 - 采用函数式编程风格"""
    
    @classmethod
    def to_response(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """将原始系统数据转换为API响应格式"""
        return pipe(
            raw_data,
            cls._add_business_fields,
            cls._format_timestamps,
            cls._add_status_display,
            cls._add_computed_fields
        )
    
    @classmethod
    def to_list_response(cls, raw_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量转换系统数据"""
        return [cls.to_response(item) for item in raw_list]
    
    @classmethod
    def with_module_count(cls, system: Dict[str, Any], module_count: int) -> Dict[str, Any]:
        """添加模块数量信息"""
        return add_field(system, 'module_count', module_count)
    
    @classmethod
    def _add_business_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """添加业务字段"""
        return pipe(
            data,
            lambda d: add_field(d, 'display_name', cls._generate_display_name(d)),
            lambda d: add_field(d, 'system_type', cls._infer_system_type(d)),
            lambda d: add_field(d, 'priority_level', cls._calculate_priority(d))
        )
```

**Transform层职责：**
- 纯函数式数据转换
- 格式化时间戳、枚举值等
- 添加计算字段和业务字段
- 数据结构重组和优化
- 保持数据不可变性

### 第四步：DAO层数据访问

```python
# database/dao.py
class SystemDAO:
    """系统数据访问对象"""
    
    @staticmethod
    def get_all(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有系统"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, version, status, 
                           created_at, updated_at, config_data
                    FROM systems 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, skip))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"查询系统数据失败: {e}")
            raise
```

**DAO层职责：**
- 封装数据库查询逻辑
- 提供标准化的数据访问接口
- 处理数据库连接和事务
- 返回原始的字典格式数据
- 记录数据访问日志

## 数据流转示例

### 完整的数据流转过程

```
1. 客户端请求
   GET /api/systems?skip=0&limit=10

2. API层处理
   ↓ 参数验证：skip=0, limit=10
   ↓ 调用：SystemService.get_systems(skip=0, limit=10)

3. Service层协调
   ↓ 调用：SystemDAO.get_all(skip=0, limit=10)
   ↓ 获得：原始数据库记录列表
   ↓ 调用：SystemTransform.to_list_response(raw_systems)
   ↓ 获得：转换后的基础响应数据
   ↓ 循环处理每个系统：
     - 调用：ModuleDAO.count_by_system_id(system_id)
     - 调用：SystemTransform.with_module_count(system, count)
     - 调用：SystemService._apply_business_rules(system)
   ↓ 返回：最终的业务数据列表

4. Transform层转换
   ↓ 原始数据：{"id": 1, "name": "sys1", "created_at": "2024-01-01 10:00:00"}
   ↓ 转换过程：
     - _add_business_fields: 添加 display_name, system_type, priority_level
     - _format_timestamps: 格式化时间为 ISO 格式
     - _add_status_display: 添加状态显示文本
     - _add_computed_fields: 添加计算字段
   ↓ 转换结果：{
       "id": 1,
       "name": "sys1",
       "display_name": "系统1",
       "system_type": "web",
       "priority_level": "high",
       "created_at": "2024-01-01T10:00:00Z",
       "status_display": "运行中",
       "module_count": 5,
       "importance_level": "critical"
     }

5. API层响应
   ↓ HTTP 200 OK
   ↓ Content-Type: application/json
   ↓ Body: [转换后的系统列表]
```

## 编程规范

### 1. 命名规范

```python
# API层：动词 + 名词
async def get_systems()
async def create_system()
async def update_system()

# Service层：动词 + 名词
def get_systems()
def create_system()
def validate_system_data()

# Transform层：to_ + 目标格式
def to_response()
def to_list_response()
def to_summary()

# DAO层：动词 + 名词
def get_all()
def get_by_id()
def create()
def update()
```

### 2. 错误处理

```python
# Service层错误处理
try:
    raw_data = SystemDAO.get_by_id(system_id)
    if not raw_data:
        raise ValueError(f"系统不存在: {system_id}")
    
    transformed_data = SystemTransform.to_response(raw_data)
    return cls._apply_business_rules(transformed_data)
    
except ValueError as e:
    logger.warning(f"业务逻辑错误: {e}")
    raise
except Exception as e:
    logger.error(f"系统错误: {e}")
    raise RuntimeError(f"获取系统失败: {system_id}")
```

### 3. 日志记录

```python
# 每层都应该记录适当的日志
logger.info(f"开始处理系统查询请求: skip={skip}, limit={limit}")
logger.debug(f"原始数据: {raw_data}")
logger.info(f"成功转换 {len(systems)} 个系统数据")
```

## 最佳实践

### 1. Transform层设计原则

```python
# ✅ 好的做法：纯函数，无副作用
@classmethod
def _format_timestamp(cls, data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化时间戳"""
    if 'created_at' in data and data['created_at']:
        formatted_time = format_datetime(data['created_at'])
        return add_field(data, 'created_at', formatted_time)
    return data

# ❌ 避免的做法：修改原始数据
@classmethod
def _format_timestamp_bad(cls, data: Dict[str, Any]) -> Dict[str, Any]:
    data['created_at'] = format_datetime(data['created_at'])  # 修改了原始数据
    return data
```

### 2. Service层业务逻辑组织

```python
# ✅ 好的做法：清晰的步骤分离
def get_systems(cls, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    # 步骤1：获取原始数据
    raw_systems = SystemDAO.get_all(skip=skip, limit=limit)
    
    # 步骤2：基础数据转换
    transformed_systems = SystemTransform.to_list_response(raw_systems)
    
    # 步骤3：业务逻辑处理
    return [cls._apply_business_rules(system) for system in transformed_systems]
```

### 3. 函数组合使用

```python
# 使用 pipe 函数进行数据转换
def to_response(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    return pipe(
        raw_data,
        cls._add_business_fields,      # 添加业务字段
        cls._format_timestamps,        # 格式化时间
        cls._add_status_display,       # 添加状态显示
        cls._add_computed_fields       # 添加计算字段
    )
```

## 总结

这个编程流程确保了：

1. **清晰的职责分离**：每层都有明确的职责
2. **函数式编程**：Transform层采用纯函数，易于测试和维护
3. **数据流向清晰**：API → Service → Transform → DAO
4. **易于扩展**：新增功能只需在对应层添加代码
5. **高可测试性**：每层都可以独立测试
6. **统一的编码风格**：遵循一致的命名和结构规范

通过遵循这个流程，可以确保后端代码的质量和可维护性，同时提高开发效率。