import asyncio


singleton_task = None


def run_singleton_task(
    function, callback, timeout=3, timeout_message="Timed out.", **kwargs
):
    global singleton_task

    def complete_task(task):
        global singleton_task
        if not task.cancelled():
            exception = task.exception()
            if type(exception) == asyncio.exceptions.TimeoutError:
                task.cancel()
                callback(timeout_message)
            else:
                callback(exception)
            singleton_task = None

    async def coroutine():
        await function()
        # await asyncio.wait_for(function(), timeout=timeout)

    if singleton_task and not singleton_task.done():
        print("cancelling previous task.")
        singleton_task.cancel()
    singleton_task = asyncio.create_task(asyncio.wait_for(coroutine(), timeout=timeout))
    singleton_task.add_done_callback(complete_task)
