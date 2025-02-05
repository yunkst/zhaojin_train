from fastapi import APIRouter, Depends, Path
from datetime import datetime, timezone

from schemas.v1.question import QuestionResponse, AnswerSubmission, AnswerHistory
from services.study import QuestionService, UserQuestionSubmissionService
from core.dependencies import get_current_user
from core.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from core.exceptions import ValidationError
from core.models.user import User

router = APIRouter(prefix="/questions", tags=["题目"])



@router.get("/select", response_model=QuestionResponse)
async def select_questions(
    db: AsyncSession = Depends(get_session),
    knowledge_id: str | None = None,
    current_user: User = Depends(get_current_user),
    question_service: QuestionService = Depends()
) -> QuestionResponse:
    """
    选取题目
    
    如果提供knowledge_id，则从指定知识点抽取题目
    """
    if not current_user.id:
        raise ValidationError(message="User not found")
    question = await question_service.select_questions(
        db=db,
        user_id=current_user.id,
        knowledge_id=knowledge_id
    )
    return QuestionResponse(
            question=question,
            time=datetime.now(timezone.utc)
        )

@router.post("/{id}/answer", response_model=AnswerHistory)
async def submit_answer(
    submission: AnswerSubmission,
    id: str = Path(..., title="题目ID"),
    current_user: User = Depends(get_current_user),
    user_question_submission_service: UserQuestionSubmissionService = Depends(),
    db: AsyncSession = Depends(get_session)
) -> AnswerHistory:
    """提交答案"""
    if not current_user.id:
        raise ValidationError(message="User not found")
    
    start_answer_time = submission.time.replace(tzinfo=timezone.utc)
    
    result = await user_question_submission_service.submit_answer(
        db=db,
        question_id=int(id),
        user_id=current_user.id,
        answer=submission.answer,
        start_answer_time=start_answer_time
    )
    return result 