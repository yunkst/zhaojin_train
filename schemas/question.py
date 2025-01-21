from typing import List, Union
from pydantic import BaseModel

class QuestionBase(BaseModel):
    id: int
    question_type: str
    description: str

class SingleSelectionQuestion(QuestionBase):
    options: List[str]

class MultiSelectionQuestion(QuestionBase):
    options: List[str]

class JudgeQuestion(QuestionBase):
    pass

class BlankFillQuestion(QuestionBase):
    pass

class QAQuestion(QuestionBase):
    pass

Question = Union[SingleSelectionQuestion, MultiSelectionQuestion, JudgeQuestion, BlankFillQuestion, QAQuestion]

class AnswerBase(BaseModel):
    analysis: str

class SingleSelectionAnswer(AnswerBase):
    result: int  # 从0开始的选项索引

class MultiSelectionAnswer(AnswerBase):
    result: List[int]  # 从0开始的选项索引列表

class JudgeAnswer(AnswerBase):
    result: bool

class BlankFillAnswer(AnswerBase):
    result: List[str]

class QAAnswer(AnswerBase):
    result: str

Answer = Union[SingleSelectionAnswer, MultiSelectionAnswer, JudgeAnswer, BlankFillAnswer, QAAnswer]

class QuestionResponse(BaseModel):
    total_score: int
    question: Question

class QuestionSet(BaseModel):
    single: List[QuestionResponse]
    multi: List[QuestionResponse]
    judge: List[QuestionResponse]
    blank: List[QuestionResponse]
    qa: List[QuestionResponse]
    time: str

class AnswerSubmission(BaseModel):
    answer: Answer
    time: str  # 问题获取时间

class AnswerHistory(BaseModel):
    id: str
    question: Question
    answer: Answer
    user_answer: Answer 