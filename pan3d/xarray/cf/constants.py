from enum import Enum
import re
import numpy as np
from vtkmodules.vtkCommonDataModel import (
    vtkImageData,
    vtkRectilinearGrid,
    vtkStructuredGrid,
    vtkUnstructuredGrid,
)

LATITUDE_REGEXP = "degrees?_?n"  # degrees_north
LONGITUDE_REGEXP = "degrees?_?e"  # degrees_east


class DimensionInformation:
    def __init__(self, xr_dataset, name):
        coord = xr_dataset[name]

        self._xr_dataset = xr_dataset
        self.name = name
        self.attrs = coord.attrs
        self.origin = 0
        self.spacing = 1
        self.has_regular_spacing = True  # will be updated later
        self.unit = Units.UNDEFINED_UNITS
        self.dims = coord.dims
        self.has_bounds = False
        self.dim_size = -1

        # unit handling
        self.unit = Units.extract(coord)

        # is as direct mapping
        if coord.dims == (name,):
            # coordinates handling (origin, spacing, has_regular_spacing)
            self.dim_size = 1
            self.coords = coord.values
            self.origin = float(coord.values[0])
            self.spacing = (float(coord.values[-1]) - self.origin) / (coord.size - 1)
            tolerance = 0.01 * self.spacing

            for i in range(coord.size):
                expected = self.origin + i * self.spacing
                truth = float(coord.values[i])
                if not np.isclose(expected, truth, atol=tolerance):
                    self.has_regular_spacing = False
                    break

            # direction
            if coord.attrs.get("positive", "") == "down":
                self.spacing *= -1

            # bounds
            bounds = coord.attrs.get("bounds")
            if bounds:
                # TODO ? only min/max
                self.bounds = None
                self.has_bounds = bounds
            elif np.issubdtype(coord.dtype, np.number):
                self.coords = coord.values
                self.bounds = np.zeros(coord.size + 1, dtype=np.double)
                self.bounds[0] = float(coord.values[0]) - 0.5 * self.spacing
                for i in range(1, coord.size):
                    center = 0.5 * float(coord.values[i - 1] + coord.values[i])
                    self.bounds[i] = center
                self.bounds[-1] = float(coord.values[-1]) + 0.5 * self.spacing
        else:  # Fake coordinates
            xr_dataset
            # TODO should do a better job
            self.origin = 0
            self.spacing = 1
            self.coords = np.linspace(
                0, coord.size - 1, num=coord.size, dtype=np.double
            )
            self.bounds = np.linspace(
                -0.5, coord.size - 0.5, num=coord.size + 1, dtype=np.double
            )

    def __repr__(self):
        return f"""
{self.name}:
  - origin     : {self.origin}
  - spacing    : {self.spacing}
  - uniform    : {self.has_regular_spacing}
  - unit       : {self.unit}
  - dimensions : {self.dims}
  - bounds     : {self.has_bounds}
  - attributes : {self.attrs}
        """


class Projection(Enum):
    SPHERICAL = "Spherical"
    EUCLIDEAN = "Euclidean"


class Scale(Enum):
    da = (1e1, {"deca", "deka"})
    h = (1e2, {"hecto"})
    k = (1e3, {"kilo"})
    M = (1e6, {"mega"})
    G = (1e9, {"giga"})
    T = (1e12, {"tera"})
    P = (1e15, {"peta"})
    E = (1e18, {"exa"})
    Z = (1e21, {"zetta"})
    Y = (1e24, {"yotta"})
    d = (1e-1, {"deci"})
    c = (1e-2, {"centi"})
    m = (1e-3, {"milli"})
    u = (1e-6, {"micro"})
    n = (1e-9, {"nano"})
    p = (1e-12, {"pico"})
    f = (1e-15, {"femto"})
    a = (1e-18, {"atto"})
    z = (1e-21, {"zepto"})
    y = (1e-24, {"yocto"})
    IDENTITY = (1, {})

    def __float__(self):
        return self.value[0]

    @classmethod
    def from_name(cls, name):
        for scale in cls:
            if name in scale.value[1]:
                return scale
        return cls.IDENTITY


