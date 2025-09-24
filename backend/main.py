#!/usr/bin/env python3
"""
AI自动化测试平台 - 后端服务主入口
整合所有API模块，提供统一的服务入口
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入各个模块的API
try:
    from src.auto_test.api_management.api import app as api_management_app
    from src.auto_test.scenario_management.api import app as scenario_management_app
    from src.auto_test.workflow_orchestration.api import app as workflow_app
    from src.auto_test.integration.api import app as integration_app
    # 如果存在AI场景执行API，也导入
    try:
        from src.auto_test.api.scenario_ai_api import app as ai_scenario_app
    except ImportError:
        ai_scenario_app = None
        logger.warning("AI场景执行API模块未找到，跳过导入")
except ImportError as e:
    logger.error(f"导入API模块失败: {e}")
    # 创建基础应用以防止启动失败
    api_management_app = None
    scenario_management_app = None
    workflow_app = None
    integration_app = None
    ai_scenario_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 启动AI自动化测试平台后端服务")
    
    # 启动时初始化
    try:
        # 这里可以添加数据库连接、缓存初始化等
        logger.info("✅ 后端服务初始化完成")
    except Exception as e:
        logger.error(f"❌ 后端服务初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("🔄 关闭AI自动化测试平台后端服务")


# 创建主应用
app = FastAPI(
    title="AI自动化测试平台",
    description="基于AI的智能场景执行系统，支持API管理、场景编排、工作流执行等功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "AI自动化测试平台"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI自动化测试平台后端服务",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# 挂载子应用
if api_management_app:
    app.mount("/api/api-management", api_management_app)
    logger.info("✅ API管理模块已挂载")

if scenario_management_app:
    app.mount("/api/scenario-management", scenario_management_app)
    logger.info("✅ 场景管理模块已挂载")

if workflow_app:
    app.mount("/api/workflow", workflow_app)
    logger.info("✅ 工作流编排模块已挂载")

if integration_app:
    app.mount("/api/integration", integration_app)
    logger.info("✅ 系统集成模块已挂载")

if ai_scenario_app:
    app.mount("/api/ai-scenario", ai_scenario_app)
    logger.info("✅ AI场景执行模块已挂载")


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )


if __name__ == "__main__":
    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌐 启动服务: http://{host}:{port}")
    logger.info(f"📚 API文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        "backend_main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )