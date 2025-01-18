from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkStructuredGrid

from ..coords.parametric_vertical import get_formula as get_z_formula
from ..coords.index_mapping import get_formula as get_coords_formula
from ..coords.convert import point_insert


def generate_mesh(metadata, dimensions, time_index, spherical):
    # Data location and extend depend if we can extrapolate cell locations
    # bounds or uniform allow to define cell bounds
    if metadata.coords_has_bounds:
        print(" => structured: bounds")
        return generate_bound_cells(metadata, dimensions, time_index, spherical)

    if metadata.uniform_spacing:
        print(" => structured: uniform spacing")
        return generate_uniform_cells(metadata, dimensions, time_index, spherical)

    # We can only figure out the point location
    print(" => structured: on points")
    return generate_mesh_points(metadata, dimensions, time_index, spherical)


def generate_uniform_cells(metadata, dimensions, time_index, spherical):
    data_location = "cell_data"
    assert spherical

    # 2D or 3D
    dims_size = len(dimensions)
    assert dims_size == 2 or dims_size == 3

    # extract extent, origin, spacing
    origin = [0, 0, 0]
    spacing = [1, 1, 1]
    extent = [0, 0, 0, 0, 0, 0]
    n_points = 1
    dims_origin_spacing = []
    for idx in range(len(dimensions)):
        array = metadata.xr_dataset[dimensions[-(1 + idx)]]

        # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
        # Use size as end of extent as we are adding 1 point for map data on cell
        extent[idx * 2 + 1] = array.size
        n_points *= array.size

        # axis origin/spacing
        axis_spacing = (array[-1].values - array[0].values) / (array.size - 1)
        axis_origin = float(array[0].values) - axis_spacing * 0.5

        # update global origin/spacing
        origin[idx] = axis_origin
        spacing[idx] = axis_spacing

    # Add (origin, spacing) for missing coords
    while len(dims_origin_spacing) < 3:
        dims_origin_spacing.insert(0, (0, 1))

    # debug
    # print(f"{dimensions=}")
    # print(f"{extent=}")
    # print(f"{n_points=}")
    # print(f"{dimensions=}")
    # print(f"{extent=}")
    # print(f"{dims_origin_spacing=}")

    # Points
    vtk_points = vtkPoints()
    vtk_points.SetDataTypeToDouble()
    vtk_points.Allocate(n_points)

    # Check if direct coord mapping
    for k in range(extent[5] + 1):
        z = origin[2] + k * spacing[2]
        z = metadata.vertical_bias + metadata.vertical_scale * z
        for j in range(extent[3] + 1):
            lat = origin[1] + j * spacing[1]
            for i in range(extent[1] + 1):
                lon = origin[0] + i * spacing[0]
                point_insert(vtk_points, spherical, lon, lat, z)

    # Mesh
    mesh = vtkStructuredGrid()
    mesh.points = vtk_points
    mesh.extent = extent

    return mesh, data_location


def generate_bound_cells(metadata, dimensions, time_index, spherical):
    data_location = "cell_data"
    raise NotImplementedError("structured::generate_bound_cells")
    return False, data_location


def generate_mesh_points(metadata, dimensions, time_index, spherical):
    data_location = "point_data"

    if metadata.coords_1d and metadata.uniform_spacing:
        print("Should put data on cell!")

    # 2D or 3D
    dims_size = len(dimensions)
    assert dims_size == 2 or dims_size == 3

    extent = [0, 0, 0, 0, 0, 0]
    n_points = 1
    for idx in range(len(dimensions)):
        array = metadata.xr_dataset[dimensions[-(1 + idx)]]
        # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
        # And extent include both index so (len-1)
        extent[idx * 2 + 1] = array.size - 1
        n_points *= array.size

    # Points
    vtk_points = vtkPoints()
    vtk_points.SetDataTypeToDouble()
    vtk_points.Allocate(n_points)

    # debug
    # print(f"{dimensions=}")
    # print(f"{extent=}")
    # print(f"{n_points=}")

    # Check if direct coord mapping
    if metadata.coords_1d and metadata.use_coords(dimensions):
        if dims_size == 2:  # 2D
            x_array = metadata.xr_dataset[metadata.longitude].values
            y_array = metadata.xr_dataset[metadata.latitude].values
            z = 0
            for j in range(extent[3] + 1):
                lat = y_array[j]
                for i in range(extent[1] + 1):
                    lon = x_array[i]
                    point_insert(vtk_points, spherical, lon, lat, z)
        else:  # 3D
            x_array = metadata.xr_dataset[metadata.longitude].values
            y_array = metadata.xr_dataset[metadata.latitude].values
            z_array = metadata.xr_dataset[metadata.vertical].values
            for k in range(extent[5] + 1):
                z = z_array[k]
                for j in range(extent[3] + 1):
                    lat = y_array[j]
                    for i in range(extent[1] + 1):
                        lon = x_array[i]
                        point_insert(vtk_points, spherical, lon, lat, z)
    else:
        # need some index mapping
        z_formula = get_z_formula(
            metadata.xr_dataset,
            metadata.vertical,
            bias=metadata.vertical_bias,
            scale=metadata.vertical_scale,
        )
        coords_formula = get_coords_formula(metadata, dimensions)
        for k in range(extent[5] + 1):
            for j in range(extent[3] + 1):
                for i in range(extent[1] + 1):
                    lon, lat = coords_formula(i=i, j=j, k=k)
                    z = z_formula(i=i, j=j, k=k, n=time_index)
                    # print(f"{time_index=}, {k=}, {j=}, {i=} = {lon=}, {lat=}, {z=}")
                    point_insert(vtk_points, spherical, lon, lat, z)

    # Mesh
    mesh = vtkStructuredGrid()
    mesh.points = vtk_points
    mesh.extent = extent

    return mesh, data_location
