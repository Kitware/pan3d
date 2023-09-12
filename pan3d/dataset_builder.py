import json
import os
import pyvista
import xarray
from pathlib import Path
from pvxarray.vtk_source import PyVistaXarraySource
from pyvista.trame.ui import plotter_ui

from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.app import get_server
from trame.widgets import html, client
from trame.widgets import vuetify3 as vuetify

from pan3d.ui import AxisSelection, MainDrawer, Toolbar
from pan3d.utils import initial_state, run_singleton_task, coordinate_auto_selection

BASE_DIR = Path(__file__).parent
CSS_FILE = BASE_DIR / "ui" / "custom.css"


@TrameApp()
class DatasetBuilder:
    def __init__(self, server=None, dataset_path=None, state=None):
        if server is None:
            server = get_server()

        if isinstance(server, str):
            server = get_server(server)

        # Fix version of vue
        server.client_type = "vue3"
        self.server = server
        self._layout = None

        self.state.update(initial_state)
        self.algorithm = PyVistaXarraySource()
        self.plotter = pyvista.Plotter(off_screen=True, notebook=False)
        self.plotter.set_background("lightgrey")
        self.dataset = None
        self.dataset_path = None
        self.mesh = None
        self.actor = None

        self.ctrl.get_plotter = lambda: self.plotter
        self.ctrl.reset = self.reset

        if dataset_path:
            self.state.dataset_path = dataset_path
            self.set_dataset_path(dataset_path=dataset_path)
        if state:
            self.state.update(state)

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
    def viewer(self):
        if self._layout is None:
            # Build UI
            self._layout = SinglePageWithDrawerLayout(self.server)
            with self._layout as layout:
                client.Style(CSS_FILE.read_text())
                layout.title.set_text("Pan3D Viewer")
                layout.footer.hide()
                with layout.toolbar:
                    layout.toolbar.align = "center"
                    Toolbar(reset=self.ctrl.reset)
                with layout.drawer:
                    MainDrawer()
                with layout.content:
                    vuetify.VBanner(
                        "{{ error_message }}",
                        v_show=("error_message",),
                    )
                    with html.Div(
                        v_show="array_active",
                        style="height: 100%; position: relative;",
                    ):
                        with plotter_ui(
                            self.ctrl.get_plotter(),
                            interactive_ratio=1,
                        ) as plot_view:
                            self.ctrl.view_update = plot_view.update
                            self.ctrl.reset_camera = plot_view.reset_camera
                    AxisSelection(
                        coordinate_select_axis_function=self.coordinate_select_axis,
                        coordinate_change_slice_function=self.coordinate_change_slice,
                    )
        return self._layout

    @property
    def data_array(self):
        da = None
        if self.algorithm.time is not None and self.algorithm.time_index is not None:
            da = self.dataset[self.state.array_active][
                {self.algorithm.time: self.algorithm.time_index}
            ]
        else:
            da = self.dataset[self.state.array_active]

        step_slices = {}
        array_condition = None
        for axis in ["x_array", "y_array", "z_array"][: da.ndim]:
            coordinate_matches = [
                (index, coordinate)
                for index, coordinate in enumerate(self.state.coordinates)
                if coordinate["name"] == self.state[axis]
            ]
            if len(coordinate_matches) > 0:
                coord_i, coordinate = coordinate_matches[0]
                step_slices[coordinate["name"]] = slice(0, -1, int(coordinate["step"]))
                coordinate_condition = (
                    da[coordinate["name"]] >= coordinate["start"]
                ) & (da[coordinate["name"]] <= coordinate["stop"])
                if array_condition is None:
                    array_condition = coordinate_condition
                else:
                    array_condition = (array_condition) & (coordinate_condition)

        if array_condition is not None:
            da = da.where((array_condition), drop=True)

        if len(step_slices.keys()) > 0:
            da = da[step_slices]

        return da

    @property
    def data_range(self):
        if self.data_array is None:
            return 0, 0
        return self.data_array.min(), self.data_array.max()

    # -----------------------------------------------------
    # UI bound methods
    # -----------------------------------------------------

    def coordinate_select_axis(self, coordinate_name, current_axis, new_axis, **kwargs):
        if getattr(self.state, current_axis):
            setattr(self.state, current_axis, None)
        if new_axis and new_axis != "undefined":
            setattr(self.state, new_axis, coordinate_name)
        self.mesh_changed()

    def coordinate_change_slice(self, coordinate_name, slice_attribute_name, value):
        coordinate_matches = [
            (index, coordinate)
            for index, coordinate in enumerate(self.state.coordinates)
            if coordinate["name"] == coordinate_name
        ]
        if len(coordinate_matches) > 0:
            value = float(value)
            coord_i, coordinate = coordinate_matches[0]
            if slice_attribute_name == "step":
                if value > 0 and value < coordinate["range"][1]:
                    coordinate[slice_attribute_name] = value
            else:
                if value > coordinate["range"][0] and value < coordinate["range"][1]:
                    coordinate[slice_attribute_name] = value
            self.mesh_changed()

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("dataset_path")
    def set_dataset_path(self, dataset_path, **kwargs):
        if self.dataset_path == dataset_path or dataset_path is None:
            return
        self.dataset_path = dataset_path
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
        self.state.update(
            dict(x_array=None, y_array=None, z_array=None, t_array=None, t_index=0)
        )
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
        da = self.data_array
        for key in da.coords.keys():
            array_min = float(da.coords[key].min())
            array_max = float(da.coords[key].max())
            coord_attrs = [
                {"key": k, "value": v} for k, v in da.coords[key].attrs.items()
            ]
            coord_attrs.append({"key": "dtype", "value": str(da.coords[key].dtype)})
            coord_attrs.append({"key": "length", "value": da.coords[key].size})
            self.state.coordinates.append(
                {
                    "name": key,
                    "attrs": coord_attrs,
                    "range": [array_min, array_max],
                    "start": array_min,
                    "stop": array_max,
                    "step": 1,
                }
            )
        self.auto_select_coordinates()

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
        if self.dataset and self.state.array_active and t_array:
            time_steps = self.dataset[self.state.array_active][t_array]
            # Set the time_max in the state for the slider
            self.state.t_max = len(time_steps) - 1
            self.mesh_changed()

    @change("t_index")
    def on_set_t_index(self, t_index, **kwargs):
        self.algorithm.time_index = t_index
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

    def auto_select_coordinates(self):
        state_update = {}
        for coordinate in self.state.coordinates:
            name = coordinate["name"].lower()
            for axis, accepted_names in coordinate_auto_selection.items():
                # If accepted name is longer than one letter, look for contains match
                name_match = [
                    coordinate["name"]
                    for accepted in accepted_names
                    if (len(accepted) == 1 and accepted == name)
                    or (len(accepted) > 1 and accepted in name)
                ]
                if len(name_match) > 0:
                    state_update[axis] = name_match[0]
        if len(state_update.keys()) > 0:
            self.state.update(state_update)

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
            timeout_message=f"Failed to create mesh in under {self.state.mesh_timeout} seconds. Try reducing data size by slicing.",
        )

    # -----------------------------------------------------
    # Config logic
    # -----------------------------------------------------

    def import_config(self, config_path):
        with open(config_path) as config_file:
            config = json.load(config_file)
            self.set_dataset_path(dataset_path=config.get("dataset_path"))
            self.state.update(config.get("state"))

    def export_config(self, config_path):
        # TODO
        pass
