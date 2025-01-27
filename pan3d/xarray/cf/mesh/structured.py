from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkStructuredGrid

from ..coords.parametric_vertical import get_formula as get_z_formula
from ..coords.index_mapping import get_formula as get_coords_formula
from ..coords.convert import point_insert, cell_center_to_point, slice_array


def generate_mesh(metadata, dimensions, time_index, spherical, slices):
    # Data location and extend depend if we can extrapolate cell locations
    # bounds or uniform allow to define cell bounds
    if metadata.coords_has_bounds:
        return generate_bound_cells(metadata, dimensions, time_index, spherical, slices)

    if metadata.uniform_spacing:
        return generate_uniform_cells(
            metadata, dimensions, time_index, spherical, slices
        )

    # We can only figure out the point location
    return generate_mesh_points(metadata, dimensions, time_index, spherical, slices)


def generate_uniform_cells(metadata, dimensions, time_index, spherical, slices):
    """
     - [X] Initial implementation
     - [X] Support range slicing
     - [X] Support index slicing
     - [ ] Automatic testing

    xarray tutorial dataset:
        - air_temperature
        - ersstv5
    """
    data_location = "cell_data"
    assert spherical

    # 2D or 3D
    dims_size = len(dimensions)
    assert dims_size == 2 or dims_size == 3

    # extract extent, origin, spacing
    origin = [0, 0, 0]
    spacing = [1, 1, 1]
    sizes = [1, 1, 1]
    for idx in range(len(dimensions)):
        name = dimensions[-(1 + idx)]
        array = slice_array(name, metadata.xr_dataset, slices)

        # axis origin/spacing (maybe)
        if array.size == 1:
            origin[idx] = float(array)
            all_array = metadata.xr_dataset[name]
            if all_array.size > 1:
                all_array = all_array[:2].values
                spacing[idx] = float(all_array[1] - all_array[0])
                origin[idx] -= 0.5 * spacing[idx]
            continue

        axis_spacing = (array[-1] - array[0]) / (array.size - 1)
        axis_origin = float(array[0]) - axis_spacing * 0.5

        # update global origin/spacing
        origin[idx] = float(axis_origin)
        spacing[idx] = float(axis_spacing)
        sizes[idx] = array.size + 1

    # debug
    # print(f"{dimensions=}")
    # print(f"{extent=}")
    # print(f"{n_points=}")
    # print(f"{dimensions=}")
    # print(f"{origin=}")
    # print(f"{spacing=}")
    # print(f"{sizes=}")

    # Points
    vtk_points = vtkPoints()
    vtk_points.SetDataTypeToDouble()
    vtk_points.Allocate(sizes[0] * sizes[1] * sizes[2])

    # Check if direct coord mapping
    for k in range(sizes[2]):
        z = origin[2] + k * spacing[2]
        z = metadata.vertical_bias + metadata.vertical_scale * z
        for j in range(sizes[1]):
            lat = origin[1] + j * spacing[1]
            for i in range(sizes[0]):
                lon = origin[0] + i * spacing[0]
                point_insert(vtk_points, spherical, lon, lat, z)

    # Mesh
    mesh = vtkStructuredGrid()
    mesh.points = vtk_points
    mesh.extent = [
        0,
        sizes[0] - 1,
        0,
        sizes[1] - 1,
        0,
        sizes[2] - 1,
    ]

    return mesh, data_location


def generate_bound_cells(metadata, dimensions, time_index, spherical, slices):
    """
    - [ ] Initial implementation
    - [ ] Support range slicing
    - [ ] Support index slicing
    - [ ] Automatic testing
    """
    data_location = "cell_data"
    raise NotImplementedError("structured::generate_bound_cells")
    return False, data_location


