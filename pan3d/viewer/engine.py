import os
import pyvista as pv
import xarray as xr

from pvxarray.vtk_source import PyVistaXarraySource
from pan3d.pangeo_forge import get_catalog
from pan3d.viewer.utils import run_singleton_task


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

        # State variables
        self.clear_dataset()
        self._state.resolution = 1.0
        self._state.available_datasets = [
            {"name": "XArray Examples - air temperature", "url": "air_temperature"},
            {"name": "XArray Examples - basin mask", "url": "basin_mask"},
            {"name": "XArray Examples - eraint uvz", "url": "eraint_uvz"},
        ]
        self._state.available_datasets += get_catalog()

        # Listen to changes
        self._state.change("array_active")(self.on_active_array)
        self._state.change("grid_x_array")(self.bind_x)
        self._state.change("grid_y_array")(self.bind_y)
        self._state.change("grid_z_array")(self.bind_z)
        self._state.change("grid_t_array")(self.bind_t)
        self._state.change("time_index")(self.set_time_index)
        self._state.change("resolution")(self.set_resolution)
        self._state.change("dataset_path")(self.set_dataset_path)

        self._ctrl.clear_dataset = self.clear_dataset

    def set_dataset_path(self, **kwargs):
        dataset_path = self._state.dataset_path
        if not dataset_path:
            return
        self._state.loading = True
        for available_dataset in self._state.available_datasets:
            if (
                available_dataset["url"] == dataset_path
                and "more_info" in available_dataset
            ):
                self._state.more_info_link = available_dataset["more_info"]
        if "https://" in dataset_path or os.path.exists(dataset_path):
            # Assumes zarr store
            try:
                self._dataset = xr.open_dataset(dataset_path, engine="zarr", chunks={})
            except Exception as e:
                self._state.error_message = str(e)
                return
        else:
            # Assume it is a named tutorial dataset
            self._dataset = xr.tutorial.load_dataset(dataset_path)
        self._state.data_vars = [
            {"name": k, "id": i} for i, k in enumerate(self._dataset.data_vars.keys())
        ]
        self._state.data_attrs = [
            {"key": k, "value": v} for k, v in self._dataset.attrs.items()
        ]
        self._state.data_attrs.insert(
            0,
            {
                "key": "dimensions",
                "value": str(dict(self._dataset.dims)),
            },
        )
        if len(self._state.data_attrs) > 0:
            self._state.show_data_attrs = True
        self._state.coordinates = []
        self._state.dataset_ready = True
        if len(self._state.data_vars) > 0:
            self._state.array_active = self._state.data_vars[0]["name"]
        else:
            self._state.no_data_vars = True
        self._state.loading = False

    def clear_dataset(self, **kwargs):
        self._state.dataset_path = None
        self._state.more_info_link = None

        self._state.data_vars = []
        self._state.data_attrs = []
        self._state.active_tree_nodes = []
        self._state.coordinates = []

        self._state.show_data_attrs = False
        self._state.dataset_ready = False
        self._state.no_data_vars = False

        self._state.array_active = None
        self._state.grid_x_array = None
        self._state.grid_y_array = None
        self._state.grid_z_array = None
        self._state.grid_t_array = None
        self._state.time_max = 0

        self._state.error_message = None
        self._state.da_size = None
        self._state.loading = False
        self._state.unapplied_changes = False

    def mesh_changed(self):
        if self._state.array_active:
            total_bytes = self.data_array.size * self.data_array.dtype.itemsize
            exponents_map = {0: "bytes", 1: "KB", 2: "MB", 3: "GB"}
            for exponent in sorted(exponents_map.keys(), reverse=True):
                divisor = 1024**exponent
                suffix = exponents_map[exponent]
                if total_bytes > divisor:
                    self._state.da_size = f"{round(total_bytes / divisor)} {suffix}"
                    break

            self._state.unapplied_changes = True

    def on_active_array(self, array_active, **kwargs):
        if array_active is None or not self._state.dataset_ready:
            self._state.active_tree_nodes = []
            return
        self._state.coordinates = list(self.data_array.coords.keys())
        self._state.active_tree_nodes = [array_active]
        self._state.grid_x_array = None
        self._state.grid_y_array = None
        self._state.grid_z_array = None
        self._state.grid_t_array = None

    def bind_x(self, grid_x_array, **kwargs):
        self.algorithm.x = grid_x_array
        self.mesh_changed()

    def bind_y(self, grid_y_array, **kwargs):
        self.algorithm.y = grid_y_array
        self.mesh_changed()

    def bind_z(self, grid_z_array, **kwargs):
        self.algorithm.z = grid_z_array
        self.mesh_changed()

    def bind_t(self, grid_t_array, **kwargs):
        self.algorithm.time = grid_t_array
        if grid_t_array:
            time_steps = self._dataset[self._state.array_active][grid_t_array]
            # Set the time_max in the state for the slider
            self._state.time_max = len(time_steps) - 1
            self.algorithm.time_index = 0
        self.mesh_changed()

    @vuwrap
    def set_time_index(self, time_index, **kwargs):
        self.algorithm.time_index = time_index
        self.mesh_changed()

    @vuwrap
    def set_resolution(self, resolution, **kwargs):
        self.algorithm.resolution = resolution
        self.mesh_changed()

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def data_array(self):
        da = None
        if self.algorithm.time is not None and self.algorithm.time_index is not None:
            da = self._dataset[self._state.array_active][
                {self.algorithm.time: self.algorithm.time_index}
            ]
        else:
            da = self._dataset[self._state.array_active]

        if self.algorithm.resolution != 1:
            rx, ry, rz = self.algorithm.resolution_to_sampling_rate(da)
            if da.ndim <= 1:
                da = da[::rx]
            elif da.ndim == 2:
                da = da[::rx, ::ry]
            elif da.ndim == 3:
                da = da[::rx, ::ry, ::rz]

        return da

    @property
    def data_range(self):
        if self.data_array is None:
            return 0, 0
        return self.data_array.min(), self.data_array.max()


