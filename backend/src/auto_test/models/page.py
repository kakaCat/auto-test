"""
页面管理数据模型
Page Management Data Models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class PageBase(BaseModel):
    """页面基础模型"""
    name: str = Field(..., description="页面名称", max_length=100)
    description: Optional[str] = Field(None, description="页面描述")
    route_path: Optional[str] = Field(None, description="路由路径", max_length=200)
    page_type: str = Field("page", description="页面类型：page, modal, drawer等")
    status: str = Field("active", description="状态：active, inactive, draft")


class PageCreate(PageBase):
    """创建页面模型"""
    system_id: int = Field(..., description="所属系统ID")

    @field_validator('system_id', mode='before')
    @staticmethod
    def _validate_system_id_create(v):
        if v is None:
            raise ValueError('system_id不能为空')
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.isdigit():
                return int(s)
        raise ValueError('system_id必须为数字类型')


class PageUpdate(BaseModel):
    """更新页面模型"""
    name: Optional[str] = Field(None, description="页面名称", max_length=100)
    description: Optional[str] = Field(None, description="页面描述")
    route_path: Optional[str] = Field(None, description="路由路径", max_length=200)
    page_type: Optional[str] = Field(None, description="页面类型")
    status: Optional[str] = Field(None, description="状态")


class Page(PageBase):
    """页面模型"""
    id: int = Field(..., description="页面ID")
    system_id: int = Field(..., description="所属系统ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    @field_validator('system_id', mode='before')
    @staticmethod
    def _validate_system_id_entity(v):
        if v is None:
            raise ValueError('system_id不能为空')
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.isdigit():
                return int(s)
        raise ValueError('system_id必须为数字类型')

    class Config:
        from_attributes = True


class PageApiBase(BaseModel):
    """页面API关联基础模型"""
    execution_type: str = Field("parallel", description="执行类型：parallel(并行), serial(串行)")
    execution_order: int = Field(0, description="执行顺序")
    trigger_action: Optional[str] = Field(None, description="触发动作", max_length=50)
    api_purpose: Optional[str] = Field(None, description="API作用描述", max_length=100)
    success_action: Optional[str] = Field(None, description="成功后的动作", max_length=100)
    error_action: Optional[str] = Field(None, description="失败后的动作", max_length=100)
    conditions: Optional[Dict[str, Any]] = Field(None, description="执行条件")


class PageApiCreate(PageApiBase):
    """创建页面API关联模型"""
    page_id: int = Field(..., description="页面ID")
    api_id: int = Field(..., description="API接口ID")


class PageApiCreateRequest(PageApiBase):
    """创建页面API关联请求模型（不包含page_id）"""
    api_id: int = Field(..., description="API接口ID")


class PageApiUpdate(BaseModel):
    """更新页面API关联模型"""
    execution_type: Optional[str] = Field(None, description="执行类型")
    execution_order: Optional[int] = Field(None, description="执行顺序")
    trigger_action: Optional[str] = Field(None, description="触发动作")
    api_purpose: Optional[str] = Field(None, description="API作用描述")
    success_action: Optional[str] = Field(None, description="成功后的动作")
    error_action: Optional[str] = Field(None, description="失败后的动作")
    conditions: Optional[Dict[str, Any]] = Field(None, description="执行条件")


class PageApi(PageApiBase):
    """页面API关联模型"""
    id: int = Field(..., description="关联ID")
    page_id: int = Field(..., description="页面ID")
    api_id: int = Field(..., description="API接口ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class PageWithApis(Page):
    """包含API列表的页面模型"""
    apis: List[Dict[str, Any]] = Field(default_factory=list, description="关联的API列表")


class PageQueryRequest(BaseModel):
    """页面查询请求模型"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    system_id: Optional[int] = Field(None, description="系统ID")
    page_type: Optional[str] = Field(None, description="页面类型")
    status: Optional[str] = Field(None, description="状态")
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(10, description="每页数量", ge=1, le=100)

    @field_validator('system_id', mode='before')
    @staticmethod
    def _validate_system_id_query(v):
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.isdigit():
                return int(s)
        raise ValueError('system_id必须为数字类型')


class PageResponse(BaseModel):
    """页面响应模型"""
    pages: List[PageWithApis] = Field(..., description="页面列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class PageApiBatchRequest(BaseModel):
    """页面API批量操作请求模型"""
    page_id: int = Field(..., description="页面ID")
    api_relations: List[PageApiCreate] = Field(..., description="API关联列表")