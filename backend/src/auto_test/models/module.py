"""
模块模型 - 极简版
Module Model - Simplified
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class ModuleBase(BaseModel):
    """模块基础模型"""
    name: str = Field(..., description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    tags: Optional[str] = Field(None, description="模块标签")
    path: str = Field(default="/", description="模块路径")

class ModuleCreate(ModuleBase):
    """创建模块模型"""
    system_id: int = Field(..., description="所属系统ID")

    @field_validator('system_id', mode='before')
    @staticmethod
    def _validate_system_id(v):
        if v is None:
            raise ValueError('system_id不能为空')
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.isdigit():
                return int(s)
        raise ValueError('system_id必须为数字类型')

class ModuleUpdate(BaseModel):
    """更新模块模型"""
    name: Optional[str] = Field(None, description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    status: Optional[str] = Field(None, description="模块状态")
    tags: Optional[str] = Field(None, description="模块标签")

class Module(ModuleBase):
    """模块模型"""
    id: int = Field(..., description="模块ID")
    system_id: int = Field(..., description="所属系统ID")
    status: str = Field(default="active", description="模块状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    system_name: Optional[str] = Field(None, description="系统名称")

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