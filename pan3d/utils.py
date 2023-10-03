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
    "mesh_timeout": 30,
    "state_export": None,
    "available_datasets": [
        {
            "name": "XArray Examples - air temperature",
            "url": "air_temperature",
        },
        {"name": "XArray Examples - basin mask", "url": "basin_mask"},
        {"name": "XArray Examples - eraint uvz", "url": "eraint_uvz"},
    ],
    "dataset_path": None,
    "da_active": None,
    "da_vars": [],
    "da_attrs": [],
    "da_coordinates": [],
    "da_x": None,
    "da_y": None,
    "da_z": None,
    "da_t": None,
    "da_t_index": 0,
    "da_t_max": 0,
    "da_size": None,
    "ui_loading": False,
    "ui_main_drawer": True,
    "ui_axis_drawer": False,
    "ui_unapplied_changes": False,
    "ui_error_message": None,
    "ui_more_info_link": None,
    "ui_expanded_coordinates": [],
    "ui_action_name": None,
    "ui_action_message": None,
    "ui_selected_config_file": None,
}

coordinate_auto_selection = {
    "da_x": ["x", "lon", "len"],
    "da_y": ["y", "lat", "width"],
    "da_z": ["z", "depth", "height"],
    "da_t": ["t", "time"],
}
