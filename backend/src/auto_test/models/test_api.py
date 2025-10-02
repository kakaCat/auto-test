"""
测试API管理 数据模型
Test APIs Management Data Models

与 docs/design/test-api-management-backend/04_REQUEST_RESPONSE_SCHEMAS.md 对齐：
- TestApi, RunResult, BatchExecuteRequest 等模型
- 字段命名采用下划线风格，tags 使用字符串列表
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class TestApiBase(BaseModel):
    """测试API基础模型"""
    name: str = Field(..., description="测试API名称")
    api_id: int = Field(..., description="关联的API接口ID")
    enabled: bool = Field(True, description="是否启用")
    tags: Optional[str] = Field(default=None, description="标签字符串（逗号分隔）")
    description: Optional[str] = Field(default=None, description="描述")
    config: Optional[Dict[str, Any]] = Field(default=None, description="执行配置(JSON)")


class TestApiCreate(TestApiBase):
    """创建测试API模型"""
    pass


class TestApiUpdate(BaseModel):
    """更新测试API模型"""
    name: Optional[str] = Field(None, description="测试API名称")
    api_id: Optional[int] = Field(None, description="关联的API接口ID")
    enabled: Optional[bool] = Field(None, description="是否启用")
    tags: Optional[str] = Field(None, description="标签字符串（逗号分隔）")
    description: Optional[str] = Field(None, description="描述")
    config: Optional[Dict[str, Any]] = Field(None, description="执行配置(JSON)")


class TestApi(TestApiBase):
    """测试API完整模型"""
    id: int = Field(..., description="测试API ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class TestApiDetail(BaseModel):
    """测试API详情模型（与当前Service返回结构对齐）"""
    id: int = Field(..., description="测试API ID")
    name: str = Field(..., description="测试API名称")
    enabled: bool = Field(True, description="是否启用")
    tags: Optional[str] = Field(default=None, description="标签字符串（逗号分隔）")
    description: Optional[str] = Field(default=None, description="描述")
    config: Optional[Dict[str, Any]] = Field(default=None, description="执行配置(JSON)")
    api_id: Optional[int] = Field(None, description="关联的API接口ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class TestApiQueryRequest(BaseModel):
    """测试API查询请求模型"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    api_id: Optional[int] = Field(None, description="接口ID筛选")
    enabled_only: Optional[bool] = Field(None, description="仅启用筛选")
    tags: Optional[str] = Field(None, description="标签字符串（逗号分隔）")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=1000, description="每页数量")


class TestApiListResponse(BaseModel):
    """测试API列表响应模型"""
    items: List[TestApi] = Field(default_factory=list, description="测试API列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页数量")


class AssertionResult(BaseModel):
    """断言结果模型"""
    name: str = Field(..., description="断言名称")
    passed: bool = Field(..., description="是否通过")
    details: Optional[Dict[str, Any]] = Field(None, description="断言详情")


class RunResult(BaseModel):
    """测试执行结果模型"""
    run_id: str = Field(..., description="运行ID")
    test_api_id: Optional[int] = Field(None, description="测试API ID")
    api_id: Optional[int] = Field(None, description="API接口ID")
    status: str = Field(..., description="状态", pattern="^(success|failed)$")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    ended_at: Optional[datetime] = Field(None, description="结束时间")
    assertions: Optional[List[AssertionResult]] = Field(None, description="断言结果列表")
    response_status_code: Optional[int] = Field(None, description="响应状态码")
    response_time_ms: Optional[int] = Field(None, description="响应耗时(ms)")
    response_headers: Optional[Dict[str, Any]] = Field(None, description="响应头")
    response_body: Optional[Any] = Field(None, description="响应体")
    assertions_passed: Optional[int] = Field(None, description="通过的断言数量")
    assertions_total: Optional[int] = Field(None, description="断言总数")
    error_message: Optional[str] = Field(None, description="错误消息")
    environment: Optional[Dict[str, Any]] = Field(None, description="环境信息")


class BatchExecuteItem(BaseModel):
    """批量执行单项结果模型"""
    test_api_id: int = Field(..., description="测试API ID")
    run_id: str = Field(..., description="运行ID")
    status: str = Field(..., description="状态", pattern="^(success|failed)$")


class BatchExecuteResponse(BaseModel):
    """批量执行响应模型"""
    items: List[BatchExecuteItem] = Field(default_factory=list, description="批量执行结果项列表")


