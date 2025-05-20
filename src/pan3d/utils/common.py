import json
import traceback
from pathlib import Path

from trame.decorators import TrameApp, change
from trame.app import get_server, asynchronous

from trame.widgets import vuetify3 as v3, html

from pan3d import catalogs as pan3d_catalogs

from pan3d.utils.convert import update_camera

from pan3d.ui.collapsible import CollapsableSection
from pan3d.utils.presets import PRESETS

from pan3d.ui.css import base, preview


@TrameApp()
class Explorer:
    def __init__(self, xarray=None, source=None, server=None, local_rendering=None):
        """
        Parameters:
            server (str/server): Trame server name or instance.
            local_rendering (str): If provided (wasm, vtkjs) local rendering will be used

        CLI options:
            - `--import-state`: Pass a string with this argument to specify a startup configuration.
                              This value must be a local path to a JSON file which adheres to the
                              schema specified in the [Configuration Files documentation](../api/configuration.md).
                              A dataset specified in this configuration will override any value passed to `--xarray-*`
            - `--xarray-file`: Provide path to xarray file
            - `--xarray-url`: Provide URL to xarray dataset
            - `--wasm`: Use WASM for local rendering
            - `--vtkjs`: Use vtk.js for local rendering
        """
        self.server = get_server(server, client_type="vue3")

        parser = self.server.cli
        explorer = parser.add_argument_group("Explorer Properties")
        explorer.add_argument(
            "--import-state",
            help="Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the [Configuration Files documentation](../api/configuration.md). A dataset specified in this configuration will override any value passed to `--xarray-*`",
        )
        explorer.add_argument(
            "--xarray-file",
            help="Provide path to xarray file",
        )
        explorer.add_argument(
            "--xarray-url",
            help="Provide URL to xarray dataset",
        )

        rendering = parser.add_argument_group("Rendering Properties")
        # Local rendering setup
        rendering.add_argument(
            "--wasm",
            help="Use WASM for local rendering",
            action="store_true",
        )
        rendering.add_argument(
            "--vtkjs",
            help="Use vtk.js for local rendering",
            action="store_true",
        )

        # CLI
        args, _ = self.server.cli.parse_known_args()
        # Local rendering
        self.local_rendering = local_rendering
        if args.wasm:
            self.local_rendering = "wasm"
        if args.vtkjs:
            self.local_rendering = "vtkjs"

        self.state.nan_colors = [
            [0, 0, 0, 1],
            [0.99, 0.99, 0.99, 1],
            [0.6, 0.6, 0.6, 1],
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 1],
            [0.9, 0.9, 0.9, 0],
        ]
        self.state.nan_color = 2

        self.ui = None

        # Process CLI
        self.ctrl.on_server_ready.add(self._process_cli)

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    def _process_cli(self, **_):
        args, _ = self.server.cli.parse_known_args()

        # import state
        if args.import_state:
            self._import_file_from_path(args.import_state)

        # load xarray (file)
        elif args.xarray_file:
            self.state.import_pending = True
            with self.state:
                self.load_dataset("file", args.xarray_file)
                self.state.data_origin_id = str(Path(args.xarray_file).resolve())
            self.state.import_pending = False

        # load xarray (url)
        elif args.xarray_url:
            self.state.import_pending = True
            with self.state:
                self.load_dataset("url", args.xarray_url)
                self.state.data_origin_id = args.xarray_url
            self.state.import_pending = False

        # Load given XArray
        elif self.xarray is not None:
            self.state.show_data_information = True
            self.ctrl.xr_update_info(self.source.input, self.source.available_arrays)
            self.ctrl.source_update_rendering_panel(self.source)

    def start(self, **kwargs):
        """Initialize the UI and start the server for XArray Viewer."""
        self.ui.server.start(**kwargs)

    @property
    async def ready(self):
        """Start and wait for the XArray Viewer corroutine to be ready."""
        await self.ui.ready

    @property
    def state(self):
        """Returns the current the trame server state."""
        return self.server.state

    @property
    def ctrl(self):
        """Returns the Controller for the trame server."""
        return self.server.controller

    @change("data_origin_order")
    def _on_order_change(self, **_):
        if self.state.import_pending:
            return

        self.state.load_button_text = "Load"
        self.state.can_load = True

    @change("data_origin_source")
    def _on_data_origin_source(self, data_origin_source, **kwargs):
        if self.state.import_pending:
            return

        self.state.data_origin_id = ""
        results, *_ = pan3d_catalogs.search(data_origin_source)
        self.state.data_origin_ids = [v["name"] for v in results]
        self.state.data_origin_id_to_desc = {
            v["name"]: v["description"] for v in results
        }

    @change("data_origin_id")
    def _on_data_origin_id(self, data_origin_id, data_origin_source, **kwargs):
        if self.state.import_pending:
            return

        self.state.load_button_text = "Load"
        self.state.can_load = True

        if data_origin_source == "file":
            self.state.data_origin_id_error = not Path(data_origin_id).exists()
        elif self.state.data_origin_id_error:
            self.state.data_origin_id_error = False

    # -----------------------------------------------------
    # Triggers
    # -----------------------------------------------------

    def import_file_upload(self, files):
        self.import_state(json.loads(files[0].get("content")))

    def _import_file_from_path(self, file_path):
        if file_path is None:
            return

        file_path = Path(file_path)
        if file_path.exists():
            self.import_state(json.loads(file_path.read_text("utf-8")))

    def load_dataset(self, source, id, order="C", config=None):
        self.state.data_origin_source = source
        self.state.data_origin_id = id
        self.state.load_button_text = "Loaded"
        self.state.can_load = False
        self.state.show_data_information = True

        if config is None:
            config = {
                "arrays": [],
                "slices": {},
            }

        try:
            self.source.load(
                {
                    "data_origin": {
                        "source": source,
                        "id": id,
                        "order": order,
                    },
                    "dataset_config": config,
                }
            )

            # Extract UI
            self.ctrl.xr_update_info(self.source.input, self.source.available_arrays)
            self.ctrl.source_update_rendering_panel(self.source)

            # no error
            self.state.data_origin_error = False
        except Exception as e:
            self.state.data_origin_error = (
                f"Error occurred while trying to load data. {e}"
            )
            self.state.data_origin_id_error = True
            self.state.load_button_text = "Load"
            self.state.can_load = True
            self.state.show_data_information = False

            print(traceback.format_exc())

    def update_rendering(self, reset_camera=False):
        raise NotImplementedError(
            """
            This method is supposed to be implemented by the Explorer.
            Please override this in the necessary Explorer class if you see this message
            """
        )

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def export_state(self, **kwargs):
        """Return a json dump of the reader and viewer state"""
        camera = self.renderer.active_camera
        state_to_export = {
            **self.source.state,
            "rendering": {
                "view_3d": self.state.view_3d,
                "color_by": self.state.color_by,
                "color_preset": self.state.color_preset,
                "color_min": self.state.color_min,
                "color_max": self.state.color_max,
                "scale_x": self.state.scale_x,
                "scale_y": self.state.scale_y,
                "scale_z": self.state.scale_z,
            },
            "camera": {
                "position": camera.position,
                "view_up": camera.view_up,
                "focal_point": camera.focal_point,
                "parallel_projection": camera.parallel_projection,
                "parallel_scale": camera.parallel_scale,
            },
            **kwargs,
        }
        return json.dumps(state_to_export, indent=2)

    def import_state(self, data_state):
        """
        Read the current state to load the data and visualization setup if any.

        Parameters:
            - data_state (dict): reader (+viewer) state to reset to
        """
        self.state.import_pending = True
        try:
            data_origin = data_state.get("data_origin")
            source = data_origin.get("source")
            id = data_origin.get("id")
            order = data_origin.get("order", "C")
            config = data_state.get("dataset_config")
            rendering_state = data_state.get("rendering", {})
            camera_state = data_state.get("camera", {})

            # load data and initial rendering setup
            with self.state:
                self.load_dataset(source, id, order, config)
                self.state.update(rendering_state)

            # override computed color range using state values
            with self.state:
                self.state.update(rendering_state)

            # update camera and render
            update_camera(self.renderer.active_camera, camera_state)
            self.update_rendering()
        finally:
            self.state.import_pending = False

    async def _save_dataset(self, file_path):
        output_path = Path(file_path).resolve()
        self.source.input.to_netcdf(output_path)

    def save_dataset(self, file_path):
        """
        Write XArray data into a file using a background task.
        So when used programmatically, make sure you await the returned task.

        Parameters:
            - file_path (str): path to use for writing the file

        Returns:
            writing task
        """
        self.state.show_save_dialog = False
        return asynchronous.create_task(self._save_dataset(file_path))

    async def _async_display(self):
        await self.ui.ready
        self.ui._ipython_display_()

    def _ipython_display_(self):
        asynchronous.create_task(self._async_display())


