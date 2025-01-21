import logging
from time import time
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel


class LogContext(BaseModel):
    """日志上下文"""

    trace_id: str | None
    process_time: float
    status_code: str
    method: str
    url: str
    client_ip: str | None
    start_time: float
    is_error: bool = False


# Dependency to get logger with trace id
def get_logger(request: Request) -> logging.LoggerAdapter[logging.Logger]:
    logger: logging.Logger = request.app.state.truthai_logger
    context: LogContext = request.state.truthai_logger__log_context
    adapter = logging.LoggerAdapter(
        logger,
        {
            "__context__::trace_id": context.trace_id,
            "__context__::method": context.method,
            "__context__::url": context.url,
            "__context__::status_code": context.status_code,
            "__context__::process_time": context.process_time,
            "__context__::client_ip": context.client_ip,
        },
    )
    return adapter


# Dependency to get access logger with trace id
def get_access_logger(request: Request) -> logging.LoggerAdapter[logging.Logger]:
    access_logger: logging.Logger = request.app.state.truthai_access_logger
    context: LogContext = request.state.truthai_logger__log_context
    adapter = logging.LoggerAdapter(
        access_logger,
        {
            "__context__::trace_id": context.trace_id,
            "__context__::method": context.method,
            "__context__::url": context.url,
            "__context__::status_code": context.status_code,
            "__context__::process_time": context.process_time,
            "__context__::client_ip": context.client_ip,
        },
    )
    return adapter


def get_trace_id(request: Request) -> str | None:
    return request.state.truthai_logger__log_context.trace_id


def update_log_context(request: Request, status_code: int):
    log_context = request.state.truthai_logger__log_context
    if not log_context:
        return
    # 请求请求执行后
    log_context.is_error = True
    log_context.process_time = round(time() - log_context.start_time, 6)
    log_context.status_code = str(status_code)
    request.state.truthai_logger__log_context = log_context


def mount_logger(app: FastAPI, logger: logging.Logger) -> None:
    app.state.truthai_logger = logger

    # Middleware to add trace-id to each request
    @app.middleware("http")
    async def add_log_context(request: Request, call_next: Any):  # type: ignore
        trace_id = request.headers.get("Request-Id", "")
        # 请求执行前
        log_context = LogContext(
            trace_id=trace_id if trace_id else None,
            process_time=-1.0,
            status_code="",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            start_time=time(),
        )
        request.state.truthai_logger__log_context = log_context
        # 请求执行
        response = await call_next(request)
        # 请求请求执行后
        if request.state.truthai_logger__log_context.is_error:
            log_context = request.state.truthai_logger__log_context
            # 统一异常处理
            status_code = log_context.status_code
            process_time = log_context.process_time
        else:
            # 正常返回
            status_code = response.status_code
            process_time = round(time() - log_context.start_time, 6)
        log_context.status_code = status_code
        log_context.process_time = process_time
        request.state.truthai_logger__log_context = log_context

        if trace_id:
            response.headers["Request-Id"] = trace_id
        return response


def mount_access_logger(app: FastAPI, access_logger: logging.Logger) -> None:
    app.state.truthai_access_logger = access_logger
