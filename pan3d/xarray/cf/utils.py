import numpy as np
from . import constants
from .coords import coords_mesh_rectilinear, coords_mesh_spherical


def to_bounds(xr_dataset, coord_name):
    xr_array = xr_dataset[coord_name]
    if xr_array.dims == (coord_name,):
        bound_array_name = xr_array.attrs.get("bounds")
        if bound_array_name:
            # TODO
            # xr_dataset[bound_array_name]
            return bound_array_name
        elif np.issubdtype(xr_array.dtype, np.number):
            origin = float(xr_array.values[0])
            spacing = (float(xr_array.values[-1]) - origin) / (xr_array.size - 1)

            if xr_array.attrs.get("positive", "") == "down":
                spacing *= -1

            bounds = np.zeros(xr_array.size + 1, dtype=np.double)
            bounds[0] = float(xr_array.values[0]) - 0.5 * spacing
            for i in range(1, xr_array.size):
                center = 0.5 * float(xr_array.values[i - 1] + xr_array.values[i])
                bounds[i] = center
            bounds[-1] = float(xr_array.values[-1]) + 0.5 * spacing

            return bounds

    # fake coordinates
    return np.linspace(
        -0.5, xr_array.size - 0.5, num=xr_array.size + 1, dtype=np.double
    )


class Coordinates:
    def __init__(self, xr_dataset, vertical_scale=1, vertical_bias=0):
        self.xr_dataset = xr_dataset
        self.vertical_scale = vertical_scale
        self.vertical_bias = vertical_bias
        self.longitude = None
        self.latitude = None
        self.vertical = None
        self.time = None

        for coord_name in xr_dataset.coords:
            unit = constants.Units.extract(xr_dataset[coord_name])
            if unit == constants.Units.LONGITUDE_UNITS:
                self.longitude = coord_name
            elif unit == constants.Units.LATITUDE_UNITS:
                self.latitude = coord_name
            elif unit == constants.Units.VERTICAL_UNITS:
                self.vertical = coord_name
            elif unit == constants.Units.TIME_UNITS:
                self.time = coord_name
            else:
                print(f"Skip coord {coord_name}")

    @property
    def extent(self):
        x_size = self.longitude_array.size if self.longitude else 0
        y_size = self.latitude_array.size if self.latitude else 0
        z_size = self.vertical_array.size if self.vertical else 0

        return [
            0,
            x_size,
            0,
            y_size,
            0,
            z_size,
        ]

    @property
    def origin(self):
        print(self.longitude, "=>", self.longitude_array.dims)
        print(self.latitude, "=>", self.latitude_array.dims)
        x = self.longitude_array.values[0] if self.longitude else 0
        y = self.latitude_array.values[0] if self.latitude else 0
        z = self.vertical_array.values[0] if self.vertical else 0
        return [x, y, z]

    @property
    def spacing(self):
        origin = self.origin
        sx, sy, sz = 1, 1, 1
        if self.longitude:
            coord = self.longitude_array
            sx = (float(coord.values[-1]) - origin[0]) / (coord.size - 1)
            if coord.attrs.get("positive", "") == "down":
                sx *= -1
        if self.latitude:
            coord = self.latitude_array
            sy = (float(coord.values[-1]) - origin[1]) / (coord.size - 1)
            if coord.attrs.get("positive", "") == "down":
                sy *= -1
        if self.vertical:
            coord = self.vertical_array
            sz = (float(coord.values[-1]) - origin[2]) / (coord.size - 1)
            if coord.attrs.get("positive", "") == "down":
                sz *= -1

        return [sx, sy, sz]

    @property
    def longitude_array(self):
        if self.longitude is None:
            return None

        return self.xr_dataset[self.longitude]

    @property
    def longitude_bounds(self):
        if self.longitude is None:
            return None

        return to_bounds(self.xr_dataset, self.longitude)

    @property
    def latitude_array(self):
        if self.latitude is None:
            return None

        return self.xr_dataset[self.latitude]

    @property
    def latitude_bounds(self):
        if self.latitude is None:
            return None

        return to_bounds(self.xr_dataset, self.latitude)

    @property
    def vertical_array(self):
        if self.vertical is None:
            return None

        return self.xr_dataset[self.vertical]

    @property
    def vertical_bounds(self):
        if self.vertical is None:
            return None

        return to_bounds(self.xr_dataset, self.vertical)

    @property
    def time_array(self):
        if self.time is None:
            return None

        return self.xr_dataset[self.time]


