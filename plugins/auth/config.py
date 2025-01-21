from pydantic import BaseModel


class AuthConfig(BaseModel):
    """鉴权模块配置."""

    enforce_url: str
    verify_url: str
    skip_enforce: bool = False
    skip_verify: bool = False
    default_user_id: int = 0
    default_user_token: str = ""
