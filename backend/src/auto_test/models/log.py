"""
日志数据模型

定义日志相关的数据结构，包括：
- 日志实体模型
- 日志请求模型
- 日志响应模型
- 日志统计模型

遵循极简架构设计原则
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LogLevel:
    """日志级别常量"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    """日志条目模型"""
    id: int = Field(..., description="日志ID")
    timestamp: datetime = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别")
    message: str = Field(..., description="日志消息")
    module: Optional[str] = Field(None, description="模块名称")
    function: Optional[str] = Field(None, description="函数名称")
    line_number: Optional[int] = Field(None, description="行号")
    user_id: Optional[str] = Field(None, description="用户ID")
    request_id: Optional[str] = Field(None, description="请求ID")
    extra_data: Optional[dict] = Field(None, description="额外数据")


class LogStats(BaseModel):
    """日志统计模型"""
    total_logs: int = Field(0, description="总日志数")
    info_logs: int = Field(0, description="信息日志数")
    warning_logs: int = Field(0, description="警告日志数")
    error_logs: int = Field(0, description="错误日志数")
    debug_logs: int = Field(0, description="调试日志数")
    critical_logs: int = Field(0, description="严重错误日志数")


class LogQueryRequest(BaseModel):
    """日志查询请求模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    level: Optional[str] = Field(None, description="日志级别筛选")
    module: Optional[str] = Field(None, description="模块筛选")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    keyword: Optional[str] = Field(None, description="关键词搜索")


class LogResponse(BaseModel):
    """日志响应模型"""
    logs: List[LogEntry] = Field(default_factory=list, description="日志列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(20, description="每页数量")
    stats: LogStats = Field(default_factory=LogStats, description="统计信息")