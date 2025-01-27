import numpy as np
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from ..coords.convert import cell_center_to_point, slice_array


def generate_mesh(metadata, dimensions, time_index, slices):
    """
     - [X] Initial implementation
     - [X] Support range slicing
     - [X] Support index slicing
     - [ ] Automatic testing

    Testing process:
       1. load xarray tutorial dataset: eraint_uvz
       2. Switch projection to Euclidean
       3. Play with range sliders
       4. Switch one range slider to a cut
    """
    data_location = "cell_data"
    extent = [0, 0, 0, 0, 0, 0]
    empty_coords = np.zeros((1,), dtype=np.double)
    arrays = [empty_coords, empty_coords, empty_coords]

    assert metadata.coords_1d

    for idx in range(len(dimensions)):
        name = dimensions[-(1 + idx)]

        arrays[idx] = cell_center_to_point(
            slice_array(name, metadata.xr_dataset, slices)
        )

        # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
        # And extent include both index (len-1)
        extent[idx * 2 + 1] = arrays[idx].size - 1

    mesh = vtkRectilinearGrid()
    mesh.x_coordinates = arrays[0]
    mesh.y_coordinates = arrays[1]
    mesh.z_coordinates = arrays[2]
    mesh.extent = extent

    return mesh, data_location
