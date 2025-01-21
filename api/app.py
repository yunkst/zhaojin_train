from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from starlette.types import AppType, Lifespan
from contextvars import ContextVar
from typing import TypeVar, Optional

class FastAPICORSMiddlewareConfig(BaseModel):
    """CORS 中间件配置模型."""

    enable: bool = False
    allow_origins: list[str] = []
    allow_credentials: bool = False
    allow_methods: list[str] = ["GET"]
    allow_headers: list[str] = []
    expose_headers: list[str] = []
    allow_origin_regex: str | None = None
    max_age: int = 600


class FastAPITrustedHostMiddleware(BaseModel):
    """TrustedHost 中间件配置模型."""

    enable: bool = False
    allowed_hosts: list[str] = []
    www_redirect: bool = True


class FastAPIGZipMiddleware(BaseModel):
    """GZip 中间件配置模型."""

    enable: bool = False
    minimum_size: int = 500
    compresslevel: int = 9


class FastAPIConfig(BaseModel):
    """FastAPI 配置模型."""

    host: str = "0.0.0.0"
    port: int = 8000
    swagger: bool = True
    root_path: str = ""
    name: str
    version: str
    description: str = ""
    summary: str = ""
    debug: bool = False
    cors: FastAPICORSMiddlewareConfig = FastAPICORSMiddlewareConfig()
    trusted_hosts: FastAPITrustedHostMiddleware = FastAPITrustedHostMiddleware()
    gzip: FastAPIGZipMiddleware = FastAPIGZipMiddleware()


# 健康检查
async def health():
    return {"status": "ok"}


def gen_lifespan(lifespan: Lifespan[AppType] | None) -> Lifespan[AppType]:
    @asynccontextmanager
    async def _lifespan(app: FastAPI):  # type: ignore
        if lifespan is not None:
            async with lifespan(app):  # type: ignore
                yield
        else:
            yield

    return _lifespan  # type: ignore


def get_app(conf: FastAPIConfig, lifespan: Lifespan[AppType] | None = None) -> FastAPI:
    from .api import v1_router
    # FastAPI 初始化配置
    fastapi_conf: dict[str, object] = {}  # type: ignore
    if not conf.swagger:
        fastapi_conf["docs_url"] = None
        fastapi_conf["redoc_url"] = None
        fastapi_conf["openapi_url"] = None

    app = FastAPI(
        version=conf.version,
        title=conf.name,
        description=conf.description,
        summary=conf.summary,
        debug=conf.debug,
        lifespan=gen_lifespan(lifespan), #type: ignore
        responses={
            400: {"description": "客户端错误"},
            401: {"description": "认证失败"},
            403: {"description": "无权限"},
            404: {"description": "资源未找到"},
            500: {"description": "服务端错误"},
        },
        **fastapi_conf, # type: ignore
    )

    # 健康检查
    app.add_api_route("/health", health, methods=["GET", "POST"], tags=["health"]) # type: ignore

    # 注册路由
    app.include_router(v1_router)

    # CORS 配置
    if conf.cors.enable:
        app.add_middleware(
            CORSMiddleware,
            **conf.cors.model_dump(
                exclude_none=True,
                exclude_defaults=True,
                exclude={"enable"},
            ),
        )
    # Trusted Host 配置
    if conf.trusted_hosts.enable:
        app.add_middleware(
            TrustedHostMiddleware,
            **conf.trusted_hosts.model_dump(
                exclude_none=True,
                exclude_defaults=True,
                exclude={"enable"},
            ),
        )
    # GZip 配置
    if conf.gzip.enable:
        app.add_middleware(
            GZipMiddleware,
            **conf.gzip.model_dump(
                exclude_none=True,
                exclude_defaults=True,
                exclude={"enable"},
            ),
        )
    AppContext.set_app(app)
    return app


T = TypeVar("T")

class AppContext:
    """应用上下文管理"""
    _app: ContextVar[Optional[FastAPI]] = ContextVar("_app", default=None)
    
    @classmethod
    def get_app(cls) -> FastAPI:
        """获取当前应用实例"""
        app = cls._app.get()
        if app is None:
            raise RuntimeError("Application context not set")
        return app
    
    @classmethod
    def set_app(cls, app: FastAPI) -> None:
        """设置当前应用实例"""
        cls._app.set(app)
    
    @classmethod
    def get_state(cls, key: str, default: T = None) -> T:
        """获取应用状态"""
        return getattr(cls.get_app().state, key, default)
