# 后端架构示例和模板代码

## 概述

本文档提供了基于 API-Service-Transform-DAO 分层架构的完整示例和模板代码，帮助开发者快速理解和实现新功能。

## 架构层次说明

```
┌─────────────────┐
│   API Layer     │  ← 处理HTTP请求/响应，参数验证
├─────────────────┤
│ Service Layer   │  ← 业务逻辑，规则验证，流程控制
├─────────────────┤
│Transform Layer  │  ← 数据转换，格式化，增强
├─────────────────┤
│   DAO Layer     │  ← 数据访问，数据库操作
└─────────────────┘
```

## 完整示例：用户管理功能

### 1. 数据模型定义 (models/user.py)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """用户基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="用户名")
    email: str = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(None, description="手机号码")
    department: Optional[str] = Field(None, description="部门")

class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=6, description="密码")

class UserUpdate(BaseModel):
    """更新用户模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(active|inactive|suspended)$")

class User(UserBase):
    """用户完整模型"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 2. DAO层实现 (database/dao.py)

```python
import logging
from typing import List, Dict, Any, Optional
from .connection import get_db_cursor

logger = logging.getLogger(__name__)

class UserDAO:
    """用户数据访问对象"""
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """获取所有用户"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.name, u.email, u.phone, u.department, 
                           u.status, u.created_at, u.updated_at,
                           d.name as department_name
                    FROM users u
                    LEFT JOIN departments d ON u.department = d.code
                    ORDER BY u.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.name, u.email, u.phone, u.department,
                           u.status, u.created_at, u.updated_at,
                           d.name as department_name
                    FROM users u
                    LEFT JOIN departments d ON u.department = d.code
                    WHERE u.id = ?
                """, (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取用户详情失败: {e}")
            raise
    
    @staticmethod
    def create(name: str, email: str, password_hash: str, 
               phone: str = None, department: str = None) -> int:
        """创建用户"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, phone, department) 
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, password_hash, phone, department))
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            raise
    
    @staticmethod
    def update(user_id: int, name: str = None, email: str = None,
               phone: str = None, department: str = None, status: str = None) -> bool:
        """更新用户"""
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if email is not None:
                updates.append("email = ?")
                params.append(email)
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone)
            if department is not None:
                updates.append("department = ?")
                params.append(department)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            with get_db_cursor() as cursor:
                cursor.execute(f"""
                    UPDATE users 
                    SET {', '.join(updates)} 
                    WHERE id = ?
                """, params)
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            raise
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            raise
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"根据邮箱获取用户失败: {e}")
            raise
    
    @staticmethod
    def count_by_department(department: str) -> int:
        """统计部门用户数量"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE department = ?", (department,))
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"统计部门用户数量失败: {e}")
            raise
```

### 3. Transform层实现 (transforms/user_transform.py)

