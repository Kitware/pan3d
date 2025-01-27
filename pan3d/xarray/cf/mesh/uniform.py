from vtkmodules.vtkCommonDataModel import vtkImageData
from ..coords.convert import slice_array


def generate_mesh(metadata, dimensions, time_index, slices):
    """
     - [X] Initial implementation
     - [X] Support range slicing
     - [X] Support index slicing
     - [ ] Automatic testing

    Testing process:
       1. load xarray tutorial dataset: air_temperature
       2. Switch projection to Euclidean
       3. Play with range sliders
       4. Switch one range slider to a cut
    """
    data_location = "cell_data"

    # data to capture
    origin = [0, 0, 0]
    spacing = [1, 1, 1]
    extent = [0, 0, 0, 0, 0, 0]

    # extract information from dimensions
    for idx in range(len(dimensions)):
        name = dimensions[-(1 + idx)]

        array = slice_array(name, metadata.xr_dataset, slices)
        # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
        # Use size as end of extent as we are adding 1 point for map data on cell
        extent[idx * 2 + 1] = array.size

        # No spacing just origin (maybe)
        if array.size == 1:
            origin[idx] = float(array)
            all_array = metadata.xr_dataset[name]
            if all_array.size > 1:
                all_array = all_array[:2].values
                spacing[idx] = float(all_array[1] - all_array[0])
                origin[idx] -= 0.5 * spacing[idx]
            continue

        # axis origin/spacing
        axis_spacing = (array[-1] - array[0]) / (array.size - 1)
        axis_origin = float(array[0]) - axis_spacing * 0.5

        # update global origin/spacing
        origin[idx] = float(axis_origin)
        spacing[idx] = float(axis_spacing)

    # print(f"{origin=}")
    # print(f"{spacing=}")
    # print(f"{extent=}")

    # Configure mesh
    mesh = vtkImageData(origin=origin, spacing=spacing, extent=extent)

    return mesh, data_location
