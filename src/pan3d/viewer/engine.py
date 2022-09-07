import vtk

from .core.data_sources import ZarrDataSource
from .core.grids import MESH_TYPES
from . import module


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

        self._state.grid_dimensions = [1, 1, 1]
        self._state.grid_spacing = [1, 1, 1]
        self._state.grid_origin = [1, 1, 1]

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
        self._ctrl = ctrl

        # Needed to override CSS
        server.enable_module(module)

        # VTK
        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_renderer.SetBackground(0.8, 0.8, 0.8)
        self._vtk_render_window = vtk.vtkRenderWindow()
        self._vtk_render_window.AddRenderer(self._vtk_renderer)
        self._vtk_render_window_interactor = vtk.vtkRenderWindowInteractor()
        self._vtk_render_window_interactor.SetRenderWindow(self._vtk_render_window)
        self._vtk_render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        self._vtk_mapper = vtk.vtkDataSetMapper()
        self._vtk_actor = vtk.vtkActor()
        self._vtk_actor.SetVisibility(0)
        self._vtk_actor.SetMapper(self._vtk_mapper)
        self._vtk_renderer.AddActor(self._vtk_actor)
        self._vtk_renderer.ResetCamera()

        self._vtk_lut = vtk.vtkLookupTable()
        self._vtk_lut.SetHueRange(0.7, 0)
        self._vtk_lut.SetSaturationRange(1.0, 0)
        self._vtk_lut.SetValueRange(0.5, 1.0)
        self._vtk_mapper.SetLookupTable(self._vtk_lut)

        # controller
        ctrl.get_render_window = self.get_render_window
        ctrl.grid_update = self.on_grid_available

        # Listen to changes
        state.change("grid_active_array")(self.on_color_by)
        state.change("view_edge_visiblity")(self.on_edge_visiblity_change)

    def get_render_window(self):
        return self._vtk_render_window

    def on_grid_available(self, input_mesh):
        self._vtk_actor.SetVisibility(1)
        self._vtk_mapper.SetInputData(input_mesh)
        self._ctrl.view_update()

    def on_edge_visiblity_change(self, view_edge_visiblity, **kwargs):
        self._vtk_actor.GetProperty().SetEdgeVisibility(1 if view_edge_visiblity else 0)
        self._ctrl.view_update()

    def on_color_by(self, grid_active_array, **kwargs):
        if grid_active_array == "Solid Color":
            self._vtk_mapper.ScalarVisibilityOff()
        else:
            self._vtk_mapper.ScalarVisibilityOn()
            self._vtk_mapper.SetScalarModeToUsePointFieldData()
            self._vtk_mapper.SelectColorArray(grid_active_array)

            input = self._vtk_mapper.GetInput()
            input_array = input.GetPointData().GetArray(grid_active_array)

            if input_array is None:
                input_array = input.GetCellData().GetArray(grid_active_array)
                self._vtk_mapper.SetScalarModeToUseCellFieldData()

            min_value, max_value = 0, 1
            if input_array:
                min_value, max_value = input_array.GetRange(-1)

            self._vtk_mapper.SetScalarRange(min_value, max_value)

        self._ctrl.view_update()


# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server, source=None):
    data_source = ZarrDataSource(source)
    mesh = MeshBuilder(server, data_source)
    viewer = MeshViewer(server, mesh)

    # Initialize state for UI
    server.state.array_tree = data_source.tree

    return viewer
