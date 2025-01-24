from typing import List, Optional

import xarray as xr
import numpy as np
import pandas as pd

from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.vtkCommonCore import vtkVariant
from vtkmodules.vtkCommonExecutionModel import vtkStreamingDemandDrivenPipeline
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkArrayCalculator
from vtkmodules.util import numpy_support

from pan3d.xarray.cf.coords.meta import MetaArrayMapping
from pan3d.xarray.cf.constants import Projection

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


class CFHelperXXX:
    def __init__(self, xr_dataset):
        self._xr_dataset = xr_dataset
        self._meta = MetaArrayMapping(xr_dataset)
        self._t_index = 0
        self._mesh = None
        self._array_names = []
        self._spherical = True

    def update(self, xr_dataset):
        self._array_names = []
        self._mesh = None
        self._xr_dataset = xr_dataset
        self._meta.update(xr_dataset)

    def _reset(self):
        self._mesh = None

    @property
    def x(self):
        return self._meta.longitude

    @property
    def y(self):
        return self._meta.latitude

    @property
    def z(self):
        return self._meta.vertical

    @property
    def t(self):
        return self._meta.time

    @property
    def spherical(self):
        return self._spherical

    @spherical.setter
    def spherical(self, v):
        if self._spherical != v:
            self._spherical = v
            self._reset()

    @property
    def vertical_bias(self):
        return self._meta.vertical_bias

    @vertical_bias.setter
    def vertical_bias(self, v):
        if self._meta.vertical_bias != v:
            self._meta.vertical_bias = v
            self._reset()

    @property
    def vertical_scale(self):
        return self._meta.vertical_scale

    @vertical_scale.setter
    def vertical_scale(self, v):
        if self._meta.vertical_scale != v:
            self._meta.vertical_scale = v
            self._reset()

    @property
    def t_index(self):
        """return the current selected time index"""
        return self._t_index

    @t_index.setter
    def t_index(self, t_index: int):
        """update the current selected time index"""
        if t_index != self._t_index:
            self._t_index = t_index
            self._reset()

    @property
    def t_size(self):
        """return the size of the coordinate used for the time"""
        if self.t is None or self._xr_dataset is None:
            return 0
        return int(self._xr_dataset[self.t].size)

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
            self._reset()

    @property
    def available_arrays(self):
        all_list = []
        for arrays in self._meta.data_arrays.values():
            if self._array_names:
                if self._array_names.intersection(arrays):
                    # only add compatible arrays
                    all_list.extend(arrays)
            else:
                # when no array selected, add all of them
                all_list.extend(arrays)

        return all_list

    @property
    def mesh(self):
        if self._mesh is None:
            self._mesh = self._meta.get_mesh(self._t_index, self.spherical, self.arrays)

        return self._mesh


