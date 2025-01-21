from typing import Optional, Sequence, Any
from sqlmodel import select, func, SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.study import (
    Knowledge, Question, UserQuestionSubmissionRecord,
)
from models.stats import StatInfo, StatType
from schemas.study import StudyStatus, KnowledgeDetail
from schemas.v1.question import (
    Question as QuestionSchema, SingleSelectionQuestion, MultiSelectionQuestion,
    JudgeQuestion, BlankFillQuestion, QAQuestion,Answer,AnswerHistory,
     MultiSelectionAnswer,JudgeAnswer,SingleSelectionAnswer,BlankFillAnswer,QAAnswer,Option
)
from core.exceptions import ValidationError,NotFoundError
from datetime import datetime,UTC
from .base import BaseService


class UserStats(SQLModel):
    """用户统计信息"""
    total_duration: int = Field(sa_type=Integer)
    practice_count: int = Field(sa_type=Integer)
    correct_count: int = Field(sa_type=Integer)

class KnowledgeStats(SQLModel):
    """知识点统计信息"""
    id: int = Field(sa_type=Integer)
    name: str
    is_important: str
    total: int = Field(sa_type=Integer)
    correct_count: int = Field(sa_type=Integer)

class KnowledgeService:
    """知识点服务"""
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[Knowledge]:
        result = await db.execute(select(Knowledge).where(Knowledge.id == id))
        return result.scalar_one_or_none()

class AnswerService:
    """答案服务"""
    @classmethod
    def make_answer(cls, answer: dict[str, Any],question_type: str) -> Answer:
        """生成答案"""
        if question_type == "judge":
            return JudgeAnswer(analysis=answer.get("analysis", ""),result=answer.get("result", ""))
        elif question_type == "single":
            return SingleSelectionAnswer(analysis=answer.get("analysis", ""),result=Option(index=answer.get("result", {}).get("index", 0),content=answer.get("result", {}).get("content", ""),option_name=answer.get("result", {}).get("option_name", "")))
        elif question_type == "multi":
            return MultiSelectionAnswer(analysis=answer.get("analysis", ""),result=[Option(index=r.get("index", 0),content=r.get("content", ""),option_name=r.get("option_name", "")) for r in answer.get("result", [])])
        elif question_type in ["qa"]:
            return QAAnswer(analysis=answer.get("analysis", ""),result=answer.get("result", ""))
        elif question_type in ["blank"]:
            return BlankFillAnswer(analysis=answer.get("analysis", ""),result=[r.get("result", "") for r in answer.get("result", [])])
        else:
            raise ValidationError(message=f"Question type {question_type} is not supported")

class QuestionService:
    """题目服务"""
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[Question]:
        raise NotImplementedError
    @classmethod
    async def make_answer_history(cls,submission_id:str, question: Question, answer: Answer) -> AnswerHistory:
        """生成答题历史"""
        return AnswerHistory(
            id=submission_id,
            question=question, # type: ignore
            answer=question.correct_answer,
            user_answer=answer
        )
    @classmethod
    async def judge_multi_answer(cls, answer: MultiSelectionAnswer,correct_answer: MultiSelectionAnswer) -> bool:
        """判断多选题答案是否正确"""
        user_answers = set([r.index for r in answer.result])
        correct_answers = set([r.index for r in correct_answer.result])
        return user_answers == correct_answers

    

    async def select_questions(self, db: AsyncSession, user_id: int, knowledge_id: str | None = None) -> QuestionSchema:
        """选取题目
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            knowledge_id: 知识点ID,如果指定则只选择该知识点下的题目
            
        Returns:
            QuestionSchema: 题目
        """
        # 构建基础查询
        stmt = (
            select(Question)
            .outerjoin(
                UserQuestionSubmissionRecord,
                (UserQuestionSubmissionRecord.question_id == Question.id) &
                (UserQuestionSubmissionRecord.user_id == user_id)
            )
            .where(UserQuestionSubmissionRecord.id.is_(None))  # 筛选未做过的题目
        )
        
        # 如果指定了knowledge_id,添加筛选条件
        if knowledge_id:
            stmt = stmt.where(Question.knowledge_id == int(knowledge_id))
            
        # 限制返回一条记录
        stmt = stmt.limit(1)
            
        # 执行查询
        db_result = await db.execute(stmt)
        q = db_result.scalar_one_or_none()
        if not q:
            raise NotFoundError(message="Question not found")
        # 转换为对应的schema
                
        question_data = {
            "id": q.id,
            "description": q.description,
            "question_type": q.question_type,
        }
        
        if q.question_type == "single":
            question_data["options"] = q.options # type: ignore
            return SingleSelectionQuestion.model_validate(question_data)
        elif q.question_type == "multi":
            question_data["options"] = q.options # type: ignore
            return MultiSelectionQuestion.model_validate(question_data)
        elif q.question_type == "judge":
            return JudgeQuestion.model_validate(question_data)
        elif q.question_type == "blank":
            return BlankFillQuestion.model_validate(question_data)
        elif q.question_type == "qa":
            return QAQuestion.model_validate(question_data)
        else:
            raise ValidationError(message=f"Question type {q.question_type} is not supported")