class Units(Enum):
    UNDEFINED_UNITS = "undefined"
    TIME_UNITS = "time"
    LATITUDE_UNITS = "latitude"
    LONGITUDE_UNITS = "longitude"
    VERTICAL_UNITS = "vertical"
    NUMBER_OF_UNITS = "number"

    @classmethod
    def extract(cls, xr_array):
        # 1. check "units"
        units = xr_array.attrs.get("units", "").lower()
        if units:
            # time
            if units in KNOWN_TIME_UNITS:
                return cls.TIME_UNITS
            for time_str in KNOWN_TIME_CONTAINS:
                if time_str in units:
                    return cls.TIME_UNITS

            # latitude
            if re.search(LATITUDE_REGEXP, units) is not None:
                return cls.LATITUDE_UNITS

            # longitude
            if re.search(LONGITUDE_REGEXP, units) is not None:
                return cls.LONGITUDE_UNITS

        # 2. check "axis"
        axis = xr_array.attrs.get("axis", "").lower()
        if axis:
            if axis == "x":
                return cls.LONGITUDE_UNITS
            if axis == "y":
                return cls.LATITUDE_UNITS
            if axis == "z":
                return cls.VERTICAL_UNITS
            if axis == "t":
                return cls.TIME_UNITS

        # 3. use field name
        field_name = xr_array.name.lower()
        if "time" in field_name:
            return cls.TIME_UNITS
        if "lat" in field_name:
            return cls.LATITUDE_UNITS
        if "lon" in field_name:
            return cls.LONGITUDE_UNITS

        # 4. data type
        if np.issubdtype(xr_array.dtype, np.datetime64):
            print("time because of type datetime64")
            return cls.TIME_UNITS
        if np.issubdtype(xr_array.dtype, np.dtype("O")):
            print("time because of type O")
            return cls.TIME_UNITS

        # Don't know
        return cls.UNDEFINED_UNITS


MESH_3D_UNITS = {
    Units.LATITUDE_UNITS,
    Units.LONGITUDE_UNITS,
    Units.VERTICAL_UNITS,
}
MESH_2D_UNITS = {
    Units.LATITUDE_UNITS,
    Units.LONGITUDE_UNITS,
}


class MeshTypes(Enum):
    VTK_IMAGE_DATA = vtkImageData
    VTK_RECTILINEAR_GRID = vtkRectilinearGrid
    VTK_STRUCTURED_GRID = vtkStructuredGrid
    VTK_UNSTRUCTURED_GRID = vtkUnstructuredGrid

    @classmethod
    def from_coord_type(cls, coord_type):
        if coord_type == CoordinateTypes.UNIFORM_RECTILINEAR:
            return cls.VTK_IMAGE_DATA
        if coord_type == CoordinateTypes.NONUNIFORM_RECTILINEAR:
            return cls.VTK_RECTILINEAR_GRID
        if coord_type in {
            CoordinateTypes.REGULAR_SPHERICAL,
            CoordinateTypes.EUCLIDEAN_2D,
            CoordinateTypes.SPHERICAL_2D,
            CoordinateTypes.EUCLIDEAN_4SIDED_CELLS,
            CoordinateTypes.SPHERICAL_4SIDED_CELLS,
        }:
            return cls.VTK_STRUCTURED_GRID
        if coord_type in {
            CoordinateTypes.EUCLIDEAN_PSIDED_CELLS,
            CoordinateTypes.SPHERICAL_PSIDED_CELLS,
        }:
            return cls.VTK_STRUCTURED_GRID

        msg = f"Don't have a matching mesh for {coord_type}"
        raise ValueError(msg)

    def new(self):
        return self.value()


