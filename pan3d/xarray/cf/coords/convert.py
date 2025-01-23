import math
import numpy as np


def extract_uniform_info(array):
    origin = float(array[0])
    spacing = (float(array[-1]) - origin) / (array.size - 1)
    tolerance = 0.01 * spacing

    for i in range(array.size):
        expected = origin + i * spacing
        truth = float(array[i])
        if not np.isclose(expected, truth, atol=tolerance):
            return None

    return (origin, spacing, array.size)


def is_uniform(array):
    return extract_uniform_info(array) is not None


def cell_center_to_point(in_array):
    uniform_data = extract_uniform_info(in_array)
    if uniform_data is not None:
        origin, spacing, size = uniform_data
        return np.linspace(
            start=origin - spacing * 0.5,
            stop=origin - spacing * 0.5 + size * spacing,
            num=size + 1,
            endpoint=True,
            dtype=np.double,
        )

    # generate fake coords
    n_cells = in_array.size
    n_points = n_cells + 1
    out_array = np.zeros(n_points, dtype=np.double)
    for i in range(1, n_cells):
        out_array[i] = 0.5 * (in_array[i - 1] + in_array[i])

    out_array[0] = out_array[1] - 2 * (out_array[1] - in_array[0])
    out_array[-1] = out_array[-2] + 2 * (in_array[-1] - out_array[-2])

    return out_array


def point_insert(vtk_point, spherical, longitude, latitude, vertical):
    if spherical:
        longitude = math.pi * longitude / 180
        latitude = math.pi * latitude / 180
        vtk_point.InsertNextPoint(
            vertical * math.cos(longitude) * math.cos(latitude),
            vertical * math.sin(longitude) * math.cos(latitude),
            vertical * math.sin(latitude),
        )
    else:
        vtk_point.InsertNextPoint(
            longitude,
            latitude,
            vertical,
        )