class UserQuestionSubmissionService(BaseService[UserQuestionSubmissionRecord]):
    """用户答题记录服务"""
    def __init__(self):
        super().__init__(UserQuestionSubmissionRecord)
    @classmethod
    async def update_user_stats(
        cls,
        db: AsyncSession,
        user_id: int,
        duration: int,
        is_correct: bool,
        question_id: int
    ) -> None:
        """更新用户统计数据
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            duration: 答题用时
            is_correct: 是否正确
            question_id: 题目ID
        """
        # 查询question_id 是否在 record 中，如果存在，计数不增加，如果已经正确，那正确也不增加
        stmt = select(UserQuestionSubmissionRecord).where(
            UserQuestionSubmissionRecord.question_id == question_id,
            UserQuestionSubmissionRecord.user_id == user_id
        )
        result = await db.execute(stmt)
        record = None
        for r, in result: # 如果有正确的就用正确的
            record = r
            if r.is_correct:
                break

        # 获取题目的知识点ID
        question_stmt = select(Question).where(Question.id == question_id)
        question_result = await db.execute(question_stmt)
        question = question_result.scalar_one_or_none()
        if not question:
            return
        
        knowledge_id = question.knowledge_id

        # 更新学习时长统计
        duration_stat = await db.execute(
            select(StatInfo).where(
                StatInfo.type == StatType.DURATION,
                StatInfo.source_id == user_id
            )
        )
        duration_info = duration_stat.scalar_one_or_none()
        if not duration_info:
            duration_info = StatInfo(
                type=StatType.DURATION,
                source_id=user_id,
                total=0
            )
            db.add(duration_info)
        duration_info.total += duration

        if not record:
            # 更新练习次数统计
            practice_stat = await db.execute(
                select(StatInfo).where(
                    StatInfo.type == StatType.PRACTICE,
                    StatInfo.source_id == user_id
                )
            )
            practice_info = practice_stat.scalar_one_or_none()
            if not practice_info:
                practice_info = StatInfo(
                    type=StatType.PRACTICE,
                    source_id=user_id,
                    total=0
                )
                db.add(practice_info)
            practice_info.total += 1

            # 更新知识点练习次数统计
            knowledge_practice_stat = await db.execute(
                select(StatInfo).where(
                    StatInfo.type == StatType.PRACTICE_BY_KNOWLEDGE,
                    StatInfo.source_id == user_id,
                    StatInfo.target_id == knowledge_id
                )
            )
            knowledge_practice_info = knowledge_practice_stat.scalar_one_or_none()
            if not knowledge_practice_info:
                knowledge_practice_info = StatInfo(
                    type=StatType.PRACTICE_BY_KNOWLEDGE,
                    source_id=user_id,
                    target_id=knowledge_id,
                    total=0
                )
                db.add(knowledge_practice_info)
            knowledge_practice_info.total += 1
        
        # 更新正确数统计
        if is_correct:
            if not record or not record.is_correct:
                correct_stat = await db.execute(
                    select(StatInfo).where(
                        StatInfo.type == StatType.CORRECT,
                        StatInfo.source_id == user_id
                    )
                )
                correct_info = correct_stat.scalar_one_or_none()
                if not correct_info:
                    correct_info = StatInfo(
                        type=StatType.CORRECT,
                        source_id=user_id,
                        total=0
                    )
                    db.add(correct_info)
                correct_info.total += 1

                # 更新知识点正确数统计
                knowledge_correct_stat = await db.execute(
                    select(StatInfo).where(
                        StatInfo.type == StatType.CORRECT_BY_KNOWLEDGE,
                        StatInfo.source_id == user_id,
                        StatInfo.target_id == knowledge_id
                    )
                )
                knowledge_correct_info = knowledge_correct_stat.scalar_one_or_none()
                if not knowledge_correct_info:
                    knowledge_correct_info = StatInfo(
                        type=StatType.CORRECT_BY_KNOWLEDGE,
                        source_id=user_id,
                        target_id=knowledge_id,
                        total=0
                    )
                    db.add(knowledge_correct_info)
                knowledge_correct_info.total += 1
        await db.flush()

    @classmethod
    async def submit_answer(
        cls,
        db: AsyncSession,
        question_id: int,
        user_id: int,
        answer: Answer,
        start_answer_time: datetime
    ) -> AnswerHistory:
        """提交答案
        
        Args:
            db: 数据库会话
            question_id: 题目ID
            user_id: 用户ID
            answer: 用户答案
            answer_time: 答题时间
            
        Returns:
            AnswerHistory: 答题历史记录
        """
        # 1. 获取题目信息
        stmt = select(Question).where(Question.id == question_id)
        result = await db.execute(stmt)
        question = result.scalar_one_or_none()
        submitted_at = datetime.now(UTC).isoformat()
        duration:int = int(min((datetime.now(UTC) - start_answer_time).total_seconds(),60*20))
        if not question:
            raise ValidationError(message="题目不存在")
        # 2. 验证答案正确性
        is_correct = False
        if question.question_type == "judge":
            # 判断题
            is_correct = answer.result == question.correct_answer.result
        elif question.question_type == "single":
            # 单选题
            is_correct = answer.result.index == question.correct_answer.result.index # type: ignore
        elif question.question_type == "multi":
            # 多选题 - 需要答案完全匹配
            is_correct = await QuestionService.judge_multi_answer(answer, question.correct_answer) # type: ignore
        elif question.question_type in ["blank", "qa"]:
            # 填空题和问答题 - 需要完全匹配
            is_correct = answer.result == question.correct_answer
        else:
            raise ValidationError(message=f"Question type {question.question_type} is not supported")
        
        await cls.update_user_stats(
            db,
            user_id=user_id,
            duration=duration,
            is_correct=is_correct,
            question_id=question_id
        )
       
         # 3. 创建答题记录
        submission = UserQuestionSubmissionRecord(
            question_id=question_id,
            user_id=user_id,
            meta={
                "answer": answer.model_dump(),
                "is_correct": is_correct,
                "duration": duration,
                "submitted_at": submitted_at
            }
        )
        
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        # 4. 返回答题历史
        return AnswerHistory(
            id=str(submission.id),
            question=question, # type: ignore
            answer=question.correct_answer,
            user_answer=answer,
            is_correct=is_correct
        )

    async def get_user_history(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[UserQuestionSubmissionRecord]:
        """获取用户答题历史"""
        stmt = select(self.model).where(
            self.model.user_id == user_id
        ).options(
            selectinload(UserQuestionSubmissionRecord.question).options(
                selectinload(Question.knowledge)
            )
        ).order_by(
            self.model.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_study_stats(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> StudyStatus:
        """获取用户学习统计信息"""
        # 查询用户统计信息
        stats_stmt = (
            select(
                StatInfo.total
            ).where(
                StatInfo.source_id == user_id
            )
        )
        
        # 获取学习时长
        duration_result = await db.execute(
            stats_stmt.where(StatInfo.type == StatType.DURATION)
        )
        total_duration = duration_result.scalar_one_or_none() or 0
        
        # 获取练习次数
        practice_result = await db.execute(
            stats_stmt.where(StatInfo.type == StatType.PRACTICE)
        )
        practice_count = practice_result.scalar_one_or_none() or 0
        
        # 获取正确数
        correct_result = await db.execute(
            stats_stmt.where(StatInfo.type == StatType.CORRECT)
        )
        correct_count = correct_result.scalar_one_or_none() or 0
        
        user_stats = UserStats(
            total_duration=total_duration,
            practice_count=practice_count,
            correct_count=correct_count
        )

        # 查询知识点统计信息
        knowledge_stmt = (
            select(
                Knowledge.id.label("id"),
                Knowledge.name.label("name"),
                func.coalesce(func.cast(Knowledge.meta["is_important"], String), "false").label("is_important"),
                func.count(Question.id).label("total")  # 统计每个知识点的总题目数
            )
            .select_from(Knowledge)
            .outerjoin(Question, Question.knowledge_id == Knowledge.id)  # 关联题目表
            .outerjoin(  # 关联统计信息表获取做题记录
                StatInfo,
                (StatInfo.target_id == Knowledge.id) &
                (StatInfo.source_id == user_id) &
                (StatInfo.type == StatType.PRACTICE_BY_KNOWLEDGE)
            )
            .group_by(Knowledge.id)  # 按知识点分组
        )
        
        correct_subq = (
            select(StatInfo.total)
            .where(
                (StatInfo.target_id == Knowledge.id) &
                (StatInfo.source_id == user_id) &
                (StatInfo.type == StatType.CORRECT_BY_KNOWLEDGE)
            )
            .correlate(Knowledge)
            .scalar_subquery()
        )
        
        knowledge_stmt = knowledge_stmt.add_columns(
            func.coalesce(correct_subq, 0).label("correct_count")
        )
        
        knowledge_result = await db.execute(knowledge_stmt)
        knowledge_stats = [KnowledgeStats.model_validate(row) for row in knowledge_result]

        # 构造知识点详情
        knowledge_detail = [
            KnowledgeDetail(
                name=stats.name,
                knowledge_id=str(stats.id),
                total=stats.total,
                correct_count=stats.correct_count,
                is_important=stats.is_important == "true"  # 将字符串转换为布尔值
            )
            for stats in knowledge_stats
        ]

        return StudyStatus(
            total_duration=user_stats.total_duration,
            practice_count=user_stats.practice_count,
            correct_count=user_stats.correct_count,
            knowledge_detail=knowledge_detail
        )
