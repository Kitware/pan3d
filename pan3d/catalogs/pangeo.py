import intake
from datetime import datetime

CATALOG_URL = "https://raw.githubusercontent.com/pangeo-data/pangeo-datastore/master/intake-catalogs/master.yaml"


def get_catalog():
    return {
        "name": "Pangeo Forge",
        "id": "pangeo",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_entry_info(entry):
    entry_data = entry.describe()
    metadata = entry_data.get("metadata", {})
    args = entry_data.get("args", {})

    name = entry_data.get("name")
    description = entry_data.get("description")
    container = entry_data.get("container")
    driver_list = entry_data.get("driver", [])
    tags_list = metadata.get("tags", [])
    requester_pays = args.get("storage_options", {}).get("requester_pays", False)
    requester_pays = str(requester_pays).lower()

    return {
        "name": name,
        "description": description,
        "container": container,
        "driver": driver_list,
        "tags": tags_list,
        "requester_pays": requester_pays,
    }


def get_all_entries():
    all_entries = []
    catalog = intake.open_catalog(CATALOG_URL)
    for subcatalog_name in catalog:
        subcatalog = catalog[subcatalog_name]
        for entry_name, entry_data in subcatalog._entries.items():
            if entry_data.container == "catalog":
                for subentry_name in entry_data:
                    subentry = entry_data[subentry_name]
                    subentry_info = get_entry_info(subentry)
                    subentry_info["catalog"] = f"{subcatalog_name}/{entry_name}"
                    all_entries.append(subentry_info)
            else:
                entry_info = get_entry_info(entry_data)
                entry_info["catalog"] = subcatalog_name
                all_entries.append(entry_info)
    return all_entries


def entry_filter_match(entry, filters):
    for filter_key, selected_values in filters.items():
        if filter_key == "id":
            # name is the unique identifier
            filter_key = "name"
        entry_value = entry.get(filter_key)
        if entry_value is None:
            return False
        if isinstance(entry_value, str):
            entry_value = [entry_value]
        if len(selected_values) and not any(v in selected_values for v in entry_value):
            return False

    return True


def get_search_options():
    all_entries = get_all_entries()
    search_options = {
        "name": [],
        "container": [],
        "driver": [],
        "tags": [],
        "catalog": [],
        "requester_pays": ["true", "false"],
    }
    for entry_info in all_entries:
        for search_option in search_options.keys():
            entry_value = entry_info.get(search_option)
            if entry_value:
                if isinstance(entry_value, str):
                    entry_value = [entry_value]
                search_options[search_option] = list(
                    set([*search_options[search_option], *entry_value])
                )

    return search_options


def search(**kwargs):
    group_name = "/".join([f'{k}:{",".join(v)}' for k, v in kwargs.items()])
    if not group_name:
        group_name = "All Pangeo Datasets"
    start = datetime.now()
    all_entries = get_all_entries()
    results = [
        {
            "name": entry["name"],
            "description": entry["description"],
            "value": {"source": "pangeo", "id": entry["name"]},
        }
        for entry in all_entries
        if entry_filter_match(entry, kwargs)
    ]

    delta = datetime.now() - start
    message = f'Found {len(results)} dataset ids \
        in {delta.total_seconds()} seconds.\
        Results added to group "{group_name}".'
    return (results, group_name, message)


def informative_error(e, **kwargs):
    if isinstance(
        e, ValueError
    ) and "User project specified in the request is invalid" in str(e):
        return "Dataset has requester pays policy and no billable Google Cloud Project was specified. See https://github.com/pangeo-data/pangeo-datastore?tab=readme-ov-file#accessing-requester-pays-data for more info."
    elif "GS_SECRET_ACCESS_KEY+GS_ACCESS_KEY_ID" in str(e):
        return "Dataset requires Google Cloud authentication. See https://cloud.google.com/sdk/gcloud/reference/auth/login for more info."
    elif "Unable to locate credentials" in str(e):
        return "Dataset requires AWS authentication. See https://docs.aws.amazon.com/signin/latest/userguide/command-line-sign-in.html for more info."

    return f'Failed to load dataset {kwargs.get("dataset")} - {str(e)}'


def load_dataset(id):
    catalog = intake.open_catalog(CATALOG_URL)
    for subcatalog_name in catalog:
        subcatalog = catalog[subcatalog_name]
        for entry_name, entry_data in subcatalog._entries.items():
            try:
                entry = subcatalog[entry_name]
                if entry.container == "catalog":
                    for subentry_name in entry:
                        if subentry_name == id:
                            subentry = entry[subentry_name]
                            return subentry.to_dask()
                elif entry_name == id:
                    return entry.to_dask()
            except Exception as e:
                raise ValueError(informative_error(e, dataset=entry_data.describe()))
