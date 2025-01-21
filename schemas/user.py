from typing import List
from pydantic import BaseModel, Field

from .study import StudyStatus, QuestionSubmissionRecord

class UserInfo(BaseModel):
    """用户基本信息"""
    name: str
    avatar: str
    employee_id: str
    class_: str = Field(alias="class")
    department: str
    job_title: str
    study_status: StudyStatus

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "张三",
                "avatar": "https://example.com/avatar.jpg",
                "employee_id": "EMP001",
                "class": "一班",
                "department": "生产部",
                "job_title": "操作员",
                "study_status": {
                    "total_duration": 3600,
                    "practice_count": 100,
                    "correct_count": 80,
                    "knowledge_detail": [
                        {
                            "name": "安全生产",
                            "correct_count": 40,
                            "total": 50,
                            "knowledge_id": "1",
                            "is_important": True
                        }
                    ]
                }
            }
        }

class UserHistoryResponse(BaseModel):
    """用户答题历史响应"""
    history: List[QuestionSubmissionRecord]

    class Config:
        from_attributes = True 