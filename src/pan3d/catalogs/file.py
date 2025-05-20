from pathlib import Path

import xarray


def get_catalog():
    return {
        "name": "Local datasets",
        "id": "file",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_search_options():
    return {"file": []}


def search(**kwargs):
    results = []
    group_name = "Local datasets"
    message = "Sorry but we don't have any search mechanism for that data source"
    return (results, group_name, message)


def load_dataset(id):
    if not Path(id).exists():
        msg = f"Could not find dataset at {id}"
        raise ValueError(msg)

    engine = None
    if ".zarr" in id:
        engine = "zarr"
    if ".nc" in id:
        engine = "netcdf4"
    return xarray.open_dataset(id, engine=engine, chunks={})
