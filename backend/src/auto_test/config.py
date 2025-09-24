"""配置管理模块 - 极简版
Configuration Management Module - Simplified

采用极简配置管理，专注于环境变量和默认值
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Config:
    """应用配置 - 极简版"""
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///auto_test.db")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "auto_test.db")
    
    # API配置
    API_PREFIX: str = "/api"
    API_VERSION: str = "v4"
    
    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS配置
    CORS_ORIGINS: List[str] = field(default_factory=lambda: ["*"])
    CORS_METHODS: List[str] = field(default_factory=lambda: ["*"])
    CORS_HEADERS: List[str] = field(default_factory=lambda: ["*"])
    
    # 应用信息
    APP_NAME: str = "AI自动化测试平台"
    APP_VERSION: str = "4.0.0"
    APP_DESCRIPTION: str = "AI Auto Test Platform - Simplified Architecture"

# 全局配置实例
config = Config()

def get_config() -> Config:
    """获取配置实例"""
    return config