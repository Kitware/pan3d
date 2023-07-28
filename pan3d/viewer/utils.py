import asyncio

singleton_task = None


def run_singleton_task(function, callback, timeout=3, **kwargs):
    global singleton_task

    def complete_task(result):
        global singleton_task
        if not result.cancelled():
            callback(result.exception())
            singleton_task = None

    async def coroutine():
        await asyncio.wait_for(function(), timeout=timeout)

    if singleton_task and not singleton_task.done():
        singleton_task.cancel()
        singleton_task = None
    singleton_task = asyncio.create_task(coroutine())
    singleton_task.add_done_callback(complete_task)