class BatchExecuteRequest(BaseModel):
    """批量执行请求模型"""
    test_api_ids: List[int] = Field(..., description="测试API ID列表")
    retry_count: Optional[int] = Field(None, description="重试次数")
    retry_delay: Optional[int] = Field(None, description="重试间隔")
    continue_on_failure: Optional[bool] = Field(None, description="失败后继续")
    parallel: Optional[bool] = Field(None, description="并行执行")
    variables: Optional[Dict[str, Any]] = Field(None, description="变量")
    environment: Optional[Dict[str, Any]] = Field(None, description="环境配置")


class ImportTestApisRequest(BaseModel):
    """导入测试API请求"""
    items: List[TestApiCreate] = Field(..., description="导入的测试API列表")
    overwrite: bool = Field(False, description="是否覆盖已有配置")


class ExportTestApisRequest(BaseModel):
    """导出测试API请求"""
    items: Optional[List[int]] = Field(None, description="导出指定ID列表，空表示全部")
    format: str = Field("json", description="导出格式", pattern="^(json|yaml)$")


class ImportTestApisResponse(BaseModel):
    """导入测试API响应"""
    imported: bool = Field(..., description="是否导入成功")
    count: int = Field(..., description="导入数量")


class ExportTestApisResponse(BaseModel):
    """导出测试API响应"""
    exported: bool = Field(..., description="是否导出成功")
    items: List[int] = Field(default_factory=list, description="导出的测试API ID列表")
    format: str = Field("json", description="导出格式", pattern="^(json|yaml)$")


class DeleteTestApiResponse(BaseModel):
    """删除测试API响应"""
    deleted: bool = Field(..., description="是否删除成功")


class RunListResponse(BaseModel):
    """执行记录列表响应模型"""
    items: List[RunResult] = Field(default_factory=list, description="执行记录列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页数量")


class ReportItem(BaseModel):
    """报告项模型"""
    report_id: int = Field(..., description="报告ID")
    run_id: str = Field(..., description="运行ID")
    summary: Dict[str, Any] = Field(default_factory=dict, description="报告摘要")


class ReportListResponse(BaseModel):
    """报告列表响应模型"""
    items: List[ReportItem] = Field(default_factory=list, description="报告列表")
    total: int = Field(0, description="总数量")


# 下面模型用于单次执行请求的结构对齐

class RequestConfig(BaseModel):
    method: Optional[str] = Field(None, description="HTTP方法")
    url: Optional[str] = Field(None, description="请求URL")
    headers: Optional[Dict[str, Any]] = Field(None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(None, description="查询参数")
    body: Optional[Any] = Field(None, description="请求体")
    body_type: Optional[str] = Field(None, description="请求体类型")
    timeout: Optional[int] = Field(None, description="超时时间")
    follow_redirects: Optional[bool] = Field(None, description="跟随重定向")
    validate_ssl: Optional[bool] = Field(None, description="校验SSL")


class ExecutionConfig(BaseModel):
    retry_count: Optional[int] = Field(None, description="重试次数")
    retry_delay: Optional[int] = Field(None, description="重试间隔")
    continue_on_failure: Optional[bool] = Field(None, description="失败后继续")
    parallel: Optional[bool] = Field(None, description="并行执行")
    variables: Optional[Dict[str, Any]] = Field(None, description="变量")


class ExpectedAssertion(BaseModel):
    class AssertionType(str, Enum):
        status_code = "status_code"
        header = "header"
        body = "body"
        jsonpath = "jsonpath"
        json_path = "json_path"
        regex = "regex"

    class AssertionOperator(str, Enum):
        eq = "eq"
        neq = "neq"
        gt = "gt"
        lt = "lt"
        contains = "contains"
        not_contains = "not_contains"
        exists = "exists"
        not_exists = "not_exists"
        match = "match"

    type: AssertionType = Field(..., description="断言类型")
    path: Optional[str] = Field(None, description="JSONPath/位置")
    target: Optional[str] = Field(None, description="目标，例如headers/body")
    operator: Optional[AssertionOperator] = Field(None, description="比较操作符")
    value: Optional[Any] = Field(None, description="期望值")


class ExpectedResponse(BaseModel):
    status_code: Optional[int] = Field(None, description="期望的状态码")
    assertions: Optional[List[ExpectedAssertion]] = Field(None, description="断言配置")


class ExecuteTestApiRequest(BaseModel):
    execution_config: Optional[ExecutionConfig] = Field(None, description="执行配置")
    environment: Optional[Dict[str, Any]] = Field(None, description="环境配置")
    request_overrides: Optional[RequestConfig] = Field(None, description="请求覆盖项")
    expected_response: Optional[ExpectedResponse] = Field(None, description="期望响应")