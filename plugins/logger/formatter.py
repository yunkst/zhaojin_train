import http
import json
import logging
from datetime import datetime


# Custom JSON Formatter for file logging
class JsonFormatter(logging.Formatter):
    """Json 日志格式化"""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None):  # noqa: N802
        """UTC 格式化时间"""
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime(datefmt) if datefmt else ct.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def format(self, record: logging.LogRecord):  # noqa: D102
        excluded = ["created", "levelname", "name", "threadName", "funcName", "msg", "args", "message"]
        extra_info = {
            key: value or "N/A"
            for key, value in record.__dict__.items()
            if key not in logging.LogRecord.__dict__ and not key.startswith("__context__::") and key not in excluded
        }
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "trace_id": getattr(record, "__context__::trace_id", "N/A") or "N/A",
            "name": record.name,
            "threadName": record.threadName,
            "funcName": record.funcName,
            "message": record.getMessage(),
            "method": getattr(record, "__context__::method", "N/A"),
            "url": getattr(record, "__context__::url", "N/A"),
            "status_code": getattr(record, "__context__::status_code", "N/A"),
            "process_time": getattr(record, "__context__::process_time", "N/A"),
            "client_ip": getattr(record, "__context__::client_ip", "N/A"),
            "extra": extra_info,
        }
        return json.dumps(log_record, ensure_ascii=False)


# Custom JSON Formatter for access file logging
class AccessJsonFormatter(logging.Formatter):
    """Json 访问日志格式化"""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None):  # noqa: N802
        """UTC 格式化时间"""
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime(datefmt) if datefmt else ct.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def format(self, record: logging.LogRecord):  # noqa: D102
        client_addr, method, path, http_ver, status_code = record.args  # type: ignore
        log_record = {
            "time": self.formatTime(record),
            "name": record.name,
            "level": record.levelname,
            "trace_id": getattr(record, "__context__::trace_id", "N/A") or "N/A",
            "client_addr": client_addr,
            "method": method,
            "path": path,
            "http_ver": http_ver,
            "status_code": str(status_code),
            "msg": http.HTTPStatus(status_code).phrase,
            "thread": record.thread,
        }
        return json.dumps(log_record, ensure_ascii=False)


# ANSI escape codes for colors
COLORS = {
    "NOTSET": "\033[94m",  # Blue
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[1;91m",  # Red
    "FATAL": "\033[1;37;41m",  # Red Background
    "CRITICAL": "\033[1;37;41m",  # Red Background
}

RESET_COLOR = "\033[0m"


# Custom formatter for console logging
class ConsoleFormatter(logging.Formatter):
    """控制台日志格式化"""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None):  # noqa: N802
        """UTC 格式化时间"""
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime(datefmt) if datefmt else ct.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def format(self, record: logging.LogRecord):  # noqa: D102
        trace_id = getattr(record, "__context__::trace_id", "N/A") or "N/A"
        # 获取格式化后的日志消息
        msg = record.getMessage().replace("|", " ").replace("\n", "")
        name = record.name.replace("|", " ").replace("\n", "")
        levelname = record.levelname
        datetime = self.formatTime(record)
        color = COLORS.get(levelname, RESET_COLOR)
        return f"{color}[{datetime}] [{name}/{levelname}] [{trace_id}] {msg}{RESET_COLOR}"


# Custom formatter for console access logging
class AccessConsoleFormatter(logging.Formatter):
    """控制台访问日志格式化"""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None):  # noqa: N802
        """UTC 格式化时间"""
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime(datefmt) if datefmt else ct.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    def format(self, record: logging.LogRecord):  # noqa: D102
        client_addr, method, path, http_ver, status_code = record.args  # type: ignore
        trace_id = getattr(record, "__context__::trace_id", "N/A") or "N/A"
        name = record.name.replace("|", " ").replace("\n", "")
        levelname = record.levelname
        thread = record.thread
        datetime = self.formatTime(record)
        msg = http.HTTPStatus(status_code).phrase
        color = COLORS.get(levelname, RESET_COLOR)
        return (
            f"{color}[{datetime}] [{name}/{levelname}] [{trace_id}] [{client_addr}] "
            f"[{method}] [{path}] [HTTP/{http_ver}] [{status_code}] [{thread}] {msg}{RESET_COLOR}"
        )
