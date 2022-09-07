import vtk
import numpy as np
from vtkmodules.numpy_interface.dataset_adapter import numpyTovtkDataArray as np2da


class AbstractGridBuilder:
    def __init__(self, server, data_source, grid):
        self._server = server
        self._data_source = data_source
        self._grid = grid

        state = server.state
        state.grid_point_data = []
        state.grid_cell_data = []

        ctrl = server.controller
        ctrl.grid_add_point_data = self.add_point_data
        ctrl.grid_add_cell_data = self.add_cell_data
        ctrl.grid_remove_point_data = self.remove_point_data
        ctrl.grid_remove_cell_data = self.remove_cell_data
        ctrl.grid_clear_point_data = self.clear_point_data
        ctrl.grid_clear_cell_data = self.clear_cell_data
        ctrl.grid_reset = self.reset  # Can/could be overriden

    def add_point_data(self, array_path):
        array = self._data_source.get(array_path)
        name = array.name.split("/")[-1]
        vtk_array = np2da(np.ravel(array), name=name)
        self._grid.GetPointData().AddArray(vtk_array)
        self._server.state.grid_point_data.append(array_path)
        self._server.state.dirty("grid_point_data")

    def clear_point_data(self):
        pd = self._grid.GetPointData()
        while pd.GetNumberOfArrays():
            pd.RemoveArray(0)
        self._server.state.grid_point_data = []

    def clear_cell_data(self):
        cd = self._grid.GetCellData()
        while cd.GetNumberOfArrays():
            cd.RemoveArray(0)
        self._server.state.grid_cell_data = []

    def remove_point_data(self, array_path):
        name = array_path.split("/")[-1]
        self._grid.GetPointData().RemoveArray(name)
        self._server.state.grid_point_data.remove(array_path)
        self._server.state.dirty("grid_point_data")

    def add_cell_data(self, array_path):
        array = self._data_source.get(array_path)
        name = array.name.split("/")[-1]
        vtk_array = np2da(np.ravel(array), name=name)
        self._grid.GetCellData().AddArray(vtk_array)
        self._server.state.grid_cell_data.append(array_path)
        self._server.state.dirty("grid_cell_data")

    def remove_cell_data(self, array_path):
        name = array_path.split("/")[-1]
        self._grid.GetCellData().RemoveArray(name)
        self._server.state.grid_cell_data.remove(array_path)
        self._server.state.dirty("grid_cell_data")

    @property
    def grid(self):
        return self._grid

    def reset(self):
        fields = (
            self._grid.GetPointData(),
            self._grid.GetCellData(),
            self._grid.GetFieldData(),
        )
        for field in fields:
            while field.GetNumberOfArrays():
                field.RemoveArray(0)

        state = self._server.state
        state.grid_point_data = []
        state.grid_cell_data = []


