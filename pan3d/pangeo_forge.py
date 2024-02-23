import xarray
from datetime import datetime


def get_catalog():
    return {
        "name": "Pangeo Forge",
        "id": "pangeo",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_catalog_search_options():
    search_options = {}
    return search_options


def search_catalog(**kwargs):
    group_name = "/".join(list(",".join(v) for v in kwargs.values()))
    start = datetime.now()
    results = []

    delta = datetime.now() - start
    message = f'Found {len(results)} dataset ids \
        in {delta.total_seconds()} seconds.\
        Results added to group "{group_name}".'
    return (results, group_name, message)


def load_dataset(dataset_id):
    return xarray.open_dataset(dataset_id, engine="zarr")
