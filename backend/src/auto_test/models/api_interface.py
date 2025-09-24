"""
API接口模型 - 极简版
API Interface Model - Simplified
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ApiInterfaceBase(BaseModel):
    """API接口基础模型"""
    name: str = Field(..., description="接口名称")
    description: Optional[str] = Field(None, description="接口描述")
    method: str = Field(..., description="HTTP方法", pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    path: str = Field(..., description="接口路径")
    version: str = Field(default="v1", description="接口版本")
    status: str = Field(default="active", description="接口状态", pattern="^(active|inactive|deprecated|testing)$")
    request_format: str = Field(default="json", description="请求格式", pattern="^(json|form|xml)$")
    response_format: str = Field(default="json", description="响应格式", pattern="^(json|xml|text)$")
    auth_required: bool = Field(default=True, description="是否需要认证")
    rate_limit: int = Field(default=1000, description="速率限制")
    timeout: int = Field(default=30, description="超时时间(秒)")
    tags: Optional[str] = Field(None, description="标签")
    request_schema: Optional[str] = Field(None, description="请求Schema")
    response_schema: Optional[str] = Field(None, description="响应Schema")
    example_request: Optional[str] = Field(None, description="请求示例")
    example_response: Optional[str] = Field(None, description="响应示例")


class ApiInterfaceCreate(ApiInterfaceBase):
    """创建API接口模型"""
    system_id: int = Field(..., description="所属系统ID")
    module_id: Optional[int] = Field(None, description="所属模块ID")


class ApiInterfaceUpdate(BaseModel):
    """更新API接口模型"""
    name: Optional[str] = Field(None, description="接口名称")
    description: Optional[str] = Field(None, description="接口描述")
    method: Optional[str] = Field(None, description="HTTP方法", pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    path: Optional[str] = Field(None, description="接口路径")
    version: Optional[str] = Field(None, description="接口版本")
    status: Optional[str] = Field(None, description="接口状态", pattern="^(active|inactive|deprecated|testing)$")
    request_format: Optional[str] = Field(None, description="请求格式", pattern="^(json|form|xml)$")
    response_format: Optional[str] = Field(None, description="响应格式", pattern="^(json|xml|text)$")
    auth_required: Optional[bool] = Field(None, description="是否需要认证")
    rate_limit: Optional[int] = Field(None, description="速率限制")
    timeout: Optional[int] = Field(None, description="超时时间(秒)")
    tags: Optional[str] = Field(None, description="标签")
    request_schema: Optional[str] = Field(None, description="请求Schema")
    response_schema: Optional[str] = Field(None, description="响应Schema")
    example_request: Optional[str] = Field(None, description="请求示例")
    example_response: Optional[str] = Field(None, description="响应示例")
    system_id: Optional[int] = Field(None, description="所属系统ID")
    module_id: Optional[int] = Field(None, description="所属模块ID")


class ApiInterface(ApiInterfaceBase):
    """API接口模型"""
    id: int = Field(..., description="接口ID")
    system_id: int = Field(..., description="所属系统ID")
    module_id: Optional[int] = Field(None, description="所属模块ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    system_name: Optional[str] = Field(None, description="系统名称")
    module_name: Optional[str] = Field(None, description="模块名称")
    
    class Config:
        from_attributes = True


class ApiInterfaceQueryRequest(BaseModel):
    """API接口查询请求模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    system_id: Optional[int] = Field(None, description="系统ID筛选")
    module_id: Optional[int] = Field(None, description="模块ID筛选")
    method: Optional[str] = Field(None, description="HTTP方法筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    tags: Optional[str] = Field(None, description="标签筛选")


class ApiInterfaceResponse(BaseModel):
    """API接口响应模型"""
    apis: List[ApiInterface] = Field(default_factory=list, description="接口列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(20, description="每页数量")


class ApiInterfaceStats(BaseModel):
    """API接口统计模型"""
    total_apis: int = Field(0, description="总接口数")
    active_apis: int = Field(0, description="活跃接口数")
    inactive_apis: int = Field(0, description="非活跃接口数")
    deprecated_apis: int = Field(0, description="已废弃接口数")
    apis_by_method: dict = Field(default_factory=dict, description="按方法统计")
    apis_by_system: dict = Field(default_factory=dict, description="按系统统计")
    apis_by_status: dict = Field(default_factory=dict, description="按状态统计")


class ApiInterfaceBatchRequest(BaseModel):
    """API接口批量操作请求模型"""
    ids: List[int] = Field(..., description="接口ID列表")
    action: str = Field(..., description="操作类型", pattern="^(activate|deactivate|deprecate|delete)$")


class ApiInterfaceImportRequest(BaseModel):
    """API接口导入请求模型"""
    apis: List[ApiInterfaceCreate] = Field(..., description="待导入的接口列表")
    overwrite: bool = Field(default=False, description="是否覆盖已存在的接口")


class ApiInterfaceExportResponse(BaseModel):
    """API接口导出响应模型"""
    apis: List[ApiInterface] = Field(default_factory=list, description="导出的接口列表")
    export_time: datetime = Field(default_factory=datetime.now, description="导出时间")
    total_count: int = Field(0, description="导出总数")