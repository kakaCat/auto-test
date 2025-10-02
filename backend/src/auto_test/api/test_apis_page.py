"""
测试API管理 - 页面路由模块
Test APIs Management - Page API Module

遵循极简控制器(API)编码规范：
- API方法不超过5行业务调用
- 不包含复杂业务逻辑，仅做入参校验与调用Service
"""

from typing import Optional
from fastapi import APIRouter, Query, Depends
from ..services.test_api_service import TestApiService
from ..utils.response import success_response, error_response
from ..models.response import ApiResponse, ApiResponseGeneric
from ..models.test_api import (
    TestApiCreate,
    TestApiUpdate,
    TestApiQueryRequest,
    TestApiListResponse,
    TestApiDetail,
    RunListResponse,
    ReportListResponse,
    DeleteTestApiResponse,
)

router = APIRouter(tags=["测试API管理-页面"])


@router.get("/test-apis/v1/test-apis", response_model=ApiResponseGeneric[TestApiListResponse], summary="获取测试API列表")
async def list_test_apis(query: TestApiQueryRequest = Depends()):
    try:
        data = TestApiService.list_test_apis(
            keyword=query.keyword,
            api_id=query.api_id,
            enabled_only=query.enabled_only,
            tags=query.tags,
            page=query.page,
            size=query.size,
        )
        return success_response(data=data, message="获取测试API列表成功")
    except Exception as e:
        return error_response(message=f"获取测试API列表失败: {str(e)}")


@router.post("/test-apis/v1/test-apis", response_model=ApiResponseGeneric[TestApiDetail], summary="创建测试API配置")
async def create_test_api(payload: TestApiCreate):
    try:
        data = TestApiService.create_test_api(payload)
        return success_response(data=data, message="创建测试API配置成功")
    except Exception as e:
        return error_response(message=f"创建测试API配置失败: {str(e)}")


@router.get("/test-apis/v1/test-apis/{test_api_id}", response_model=ApiResponseGeneric[TestApiDetail], summary="获取测试API详情")
async def get_test_api(test_api_id: int):
    try:
        data = TestApiService.get_test_api_by_id(test_api_id)
        return success_response(data=data, message="获取测试API详情成功")
    except Exception as e:
        return error_response(message=f"获取测试API详情失败: {str(e)}")


@router.put("/test-apis/v1/test-apis/{test_api_id}", response_model=ApiResponseGeneric[TestApiDetail], summary="更新测试API配置")
async def update_test_api(test_api_id: int, payload: TestApiUpdate):
    try:
        data = TestApiService.update_test_api(test_api_id, payload)
        return success_response(data=data, message="更新测试API配置成功")
    except Exception as e:
        return error_response(message=f"更新测试API配置失败: {str(e)}")


@router.delete("/test-apis/v1/test-apis/{test_api_id}", response_model=ApiResponseGeneric[DeleteTestApiResponse], summary="删除测试API配置")
async def delete_test_api(test_api_id: int):
    try:
        ok = TestApiService.delete_test_api(test_api_id)
        return success_response(data={"deleted": ok}, message="删除测试API配置成功")
    except Exception as e:
        return error_response(message=f"删除测试API配置失败: {str(e)}")


@router.get("/test-apis/v1/test-apis/{test_api_id}/runs", response_model=ApiResponseGeneric[RunListResponse], summary="获取执行记录列表")
async def list_runs(test_api_id: int, page: int = Query(1), size: int = Query(10)):
    try:
        data = TestApiService.list_runs(test_api_id, page, size)
        return success_response(data=data, message="获取执行记录列表成功")
    except Exception as e:
        return error_response(message=f"获取执行记录列表失败: {str(e)}")


@router.get("/test-apis/v1/test-apis/{test_api_id}/reports", response_model=ApiResponseGeneric[ReportListResponse], summary="获取报告列表")
async def list_reports(test_api_id: int):
    try:
        data = TestApiService.list_reports(test_api_id)
        return success_response(data=data, message="获取报告列表成功")
    except Exception as e:
        return error_response(message=f"获取报告列表失败: {str(e)}")