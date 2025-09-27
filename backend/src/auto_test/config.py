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
    
    # AI配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # MCP配置
    MCP_TOOLS_ENABLED: bool = os.getenv("MCP_TOOLS_ENABLED", "true").lower() == "true"
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8003"))
    
    # 执行配置
    MAX_CONCURRENT_EXECUTIONS: int = int(os.getenv("MAX_CONCURRENT_EXECUTIONS", "5"))
    EXECUTION_TIMEOUT: int = int(os.getenv("EXECUTION_TIMEOUT", "300"))
    ENABLE_EXECUTION_LOGGING: bool = os.getenv("ENABLE_EXECUTION_LOGGING", "true").lower() == "true"
    
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