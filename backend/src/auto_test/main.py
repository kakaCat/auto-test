"""
自动化测试平台 - 极简版主应用入口
AI Auto Test Platform - Simplified Main Application Entry

采用极简架构设计，专注于快速开发和简单维护
"""

import logging
import uvicorn
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# 简化的配置和数据库导入
from .config import Config
from .database.connection import init_database
from .utils.logger import get_logger

# 导入路由
from .api.systems import router as systems_router
from .api.modules import router as modules_router
from .api.stats import router as stats_router
from .api.workflows import router as workflows_router
from .api.scenarios import router as scenarios_router
from .api.api_interfaces import router as api_interfaces_router
from .api.logs import router as logs_router
from .api.pages import router as pages_router

# 设置日志
logger = get_logger(__name__)

def create_app() -> FastAPI:
    """创建FastAPI应用实例 - 极简版"""
    
    # 初始化数据库
    init_database()
    
    # 创建FastAPI应用
    app = FastAPI(
        title="AI自动化测试平台 - 极简版",
        description="AI Auto Test Platform - Simplified Architecture",
        version="4.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 配置Gzip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = datetime.now()
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
        return response
    
    # 注册路由 - 版本号由各业务模块自己管理
    app.include_router(systems_router, prefix="/api", tags=["System Management"])
    app.include_router(modules_router, prefix="/api", tags=["Module Management"])
    app.include_router(stats_router, prefix="/api", tags=["Statistics"])
    app.include_router(workflows_router, prefix="/api", tags=["Workflow Management"])
    app.include_router(scenarios_router, prefix="/api", tags=["Scenario Management"])
    app.include_router(api_interfaces_router, prefix="/api", tags=["API Interface Management"])
    app.include_router(logs_router, prefix="/api", tags=["Log Management"])
    app.include_router(pages_router, prefix="/api", tags=["Page Management"])
    
    # 根路径
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """根路径 - 返回API基本信息"""
        return {
            "message": "AI自动化测试平台 - 极简版",
            "version": "4.0.0",
            "architecture": "simplified",
            "status": "running",
            "docs": "/docs",
            "timestamp": datetime.now().isoformat()
        }
    
    # 健康检查
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """健康检查接口"""
        return {
            "status": "healthy",
            "version": "4.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    # 获取配置
    config = Config()
    
    # 启动应用
    uvicorn.run(
        "auto_test.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )