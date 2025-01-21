from enum import Enum

from pydantic import BaseModel, field_validator


class LogLevel(str, Enum):
    """日志级别."""

    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class StreamLoggerType(str, Enum):
    """流日志器类型."""

    STDOUT = "STDOUT"
    STDERR = "STDERR"
    NONE = "NONE"


class FileLoggerConfig(BaseModel):
    """文件日志器配置."""

    enable: bool = True
    path: str
    when: str = "midnight"
    interval: int = 1
    backup_count: int = 7


class StreamLoggerConfig(BaseModel):
    """流日志器配置."""

    enable: bool = True
    type: StreamLoggerType = StreamLoggerType.STDOUT

    @field_validator("type", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> StreamLoggerType:
        """验证流日志器类型."""
        if isinstance(value, str):
            value_upper = value.upper()
            if value_upper in StreamLoggerType.__members__:
                return StreamLoggerType[value_upper]
        return StreamLoggerType.STDOUT


class FileAccessLoggerConfig(BaseModel):
    """文件访问日志器配置."""

    enable: bool = False
    path: str
    when: str = "midnight"
    interval: int = 1
    backup_count: int = 7


class LoggerConfig(BaseModel):
    """日志器配置."""

    level: LogLevel = LogLevel.INFO
    name: str
    file_logger: FileLoggerConfig | None = None
    stream_logger: StreamLoggerConfig | None = None
    file_access_logger: FileAccessLoggerConfig | None = None

    @field_validator("level", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> LogLevel:
        """验证日志级别."""
        if isinstance(value, str):
            value_upper = value.upper()
            if value_upper in LogLevel.__members__:
                return LogLevel[value_upper]
        return LogLevel.INFO
