#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一API服务启动脚本 (Unified API Service Launcher)

功能概述：
- 启动使用新架构的统一API服务
- 初始化所有模块和依赖
- 配置数据库连接和迁移
- 设置日志和监控
- 支持开发和生产环境

使用方法：
python start_unified_api.py [--port PORT] [--host HOST] [--debug] [--migrate]

参数说明：
--port: 服务端口，默认8003
--host: 服务主机，默认127.0.0.1
--debug: 启用调试模式
--migrate: 运行数据迁移
--env: 环境配置 (dev/prod)，默认dev
"""

import os
import sys
import argparse
import logging
import asyncio
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def setup_logging(debug: bool = False):
    """设置日志配置"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler('unified_api.log')
    file_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库日志级别
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

def initialize_environment(env: str):
    """初始化环境配置"""
    logger = logging.getLogger(__name__)
    
    # 设置环境变量
    os.environ['ENVIRONMENT'] = env
    
    if env == 'dev':
        os.environ['DEBUG'] = 'true'
        os.environ['DATABASE_URL'] = 'sqlite:///./autotest_dev.db'
    elif env == 'prod':
        os.environ['DEBUG'] = 'false'
        # 生产环境数据库配置
        if 'DATABASE_URL' not in os.environ:
            os.environ['DATABASE_URL'] = 'sqlite:///./autotest_prod.db'
    
    logger.info(f"环境配置完成: {env}")

def validate_configuration():
    """验证配置"""
    logger = logging.getLogger(__name__)
    
    try:
        from auto_test.config import get_api_config
        settings = get_api_config()
        
        logger.info(f"配置验证成功:")
        logger.info(f"  - 调试模式: {settings.debug}")
        logger.info(f"  - 主机: {settings.host}")
        logger.info(f"  - 端口: {settings.port}")
        
        return True
        
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        return False

async def start_server(host: str, port: int, debug: bool):
    """启动服务器"""
    logger = logging.getLogger(__name__)
    
    try:
        import uvicorn
        from auto_test.main import app
        
        logger.info(f"启动统一API服务...")
        logger.info(f"  - 主机: {host}")
        logger.info(f"  - 端口: {port}")
        logger.info(f"  - 调试模式: {debug}")
        logger.info(f"  - API文档: http://{host}:{port}/docs")
        logger.info(f"  - ReDoc文档: http://{host}:{port}/redoc")
        
        # 配置uvicorn
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一API服务启动脚本")
    parser.add_argument("--port", type=int, default=8000, help="服务端口 (默认: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务主机 (默认: 127.0.0.1)")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--env", type=str, choices=['dev', 'prod'], default='dev', help="环境配置 (默认: dev)")
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.debug)
    
    logger.info("=" * 60)
    logger.info("统一API服务启动脚本")
    logger.info("=" * 60)
    
    try:
        # 初始化环境
        initialize_environment(args.env)
        
        # 验证配置
        if not validate_configuration():
            logger.error("配置验证失败，退出")
            return 1
        
        # 启动服务器
        asyncio.run(start_server(args.host, args.port, args.debug))
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("用户中断，退出")
        return 0
    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        return 1
    finally:
        logger.info("统一API服务已退出")

if __name__ == "__main__":
    sys.exit(main())