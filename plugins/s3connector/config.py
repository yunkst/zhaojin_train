from pydantic import BaseModel


class S3Config(BaseModel):
    """S3连接器配置"""

    activate: bool = False
    host: str
    user: str
    password: str
    region_name: str = "cn-north-1"
