from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

import pytz
from pydantic import BaseModel, ConfigDict, field_validator
from ulid import ULID
__all__ = ["DEFAULT_TZ", "CoreModel", "Pagination", "datetime2str", "datetime_tz_now", "get_ulid", "replace_url_prefix"]

DEFAULT_TZ = timezone(timedelta(hours=0))


def datetime_tz_now() -> datetime:
    now = datetime.now().astimezone()
    now = now.replace(microsecond=round(now.microsecond / 1000) * 1000)
    return now


class Pagination:
    def __init__(self, data: list[Any], limit: int, next_default_key: str = "id"):
        if len(data) == limit + 1:
            _next = getattr(data[-1], next_default_key)
            data = data[:-1]
            has_more = True
        else:
            _next = None
            has_more = False
        self._data = data
        self._has_more = has_more
        self._next = _next

    @property
    def data(self) -> list[object]:
        return self._data

    @property
    def has_more(self) -> bool:
        return self._has_more

    @property
    def next(self) -> Any | None:
        return self._next


def datetime2str(dt: datetime) -> str:
    utc_0 = dt.astimezone(DEFAULT_TZ)
    return f"{utc_0.strftime('%Y-%m-%dT%H:%M:%S.')}{utc_0.strftime('%f')[:3]}Z"


def get_ulid() -> str:
    return str(ULID())


def replace_url_prefix(url: str, prefix: str) -> str:
    """将 url 中的 host 替换为 prefix."""
    if not prefix:
        return url
    parsed_url = urlparse(url)
    return url.replace(f"{parsed_url.scheme}://{parsed_url.netloc}", prefix)


class CoreModel(BaseModel):
    @field_validator("next", mode="before", check_fields=False)
    @classmethod
    def set_next_timezone(cls, v):  # type: ignore
        """确保 next 字段是datetime类型时, 总是使用 +08 时区."""
        if isinstance(v, datetime):
            v = v.replace(tzinfo=DEFAULT_TZ).astimezone(pytz.utc)
        return v

    model_config = ConfigDict(
        # 将 orm 模型中的属性映射到 pydantic 模型中
        from_attributes=True,
        # 自定义序列化器，用于格式化 datetime
        json_encoders={datetime: lambda v: datetime2str(v)},
    )
