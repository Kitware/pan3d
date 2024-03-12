# https://intake-esgf.readthedocs.io/en/latest/quickstart.html
from intake_esgf import ESGFCatalog
from intake_esgf.exceptions import NoSearchResults
from datetime import datetime


def get_catalog():
    return {
        "name": "ESGF",
        "id": "esgf",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_search_options():
    catalog = ESGFCatalog()
    # perform unfiltered search and get unique values for each column
    results = catalog.search()
    search_options = {}
    for col in results.df.columns:
        search_options[col] = list(results.df[col].explode().unique())
    return search_options


def search(**kwargs):
    group_name = "/".join([f'{k}:{",".join(v)}' for k, v in kwargs.items()])
    if not group_name:
        group_name = "All ESGF Datasets"
    start = datetime.now()
    catalog = ESGFCatalog()
    results = []
    try:
        search = catalog.search(**kwargs)
        results = [
            {"name": id, "value": {"source": "esgf", "id": id}}
            for id in search.df.id.explode().unique()
        ]
    except NoSearchResults:
        pass

    delta = datetime.now() - start
    message = f'Found {len(results)} dataset ids \
        in {delta.total_seconds()} seconds.\
        Results added to group "{group_name}".'
    return (results, group_name, message)


def load_dataset(id):
    catalog = ESGFCatalog()
    search = catalog.search(id=id)
    loaded = search.to_dataset_dict()
    keys = list(loaded.keys())
    if len(keys) > 0:
        return loaded[keys[0]]
    else:
        raise ValueError(f"No dataset found for {id}.")
