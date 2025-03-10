from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from core.database import get_session
from core.dependencies import get_current_user
from core.models.user import User
from schemas.user import UserInfo
from services.user import UserService
from services.study import (
    UserQuestionSubmissionService,
)
from services.leaderboard import LeaderboardService
from schemas.leaderboard import GroupType, BoardType
from schemas.study import QuestionSubmissionRecordResponse
router = APIRouter(prefix="/users", tags=["用户"])

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    user_study_service: UserQuestionSubmissionService = Depends(),
    leaderboard_service: LeaderboardService = Depends()
) -> UserInfo:
    """获取当前用户信息"""
    if not current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户ID不能为空"
        )
    # 获取学习统计信息
    study_stats = await user_study_service.get_study_stats(
        db,
        user_id=current_user.id,
    )
    # 获取部门排名
    department_index = await leaderboard_service.get_user_index(
        db,
        user_id=current_user.id,
        group=GroupType.DEPARTMENT,
        board_type=BoardType.DURATION
    )
    # 获取公司排名
    company_index = await leaderboard_service.get_user_index(
        db,
        user_id=current_user.id,
        group=GroupType.COMPANY,
        board_type=BoardType.DURATION
    )
    
    return UserInfo(
        name=current_user.name,
        avatar=current_user.avatar,
        study_status=study_stats,
        employee_id=current_user.employee_id,
        class_=current_user.class_name, # type: ignore
        department=current_user.department_name,
        job_title=current_user.job_title,
        department_index=department_index,
        company_index=company_index
    )

@router.get("/me/qa/history", response_model=List[QuestionSubmissionRecordResponse])
async def get_qa_history(
    skip: int = 0,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    submission_service: UserQuestionSubmissionService = Depends()
) -> List[QuestionSubmissionRecordResponse]:
    """获取当前用户的答题历史"""
    records = await submission_service.get_user_history(
        db,
        current_user.id,
        skip=skip,
        limit=limit
    )
    
    result = []
    for record in records:
        if not record.question:  # 如果题目不存在，跳过
            continue
            
        try:
            # 从 meta 中获取答案数据
            user_answer = record.answer
            result.append(QuestionSubmissionRecordResponse(
                id=str(record.id),
                question=record.question, # type: ignore
                answer=record.question.correct_answer, # type: ignore
                user_answer=user_answer,
                is_correct=record.is_correct
            ))
        except Exception as e:
            print(e)
            continue  # 如果处理某条记录出错，跳过该记录
    
    return result

@router.get("", response_model=List[UserInfo])
async def get_users(
    department: str = Query(None, description="部门名称"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(),
    submission_service: UserQuestionSubmissionService = Depends(),
) -> List[UserInfo]:
    """获取用户列表"""
    # 计算偏移量
    skip = (page - 1) * page_size
    
    # 获取用户列表
    users = await user_service.get_multi(
        db,
        department_name=department,
        skip=skip,
        limit=page_size
    )
    
    # 获取每个用户的详细信息
    result: List[UserInfo] = []
    for user in users:
        if not user.id:
            continue
        # 获取学习统计信息
        study_stats = await submission_service.get_study_stats(
            db,
            user_id=user.id,
        )
        
        result.append(UserInfo(
            name=user.name,
            avatar=user.avatar,
            study_status=study_stats,
            employee_id=user.employee_id,
            class_=user.class_name, # type: ignore
            department=user.department_name,
            job_title=user.job_title
        ))
    
    return result 