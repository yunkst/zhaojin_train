from typing import List
from enum import Enum
from pydantic import BaseModel

class GroupType(str, Enum):
    CLASS = "class"
    DEPARTMENT = "department"
    COMPANY = "company"

class BoardType(str, Enum):
    DURATION = "duration"
    PRACTICE = "practice"
    CORRECT = "correct"

class LeaderboardEntry(BaseModel):
    index: int
    name: str
    avatar: str
    score: int

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardEntry]
    me: LeaderboardEntry

    class Config:
        from_attributes = True 