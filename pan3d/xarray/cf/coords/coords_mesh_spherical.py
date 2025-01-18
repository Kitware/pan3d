import math
from vtkmodules.vtkCommonCore import vtkPoints, vtkMath


def add_1d_points(vtk_point, coords):
    extent = coords.extent
    vtk_point.SetDataTypeToDouble()
    vtk_point.Allocate(
        (extent[1] - extent[0] + 1)
        * (extent[3] - extent[2] + 1)
        * (extent[5] - extent[4] + 1)
    )

    # check the height scale and bias
    z_scale = coords.vertical_scale
    z_bias = coords.vertical_bias
    if coords.vertical:
        z_min = float(coords.vertical_array.min())
        z_max = float(coords.vertical_array.max())
        if z_min * z_scale + z_bias < 0 or z_max * z_scale + z_bias < 0:
            z_bias = -math.min(z_min, z_max) * z_scale
    elif (z_scale + z_bias) <= 0:
        z_scale = 1
        z_bias = 0

    # Fill points
    longitude = coords.longitude_bounds
    latitude = coords.latitude_bounds
    vertical = coords.vertical_bounds
    for k in range(extent[4], extent[5] + 1):
        h = vertical[k] if vertical else 1
        h = h * z_scale + z_bias
        for j in range(extent[2], extent[3] + 1):
            lat = vtkMath.RadiansFromDegrees(latitude[j])
            for i in range(extent[0], extent[1] + 1):
                lon = vtkMath.RadiansFromDegrees(longitude[i])
                vtk_point.InsertNextPoint(
                    h * math.cos(lon) * math.cos(lat),
                    h * math.sin(lon) * math.cos(lat),
                    h * math.sin(lat),
                )


def add_2d_points(vtk_point, extent):
    raise NotImplementedError()


def add_1d_structured(vtk_structured, coords):
    vtk_structured.SetExtent(coords.extent)
    vtk_points = vtkPoints()
    add_1d_points(vtk_points, coords)
    vtk_structured.SetPoints(vtk_points)


def add_2d_structured(vtk_point, extent):
    raise NotImplementedError()


def add_1d_unstructured(vtk_point, extent):
    raise NotImplementedError()


def add_2d_unstructured(vtk_point, extent):
    raise NotImplementedError()
