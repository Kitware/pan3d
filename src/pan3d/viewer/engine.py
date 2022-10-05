import pyvista as pv
from pvxarray.vtk_source import PyVistaXarraySource

from . import module


class MeshBuilder:
    def __init__(self, server, dataset):
        self._server = server
        self._state = server.state
        self._ctrl = server.controller

        self._dataset = dataset
        self._grid_editor = None

        self._algorithm = PyVistaXarraySource(dataset, resolution=1.0)

        # State variables
        self._state.array_active = None
        self._state.grid_x_array = None
        self._state.grid_y_array = None
        self._state.grid_z_array = None
        self._state.grid_t_array = None

        # Listen to changes
        self._state.change("array_active")(self.on_active_array)
        self._state.change("grid_x_array")(self.bind_x)
        self._state.change("grid_y_array")(self.bind_y)
        self._state.change("grid_z_array")(self.bind_z)
        self._state.change("grid_t_array")(self.bind_t)

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def data_array(self):
        return self._algorithm.data_array

    @data_array.setter
    def data_array(self, data_array):
        self._algorithm.data_array = data_array

    def bind_x(self, grid_x_array, **kwargs):
        self.algorithm.x = grid_x_array

    def bind_y(self, grid_y_array, **kwargs):
        self.algorithm.y = grid_y_array

    def bind_z(self, grid_z_array, **kwargs):
        self.algorithm.z = grid_z_array

    def bind_t(self, grid_t_array, **kwargs):
        self.algorithm.time = grid_t_array

    def on_active_array(self, array_active, **kwargs):
        if array_active is None:
            return
        self.data_array = self._dataset[array_active]
        self._state.coordinates = list(self.data_array.coords.keys())


class MeshViewer:
    def __init__(self, server, mesher):
        state, ctrl = server.state, server.controller
        self._ctrl = ctrl
        self._state = state
        self.mesher = mesher

        # Needed to override CSS
        server.enable_module(module)

        self.plotter = pv.Plotter(off_screen=True, notebook=False)
        self.actor = None
        self.plotter.set_background("grey")

        # controller
        ctrl.get_render_window = self.get_render_window
        ctrl.build = self.build

        # Listen to changes
        state.change("grid_active_array")(self.on_color_by)
        state.change("view_edge_visiblity")(self.on_edge_visiblity_change)

    def add_mesh(self, **kwargs):
        self.mesher.algorithm.Modified()
        self.plotter.clear()
        self.actor = self.plotter.add_mesh(
            self.mesher.algorithm, show_edges=self._state.view_edge_visiblity, **kwargs
        )
        self.plotter.view_isometric()
        self._ctrl.view_update()

    def get_render_window(self):
        return self.plotter.ren_win

    def on_edge_visiblity_change(self, view_edge_visiblity, **kwargs):
        if self.actor is None:
            return
        self.actor.GetProperty().SetEdgeVisibility(1 if view_edge_visiblity else 0)
        self._ctrl.view_update()

    def on_color_by(self, grid_active_array, **kwargs):
        if self.actor is None:
            return
        if grid_active_array == "Solid Color":
            self.add_mesh(color=True)
        else:
            self.add_mesh()
        self._ctrl.view_update()

    def build(self):
        self.add_mesh()


# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server, dataset):
    mesher = MeshBuilder(server, dataset)
    viewer = MeshViewer(server, mesher)

    # Initialize state for UI
    server.state.data_vars = [
        {"name": k, "id": i} for i, k in enumerate(dataset.data_vars.keys())
    ]
    server.state.coordinates = []

    return viewer