```python
from typing import Dict, Any, List
from datetime import datetime
from ..utils.datetime_utils import format_datetime, calculate_days_ago

class UserTransform:
    """用户数据转换器"""
    
    @staticmethod
    def enhance_user_data(user: Dict[str, Any]) -> Dict[str, Any]:
        """增强用户数据"""
        enhanced = user.copy()
        
        # 时间格式化
        enhanced.update(UserTransform._format_timestamps(user))
        
        # 状态显示
        enhanced.update(UserTransform._add_status_display(user))
        
        # 联系信息处理
        enhanced.update(UserTransform._process_contact_info(user))
        
        # 部门信息
        enhanced.update(UserTransform._add_department_info(user))
        
        # 用户统计信息
        enhanced.update(UserTransform._add_user_stats(user))
        
        return enhanced
    
    @staticmethod
    def _format_timestamps(user: Dict[str, Any]) -> Dict[str, Any]:
        """格式化时间戳"""
        return {
            'created_at_formatted': format_datetime(user.get('created_at')),
            'updated_at_formatted': format_datetime(user.get('updated_at')),
            'created_date': user.get('created_at', '').split(' ')[0] if user.get('created_at') else '',
            'updated_date': user.get('updated_at', '').split(' ')[0] if user.get('updated_at') else '',
            'user_age_days': calculate_days_ago(user.get('created_at')),
            'user_age_display': UserTransform._get_age_display(user.get('created_at'))
        }
    
    @staticmethod
    def _add_status_display(user: Dict[str, Any]) -> Dict[str, Any]:
        """添加状态显示信息"""
        status = user.get('status', 'active')
        status_map = {
            'active': {'display': '活跃', 'color': 'success', 'icon': 'check-circle'},
            'inactive': {'display': '非活跃', 'color': 'warning', 'icon': 'pause-circle'},
            'suspended': {'display': '已暂停', 'color': 'danger', 'icon': 'x-circle'}
        }
        
        status_info = status_map.get(status, status_map['active'])
        return {
            'status_display': status_info['display'],
            'status_color': status_info['color'],
            'status_icon': status_info['icon']
        }
    
    @staticmethod
    def _process_contact_info(user: Dict[str, Any]) -> Dict[str, Any]:
        """处理联系信息"""
        email = user.get('email', '')
        phone = user.get('phone', '')
        
        return {
            'has_email': bool(email),
            'has_phone': bool(phone),
            'email_domain': email.split('@')[1] if '@' in email else '',
            'phone_formatted': UserTransform._format_phone(phone),
            'contact_methods': UserTransform._get_contact_methods(email, phone)
        }
    
    @staticmethod
    def _add_department_info(user: Dict[str, Any]) -> Dict[str, Any]:
        """添加部门信息"""
        department = user.get('department', '')
        department_name = user.get('department_name', '')
        
        return {
            'has_department': bool(department),
            'department_display': department_name or department or '未分配',
            'department_code': department
        }
    
    @staticmethod
    def _add_user_stats(user: Dict[str, Any]) -> Dict[str, Any]:
        """添加用户统计信息"""
        name = user.get('name', '')
        
        return {
            'name_length': len(name),
            'user_key': f"{user.get('id', 0)}_{name.replace(' ', '_').lower()}",
            'search_keywords': UserTransform._generate_search_keywords(user)
        }
    
    @staticmethod
    def _format_phone(phone: str) -> str:
        """格式化手机号"""
        if not phone:
            return ''
        
        # 简单的手机号格式化
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) == 11:
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        return phone
    
    @staticmethod
    def _get_contact_methods(email: str, phone: str) -> List[str]:
        """获取联系方式列表"""
        methods = []
        if email:
            methods.append('email')
        if phone:
            methods.append('phone')
        return methods
    
    @staticmethod
    def _get_age_display(created_at: str) -> str:
        """获取用户年龄显示"""
        if not created_at:
            return '未知'
        
        days = calculate_days_ago(created_at)
        if days == 0:
            return '今天'
        elif days == 1:
            return '昨天'
        elif days < 7:
            return f'{days}天前'
        elif days < 30:
            return f'{days // 7}周前'
        elif days < 365:
            return f'{days // 30}个月前'
        else:
            return f'{days // 365}年前'
    
    @staticmethod
    def _generate_search_keywords(user: Dict[str, Any]) -> List[str]:
        """生成搜索关键词"""
        keywords = []
        
        # 基本信息
        if user.get('name'):
            keywords.append(user['name'])
        if user.get('email'):
            keywords.append(user['email'])
        if user.get('department_name'):
            keywords.append(user['department_name'])
        if user.get('status'):
            keywords.append(user['status'])
        
        return keywords
```

### 4. Service层实现 (services/user_service.py)

