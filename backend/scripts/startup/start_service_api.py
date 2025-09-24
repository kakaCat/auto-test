#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务API模块启动脚本

功能概述：
- 启动服务API模块
- 提供服务管理接口

使用方法：
python start_service_api.py [--port PORT] [--host HOST]
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

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('service_api.log')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="服务API模块启动脚本")
    parser.add_argument("--port", type=int, default=8001, help="服务端口")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务主机")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("启动服务API模块...")
    
    try:
        # 启动服务
        import uvicorn
        
        logger.info(f"启动服务API: http://{args.host}:{args.port}")
        
        # 使用模块路径运行
        uvicorn.run(
            "auto_test.main:app",
            host=args.host,
            port=args.port,
            access_log=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())