class CoordinateTypes(Enum):
    UNIFORM_RECTILINEAR = "uniform rectilinear"
    NONUNIFORM_RECTILINEAR = "non-uniform rectilinear"
    REGULAR_SPHERICAL = "regular spherical"
    EUCLIDEAN_2D = "2d euclidean"
    SPHERICAL_2D = "2d spherical"
    EUCLIDEAN_4SIDED_CELLS = "euclidean 4 sided cells"
    SPHERICAL_4SIDED_CELLS = "spherical 4 sided cells"
    EUCLIDEAN_PSIDED_CELLS = "euclidean p-sided cells"
    SPHERICAL_PSIDED_CELLS = "spherical p-sided cells"

    @classmethod
    def get_coordinate_type(cls, xr_dataset, field_name, use_spherical=False):
        print(f"{use_spherical=}")
        # Remove time axis
        dims = [
            array_name
            for array_name in xr_dataset[field_name].dims
            if Units.extract(xr_dataset[array_name]) != Units.TIME_UNITS
        ]
        coords = xr_dataset[field_name].coords
        cells_unstructured = len(coords) != len(dims) and len(dims) == 1
        has_bounds_count = 0

        # Check bounds
        for coord_name in coords:
            if Units.extract(xr_dataset[coord_name]) in MESH_2D_UNITS:
                if xr_dataset[coord_name].attrs.get("bounds"):
                    has_bounds_count += 1

        if cells_unstructured:
            return (
                cls.SPHERICAL_PSIDED_CELLS
                if use_spherical
                else cls.EUCLIDEAN_PSIDED_CELLS
            )

        if has_bounds_count == 2:
            return cls.SPHERICAL_2D if use_spherical else cls.EUCLIDEAN_2D

        name_to_unit = {
            dim_name: Units.extract(xr_dataset[dim_name]) for dim_name in dims
        }
        dim_units = set(name_to_unit.values())
        if use_spherical:
            if dim_units >= MESH_2D_UNITS or dim_units >= MESH_3D_UNITS:
                return cls.REGULAR_SPHERICAL

        # Check irregular spacing
        for name, unit in name_to_unit.items():
            if unit in MESH_3D_UNITS:
                info = DimensionInformation(xr_dataset, name)
                if not info.has_regular_spacing:
                    return cls.NONUNIFORM_RECTILINEAR

        return cls.UNIFORM_RECTILINEAR

    @property
    def use_point_data(self):
        # point_data for only the following types
        return self in {
            CoordinateTypes.UNIFORM_RECTILINEAR,
            CoordinateTypes.NONUNIFORM_RECTILINEAR,
            CoordinateTypes.EUCLIDEAN_2D,
            CoordinateTypes.SPHERICAL_2D,
        }


KNOWN_TIME_CONTAINS = {
    " since ",
    " after ",
}
KNOWN_TIME_UNITS = {
    "second",
    "seconds",
    "day",
    "days",
    "hour",
    "hours",
    "minute",
    "minutes",
    "s",
    "sec",
    "secs",
    "shake",
    "shakes",
    "sidereal_day",
    "sidereal_days",
    "sidereal_hour",
    "sidereal_hours",
    "sidereal_minute",
    "sidereal_minutes",
    "sidereal_second",
    "sidereal_seconds",
    "sidereal_year",
    "sidereal_years",
    "tropical_year",
    "tropical_years",
    "lunar_month",
    "lunar_months",
    "common_year",
    "common_years",
    "leap_year",
    "leap_years",
    "Julian_year",
    "Julian_years",
    "Gregorian_year",
    "Gregorian_years",
    "sidereal_month",
    "sidereal_months",
    "tropical_month",
    "tropical_months",
    "d",
    "min",
    "mins",
    "hrs",
    "h",
    "fortnight",
    "fortnights",
    "week",
    "jiffy",
    "jiffies",
    "year",
    "years",
    "yr",
    "yrs",
    "a",
    "eon",
    "eons",
    "month",
    "months",
}
