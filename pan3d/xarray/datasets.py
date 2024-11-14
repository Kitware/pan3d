from typing import Dict, Optional

import numpy as np
import warnings
from pan3d.xarray.errors import DataCopyWarning
from vtkmodules.vtkCommonDataModel import vtkRectilinearGrid, vtkStructuredGrid


def imagedata_to_rectilinear(image_data):
    output = vtkRectilinearGrid()
    output.SetDimensions(image_data.dimensions)
    origin = image_data.origin
    spacing = image_data.spacing
    extent = image_data.extent
    coords = []
    for axis in range(3):
        coords.append(
            np.array(
                [
                    origin[axis] + (spacing[axis] * i)
                    for i in range(extent[axis * 2], extent[axis * 2 + 1] + 1)
                ],
                dtype=np.double,
            )
        )

    output.x_coordinates, output.y_coordinates, output.z_coordinates = coords
    output.point_data.ShallowCopy(image_data.point_data)
    output.cell_data.ShallowCopy(image_data.cell_data)
    output.field_data.ShallowCopy(image_data.field_data)

    return output


def _coerce_shapes(*arrs):
    """Coerce all argument arrays to have the same shape."""
    maxi = 0
    ndim = 0
    for i, arr in enumerate(arrs):
        if arr is None:
            continue
        if arr.ndim > ndim:
            ndim = arr.ndim
            maxi = i
    # print(arrs)
    # if ndim != len(arrs) - (*arrs,).count(None):
    #     print(ndim, len(arrs))
    #     raise ValueError
    if ndim < 1:
        raise ValueError
    shape = arrs[maxi].shape
    reshaped = []
    for arr in arrs:
        if arr is not None and arr.shape != shape:
            if arr.ndim < ndim:
                arr = np.repeat([arr], shape[2 - maxi], axis=2 - maxi)
            else:
                raise ValueError
        reshaped.append(arr)
    return reshaped


def _points(
    accessor,
    x: Optional[str] = None,
    y: Optional[str] = None,
    z: Optional[str] = None,
    order: Optional[str] = "F",
    scales: Optional[Dict] = None,
):
    """Generate structured points as new array."""
    if order is None:
        order = "F"
    ndim = 3 - (x, y, z).count(None)
    if ndim < 2:
        if ndim == 1:
            raise ValueError(
                "One dimensional structured grids should be rectilinear grids."
            )
        raise ValueError("You must specify at least two dimensions as X, Y, or Z.")
    if x is not None:
        x = accessor._get_array(x, scale=(scales and scales.get(x)) or 1)
    if y is not None:
        y = accessor._get_array(y, scale=(scales and scales.get(y)) or 1)
    if z is not None:
        z = accessor._get_array(z, scale=(scales and scales.get(z)) or 1)
    arrs = _coerce_shapes(x, y, z)
    x, y, z = arrs
    arr = [a for a in arrs if a is not None][0]
    points = np.zeros((arr.size, 3), dtype=arr.dtype)
    if x is not None:
        points[:, 0] = x.ravel(order=order)
    if y is not None:
        points[:, 1] = y.ravel(order=order)
    if z is not None:
        points[:, 2] = z.ravel(order=order)
    shape = list(x.shape) + [1] * (3 - ndim)
    return points, shape


def rectilinear(
    accessor,
    x: Optional[str] = None,
    y: Optional[str] = None,
    z: Optional[str] = None,
    order: Optional[str] = "C",
    component: Optional[str] = None,
    scales: Optional[Dict] = None,
):
    if scales is None:
        scales = {}

    ndim = 3 - (x, y, z).count(None)
    if ndim < 1:
        raise ValueError("You must specify at least one dimension as X, Y, or Z.")

    # Build dataset
    dataset = vtkRectilinearGrid()

    if x is not None:
        dataset.x_coordinates = accessor._get_array(x, scale=scales.get(x, 1))
    if y is not None:
        dataset.y_coordinates = accessor._get_array(y, scale=scales.get(y, 1))
    if z is not None:
        dataset.z_coordinates = accessor._get_array(z, scale=scales.get(z, 1))

    # Update grid size
    dataset.dimensions = [
        dataset.x_coordinates.size,
        dataset.y_coordinates.size,
        dataset.z_coordinates.size,
    ]

    # Handle field
    values = accessor.data
    values_dim = values.ndim
    if component is not None:
        # if ndim < values.ndim and values.ndim == ndim + 1:
        # Assuming additional component array
        dims = set(accessor._xarray.dims)
        dims.discard(component)
        print("values changed - transpose")
        values = accessor._xarray.transpose(
            *dims, component, transpose_coords=True
        ).values
        values = values.reshape((-1, values.shape[-1]), order=order)
        warnings.warn(
            DataCopyWarning(
                "Made a copy of the multicomponent array - VTK data not shared with xarray."
            )
        )
        ndim += 1
    else:
        print("values changed - ravel")
        values = values.ravel(order=order)

    # Validate dimensions of field
    if values_dim != ndim:
        msg = f"Dimensional mismatch between specified X, Y, Z coords and dimensionality of DataArray ({ndim} vs {values_dim})"
        if ndim > values_dim:
            raise ValueError(
                f"{msg}. Too many coordinate dimensions specified leave out Y and/or Z."
            )
        raise ValueError(
            f"{msg}. Too few coordinate dimensions specified. Be sure to specify Y and/or Z or reduce the dimensionality of the DataArray by indexing along non-spatial coordinates like Time."
        )

    array_name = str(accessor._xarray.name or "data")
    dataset.point_data[array_name] = values
    return dataset


def structured(
    accessor,
    x: Optional[str] = None,
    y: Optional[str] = None,
    z: Optional[str] = None,
    order: Optional[str] = "F",
    component: Optional[str] = None,
    scales: Optional[Dict] = None,
):
    if scales is None:
        scales = {}

    points, shape = _points(accessor, x=x, y=y, z=z, order=order, scales=scales)

    dataset = vtkStructuredGrid()
    dataset.SetDimensions(shape)
    dataset.points = points
    dataset.point_data[accessor._xarray.name or "data"] = accessor.data.ravel(
        order=order
    )

    return dataset
