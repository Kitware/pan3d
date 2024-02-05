import os


def has_gpu_rendering():
    # Detect known environments without gpu rendering
    target_env_vars = ["BINDER_REQUEST"]
    return not any(os.environ.get(k) for k in target_env_vars)


initial_state = {
    "trame__title": "Pan3D Viewer",
    "dataset_ready": False,
    "state_export": None,
    "available_datasets": [
        # from https://docs.xarray.dev/en/stable/generated/xarray.tutorial.open_dataset.html
        {
            "name": "XArray Examples - Air Temperature",
            "url": "air_temperature",
        },
        {"name": "XArray Examples - Ocean Basins", "url": "basin_mask"},
        {"name": "XArray Examples - Ice Velocity", "url": "ASE_ice_velocity"},
        {"name": "XArray Examples - Regional Arctic System Model", "url": "rasm"},
        {
            "name": "XArray Examples - Regional Ocean Model System",
            "url": "ROMS_example",
        },
        {"name": "XArray Examples - ERA-Interim analysis", "url": "eraint_uvz"},
        {"name": "XArray Examples - NOAA Sea Surface Temperatures", "url": "ersstv5"},
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
    "da_size": None,
    "ui_loading": False,
    "ui_main_drawer": False,
    "ui_axis_drawer": False,
    "ui_unapplied_changes": False,
    "ui_error_message": None,
    "ui_more_info_link": None,
    "ui_expanded_coordinates": [],
    "ui_action_name": None,
    "ui_action_message": None,
    "ui_action_config_file": None,
    "ui_current_time_string": "",
    "render_auto": False,
    "render_x_scale": 1,
    "render_y_scale": 1,
    "render_z_scale": 1,
    "render_scalar_warp": False,
    "render_transparency": False,
    "render_transparency_function": "linear",
    "render_transparency_function_options": [
        "linear",
        "linear_r",
        "geom",
        "geom_r",
        "sigmoid",
        "sigmoid_r",
    ],
    "render_colormap": "viridis",
    "render_colormap_options": [
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "terrain",
        "ocean",
        "cividis",
        "seismic",
        "rainbow",
        "jet",
        "turbo",
        "gray",
        "cool",
        "hot",
        "coolwarm",
        "hsv",
    ],
}

coordinate_auto_selection = {
    "x": ["x", "i", "lon", "len", "nx"],
    "y": ["y", "j", "lat", "width", "ny"],
    "z": ["z", "k", "depth", "height", "nz", "level"],
    "t": ["t", "time", "year", "month", "date", "day", "hour", "minute", "second"],
}
