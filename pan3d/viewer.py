import os
import pyvista
from pvxarray.vtk_source import PyVistaXarraySource
import xarray

from trame.decorators import TrameApp, change
from trame.ui.vuetify import SinglePageWithDrawerLayout  # TODO: upgrade to vuetify 3
from trame.app import get_server

from .ui import initialize as viewer_ui
from .utils import initial_state, run_singleton_task


@TrameApp()
class Pan3DViewer:
    def __init__(self, server=None, dataset_path=None, state=None):
        if server is None:
            server = get_server()

        if isinstance(server, str):
            server = get_server(server)

        self.server = server
        self.state.update(initial_state)
        self.dataset = None
        self.dataset_path = dataset_path
        self.algorithm = PyVistaXarraySource()
        self.plotter = pyvista.Plotter(off_screen=True, notebook=False)
        self.plotter.set_background("lightgrey")
        self.mesh = None
        self.actor = None

        self.ctrl.get_plotter = lambda: self.plotter
        self.ctrl.reset = self.reset

        # Fix version of vue
        server.client_type = "vue2"  # TODO: upgrade to vue3
        # Build GUI
        self.layout = SinglePageWithDrawerLayout(self.server)
        viewer_ui(self.layout, self.ctrl)

    # -----------------------------------------------------
    # Properties
    # -----------------------------------------------------

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    @property
    def gui(self):
        return self.layout

    @property
    def data_array(self):
        da = None
        if self.algorithm.time is not None and self.algorithm.time_index is not None:
            da = self.dataset[self.state.array_active][
                {self.algorithm.time: self.algorithm.time_index}
            ]
        else:
            da = self.dataset[self.state.array_active]

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

    def mesh_changed(self):
        if self.state.array_active:
            total_bytes = self.data_array.size * self.data_array.dtype.itemsize
            exponents_map = {0: "bytes", 1: "KB", 2: "MB", 3: "GB"}
            for exponent in sorted(exponents_map.keys(), reverse=True):
                divisor = 1024**exponent
                suffix = exponents_map[exponent]
                if total_bytes > divisor:
                    self.state.da_size = f"{round(total_bytes / divisor)} {suffix}"
                    break

            self.state.unapplied_changes = True

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("dataset_path")
    def set_dataset_path(self, **kwargs):
        dataset_path = self.state.dataset_path
        if not dataset_path:
            return
        self.state.loading = True
        for available_dataset in self.state.available_datasets:
            if (
                available_dataset["url"] == dataset_path
                and "more_info" in available_dataset
            ):
                self.state.more_info_link = available_dataset["more_info"]
        if "https://" in dataset_path or os.path.exists(dataset_path):
            # Assumes zarr store
            try:
                self.dataset = xarray.open_dataset(
                    dataset_path, engine="zarr", chunks={}
                )
            except Exception as e:
                self.state.error_message = str(e)
                return
        else:
            # Assume it is a named tutorial dataset
            self.dataset = xarray.tutorial.load_dataset(dataset_path)
        self.state.data_vars = [
            {"name": k, "id": i} for i, k in enumerate(self.dataset.data_vars.keys())
        ]
        self.state.data_attrs = [
            {"key": k, "value": v} for k, v in self.dataset.attrs.items()
        ]
        self.state.data_attrs.insert(
            0,
            {
                "key": "dimensions",
                "value": str(dict(self.dataset.dims)),
            },
        )
        if len(self.state.data_attrs) > 0:
            self.state.show_data_attrs = True
        self.state.coordinates = []
        self.state.dataset_ready = True
        if len(self.state.data_vars) > 0:
            self.state.array_active = self.state.data_vars[0]["name"]
        else:
            self.state.no_data_vars = True
        self.state.loading = False

    @change("array_active")
    def on_set_array_active(self, array_active, **kwargs):
        if array_active is None or not self.state.dataset_ready:
            return
        self.state.coordinates = list(self.data_array.coords.keys())

    @change("x_array")
    def on_set_x_array(self, x_array, **kwargs):
        self.algorithm.x = x_array
        self.mesh_changed()

    @change("y_array")
    def on_set_y_array(self, y_array, **kwargs):
        self.algorithm.y = y_array
        self.mesh_changed()

    @change("z_array")
    def on_set_z_array(self, z_array, **kwargs):
        self.algorithm.z = z_array
        self.mesh_changed()

    @change("t_array")
    def on_set_t_array(self, t_array, **kwargs):
        self.algorithm.time = t_array
        if t_array:
            time_steps = self.dataset[self.state.array_active][t_array]
            # Set the time_max in the state for the slider
            self.state.t_max = len(time_steps) - 1
            self.state.t_index = 0
        self.mesh_changed()

    @change("t_index")
    def on_set_t_index(self, t_index, **kwargs):
        self.algorithm.time_index = t_index
        self.mesh_changed()

    @change("resolution")
    def on_set_resolution(self, resolution, **kwargs):
        self.algorithm.resolution = resolution
        self.mesh_changed()

    @change("view_edge_visibility")
    def on_set_edge_visiblity(self, view_edge_visibility, **kwargs):
        if self.actor is None:
            return
        self.actor.GetProperty().SetEdgeVisibility(1 if view_edge_visibility else 0)
        self.plotter.update()

    @change("x_scale", "y_scale", "z_scale")
    def on_set_scale(self, x_scale=None, y_scale=None, z_scale=None, **kwargs):
        x_scale = x_scale or self.state.x_scale
        y_scale = y_scale or self.state.y_scale
        z_scale = z_scale or self.state.z_scale
        self.plotter.set_scale(xscale=x_scale, yscale=y_scale, zscale=z_scale)

    # -----------------------------------------------------
    # Render Logic
    # -----------------------------------------------------

    def plot_mesh(self):
        self.plotter.clear()
        self.actor = self.plotter.add_mesh(
            self.mesh,
            show_edges=self.state.view_edge_visibility,
            clim=self.data_range,
        )
        self.plotter.view_isometric()

    def reset(self, **kwargs):
        if not self.state.array_active:
            return
        self.state.error_message = None
        self.state.loading = True

        async def update_mesh():
            self.mesh = self.data_array.pyvista.mesh(
                self.algorithm.x,
                self.algorithm.y,
                self.algorithm.z,
                self.algorithm.order,
                self.algorithm.component,
            )
            self.plot_mesh()

        def mesh_updated(exception=None):
            with self.state:
                self.state.error_message = (
                    str(exception) if exception is not None else None
                )
                self.state.loading = False
                self.state.unapplied_changes = False

        run_singleton_task(
            update_mesh,
            mesh_updated,
            timeout=self.state.mesh_timeout,
            timeout_message=f"Failed to create mesh in under {self.state.mesh_timeout} seconds. Try reducing data size by slicing or decreasing resolution.",
        )
