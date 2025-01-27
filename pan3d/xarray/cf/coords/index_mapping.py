def get_formula(metadata, kji_dims):
    lon_mapper = get_value_mapper(metadata.xr_dataset, kji_dims, metadata.longitude)
    lat_mapper = get_value_mapper(metadata.xr_dataset, kji_dims, metadata.latitude)
    return CoordMapper(lon_mapper, lat_mapper)


class CoordMapper:
    def __init__(self, lon_mapper, lat_mapper):
        self.lon = lon_mapper
        self.lat = lat_mapper

    def __call__(self, i=0, j=0, k=0):
        return self.lon(i=i, j=j, k=k), self.lat(i=i, j=j, k=k)


def get_value_mapper(xr_dataset, in_dims, out_name):
    out_slice_size = len(xr_dataset[out_name].dims)
    if out_slice_size == 3:
        return IndexMapper3(xr_dataset, in_dims, out_name)
    if out_slice_size == 2:
        return IndexMapper2(xr_dataset, in_dims, out_name)
    if out_slice_size == 1:
        return IndexMapper1(xr_dataset, in_dims, out_name)

    msg = f"No IndexMapper for dimensions {xr_dataset[out_name].dims}"
    raise ValueError(msg)


class IndexMapper:
    def __init__(self, xr_dataset, in_dims, out_name):
        self.out_array = xr_dataset[out_name].values

        name_to_ijk = {in_dims[-(i + 1)]: "ijk"[i] for i in range(len(in_dims))}
        out_dims = xr_dataset[out_name].dims
        map_method_name = "".join([name_to_ijk[name] for name in out_dims])
        # print(out_name, "=>", map_method_name)

        setattr(self, "fn", getattr(self, map_method_name))

    def __call__(self, **kwargs):
        return self.fn(**kwargs)


class IndexMapper3(IndexMapper):

    def ijk(self, i=0, j=0, k=0, **_):
        return self.out_array[i, j, k]

    def ikj(self, i=0, j=0, k=0, **_):
        return self.out_array[i, k, j]

    def jki(self, i=0, j=0, k=0, **_):
        return self.out_array[j, k, i]

    def kij(self, i=0, j=0, k=0, **_):
        return self.out_array[k, i, j]

    def jik(self, i=0, j=0, k=0, **_):
        return self.out_array[j, i, k]

    def kji(self, i=0, j=0, k=0, **_):
        return self.out_array[k, j, i]


class IndexMapper2(IndexMapper):

    def ij(self, i=0, j=0, k=0, **_):
        return self.out_array[i, j]

    def ji(self, i=0, j=0, k=0, **_):
        return self.out_array[j, i]

    def ik(self, i=0, j=0, k=0, **_):
        return self.out_array[i, k]

    def ki(self, i=0, j=0, k=0, **_):
        return self.out_array[k, i]

    def jk(self, i=0, j=0, k=0, **_):
        return self.out_array[j, k]

    def kj(self, i=0, j=0, k=0, **_):
        return self.out_array[k, j]


class IndexMapper1(IndexMapper):

    def i(self, i=0, j=0, k=0, **_):
        return self.out_array[i]

    def j(self, i=0, j=0, k=0, **_):
        return self.out_array[j]

    def k(self, i=0, j=0, k=0, **_):
        return self.out_array[k]
