from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.app import get_app
from api.exception import setup_exception_handler
from core.config import settings
from plugins.logger import (
    get_logger,
    mount_access_logger,
    mount_logger,
    setup_access_logger,
    setup_logger,
    update_log_context,
)


def init_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):  # type: ignore
        # FastAPI 启动之前的初始化
        yield
        # FastAPI 结束之前的收尾工作

    # 获取 FastAPI 实例
    cur_app = get_app(settings.fastapi, lifespan=lifespan)  # type: ignore

    # 日志
    logger = setup_logger(settings.logger)
    mount_logger(cur_app, logger)
    access_logger = setup_access_logger(settings.logger)
    mount_access_logger(cur_app, access_logger)

    # 错误处理
    setup_exception_handler(cur_app, get_logger, update_log_context)

    # 文件管理器

    return cur_app


# 配置加载
# 初始化
app: FastAPI = init_app()

if __name__ == "__main__":
    import uvicorn

    # 启动服务
    uvicorn.run(
        app,
        host=settings.fastapi.host,
        port=settings.fastapi.port,
        root_path=settings.fastapi.root_path,
        proxy_headers=True,
    )
