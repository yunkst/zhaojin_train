from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel
import yaml
from api.app import FastAPIConfig
from plugins.logger.config import LoggerConfig, LogLevel, FileLoggerConfig, StreamLoggerConfig, FileAccessLoggerConfig, StreamLoggerType
class PostgresSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    db: str = "zhaojin"
    user: str = "postgres"
    password: str = "postgres"

class Settings(BaseModel):
    DEBUG_MODE: bool = False
    fastapi: FastAPIConfig = FastAPIConfig(
        name="zhaojin",
        version="1.0.0",
        description="招金培训系统后端 API 文档",
        summary="招金培训系统后端 API 文档",
        debug=DEBUG_MODE,
    )
    API_V1_STR: str = "/v1"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*30  # 30天
    postgres: PostgresSettings = PostgresSettings()
    logger: LoggerConfig = LoggerConfig(
        level=LogLevel.INFO,
        name="zhaojin",
        file_logger=FileLoggerConfig(path="logs/zhaojin.log"),
        stream_logger=StreamLoggerConfig(type=StreamLoggerType.STDOUT),
        file_access_logger=FileAccessLoggerConfig(path="logs/access.log"),
    )
    backend_cors_origins: List[str] = ["*"]

    @property
    def DATABASE_URL(self) -> str:
        """构建数据库 URL"""
        return f"postgresql+asyncpg://{self.postgres.user}:{self.postgres.password}@{self.postgres.host}:{self.postgres.port}/{self.postgres.db}"

def load_config(config_path: str = "config.yaml") -> Settings:
    """从YAML文件加载配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    return Settings.model_validate(config_dict)

settings = load_config()