from enum import Enum
import numpy as np
from pan3d.xarray.cf import mesh
from pan3d.xarray.cf.coords.convert import is_uniform
from pan3d.xarray.cf.constants import Projection
from vtkmodules.vtkCommonDataModel import (
    vtkImageData,
    vtkRectilinearGrid,
    vtkStructuredGrid,
    vtkUnstructuredGrid,
)

PRESSURE_UNITS = {
    "bar",
    "bar",
    "millibar",
    "decibar",
    "atmosphere",
    "atm",
    "pascal",
    "Pa",
    "hPa",
}
LENGTH_UNITS = {
    "meter",
    "metre",
    "m",
    "kilometer",
    "km",
}
COORDINATES_DETECTION = {
    "longitude": {
        "units": {
            "degrees_east",
            "degree_east",
            "degree_e",
            "degrees_e",
            "degreee",  # codespell:ignore
            "degreese",
        },
        "axis": {"X"},
        "std_name": {
            "longitude",
        },
    },
    "latitude": {
        "units": {
            "degrees_north",
            "degree_north",
            "degree_n",
            "degrees_n",
            "degreen",
            "degreesn",
        },
        "axis": {"Y"},
        "std_name": {
            "latitude",
        },
    },
    "vertical": {
        "units": {},
        "axis": {"Z"},
        "std_name": {
            "depth",
            "level",
        },
        "positive": {
            "up",
            "down",
        },
    },
    "time": {
        "units": {
            "since",
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
        },
        "axis": {"T"},
        "std_name": {
            "time",
        },
        "calendar": {
            "standard",
            "utc",
            "proleptic_gregorian",
            "julian",
            "tai",
            "noleap",
            "365_day",
            "all_leap",
            "366_day",
            "360_day",
            "none",
        },
    },
}


class CoordinateType(Enum):
    LONGITUDE = "longitude"
    LATITUDE = "latitude"
    VERTICAL = "vertical"
    TIME = "time"
    UNKNOWN = "unknown"

    @classmethod
    def from_array(cls, xr_array):
        axis = xr_array.attrs.get("axis", "")
        units = xr_array.attrs.get("units", "").lower()
        std_name = xr_array.attrs.get("standard_name", "")
        positive = xr_array.attrs.get("positive", "")
        calendar = xr_array.attrs.get("calendar", "")

        # axis provide a direct mapping if available
        if axis:
            if axis == "X":
                return cls.LONGITUDE
            if axis == "Y":
                return cls.LATITUDE
            if axis == "Z":
                return cls.VERTICAL
            if axis == "T":
                return cls.TIME

        # units
        if units:
            if units in COORDINATES_DETECTION["longitude"]["units"]:
                return cls.LONGITUDE
            if units in COORDINATES_DETECTION["latitude"]["units"]:
                return cls.LATITUDE

            # Time unit check
            t_unit = COORDINATES_DETECTION["time"]["units"]
            unit_token = set(units.split(" "))
            if len(unit_token & t_unit) == 2:
                return cls.TIME

        # unique attribute
        if positive:
            return cls.VERTICAL
        if calendar:
            return cls.TIME

        # std name
        if std_name in COORDINATES_DETECTION["longitude"]["std_name"]:
            return cls.LONGITUDE
        if std_name in COORDINATES_DETECTION["latitude"]["std_name"]:
            return cls.LATITUDE
        if std_name in COORDINATES_DETECTION["time"]["std_name"]:
            return cls.TIME
        if std_name in COORDINATES_DETECTION["vertical"]["std_name"]:
            return cls.VERTICAL

        # based on data type
        if np.issubdtype(xr_array.dtype, np.datetime64):
            return cls.TIME
        if np.issubdtype(xr_array.dtype, np.dtype("O")):
            return cls.TIME

        return cls.UNKNOWN

    @classmethod
    def can_be_vertical(cls, xr_array):
        units = xr_array.attrs.get("units", "").lower()

        if xr_array.dims != (xr_array.name,):
            return False

        # vertical tends to be harder to detect
        for unit in PRESSURE_UNITS:
            if unit in units:
                return True

        for unit in LENGTH_UNITS:
            if unit in units:
                return True

        return False

    @classmethod
    def can_be_time(cls, xr_array):
        if xr_array.dims != (xr_array.name,):
            return False

        return xr_array.name in COORDINATES_DETECTION["time"]["units"]


