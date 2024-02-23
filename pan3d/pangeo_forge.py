import json
import xarray
import requests
from pathlib import Path


BASE_DIR = Path(__file__).parent
CACHED_CATALOG_PATH = Path(BASE_DIR, "../examples/pangeo_catalog.json")
GROUPS = [
    {'name': 'Pangeo - CMIP6', 'value': 'cmip6',},
    {'name': 'Pangeo - CMIP6 Static', 'value': 'cmip6_static',},
    {'name': 'Pangeo - CMIP6 PMIP', 'value': 'cmip6_pmip',},
    {'name': 'Pangeo - EOBS', 'value': 'eobs',},
    {'name': 'Pangeo - Miscellaneous', 'value': 'misc',},
]


def get_catalog():
    return {
        'name': 'Pangeo Forge',
        'id': 'pangeo',
        'search_terms': [
            {'key': 'id', 'options': []}
        ]
    }


def get_group_datasets(group_id):
    # Use cached catalog
    with open(CACHED_CATALOG_PATH) as f:
        catalog_contents = json.load(f)
        return catalog_contents.get(group_id, [])

def load_dataset(dataset_id):
    return xarray.open_dataset(dataset_id, engine='zarr')
