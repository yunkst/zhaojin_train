from pydantic import BaseModel


class Coder(BaseModel):
    # HTTP 响应码
    status_code: int
    # 业务错误码
    code: int
    # 错误信息
    message: str


class ErrCode:
    """错误码"""

    UNKNOWN = Coder(status_code=500, code=100002, message="Internal server error")
    BAD_REQUEST = Coder(status_code=400, code=100003, message="Bad request")
    VALIDATION = Coder(status_code=400, code=100004, message="Validation failed")
    TOKEN_INVALID = Coder(status_code=401, code=100101, message="Token invalid")
    PERMISSION_DENIED = Coder(status_code=403, code=100101, message="Permission denied")
    TASK_NOT_FOUND = Coder(status_code=404, code=110001, message="Task not found")


# =========================================================================================== #

__all__ = ["ErrCode", "AppException"]


class AppException(Exception):  # noqa: N818
    """业务异常"""

    def __init__(self, coder: Coder, *, detail: str | None = None):
        """Initialize the AppException with the given Coder.

        Parameters
        ----------
        coder: Coder
            错误码
        detail: str
            附加信息

        Examples
        --------
        >>> raise AppException(ErrCode.BAD_REQUEST)
        >>> raise AppException(ErrCode.BAD_REQUEST, detail="Bad request")

        """
        super().__init__()
        self._status_code: int = coder.status_code
        self._code: int = coder.code
        self._message: str = coder.message
        if detail:
            self._message = f"{self._message} ({detail})"

    @property
    def status_code(self) -> int:  # noqa: D102
        return self._status_code

    @property
    def code(self) -> int:  # noqa: D102
        return self._code

    @property
    def message(self) -> str:  # noqa: D102
        return self._message

    def __str__(self) -> str:  # noqa: D105
        return f"{self.code}: {self.message}"
