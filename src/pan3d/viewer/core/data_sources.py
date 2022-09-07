import zarr


class HierarchyBuilder:
    def __init__(self):
        self.hierarchy = {"/": {"id": "/", "children": []}}

    def create_node_zarr(self, name, obj):
        # print(name, obj)
        new_node = {"id": name, "name": name.split("/")[-1], "children": []}

        if isinstance(obj, zarr.core.Array):
            new_node["dimensions"] = obj.shape
            new_node["type"] = f"{obj.dtype}"

        parent_id = "/".join(name.split("/")[:-1])
        if len(parent_id) == 0:
            parent_id = "/"
        if parent_id in self.hierarchy:
            self.hierarchy[parent_id]["children"].append(new_node)
        self.hierarchy[name] = new_node

    @property
    def root(self):
        return self.hierarchy["/"]

    @property
    def children(self):
        return self.root["children"]


class ZarrDataSource:
    def __init__(self, source):
        self._zarr = source
        self._hierarchy = HierarchyBuilder()
        if isinstance(source, str):
            self._zarr = zarr.open(source, mode="r")

        self._zarr.visititems(self._hierarchy.create_node_zarr)

    @property
    def tree(self):
        return self._hierarchy.children

    def get(self, path):
        # print("get", path)
        if not path or path not in self._zarr:
            # print(" => none (0)")
            return None

        entry = self._zarr[path]
        if isinstance(entry, zarr.core.Array):
            # print(" => array", entry)
            return entry

        # print(" => none (1)")
        return None