class MetaArrayMapping:
    def __init__(self, xr_dataset):
        self.xr_dataset = None
        self.data_arrays = {}
        self.conventions = None
        self.longitude = None
        self.latitude = None
        self.vertical = None
        self.time = None
        self.valid = False
        self.vertical_bias = 6378137
        self.vertical_scale = 100

        self.update(xr_dataset)

    def update(self, xr_dataset):
        self.xr_dataset = xr_dataset
        self.valid = False
        self.data_arrays = {}
        self.conventions = None
        self.longitude = None
        self.latitude = None
        self.vertical = None
        self.time = None

        if xr_dataset is None:
            return

        self.conventions = (
            xr_dataset.Conventions if hasattr(xr_dataset, "Conventions") else None
        )
        if self.conventions is not None:
            for convention in {"COARDS", "CF-1"}:
                if convention in self.conventions:
                    self.valid = True
                    break

        # start extracting coordinates from data dimensions
        for array_name in xr_dataset:
            # skip bounds array as data array
            if "bnd" in array_name or "bound" in array_name:
                continue

            dims = xr_dataset[array_name].dims
            if dims not in self.data_arrays:
                self.data_arrays[dims] = [array_name]
                for coord_name in dims:
                    coord_type = CoordinateType.from_array(xr_dataset[coord_name])
                    if coord_type != CoordinateType.UNKNOWN:
                        setattr(self, coord_type.value, coord_name)

                    # Extended binding if not found
                    if self.vertical is None and CoordinateType.can_be_vertical(
                        xr_dataset[array_name]
                    ):
                        self.vertical = array_name
                    if self.time is None and CoordinateType.can_be_time(
                        xr_dataset[coord_name]
                    ):
                        self.time = coord_name
            else:
                self.data_arrays[dims].append(array_name)

        # inspect coordinates if not already filled
        if any(
            coord is None for coord in [self.longitude, self.latitude, self.vertical]
        ):
            for coord_name in xr_dataset.coords:
                coord_type = CoordinateType.from_array(xr_dataset[coord_name])
                if (
                    coord_type != CoordinateType.UNKNOWN
                    and getattr(self, coord_type.value) is None
                ):
                    setattr(self, coord_type.value, coord_name)

                # Extended binding if not found
                if self.vertical is None and CoordinateType.can_be_vertical(
                    xr_dataset[coord_name]
                ):
                    self.vertical = coord_name

    def __repr__(self):
        data_lines = []
        for dims, array_names in self.data_arrays.items():
            data_lines.append(f" - {dims}:")
            for name in array_names:
                data_lines.append(f"    - {name}")
        data_str = "\n".join(data_lines)
        return f"""Conventions: {self.conventions} {'✅' if self.valid else '❌'}
Coordinates:
  - longitude : {self.longitude}
  - latitude  : {self.latitude}
  - vertical  : {self.vertical}
  - time      : {self.time}
Computed:
  - has_bound     : {self.coords_has_bounds}
  - uniform (2D)  : {self.uniform_lat_lon}
  - uniform (all) : {self.uniform_spacing}
  - coords 1d     : {self.coords_1d}
Data:
{data_str}
"""

    @property
    def coords_has_bounds(self):
        if self.latitude is None or self.longitude is None:
            return None

        lon_bnd = self.xr_dataset[self.longitude].attrs.get("bounds")
        lat_bnd = self.xr_dataset[self.latitude].attrs.get("bounds")
        return lon_bnd is not None and lat_bnd is not None

    @property
    def uniform_lat_lon(self):
        return (
            self.coords_1d
            and is_uniform(self.xr_dataset[self.longitude].values)
            and is_uniform(self.xr_dataset[self.latitude].values)
        )

    @property
    def uniform_spacing(self):
        uniform = self.uniform_lat_lon

        if self.vertical is not None and uniform:
            uniform = len(self.xr_dataset[self.vertical].dims) == 1 and is_uniform(
                self.xr_dataset[self.vertical].values
            )

        return uniform

    @property
    def coords_1d(self):
        vertical_ok = True
        if self.vertical is not None:
            vertical_ok = len(
                self.xr_dataset[self.vertical].dims
            ) == 1 and self.xr_dataset[self.vertical].dims == (self.vertical,)

        return (
            vertical_ok
            and self.longitude is not None
            and len(self.xr_dataset[self.longitude].dims) == 1
            and self.xr_dataset[self.longitude].dims == (self.longitude,)
            and self.latitude is not None
            and len(self.xr_dataset[self.latitude].dims) == 1
            and self.xr_dataset[self.latitude].dims == (self.latitude,)
        )

    def use_coords(self, dims):
        if self.longitude not in dims:
            return False
        if self.latitude not in dims:
            return False
        if self.vertical is not None and self.vertical not in dims:
            return False
        return True

    def compatible_fields(self, fields=None):
        if not fields:
            return []
        data_dims = self.xr_dataset[fields[0]].dims
        return [n for n in fields if self.xr_dataset[n].dims == data_dims]

    def dimensions(self, field):
        return self.xr_dataset[field].dims

    def timeless_dimensions(self, field):
        dims = self.xr_dataset[field].dims
        return dims[1:] if dims[0] == self.time else dims

    def field_extent(self, field):
        extent = [0, 0, 0, 0, 0, 0]
        dimensions = self.timeless_dimensions(field)
        for idx in range(len(dimensions)):
            array = self.xr_dataset[dimensions[-(1 + idx)]]
            # Fill in reverse order (t, z, y, x) => [0, x.size, 0, y.size, 0, z.size]
            # And extent include both index so (len-1)
            extent[idx * 2 + 1] = array.size - 1

        return extent

    def get_vtk_mesh_type(self, projection, fields=None):
        fields = self.compatible_fields(fields)

        if self.longitude is None or self.latitude is None or not fields:
            # default empty mesh
            return vtkImageData()

        # unstructured
        timeless_dims = self.timeless_dimensions(fields[0])
        if len(timeless_dims) == 1:
            return vtkUnstructuredGrid()

        # structured
        if (
            self.coords_has_bounds
            or projection == Projection.SPHERICAL
            or not self.coords_1d
        ):
            return vtkStructuredGrid()

        # rectilinear
        if not self.uniform_spacing:
            return vtkRectilinearGrid()

        # imagedata
        return vtkImageData()

    def get_vtk_whole_extent(self, projection, fields=None):
        if self.longitude is None or self.latitude is None or not fields:
            return [
                0,
                0,
                0,
                0,
                0,
                0,
            ]

        mesh_type = self.get_vtk_mesh_type(projection, fields)
        fields = self.compatible_fields(fields)
        extent = self.field_extent(fields[0])
        dimensions = self.timeless_dimensions(fields[0])

        print(f"before {extent=}")
        print(f"class {mesh_type.GetClassName()}")

        if mesh_type.IsA("vtkStructuredGrid") and not (
            self.uniform_lat_lon and self.use_coords(dimensions)
        ):
            # point data
            return extent

        # cell data, need to +1 on the extent
        for i in range(3):
            if extent[i * 2 + 1] > 0:
                extent[i * 2 + 1] += 1

        print(f"after {extent=}")

        return extent

    def get_vtk_mesh(self, time_index=0, projection=None, fields=None):
        vtk_mesh, data_location = None, None
        if self.xr_dataset is None or not fields:
            return vtk_mesh

        # resolve projection
        if projection is None:
            projection = Projection.SPHERICAL
        spherical_proj = projection == Projection.SPHERICAL

        # ensure similar dimension across array names
        fields = self.compatible_fields(fields)
        data_dims_no_time = self.timeless_dimensions(fields[0])

        # No mesh if no lon/lat
        if self.longitude is None or self.latitude is None:
            return vtk_mesh

        # Unstructured
        if len(data_dims_no_time) == 1:
            vtk_mesh, data_location = mesh.unstructured.generate_mesh(
                self, data_dims_no_time, time_index, spherical_proj
            )

        # Structured
        if vtk_mesh is None and (
            self.coords_has_bounds or spherical_proj or not self.coords_1d
        ):
            vtk_mesh, data_location = mesh.structured.generate_mesh(
                self, data_dims_no_time, time_index, spherical_proj
            )

        # This should only happen if we don't want spherical_proj
        if vtk_mesh is None:
            assert not spherical_proj

        # Rectilinear
        if vtk_mesh is None and not self.uniform_spacing:
            vtk_mesh, data_location = mesh.rectilinear.generate_mesh(
                self, data_dims_no_time, time_index
            )

        # Uniform
        if vtk_mesh is None:
            vtk_mesh, data_location = mesh.uniform.generate_mesh(
                self, data_dims_no_time, time_index
            )

        # Add fields
        if vtk_mesh:
            container = getattr(vtk_mesh, data_location)
            for field_name in fields:
                field = (
                    self.xr_dataset[field_name][time_index].values
                    if self.time
                    else self.xr_dataset[field_name].values
                )
                container[field_name] = field.ravel()
        else:
            print(" !!! No mesh for data")

        return vtk_mesh