def generate_mesh_points(metadata, dimensions, time_index, spherical, slices):
    """
     - [ ] Initial implementation
     - [ ] Support range slicing
     - [ ] Support index slicing
     - [ ] Automatic testing

    xarray tutorial dataset:
        - ROMS_example: CUSTOM Z FORMULA
        - rasm: CUSTOM Z FORMULA but
            - non CF format
            - 2d coord remapping


    """
    data_location = "point_data"

    if (
        metadata.coords_1d
        and metadata.uniform_lat_lon
        and metadata.use_coords(dimensions)
    ):
        return generate_mesh_points_data_on_cell(
            metadata, dimensions, time_index, spherical, slices
        )

    # 2D or 3D
    dims_size = len(dimensions)
    assert dims_size == 2 or dims_size == 3

    extent = [0, 0, 0, 0, 0, 0]
    dim_ranges = [
        (0, 1, 1),  # i
        (0, 1, 1),  # j
        (0, 1, 1),  # k
    ]
    n_points = 1
    for idx in range(len(dimensions)):
        name = dimensions[-(1 + idx)]
        array = slice_array(name, metadata.xr_dataset, slices)
        all_array = metadata.xr_dataset[name]
        if array.size != all_array.size:
            slice_info = slices.get(name)
            if isinstance(slice_info, int):
                start = slice_info
                dim_ranges[idx] = (start, start + 1)
            else:
                start, stop, step = slice_info
                stop -= (stop - start) % step
                size = int((stop - start) / step)
                extent[idx * 2 + 1] = size - 1
                dim_ranges[idx] = (start, stop, step)
                n_points *= size
        else:
            # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
            # And extent include both index so (len-1)
            extent[idx * 2 + 1] = array.size - 1
            n_points *= array.size
            dim_ranges[idx] = (0, array.size, 1)

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
        print(" => 1D coords - Need data to test")
        if dims_size == 2:  # 2D
            print(" => 2D dataset - Need data to test")
            x_array = metadata.xr_dataset[metadata.longitude].values
            y_array = metadata.xr_dataset[metadata.latitude].values
            z = 0
            for j in range(*dim_ranges[1]):
                lat = y_array[j]
                for i in range(*dim_ranges[0]):
                    lon = x_array[i]
                    point_insert(vtk_points, spherical, lon, lat, z)
        else:  # 3D
            print(" => 3D dataset - Need data to test")
            x_array = metadata.xr_dataset[metadata.longitude].values
            y_array = metadata.xr_dataset[metadata.latitude].values
            z_array = metadata.xr_dataset[metadata.vertical].values
            for k in range(*dim_ranges[2]):
                z = z_array[k]
                for j in range(*dim_ranges[1]):
                    lat = y_array[j]
                    for i in range(*dim_ranges[0]):
                        lon = x_array[i]
                        point_insert(vtk_points, spherical, lon, lat, z)
    else:
        # CUSTOM Z FORMULA
        # need some index mapping
        z_formula = get_z_formula(
            metadata.xr_dataset,
            metadata.vertical,
            bias=metadata.vertical_bias,
            scale=metadata.vertical_scale,
        )
        coords_formula = get_coords_formula(metadata, dimensions)
        for k in range(*dim_ranges[2]):
            for j in range(*dim_ranges[1]):
                for i in range(*dim_ranges[0]):
                    lon, lat = coords_formula(i=i, j=j, k=k)
                    z = z_formula(i=i, j=j, k=k, n=time_index)
                    # print(f"{time_index=}, {k=}, {j=}, {i=} = {lon=}, {lat=}, {z=}")
                    point_insert(vtk_points, spherical, lon, lat, z)

    # Mesh
    mesh = vtkStructuredGrid()
    mesh.points = vtk_points
    mesh.extent = extent

    return mesh, data_location


def generate_mesh_points_data_on_cell(
    metadata, dimensions, time_index, spherical, slices
):
    """
     - [X] Initial implementation
     - [x] Support range slicing
     - [x] Support index slicing
     - [ ] Automatic testing

    Testing process 2D: <------------------- MISSING
       1. xxxx
       2. Play with range sliders
       3. Switch one range slider to a cut

    Testing process 3D:
       1. load xarray tutorial dataset: eraint_uvz | basin_mask
       2. Play with range sliders
       3. Switch one range slider to a cut
    """
    # Slice Ready
    data_location = "cell_data"

    # 2D or 3D
    dims_size = len(dimensions)
    assert dims_size == 2 or dims_size == 3

    # compute extent between dimensions and slices
    extent = metadata.dims_extent(dimensions, slices)
    n_points = 1

    # Increase extent by 1 since we add points to put data on cells
    for i in range(3):
        if extent[i * 2 + 1] > 0:
            extent[i * 2 + 1] += 1

    # Extract point count
    for i in range(3):
        n_points *= extent[i * 2 + 1] - extent[i * 2] + 1

    # Points
    vtk_points = vtkPoints()
    vtk_points.SetDataTypeToDouble()
    vtk_points.Allocate(n_points)

    # debug
    # print(f"{dimensions=}")
    # print(f"{extent=}")
    # print(f"{n_points=}")
    # print(f"{slices=}")

    # Check if direct coord mapping
    if dims_size == 2:  # 2D
        print("#" * 60)
        print("structured::generate_mesh_points_data_on_cell")
        print("We are in 2D mode\n" * 5)
        print("#" * 60)
        x_array = cell_center_to_point(
            slice_array(metadata.longitude, metadata.xr_dataset, slices)
        )
        y_array = cell_center_to_point(
            slice_array(metadata.latitude, metadata.xr_dataset, slices)
        )
        if y_array.size == 1:
            y_array = [y_array]
        if x_array.size == 1:
            x_array = [x_array]
        z = metadata.vertical_bias
        for j in range(extent[3] + 1):
            lat = y_array[j]
            for i in range(extent[1] + 1):
                lon = x_array[i]
                point_insert(vtk_points, spherical, lon, lat, z)
    else:  # 3D
        x_array = cell_center_to_point(
            slice_array(metadata.longitude, metadata.xr_dataset, slices)
        )
        y_array = cell_center_to_point(
            slice_array(metadata.latitude, metadata.xr_dataset, slices)
        )
        z_array = cell_center_to_point(
            slice_array(metadata.vertical, metadata.xr_dataset, slices)
        )
        if z_array.size == 1:
            z_array = [z_array]
        if y_array.size == 1:
            y_array = [y_array]
        if x_array.size == 1:
            x_array = [x_array]
        for k in range(extent[5] + 1):
            z = z_array[k]
            for j in range(extent[3] + 1):
                lat = y_array[j]
                for i in range(extent[1] + 1):
                    lon = x_array[i]
                    point_insert(vtk_points, spherical, lon, lat, z)

    # Mesh
    mesh = vtkStructuredGrid()
    mesh.points = vtk_points
    mesh.extent = extent

    return mesh, data_location
