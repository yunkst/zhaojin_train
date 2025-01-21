import asyncio
import logging
import traceback
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import RequestResponseEndpoint

from error import AppException, ErrCode

__all__ = ["setup_exception_handler"]


async def _async_log(
    request: Request,
    exc: Exception,
    get_logger: Callable[[Request], logging.Logger | logging.LoggerAdapter[logging.Logger]],
):
    """异步日志处理函数"""

    def _log():
        get_logger(request).error(exc, exc_info=True)

    # 在事件循环中执行日志记录
    await asyncio.get_event_loop().run_in_executor(None, _log)


def setup_exception_handler(
    app: FastAPI,
    get_logger: Callable[[Request], logging.Logger | logging.LoggerAdapter[logging.Logger]],
    before_func: Callable[[Request, int], None] = lambda r, c: None,
):
    """设置异常处理器"""

    @app.middleware("http")
    async def handle_call_exception(request: Request, call_next: RequestResponseEndpoint):  # type: ignore
        """异常处理中间间"""
        try:
            return await call_next(request)
        except Exception as exc:
            before_func(request, ErrCode.UNKNOWN.status_code)
            await _async_log(request, exc, get_logger)
            return JSONResponse(
                status_code=ErrCode.UNKNOWN.status_code,
                content=jsonable_encoder({"code": ErrCode.UNKNOWN.code, "message": str(exc)}),
            )

    @app.exception_handler(RequestValidationError)
    async def req_validation_exception_handler(request: Request, exc: RequestValidationError):  # type: ignore
        """处理请求参数验证的异常"""
        before_func(request, ErrCode.VALIDATION.status_code)
        errs = exc.errors()
        logger = get_logger(request)
        logger.warning("req_validation_exception_handler: url=[%s], errs=[%s]", request.url.path, errs)
        return JSONResponse(
            status_code=ErrCode.VALIDATION.status_code,
            content=jsonable_encoder({"code": ErrCode.VALIDATION.code, "message": errs}),
        )

    @app.exception_handler(ResponseValidationError)
    async def resp_validation_exception_handler(request: Request, exc: ResponseValidationError):  # type: ignore
        """处理参数参数验证的异常"""
        before_func(request, ErrCode.UNKNOWN.status_code)
        errs = exc.errors()
        logger = get_logger(request)
        logger.warning("resp_validation_exception_handler: url=[%s], errs=[%s]", request.url.path, errs)
        return JSONResponse(
            status_code=ErrCode.UNKNOWN.status_code,
            content=jsonable_encoder({"code": ErrCode.UNKNOWN.code, "message": errs}),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):  # type: ignore
        """处理客户端请求异常"""
        before_func(request, exc.status_code)
        logger = get_logger(request)
        logger.warning(
            "http_exception_handler: url=[%s], status_code=[%s], message=[%s]",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"code": ErrCode.BAD_REQUEST.code, "message": exc.detail}),
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):  # type: ignore
        """处理自定义异常"""
        before_func(request, exc.status_code)
        # 获取异常的栈回溯信息
        tb = traceback.extract_tb(exc.__traceback__)
        last_tb = tb[-1]  # 获取最后一个回溯信息，即引发异常的地方
        # 打印或记录最后一个引发异常的文件名、函数名和行号
        filename = last_tb.filename.split("/")[-1]
        func_name = last_tb.name
        lineno = last_tb.lineno
        logger = get_logger(request)
        logger.warning(
            "app_exception_handler: url=[%s], code=[%s], filename=[%s], func_name=[%s], lineno=[%s]",
            request.url.path,
            exc.code,
            filename,
            func_name,
            lineno,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"code": exc.code, "message": exc.message}),
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):  # type: ignore
        """处理其他参数验证的异常"""
        before_func(request, ErrCode.UNKNOWN.status_code)
        logger = get_logger(request)
        logger.error("validation_exception_handler: url=[%s]", request.url.path)
        logger.error(exc, exc_info=True)
        return JSONResponse(
            status_code=ErrCode.UNKNOWN.status_code,
            content=jsonable_encoder({"code": ErrCode.UNKNOWN.code, "message": ErrCode.UNKNOWN.message}),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):  # type: ignore
        """处理服务端异常, 全局异常处理"""
        before_func(request, ErrCode.UNKNOWN.status_code)
        logger = get_logger(request)
        logger.error("global_exception_handler: url=[%s]", request.url.path)
        logger.error(exc, exc_info=True)
        return JSONResponse(
            status_code=ErrCode.UNKNOWN.status_code,
            content=jsonable_encoder({"code": ErrCode.UNKNOWN.code, "message": ErrCode.UNKNOWN.message}),
        )
