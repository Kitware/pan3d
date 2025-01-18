import numpy as np
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid


def generate_mesh(metadata, dimensions, time_index):
    data_location = "point_data"
    extent = [0, 0, 0, 0, 0, 0]
    empty_coords = np.zeros((1,), dtype=np.double)
    arrays = [empty_coords, empty_coords, empty_coords]

    assert metadata.coords_1d

    for idx in range(len(dimensions)):
        array = metadata.xr_dataset[dimensions[-(1 + idx)]]
        arrays[idx] = array.values

        # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
        # And extent include both index so (len-1)
        extent[idx * 2 + 1] = array.size - 1

    mesh = vtkRectilinearGrid()
    mesh.x_coordinates = arrays[0]
    mesh.y_coordinates = arrays[1]
    mesh.z_coordinates = arrays[2]
    mesh.extent = extent

    return mesh, data_location
