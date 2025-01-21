from typing import List, Union, Optional
from pydantic import BaseModel
from datetime import datetime

class Option(BaseModel):
    """选项"""
    index: int  # 序列,给选项排序
    content: Optional[str] = None # 选项内容
    option_name: str  # 序列名,比如 A B C 这种选项名

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """题目基类"""
    id: int
    question_type: str
    description: str

    class Config:
        from_attributes = True

class SingleSelectionQuestion(QuestionBase):
    """单选题"""
    options: List[Option]

class MultiSelectionQuestion(QuestionBase):
    """多选题"""
    options: List[Option]

class JudgeQuestion(QuestionBase):
    """判断题"""
    pass

class BlankFillQuestion(QuestionBase):
    """填空题"""
    pass

class QAQuestion(QuestionBase):
    """问答题"""
    pass

Question = Union[SingleSelectionQuestion, MultiSelectionQuestion, JudgeQuestion, BlankFillQuestion, QAQuestion]

class QuestionResponse(BaseModel):
    question: Question
    time: datetime
    
class AnswerBase(BaseModel):
    """答案基类"""
    analysis: Optional[str] = None

    class Config:
        from_attributes = True

class SingleSelectionAnswer(AnswerBase):
    """单选题答案"""
    result: Option  # 选中的选项

class MultiSelectionAnswer(AnswerBase):
    """多选题答案"""
    result: List[Option]  # 选中的选项列表

class JudgeAnswer(AnswerBase):
    """判断题答案"""
    result: bool

class BlankFillAnswer(AnswerBase):
    """填空题答案"""
    result: List[str]

class QAAnswer(AnswerBase):
    """问答题答案"""
    result: str

Answer = Union[SingleSelectionAnswer, MultiSelectionAnswer, JudgeAnswer, BlankFillAnswer, QAAnswer]

class AnswerSubmission(BaseModel):
    """答案提交"""
    answer: Answer
    time: datetime  # 问题获取时间

class AnswerHistory(BaseModel):
    """答题历史"""
    id: str
    question: Question
    answer: Answer  # 正确答案
    user_answer: Answer  # 用户答案
    is_correct: bool  # 是否正确

    class Config:
        from_attributes = True 