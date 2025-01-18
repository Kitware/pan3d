def add_imagedata(image_data, coords):
    print(f"{coords.extent=}")
    print(f"{coords.origin=}")
    print(f"{coords.spacing=}")
    image_data.SetExtent(*coords.extent)
    image_data.SetOrigin(*coords.origin)
    image_data.SetSpacing(*coords.spacing)


def add_rectilinear(rectilinear_grid):
    raise NotImplementedError()


def fake_rectilinear(rectilinear_grid):
    raise NotImplementedError()


def add_1d_points(vtk_point, extent):
    raise NotImplementedError()


def add_2d_points(vtk_point, extent):
    raise NotImplementedError()


def add_1d_structured(vtk_structured_grid):
    raise NotImplementedError()


def add_2d_structured(vtk_structured_grid):
    raise NotImplementedError()


def fake_structured(vtk_structured_grid):
    raise NotImplementedError()


def add_1d_unstructured(vtk_unstructured_grid, extent):
    raise NotImplementedError()


def add_2d_unstructured(vtk_unstructured_grid, extent):
    raise NotImplementedError()
