# https://openorganelle.janelia.org/faq#python
# https://open.quiltdata.com/b/janelia-cosem-datasets/tree/
from datetime import datetime
import quilt3 as q3
import re
import zarr


BUCKET_URL = "s3://janelia-cosem-datasets"
REFORMATTED_CACHE = "./janelia-reformatted"
prefix_delimiter_pattern = "_|-"
dataset_suffixes = [".zarr/", ".n5/"]


def get_dataset_folders():
    bucket = q3.Bucket(BUCKET_URL)
    directory_info, object_info, delete_markers = bucket.ls("")
    return [
        folder.get("Prefix").replace("/", "")
        for folder in directory_info
        if folder.get("Prefix") is not None
    ]


def get_catalog():
    return {
        "name": "Janelia COSEM",
        "id": "janelia",
        "search_terms": [{"key": "id", "options": []}],
    }


def get_search_options():
    prefixes = []
    for folder in get_dataset_folders():
        partial_prefixes = [
            folder[: match.start(0)]
            for match in re.finditer(prefix_delimiter_pattern, folder)
        ]
        for partial_prefix in partial_prefixes:
            if partial_prefix not in prefixes:
                prefixes.append(partial_prefix)
    return {"prefix": prefixes}


def search(**kwargs):
    start = datetime.now()
    prefix = kwargs.get("prefix")
    dataset_folders = get_dataset_folders()
    results = [
        {"name": id, "value": {"source": "janelia", "id": id}}
        for id in dataset_folders
        if not prefix or prefix in id
    ]
    delta = datetime.now() - start
    group_name = prefix or "All Janelia COSEM datasets"
    message = f'Found {len(results)} dataset ids \
        in {delta.total_seconds()} seconds.\
        Results added to group "{group_name}".'
    return (results, group_name, message)


def reformat_zarr_group(original_group, new_group):
    subgroups = list(original_group.groups())
    if len(subgroups):
        return {gname: reformat_zarr_group(g, new_group) for gname, g in subgroups}
    else:
        name = original_group.name.split("/")[-1]
        arr = original_group[
            "s0"
        ]  # in janelia's schema, s0 is the full-resolution data
        zarr.copy(
            arr,
            new_group,
            name=name,
            attrs={
                "_ARRAY_DIMENSIONS": [
                    "x",
                    "y",
                    "z",
                ],  # axes are ordered 'xyz' instead of 'zyx'
            },
        )


def cache_reformatted(dataset_path):
    dataset_url = f"{BUCKET_URL}/{dataset_path}"
    print(dataset_url)
    original_group = zarr.open(zarr.N5FSStore(dataset_url, anon=True))
    return original_group
    # reformatted_path = f'{REFORMATTED_CACHE}/{dataset_path.replace("/", "_")}'
    # if not os.path.exists(reformatted_path):
    #     new_group = zarr.open(zarr.DirectoryStore(reformatted_path))
    #     reformat_zarr_group(original_group, new_group)
    #     zarr.consolidate_metadata(new_group)
    # return xarray.open_zarr(reformatted_path)


# TODO: this doesn't work
def load_dataset(id):
    bucket = q3.Bucket(BUCKET_URL)
    directory_info, object_info, delete_markers = bucket.ls(id)
    dataset_path = None
    for suffix in dataset_suffixes:
        if dataset_path is None:
            for folder in directory_info:
                if folder.get("Prefix").endswith(suffix):
                    dataset_path = folder.get("Prefix")

    if dataset_path is None:
        raise ValueError(f"No dataset found")
    try:
        # attempt to reformat to something xarray can read
        return cache_reformatted(dataset_path)
    except Exception as e:
        if isinstance(e.__cause__, PermissionError):
            raise e.__cause__
        else:
            raise e


# Testing
# print(get_search_options())
# print(search(prefix='jrc_hela'))
# print(load_dataset('jrc_mus-granule-neurons-1'))
# print(load_dataset('jrc_hela-1'))
