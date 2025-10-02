"""
测试API管理 - 弹框路由模块
Test APIs Management - Dialog API Module

遵循极简控制器(API)编码规范。
"""

from fastapi import APIRouter
from ..services.test_api_service import TestApiService
from ..utils.response import success_response, error_response
from ..models.response import ApiResponse, ApiResponseGeneric
from ..models.test_api import (
    BatchExecuteRequest,
    ImportTestApisRequest,
    ExportTestApisRequest,
    ExecuteTestApiRequest,
    RunResult,
    BatchExecuteResponse,
    ImportTestApisResponse,
    ExportTestApisResponse,
)

router = APIRouter(tags=["测试API管理-弹框"])


@router.post("/test-apis/v1/test-apis/{test_api_id}/execute", response_model=ApiResponseGeneric[RunResult], summary="执行单个测试API")
async def execute_test_api(test_api_id: int, payload: ExecuteTestApiRequest):
    try:
        data = TestApiService.execute_test_api(test_api_id, payload)
        return success_response(data=data, message="执行测试API成功")
    except Exception as e:
        return error_response(message=f"执行测试API失败: {str(e)}")


@router.post("/test-apis/v1/test-apis/batch-execute", response_model=ApiResponseGeneric[BatchExecuteResponse], summary="批量执行测试API")
async def batch_execute(payload: BatchExecuteRequest):
    try:
        data = TestApiService.batch_execute(payload)
        return success_response(data=data, message="批量执行测试API成功")
    except Exception as e:
        return error_response(message=f"批量执行测试API失败: {str(e)}")


@router.post("/test-apis/v1/test-apis/import", response_model=ApiResponseGeneric[ImportTestApisResponse], summary="导入测试API配置")
async def import_test_apis(payload: ImportTestApisRequest):
    try:
        data = TestApiService.import_test_apis(payload)
        return success_response(data=data, message="导入测试API配置成功")
    except Exception as e:
        return error_response(message=f"导入测试API配置失败: {str(e)}")


@router.post("/test-apis/v1/test-apis/export", response_model=ApiResponseGeneric[ExportTestApisResponse], summary="导出测试API配置")
async def export_test_apis(payload: ExportTestApisRequest):
    try:
        data = TestApiService.export_test_apis(payload)
        return success_response(data=data, message="导出测试API配置成功")
    except Exception as e:
        return error_response(message=f"导出测试API配置失败: {str(e)}")