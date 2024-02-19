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
    print("fetching Pangeo Forge catalog...")
    catalog = []
    feedstocks = requests.get("https://api.pangeo-forge.org/feedstocks/").json()
    for feedstock in feedstocks:
        if feedstock["provider"] == "github":
            data = requests.get(
                f"https://api.pangeo-forge.org/feedstocks/{feedstock['id']}/datasets"
            ).json()
            for item in data:
                if (
                    not item["is_test"]
                    and item["dataset_public_url"]
                    and "https://" in item["dataset_public_url"]
                    and item["dataset_type"] == "zarr"
                ):
                    item_name = feedstock["spec"].split("/")[-1]
                    if len(data) > 1:
                        item_name += f' - {item["recipe_id"]}'
                    if item_name not in [i["name"] for i in catalog]:
                        catalog.append(
                            {
                                "name": item_name,
                                "id": item["id"],
                                "value": item["dataset_public_url"],
                                "more_info": f'https://pangeo-forge.org/dashboard/feedstock/{feedstock["id"]}',
                            }
                        )
    print(f"Retrieved {len(catalog)} viable datasets.")
    return catalog


def get_group_datasets(group_id):
    # Use cached catalog
    with open(CACHED_CATALOG_PATH) as f:
        catalog_contents = json.load(f)
        return catalog_contents.get(group_id, [])

def load_dataset(dataset_id):
    return xarray.open_dataset(dataset_id, engine='zarr')
