import math


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
