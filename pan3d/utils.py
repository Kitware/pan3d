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
        # TODO: Can the task be truly interrupted and cancelled?
        singleton_task.cancel()
    singleton_task = asyncio.run_coroutine_threadsafe(coroutine(), task_loop)


initial_state = {
    "trame__title": "Pan3D Viewer",
    "dataset_ready": False,
    "loading": False,
    "unapplied_changes": False,
    "available_datasets": [
        {
            "name": "XArray Examples - air temperature",
            "url": "air_temperature",
        },
        {"name": "XArray Examples - basin mask", "url": "basin_mask"},
        {"name": "XArray Examples - eraint uvz", "url": "eraint_uvz"},
    ],
    "dataset_path": None,
    "more_info_link": None,
    "array_active": None,
    "data_vars": [],
    "data_attrs": [],
    "coordinates": [],
    "expanded_coordinates": [],
    "x_array": None,
    "x_scale": 1,
    "y_array": None,
    "y_scale": 1,
    "z_array": None,
    "z_scale": 1,
    "t_array": None,
    "t_index": 0,
    "t_max": 0,
    "view_edge_visibility": True,
    "error_message": None,
    "da_size": None,
    "mesh_timeout": 30,
}

coordinate_auto_selection = {
    "x_array": ["x", "lon", "len"],
    "y_array": ["y", "lat", "width"],
    "z_array": ["z", "depth"],
    "t_array": ["t", "time"],
}
