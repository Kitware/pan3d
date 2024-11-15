import importlib


def _call_catalog_function(catalog_name, function_name, **kwargs):
    try:
        module = importlib.import_module(f"pan3d.catalogs.{catalog_name}")
        func = getattr(module, function_name)
        return func(**kwargs)
    except ImportError:
        raise ValueError(
            f"{catalog_name} catalog module not enabled. Install pan3d[{catalog_name}] to load this catalog."
        )
    except AttributeError:
        raise ValueError(f"{catalog_name} is not a valid catalog module.")


def get(catalog_name):
    return _call_catalog_function(catalog_name, "get_catalog")


def get_search_options(catalog_name):
    return _call_catalog_function(catalog_name, "get_search_options")


def search(catalog_name, **filters):
    return _call_catalog_function(catalog_name, "search", **filters)


def load_dataset(catalog_name, id):
    return _call_catalog_function(catalog_name, "load_dataset", id=id)


def list_availables():
    # FIXME - make it dynamic
    return [
        {"value": "file", "title": "Local file"},
        {"value": "url", "title": "Remote URL"},
        {"value": "xarray", "title": "XArray Tutorial"},
        # {"value": "esgf", "title": "ESGF"},
        # {"value": "pangeo", "title": "Pangeo"},
    ]


def list_availables_search():
    # FIXME do a try import and if empty suggest pip install
    return [
        {"id": "esgf", "name": "ESGF", "search_terms": [{"key": "id", "options": []}]},
        {
            "id": "pangeo",
            "name": "Pangeo Forge",
            "search_terms": [{"key": "id", "options": []}],
        },
    ]


__all__ = [
    get,
    get_search_options,
    search,
    load_dataset,
    list_availables,
]
