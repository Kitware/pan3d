import requests


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
                                "url": item["dataset_public_url"],
                                "more_info": f'https://pangeo-forge.org/dashboard/feedstock/{feedstock["id"]}',
                            }
                        )
    print(f"Retrieved {len(catalog)} viable datasets.")
    return catalog
