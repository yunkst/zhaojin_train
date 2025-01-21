import aiohttp
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from .appraisee import Appraisee
from .config import AuthConfig

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="")


async def get_appraisee(request: Request, token: str = Depends(OAUTH2_SCHEME)) -> Appraisee:
    return await request.app.state.truthai_auth(token)


class Authenticator:
    """用户鉴权模块"""

    def __init__(self, config: AuthConfig):
        """实例化一个鉴权器

        Parameters
        ----------
        config: AuthConfig
            配置

        """
        self._verify_url = config.verify_url
        self._enforce_url = config.enforce_url
        self._skip_enforce = config.skip_enforce
        self._skip_verify = config.skip_verify
        self._default_user_id = config.default_user_id
        self._default_user_token = config.default_user_token

    def mount_app(self, app: FastAPI) -> None:  # noqa: D102
        app.state.truthai_auth = self

    async def __call__(self, token: str) -> Appraisee:  # noqa: D102
        if self._skip_verify:
            return Appraisee(
                enforce_url=self._enforce_url,
                id=self._default_user_id,
                token=self._default_user_token,
                skip_enforce=self._skip_enforce,
            )
        try:
            async with (
                aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"}) as session,
                session.post(
                    self._verify_url,
                ) as response,
            ):
                data: dict[str, object] = await response.json()
                status_code = response.status
            if status_code != 200:
                detail = str(data.get("detail", "N/A"))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Could not validate credentials: {detail}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user_id_str = str(data.get("user_id", "Unknown"))
            if not user_id_str.isdigit():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials: Invalid User ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            appraisee = Appraisee(
                enforce_url=self._enforce_url,
                id=int(user_id_str),
                token=token,
                skip_enforce=self._skip_enforce,
            )
            return appraisee
        except Exception as exc:
            if isinstance(exc, HTTPException):
                raise exc from exc
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {exc}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
