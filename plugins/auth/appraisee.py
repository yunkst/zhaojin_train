import aiohttp
from fastapi import HTTPException, status


class Appraisee:
    """被鉴权者"""

    def __init__(self, *, enforce_url: str, id: int, token: str, skip_enforce: bool = False):  # noqa: A002, D107
        self._enforce_url = enforce_url
        self._id = id
        self._token = token
        self._skip_enforce = skip_enforce

    @property
    def id(self) -> int:  # noqa: D102
        return self._id

    @property
    def token(self) -> str:  # noqa: D102
        return self._token

    async def batch_can(self, permissions: list[tuple[str, str]]) -> tuple[bool, ...]:
        """批量执行被鉴权者权限检查

        Parameters
        ----------
        permissions : list[tuple[str, str]]
            包含对象和操作的元组列表。每个元组表示一个需要检查的权限。
            元组的第一个元素是对象，第二个元素是操作。

        Returns
        -------
        tuple[bool, ...]
            每个布尔值表示一个权限检查的结果。

        """
        permission_number = len(permissions)
        if len(permissions) <= 0:
            return ()
        if self._skip_enforce:
            return (True,) * permission_number
        if not self._enforce_url:
            # 安全起见，没有就是 False
            return (False,) * permission_number
        async with (
            aiohttp.ClientSession(headers={"Authorization": f"Bearer {self._token}"}) as session,
            session.post(
                self._enforce_url,
                json={"user_id": self._id, "permissions": [{"object": o, "action": a} for o, a in permissions]},
            ) as response,
        ):
            data: dict[str, object] = await response.json()
            status_code = response.status
        try:
            assert status_code == 200
            results = data["results"]
            assert isinstance(results, list)
            assert len(results) == permission_number  # type: ignore
            return tuple(results)  # type: ignore
        except:  # noqa: E722
            return (False,) * permission_number

    async def can(self, obj: str, action: str, response_403_when_cannot: bool = False) -> bool:
        """检查被鉴权者是否被允许某个权限

        Parameters
        ----------
        obj : str
            权限节点(对象)
        action : str
            权限动作
        response_403_when_cannot : bool, optional
            在没有权限时是否直接抛出 403 的 HTTP 异常(就是直接返回 403 响应), 默认为 False

        Returns
        -------
        bool
            是否有权限

        Raises
        ------
        HTTPException
            403 响应, 表示用户没有该权限

        Examples
        --------
        >>> appraisee.can("book", "read")

        """
        result = (await self.batch_can([(obj, action)]))[0]
        if not result and response_403_when_cannot:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return result
