# https://intake-esgf.readthedocs.io/en/latest/quickstart.html
from intake_esgf import ESGFCatalog
from intake_esgf.exceptions import NoSearchResults
from datetime import datetime
from pathlib import Path
import json


BASE_DIR = Path(__file__).parent
CACHED_CATALOG_PATH = Path(BASE_DIR, "../examples/esgf_catalog.json")

if not CACHED_CATALOG_PATH.exists():
    with open(CACHED_CATALOG_PATH, 'w') as f:
        json.dump({}, f)

EXPERIMENT_IDS = [
    'pdSST-futAntSIC',
    'pdSST-futArcSIC',
    'pdSST-piAntSIC',
    'pdSST-pdSIC',
    'piSST-pdSIC',
    'dcppA-hindcast',
    'pdSST-piArcSIC'
]
SOURCE_IDS = [
    'NorESM2-LM',
    'HadGEM3-GC31-MM',
    'IPSL-CM6A-LR',
    'CESM2',
    'CESM1-WACCM-SC',
    'CanESM5',
    'MIROC6',
    'E3SM-1-0',
    'AWI-CM-1-1-MR',
    'TaiESM1',
]


GROUPS = []
for experiment_id in EXPERIMENT_IDS:
    for source_id in SOURCE_IDS:
        GROUPS.append({
            'name': f'ESGF - {experiment_id} - {source_id}',
            'value': f'{experiment_id}/{source_id}'
        })

def get_group_datasets(group_value):
    catalog_contents = {}
    with open(CACHED_CATALOG_PATH) as f:
        catalog_contents = json.load(f)
    datasets = catalog_contents.get(group_value)
    if datasets is not None:
        return datasets

    print(f'Searching for datasets in {group_value}.')
    experiment_id, source_id = group_value.split('/')
    start = datetime.now()
    catalog = ESGFCatalog()
    results = []
    try:
        search = catalog.search(
            experiment_id=experiment_id,
            source_id=source_id,
        )
        results = [
            {
                'name': id,
                'value': {
                    'source': 'esgf',
                    'id': id
                }
            }
            # get first dataset for each unique variable
            for id in search.df.groupby('variable_id').head(n=1).id
        ]
    except NoSearchResults:
        pass

    catalog_contents[group_value] = results
    with open(CACHED_CATALOG_PATH, 'w') as f:
        json.dump(catalog_contents, f)

    delta = datetime.now() - start
    print(f'Cached {len(results)} dataset ids in {delta.total_seconds()} seconds.')
    return results


def load_dataset(id):
    catalog = ESGFCatalog()
    search = catalog.search(id=id)
    loaded = search.to_dataset_dict()
    keys = list(loaded.keys())
    if len(keys) > 0:
        return loaded[keys[0]]
    else:
        raise ValueError(f'No dataset found for {id}.')