```python
import logging
import hashlib
from typing import List, Dict, Any, Optional
from ..database.dao import UserDAO
from ..models.user import UserCreate, UserUpdate
from ..transforms.user_transform import UserTransform

logger = logging.getLogger(__name__)

class UserService:
    """用户业务服务"""
    
    @staticmethod
    def get_users() -> List[Dict[str, Any]]:
        """
        获取用户列表
        
        Returns:
            List[Dict[str, Any]]: 用户列表，包含业务转换后的数据
        """
        try:
            raw_users = UserDAO.get_all()
            
            # 应用数据转换和业务规则
            enhanced_users = []
            for user in raw_users:
                enhanced_user = UserTransform.enhance_user_data(user)
                enhanced_user = UserService._apply_business_rules(enhanced_user)
                enhanced_users.append(enhanced_user)
            
            logger.info(f"获取用户列表成功，共 {len(enhanced_users)} 个用户")
            return enhanced_users
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取用户详情
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户详情，包含业务转换后的数据
        """
        try:
            user = UserDAO.get_by_id(user_id)
            if user:
                enhanced_user = UserTransform.enhance_user_data(user)
                return UserService._apply_business_rules(enhanced_user)
            return None
        except Exception as e:
            logger.error(f"获取用户详情失败: {str(e)}")
            raise
    
    @staticmethod
    def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """
        创建新用户
        
        Args:
            user_data (UserCreate): 用户创建数据
            
        Returns:
            Dict[str, Any]: 创建的用户信息
        """
        try:
            # 业务规则验证
            if UserService._is_email_exists(user_data.email):
                raise ValueError(f"邮箱 '{user_data.email}' 已存在")
            
            # 密码加密
            password_hash = UserService._hash_password(user_data.password)
            
            # 创建用户
            user_id = UserDAO.create(
                user_data.name,
                user_data.email,
                password_hash,
                user_data.phone,
                user_data.department
            )
            
            created_user = UserDAO.get_by_id(user_id)
            enhanced_user = UserTransform.enhance_user_data(created_user)
            
            logger.info(f"用户创建成功: {user_data.name} (ID: {user_id})")
            return UserService._apply_business_rules(enhanced_user)
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """
        更新用户信息
        
        Args:
            user_id (int): 用户ID
            user_data (UserUpdate): 用户更新数据
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的用户信息
        """
        try:
            # 检查用户是否存在
            existing_user = UserDAO.get_by_id(user_id)
            if not existing_user:
                raise ValueError(f"用户ID {user_id} 不存在")
            
            # 邮箱唯一性检查
            if user_data.email and user_data.email != existing_user['email']:
                if UserService._is_email_exists(user_data.email):
                    raise ValueError(f"邮箱 '{user_data.email}' 已存在")
            
            # 更新用户
            success = UserDAO.update(
                user_id,
                user_data.name,
                user_data.email,
                user_data.phone,
                user_data.department,
                user_data.status
            )
            
            if success:
                updated_user = UserDAO.get_by_id(user_id)
                enhanced_user = UserTransform.enhance_user_data(updated_user)
                logger.info(f"用户更新成功: ID {user_id}")
                return UserService._apply_business_rules(enhanced_user)
            
            return None
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查用户是否存在
            existing_user = UserDAO.get_by_id(user_id)
            if not existing_user:
                raise ValueError(f"用户ID {user_id} 不存在")
            
            # 业务规则检查：不能删除管理员用户
            if existing_user.get('department') == 'admin':
                raise ValueError("不能删除管理员用户")
            
            success = UserDAO.delete(user_id)
            if success:
                logger.info(f"用户删除成功: ID {user_id}")
            
            return success
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            raise
    
    @staticmethod
    def _apply_business_rules(user: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用业务规则和验证
        
        Args:
            user (Dict[str, Any]): 转换后的用户数据
            
        Returns:
            Dict[str, Any]: 应用业务规则后的用户数据
        """
        enhanced = user.copy()
        
        # 业务规则1: 权限检查
        enhanced['can_edit'] = enhanced.get('status') != 'suspended'
        enhanced['can_delete'] = enhanced.get('department') != 'admin'
        
        # 业务规则2: 安全等级评估
        enhanced['security_level'] = UserService._assess_security_level(enhanced)
        
        # 业务规则3: 活跃度评估
        enhanced['activity_score'] = UserService._calculate_activity_score(enhanced)
        
        return enhanced
    
    @staticmethod
    def _assess_security_level(user: Dict[str, Any]) -> str:
        """评估用户安全等级"""
        score = 0
        
        # 基于部门评估
        if user.get('department') == 'admin':
            score += 3
        elif user.get('department') in ['security', 'finance']:
            score += 2
        else:
            score += 1
        
        # 基于联系方式完整性
        if user.get('has_email') and user.get('has_phone'):
            score += 1
        
        if score >= 4:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _calculate_activity_score(user: Dict[str, Any]) -> int:
        """计算用户活跃度分数"""
        score = 50  # 基础分数
        
        # 基于状态
        status = user.get('status', 'active')
        if status == 'active':
            score += 30
        elif status == 'inactive':
            score += 10
        
        # 基于注册时间
        age_days = user.get('user_age_days', 0)
        if age_days < 30:
            score += 20  # 新用户加分
        elif age_days > 365:
            score += 10  # 老用户加分
        
        return min(100, max(0, score))
    
    @staticmethod
    def _is_email_exists(email: str) -> bool:
        """检查邮箱是否已存在"""
        try:
            existing_user = UserDAO.get_by_email(email)
            return existing_user is not None
        except Exception:
            return False
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()
```

### 5. API层实现 (api/users.py)

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from ..models.user import User, UserCreate, UserUpdate
from ..services.user_service import UserService
from ..utils.response import success_response, error_response

logger = logging.getLogger(__name__)
router = APIRouter(tags=["用户管理"])

