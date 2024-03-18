import asyncio
import concurrent.futures
import json
import pandas
import pyvista
from pathlib import Path
from typing import Dict, List, Optional, Union

from trame.decorators import TrameApp, change
from trame.app import get_server
from trame.widgets import html, client
from trame.widgets import vuetify3 as vuetify
from trame_server.core import Server
from trame_server.state import State
from trame_server.controller import Controller
from trame_vuetify.ui.vuetify3 import VAppLayout

from pan3d import catalogs as pan3d_catalogs
from pan3d.dataset_builder import DatasetBuilder
from pan3d.ui import AxisDrawer, MainDrawer, Toolbar, RenderOptions
from pan3d.utils import (
    initial_state,
    has_gpu_rendering,
)

BASE_DIR = Path(__file__).parent
CSS_FILE = BASE_DIR / "ui" / "custom.css"


@TrameApp()
class DatasetViewer:
    """Create a Trame GUI for a DatasetBuilder instance and manage rendering"""

    def __init__(
        self,
        builder: Optional[DatasetBuilder] = None,
        server: Union[Server, str] = None,
        state: dict = None,
        catalogs: List[str] = [],
    ) -> None:
        """Create an instance of the DatasetViewer class.

        Parameters:
            builder: Pan3D DatasetBuilder instance.
            server: Trame server name or instance.
            state:  A dictionary of initial state values.
            catalogs: A list of strings referencing available catalog modules (options include 'pangeo', 'esgf'). Each included catalog will be available to search in the Viewer UI.
        """
        if builder is None:
            builder = DatasetBuilder()
            builder._viewer = self
        self.builder = builder
        self.server = get_server(server, client_type="vue3")
        self.current_event_loop = asyncio.get_event_loop()
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._ui = None

        self.plotter = pyvista.Plotter(off_screen=True, notebook=False)
        self.plotter.set_background("lightgrey")
        self.plot_view = None
        self.actor = None
        self.ctrl.get_plotter = lambda: self.plotter
        self.ctrl.on_client_connected.add(self._on_ready)

        self.state.update(initial_state)
        self.state.ready()
        if state:
            self.state.update(state)

        if catalogs:
            self.state.available_catalogs = [
                pan3d_catalogs.get(catalog_name) for catalog_name in catalogs
            ]

        self._force_local_rendering = not has_gpu_rendering()
        if self._force_local_rendering:
            pyvista.global_theme.trame.default_mode = "client"

        self._dataset_changed()
        self._data_array_changed()
        self._time_index_changed()
        self._mesh_changed()

    def _on_ready(self, **kwargs):
        self.state.render_auto = True
        self._mesh_changed()

    def start(self, **kwargs):
        """Initialize the UI and start the server for the Viewer."""
        self.ui.server.start(**kwargs)

    @property
    async def ready(self) -> None:
        """Coroutine to wait for the Viewer server to be ready."""
        await self.ui.ready

    @property
    def state(self) -> State:
        """Returns the current State of the Trame server."""
        return self.server.state

    @property
    def ctrl(self) -> Controller:
        """Returns the Controller for the Trame server."""
        return self.server.controller

    @property
    def ui(self) -> VAppLayout:
        """Constructs and returns a Trame UI for managing and viewing the current data."""
        if self._ui is None:
            # Build UI
            self._ui = VAppLayout(self.server)
            with self._ui:
                client.Style(CSS_FILE.read_text())
                Toolbar(
                    self.apply_and_render,
                    self._submit_import,
                    self.builder.export_config,
                )
                MainDrawer(
                    update_catalog_search_term_function=self._update_catalog_search_term,
                    catalog_search_function=self._catalog_search,
                    catalog_term_search_function=self._catalog_term_option_search,
                    switch_data_group_function=self._switch_data_group,
                )
                AxisDrawer(
                    coordinate_select_axis_function=self._coordinate_select_axis,
                    coordinate_change_slice_function=self._coordinate_change_slice,
                    coordinate_toggle_expansion_function=self._coordinate_toggle_expansion,
                )
                with vuetify.VMain():
                    vuetify.VBanner(
                        "{{ ui_error_message }}",
                        v_show=("ui_error_message",),
                    )
                    with html.Div(
                        v_if=("da_active",), style="height: 100%; position: relative"
                    ):
                        RenderOptions()
                        with pyvista.trame.ui.plotter_ui(
                            self.ctrl.get_plotter(),
                            interactive_ratio=1,
                            collapse_menu=True,
                        ) as plot_view:
                            self.ctrl.view_update = plot_view.update
                            self.ctrl.reset_camera = plot_view.reset_camera
                            self.ctrl.push_camera = plot_view.push_camera
                            self.plot_view = plot_view
        return self._ui

    # -----------------------------------------------------
    # UI bound methods
    # -----------------------------------------------------
    def _update_catalog_search_term(self, term_key, term_value):
        self.state.catalog_current_search[term_key] = term_value
        self.state.dirty("catalog_current_search")

    def _catalog_search(self):
        def load_results():
            catalog_id = self.state.catalog.get("id")
            results, group_name, message = pan3d_catalogs.search(
                catalog_id, **self.state.catalog_current_search
            )

            if len(results) > 0:
                self.state.available_data_groups.append(
                    {"name": group_name, "value": group_name}
                )
                self.state.available_datasets[group_name] = results
                self.state.ui_catalog_search_message = message
                self.state.dirty("available_data_groups", "available_datasets")
            else:
                self.state.ui_catalog_search_message = (
                    "No results found for current search criteria."
                )

        self.run_as_async(
            load_results,
            loading_state="ui_catalog_term_search_loading",
            error_state="ui_catalog_search_message",
            unapplied_changes_state=None,
        )

    def _catalog_term_option_search(self):
        def load_terms():
            catalog_id = self.state.catalog.get("id")
            search_options = pan3d_catalogs.get_search_options(catalog_id)
            self.state.available_catalogs = [
                {
                    **catalog,
                    "search_terms": [
                        {"key": k, "options": v} for k, v in search_options.items()
                    ],
                }
                if catalog.get("id") == catalog_id
                else catalog
                for catalog in self.state.available_catalogs
            ]
            for catalog in self.state.available_catalogs:
                if catalog.get("id") == catalog_id:
                    self.state.catalog = catalog

        self.run_as_async(
            load_terms,
            loading_state="ui_catalog_term_search_loading",
            error_state="ui_catalog_search_message",
            unapplied_changes_state=None,
        )

    def _switch_data_group(self):
        # Setup from previous group needs to be cleared
        self.state.dataset_info = None
        self.state.da_attrs = {}
        self.state.da_vars = {}
        self.state.da_vars_attrs = {}
        self.state.da_coordinates = []
        self.state.ui_expanded_coordinates = []
        self.state.da_active = None
        self.state.da_x = None
        self.state.da_y = None
        self.state.da_z = None
        self.state.da_t = None
        self.state.da_t_index = 0
        self.plotter.clear()
        self.plotter.view_isometric()

    def _coordinate_select_axis(
        self, coordinate_name, current_axis, new_axis, **kwargs
    ):
        if current_axis and self.state[current_axis]:
            self.state[current_axis] = None
        if new_axis and new_axis != "undefined":
            self.state[new_axis] = coordinate_name

    def _coordinate_change_slice(self, coordinate_name, slice_attribute_name, value):
        try:
            value = float(value)
            coordinate_matches = [
                (index, coordinate)
                for index, coordinate in enumerate(self.state.da_coordinates)
                if coordinate["name"] == coordinate_name
            ]
            if len(coordinate_matches) > 0:
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
                self.state.dirty("da_coordinates")
        except Exception:
            pass

    def _coordinate_toggle_expansion(self, coordinate_name):
        if coordinate_name in self.state.ui_expanded_coordinates:
            self.state.ui_expanded_coordinates.remove(coordinate_name)
        else:
            self.state.ui_expanded_coordinates.append(coordinate_name)
        self.state.dirty("ui_expanded_coordinates")

    def _submit_import(self):
        def submit():
            files = self.state["ui_action_config_file"]
            if files and len(files) > 0:
                file_content = files[0]["content"]
                self.plotter.clear()
                self.plotter.view_isometric()

                self.builder.import_config(json.loads(file_content.decode()))
                self._mesh_changed()

        self.run_as_async(
            submit, loading_state="ui_import_loading", unapplied_changes_state=None
        )

    # -----------------------------------------------------
    # Rendering methods
    # -----------------------------------------------------

    def set_render_scales(self, **kwargs: Dict[str, str]) -> None:
        """Set the scales at which each axis (x, y, and/or z) should be rendered.

        Parameters:
            kwargs: A dictionary mapping of axis names to integer scales.\n
                Keys must be 'x' | 'y' | 'z'.\n
                Values must be integers > 0.
        """
        if "x" in kwargs and kwargs["x"] != self.state.render_x_scale:
            self.state.render_x_scale = int(kwargs["x"])
        if "y" in kwargs and kwargs["y"] != self.state.render_y_scale:
            self.state.render_y_scale = int(kwargs["y"])
        if "z" in kwargs and kwargs["z"] != self.state.render_z_scale:
            self.state.render_z_scale = int(kwargs["z"])
        self.plotter.set_scale(
            xscale=self.state.render_x_scale or 1,
            yscale=self.state.render_y_scale or 1,
            zscale=self.state.render_z_scale or 1,
        )

    def set_render_options(
        self,
        colormap: str = "viridis",
        transparency: bool = False,
        transparency_function: str = None,
        scalar_warp: bool = False,
    ) -> None:
        """Set available options for rendering data.

        Parameters:
            colormap: A colormap name from Matplotlib (https://matplotlib.org/stable/users/explain/colors/colormaps.html)
            transparency: If true, enable transparency and use transparency_function.
            transparency_function: One of PyVista's opacity transfer functions (https://docs.pyvista.org/version/stable/examples/02-plot/opacity.html#transfer-functions)
            scalar_warp: If true, warp the mesh proportional to its scalars.
        """
        if self.state.render_colormap != colormap:
            self.state.render_colormap = colormap
        if self.state.render_transparency != transparency:
            self.state.render_transparency = transparency
        if self.state.render_transparency_function != transparency_function:
            self.state.render_transparency_function = transparency_function
        if self.state.render_scalar_warp != scalar_warp:
            self.state.render_scalar_warp = scalar_warp

        if self.builder.mesh is not None and self.builder.data_array is not None:
            self.apply_and_render()

    def plot_mesh(self) -> None:
        """Render current cached mesh in viewer's plotter."""
        if self.builder.data_array is None:
            return

        self.plotter.clear()
        args = dict(
            cmap=self.state.render_colormap,
            clim=self.builder.data_range,
            scalar_bar_args=dict(interactive=True),
        )
        if self.state.render_transparency:
            args["opacity"] = self.state.render_transparency_function

        mesh = self.builder.mesh

        if self.state.render_scalar_warp:
            mesh = mesh.warp_by_scalar()
        self.actor = self.plotter.add_mesh(
            mesh,
            **args,
        )
        if len(self.builder.data_array.shape) > 2:
            self.plotter.view_isometric()
        else:
            self.plotter.view_xy()

        if self.plot_view:
            self.ctrl.push_camera()
            self.ctrl.view_update()

    def apply_and_render(self, **kwargs) -> None:
        """Asynchronously reset and update cached mesh and render to viewer's plotter."""

        self.run_as_async(self.plot_mesh)

    def run_as_async(
        self,
        function,
        loading_state="ui_loading",
        error_state="ui_error_message",
        unapplied_changes_state="ui_unapplied_changes",
    ):
        async def run():
            with self.state:
                if loading_state is not None:
                    self.state[loading_state] = True
                if error_state is not None:
                    self.state[error_state] = None
                if unapplied_changes_state is not None:
                    self.state[unapplied_changes_state] = False

            await asyncio.sleep(0.001)

            with self.state:
                try:
                    function()
                except Exception as e:
                    if error_state is not None:
                        self.state[error_state] = str(e)
                    else:
                        raise e
                if loading_state is not None:
                    self.state[loading_state] = False

        if self.current_event_loop.is_running():
            asyncio.run_coroutine_threadsafe(run(), self.current_event_loop)
        else:
            # Pytest environment needs synchronous execution
            function()

    # -----------------------------------------------------
    # State sync with Builder
    # -----------------------------------------------------
    def _dataset_changed(self) -> None:
        self.state.ui_more_info_link = None
        self.state.da_attrs = {}
        self.state.da_vars = {}
        self.state.da_vars_attrs = {}

        dataset = self.builder.dataset
        if dataset:
            if self._ui is not None:
                self.state.ui_main_drawer = True

            self.state.da_attrs = [
                {"key": str(k), "value": str(v)} for k, v in dataset.attrs.items()
            ]
            self.state.da_attrs.insert(
                0,
                {
                    "key": "dimensions",
                    "value": str(dict(dataset.sizes)),
                },
            )
            self.state.da_vars = [
                {"name": k, "id": i} for i, k in enumerate(dataset.data_vars.keys())
            ]
            self.state.da_vars_attrs = {
                var["name"]: [
                    {"key": str(k), "value": str(v)}
                    for k, v in dataset.data_vars[var["name"]].attrs.items()
                ]
                for var in self.state.da_vars
            }
            if len(self.state.da_vars) == 0:
                self.state.no_da_vars = True
            self.state.dataset_ready = True
        else:
            self.state.dataset_ready = False

    def _data_array_changed(self) -> None:
        dataset = self.builder.dataset
        da_name = self.builder.data_array_name
        self.state.da_coordinates = []
        self.state.ui_expanded_coordinates = []

        if dataset is None or da_name is None:
            return
        da = dataset[da_name]
        if len(da.dims) > 0 and self._ui is not None:
            self.state.ui_axis_drawer = True
        for key in da.dims:
            current_coord = da.coords[key]
            d = current_coord.dtype
            numeric = True
            array_min = current_coord.values.min()
            array_max = current_coord.values.max()

            # make content serializable by its type
            if d.kind in ["O", "M"]:  # is datetime
                if not hasattr(array_min, "strftime"):
                    array_min = pandas.to_datetime(array_min)
                if not hasattr(array_max, "strftime"):
                    array_max = pandas.to_datetime(array_max)
                array_min = array_min.strftime("%b %d %Y %H:%M")
                array_max = array_max.strftime("%b %d %Y %H:%M")
                numeric = False
            elif d.kind in ["m"]:  # is timedelta
                if not hasattr(array_min, "total_seconds"):
                    array_min = pandas.to_timedelta(array_min)
                if not hasattr(array_max, "total_seconds"):
                    array_max = pandas.to_timedelta(array_max)
                array_min = array_min.total_seconds()
                array_max = array_max.total_seconds()
            elif d.kind in ["i", "u"]:
                array_min = int(array_min)
                array_max = int(array_max)
            elif d.kind in ["f", "c"]:
                array_min = round(float(array_min), 2)
                array_max = round(float(array_max), 2)

            coord_attrs = [
                {"key": str(k), "value": str(v)}
                for k, v in da.coords[key].attrs.items()
            ]
            coord_attrs.append({"key": "dtype", "value": str(da.coords[key].dtype)})
            coord_attrs.append({"key": "length", "value": int(da.coords[key].size)})
            coord_attrs.append(
                {
                    "key": "range",
                    "value": [array_min, array_max],
                }
            )
            if key not in [c["name"] for c in self.state.da_coordinates]:
                coord_info = {
                    "name": key,
                    "numeric": numeric,
                    "attrs": coord_attrs,
                    "size": da.coords[key].size,
                    "range": [array_min, array_max],
                }
                coord_slicing = {
                    "start": array_min,
                    "stop": array_max,
                    "step": 1,
                }
                if self.builder.slicing and self.builder.slicing.get(key):
                    coord_slicing = dict(
                        zip(["start", "stop", "step"], self.builder.slicing.get(key))
                    )
                self.state.da_coordinates.append(dict(**coord_info, **coord_slicing))

            self.state.dirty("da_coordinates")
            self.plotter.clear()
            self.plotter.view_isometric()

    def _data_slicing_changed(self) -> None:
        if self.builder.slicing is None:
            return
        for coord in self.state.da_coordinates:
            slicing = self.builder.slicing.get(coord["name"])
            if slicing:
                coord.update(dict(zip(["start", "stop", "step"], slicing)))

    def _time_index_changed(self) -> None:
        dataset = self.builder.dataset
        da_name = self.builder.data_array_name
        t = self.builder.t
        t_index = self.builder.t_index
        if (
            dataset is not None
            and da_name is not None
            and t is not None
            and dataset[da_name] is not None
            and dataset[da_name][t] is not None
        ):
            d = dataset[da_name].coords[t].dtype
            time_steps = dataset[da_name][t]
            current_time = time_steps.values[t_index]

            if d.kind in ["O", "M"]:  # is datetime
                if not hasattr(current_time, "strftime"):
                    current_time = pandas.to_datetime(current_time)
                current_time = current_time.strftime("%b %d %Y %H:%M")
            elif d.kind in ["m"]:  # is timedelta
                if not hasattr(current_time, "total_seconds"):
                    current_time = pandas.to_timedelta(current_time)
                current_time = f"{current_time.total_seconds()} seconds"
            self.state.ui_current_time_string = str(current_time)

    def _mesh_changed(self) -> None:
        da = self.builder.data_array
        if da is None:
            self.state.da_size = 0
            self.state.ui_unapplied_changes = False
            return
        total_bytes = da.size * da.dtype.itemsize
        exponents_map = {0: "bytes", 1: "KB", 2: "MB", 3: "GB"}
        for exponent in sorted(exponents_map.keys(), reverse=True):
            divisor = 1024**exponent
            suffix = exponents_map[exponent]
            if total_bytes > divisor:
                self.state.da_size = f"{round(total_bytes / divisor)} {suffix}"
                break
        self.state.ui_unapplied_changes = True

        if self.state.render_auto:
            self.apply_and_render()

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------
    @change("ui_search_catalogs")
    def _on_change_ui_search_catalogs(self, ui_search_catalogs, **kwargs):
        if ui_search_catalogs:
            self.state.catalog = self.state.available_catalogs[0]
        else:
            self.state.catalog = None

    @change("catalog")
    def _on_change_catalog(self, catalog, **kwargs):
        self.state.catalog_current_search = {}
        self.state.ui_catalog_search_message = None

    @change("dataset_info")
    def _on_change_dataset_info(self, dataset_info, **kwargs):
        self.plotter.clear()
        self.plotter.view_isometric()

        if dataset_info is not None:
            dataset_exists = False
            for dataset_group in self.state.available_datasets.values():
                for d in dataset_group:
                    if d["value"] == dataset_info:
                        dataset_exists = True
                        self.state.ui_more_info_link = d.get("link")
            if not dataset_exists:
                self.state.available_data_groups = [
                    "default",
                    *self.state.available_data_groups,
                ]
                self.state.data_group = "default"
                self.state.available_datasets["default"] = [
                    {
                        "value": dataset_info,
                        "name": dataset_info["id"],
                    }
                ]
                self.state.dirty("available_datasets")

        def load_dataset():
            self.builder.dataset_info = dataset_info

        self.run_as_async(load_dataset, unapplied_changes_state=None)

    @change("da_active")
    def _on_change_da_active(self, da_active, **kwargs):
        self.builder.data_array_name = da_active

    @change("da_x")
    def _on_change_da_x(self, da_x, **kwargs):
        self.builder.x = da_x

    @change("da_y")
    def _on_change_da_y(self, da_y, **kwargs):
        self.builder.y = da_y

    @change("da_z")
    def _on_change_da_z(self, da_z, **kwargs):
        self.builder.z = da_z

    @change("da_t")
    def _on_change_da_t(self, da_t, **kwargs):
        self.builder.t = da_t

    @change("da_t_index")
    def _on_change_da_t_index(self, da_t_index, **kwargs):
        self.builder.t_index = da_t_index

    @change("da_coordinates")
    def _on_change_da_coordinates(self, da_coordinates, **kwargs):
        if len(da_coordinates) == 0:
            self.builder.slicing = None
        else:
            self.builder.slicing = {
                coord["name"]: [
                    coord["start"],
                    coord["stop"],
                    coord["step"],
                ]
                for coord in da_coordinates
            }

    @change("ui_action_name")
    def _on_change_action_name(self, ui_action_name, **kwargs):
        self.state.ui_action_message = None
        self.state.ui_action_config_file = None
        if ui_action_name == "Export":
            self.state.state_export = self.builder.export_config(None)

    @change("render_x_scale", "render_y_scale", "render_z_scale")
    def _on_change_render_scales(
        self, render_x_scale, render_y_scale, render_z_scale, **kwargs
    ):
        self.set_render_scales(
            x=int(render_x_scale), y=int(render_y_scale), z=int(render_z_scale)
        )

    @change(
        "render_colormap",
        "render_transparency",
        "render_transparency_function",
        "render_scalar_warp",
    )
    def _on_change_render_options(
        self,
        render_colormap,
        render_transparency,
        render_transparency_function,
        render_scalar_warp,
        **kwargs,
    ):
        self.set_render_options(
            colormap=render_colormap,
            transparency=render_transparency,
            transparency_function=render_transparency_function,
            scalar_warp=render_scalar_warp,
        )
