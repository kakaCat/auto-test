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
    status: str = Field(default="active", description="状态", pattern="^(active|inactive|deprecated|testing)$")
    request_format: str = Field(default="json", description="请求格式", pattern="^(json|form|xml)$")
    response_format: str = Field(default="json", description="响应格式", pattern="^(json|xml|text)$")
    auth_required: int = Field(default=1, description="是否需要认证(0:否, 1:是)")
    rate_limit: int = Field(default=1000, description="速率限制")
    timeout: int = Field(default=30, description="超时时间(秒)")
    tags: Optional[str] = Field(None, description="标签")
    request_schema: Optional[dict] = Field(None, description="请求模式（支持字典）")
    response_schema: Optional[dict] = Field(None, description="响应模式（支持字典）")
    example_request: Optional[str] = Field(None, description="请求示例")
    example_response: Optional[str] = Field(None, description="响应示例")


class ApiInterfaceCreate(ApiInterfaceBase):
    """创建API接口模型"""
    system_id: int = Field(..., description="所属系统ID")
    module_id: int = Field(..., description="所属模块ID")


class ApiInterfaceUpdate(BaseModel):
    """更新API接口模型"""
    name: Optional[str] = Field(None, description="接口名称")
    description: Optional[str] = Field(None, description="接口描述")
    method: Optional[str] = Field(None, description="HTTP方法", pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    path: Optional[str] = Field(None, description="接口路径")
    version: Optional[str] = Field(None, description="接口版本")
    status: Optional[str] = Field(None, description="状态", pattern="^(active|inactive|deprecated|testing)$")
    enabled: Optional[bool] = Field(None, description="是否启用（兼容字段）")
    request_format: Optional[str] = Field(None, description="请求格式", pattern="^(json|form|xml)$")
    response_format: Optional[str] = Field(None, description="响应格式", pattern="^(json|xml|text)$")
    auth_required: Optional[int] = Field(None, description="是否需要认证(0:否, 1:是)")
    rate_limit: Optional[int] = Field(None, description="速率限制")
    timeout: Optional[int] = Field(None, description="超时时间(秒)")
    tags: Optional[str] = Field(None, description="标签")
    request_schema: Optional[str] = Field(None, description="请求模式")
    response_schema: Optional[str] = Field(None, description="响应模式")
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
    enabled: Optional[bool] = Field(None, description="是否启用（兼容字段）")
    
    class Config:
        from_attributes = True


class ApiInterfaceQueryRequest(BaseModel):
    """API接口查询请求模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=1000, description="每页数量")
    system_id: Optional[int] = Field(None, description="系统ID筛选")
    module_id: Optional[int] = Field(None, description="模块ID筛选")
    method: Optional[str] = Field(None, description="HTTP方法筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    tags: Optional[str] = Field(None, description="标签筛选")
    enabled_only: Optional[bool] = Field(None, description="仅显示启用的")


class ApiInterfaceResponse(BaseModel):
    """API接口响应模型"""
    # 兼容字段（存量）：apis
    apis: List[ApiInterface] = Field(default_factory=list, description="接口列表（兼容字段，将逐步废弃）")
    # 统一规范字段：list
    list: List[ApiInterface] = Field(default_factory=list, description="接口列表（统一规范字段）")
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
    timestamp: Optional[str] = Field(None, description="统计时间戳")
    health_score: Optional[float] = Field(None, description="健康评分")


class ApiInterfaceBatchRequest(BaseModel):
    """API接口批量操作请求模型"""
    api_ids: List[int] = Field(..., description="接口ID列表")
    status: str = Field(..., description="目标状态", pattern="^(active|inactive|deprecated|testing)$")


class ApiInterfaceImportRequest(BaseModel):
    """API接口导入请求模型"""
    apis: List[ApiInterfaceCreate] = Field(..., description="待导入的接口列表")
    overwrite: bool = Field(default=False, description="是否覆盖已存在的接口")


class ApiInterfaceExportResponse(BaseModel):
    """API接口导出响应模型"""
    apis: List[ApiInterface] = Field(default_factory=list, description="导出的接口列表")
    export_time: datetime = Field(default_factory=datetime.now, description="导出时间")
    total_count: int = Field(0, description="导出总数")


class DeleteApiInterfaceResponse(BaseModel):
    """删除API接口响应数据"""
    deleted: bool = Field(..., description="是否删除成功")


class ApiInterfaceImportResponseItem(BaseModel):
    name: str = Field(..., description="接口名称")
    status: str = Field(..., description="导入状态: success/error")
    id: Optional[int] = Field(None, description="创建成功的ID")
    error: Optional[str] = Field(None, description="错误信息")


class ApiInterfaceImportResponse(BaseModel):
    """API接口导入结果响应模型"""
    total: int = Field(0, description="导入总数")
    success_count: int = Field(0, description="成功数量")
    error_count: int = Field(0, description="失败数量")
    results: List[ApiInterfaceImportResponseItem] = Field(default_factory=list, description="逐项导入结果")


class ApiInterfaceBatchStatusResult(BaseModel):
    """批量更新状态结果模型"""
    updated_count: int = Field(..., description="更新数量")
    total_count: int = Field(..., description="总处理数量")
    status: str = Field(..., description="目标状态")
    timestamp: str = Field(..., description="操作时间戳")


class ApiInterfaceBatchDeleteResult(BaseModel):
    """批量删除结果模型"""
    deleted_count: int = Field(..., description="删除数量")
    total_count: int = Field(..., description="总处理数量")
    timestamp: str = Field(..., description="操作时间戳")


class ApiInterfaceTestResult(BaseModel):
    """单个API测试结果"""
    api_id: int = Field(..., description="API接口ID")
    test_result: str = Field(..., description="测试结果")
    response_time: str = Field(..., description="响应时间")
    status_code: int = Field(..., description="HTTP状态码")
    test_time: str = Field(..., description="测试时间")


class ApiBatchTestResult(BaseModel):
    """批量测试结果"""
    tested_count: int = Field(..., description="测试数量")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    test_time: str = Field(..., description="测试时间")


class HttpMethodOption(BaseModel):
    value: str = Field(..., description="HTTP方法值")
    label: str = Field(..., description="显示标签")
    color: str = Field(..., description="前端颜色标识")


class ApiStatusOption(BaseModel):
    value: str = Field(..., description="状态值")
    label: str = Field(..., description="显示标签")
    color: str = Field(..., description="前端颜色标识")