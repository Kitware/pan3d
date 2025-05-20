import xarray
from pathlib import Path


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
        raise ValueError(f"Could not find dataset at {id}")

    engine = None
    if ".zarr" in id:
        engine = "zarr"
    if ".nc" in id:
        engine = "netcdf4"
    return xarray.open_dataset(id, engine=engine, chunks={})
