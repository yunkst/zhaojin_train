from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

DataT = TypeVar("DataT")

class ResponseBase(BaseModel):
    code: int = 200
    message: str = "Success"

class DataResponse(ResponseBase, Generic[DataT]):
    data: Optional[DataT] = None

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 30

class PaginatedResponse(ResponseBase, Generic[DataT]):
    data: list[DataT]
    total: int
    page: int
    page_size: int 