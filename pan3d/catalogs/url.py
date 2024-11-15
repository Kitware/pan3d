import xarray


def get_catalog():
    return {
        "name": "Remote URL datasets",
        "id": "url",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_search_options():
    return {"url": []}


def search(**kwargs):
    results = []
    group_name = "Remote URL datasets"
    message = "Sorry but we don't have any search mechanism for that data source"
    return (results, group_name, message)


def load_dataset(id):
    engine = None
    if ".zarr" in id:
        engine = "zarr"
    if ".nc" in id:
        engine = "netcdf4"
    return xarray.open_dataset(id, engine=engine, chunks={})
