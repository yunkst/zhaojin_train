from fastapi import APIRouter, Depends, Path

from schemas.v1.user import UserInfo
from schemas.v1.leaderboard import GroupType, BoardType, LeaderboardResponse
from services.leaderboard import LeaderboardService
from core.dependencies import get_current_user
from core.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Query
router = APIRouter(prefix="/leaderboards", tags=["排行榜"])

@router.get("/{group}/{board_type}", response_model=LeaderboardResponse)
async def get_leaderboard(
    group: GroupType = Path(..., title="分组类型"),
    board_type: BoardType = Path(..., title="榜单类型"),
    count: int = Query(20, ge=1, le=1000),
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    leaderboard_service: LeaderboardService = Depends()
) -> LeaderboardResponse:
    """
    获取排行榜
    
    - group: 分组类型(class/department/company)
    - board_type: 榜单类型(duration/practice/correct)
    """
    result = await leaderboard_service.get_leaderboard(
        db=db,
        group=group,
        board_type=board_type,
        user_id=current_user.id,
        count=count
    )
    return result
