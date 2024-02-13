from typing import Callable

from fastapi import BackgroundTasks


async def create_background_task(
    background_tasks: BackgroundTasks,
    func: Callable,
    *args: str
) -> None:

    background_tasks.add_task(func, *args)
