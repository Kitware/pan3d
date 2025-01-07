from typing import List, Optional

import xarray as xr
import numpy as np
import pandas as pd
import traceback

from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkCommonCore import vtkVariant
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersCore import vtkArrayCalculator
from vtkmodules.util import numpy_support, xarray_support

VTK_DATASETS = {"vtkImageData": vtkImageData}

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def is_time_array(xarray, name, values):
    if values.dtype.type == np.datetime64 or values.dtype.type == np.timedelta64:
        un = np.datetime_data(values.dtype)
        # unit = ns and 1 base unit in a spep
        if un[0] == "ns" and un[1] == 1 and name in xarray.coords.keys():
            return True
    return False


# -----------------------------------------------------------------------------


def attr_value_to_vtk(value):
    if np.issubdtype(type(value), np.integer):
        return vtkVariant(int(value))

    if np.issubdtype(type(value), np.floating):
        return vtkVariant(float(value))

    if isinstance(value, np.ndarray):
        return vtkVariant(numpy_support.numpy_to_vtk(value))

    return vtkVariant(value)


# -----------------------------------------------------------------------------


def get_time_labels(times):
    return [pd.to_datetime(time).strftime("%Y-%m-%d %H:%M:%S") for time in times]


# -----------------------------------------------------------------------------
# VTK Algorithms
# -----------------------------------------------------------------------------