class SummaryToolbar(v3.VCard):
    def __init__(
        self,
        t_labels="t_labels",
        slice_t="slice_t",
        slice_t_max="slice_t_max",
        color_by="color_by",
        data_arrays="data_arrays",
        max_time_width="max_time_width",
        max_time_index_width="max_time_index_width",
        **kwargs,
    ):
        super().__init__(
            classes="summary-toolbar",
            rounded="pill",
            **kwargs,
        )

        # Activate CSS
        self.server.enable_module(base)
        self.server.enable_module(preview)

        with self:
            with v3.VToolbar(
                classes="pl-2",
                height=50,
                elevation=1,
                style="background: none;",
            ):
                v3.VIcon("mdi-clock-outline")
                html.Pre(
                    f"{{{{ {t_labels}[slice_t] }}}}",
                    classes="mx-2 text-left",
                    style=(f"`min-width: ${{ {max_time_width} }}rem;`",),
                )
                v3.VSlider(
                    prepend_inner_icon="mdi-clock-outline",
                    v_model=(slice_t, 0),
                    min=0,
                    max=(slice_t_max, 0),
                    step=1,
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
                    classes="mx-2",
                )
                html.Div(
                    f"{{{{ {slice_t} + 1 }}}}/{{{{ {slice_t_max} + 1 }}}}",
                    classes="mx-2 text-right",
                    style=(f"`min-width: ${{ {max_time_index_width} }}rem;`",),
                )
                v3.VSelect(
                    placeholder="Color By",
                    prepend_inner_icon="mdi-format-color-fill",
                    v_model=(color_by, None),
                    items=(data_arrays, []),
                    clearable=True,
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
                    max_width=200,
                )