class MeshViewer:
    def __init__(self, server, mesher):
        state, ctrl = server.state, server.controller
        self._ctrl = ctrl
        self._state = state
        self.mesher = mesher

        self.plotter = pv.Plotter(off_screen=True, notebook=False)
        self.plotter.set_background("lightgrey")
        self.mesh = None
        self.actor = None

        # controller
        ctrl.get_plotter = lambda: self.plotter
        ctrl.reset = self.reset

        self._state.x_scale = 1
        self._state.y_scale = 1
        self._state.z_scale = 1
        self._state.mesh_timeout = 30
        # Listen to changes
        self._state.change("view_edge_visiblity")(self.on_edge_visiblity_change)
        self._state.change("x_scale")(self.set_scale)
        self._state.change("y_scale")(self.set_scale)
        self._state.change("z_scale")(self.set_scale)

    @vuwrap
    def reset(self, **kwargs):
        if not self._state.array_active:
            return
        self._state.error_message = None
        self._state.loading = True

        async def update_mesh():
            self.mesh = self.mesher.data_array.pyvista.mesh(
                self.mesher.algorithm.x,
                self.mesher.algorithm.y,
                self.mesher.algorithm.z,
                self.mesher.algorithm.order,
                self.mesher.algorithm.component,
            )
            self.plot_mesh()

        def mesh_updated(exception=None):
            with self._state:
                self._state.error_message = (
                    str(exception) if exception is not None else None
                )
                self._state.loading = False
                self._state.unapplied_changes = False

        run_singleton_task(
            update_mesh,
            mesh_updated,
            timeout=self._state.mesh_timeout,
            timeout_message=f"Failed to create mesh in under {self._state.mesh_timeout} seconds. Try reducing data size by slicing or decreasing resolution.",
        )

    @vuwrap
    def plot_mesh(self):
        self.plotter.clear()
        self.actor = self.plotter.add_mesh(
            self.mesh,
            show_edges=self._state.view_edge_visiblity,
            clim=self.mesher.data_range,
        )
        self.plotter.view_isometric()

    @vuwrap
    def on_edge_visiblity_change(self, view_edge_visiblity, **kwargs):
        if self.actor is None:
            return
        self.actor.GetProperty().SetEdgeVisibility(1 if view_edge_visiblity else 0)

    @vuwrap
    def set_scale(self, x_scale=None, y_scale=None, z_scale=None, **kwargs):
        x_scale = x_scale or self._state.x_scale
        y_scale = y_scale or self._state.y_scale
        z_scale = z_scale or self._state.z_scale
        self.plotter.set_scale(xscale=x_scale, yscale=y_scale, zscale=z_scale)


# ---------------------------------------------------------
# Server binding
# ---------------------------------------------------------


def initialize(server, **kwargs):
    mesher = MeshBuilder(server, **kwargs)
    viewer = MeshViewer(server, mesher)
    return viewer
