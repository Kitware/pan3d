import asyncio
import threading


singleton_task = None
task_thread = None
task_loop = asyncio.new_event_loop()


def loop_runner(loop):
    loop.run_forever()


def start_task_thread():
    global task_thread

    task_thread = threading.Thread(
        name="Task Thread",
        target=loop_runner,
        args=(task_loop,),
    )
    task_thread.start()


def run_singleton_task(
    function, callback, timeout=3, timeout_message="Timed out.", **kwargs
):
    global singleton_task
    global task_loop
    global task_thread

    async def coroutine():
        try:
            await asyncio.wait_for(function(), timeout=timeout)
        except Exception as e:
            if type(e) == asyncio.exceptions.TimeoutError:
                callback(timeout_message)
            else:
                callback(e)
        else:
            callback()

    task_loop.set_exception_handler(lambda self, context: callback(context["message"]))

    if not task_thread:
        start_task_thread()
    if singleton_task and not singleton_task.done():
        print("DO SOMETHING WITH OLD TASK", singleton_task)
    singleton_task = asyncio.run_coroutine_threadsafe(coroutine(), task_loop)
