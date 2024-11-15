import traceback
from typing import List, Optional

import json
import numpy as np
import pandas as pd
import xarray as xr
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkFiltersCore import vtkArrayCalculator

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def get_time_labels(times):
    return [pd.to_datetime(time).strftime("%Y-%m-%d %H:%M:%S") for time in times]


def slice_array(array_name, dataset, slice_info):
    if array_name is None:
        return np.zeros(1, dtype=np.float32)
    array = dataset[array_name].values
    if slice_info is None:
        return array
    if isinstance(slice_info, int):
        return array[slice_info]
    return array[slice(*slice_info)]


def to_isel(slices_info, *array_names):
    slices = {}
    for name in array_names:
        if name is None:
            continue

        info = slices_info.get(name)
        if info is None:
            continue
        if isinstance(info, int):
            slices[name] = info
        else:
            slices[name] = slice(*info)

    return slices if slices else None


def is_time_type(dtype):
    if np.issubdtype(dtype, np.datetime64):
        return True

    if np.issubdtype(dtype, np.dtype("O")):
        return True

    return False


# -----------------------------------------------------------------------------
# VTK Algorithms
# -----------------------------------------------------------------------------


class vtkXArrayRectilinearSource(VTKPythonAlgorithmBase):
    def __init__(
        self,
        input: Optional[xr.Dataset] = None,
        x: Optional[str] = None,
        y: Optional[str] = None,
        z: Optional[str] = None,
        t: Optional[str] = None,
        arrays: Optional[List[str]] = None,
        order: str = "C",
    ):
        VTKPythonAlgorithmBase.__init__(
            self,
            nInputPorts=0,
            nOutputPorts=1,
            outputType="vtkRectilinearGrid",
        )
        # Data source
        self._input = input
        self._xarray_mesh = None
        self._pipeline = None
        self._computed = {}
        self._data_origin = None

        # Array name selectors
        self._x = x
        self._y = y
        self._z = z
        self._t = t

        # Data sub-selection
        self._array_names = set(arrays or [])
        self._t_index = 0
        self._slices = None

        # Data order
        self._order = order

        # Auto apply coords if none provided
        if all(v is None for v in (x, y, z, t)):
            self.apply_coords()

        if len(self._array_names) == 0:
            self.arrays = self.available_arrays

    def __str__(self):
        return f"""
x: {self.x}
y: {self.y}
z: {self.z}
t: {self.t} ({self.t_index + 1}/{self.t_size})
loaded: {self.arrays}
all:    {self.available_arrays}
slices: {json.dumps(self.slices, indent=2)}
computed: {json.dumps(self.computed, indent=2)}
order: {self._order}
"""

    # -------------------------------------------------------------------------
    # Data input
    # -------------------------------------------------------------------------

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, xarray_dataset: xr.Dataset):
        self._input = xarray_dataset
        self._xarray_mesh = None
        self.Modified()

    # -------------------------------------------------------------------------
    # Array selectors
    # -------------------------------------------------------------------------

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x_array_name: str):
        if x_array_name is None:
            if self._x is not None:
                self._x = None
                self._xarray_mesh = None
                self.Modified()
            return

        coords = self.available_coords
        if x_array_name not in coords:
            raise ValueError(
                f"x={x_array_name} is not a coordinate array [{', '.join(coords)}]"
            )
        if self._x != x_array_name:
            self._x = x_array_name
            self._xarray_mesh = None
            self.Modified()

    @property
    def x_size(self):
        if self._x is None:
            return 0
        return int(self._input[self._x].size)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y_array_name: str):
        if y_array_name is None:
            if self._y is not None:
                self._y = None
                self._xarray_mesh = None
                self.Modified()
            return

        coords = self.available_coords
        if y_array_name not in coords:
            raise ValueError(
                f"y={y_array_name} is not a coordinate array [{', '.join(coords)}]"
            )
        if self._y != y_array_name:
            self._y = y_array_name
            self._xarray_mesh = None
            self.Modified()

    @property
    def y_size(self):
        if self._y is None:
            return 0
        return int(self._input[self._y].size)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, z_array_name: str):
        if z_array_name is None:
            if self._z is not None:
                self._z = None
                self._xarray_mesh = None
                self.Modified()
            return

        coords = self.available_coords
        if z_array_name not in coords:
            raise ValueError(
                f"z={z_array_name} is not a coordinate array [{', '.join(coords)}]"
            )
        if self._z != z_array_name:
            self._z = z_array_name
            self._xarray_mesh = None
            self.Modified()

    @property
    def z_size(self):
        if self._z is None:
            return 0
        return int(self._input[self._z].size)

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, t_array_name: str):
        if t_array_name is None:
            if self._t is not None:
                self._t = None
                self._xarray_mesh = None
                self.Modified()
            return

        coords = self.available_coords
        if t_array_name not in coords:
            raise ValueError(
                f"t={t_array_name} is not a coordinate array [{', '.join(coords)}]"
            )
        if self._t != t_array_name:
            self._t = t_array_name
            self._xarray_mesh = None
            self.Modified()

    @property
    def slice_extents(self):
        return {
            coord_name: [0, self.input[coord_name].size - 1]
            for coord_name in [self.x, self.y, self.z]
            if coord_name is not None
        }

    def apply_coords(self):
        """Use array dims to map coordinates"""
        if self.input is None:
            return

        array_name = self.available_arrays[0]
        coords = self._input[array_name].dims

        # print("=" * 60)
        # for n in self.available_arrays:
        #     print(f"{n}: {self._input[n].dims}")
        # print("=" * 60)

        # reset coords arrays
        self.x = None
        self.y = None
        self.z = None
        self.t = None

        # assign mapping
        axes = ["t", "z", "y", "x"]
        if len(coords) == 4:
            for key, value in zip(axes, coords):
                setattr(self, key, value)
        elif len(coords) == 2:
            axes.remove("t")
            axes.remove("z")
            for key, value in zip(axes, coords):
                setattr(self, key, value)
        elif len(coords) == 3:
            # Is it 2D dataset with time or 3D dataset ?
            outer_dtype = self._input[array_name][coords[0]].dtype
            if is_time_type(outer_dtype):
                axes.remove("z")
                for key, value in zip(axes, coords):
                    setattr(self, key, value)
            else:
                axes.remove("t")
                for key, value in zip(axes, coords):
                    setattr(self, key, value)

    @property
    def available_coords(self):
        if self._input is None:
            return []

        return list(self._input.coords.keys())

    # -------------------------------------------------------------------------
    # Data sub-selection
    # -------------------------------------------------------------------------

    @property
    def t_index(self):
        return self._t_index

    @t_index.setter
    def t_index(self, t_index: int):
        if t_index != self._t_index:
            self._t_index = t_index
            self._xarray_mesh = None
            self.Modified()

    @property
    def t_size(self):
        if self._t is None:
            return 0
        return int(self._input[self._t].size)

    @property
    def t_labels(self):
        if self._t is None:
            return []

        t_array = self._input[self._t]
        t_type = t_array.dtype
        if np.issubdtype(t_type, np.datetime64):
            return get_time_labels(t_array.values)
        return [str(t) for t in t_array.values]

    @property
    def arrays(self):
        return list(self._array_names)

    @arrays.setter
    def arrays(self, array_names: List[str]):
        new_names = set(array_names or [])
        if new_names != self._array_names:
            self._array_names = new_names
            self._xarray_mesh = None
            self.Modified()

    @property
    def available_arrays(self):
        """List available data fields"""
        if self._input is None:
            return []

        filtered_arrays = []
        max_dim = 0
        coords = set([k for k, v in self._input.coords.items() if len(v.shape) == 1])
        for name in set(self._input.data_vars.keys()) - set(self._input.coords.keys()):
            if name.endswith("_bnds") or name.endswith("_bounds"):
                continue

            dims = set(self._input[name].dims)
            max_dim = max(max_dim, len(dims))
            if dims.issubset(coords):
                filtered_arrays.append(name)

        return [n for n in filtered_arrays if len(self._input[n].shape) == max_dim]

    @property
    def slices(self):
        result = dict(self._slices or {})
        if self.t is not None:
            result[self.t] = self.t_index
        return result

    @slices.setter
    def slices(self, v):
        if v != self._slices:
            self._slices = v
            self._xarray_mesh = None
            self.Modified()

    # -------------------------------------------------------------------------
    # properties
    # -------------------------------------------------------------------------

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, order: str):
        self._order = order
        self._xarray_mesh = None
        self.Modified()

    # -------------------------------------------------------------------------
    # add-on logic
    # -------------------------------------------------------------------------

    @property
    def computed(self):
        return self._computed

    @computed.setter
    def computed(self, v):
        if self._computed != v:
            self._computed = v or {}
            self._pipeline = None
            scalar_arrays = self._computed.get("_use_scalars", [])
            vector_arrays = self._computed.get("_use_vectors", [])

            for output_name, func in self._computed.items():
                if output_name[0] == "_":
                    continue
                filter = vtkArrayCalculator(
                    result_array_name=output_name,
                    function=func,
                )

                # register array dependencies
                for scalar_array in scalar_arrays:
                    filter.AddScalarArrayName(scalar_array)
                for vector_array in vector_arrays:
                    filter.AddVectorArrayName(vector_array)

                if self._pipeline is None:
                    self._pipeline = filter
                else:
                    self._pipeline = self._pipeline >> filter

            self.Modified()

    def load(self, data_info):
        if "data_origin" not in data_info:
            raise ValueError("Only state with data_origin can be loaded")

        from pan3d import catalogs

        self._data_origin = data_info["data_origin"]
        self.input = catalogs.load_dataset(
            self._data_origin["source"], self._data_origin["id"]
        )

        self.order = self._data_origin.get("order", "C")

        dataset_config = data_info.get("dataset_config")
        if dataset_config is None:
            self.apply_coords()
            self.arrays = self.available_arrays
        else:
            self.x = dataset_config.get("x")
            self.y = dataset_config.get("y")
            self.z = dataset_config.get("z")
            self.t = dataset_config.get("t")
            self.slices = dataset_config.get("slices")
            self.t_index = dataset_config.get("t_index", 0)
            self.apply_coords()
            self.arrays = dataset_config.get("arrays", self.available_arrays)

    @property
    def state(self):
        if self._data_origin is None:
            raise RuntimeError(
                "No state available without data origin. Need to use the load method to set the data origin."
            )

        return {
            "data_origin": self._data_origin,
            "dataset_config": {
                k: getattr(self, k)
                for k in ["x", "y", "z", "t", "slices", "t_index", "arrays"]
            },
        }

    # -------------------------------------------------------------------------
    # Algorithm
    # -------------------------------------------------------------------------

    def RequestData(self, request, inInfo, outInfo):
        # Use open data_array handle to fetch data at
        # desired Level of Detail
        try:
            pdo = self.GetOutputData(outInfo, 0)

            # Generate mesh
            if self._xarray_mesh is None:
                # grid
                mesh = vtkRectilinearGrid()
                mesh.x_coordinates = slice_array(
                    self._x, self._input, self.slices.get(self._x)
                )
                mesh.y_coordinates = slice_array(
                    self._y, self._input, self.slices.get(self._y)
                )
                mesh.z_coordinates = slice_array(
                    self._z, self._input, self.slices.get(self._z)
                )
                mesh.dimensions = [
                    mesh.x_coordinates.size,
                    mesh.y_coordinates.size,
                    mesh.z_coordinates.size,
                ]
                # fields
                indexing = to_isel(self.slices, self.x, self.y, self.z, self.t)
                for field_name in self._array_names:
                    da = self._input[field_name]
                    if indexing is not None:
                        da = da.isel(indexing)
                    mesh.point_data[field_name] = da.values.ravel(order=self._order)

                self._xarray_mesh = mesh

            # Compute derived quantity
            if self._pipeline is not None:
                pdo.ShallowCopy(self._pipeline(self._xarray_mesh))
            else:
                pdo.ShallowCopy(self._xarray_mesh)

        except Exception as e:
            traceback.print_exc()
            raise e
        return 1
