import asyncio
import functools
import inspect
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(times: int, sleep_time: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator_retry(func: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper_retry(*args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
                for attempts in range(1, times + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        print(f"Attempt {attempts} failed with error: {e}")
                        if attempts == times:
                            print("All retry attempts failed.")
                            raise
                        await asyncio.sleep(sleep_time)
                raise RuntimeError("Unreachable code")

            return wrapper_retry  # type: ignore

        @functools.wraps(func)
        def wrapper_retry(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempts in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempts} failed with error: {e}")
                    if attempts == times:
                        print("All retry attempts failed.")
                        raise
                    time.sleep(sleep_time)
            raise RuntimeError("Unreachable code")

        return wrapper_retry

    return decorator_retry
