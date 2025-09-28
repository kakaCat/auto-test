"""配置管理模块 - 极简版
Configuration Management Module - Simplified

采用极简配置管理，专注于环境变量和默认值
"""

import os
from pathlib import Path
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

    def __post_init__(self) -> None:
        """标准化数据库路径，避免因工作目录不同而产生多个 SQLite 文件。

        规则：
        - 若设置了 `DATABASE_PATH`：
          - 支持 `~`，自动展开；
          - 若为相对路径，则相对于仓库根目录解析为绝对路径；
        - 若未设置：统一使用仓库根目录下的 `auto_test.db`；
        - 若 `DATABASE_URL` 为 SQLite 或未显式设置，则与 `DATABASE_PATH` 保持一致。
        """
        # 仓库根目录：.../auto-test
        repo_root = Path(__file__).resolve().parents[3]

        # 处理 DATABASE_PATH -> 绝对路径
        db_path_env = os.getenv("DATABASE_PATH")
        if db_path_env and db_path_env.strip():
            p = Path(db_path_env).expanduser()
            if not p.is_absolute():
                p = (repo_root / p).resolve()
        else:
            p = (repo_root / "auto_test.db").resolve()

        self.DATABASE_PATH = str(p)

        # 若 DATABASE_URL 未设置或为 sqlite，确保与 DATABASE_PATH 一致
        db_url_env = os.getenv("DATABASE_URL")
        if not db_url_env or db_url_env.startswith("sqlite:///"):
            self.DATABASE_URL = f"sqlite:///{self.DATABASE_PATH}"

# 全局配置实例
config = Config()

def get_config() -> Config:
    """获取配置实例"""
    return config