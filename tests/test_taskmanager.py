import asyncio
from collections.abc import Callable
from pathlib import Path
from time import sleep

from plugins.logger import setup_logger
from services.taskmanager import TaskExecuterBase, TaskManager, TaskManagerConfig


class TestTaskExecuter(TaskExecuterBase):
    def init(self) -> None:
        pass

    def process(self, payload: dict[str, object], on_progress: Callable[[float], None]) -> None | dict[str, object]:
        for i in range(5):
            sleep(0.5)
            on_progress((i + 1) / 5)

    def cleanup(self, payload: dict[str, object]) -> None: ...

    def create_task(self, *args: list[object], **kwargs: dict[str, object]) -> tuple[str, dict[str, object]]:
        return "test", {}


def test_task_manager():
    # 日志模块
    logger = setup_logger()

    # 创建 data 目录
    Path("data").mkdir(parents=True, exist_ok=True)

    # 配置参数
    config = TaskManagerConfig(
        db_url="sqlite+aiosqlite:///data/tasks.db",
    )

    # 初始化任务管理器
    task_manager = TaskManager(config=config, logger=logger)

    # 注册任务执行器
    task_executer = TestTaskExecuter()
    task_manager.register_task_executer("test", task_executer)

    async def run():
        # 启动任务执行器
        await task_manager.init()
        task_manager.start()
        # 添加任务
        task_id = await task_manager.add_task("test")
        logger.info("task_id: %s", task_id)
        # 轮询并等待任务完成
        while True:
            task = await task_manager.get_task(task_id)
            if task is None:
                break
            logger.warning("status: %s  progress: %.2f%%", task.status, task.progress * 100)
            if task.status == "finished":
                break
            await asyncio.sleep(0.5)
        logger.info(await task_manager.get_tasks_desc())
        await task_manager.destory()

    asyncio.run(run())
