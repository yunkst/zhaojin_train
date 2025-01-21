from fastapi import APIRouter

from core.config import settings
from .v1 import auth, users, questions, leaderboard

# API v1 路由
v1_router = APIRouter(prefix=settings.API_V1_STR)

# 注册v1版本的所有路由
v1_router.include_router(auth.router)
v1_router.include_router(users.router)
v1_router.include_router(questions.router)
v1_router.include_router(leaderboard.router)

# API v2 路由 (未来添加)
# v2_router = APIRouter(prefix=settings.API_V2_STR) 