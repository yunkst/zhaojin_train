from typing import List
from pydantic import BaseModel

from ..base.user import UserBase

class KnowledgeDetail(BaseModel):
    name: str
    correct_count: int
    total: int
    knowledge_id: str
    is_important: bool

    model_config = {"from_attributes": True}

class StudyDetail(BaseModel):
    total_duration: int
    practice_count: int
    correct_count: int
    knowledge_detail: List[KnowledgeDetail]

    model_config = {"from_attributes": True}

class UserInfo(UserBase):
    study_status: StudyDetail

    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    employee_id: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 