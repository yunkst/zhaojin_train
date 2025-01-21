from typing import List
from datetime import datetime
from pydantic import BaseModel
from schemas.v1.question import Answer, Question

class KnowledgeDetail(BaseModel):
    """知识点掌握情况"""
    name: str
    correct_count: int
    total: int
    knowledge_id: str
    is_important: bool

    class Config:
        from_attributes = True

class StudyStatus(BaseModel):
    """学习详情"""
    total_duration: int
    practice_count: int
    correct_count: int
    knowledge_detail: List[KnowledgeDetail]

    class Config:
        from_attributes = True

class QuestionSubmissionRecord(BaseModel):
    """答题记录"""
    question_id: int
    is_correct: bool
    answer: str
    submitted_at: datetime
    duration: int  # 答题用时(秒)
    knowledge_id: str
    knowledge_name: str

    class Config:
        from_attributes = True

class QuestionSubmissionRecordResponse(BaseModel):
    """答题历史记录响应模型"""
    id :str
    question: Question
    answer: Answer
    user_answer: Answer
    is_correct: bool
