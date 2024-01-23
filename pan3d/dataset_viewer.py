import pandas
import pyvista
from pathlib import Path
from typing import Union

from trame.decorators import TrameApp, change
from trame.app import get_server
from trame.widgets import html, client
from trame.widgets import vuetify3 as vuetify
from trame_server.core import Server
from trame_server.state import State
from trame_server.controller import Controller
from trame_vuetify.ui.vuetify3 import VAppLayout

from pan3d.dataset_builder import DatasetBuilder
from pan3d.ui import AxisDrawer, MainDrawer, Toolbar, RenderOptions
from pan3d.utils import (
    initial_state,
    has_gpu_rendering,
    run_singleton_task,
)

BASE_DIR = Path(__file__).parent
CSS_FILE = BASE_DIR / "ui" / "custom.css"

@TrameApp()
class DatasetViewer():
    """Create a Trame GUI for a DatasetBuilder instance and manage rendering"""
    def __init__(
        self,
        builder: DatasetBuilder,
        server: Union[Server, str] = None,
        state: dict = None,
        pangeo: bool = False,
    ) -> None:
        """Create an instance of the DatasetViewer class.

        Parameters:
            server: Trame server instance.
            state:  A dictionary of initial state values.
            pangeo: If true, use a list of example datasets from Pangeo Forge (examples/pangeo_catalog.json).
        """
        self.builder = builder
        self.server = get_server(server, client_type="vue3")
        self.state.update(initial_state)
        self._layout = None

        self.plotter = pyvista.Plotter(off_screen=True, notebook=False)
        self.plotter.set_background("lightgrey")
        self.actor = None

        self.ctrl.get_plotter = lambda: self.plotter
        self.ctrl.reset = self.apply_and_render

        if pangeo:
            with open(Path(BASE_DIR, "../examples/pangeo_catalog.json")) as f:
                self.state.available_datasets += json.load(f)

        if state:
            self.state.update(state)

        self._force_local_rendering = not has_gpu_rendering()
        if self._force_local_rendering:
            pyvista.global_theme.trame.default_mode = "client"

    def __repr_html__(self):
        return self.layout

    @property
    def state(self) -> State:
        """Returns the current State of the Trame server."""
        return self.server.state

    @property
    def ctrl(self) -> Controller:
        """Returns the Controller for the Trame server."""
        return self.server.controller

    @property
    def layout(self) -> VAppLayout:
        """Constructs and returns a Trame UI for managing and viewing the current data."""
        if self._layout is None:
            # Build UI
            self._layout = VAppLayout(self.server)
            with self._layout:
                client.Style(CSS_FILE.read_text())
                Toolbar(
                    self.ctrl.reset,
                    self.builder.import_config,
                    self.builder.export_config,
                )
                MainDrawer()
                AxisDrawer(
                    coordinate_select_axis_function=self._coordinate_select_axis,
                    coordinate_change_slice_function=self._coordinate_change_slice,
                    coordinate_toggle_expansion_function=self._coordinate_toggle_expansion,
                )
                with vuetify.VMain(v_if=("da_active",)):
                    vuetify.VBanner(
                        "{{ ui_error_message }}",
                        v_show=("ui_error_message",),
                    )
                    with html.Div(style="height: 100%; position: relative"):
                        RenderOptions()
                        with pyvista.trame.ui.plotter_ui(
                            self.ctrl.get_plotter(),
                            interactive_ratio=1,
                            collapse_menu=True,
                        ) as plot_view:
                            self.ctrl.view_update = plot_view.update
                            self.ctrl.reset_camera = plot_view.reset_camera
                            self.ctrl.push_camera = plot_view.push_camera
        return self._layout

    # -----------------------------------------------------
    # UI bound methods
    # -----------------------------------------------------

    def _coordinate_select_axis(
        self, coordinate_name, current_axis, new_axis, **kwargs
    ):
        if self.state[current_axis]:
            self.state[current_axis] = None
        if new_axis and new_axis != "undefined":
            self.state[new_axis] = coordinate_name

    def _coordinate_change_slice(self, coordinate_name, slice_attribute_name, value):
        if value.isnumeric():
            coordinate_matches = [
                (index, coordinate)
                for index, coordinate in enumerate(self.state.da_coordinates)
                if coordinate["name"] == coordinate_name
            ]
            if len(coordinate_matches) > 0:
                coord_i, coordinate = coordinate_matches[0]
                value = float(value)
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

    def _coordinate_toggle_expansion(self, coordinate_name):
        if coordinate_name in self.state.ui_expanded_coordinates:
            self.state.ui_expanded_coordinates.remove(coordinate_name)
        else:
            self.state.ui_expanded_coordinates.append(coordinate_name)
        self.state.dirty("ui_expanded_coordinates")

    # -----------------------------------------------------
    # Rendering methods
    # -----------------------------------------------------

    def set_render_scales(self, **kwargs) -> None:
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

        if self.builder.mesh is not None and self.data_array is not None:
            self.plot_mesh()

    async def plot_mesh(self) -> None:
        """Render current cached mesh in viewer's plotter."""
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
        self.plotter.view_isometric()
        self.ctrl.push_camera()
        self.ctrl.view_update()

    def apply_and_render(self, **kwargs) -> None:
        """Asynchronously reset and update cached mesh and render to viewer's plotter."""
        da = self.builder.data_array
        self.state.ui_error_message = None
        self.state.ui_loading = True
        self.state.ui_unapplied_changes = False

        self.plot_mesh()

        def mesh_updated(exception=None):
            with self.state:
                self.state.ui_error_message = (
                    str(exception) if exception is not None else None
                )
                self.state.ui_loading = False

        run_singleton_task(
            self.plot_mesh,
            mesh_updated,
            timeout=100,
            timeout_message="Failed to create mesh in under 100 seconds. Try reducing data size by slicing.",
        )

    # -----------------------------------------------------
    # State sync with Builder
    # -----------------------------------------------------
    def _dataset_changed(self) -> None:
        self.state.ui_more_info_link = None
        self.state.da_attrs = {}
        self.state.da_vars = {}
        self.state.da_vars_attrs = {}

        dataset_path = self.builder.dataset_path
        dataset = self.builder.dataset
        if dataset:
            self.state.ui_loading = True
            for available_dataset in self.state.available_datasets:
                if (
                    available_dataset["url"] == dataset_path
                    and "more_info" in available_dataset
                ):
                    self.state.ui_more_info_link = available_dataset["more_info"]
            self.state.da_attrs = [
                {"key": k, "value": v} for k, v in dataset.attrs.items()
            ]
            self.state.da_attrs.insert(
                0,
                {
                    "key": "dimensions",
                    "value": str(dict(dataset.dims)),
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

    def _data_array_changed(self) -> None:
        dataset = self.builder.dataset
        da_name = self.builder.data_array_name
        da = dataset[da_name]
        self.state.update(
            dict(
                da_active=da_name,
                da_x=None,
                da_y=None,
                da_z=None,
                da_t=None,
                da_t_index=0,
                da_coordinates=[],
                ui_expanded_coordinates=[],
                ui_error_message=None,
                ui_axis_drawer=False,
                ui_current_time_string="",
            )
        )
        for key in da.dims:
            current_coord = da.coords[key]
            d = current_coord.dtype
            numeric = True
            array_min = current_coord.values.min()
            array_max = current_coord.values.max()

            # make content serializable by its type
            if d.kind in ["m", "M", "O"]:  # is timedelta or datetime
                if not hasattr(array_min, "strftime"):
                    array_min = pandas.to_datetime(array_min)
                if not hasattr(array_max, "strftime"):
                    array_max = pandas.to_datetime(array_max)
                array_min = array_min.strftime("%b %d %Y %H:%M")
                array_max = array_max.strftime("%b %d %Y %H:%M")
                numeric = False
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
                self.state.da_coordinates.append(
                    {
                        "name": key,
                        "numeric": numeric,
                        "attrs": coord_attrs,
                        "size": da.coords[key].size,
                        "range": [array_min, array_max],
                        "start": array_min,
                        "stop": array_max,
                        "step": 1,
                    }
                )
            if key not in self.state.ui_expanded_coordinates:
                self.state.ui_expanded_coordinates.append(key)

            self.state.dirty("da_coordinates", "ui_expanded_coordinates")
            if len(self.state.da_coordinates) > 0:
                self.state.ui_axis_drawer = True

            self.plotter.clear()
            self.plotter.view_isometric()

    def _time_index_changed(self) -> None:
        dataset = self.builder.dataset
        da_name = self.builder.data_array_name
        t = self.builder.t
        t_index = self.builder.t_index
        if (
            dataset is not None and
            da_name is not None and
            t is not None and
            dataset[da_name] is not None and
            dataset[da_name][t] is not None
        ):
            time_steps = dataset[da_name][t]
            current_time = time_steps.values[t_index]
            if not hasattr(current_time, "strftime"):
                current_time = pandas.to_datetime(current_time)
            self.state.ui_current_time_string = current_time.strftime("%b %d %Y %H:%M")

    def _mesh_changed(self) -> None:
        total_bytes = 0
        da = self.builder.data_array
        if da is not None:
            total_bytes = da.size * da.dtype.itemsize
        exponents_map = {0: "bytes", 1: "KB", 2: "MB", 3: "GB"}
        for exponent in sorted(exponents_map.keys(), reverse=True):
            divisor = 1024**exponent
            suffix = exponents_map[exponent]
            if total_bytes > divisor:
                self.state.da_size = f"{round(total_bytes / divisor)} {suffix}"
                break
        self.state.ui_unapplied_changes = True
        self.state.ui_loading = False

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------
    @change("dataset_path")
    def _on_change_dataset_path(self, dataset_path, **kwargs):
        self.builder.dataset_path = dataset_path
        self._mesh_changed()

    @change("da_active")
    def _on_change_da_active(self, da_active, **kwargs):
        self.builder.data_array_name = da_active
        self._mesh_changed()

    @change("da_x", "da_y", "da_z", "da_t")
    def _on_change_axis_assignment(self, da_x, da_y, da_z, da_t, **kwargs):
        self.builder.x = da_x
        self.builder.y = da_y
        self.builder.z = da_z
        self.builder.t = da_t
        self._mesh_changed()

    @change("da_t_index")
    def _on_change_da_t_index(self, da_t_index, **kwargs):
        self.builder.t_index = da_t_index
        self._mesh_changed()

    @change("da_coordinates")
    def _on_change_da_coordinates(self, da_coordinates, **kwargs):
        self.builder.slicing = {
            coord['name']: [
                coord['start'],
                coord['stop'],
                coord['step'],
            ] for coord in da_coordinates
        }
        self._mesh_changed()

    @change("ui_action_name")
    def _on_change_action_name(self, ui_action_name, **kwargs):
        self.state.ui_action_message = None
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
