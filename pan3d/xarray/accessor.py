from typing import Dict, List, Optional

import numpy as np
import xarray as xr

from vtkmodules.vtkCommonDataModel import vtkDataSet
from pan3d.xarray import datasets, algorithm


class _LocIndexer:
    def __init__(self, parent: "VTKAccessor"):
        self.parent = parent

    def __getitem__(self, key) -> xr.DataArray:
        return self.parent._xarray.loc[key]

    def __setitem__(self, key, value) -> None:
        self.parent._xarray.__setitem__(self, key, value)


@xr.register_dataarray_accessor("vtk")
class VTKAccessor:
    def __init__(self, xarray_obj: xr.DataArray):
        self._xarray = xarray_obj

    def __getitem__(self, key):
        return self._xarray.__getitem__(key)

    @property
    def data(self):
        return self._xarray.values

    @property
    def loc(self) -> _LocIndexer:
        """Attribute for location based indexing like pandas."""
        return _LocIndexer(self)

    def _get_array(self, key, scale=1):
        try:
            values = self._xarray[key].values
            if "float" not in str(values.dtype) and "int" not in str(values.dtype):
                # non-numeric coordinate, assign array of scaled indices
                values = np.array(range(len(values))) * scale

            return values
        except KeyError:
            raise KeyError(
                f"Key {key} not present in DataArray. Choices are: {list(self._xarray.coords.keys())}"
            )

    def dataset(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        z: Optional[str] = None,
        order: Optional[str] = None,
        component: Optional[str] = None,
        mesh_type: Optional[str] = None,
        scales: Optional[Dict] = None,
    ) -> vtkDataSet:
        if mesh_type is None:  # Try to guess mesh type
            max_ndim = max(
                *[self._get_array(n).ndim for n in (x, y, z) if n is not None]
            )
            mesh_type = "structured" if max_ndim > 1 else "rectilinear"

        try:
            builder = getattr(datasets, mesh_type)
        except KeyError:
            raise KeyError
        return builder(
            self, x=x, y=y, z=z, order=order, component=component, scales=scales
        )

    def algorithm(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        z: Optional[str] = None,
        t: Optional[str] = None,
        arrays: Optional[List[str]] = None,
        order: str = "C",
    ):
        return algorithm.vtkXArrayRectilinearSource(
            input=self._xarray,
            x=x,
            y=y,
            z=z,
            t=t,
            arrays=arrays,
            order=order,
        )
