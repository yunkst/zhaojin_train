from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric, JSON, Index
from schemas.v1.question import Answer, Option, JudgeAnswer, SingleSelectionAnswer, MultiSelectionAnswer, BlankFillAnswer, QAAnswer
from .base import BaseModel
from .user import User
class Knowledge(BaseModel):
    """知识点"""
    __tablename__ = "knowledge"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # 关系
    questions: Mapped[List["Question"]] = relationship(back_populates="knowledge")
    user_eases: Mapped[List["UserKnowledgeEase"]] = relationship(back_populates="knowledge")

class Question(BaseModel):
    """题目"""
    __tablename__ = "question"

    difficulty: Mapped[float] = mapped_column(
        Numeric(8,6),
        nullable=False
    )
    knowledge_id: Mapped[int] = mapped_column(ForeignKey("knowledge.id"), nullable=False)

    # 关系
    knowledge: Mapped[Optional[Knowledge]] = relationship(back_populates="questions")
    study_cards: Mapped[List["UserQuestionStudyCard"]] = relationship(back_populates="question")
    submission_records: Mapped[List["UserQuestionSubmissionRecord"]] = relationship(back_populates="question")

    # 从meta中提取的属性
    @property
    def question_type(self) -> str:
        """题目类型"""
        return self.meta.get("type", "")
    
    @property
    def options(self) -> List[Option]:
        return self.meta.get("options", [])
    
    @property
    def correct_answer(self) -> Answer:
        """正确答案"""
        if self.question_type == "judge":
            return JudgeAnswer(**self.meta.get("correct_answer", {'analysis': '', 'result': ''}))
        elif self.question_type == "single":
            return SingleSelectionAnswer(**self.meta.get("correct_answer", {'analysis': '', 'result': Option(index=0, content='', option_name='')}))
        elif self.question_type == "multi":
            return MultiSelectionAnswer(**self.meta.get("correct_answer", {'analysis': '', 'result': []}))
        elif self.question_type in ["blank"]:
            return BlankFillAnswer(**self.meta.get("correct_answer", {'analysis': '', 'result': []}))
        return QAAnswer(**self.meta.get("correct_answer", {'analysis': '', 'result': ''}))
    
    @property
    def description(self) -> str:
        """题目描述"""
        return self.meta.get("description", "")
    
    # 索引
    __table_args__ = (
        Index("ix_question_knowledge_id", "knowledge_id"),
    )

class UserQuestionSubmissionRecord(BaseModel):
    """用户答题记录"""
    __tablename__ = "user_question_submission_record"

    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # 关系
    question: Mapped[Optional[Question]] = relationship(back_populates="submission_records")
    user: Mapped[Optional[User]] = relationship()
# 索引
    __table_args__ = (
        Index("ix_user_question_submission_record_question_id", "question_id"),
        Index("ix_user_question_submission_record_user_id", "user_id"),
        Index("ix_user_question_submission_record_created_at", "created_at"),
    )
    # 从meta中提取的属性
    @property
    def is_correct(self) -> bool:
        """是否正确"""
        return self.meta.get("is_correct", False)
    
    @property
    def answer(self) -> Answer:
        """用户答案"""
        from services.study import AnswerService
        return AnswerService.make_answer(self.meta.get("answer", {}), self.question.question_type) # type: ignore
    
    @property
    def duration(self) -> int:
        """答题用时(秒)"""
        return self.meta.get("duration", 0)
    
    @property
    def submitted_at(self) -> datetime:
        """提交时间"""
        return datetime.fromisoformat(self.meta.get("submitted_at", ""))

    @property
    def knowledge_id(self) -> int:
        """获取知识点ID"""
        return self.question.knowledge_id if self.question else 0

    @property
    def knowledge(self) -> Optional[Knowledge]:
        """获取知识点"""
        return self.question.knowledge if self.question else None

    # 索引
    __table_args__ = (
        Index("ix_user_question_submission_record_question_id", "question_id"),
        Index("ix_user_question_submission_record_user_id", "user_id"),
        Index("ix_user_question_submission_record_created_at", "created_at"),
    )

class UserQuestionStudyCard(BaseModel):
    """用户学习卡片"""
    __tablename__ = "user_question_study_card"

    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    card_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False
    )
    due: Mapped[datetime] = mapped_column(nullable=False)
    last_study_time: Mapped[Optional[datetime]]
    study_count: Mapped[int] = mapped_column(nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(nullable=False, default=0)
    adaptivity_easy_factor: Mapped[float] = mapped_column(
        Numeric(8,6),
        nullable=False
    )
    ease: Mapped[float] = mapped_column(
        Numeric(8,6),
        nullable=False
    )

    # 关系
    question: Mapped[Optional[Question]] = relationship(back_populates="study_cards")
    user: Mapped[Optional[User]] = relationship()

    # 索引
    __table_args__ = (
        Index("ix_user_question_study_card_question_id", "question_id"),
        Index("ix_user_question_study_card_user_id", "user_id"),
        Index("ix_user_question_study_card_due", "due"),
    )

class UserKnowledgeEase(BaseModel):
    """用户知识点熟练度"""
    __tablename__ = "user_knowledge_ease"

    knowledge_id: Mapped[int] = mapped_column(ForeignKey("knowledge.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    ease: Mapped[float] = mapped_column(
        Numeric(8,6),
        nullable=False
    )

    # 关系
    knowledge: Mapped[Optional[Knowledge]] = relationship(back_populates="user_eases")
    user: Mapped[Optional[User]] = relationship()

    # 索引
    __table_args__ = (
        Index("ix_user_knowledge_ease_knowledge_id", "knowledge_id"),
        Index("ix_user_knowledge_ease_user_id", "user_id"),
    ) 