@router.get("/", response_model=dict)
async def get_users(
    department: Optional[str] = Query(None, description="部门筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """
    获取用户列表
    
    - **department**: 按部门筛选
    - **status**: 按状态筛选  
    - **limit**: 返回数量限制
    """
    try:
        users = UserService.get_users()
        
        # 应用筛选条件
        if department:
            users = [u for u in users if u.get('department') == department]
        if status:
            users = [u for u in users if u.get('status') == status]
        
        # 应用数量限制
        users = users[:limit]
        
        return success_response(
            data=users,
            message=f"获取用户列表成功，共 {len(users)} 个用户"
        )
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        return error_response(
            message=f"获取用户列表失败: {str(e)}",
            code=500
        )

@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int):
    """
    获取用户详情
    
    - **user_id**: 用户ID
    """
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return success_response(
            data=user,
            message="获取用户详情成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详情失败: {str(e)}")
        return error_response(
            message=f"获取用户详情失败: {str(e)}",
            code=500
        )

@router.post("/", response_model=dict)
async def create_user(user_data: UserCreate):
    """
    创建新用户
    
    - **name**: 用户名（必填）
    - **email**: 邮箱地址（必填）
    - **password**: 密码（必填，最少6位）
    - **phone**: 手机号码（可选）
    - **department**: 部门（可选）
    """
    try:
        user = UserService.create_user(user_data)
        return success_response(
            data=user,
            message="创建用户成功"
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        return error_response(
            message=f"创建用户失败: {str(e)}",
            code=500
        )

@router.put("/{user_id}", response_model=dict)
async def update_user(user_id: int, user_data: UserUpdate):
    """
    更新用户信息
    
    - **user_id**: 用户ID
    - **name**: 用户名（可选）
    - **email**: 邮箱地址（可选）
    - **phone**: 手机号码（可选）
    - **department**: 部门（可选）
    - **status**: 状态（可选：active/inactive/suspended）
    """
    try:
        user = UserService.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在或更新失败")
        
        return success_response(
            data=user,
            message="更新用户成功"
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            code=400
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败: {str(e)}")
        return error_response(
            message=f"更新用户失败: {str(e)}",
            code=500
        )

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    """
    删除用户
    
    - **user_id**: 用户ID
    """
    try:
        success = UserService.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="用户不存在或删除失败")
        
        return success_response(
            message="删除用户成功"
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            code=400
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        return error_response(
            message=f"删除用户失败: {str(e)}",
            code=500
        )

@router.get("/{user_id}/stats", response_model=dict)
async def get_user_stats(user_id: int):
    """
    获取用户统计信息
    
    - **user_id**: 用户ID
    """
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 提取统计信息
        stats = {
            'activity_score': user.get('activity_score', 0),
            'security_level': user.get('security_level', 'low'),
            'user_age_days': user.get('user_age_days', 0),
            'contact_methods': user.get('contact_methods', []),
            'department_info': {
                'code': user.get('department_code', ''),
                'name': user.get('department_display', ''),
                'has_department': user.get('has_department', False)
            }
        }
        
        return success_response(
            data=stats,
            message="获取用户统计信息成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户统计信息失败: {str(e)}")
        return error_response(
            message=f"获取用户统计信息失败: {str(e)}",
            code=500
        )
```

## 开发模板

### 新功能开发步骤

1. **定义数据模型** (models/)
2. **实现DAO层** (database/dao.py)
3. **创建Transform层** (transforms/)
4. **编写Service层** (services/)
5. **实现API层** (api/)
6. **注册路由** (main.py)

### 代码模板

#### DAO方法模板

```python
@staticmethod
def method_name(param: type) -> return_type:
    """方法描述"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SQL语句", (param,))
            # 处理结果
            return result
    except Exception as e:
        logger.error(f"操作失败: {e}")
        raise
```

#### Service方法模板

```python
@staticmethod
def method_name(param: type) -> return_type:
    """
    方法描述
    
    Args:
        param (type): 参数描述
        
    Returns:
        return_type: 返回值描述
    """
    try:
        # 业务逻辑
        raw_data = DAO.method(param)
        enhanced_data = Transform.enhance(raw_data)
        result = Service._apply_business_rules(enhanced_data)
        
        logger.info(f"操作成功")
        return result
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        raise
```

#### API端点模板

```python
@router.method("/path", response_model=dict)
async def endpoint_name(param: type):
    """
    端点描述
    
    - **param**: 参数描述
    """
    try:
        result = Service.method(param)
        return success_response(
            data=result,
            message="操作成功"
        )
    except ValueError as e:
        return error_response(message=str(e), code=400)
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        return error_response(
            message=f"操作失败: {str(e)}",
            code=500
        )
```

## 最佳实践

### 1. 错误处理
- DAO层：记录错误并重新抛出
- Service层：业务逻辑验证，记录操作日志
- API层：统一错误响应格式

### 2. 日志记录
- 关键操作记录INFO级别日志
- 错误记录ERROR级别日志
- 包含足够的上下文信息

### 3. 数据验证
- 模型层：使用Pydantic进行数据验证
- Service层：业务规则验证
- API层：参数验证和权限检查

### 4. 性能优化
- 使用数据库连接池
- 避免N+1查询问题
- 合理使用索引

### 5. 安全考虑
- 密码加密存储
- SQL注入防护
- 输入数据清理
- 权限验证

这个架构示例展示了如何构建可维护、可扩展的后端服务，每一层都有明确的职责，便于测试和维护。