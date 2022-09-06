import json
import vtk
import zarr
import logging
import numpy as np
from . import module

from vtkmodules.numpy_interface.dataset_adapter import numpyTovtkDataArray as np2da

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HierarchyBuilder:
    def __init__(self):
        self.hierarchy = {"/": {"id": "/", "children": []}}

    def create_node_zarr(self, name, obj):
        # print(name, obj)
        new_node = {"id": name, "name": name.split("/")[-1], "children": []}

        if isinstance(obj, zarr.core.Array):
            new_node["dimensions"] = obj.shape
            new_node["type"] = f"{obj.dtype}"

        parent_id = "/".join(name.split("/")[:-1])
        if len(parent_id) == 0:
            parent_id = "/"
        if parent_id in self.hierarchy:
            self.hierarchy[parent_id]["children"].append(new_node)
        self.hierarchy[name] = new_node

    @property
    def root(self):
        return self.hierarchy["/"]

    @property
    def children(self):
        return self.root["children"]


class ZarrDataSource:
    def __init__(self, source):
        self._zarr = source
        self._hierarchy = HierarchyBuilder()
        if isinstance(source, str):
            self._zarr = zarr.open(source, mode="r")

        self._zarr.visititems(self._hierarchy.create_node_zarr)

    @property
    def tree(self):
        return self._hierarchy.children

    def get(self, path):
        # print("get", path)
        if not path or path not in self._zarr:
            # print(" => none (0)")
            return None

        entry = self._zarr[path]
        if isinstance(entry, zarr.core.Array):
            # print(" => array", entry)
            return entry

        # print(" => none (1)")
        return None


class RectilinearBuilder:
    def __init__(self, server, data_source):
        self._server = server
        self._data_source = data_source
        self._grid = vtk.vtkRectilinearGrid()

        state = server.state
        state.grid_x_array = None
        state.grid_y_array = None
        state.grid_z_array = None
        state.grid_point_data = []
        state.grid_cell_data = []
        self.update_state()

        ctrl = server.controller
        ctrl.grid_bind_x = self.bind_x
        ctrl.grid_bind_y = self.bind_y
        ctrl.grid_bind_z = self.bind_z
        ctrl.grid_add_point_data = self.add_point_data
        ctrl.grid_add_cell_data = self.add_cell_data
        ctrl.grid_remove_point_data = self.remove_point_data
        ctrl.grid_remove_cell_data = self.remove_cell_data
        ctrl.grid_clear_point_data = self.clear_point_data
        ctrl.grid_clear_cell_data = self.clear_cell_data
        ctrl.grid_reset = self.reset

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
        state.grid_x_array = None
        state.grid_y_array = None
        state.grid_z_array = None
        state.grid_point_data = []
        state.grid_cell_data = []

    def bind_x(self, array_path, add_col=False):
        self._server.state.grid_x_array = array_path
        array = self._data_source.get(array_path)
        vtk_array = np2da(array, name="x")
        self._grid.SetXCoordinates(vtk_array)
        self.update_state()

    def bind_y(self, array_path, add_col=False):
        self._server.state.grid_y_array = array_path
        array = self._data_source.get(array_path)
        vtk_array = np2da(array, name="x")
        self._grid.SetYCoordinates(vtk_array)
        self.update_state()

    def bind_z(self, array_path, add_col=False):
        self._server.state.grid_z_array = array_path
        array = self._data_source.get(array_path)
        vtk_array = np2da(array, name="x")
        self._grid.SetZCoordinates(vtk_array)
        self.update_state()

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

    def update_state(self):
        state = self._server.state
        z, y, x = self.point_dimensions
        state.grid_point_dimensions = (z, y, x)
        state.grid_cell_dimensions = self.cell_dimensions
        self.grid.SetDimensions(x, y, z)

    @property
    def grid(self):
        return self._grid


MESH_TYPES = {
    "vtkRectilinearGrid": RectilinearBuilder,
}


class MeshBuilder:
    def __init__(self, server, data_source):
        self._server = server
        self._state = server.state
        self._ctrl = server.controller

        self._data_source = data_source
        self._mesh_type = "vtkRectilinearGrid"
        self._grid_editor = None

        # State variables
        self._state.array_active = None
        self._state.array_info = None
        self._state.array_actions = []

        # Listen to changes
        self._state.change("grid_type")(self.on_mesh_type)
        self._state.change("array_active")(self.on_active_array)

    def on_mesh_type(self, grid_type, **kwargs):
        self._grid_editor = MESH_TYPES[grid_type](self._server, self._data_source)
        self._ctrl.grid_update(self._grid_editor.grid)

    def on_active_array(self, array_active, **kwargs):
        self._active_array = self._data_source.get(array_active)
        self._state.array_info = None
        self._state.array_actions = []
        if self._active_array is not None:
            dims = list(self._active_array.shape)
            self._state.array_info = {
                "dimensions": dims,
                "type": f"{self._active_array.dtype}",
                "name": self._active_array.name,
            }
            if len(dims) == 4:
                self._state.array_actions.append("field(time) add to points")
                self._state.array_actions.append("field(time) add to cells")
            if len(dims) == 3:
                self._state.array_actions.append("field add to points")
                self._state.array_actions.append("field add to cells")
            if len(dims) == 1:
                self._state.array_actions.append("Use for points along X")
                self._state.array_actions.append("Use for cells size along X")
                self._state.array_actions.append("Use for points along Y")
                self._state.array_actions.append("Use for cells size along Y")
                self._state.array_actions.append("Use for points along Z")
                self._state.array_actions.append("Use for cells size along Z")
                self._state.array_actions.append("Use for time")


class MeshViewer:
    def __init__(self, server, mesh):
        state, ctrl = server.state, server.controller
        server.enable_module(module)

        # VTK
        self._vtk_grid = vtk.vtkImageData()
        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_render_window = vtk.vtkRenderWindow()
        self._vtk_render_window.AddRenderer(self._vtk_renderer)
        self._vtk_render_window_interactor = vtk.vtkRenderWindowInteractor()
        self._vtk_render_window_interactor.SetRenderWindow(self._vtk_render_window)
        self._vtk_render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        self._vtk_mapper = vtk.vtkDataSetMapper()
        self._vtk_actor = vtk.vtkActor()
        self._vtk_mapper.SetInputData(self._vtk_grid)
        self._vtk_actor.SetMapper(self._vtk_mapper)
        self._vtk_renderer.AddActor(self._vtk_actor)
        self._vtk_renderer.ResetCamera()

        # to fix
        self._vtk_grid.SetDimensions(10, 10, 10)
        self._vtk_actor.GetProperty().SetEdgeVisibility(1)

        # controller
        ctrl.get_render_window = self.get_render_window
        ctrl.grid_update = self._vtk_mapper.SetInputData

    def get_render_window(self):
        return self._vtk_render_window


# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server, source=None):
    state, ctrl = server.state, server.controller

    data_source = ZarrDataSource(source)
    mesh = MeshBuilder(server, data_source)
    viewer = MeshViewer(server, mesh)

    # Initialize state for UI
    state.array_tree = data_source.tree

    return viewer
