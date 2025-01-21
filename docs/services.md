# Services 功能说明文档

## 目录

- [基础服务](#基础服务)
- [用户相关服务](#用户相关服务)
- [学习相关服务](#学习相关服务)
- [组织架构服务](#组织架构服务)
- [统计服务](#统计服务)
- [认证服务](#认证服务)
- [排行榜服务](#排行榜服务)
- [工具服务](#工具服务)

## 基础服务

位置：`services/base.py`

`BaseService` 提供通用的 CRUD 操作：

| 方法 | 说明 |
|------|------|
| `get` | 通过 ID 获取单条记录 |
| `get_multi` | 获取多条记录（支持分页） |
| `create` | 创建记录 |
| `update` | 更新记录 |
| `delete` | 删除记录 |

## 用户相关服务

位置：`services/user.py`

### UserService

用户基本信息管理：

| 方法 | 说明 |
|------|------|
| `get_by_id` | 通过 ID 获取用户 |
| `get_by_employee_id` | 通过工号获取用户 |
| `authenticate` | 用户认证（验证工号和密码） |
| `get_multi` | 获取用户列表（支持按部门筛选） |

### UserPointsService

用户积分管理：

| 方法 | 说明 |
|------|------|
| `get_by_user` | 获取用户积分信息 |
| `add_points` | 增加用户积分，同时创建积分记录 |

### OnlineDaysService

用户在线时长管理：

| 方法 | 说明 |
|------|------|
| `get_by_user` | 获取用户在线天数 |
| `record_online` | 记录用户在线，更新连续天数 |

## 学习相关服务

位置：`services/study.py`

### KnowledgeService

知识点管理：
- 知识点的 CRUD 操作
- 知识点关联的题目管理

### QuestionService

题目管理：
- 题目的 CRUD 操作
- 题目难度系数管理
- 题目与知识点关联

### UserQuestionService

用户答题管理：
- 记录用户答题情况
- 统计正确率和用时
- 管理学习卡片

### UserKnowledgeService

用户知识掌握度管理：
- 记录用户对知识点的熟练度
- 更新学习进度

## 组织架构服务

位置：`services/organization.py`

### CorporationService

集团管理：
- 集团基本信息维护
- 下属公司管理

### CompanyService

公司管理：
- 公司基本信息维护
- 部门管理

### DepartmentService

部门管理：
- 部门基本信息维护
- 班级管理

### ClassService

班级管理：
- 班级基本信息维护
- 班级成员管理

## 统计服务

位置：`services/stats.py`

### StatInfoService

统计信息管理：
- 维护各类统计数据
- 支持多维度统计（用户、部门、知识点等）
- 记录统计历史

## 认证服务

位置：`services/auth.py`

### JWTAuthService

JWT 认证管理：
- 用户认证信息维护
- JWT token 管理
- 密码加密和验证

## 排行榜服务

位置：`services/leaderboard.py`

### LeaderboardService

排行榜管理：
- 积分排行
- 在线时长排行
- 学习进度排行

## 工具服务

位置：`services/utils.py`

提供各种辅助功能：
- 数据处理
- 格式转换
- 通用工具方法

## 服务间关系

1. 所有服务都继承自 `BaseService`，复用基础的 CRUD 操作
2. 服务之间保持低耦合，通过模型关系进行关联
3. 每个服务专注于自己的业务领域
4. 服务间可以相互调用，但要注意依赖方向

## 使用建议

1. 在 API 层面，应该通过依赖注入获取服务实例
2. 复杂业务逻辑应该在服务层实现，而不是在 API 层
3. 服务方法应该是原子的，避免跨多个服务的事务
4. 需要跨服务的操作应该在更上层编排

## 代码示例

### 服务注入示例

```python
from fastapi import Depends
from services.user import UserService
from core.database import get_db

async def get_user_service():
    return UserService()

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get(db, user_id)
```

### 服务调用示例

```python
async def record_user_study(
    db: AsyncSession,
    user_id: int,
    question_id: int,
    is_correct: bool
):
    # 记录答题
    submission = await question_service.record_submission(
        db, user_id, question_id, is_correct
    )
    
    # 更新积分
    if is_correct:
        await points_service.add_points(db, user_id, 10)
    
    # 更新在线时长
    await online_service.record_online(db, user_id)
    
    return submission
``` 