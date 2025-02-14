import json
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from typing import List, Dict, Any
import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings
from core.models.study import Question
from schemas.v1.question import (
    Option, SingleSelectionAnswer, MultiSelectionAnswer,
    JudgeAnswer, BlankFillAnswer, QAAnswer, Answer
)

async def create_db_session():
    """创建数据库会话"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    async_session = AsyncSession(engine)
    return async_session

def parse_options(options: List[Dict[str, Any]]) -> List[Option]:
    """解析选项数据"""
    return [
        Option(
            index=opt["index"],
            content=opt["content"],
            option_name=opt["option_name"]
        )
        for opt in options
    ]

def make_answer(question_type: str, correct_answer: Any) -> Answer:
    """生成答案数据"""
    if question_type == "single":
        return SingleSelectionAnswer(
            result=Option(
                index=correct_answer["index"],
                content=correct_answer.get("content", ""),
                option_name=correct_answer.get("option_name", "")
            )
        )
    elif question_type == "multi":
        return MultiSelectionAnswer(
            result=[
                Option(
                    index=opt["index"],
                    content=opt.get("content", ""),
                    option_name=opt.get("option_name", "")
                )
                for opt in correct_answer
            ]
        )
    elif question_type == "judge":
        return JudgeAnswer(result=correct_answer)
    elif question_type == "blank":
        return BlankFillAnswer(result=correct_answer)
    elif question_type == "qa":
        return QAAnswer(result=correct_answer)
    else:
        raise ValueError(f"不支持的题目类型: {question_type}")

async def import_questions(json_file: str, knowledge_id: int = 1):
    """导入题目数据
    
    Args:
        json_file: JSON文件路径
        knowledge_id: 知识点ID，默认为1
    """
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    # 创建数据库会话
    db = await create_db_session()
    
    try:
        # 遍历题目数据
        for q_data in questions_data:
            # 创建题目对象
            question = Question(
                difficulty=1,
                knowledge_id=knowledge_id,
                meta={}
            )
            
            # 使用属性设置器设置题目属性
            question.question_type = q_data["type"]
            question.description = q_data["description"]
            if "options" in q_data:
                question.options = parse_options(q_data["options"])
            
            # 设置正确答案
            if "correct_answer" in q_data:
                question.correct_answer = make_answer(q_data["type"], q_data["correct_answer"]['result'])
            
            # 保存到数据库
            db.add(question)
        
        # 提交事务
        await db.commit()
        print(f"成功导入 {len(questions_data)} 道题目")
        
    except Exception as e:
        print(f"导入失败: {str(e)}")
        traceback.print_exc()
        await db.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    for json_file in ['tools/question_json/3.json']:
        knowledge_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        asyncio.run(import_questions(json_file, knowledge_id)) 