class DataOrigin(CollapsableSection):
    def __init__(self, load_dataset):
        super().__init__("Data origin", "show_data_origin", True)

        self.state.load_button_text = "Load"
        self.state.can_load = True
        self.state.data_origin_id_to_desc = {}

        with self.content:
            v3.VSelect(
                label="Source",
                v_model=("data_origin_source", "xarray"),
                items=(
                    "data_origin_sources",
                    pan3d_catalogs.list_availables(),
                ),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            v3.VTextField(
                placeholder="Location",
                v_if="['file', 'url'].includes(data_origin_source)",
                v_model=("data_origin_id", ""),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
                append_inner_icon=(
                    "data_origin_id_error ? 'mdi-file-document-alert-outline' : undefined",
                ),
                error=("data_origin_id_error", False),
            )

            with v3.VTooltip(
                v_else=True,
                text=("`${ data_origin_id_to_desc[data_origin_id] }`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VSelect(
                        v_bind="props",
                        label="Name",
                        v_model="data_origin_id",
                        items=("data_origin_ids", []),
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )

            # v3.VDivider()
            # v3.VSwitch(
            #     label=("`Order ${data_origin_order}`",),
            #     v_model=("data_origin_order", "C"),
            #     true_value="C",
            #     false_value="F",
            #     hide_details=True,
            #     density="compact",
            #     flat=True,
            #     variant="solo",
            #     classes="mx-6",
            # )
            v3.VDivider()
            v3.VBtn(
                "{{ load_button_text }}",
                block=True,
                classes="text-none",
                flat=True,
                density="compact",
                rounded=0,
                disabled=("!data_origin_id?.length || !can_load",),
                color=("can_load ? 'primary': undefined",),
                click=(
                    load_dataset,
                    "[data_origin_source, data_origin_id, data_origin_order]",
                ),
            )


class DataInformation(CollapsableSection):
    def __init__(self, xarray_info="xarray_info"):
        super().__init__("Data information", "show_data_information")

        self._var_name = xarray_info
        self.state.setdefault(xarray_info, [])

        with self.content:
            with v3.VTable(density="compact", hover=True):
                with html.Tbody():
                    with html.Template(v_for=f"item, i in {xarray_info}", key="i"):
                        with v3.VTooltip():
                            with html.Template(v_slot_activator="{ props }"):
                                with html.Tr(v_bind="props", classes="pointer"):
                                    with html.Td(
                                        classes="d-flex align-center text-no-wrap"
                                    ):
                                        v3.VIcon(
                                            "{{ item.icon }}",
                                            size="sm",
                                            classes="mr-2",
                                        )
                                        html.Div("{{ item.name }}")
                                    html.Td(
                                        "{{ item.length }}",
                                        classes="text-right",
                                    )

                            with v3.VTable(
                                density="compact",
                                theme="dark",
                                classes="no-bg ma-0 pa-0",
                            ):
                                with html.Tbody():
                                    with html.Tr(
                                        v_for="attr, j in item.attrs",
                                        key="j",
                                    ):
                                        html.Td(
                                            "{{ attr.key }}",
                                        )
                                        html.Td(
                                            "{{ attr.value }}",
                                        )

    def update_information(self, xr, available_arrays=None):
        xarray_info = []
        coords = set(xr.coords.keys())
        data = set(available_arrays or [])
        for name in xr.variables:
            icon = "mdi-variable"
            order = 3
            length = f'({",".join(xr[name].dims)})'
            attrs = []
            if name in coords:
                icon = "mdi-ruler"
                order = 1
                length = xr[name].size
                shape = xr[name].shape
                if length > 1 and len(shape) == 1:
                    attrs.append(
                        {
                            "key": "range",
                            "value": f"[{xr[name].values[0]}, {xr[name].values[-1]}]",
                        }
                    )
            if name in data:
                icon = "mdi-database"
                order = 2
            xarray_info.append(
                {
                    "order": order,
                    "icon": icon,
                    "name": name,
                    "length": length,
                    "type": str(xr[name].dtype),
                    "attrs": attrs
                    + [
                        {"key": "type", "value": str(xr[name].dtype)},
                    ]
                    + [
                        {"key": str(k), "value": str(v)}
                        for k, v in xr[name].attrs.items()
                    ],
                }
            )
        xarray_info.sort(key=lambda item: item["order"])

        # Update UI
        self.state[self._var_name] = xarray_info


class ControlPanel(v3.VCard):
    def __init__(
        self,
        enable_data_selection,
        toggle,
        load_dataset,
        import_file_upload,
        export_file_download,
        xr_update_info="xr_update_info",
        panel_label="XArray Viewer",
        **kwargs,
    ):
        super().__init__(
            classes="controller",
            rounded=(f"{toggle} || 'circle'",),
            **kwargs,
        )

        # state initialization
        self.state.import_pending = False

        # extract trigger name
        download_export = self.ctrl.trigger_name(export_file_download)

        with self:
            with v3.VCardTitle(
                classes=(
                    f"`d-flex pa-1 position-fixed bg-white ${{ {toggle} ? 'controller-content rounded-t border-b-thin':'rounded-circle'}}`",
                ),
                style="z-index: 1;",
            ):
                v3.VProgressLinear(
                    v_if=toggle,
                    indeterminate=("trame__busy",),
                    bg_color="rgba(0,0,0,0)",
                    absolute=True,
                    color="primary",
                    location="bottom",
                    height=2,
                )
                v3.VProgressCircular(
                    v_else=True,
                    bg_color="rgba(0,0,0,0)",
                    indeterminate=("trame__busy",),
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;",
                    color="primary",
                    width=3,
                )
                v3.VBtn(
                    icon="mdi-close",
                    v_if=toggle,
                    click=f"{toggle} = !{toggle}",
                    flat=True,
                    size="sm",
                )
                v3.VBtn(
                    icon="mdi-menu",
                    v_else=True,
                    click=f"{toggle} = !{toggle}",
                    flat=True,
                    size="sm",
                )
                if self.server.hot_reload:
                    v3.VBtn(
                        v_show=toggle,
                        icon="mdi-refresh",
                        flat=True,
                        size="sm",
                        click=self.ctrl.on_server_reload,
                    )
                v3.VSpacer()
                html.Div(
                    panel_label,
                    v_show=toggle,
                    classes="text-h6 px-2",
                )
                v3.VSpacer()

                with v3.VMenu(v_if=toggle, density="compact"):
                    with html.Template(v_slot_activator="{props}"):
                        v3.VBtn(
                            v_bind="props",
                            icon="mdi-file-arrow-left-right-outline",
                            flat=True,
                            size="sm",
                            classes="mx-1",
                        )
                    with v3.VList(density="compact"):
                        if enable_data_selection:
                            with v3.VListItem(
                                title="Export state file",
                                disabled=("can_load",),
                                click=f"utils.download('xarray-state.json', trigger('{download_export}'), 'text/plain')",
                            ):
                                with html.Template(v_slot_prepend=True):
                                    v3.VIcon(
                                        "mdi-cloud-download-outline", classes="mr-n5"
                                    )

                        with v3.VListItem(
                            title="Import state file",
                            click="trame.utils.get('document').querySelector('#fileImport').click()",
                        ):
                            html.Input(
                                id="fileImport",
                                hidden=True,
                                type="file",
                                change=(
                                    import_file_upload,
                                    "[$event.target.files]",
                                ),
                                __events=["change"],
                            )
                            with html.Template(v_slot_prepend=True):
                                v3.VIcon("mdi-cloud-upload-outline", classes="mr-n5")
                        v3.VDivider()
                        with v3.VListItem(
                            title="Save dataset to disk",
                            disabled=("can_load",),
                            click="show_save_dialog = true",
                        ):
                            with html.Template(v_slot_prepend=True):
                                v3.VIcon("mdi-file-download-outline", classes="mr-n5")

            with v3.VCardText(
                v_show=(toggle, True),
                classes="controller-content py-1 mt-10",
            ) as ui_content:
                self.ui_content = ui_content
                if enable_data_selection:
                    DataOrigin(load_dataset)
                self.ctrl[xr_update_info] = DataInformation().update_information


@TrameApp()
class RenderingSettingsBasic(CollapsableSection):
    def __init__(self, source, update_rendering):
        super().__init__("Rendering", "show_rendering")

        self.source = source
        with self.content:
            v3.VSelect(
                placeholder="Data arrays",
                prepend_inner_icon="mdi-database",
                hide_selected=True,
                v_model=("data_arrays", []),
                items=("data_arrays_available", []),
                multiple=True,
                hide_details=True,
                density="compact",
                chips=True,
                closable_chips=True,
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            v3.VSelect(
                placeholder="Color By",
                prepend_inner_icon="mdi-format-color-fill",
                v_model=("color_by", None),
                items=("data_arrays", []),
                clearable=True,
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            with v3.VRow(no_gutters=True, classes="align-center mr-0"):
                with v3.VCol():
                    v3.VTextField(
                        prepend_inner_icon="mdi-water-minus",
                        v_model_number=("color_min", 0.45),
                        type="number",
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                        reverse=True,
                    )
                with v3.VCol():
                    v3.VTextField(
                        prepend_inner_icon="mdi-water-plus",
                        v_model_number=("color_max", 5.45),
                        type="number",
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                        reverse=True,
                    )
                with html.Div(classes="flex-0"):
                    v3.VBtn(
                        icon="mdi-arrow-split-vertical",
                        size="sm",
                        density="compact",
                        flat=True,
                        variant="outlined",
                        classes="mx-2",
                        click=self.reset_color_range,
                    )
            # v3.VDivider()
            with html.Div(classes="mx-2"):
                html.Img(
                    src=("preset_img", None),
                    style="height: 0.75rem; width: 100%;",
                    classes="rounded-lg border-thin",
                )
            v3.VSelect(
                placeholder="Color Preset",
                prepend_inner_icon="mdi-palette",
                v_model=("color_preset", "Fast"),
                items=("color_presets", list(PRESETS.keys())),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )

            with v3.VTooltip(
                text=("`NaN Color (${nan_colors[nan_color]})`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VItemGroup(
                        v_model="nan_color",
                        v_bind="props",
                        classes="d-inline-flex ga-1 pa-2",
                        mandatory="force",
                    ):
                        v3.VIcon(
                            "mdi-eyedropper-variant",
                            classes="my-auto mx-1 text-medium-emphasis",
                        )
                        with v3.VItem(
                            v_for="(color, i) in nan_colors", key="i", value=("i",)
                        ):
                            with v3.Template(
                                raw_attrs=['#default="{ isSelected, toggle }"']
                            ):
                                with v3.VAvatar(
                                    density="compact",
                                    color=("isSelected ? 'primary': 'transparent'",),
                                ):
                                    v3.VBtn(
                                        "{{ color[3] < 0.1 ? 't' : '' }}",
                                        density="compact",
                                        border="md surface opacity-100",
                                        color=(
                                            "color[3] ? `rgb(${color[0] * 255}, ${color[1] * 255}, ${color[2] * 255})` : undefined",
                                        ),
                                        flat=True,
                                        icon=True,
                                        ripple=False,
                                        size="small",
                                        click="toggle",
                                    )

    @change("data_arrays")
    def _on_array_selection(self, data_arrays, **_):
        if self.state.import_pending:
            return

        self.state.dirty_data = True
        if len(data_arrays) == 1:
            self.state.color_by = data_arrays[0]
        elif len(data_arrays) == 0:
            self.state.color_by = None

        self.source.arrays = data_arrays

    def reset_color_range(self):
        color_by = self.state.color_by
        ds = self.source()
        if color_by in ds.point_data.keys():
            array = ds.point_data[color_by]
            min_value, max_value = array.GetRange()

            self.state.color_min = min_value
            self.state.color_max = max_value
        else:
            self.state.color_min = 0
            self.state.color_max = 1

    def update_from_source(self, source=None):
        raise NotImplementedError(
            """
            This method needs to be implemented in the specialization of this class.
            Please override it in the necessary class representing the rendering settings for the Explorer.
            """
        )