class RectilinearBuilder(AbstractGridBuilder):
    def __init__(self, server, data_source):
        super().__init__(server, data_source, vtk.vtkRectilinearGrid())

        state = server.state
        state.grid_x_array = None
        state.grid_y_array = None
        state.grid_z_array = None
        self._update_dims()

        ctrl = server.controller
        ctrl.grid_bind_x = self.bind_x
        ctrl.grid_bind_y = self.bind_y
        ctrl.grid_bind_z = self.bind_z
        ctrl.grid_reset = self.reset

    def reset(self):
        super().reset()
        state = self._server.state
        state.grid_x_array = None
        state.grid_y_array = None
        state.grid_z_array = None

    def bind_x(self, array_path, add_col=False):
        self._server.state.grid_x_array = array_path
        array = self._data_source.get(array_path)

        if add_col:
            x_array = vtk.vtkDoubleArray()
            x_array.SetName("x")
            x_array.SetNumberOfTuples(array.size + 1)
            dx = array[-1] - array[-2]
            for i in range(array.size):
                x_array.SetTuple1(i, array[i])
            x_array.SetTuple1(array.size, array[array.size - 1] + dx)
            self._grid.SetXCoordinates(x_array)
        else:
            vtk_array = np2da(array, name="x")
            self._grid.SetXCoordinates(vtk_array)

        self.clear_point_data()
        self.clear_cell_data()
        self._update_dims()

    def bind_y(self, array_path, add_col=False):
        self._server.state.grid_y_array = array_path
        array = self._data_source.get(array_path)

        if add_col:
            y_array = vtk.vtkDoubleArray()
            y_array.SetName("y")
            y_array.SetNumberOfTuples(array.size + 1)
            dy = array[-1] - array[-2]
            for i in range(array.size):
                y_array.SetTuple1(i, array[i])
            y_array.SetTuple1(array.size, array[array.size - 1] + dy)
            self._grid.SetYCoordinates(y_array)
        else:
            vtk_array = np2da(array, name="x")
            self._grid.SetYCoordinates(vtk_array)

        self.clear_point_data()
        self.clear_cell_data()
        self._update_dims()

    def bind_z(self, array_path, add_col=False):
        self._server.state.grid_z_array = array_path
        array = self._data_source.get(array_path)

        if add_col:
            z_array = vtk.vtkDoubleArray()
            z_array.SetName("z")
            z_array.SetNumberOfTuples(array.size + 1)
            dz = array[-1] - array[-2]
            for i in range(array.size):
                z_array.SetTuple1(i, array[i])
            z_array.SetTuple1(array.size, array[array.size - 1] + dz)
            self._grid.SetZCoordinates(z_array)
        else:
            vtk_array = np2da(array, name="x")
            self._grid.SetZCoordinates(vtk_array)

        self.clear_point_data()
        self.clear_cell_data()
        self._update_dims()

    @property
    def point_dimensions(self):
        x = self._grid.GetXCoordinates()
        y = self._grid.GetYCoordinates()
        z = self._grid.GetZCoordinates()

        return (
            z.GetNumberOfValues() if z else 0,
            y.GetNumberOfValues() if y else 0,
            x.GetNumberOfValues() if x else 0,
        )

    @property
    def cell_dimensions(self):
        nz, ny, nx = self.point_dimensions

        return (
            nz - 1,
            ny - 1,
            nx - 1,
        )

    def _update_dims(self):
        state = self._server.state
        z, y, x = self.point_dimensions
        state.grid_dimensions = (x, y, z)
        state.grid_point_dimensions = (z, y, x)
        state.grid_cell_dimensions = self.cell_dimensions
        self.grid.SetDimensions(x, y, z)


class ImageDataBuilder(AbstractGridBuilder):
    def __init__(self, server, data_source):
        super().__init__(server, data_source, vtk.vtkImageData())
        self._dimensions = [10, 10, 10]
        self._spacing = [1, 1, 1]
        self._origin = [0, 0, 0]

        state, ctrl = server.state, server.controller
        state.grid_dimensions = self._dimensions
        state.grid_spacing = self._spacing
        state.grid_origin = self._origin

        ctrl.grid_set_dimensions = self.set_dimensions
        ctrl.grid_set_spacing = self.set_spacing
        ctrl.grid_set_origin = self.set_origin

        state.change("grid_dimensions")(ctrl.grid_set_dimensions)
        state.change("grid_spacing")(ctrl.grid_set_spacing)
        state.change("grid_origin")(ctrl.grid_set_origin)

    def __del__(self):
        print("Delete ImageDataBuilder")
        ctrl = self._server.controller
        ctrl.grid_set_dimensions.clear()
        ctrl.grid_set_spacing.clear()
        ctrl.grid_set_origin.clear()

    def set_dimensions(self, grid_dimensions, **kwargs):
        self._dimensions = [
            int(grid_dimensions[0]),
            int(grid_dimensions[1]),
            int(grid_dimensions[2]),
        ]
        self.grid.SetDimensions(self._dimensions)

        self._server.state.grid_point_dimensions = self.point_dimensions
        self._server.state.grid_cell_dimensions = self.cell_dimensions
        self.clear_point_data()
        self.clear_cell_data()

    def set_spacing(self, grid_spacing, **kwargs):
        self._spacing = [
            float(grid_spacing[0]),
            float(grid_spacing[1]),
            float(grid_spacing[2]),
        ]
        self.grid.SetSpacing(self._spacing)

    def set_origin(self, grid_origin, **kwargs):
        self._origin = [
            float(grid_origin[0]),
            float(grid_origin[1]),
            float(grid_origin[2]),
        ]
        self.grid.SetOrigin(self._origin)

    @property
    def point_dimensions(self):
        return (
            self._dimensions[2],
            self._dimensions[1],
            self._dimensions[0],
        )

    @property
    def cell_dimensions(self):
        return (
            self._dimensions[2] - 1,
            self._dimensions[1] - 1,
            self._dimensions[0] - 1,
        )


MESH_TYPES = {
    "vtkRectilinearGrid": RectilinearBuilder,
    "vtkImageData": ImageDataBuilder,
}
