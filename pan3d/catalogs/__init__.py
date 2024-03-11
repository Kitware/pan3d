import importlib


def call_catalog_function(catalog_name, function_name, **kwargs):
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
