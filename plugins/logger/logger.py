import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import cast

from .config import LoggerConfig, LogLevel, StreamLoggerConfig, StreamLoggerType
from .formatter import AccessConsoleFormatter, AccessJsonFormatter, ConsoleFormatter, JsonFormatter

__default_logger_config = LoggerConfig(name="main", level=LogLevel.DEBUG, stream_logger=StreamLoggerConfig())

__logger_map: dict[str, logging.Logger] = {}
__access_logger_map: dict[str, logging.Logger] = {}


class SkipPathFilter(logging.Filter):
    """日志过滤器，用于跳过指定路径"""

    def __init__(self, paths_to_skip: list[str]):
        super().__init__()
        self.paths_to_skip = paths_to_skip

    def filter(self, record: logging.LogRecord):
        # 检查日志记录中的路径
        return record.args[2] not in self.paths_to_skip  # type: ignore


def setup_logger(config: LoggerConfig = __default_logger_config) -> logging.Logger:
    if config.name in __logger_map:
        return __logger_map[config.name]

    logger = logging.getLogger(config.name)
    logger.setLevel(config.level.value)

    if config.file_logger and config.file_logger.enable:
        log_file = Path(config.file_logger.path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = cast(
            logging.Handler,
            TimedRotatingFileHandler(
                log_file,
                encoding="utf-8",
                when=config.file_logger.when,
                interval=config.file_logger.interval,
                backupCount=config.file_logger.backup_count,
                errors="replace",
            ),
        )
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    if config.stream_logger and config.stream_logger.enable:
        stream_handler: logging.Handler | None = None

        if config.stream_logger.type == StreamLoggerType.STDOUT:
            stream_handler = logging.StreamHandler(stream=sys.stdout)
        elif config.stream_logger.type == StreamLoggerType.STDERR:
            stream_handler = logging.StreamHandler(stream=sys.stderr)
        if stream_handler:
            stream_handler.setFormatter(ConsoleFormatter())
            logger.addHandler(stream_handler)

    __logger_map[config.name] = logger
    return logger


def setup_access_logger(config: LoggerConfig = __default_logger_config) -> logging.Logger:
    logger_name = "uvicorn.access"
    if logger_name in __access_logger_map:
        return __access_logger_map[logger_name]

    # 获取 uvicorn 的访问日志记录器
    access_logger = logging.getLogger(logger_name)
    # 创建并添加过滤器
    skip_health_filter = SkipPathFilter(["/health"])
    access_logger.addFilter(skip_health_filter)
    # 替换默认的 Formatter
    for handler in access_logger.handlers:
        handler.setFormatter(AccessConsoleFormatter())

    if config.file_access_logger and config.file_access_logger.enable:
        access_log_file = Path(config.file_access_logger.path)
        access_log_file.parent.mkdir(parents=True, exist_ok=True)
        access_handler = cast(
            logging.Handler,
            TimedRotatingFileHandler(
                access_log_file,
                encoding="utf-8",
                when=config.file_access_logger.when,
                interval=config.file_access_logger.interval,
                backupCount=config.file_access_logger.backup_count,
                errors="replace",
            ),
        )
        access_handler.setFormatter(AccessJsonFormatter())
        access_logger.addHandler(access_handler)

    __access_logger_map[logger_name] = access_logger
    return access_logger
