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


@xr.register_dataset_accessor("pan3d")
class Pan3DAccessor:
    accessor_id = 0

    @classmethod
    def next_id(cls):
        cls.accessor_id += 1
        return f"pan3d_accessor_{cls.accessor_id}"

    def __init__(self, xarray):
        self.xarray = xarray
        self.accessor_id = 0
        self._viewer_preview = None
        self._viewer_slicer = None
        self._viewer_globe = None

    @property
    def preview(self):
        from pan3d.viewers.preview import XArrayViewer

        if self._viewer_preview is None:
            self._viewer_preview = XArrayViewer(
                xarray=self.xarray, server=self.next_id()
            )

        return self._viewer_preview

    @property
    def slicer(self):
        from pan3d.explorers.slicer import XArraySlicer

        if self._viewer_slicer is None:
            self._viewer_slicer = XArraySlicer(
                xarray=self.xarray, server=self.next_id()
            )

        return self._viewer_slicer

    @property
    def globe(self):
        from pan3d.explorers.globe import GlobeViewer

        if self._viewer_globe is None:
            self._viewer_globe = GlobeViewer(xarray=self.xarray, server=self.next_id())

        return self._viewer_globe


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