class XArrayDataSetCFHelper:
    def __init__(self, xr_dataset):
        self.xr_dataset = xr_dataset
        self._active_array_names = {}
        self._active_dimensions = None
        self._cached_dimensions_info = {}
        self._x = None
        self._y = None
        self._z = None
        self._t = None

    @property
    def available_arrays(self) -> list[str]:
        if self._active_dimensions is None:
            return [
                n
                for n in self.xr_dataset.data_vars.keys()
                if "bnd" not in n and "bound" not in n
            ]

        # List only arrays with the same active dimensions
        return [
            n
            for n in self.xr_dataset.data_vars.keys()
            if self.xr_dataset[n].dims == self._active_dimensions
        ]

    @property
    def array_selection(self) -> set[str]:
        """return the list of arrays that are currently selected to be added to the generated VTK mesh"""
        return self._active_array_names

    @array_selection.setter
    def array_selection(self, array_names=None):
        """update the list of arrays to load on the generated VTK mesh"""
        if array_names is None:
            array_names = []

        # Filter with only valid arrays
        allowed_names = set(self.available_arrays)
        new_names = set([n for n in array_names if n in allowed_names])

        # Do we have a change
        if new_names != self._active_array_names:
            if len(new_names):
                # Check compatibility
                self._active_dimensions = None
                compatible_set = set()
                for name in new_names:
                    if self._active_dimensions is None:
                        self._active_dimensions = self.xr_dataset[name].dims
                        compatible_set.add(name)
                    elif self.xr_dataset[name].dims == self._active_dimensions:
                        compatible_set.add(name)

                self._active_array_names = compatible_set
            else:
                # no selection
                self._active_array_names = new_names
                self._active_dimensions = None

            # Update dimension mapping
            self._compute_dimensions_information()

            return True

        return False

    def _compute_dimensions_information(self):
        # reset
        self._cached_dimensions_info.clear()
        self._x = None
        self._y = None
        self._z = None
        self._t = None
        self._t_index = 0

        # look deeper if possible
        if self._active_dimensions is None:
            return

        # extract field dimension information
        for dim_name in self._active_dimensions:
            info = constants.DimensionInformation(self.xr_dataset, dim_name)
            self._cached_dimensions_info[dim_name] = info

            # track dimension orientation
            if info.unit == constants.Units.LONGITUDE_UNITS:
                self._x = dim_name
            if info.unit == constants.Units.LATITUDE_UNITS:
                self._y = dim_name
            if info.unit == constants.Units.VERTICAL_UNITS:
                self._z = dim_name
            if info.unit == constants.Units.TIME_UNITS:
                self._t = dim_name

        # extract coord dimension from dataset
        for coord_name in self.xr_dataset.coords:
            if coord_name not in self._cached_dimensions_info:
                info = constants.DimensionInformation(self.xr_dataset, coord_name)
                self._cached_dimensions_info[coord_name] = info

                # track dimension orientation
                if info.unit == constants.Units.LONGITUDE_UNITS:
                    self._x = coord_name
                if info.unit == constants.Units.LATITUDE_UNITS:
                    self._y = coord_name
                if info.unit == constants.Units.VERTICAL_UNITS:
                    self._z = coord_name

    @property
    def x(self):
        """return the name that is currently mapped to the X axis"""
        return self._x

    @property
    def x_size(self):
        """return the size of the coordinate used for the X axis"""
        if self._x is None:
            return 0
        return int(self.xr_dataset[self._x].size)

    @property
    def x_info(self):
        """return the X coordinate information if available"""
        if self._x is None:
            return None
        return self._cached_dimensions_info.get(self._x)

    @property
    def y(self):
        """return the name that is currently mapped to the Y axis"""
        return self._y

    @property
    def y_size(self):
        """return the size of the coordinate used for the Y axis"""
        if self._y is None:
            return 0
        return int(self.xr_dataset[self._y].size)

    @property
    def y_info(self):
        """return the Y coordinate information if available"""
        if self._y is None:
            return None
        return self._cached_dimensions_info.get(self._y)

    @property
    def z(self):
        """return the name that is currently mapped to the Z axis"""
        return self._z

    @property
    def z_size(self):
        """return the size of the coordinate used for the Z axis"""
        if self._z is None:
            return 0
        return int(self.xr_dataset[self._z].size)

    @property
    def z_info(self):
        """return the Z coordinate information if available"""
        if self._z is None:
            return None
        return self._cached_dimensions_info.get(self._z)

    @property
    def t(self):
        """return the name that is currently mapped to the time axis"""
        return self._t

    @property
    def t_size(self):
        """return the size of the coordinate used for the time axis"""
        if self._t is None:
            return 0
        return int(self.xr_dataset[self._t].size)

    @property
    def t_info(self):
        """return the T coordinate information if available"""
        if self._t is None:
            return None
        return self._cached_dimensions_info.get(self._t)

    def get_info(self, name):
        info = self._cached_dimensions_info.get(name)
        if info is None:
            info = self._cached_dimensions_info.setdefault(
                name, constants.DimensionInformation(self.xr_dataset, name)
            )
        return info

    @property
    def mesh(self):
        if not self._cached_dimensions_info:
            print("no cache")
            return None

        if len(self.array_selection) == 0:
            print("no field")
            return None

        # Most coordinate variables are defined by a variable the same name as the
        # dimension they describe.  Those are handled elsewhere.  This class handles
        # dependent variables that define coordinates that are not the same name as
        # any dimension.  This is only done when the coordinates cannot be expressed
        # as a 1D table lookup from dimension index.  This occurs in only two places
        # in the CF convention.  First, it happens for 2D coordinate variables with
        # 4-sided cells.  This is basically when the grid is a 2D curvilinear grid.
        # Each i,j topological point can be placed anywhere in space.  Second, it
        # happens for multi-dimensional coordinate variables with p-sided cells.
        # These are unstructured collections of polygons.

        # we need at least a 2D surface
        if self.x is None and self.y is None:
            print("no (x,y)")
            return None

        if len(self.x_info.dims) != len(self.y_info.dims):
            msg = f"Number of dimensions in different coordinate arrays do not match (x:{self.x_info.dims}, y:{self.y_info.dims})"
            raise ValueError(msg)

        field_name = next(iter(self.array_selection))
        coord_mode = constants.CoordinateTypes.get_coordinate_type(
            self.xr_dataset, field_name, use_spherical=True
        )
        print(f"{coord_mode=}")
        mesh_type = constants.MeshTypes.from_coord_type(coord_mode)
        mesh = mesh_type.new()

        # -------------------------------------------------
        # Generate mesh structure
        # -------------------------------------------------
        if mesh_type == constants.MeshTypes.VTK_IMAGE_DATA:
            coords_mesh_rectilinear.add_imagedata(mesh, Coordinates(self.xr_dataset))
        elif mesh_type == constants.MeshTypes.VTK_RECTILINEAR_GRID:
            if coord_mode in {
                constants.CoordinateTypes.EUCLIDEAN_PSIDED_CELLS,
                constants.CoordinateTypes.SPHERICAL_PSIDED_CELLS,
            }:
                # There is no sensible way to store p-sided cells in a structured grid.
                # Just fake some coordinates (related to ParaView bug #11543).
                coords_mesh_rectilinear.fake_rectilinear(mesh, self.xr_dataset)
            else:
                coords_mesh_rectilinear.add_rectilinear(mesh, self.xr_dataset)
        elif mesh_type in {
            constants.MeshTypes.VTK_STRUCTURED_GRID,
            constants.MeshTypes.VTK_UNSTRUCTURED_GRID,
        }:
            if coord_mode in {
                constants.CoordinateTypes.UNIFORM_RECTILINEAR,
                constants.CoordinateTypes.NONUNIFORM_RECTILINEAR,
            }:
                if mesh_type == constants.MeshTypes.VTK_STRUCTURED_GRID:
                    coords_mesh_rectilinear.add_1d_structured(mesh, self.xr_dataset)
                else:
                    coords_mesh_rectilinear.add_1d_unstructured(mesh, self.xr_dataset)
            elif coord_mode == constants.CoordinateTypes.REGULAR_SPHERICAL:
                if mesh_type == constants.MeshTypes.VTK_STRUCTURED_GRID:
                    coords_mesh_spherical.add_1d_structured(
                        mesh, Coordinates(self.xr_dataset)
                    )
                else:
                    coords_mesh_spherical.add_1d_unstructured(mesh, self.xr_dataset)
            elif coord_mode in {
                constants.CoordinateTypes.EUCLIDEAN_2D,
                constants.CoordinateTypes.EUCLIDEAN_4SIDED_CELLS,
            }:
                if mesh_type == constants.MeshTypes.VTK_STRUCTURED_GRID:
                    coords_mesh_rectilinear.add_2d_structured(mesh, self.xr_dataset)
                else:
                    coords_mesh_rectilinear.add_2d_unstructured(mesh, self.xr_dataset)
            elif coord_mode in {
                constants.CoordinateTypes.SPHERICAL_2D,
                constants.CoordinateTypes.SPHERICAL_4SIDED_CELLS,
            }:

                coords_mesh_spherical.add_2d_structured(mesh, self.xr_dataset)
            elif coord_mode in {
                constants.CoordinateTypes.EUCLIDEAN_PSIDED_CELLS,
                constants.CoordinateTypes.SPHERICAL_PSIDED_CELLS,
            }:
                # There is no sensible way to store p-sided cells in a structured grid.
                # Just fake some coordinates (ParaView bug #11543).
                coords_mesh_rectilinear.fake_structured(mesh, self.xr_dataset)
            else:
                msg = f"Unknown coordinate type {coord_mode}"
                raise ValueError(msg)
        elif mesh_type == constants.MeshTypes.VTK_UNSTRUCTURED_GRID:
            if coord_mode in {
                constants.CoordinateTypes.UNIFORM_RECTILINEAR,
                constants.CoordinateTypes.NONUNIFORM_RECTILINEAR,
            }:
                coords_mesh_rectilinear.add_1d_unstructured(mesh, self.xr_dataset)

        # -------------------------------------------------
        # Add fields to mesh
        # -------------------------------------------------
        for field_name in self.array_selection:
            array = self.xr_dataset[field_name]

            # slice array with current time
            if self.t:
                array = array.isel({self.t: self._t_index})

            if coord_mode.use_point_data:
                mesh.point_data[field_name] = array.values.ravel(order="C")
            else:
                mesh.cell_data[field_name] = array.values.ravel(order="C")

        # -------------------------------------------------
        # Add time metadata
        # -------------------------------------------------
        # TODO

        return mesh
