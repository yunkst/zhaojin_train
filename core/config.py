from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from plugins.logger.config import LoggerConfig, LogLevel, FileLoggerConfig, StreamLoggerConfig, FileAccessLoggerConfig, StreamLoggerType
from api.app import FastAPIConfig

class Settings(BaseSettings):
    # 调试模式
    DEBUG_MODE: bool = False
    
    # FastAPI配置
    fastapi: FastAPIConfig = FastAPIConfig(
        name="zhaojin",
        version="1.0.0",
        description="招金培训系统后端 API 文档",
        summary="招金培训系统后端 API 文档",
        debug=DEBUG_MODE,
    )
    
    # API配置
    API_V1_STR: str = "/v1"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*30 # 30天
    
    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "zhaojin"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    

    # 日志配置
    logger: LoggerConfig = LoggerConfig(
        level=LogLevel.INFO,
        name="zhaojin",
        file_logger=FileLoggerConfig(path="logs/zhaojin.log"),
        stream_logger=StreamLoggerConfig(type=StreamLoggerType.STDOUT),
        file_access_logger=FileAccessLoggerConfig(path="logs/access.log")
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """构建数据库 URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="APP_"
    )

@lru_cache
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 确保只创建一次实例
    """
    return Settings()

settings = get_settings() 