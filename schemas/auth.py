from pydantic import BaseModel

class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    """登录请求模型"""
    employee_id: str
    password: str 