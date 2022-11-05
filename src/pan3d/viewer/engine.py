import os

import geovista as gv
import pyvista as pv
import xarray as xr
from pvxarray.vtk_source import PyVistaXarraySource


def vuwrap(func):
    def wrapper(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self._ctrl.view_update()
        return ret

    return wrapper


class MeshBuilder:
    def __init__(self, server):
        self._server = server
        self._state = server.state
        self._ctrl = server.controller

        self._dataset = None
        self._algorithm = PyVistaXarraySource()
        self._algorithm.time_index = 0

        # State variables
        self.clear_dataset()
        self._state.resolution = 1.0

        # Listen to changes
        self._state.change("array_active")(self.on_active_array)
        self._state.change("grid_x_array")(self.bind_x)
        self._state.change("grid_y_array")(self.bind_y)
        self._state.change("grid_z_array")(self.bind_z)
        self._state.change("grid_t_array")(self.bind_t)
        self._state.change("time_index")(self.set_time_index)
        self._state.change("z_index")(self.set_z_index)
        self._state.change("resolution")(self.set_resolution)
        self._state.change("dataset_path")(self.set_dataset_path)

        self._ctrl.clear_dataset = self.clear_dataset

    def set_dataset_path(self, **kwargs):
        dataset_path = self._state.dataset_path
        if not dataset_path:
            return
        if os.path.exists(dataset_path):
            # Assumes zarr store
            self._dataset = xr.open_dataset(
                dataset_path, engine="zarr", consolidated=False
            )
        else:
            # Assume it is a named tutorial dataset
            self._dataset = xr.tutorial.load_dataset(dataset_path)
        self._state.data_vars = [
            {"name": k, "id": i} for i, k in enumerate(self._dataset.data_vars.keys())
        ]
        self._state.coordinates = []
        self._state.dataset_ready = True
        # Set first array as active
        # TODO self._state.array_active = list(dataset.data_vars.keys())[0]

    def clear_dataset(self, **kwargs):
        self._state.dataset_path = None
        self._state.data_vars = []
        self._state.coordinates = []
        self._state.dataset_ready = False
        self._state.array_active = None
        self._state.grid_x_array = None
        self._state.grid_y_array = None
        self._state.grid_z_array = None
        self._state.grid_t_array = None
        self._state.time_max = 0
        self._state.z_max = 0

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def data_array(self):
        return self._algorithm.data_array

    def on_active_array(self, array_active, **kwargs):
        if array_active is None or not self._state.dataset_ready:
            return
        self._algorithm.data_array = self._dataset[array_active]
        self._state.coordinates = list(self.data_array.coords.keys())

    def bind_x(self, grid_x_array, **kwargs):
        self.algorithm.x = grid_x_array

    def bind_y(self, grid_y_array, **kwargs):
        self.algorithm.y = grid_y_array

    def bind_z(self, grid_z_array, **kwargs):
        self.algorithm.z = grid_z_array
        if grid_z_array:
            # Set the z_max in the state for the slider
            self._state.z_max = len(self.data_array[grid_z_array]) - 1

    def bind_t(self, grid_t_array, **kwargs):
        self.algorithm.time = grid_t_array
        if grid_t_array:
            # Set the time_max in the state for the slider
            self._state.time_max = len(self.data_array[grid_t_array]) - 1

    @vuwrap
    def set_time_index(self, time_index, **kwargs):
        self.algorithm.time_index = time_index

    @vuwrap
    def set_z_index(self, z_index, **kwargs):
        self.algorithm.z_index = z_index

    @vuwrap
    def set_resolution(self, resolution, **kwargs):
        self.algorithm.resolution = resolution

    @property
    def data_range(self):
        return self.data_array.min(), self.data_array.max()


class MeshViewer:
    def __init__(self, server, mesher):
        state, ctrl = server.state, server.controller
        self._ctrl = ctrl
        self._state = state
        self.mesher = mesher

        self.plotter = gv.GeoPlotter(off_screen=True, notebook=False)
        self.plotter.set_background("lightgrey")
        self.plotter.enable_depth_peeling()
        self.actor = None
        self.basemap_actor = None
        self.setup_geovista()

        # controller
        ctrl.get_render_window = lambda: self.plotter.ren_win
        ctrl.reset = self.reset

        # Listen to changes
        self._state.change("view_edge_visiblity")(self.on_edge_visiblity_change)
        self._state.change("view_basemap")(self.on_view_basemap_change)

    def setup_geovista(self):
        self.basemap_actor = self.plotter.add_base_layer(texture=gv.blue_marble())
        resolution = "10m"
        self.plotter.add_coastlines(resolution=resolution, color="white")
        # self.plotter.add_axes()
        # self.plotter.add_text(
        #     f"NOAA/NCEI OISST AVHRR ({resolution} Coastlines)",
        #     position="upper_left",
        #     font_size=10,
        #     shadow=True,
        # )
        self.plotter.view_isometric()

    @vuwrap
    def reset(self, **kwargs):
        self.plotter.clear()
        self.mesher.algorithm.Modified()
        self.setup_geovista()
        self.actor = self.plotter.add_mesh(
            self.mesher.algorithm,
            show_edges=self._state.view_edge_visiblity,
            clim=self.mesher.data_range,
            cmap="coolwarm",
            # Requires https://github.com/pyvista/pyvista/pull/3556
            nan_opacity=0,
            **kwargs,
        )

    @vuwrap
    def on_edge_visiblity_change(self, view_edge_visiblity, **kwargs):
        if self.actor is None:
            return
        self.actor.GetProperty().SetEdgeVisibility(1 if view_edge_visiblity else 0)

    @vuwrap
    def on_view_basemap_change(self, view_basemap, **kwargs):
        if self.basemap_actor is None:
            return
        self.basemap_actor.SetVisibility(1 if view_basemap else 0)


# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server):
    mesher = MeshBuilder(server)
    viewer = MeshViewer(server, mesher)
    return viewer
