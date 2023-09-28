import json
import os
import pyvista
import xarray
from pathlib import Path
from pvxarray.vtk_source import PyVistaXarraySource
from pyvista.trame.ui import plotter_ui

from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import VAppLayout
from trame.app import get_server
from trame.widgets import html, client
from trame.widgets import vuetify3 as vuetify

from pan3d.ui import AxisDrawer, MainDrawer, Toolbar
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
        self.da_active = None
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
            self._layout = VAppLayout(self.server)
            with self._layout:
                client.Style(CSS_FILE.read_text())
                Toolbar(
                    self.ctrl.reset,
                    self.import_config,
                    self.export_config,
                )
                MainDrawer()
                AxisDrawer(
                    coordinate_select_axis_function=self.coordinate_select_axis,
                    coordinate_change_slice_function=self.coordinate_change_slice,
                    coordinate_toggle_expansion_function=self.coordinate_toggle_expansion,
                )
                with vuetify.VMain(v_show="da_active"):
                    with html.Div(style="height: 100%; position: relative"):
                        vuetify.VBanner(
                            "{{ ui_error_message }}",
                            v_show=("ui_error_message",),
                        )
                        with plotter_ui(
                            self.ctrl.get_plotter(),
                            interactive_ratio=1,
                        ) as plot_view:
                            self.ctrl.view_update = plot_view.update
                            self.ctrl.reset_camera = plot_view.reset_camera
        return self._layout

    @property
    def data_array(self):
        da = None
        if self.algorithm.time is not None and self.algorithm.time_index is not None:
            da = self.dataset[self.state.da_active][
                {self.algorithm.time: self.algorithm.time_index}
            ]
        else:
            da = self.dataset[self.state.da_active]

        step_slices = {}
        array_condition = None
        for axis in ["da_x", "da_y", "da_z"][: da.ndim]:
            coordinate_matches = [
                (index, coordinate)
                for index, coordinate in enumerate(self.state.da_coordinates)
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

        if len(step_slices) > 0:
            da = da[step_slices]

        return da

    @property
    def data_range(self):
        da = self.data_array
        if da is None:
            return 0, 0
        return da.min(), da.max()

    # -----------------------------------------------------
    # UI bound methods
    # -----------------------------------------------------

    def coordinate_select_axis(self, coordinate_name, current_axis, new_axis, **kwargs):
        if self.state[current_axis]:
            self.state[current_axis] = None
        if new_axis and new_axis != "undefined":
            self.state[new_axis] = coordinate_name
        self.mesh_changed()

    def coordinate_change_slice(self, coordinate_name, slice_attribute_name, value):
        if value.isnumeric():
            coordinate_matches = [
                (index, coordinate)
                for index, coordinate in enumerate(self.state.da_coordinates)
                if coordinate["name"] == coordinate_name
            ]
            if len(coordinate_matches) > 0:
                value = float(value)
                coord_i, coordinate = coordinate_matches[0]
                if slice_attribute_name == "step":
                    if value > 0 and value < coordinate["size"]:
                        coordinate[slice_attribute_name] = value
                else:
                    if (
                        value >= coordinate["range"][0]
                        and value <= coordinate["range"][1]
                    ):
                        coordinate[slice_attribute_name] = value

                self.state.da_coordinates[coord_i] = coordinate
                self.mesh_changed()
                self.state.dirty("da_coordinates")

    def coordinate_toggle_expansion(self, coordinate_name):
        if coordinate_name in self.state.ui_expanded_coordinates:
            self.state.ui_expanded_coordinates.remove(coordinate_name)
        else:
            self.state.ui_expanded_coordinates.append(coordinate_name)
        self.state.dirty("ui_expanded_coordinates")

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("dataset_path")
    def set_dataset_path(self, dataset_path, **kwargs):
        if self.dataset_path == dataset_path or dataset_path is None:
            return
        self.dataset_path = dataset_path
        self.state.dataset_path = dataset_path
        self.state.ui_loading = True
        for available_dataset in self.state.available_datasets:
            if (
                available_dataset["url"] == dataset_path
                and "more_info" in available_dataset
            ):
                self.state.ui_more_info_link = available_dataset["more_info"]
        if "https://" in dataset_path or os.path.exists(dataset_path):
            engine = None
            if ".zarr" in dataset_path:
                engine = "zarr"
            if ".nc" in dataset_path:
                engine = "netcdf4"
            try:
                self.dataset = xarray.open_dataset(
                    dataset_path, engine=engine, chunks={}
                )
            except Exception as e:
                self.state.ui_error_message = str(e)
                return
        else:
            # Assume it is a named tutorial dataset
            self.dataset = xarray.tutorial.load_dataset(dataset_path)
        # reset algorithm
        self.algorithm = PyVistaXarraySource()
        self.state.da_vars = [
            {"name": k, "id": i} for i, k in enumerate(self.dataset.data_vars.keys())
        ]
        self.state.da_attrs = [
            {"key": k, "value": v} for k, v in self.dataset.attrs.items()
        ]
        self.state.da_attrs.insert(
            0,
            {
                "key": "dimensions",
                "value": str(dict(self.dataset.dims)),
            },
        )
        self.state.da_coordinates = []
        self.state.ui_expanded_coordinates = []
        self.state.update(
            dict(da_x=None, da_y=None, da_z=None, da_t=None, da_t_index=0)
        )
        self.state.dataset_ready = True
        if len(self.state.da_vars) > 0:
            self.set_da_active(self.state.da_vars[0]["name"])
        else:
            self.state.no_da_vars = True
        self.state.ui_loading = False

    @change("da_active")
    def set_da_active(self, da_active, **kwargs):
        if (
            da_active is None
            or not self.state.dataset_ready
            or da_active == self.da_active
        ):
            return
        self.da_active = da_active
        self.state.da_active = da_active

        da = self.data_array
        self.state.ui_axis_drawer = True
        self.state.ui_expanded_coordinates = []
        for key in da.coords.keys():
            array_min = float(da.coords[key].min())
            array_max = float(da.coords[key].max())
            coord_attrs = [
                {"key": k, "value": v} for k, v in da.coords[key].attrs.items()
            ]
            coord_attrs.append({"key": "dtype", "value": str(da.coords[key].dtype)})
            coord_attrs.append({"key": "length", "value": da.coords[key].size})
            coord_attrs.append(
                {
                    "key": "range",
                    "value": [array_min, array_max],
                }
            )
            self.state.da_coordinates.append(
                {
                    "name": key,
                    "attrs": coord_attrs,
                    "size": da.coords[key].size,
                    "range": [array_min, array_max],
                    "start": array_min,
                    "stop": array_max,
                    "step": 1,
                }
            )
            self.state.ui_expanded_coordinates.append(key),
        self.auto_select_coordinates()
        self.state.dirty("da_coordinates", "ui_expanded_coordinates")
        self.plotter.clear()
        self.plotter.view_isometric()

    @change("da_x", "da_y", "da_z")
    def on_set_da_axis(self, da_x, da_y, da_z, **kwargs):
        self.algorithm.x = da_x
        self.algorithm.y = da_y
        self.algorithm.z = da_z
        self.mesh_changed()

    @change("da_t")
    def on_set_da_t(self, da_t, **kwargs):
        self.algorithm.time = da_t
        if self.dataset and self.state.da_active and da_t:
            time_steps = self.dataset[self.state.da_active][da_t]
            # Set the time_max in the state for the slider
            self.state.da_t_max = len(time_steps) - 1
            self.mesh_changed()

    @change("da_t_index")
    def on_set_da_t_index(self, da_t_index, **kwargs):
        self.algorithm.time_index = int(da_t_index)
        self.mesh_changed()

    @change("ui_dialog_shown")
    def on_set_ui_dialog_shown(self, ui_dialog_shown, **kwargs):
        self.state.ui_dialog_message = None
        if ui_dialog_shown == "Export":
            self.state.state_export = self.export_config(None)

    # -----------------------------------------------------
    # Render Logic
    # -----------------------------------------------------

    def auto_select_coordinates(self):
        state_update = {}
        for coordinate in self.state.da_coordinates:
            name = coordinate["name"].lower()
            for axis, accepted_names in coordinate_auto_selection.items():
                # don't overwrite if already assigned
                if not self.state[axis]:
                    # If accepted name is longer than one letter, look for contains match
                    name_match = [
                        coordinate["name"]
                        for accepted in accepted_names
                        if (len(accepted) == 1 and accepted == name)
                        or (len(accepted) > 1 and accepted in name)
                    ]
                    if len(name_match) > 0:
                        state_update[axis] = name_match[0]
        if len(state_update) > 0:
            self.state.update(state_update)

    def mesh_changed(self):
        if self.state.da_active:
            da = self.data_array
            total_bytes = da.size * da.dtype.itemsize
            exponents_map = {0: "bytes", 1: "KB", 2: "MB", 3: "GB"}
            for exponent in sorted(exponents_map.keys(), reverse=True):
                divisor = 1024**exponent
                suffix = exponents_map[exponent]
                if total_bytes > divisor:
                    self.state.da_size = f"{round(total_bytes / divisor)} {suffix}"
                    break

            self.state.ui_unapplied_changes = True

    def plot_mesh(self):
        self.plotter.clear()
        self.actor = self.plotter.add_mesh(
            self.mesh,
            clim=self.data_range,
        )
        self.plotter.view_isometric()

    def reset(self, **kwargs):
        if not self.state.da_active:
            return
        self.state.ui_error_message = None
        self.state.ui_loading = True
        self.state.ui_unapplied_changes = False

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
                self.state.ui_error_message = (
                    str(exception) if exception is not None else None
                )
                self.state.ui_loading = False

        run_singleton_task(
            update_mesh,
            mesh_updated,
            timeout=self.state.mesh_timeout,
            timeout_message=f"Failed to create mesh in under {self.state.mesh_timeout} seconds. Try reducing data size by slicing.",
        )

    # -----------------------------------------------------
    # Config logic
    # -----------------------------------------------------

    def import_config(self, config_file):
        if isinstance(config_file, dict):
            config = config_file
        elif isinstance(config_file, str):
            path = Path(config_file)
            if path.exists():
                config = json.loads(path.read_text())
            else:
                config = json.loads(config_file)
        origin_config = config.get("data_origin")
        array_config = config.get("data_array")
        slices_config = config.get("data_slices")
        ui_config = config.get("ui")

        if not origin_config or not array_config:
            self.state.ui_dialog_message = "Invalid format of import file."
            return

        self.set_dataset_path(dataset_path=origin_config)
        if "active" in array_config:
            self.set_da_active(array_config["active"])
        for axis in ["x", "y", "z", "t"]:
            if axis in array_config:
                self.state[f"da_{axis}"] = array_config[axis]
        if "da_t_index" in array_config:
            self.state.da_t_index = array_config["t_index"]

        if slices_config:
            da_coordinates = self.state.da_coordinates
            for coordinate in da_coordinates:
                if coordinate["name"] in slices_config:
                    start, stop, step = slices_config[coordinate["name"]]
                    coordinate["start"] = start
                    coordinate["stop"] = stop
                    coordinate["step"] = step
            self.state.dirty("da_coordinates")

        if ui_config:
            for key, value in ui_config.items():
                self.state[f"ui_{key}"] = value

        self.state.update({"ui_dialog_shown": None, "ui_selected_config_file": None})

    def export_config(self, config_file=None):
        config = {}
        config["data_origin"] = self.state.dataset_path
        config["data_array"] = {"active": self.state.da_active}

        for axis in ["x", "y", "z", "t"]:
            if self.state[f"da_{axis}"]:
                config["data_array"][axis] = self.state[f"da_{axis}"]
        if self.state.da_t_index:
            config["data_array"]["t_index"] = self.state.da_t_index

        da_coordinates = self.state.da_coordinates
        for coordinate in da_coordinates:
            if (
                coordinate.get("start")
                or coordinate.get("stop")
                or coordinate.get("step")
            ):
                if "data_slices" not in config:
                    config["data_slices"] = {}
                coordinate_slice = [
                    coordinate.get("start", 0),
                    coordinate.get("stop", -1),
                    coordinate.get("step", 1),
                ]
                config["data_slices"][coordinate["name"]] = coordinate_slice

        for state_var in ["main_drawer", "axis_drawer", "expanded_coordinates"]:
            if "ui" not in config:
                config["ui"] = {}
            config["ui"][state_var] = self.state[f"ui_{state_var}"]

        if config_file:
            Path(config_file).write_text(json.dumps(config))
        else:
            return config
