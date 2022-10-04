import pyvista as pv

from .core.data_sources import ZarrDataSource
from .core.grids import RectilinearBuilder
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

        self._state.grid_dimensions = [1, 1, 1]
        self._state.grid_spacing = [1, 1, 1]
        self._state.grid_origin = [1, 1, 1]

        # Listen to changes
        self._state.change("array_active")(self.on_active_array)

        self._grid_editor = RectilinearBuilder(self._server, self._data_source)
        # self._ctrl.grid_update(self._grid_editor.grid)

    def on_active_array(self, array_active, **kwargs):
        self._active_array = self._data_source.get(array_active)
        self._state.array_info = None
        if self._active_array is not None:
            dims = list(self._active_array.shape)
            self._state.array_info = {
                "dimensions": dims,
                "type": f"{self._active_array.dtype}",
                "name": self._active_array.name,
            }


class MeshViewer:
    def __init__(self, server, mesher):
        state, ctrl = server.state, server.controller
        self._ctrl = ctrl

        # Needed to override CSS
        server.enable_module(module)

        self.plotter = pv.Plotter(off_screen=True, notebook=False)
        self.actor = None
        self.plotter.set_background('blue')

        # controller
        ctrl.get_render_window = self.get_render_window

        self.actor = self.plotter.add_mesh(mesher._grid_editor.grid, name='mesh')

        # Listen to changes
        state.change("grid_active_array")(self.on_color_by)
        state.change("view_edge_visiblity")(self.on_edge_visiblity_change)

    def get_render_window(self):
        return self.plotter.ren_win

    def on_edge_visiblity_change(self, view_edge_visiblity, **kwargs):
        if self.actor is None:
            return
        self.actor.GetProperty().SetEdgeVisibility(1 if view_edge_visiblity else 0)
        self.plotter.view_isometric()  # DEBUG
        self._ctrl.view_update()

    def on_color_by(self, grid_active_array, **kwargs):
        if self.actor is None:
            return
        mapper = self.actor.mapper
        if grid_active_array == "Solid Color":
            mapper.color_mode = False
        else:
            mapper.color_mode = 'map'
            mapper.SetScalarModeToUsePointFieldData()
            mapper.SelectColorArray(grid_active_array)

            input = mapper.GetInput()
            input_array = input.GetPointData().GetArray(grid_active_array)

            if input_array is None:
                input_array = input.GetCellData().GetArray(grid_active_array)
                mapper.SetScalarModeToUseCellFieldData()

            min_value, max_value = 0, 1
            if input_array:
                min_value, max_value = input_array.GetRange(-1)

            mapper.SetScalarRange(min_value, max_value)

        self._ctrl.view_update()


# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server, source=None):
    data_source = ZarrDataSource(source)
    mesher = MeshBuilder(server, data_source)
    viewer = MeshViewer(server, mesher)

    # Initialize state for UI
    server.state.array_tree = data_source.tree

    return viewer