class vtkXArrayCFSource(VTKPythonAlgorithmBase):
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
            outputType="vtkDataObject",
        )
        # Data source
        self._input = input
        self._pipeline = None
        self._computed = {}
        self._data_origin = None

        # Data sub-selection
        self._array_names = set(arrays or [])
        self._t_index = 0
        self._slices = None

        # vtk internal vars
        self._arrays = {}

        # projection
        self._proj_mode = Projection.SPHERICAL
        self._proj_vertical_bias = 6378137  # earth radius in meter
        self._proj_vertical_scale = (
            100  # increase z scaling to see something compare to earth radius
        )

        # Create reader if xarray available
        self._mapping = MetaArrayMapping(self._input)

    # -------------------------------------------------------------------------
    # Information
    # -------------------------------------------------------------------------

    def __str__(self):
        return f"VTK XArray CF (Python) reader\n{self._mapping}"

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
        self._slices = None
        self._array_names.clear()
        self._input = xarray_dataset
        self._mapping.update(self._input)
        self.t_index = 0
        self.Modified()

    # -------------------------------------------------------------------------
    # Array selectors
    # -------------------------------------------------------------------------

    @property
    def x(self):
        """return the name that is currently mapped to the X axis"""
        return self._mapping.longitude

    @property
    def x_size(self):
        """return the size of the coordinate used for the X axis"""
        if self.x is None:
            return 0
        return int(self._input[self.x].size)

    @property
    def y(self):
        """return the name that is currently mapped to the Y axis"""
        return self._mapping.latitude

    @property
    def y_size(self):
        """return the size of the coordinate used for the Y axis"""
        if self.y is None:
            return 0
        return int(self._input[self.y].size)

    @property
    def z(self):
        """return the name that is currently mapped to the Z axis"""
        return self._mapping.vertical

    @property
    def z_size(self):
        """return the size of the coordinate used for the Z axis"""
        if self.z is None:
            return 0
        return int(self._input[self.z].size)

    @property
    def t(self):
        """return the name that is currently mapped to the time axis"""
        return self._mapping.time

    @property
    def slice_extents(self):
        """return a dictionary for the X, Y, Z dimensions with the corresponding extent [0, size-1]"""
        # !!! can be different based on which field is selected !!!
        # -> result not obvious based on the mesh type
        return {
            coord_name: [0, self.input[coord_name].size - 1]
            for coord_name in [self.x, self.y, self.z]
            if coord_name is not None
        }

    @property
    def available_coords(self):
        """List available coordinates arrays that are 1D"""
        # !!! Do we use that ???
        if self._input is None:
            return []

        return [k for k, v in self._input.coords.items() if len(v.shape) == 1]

    # -------------------------------------------------------------------------
    # Projection management
    # -------------------------------------------------------------------------

    @property
    def projection(self):
        return self._proj_mode

    @projection.setter
    def projection(self, mode=None):
        if mode in Projection and self._proj_mode != mode:
            if isinstance(mode, str):
                mode = Projection(mode)
            self._proj_mode = mode
            self.Modified()

    @property
    def vertical_bias(self):
        return self._proj_vertical_bias

    @vertical_bias.setter
    def vertical_bias(self, v):
        if self._proj_vertical_bias != v:
            self._proj_vertical_bias = v
            self.Modified()

    @property
    def vertical_scale(self):
        return self._proj_vertical_scale

    @vertical_scale.setter
    def vertical_scale(self, v):
        if self._proj_vertical_scale != v:
            self._proj_vertical_scale = v
            self.Modified()

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
        if self.t is None:
            return 0
        return int(self._input[self.t].size)

    @property
    def t_labels(self):
        """return a list of string that match the various time values available"""
        if self.t is None:
            return []

        t_array = self._input[self.t]
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
        if self._input is None:
            return []

        all_list = []
        for arrays in self._mapping.data_arrays.values():
            if self._array_names:
                if self._array_names.intersection(arrays):
                    # only add compatible arrays
                    all_list.extend(arrays)
            else:
                # when no array selected, add all of them
                all_list.extend(arrays)

        return all_list

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
            if "time" in v:
                self.t_index = v.get("time", 0)

            self.Modified()

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

        dataset_config = data_info.get("dataset_config")
        if dataset_config is None:
            self.arrays = self.available_arrays
        else:
            self.slices = dataset_config.get("slices")
            self.t_index = dataset_config.get("t_index", 0)
            self.arrays = dataset_config.get("arrays", [self.available_arrays[0]])

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

    def RequestDataObject(self, request, inInfo, outInfo):
        output = self._mapping.get_vtk_mesh_type(self._proj_mode, self.arrays)
        outInfo.GetInformationObject(0).Set(vtkDataObject.DATA_OBJECT(), output)
        print(f"RequestDataObject::{output.GetClassName()=}")
        return 1

    def RequestInformation(self, request, inInfo, outInfo):
        whole_extent = self._mapping.get_vtk_whole_extent(self._proj_mode, self.arrays)
        print(f"{whole_extent=}")
        outInfo.GetInformationObject(0).Set(
            vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
            *whole_extent,
        )

        return 1

    def RequestData(self, request, inInfo, outInfo):
        """implementation of the vtk algorithm for generating the VTK mesh"""
        # Use open data_array handle to fetch data at
        # desired Level of Detail
        mesh = self._mapping.get_vtk_mesh(
            time_index=self.t_index, projection=self._proj_mode, fields=self.arrays
        )
        if mesh is not None:
            print(f"{mesh.extent=}")
            print(f"{mesh.GetClassName()=}")
            pdo = self.GetOutputData(outInfo, 0)

            # Compute derived quantity
            if self._pipeline is not None:
                mesh = self._pipeline(mesh)
                pdo.ShallowCopy(mesh)
            else:
                pdo.ShallowCopy(mesh)

        return 1
