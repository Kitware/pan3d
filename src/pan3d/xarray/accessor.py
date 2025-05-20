from typing import Optional

import numpy as np
import xarray as xr
from vtkmodules.vtkCommonDataModel import vtkDataSet

from pan3d.xarray import algorithm, datasets


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
        self._local_rendering = None
        self._viewer_preview = None
        self._viewer_slicer = None
        self._viewer_globe = None
        self._viewer_contour = None

    @property
    def local(self):
        """Builder pattern for viewer creation using local rendering"""
        self._local_rendering = "wasm"
        return self

    @property
    def remote(self):
        """Builder pattern for viewer creation using remote rendering"""
        self._local_rendering = None
        return self

    @property
    def preview(self):
        from pan3d.viewers.preview import XArrayViewer

        if self._viewer_preview is None:
            self._viewer_preview = XArrayViewer(
                xarray=self.xarray,
                server=self.next_id(),
                local_rendering=self._local_rendering,
            )

        return self._viewer_preview

    @property
    def slicer(self):
        from pan3d.explorers.slicer import SliceExplorer

        if self._viewer_slicer is None:
            self._viewer_slicer = SliceExplorer(
                xarray=self.xarray,
                server=self.next_id(),
                local_rendering=self._local_rendering,
            )

        return self._viewer_slicer

    @property
    def globe(self):
        from pan3d.explorers.globe import GlobeExplorer

        if self._viewer_globe is None:
            self._viewer_globe = GlobeExplorer(
                xarray=self.xarray,
                server=self.next_id(),
                local_rendering=self._local_rendering,
            )

        return self._viewer_globe

    @property
    def contour(self):
        from pan3d.explorers.contour import ContourExplorer

        if self._viewer_contour is None:
            self._viewer_contour = ContourExplorer(
                xarray=self.xarray,
                server=self.next_id(),
                local_rendering=self._local_rendering,
            )

        return self._viewer_contour


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
        except KeyError as err:
            msg = f"Key {key} not present in DataArray. Choices are: {list(self._xarray.coords.keys())}"
            raise KeyError(msg) from err

    def dataset(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        z: Optional[str] = None,
        order: Optional[str] = None,
        component: Optional[str] = None,
        mesh_type: Optional[str] = None,
        scales: Optional[dict] = None,
    ) -> vtkDataSet:
        if mesh_type is None:  # Try to guess mesh type
            max_ndim = max(
                *[self._get_array(n).ndim for n in (x, y, z) if n is not None]
            )
            mesh_type = "structured" if max_ndim > 1 else "rectilinear"

        try:
            builder = getattr(datasets, mesh_type)
        except KeyError as err:
            raise KeyError() from err
        return builder(
            self, x=x, y=y, z=z, order=order, component=component, scales=scales
        )

    def algorithm(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        z: Optional[str] = None,
        t: Optional[str] = None,
        arrays: Optional[list[str]] = None,
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
