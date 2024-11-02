from xarray.tutorial import open_dataset

ALL_ENTRIES = [
    {
        "name": "air_temperature",
        "description": "NCEP reanalysis subset",
    },
    {
        "name": "air_temperature_gradient",
        "description": "NCEP reanalysis subset with approximate x,y gradients",
    },
    {
        "name": "basin_mask",
        "description": "Dataset with ocean basins marked using integers",
    },
    # -------------------------------------------------------------------------
    # {
    #     "name": "ASE_ice_velocity",
    #     "description": "MEaSUREs InSAR-Based Ice Velocity of the Amundsen Sea Embayment, Antarctica, Version 1",
    # },
    # -------------------------------------------------------------------------
    # {
    #     "name": "rasm",
    #     "description": "Output of the Regional Arctic System Model (RASM)",
    # },
    # -------------------------------------------------------------------------
    # {
    #     "name": "ROMS_example",
    #     "description": "Regional Ocean Model System (ROMS) output",
    # },
    # -------------------------------------------------------------------------
    # {
    #     "name": "tiny",
    #     "description": "small synthetic dataset with a 1D data variable",
    # },
    # -------------------------------------------------------------------------
    # needs pandas[xarray]
    # {
    #     "name": "era5-2mt-2019-03-uk.grib",
    #     "description": "ERA5 temperature data over the UK",
    # },
    # -------------------------------------------------------------------------
    {
        "name": "eraint_uvz",
        "description": "data from ERA-Interim reanalysis, monthly averages of upper level data",
    },
    {
        "name": "ersstv5",
        "description": "NOAA’s Extended Reconstructed Sea Surface Temperature monthly averages",
    },
]


def get_catalog():
    return {
        "name": "Xarray Tutorial",
        "id": "xarray",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_search_options():
    search_options = {
        "name": [],
    }
    for entry_info in ALL_ENTRIES:
        for search_option in search_options.keys():
            entry_value = entry_info.get(search_option)
            if entry_value:
                if isinstance(entry_value, str):
                    entry_value = [entry_value]
                search_options[search_option] = list(
                    set([*search_options[search_option], *entry_value])
                )

    return search_options


def to_result(entry):
    return {**entry, "value": {"source": "xarray", "id": entry["name"]}}


def search(**kwargs):
    results = [to_result(entry) for entry in ALL_ENTRIES]
    group_name = "Xarray Tutorial"
    message = (
        f'Found {len(ALL_ENTRIES)} dataset ids. Results added to group "{group_name}".'
    )
    return (results, group_name, message)


def load_dataset(id):
    return open_dataset(id)
