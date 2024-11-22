import os


def has_gpu():
    # Detect known environments without gpu rendering
    target_env_vars = ["BINDER_REQUEST"]
    return not any(os.environ.get(k) for k in target_env_vars)


XARRAY_EXAMPLES = [
    # from https://docs.xarray.dev/en/stable/generated/xarray.tutorial.open_dataset.html
    {
        "name": "XArray Examples - Air Temperature",
        "value": {"source": "xarray", "id": "air_temperature"},
    },
    {
        "name": "XArray Examples - Ocean Basins",
        "value": {"source": "xarray", "id": "basin_mask"},
    },
    {
        "name": "XArray Examples - Ice Velocity",
        "value": {"source": "xarray", "id": "ASE_ice_velocity"},
    },
    {
        "name": "XArray Examples - Regional Arctic System Model",
        "value": {"source": "xarray", "id": "rasm"},
    },
    {
        "name": "XArray Examples - Regional Ocean Model System",
        "value": {"source": "xarray", "id": "ROMS_example"},
    },
    {
        "name": "XArray Examples - ERA-Interim analysis",
        "value": {"source": "xarray", "id": "eraint_uvz"},
    },
    {
        "name": "XArray Examples - NOAA Sea Surface Temperatures",
        "value": {"source": "xarray", "id": "ersstv5"},
    },
]

# Used in preview

XYZ = ["x", "y", "z"]
SLICE_VARS = ["slice_{}_range", "slice_{}_cut", "slice_{}_type", "slice_{}_step"]
VIEW_UPS = {
    (1, 1, 1): (0, 0, 1),
    (-1, -1, 1): (0, 0, 1),
    (1, 0, 0): (0, 0, 1),
    (0, 1, 0): (0, 0, 1),
    (0, 0, 1): (0, 1, 0),
}
