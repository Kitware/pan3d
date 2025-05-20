import warnings
from pathlib import Path

import numpy as np
import xarray as xr
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkIOLegacy import vtkDataSetReader
from vtkmodules.vtkIOXML import (
    vtkXMLImageDataReader,
    vtkXMLRectilinearGridReader,
    vtkXMLStructuredGridReader,
)
from xarray.backends import BackendEntrypoint

from pan3d.xarray.errors import DataCopyWarning

READERS = {
    ".vti": vtkXMLImageDataReader,
    ".vtr": vtkXMLRectilinearGridReader,
    ".vts": vtkXMLStructuredGridReader,
    ".vtk": vtkDataSetReader,
}


def read(file_path):
    reader = READERS[Path(file_path).suffix](file_name=file_path)
    # reader.SetFileName(file_path)
    return reader()


def rectilinear_grid_to_dataset(mesh):
    dims = list(mesh.dimensions)
    dims = dims[-1:] + dims[:-1]
    return xr.Dataset(
        {
            name: (["z", "x", "y"], mesh.point_data[name].ravel().reshape(dims))
            for name in mesh.point_data.keys()
        },
        coords={
            "x": (["x"], mesh.x_coordinates),
            "y": (["y"], mesh.y_coordinates),
            "z": (["z"], mesh.z_coordinates),
        },
    )


def image_data_to_dataset(mesh):
    origin = mesh.origin
    spacing = mesh.spacing
    extent = mesh.extent

    def gen_coords(i):
        return np.array(
            [
                origin[i] + (spacing[i] * v)
                for v in range(extent[i * 2], extent[i * 2 + 1] + 1)
            ],
            dtype=np.double,
        )

    dims = list(mesh.dimensions)
    return xr.Dataset(
        {
            name: (["z", "x", "y"], mesh.point_data[name].ravel().reshape(dims))
            for name in mesh.point_data.keys()
        },
        coords={
            "x": (["x"], gen_coords(0)),
            "y": (["y"], gen_coords(1)),
            "z": (["z"], gen_coords(2)),
        },
    )


def structured_grid_to_dataset(mesh):
    warnings.warn(
        DataCopyWarning(
            "StructuredGrid dataset engine duplicates data - VTK data not shared with xarray."
        ),
        stacklevel=2,
    )
    dims = [0, 0, 0]
    mesh.GetDimensions(dims)
    return xr.Dataset(
        {
            name: (
                ["xi", "yi", "zi"],
                mesh.point_data[name].ravel().reshape(dims),
            )
            for name in mesh.point_data.keys()
        },
        coords={
            "x": (["xi", "yi", "zi"], mesh.x_coordinates),
            "y": (["xi", "yi", "zi"], mesh.y_coordinates),
            "z": (["xi", "yi", "zi"], mesh.z_coordinates),
        },
    )


DATASET_TO_XARRAY = {
    "vtkRectilinearGrid": rectilinear_grid_to_dataset,
    "vtkImageData": image_data_to_dataset,
    "vtkStructuredGrid": structured_grid_to_dataset,
}


def dataset_to_xarray(dataset):
    if isinstance(dataset, vtkDataObject):
        for ds_type, fn in DATASET_TO_XARRAY.items():
            if dataset.IsA(ds_type):
                return fn(dataset)

    msg = f"pan3d is unable to generate an xarray DataSet from the {type(dataset)} VTK data type at this time."
    raise TypeError(msg)


class VTKBackendEntrypoint(BackendEntrypoint):
    def open_dataset(
        self,
        filename_or_obj,
        *,
        drop_variables=None,
    ):
        return dataset_to_xarray(read(filename_or_obj))

    open_dataset_parameters = [
        "filename_or_obj",
        "attrs",
    ]

    def guess_can_open(self, filename_or_obj):
        try:
            return Path(filename_or_obj).suffix in READERS
        except TypeError:
            return False
