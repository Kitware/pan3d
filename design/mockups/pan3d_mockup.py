# print('importing pan3d_mockup.py')
import numpy as np
import vtk
import pyvista as pv
import xarray


def to_vtk(data_array, grid=None):
    """Hard-coded to return rectilinear grid from 3-D data array.

    Logic copied from Ryan's notebook
    """
    xg = data_array.indexes["XC_agg"].values
    yg = data_array.indexes["YC_agg"].values
    zg = data_array.indexes["Z"].values

    # manually extend arrays
    dxg = xg[-1] - xg[-2]
    xg = np.concatenate([xg, [xg[-1] + dxg]])

    dyg = yg[-1] - yg[-2]
    yg = np.concatenate([yg, [yg[-1] + dyg]])

    # dz = ds.drF.values
    dz = -2985  # more hard-coding
    zg = np.concatenate([zg, [dz]])

    aspect = 0.3e3
    offset = 4000

    if grid is None:
        grid = pv.RectilinearGrid(xg / aspect, yg / aspect + offset, zg)
    name = data_array.name
    grid.cell_data[name] = data_array.values.flatten()

    return grid


def plot(data_object, **kwargs):
    kwargs["notebook"] = True
    if isinstance(data_object, vtk.vtkDataObject):
        return pv.plot(data_object, **kwargs)

    elif isinstance(data_object, xarray.core.dataarray.DataArray):
        if data_object.ndim == 3:
            vtk_grid = to_vtk(data_object)
            return pv.plot(vtk_grid, **kwargs)
        elif data_object.ndim == 4:
            # Presume that time is the 4th dim
            return "TBD time varying"
        else:
            return "Unsupported: DataArray with ndim {}".format(data_object.ndim)

    else:
        return "Unsupported: data type {}".format(type(data_object))


class Plotter(pv.Plotter):
    def __init__(self, data_array, **kwargs):
        super(Plotter, self).__init__()
        self.initialized = False
        self.kwargs = kwargs  # pass to add_mesh() call
        self.data_array = data_array
        self.grid = None
        self.set_index(0)
        self.initialized = True

    def set_index(self, i):
        """Have to reconstruct the vtk grid each time. Wish I knew why."""
        if True:
            # if self.grid is None:
            # print('New grid', i)
            self.grid = to_vtk(self.data_array[i])
            self.add_mesh(self.grid, **self.kwargs)
        else:
            print("Same grid", i)
            to_vtk(self.data_array[i], self.grid)
            self.grid.Modified()
        if self.initialized:
            self.render()
