"""
系统模型 - 极简版
System Model - Simplified
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SystemBase(BaseModel):
    """系统基础模型"""
    name: str = Field(..., description="系统名称")
    description: Optional[str] = Field(None, description="系统描述")
    url: Optional[str] = Field(None, description="系统基础URL，用于API Base路径")

class SystemCreate(SystemBase):
    """创建系统模型"""
    pass

class SystemUpdate(BaseModel):
    """更新系统模型"""
    name: Optional[str] = Field(None, description="系统名称")
    description: Optional[str] = Field(None, description="系统描述")
    url: Optional[str] = Field(None, description="系统基础URL，用于API Base路径")
    status: Optional[str] = Field(None, description="系统状态")
    category: Optional[str] = Field(None, description="系统分类")
    enabled: Optional[bool] = Field(None, description="是否启用")

class System(SystemBase):
    """系统模型"""
    id: int = Field(..., description="系统ID")
    status: str = Field(default="active", description="系统状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True