from typing import List, Optional
from sqlalchemy import select, String, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.stats import StatInfo, StatType
from models.organization import Class, Department, Company
from schemas.v1.leaderboard import LeaderboardResponse, LeaderboardEntry, GroupType, BoardType

class LeaderboardService:
    """排行榜服务"""
    
    async def get_leaderboard(
        self,
        db: AsyncSession,
        group: GroupType,
        board_type: BoardType,
        user_id: int,
        count: int
    ) -> LeaderboardResponse:
        """获取排行榜数据
        
        Args:
            group: 分组类型(class/department/company)
            board_type: 榜单类型(duration/practice/correct)
            user_id: 当前用户ID
            count: 排行榜数量
        """
        # 将 board_type 转换为对应的 StatType
        stat_type = {
            "duration": StatType.DURATION,
            "practice": StatType.PRACTICE,
            "correct": StatType.CORRECT
        }[board_type]
        
        # 构建基础查询
        base_query = select(
            User.id,
            User.name,
            func.coalesce(func.cast(User.meta["avatar"], String), "").label("avatar"),
            func.coalesce(StatInfo.total, 0).label("score")  # 不需要max，因为每个用户最多只有一条记录
        ).outerjoin(  # 使用outerjoin确保所有用户都会出现
            StatInfo,
            (StatInfo.source_id == User.id) & 
            (StatInfo.type == stat_type)
        )

        # 根据分组类型添加关联
        if group == "class":
            base_query = base_query.add_columns(
                Class.id.label("group_id"),
                Class.name.label("group_name")
            ).join(Class)  # 这里保持inner join因为用户必须属于一个班级
        elif group == "department":
            base_query = base_query.add_columns(
                Department.id.label("group_id"),
                Department.name.label("group_name")
            ).join(Department)  # 这里保持inner join因为用户必须属于一个部门
        else:  # company
            base_query = base_query.add_columns(
                Company.id.label("group_id"),
                Company.name.label("group_name")
            ).join(Company)  # 这里保持inner join因为用户必须属于一个公司

        # 构建最终查询
        query = (
            base_query
            .order_by(func.coalesce(StatInfo.total, 0).desc())  # 按分数降序排序
        )

        # 执行查询
        result = await db.execute(query)
        rows = result.all()

        # 构建排行榜数据
        leaderboard_entries: List[LeaderboardEntry] = []
        my_entry: Optional[LeaderboardEntry] = None
        
        for index, row in enumerate(rows, 1):
            entry = LeaderboardEntry(
                index=index,
                name=row.name,
                avatar=row.avatar or "",
                score=row.score
            )
            leaderboard_entries.append(entry)
            
            # 如果是当前用户，保存其位置信息
            if row.id == user_id:
                my_entry = entry

        return LeaderboardResponse(
            leaderboard=leaderboard_entries[:count],
            me=my_entry or LeaderboardEntry(index=0, name="", avatar="", score=0)
        )
