from pydantic import BaseModel

class UserBase(BaseModel):
    """用户基础信息"""
    name: str
    avatar: str
    employee_id: str
    class_name: str = ""  # Using class_name since class is a reserved word
    department: str
    job_title: str
    id:int
    model_config = {"from_attributes": True}  # 支持从ORM模型创建 