#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API管理模块 v2 启动脚本

功能概述：
- 启动使用新架构的API管理服务
- 配置数据库连接
- 设置日志和监控

使用方法：
python start_api_v2.py [--port PORT] [--host HOST] [--debug]
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def setup_logging(debug=False):
    """设置日志配置"""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('api_v2.log')
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger('uvicorn').setLevel(logging.INFO)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="API管理模块 v2 启动脚本")
    parser.add_argument("--port", type=int, default=8002, help="服务端口")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务主机")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("启动API管理模块 v2...")
    
    try:
        # 启动服务
        import uvicorn
        
        logger.info(f"启动API服务: http://{args.host}:{args.port}")
        logger.info(f"API文档: http://{args.host}:{args.port}/docs")
        
        # 使用模块路径运行
        uvicorn.run(
            "auto_test.main:app",
            host=args.host,
            port=args.port,
            reload=args.debug,
            access_log=True,
            log_level="debug" if args.debug else "info"
        )
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())