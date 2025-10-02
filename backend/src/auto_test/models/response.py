"""
统一响应模型
Unified API Response Model

用于 FastAPI 路由的 response_model，保持 success/message/data/code 结构。
"""

from typing import Any, Optional, Union, TypeVar, Generic
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    data: Optional[Any] = Field(None, description="业务数据")
    code: Optional[Union[int, str]] = Field(None, description="错误码或状态码（支持字符串或整数）")


# 泛型响应模型，用于为 data 提供强类型
T = TypeVar("T")

class ApiResponseGeneric(BaseModel, Generic[T]):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    data: Optional[T] = Field(None, description="业务数据（泛型）")
    code: Optional[Union[int, str]] = Field(None, description="错误码或状态码（支持字符串或整数）")