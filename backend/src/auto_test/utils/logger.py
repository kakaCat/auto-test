"""
日志工具 - 极简版
Logger Utils - Simplified

提供简化的日志配置
"""

import logging
from ..config import get_config

def get_logger(name: str = __name__) -> logging.Logger:
    """获取日志记录器"""
    config = get_config()
    
    # 配置日志格式
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        force=True
    )
    
    return logging.getLogger(name)