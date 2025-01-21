from typing import Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import APIError

def add_exception_handlers(app: FastAPI) -> None:
    """添加异常处理器"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """处理自定义 API 错误"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail
            },
            headers=exc.headers
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """处理请求参数验证错误"""
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "Validation error"
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request,
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """处理数据库错误"""
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Database error"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理未捕获的异常"""
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal server error"
            }
        ) 