class vtkXArraySource(VTKPythonAlgorithmBase):
    """vtk source for converting XArray into a VTK mesh"""

    def __init__(
        self,
        input: Optional[xr.Dataset] = None,
        arrays: Optional[List[str]] = None,
    ):
        """
        Create vtkXArraySource

        Parameters:
            input (xr.Dataset): Provide an XArray to use as input. The load() method will replace it.
            arrays (list[str]): List of field to load onto the generated VTK mesh.
        """
        VTKPythonAlgorithmBase.__init__(
            self,
            nInputPorts=0,
            nOutputPorts=1,
        )
        # Data source
        self._input = input
        self._pipeline = None
        self._computed = {}
        self._data_origin = None

        # Array name selectors
        self._x = None
        self._y = None
        self._z = None
        self._t = None

        # Data sub-selection
        self._array_names = set(arrays or [])
        self._t_index = 0
        self._slices = None

        # vtk internal vars
        self._arrays = {}
        self._accessor = None
        self._reader = None

        # Create reader if xarray available
        if self._input:
            self._build_reader()

    # -------------------------------------------------------------------------
    # Reader Setup
    # -------------------------------------------------------------------------

    def _build_reader(self):
        # reset
        self._array_names.clear()
        self._arrays = {}  # to prevent garbage collection
        self._x = None
        self._y = None
        self._z = None
        self._t = None

        # vtk reader
        self._accessor = xarray_support.vtkXArrayAccessor()
        self._reader = xarray_support.vtkNetCDFCFReader(accessor=self._accessor)

        # XArray binding
        xarray = self._input
        accessor = self._accessor
        reader = self._reader
        time_names = []

        # map dimensions
        dim_keys = list(xarray.sizes.keys())
        dim_values = [xarray.sizes[k] for k in dim_keys]
        dim_name_to_index = {k: i for i, k in enumerate(dim_keys)}

        accessor.SetDim(dim_keys)
        accessor.SetDimLen(dim_values)

        # map variables
        var_keys = [*xarray.data_vars.keys(), *xarray.coords.keys()]
        var_is_coord = [0] * len(xarray.data_vars) + [1] * len(xarray.coords)
        var_name_to_index = {k: i for i, k in enumerate(var_keys)}

        accessor.SetVar(var_keys, var_is_coord)
        for i, k in enumerate(var_keys):
            # need contiguous array (noop if true, otherwise copy)
            v_data = np.ascontiguousarray(xarray[k].values)

            # Capture time array names
            if is_time_array(xarray, k, v_data):
                time_names.append(k)

            # Convert time data
            if v_data.dtype.char == "O":
                # object array, assume cftime (copy as double array)
                v_data = xarray_support.ndarray_cftime_toordinal(v_data).astype(
                    np.float64
                )
                time_names.append(k)

            # save array
            self._arrays[k] = v_data

            # register data to accessor
            accessor.SetVarValue(i, v_data)
            accessor.SetVarType(i, xarray_support.get_nc_type(v_data.dtype))
            accessor.SetVarDims(i, [dim_name_to_index[name] for name in xarray[k].dims])
            accessor.SetVarCoords(
                i, [var_name_to_index[name] for name in xarray[k].coords]
            )

            # handle attributes
            for attr_k, attr_v in xarray[k].attrs.items():
                accessor.SetAtt(i, attr_k, attr_value_to_vtk(attr_v))

        # map time array name to reader
        if len(time_names) >= 1:
            for name in time_names:
                if accessor.IsCOARDSCoordinate(name):
                    reader.SetTimeDimensionName(name)
                    self._t = name
                    break

        # Extract coordinate mapping
        reader.UpdateInformation()
        vtk_str_array = reader.GetAllDimensions()
        coords = []
        coords_names = ["_x", "_y", "_z"]
        if vtk_str_array.GetNumberOfValues() == 1 and ", " in vtk_str_array.GetValue(0):
            print("vtk reader.GetAllDimensions() is not properly working...")
            coords = vtk_str_array.GetValue(0)[1:-1].split(", ")
        else:
            for i in range(vtk_str_array.GetNumberOfValues()):
                coords.append(vtk_str_array.GetValue(i))
        while len(coords):
            coord_name = coords.pop()  # (Z, Y, X)
            attr_name = coords_names.pop(0)  # (X, Y, Z)
            setattr(self, attr_name, coord_name)

    # -------------------------------------------------------------------------
    # Information
    # -------------------------------------------------------------------------

    def __str__(self):
        return """VTK NetCDF/XArray reader"""

    # -------------------------------------------------------------------------
    # Data input
    # -------------------------------------------------------------------------

    @property
    def input(self):
        """return current input XArray"""
        return self._input

    @input.setter
    def input(self, xarray_dataset: xr.Dataset):
        """update input with a new XArray"""
        self._input = xarray_dataset
        self._build_reader()
        self.Modified()

    # -------------------------------------------------------------------------
    # Array selectors
    # -------------------------------------------------------------------------

    @property
    def x(self):
        """return the name that is currently mapped to the X axis"""
        return self._x

    @property
    def x_size(self):
        """return the size of the coordinate used for the X axis"""
        if self._x is None:
            return 0
        return int(self._input[self._x].size)

    @property
    def y(self):
        """return the name that is currently mapped to the Y axis"""
        return self._y

    @property
    def y_size(self):
        """return the size of the coordinate used for the Y axis"""
        if self._y is None:
            return 0
        return int(self._input[self._y].size)

    @property
    def z(self):
        """return the name that is currently mapped to the Z axis"""
        return self._z

    @property
    def z_size(self):
        """return the size of the coordinate used for the Z axis"""
        if self._z is None:
            return 0
        return int(self._input[self._z].size)

    @property
    def t(self):
        """return the name that is currently mapped to the time axis"""
        return self._t

    @property
    def slice_extents(self):
        """return a dictionary for the X, Y, Z dimensions with the corresponding extent [0, size-1]"""
        return {
            coord_name: [0, self.input[coord_name].size - 1]
            for coord_name in [self.x, self.y, self.z]
            if coord_name is not None
        }

    @property
    def available_coords(self):
        """List available coordinates arrays that have are 1D"""
        if self._input is None:
            return []

        return [k for k, v in self._input.coords.items() if len(v.shape) == 1]

    # -------------------------------------------------------------------------
    # Data sub-selection
    # -------------------------------------------------------------------------

    @property
    def t_index(self):
        """return the current selected time index"""
        return self._t_index

    @t_index.setter
    def t_index(self, t_index: int):
        """update the current selected time index"""
        if t_index != self._t_index:
            self._t_index = t_index
            self.Modified()

    @property
    def t_size(self):
        """return the size of the coordinate used for the time"""
        if self._t is None:
            return 0
        return int(self._input[self._t].size)

    @property
    def t_labels(self):
        """return a list of string that match the various time values available"""
        if self._t is None:
            return []

        t_array = self._input[self._t]
        t_type = t_array.dtype
        if np.issubdtype(t_type, np.datetime64):
            return get_time_labels(t_array.values)
        return [str(t) for t in t_array.values]

    @property
    def arrays(self):
        """return the list of arrays that are currently selected to be added to the generated VTK mesh"""
        return list(self._array_names)

    @arrays.setter
    def arrays(self, array_names: List[str]):
        """update the list of arrays to load on the generated VTK mesh"""
        new_names = set(array_names or [])
        if new_names != self._array_names:
            self._array_names = new_names
            self.Modified()

    @property
    def available_arrays(self):
        """List all available data fields for the `arrays` option"""
        if self._input is None or self._reader is None:
            return []

        vtk_str_array = self._reader.GetAllVariableArrayNames()
        return [
            vtk_str_array.GetValue(i) for i in range(vtk_str_array.GetNumberOfValues())
        ]

    @property
    def slices(self):
        """return the current slicing information which include axes crop/cut and time selection"""
        result = dict(self._slices or {})
        if self.t is not None:
            result[self.t] = self.t_index
        return result

    @slices.setter
    def slices(self, v):
        """update the slicing of the data along axes"""
        if v != self._slices:
            self._slices = v
            # FIXME !!! update accessor
            # Ask Dan
            # self.Modified()
            # raise NotImplementedError()
            print("set slices not implemented", v)
            if "time" in v:
                self.t_index = v.get("time", 0)

    # -------------------------------------------------------------------------
    # add-on logic
    # -------------------------------------------------------------------------

    @property
    def computed(self):
        """return the current description of the computed/derived fields on the VTK mesh"""
        return self._computed

    @computed.setter
    def computed(self, v):
        """
        update the computed/derived fields to add on the VTK mesh

        The layout of the dictionary provided should be as follow:
          - key: name of the field to be added
          - value: formula to apply for the given field name. The syntax is captured in the document (https://docs.paraview.org/en/latest/UsersGuide/filteringData.html#calculator)

        Then additional keys need to be provided to describe your formula dependencies:
        `_use_scalars` and `_use_vectors` which should be a list of string matching the name of the fields you are using in your expression.


        Please find below an example:

        ```
            {
                "_use_scalars": ["u", "v"],       # (u,v) needed for "vec" and "m2"
                "vec": "(u * iHat) + (v * jHat)", # 2D vector
                "m2": "u*u + v*v",
            }
        ```
        """
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
        """
        create a new XArray input with the `data_origin` and `dataset_config` information.

        Here is an example of the layout of the parameter

        ```
        {
          "data_origin": {
            "source": "url", # one of [file, url, xarray, pangeo, esgf]
            "id": "https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/noaa-coastwatch-geopolar-sst-feedstock/noaa-coastwatch-geopolar-sst.zarr",
            "order": "C"     # (optional) order to use in numpy
          },
          "dataset_config": {
            "x": "lon",      # (optional) coord name for X
            "y": "lat",      # (optional) coord name for Y
            "z": null,       # (optional) coord name for Z
            "t": "time",     # (optional) coord name for time
            "slices": {      # (optional) array slicing
              "lon": [
                1000,
                6000,
                20
              ],
              "lat": [
                500,
                3000,
                20
              ],
              "time": 5
            },
            "t_index": 5,    # (optional) selected time index
            "arrays": [      # (optional) names of arrays to load onto VTK mesh.
              "analysed_sst" #            If missing no array will be loaded
            ]                #            onto the mesh.
          }
        }
        ```
        """
        if "data_origin" not in data_info:
            raise ValueError("Only state with data_origin can be loaded")

        from pan3d import catalogs

        self._data_origin = data_info["data_origin"]
        self.input = catalogs.load_dataset(
            self._data_origin["source"], self._data_origin["id"]
        )
        self._build_reader()

        dataset_config = data_info.get("dataset_config")
        if dataset_config is None:
            self.arrays = self.available_arrays
        else:
            # self.slices = dataset_config.get("slices") # FIXME: not implemented yet
            self.t_index = dataset_config.get("t_index", 0)
            self.arrays = dataset_config.get("arrays", self.available_arrays)

    @property
    def state(self):
        """return current state that can be reused in a load() later on"""
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
        """implementation of the vtk algorithm for generating the VTK mesh"""
        # Use open data_array handle to fetch data at
        # desired Level of Detail
        if self._reader is None:
            return 0

        try:
            output = None

            if self.t_size:
                t = self._arrays[self.t][self.t_index]
                self._reader.UpdateTimeStep(t)
                # print("Update VTK time", t)

            # update arrays
            for name in self.available_arrays:
                active = 1 if name in self._array_names else 0
                self._reader.SetVariableArrayStatus(name, active)

            # generate the mesh
            mesh = self._reader()

            # Compute derived quantity
            if self._pipeline is not None:
                output = self._pipeline(mesh)
            else:
                output = mesh

            # set it as output
            print("output => ", output.GetClassName())
            filter_output = VTK_DATASETS[output.GetClassName()].GetData(outInfo)
            print(f"{filter_output=}")  # <= it is None...
            filter_output.ShallowCopy(output)

        except Exception as e:
            traceback.print_exc()
            raise e
        return 1
