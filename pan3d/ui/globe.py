import math
from pathlib import Path

from trame.decorators import TrameApp, change
from trame.widgets import html, vuetify3 as v3

from pan3d import catalogs as pan3d_catalogs
from pan3d.utils.constants import XYZ, SLICE_VARS
from pan3d.utils.convert import max_str_length
from pan3d.utils.presets import PRESETS

from pan3d.ui.collapsible import CollapsableSection
from pan3d.ui.preview import DataOrigin, DataInformation


@TrameApp()
class RenderingSettings(CollapsableSection):
    def __init__(self, source, update_rendering):
        super().__init__("Rendering", "show_rendering")

        self.source = source
        self.state.setdefault("slice_extents", {})
        self.state.setdefault("axis_names", [])
        self.state.setdefault("t_labels", [])
        self.state.setdefault("max_time_width", 0)
        self.state.setdefault("max_time_index_width", 0)
        self.state.setdefault("dataset_bounds", [0, 1, 0, 1, 0, 1])

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
                text=("`Opacity: ${opacity.toFixed(2)}`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            classes="pr-3 ml-3",
                            prepend_icon="mdi-opacity",
                            v_model=("opacity", 1.0),
                            min=0.0,
                            max=1.0,
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
            with v3.VTooltip(
                text=("`Globe texture: ${texture}`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSelect(
                            placeholder="Globe Texture",
                            prepend_inner_icon="mdi-earth",
                            v_model=("texture", self.state.textures[0]),
                            items=("textures",),
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                    v3.VDivider()
            # X crop/cut
            with v3.VTooltip(
                v_if="axis_names?.[0]",
                text=(
                    "`${axis_names[0]}: [${dataset_bounds[0]}, ${dataset_bounds[1]}] ${slice_x_type ==='range' ? ('(' + slice_x_range.map((v,i) => v+1).concat(slice_x_step).join(', ') + ')'): slice_x_cut}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if="axis_names?.[0]",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if="slice_x_type === 'range'",
                            prepend_icon="mdi-axis-x-arrow",
                            v_model=("slice_x_range", [0, 1]),
                            min=("slice_extents[axis_names[0]][0]",),
                            max=("slice_extents[axis_names[0]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon="mdi-axis-x-arrow",
                            v_model=("slice_x_cut", 0),
                            min=("slice_extents[axis_names[0]][0]",),
                            max=("slice_extents[axis_names[0]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=("slice_x_type", "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )

            # Y crop/cut
            with v3.VTooltip(
                v_if="axis_names?.[1]",
                text=(
                    "`${axis_names[1]}: [${dataset_bounds[2]}, ${dataset_bounds[3]}] ${slice_y_type ==='range' ? ('(' + slice_y_range.map((v,i) => v+1).join(', ') + ', 1)'): slice_y_cut}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_if="axis_names?.[1]",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if="slice_y_type === 'range'",
                            prepend_icon="mdi-axis-y-arrow",
                            v_model=("slice_y_range", [0, 1]),
                            min=("slice_extents[axis_names[1]][0]",),
                            max=("slice_extents[axis_names[1]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon="mdi-axis-y-arrow",
                            v_model=("slice_y_cut", 0),
                            min=("slice_extents[axis_names[1]][0]",),
                            max=("slice_extents[axis_names[1]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=("slice_y_type", "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )

            # Z crop/cut
            with v3.VTooltip(
                v_if="axis_names?.[2]",
                text=(
                    "`${axis_names[2]}: [${dataset_bounds[4]}, ${dataset_bounds[5]}] ${slice_z_type ==='range' ? ('(' + slice_z_range.map((v,i) => v+1).join(', ') + ', 1)'): slice_z_cut}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex",
                        v_bind="props",
                    ):
                        v3.VRangeSlider(
                            v_if="slice_z_type === 'range'",
                            prepend_icon="mdi-axis-z-arrow",
                            v_model=("slice_z_range", [0, 1]),
                            min=("slice_extents[axis_names[2]][0]",),
                            max=("slice_extents[axis_names[2]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VSlider(
                            v_else=True,
                            prepend_icon="mdi-axis-z-arrow",
                            v_model=("slice_z_cut", 0),
                            min=("slice_extents[axis_names[2]][0]",),
                            max=("slice_extents[axis_names[2]][1]",),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VCheckbox(
                            v_model=("slice_z_type", "range"),
                            true_value="range",
                            false_value="cut",
                            true_icon="mdi-crop",
                            false_icon="mdi-box-cutter",
                            hide_details=True,
                            density="compact",
                            size="sm",
                            classes="mx-2",
                        )
                    v3.VDivider()

            # Slice steps
            with v3.VTooltip(text="Level Of Details / Slice stepping"):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VRow(
                        v_bind="props",
                        no_gutter=True,
                        classes="align-center my-0 mx-0 border-b-thin",
                    ):
                        v3.VIcon(
                            "mdi-stairs",
                            classes="ml-2 text-medium-emphasis",
                        )
                        with v3.VCol(classes="pa-0", v_if="axis_names?.[0]"):
                            v3.VTextField(
                                v_model_number=("slice_x_step", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=['min="1"'],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if="axis_names?.[1]"):
                            v3.VTextField(
                                v_model_number=("slice_y_step", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=['min="1"'],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if="axis_names?.[2]"):
                            v3.VTextField(
                                v_model_number=("slice_z_step", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=['min="1"'],
                                type="number",
                            )
            # Time slider
            with v3.VTooltip(
                v_if="slice_t_max > 0",
                text=("`time: ${t_labels[slice_t]} (${slice_t+1}/${slice_t_max+1})`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            prepend_icon="mdi-clock-outline",
                            v_model=("slice_t", 0),
                            min=0,
                            max=("slice_t_max", 0),
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                    v3.VDivider()
            v3.VBtn(
                "Update 3D view",
                block=True,
                classes="text-none",
                flat=True,
                density="compact",
                rounded=0,
                disabled=("data_arrays.length === 0",),
                color=("dirty_data && data_arrays.length ? 'primary': undefined",),
                click=(update_rendering, "[true]"),
            )

    def update_from_source(self, source=None):
        if source is None:
            source = self.source

        with self.state:
            self.state.data_arrays_available = source.available_arrays
            self.state.data_arrays = source.arrays
            self.state.color_by = self.state.data_arrays[0]
            self.state.axis_names = [source.x, source.y, source.z]
            self.state.slice_extents = source.slice_extents
            slices = source.slices
            for axis in XYZ:
                # default
                axis_extent = self.state.slice_extents.get(getattr(source, axis))
                self.state[f"slice_{axis}_range"] = axis_extent
                self.state[f"slice_{axis}_cut"] = 0
                self.state[f"slice_{axis}_step"] = 1
                self.state[f"slice_{axis}_type"] = "range"

                # use slice info if available
                axis_slice = slices.get(getattr(source, axis))
                if axis_slice is not None:
                    if isinstance(axis_slice, int):
                        # cut
                        self.state[f"slice_{axis}_cut"] = axis_slice
                        self.state[f"slice_{axis}_type"] = "cut"
                    else:
                        # range
                        self.state[f"slice_{axis}_range"] = [
                            axis_slice[0],
                            axis_slice[1] - 1,
                        ]  # end is inclusive
                        self.state[f"slice_{axis}_step"] = axis_slice[2]

            # Update time
            self.state.slice_t = source.t_index
            self.state.slice_t_max = source.t_size - 1
            self.state.t_labels = source.t_labels
            self.state.max_time_width = math.ceil(
                0.58 * max_str_length(self.state.t_labels)
            )
            if self.state.slice_t_max > 0:
                self.state.max_time_index_width = math.ceil(
                    0.6 + (math.log10(self.state.slice_t_max + 1) + 1) * 2 * 0.58
                )

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

    @change("slice_t", *[var.format(axis) for axis in XYZ for var in SLICE_VARS])
    def on_change(self, slice_t, **_):
        if self.state.import_pending:
            return

        slices = {self.source.t: slice_t}
        for axis in XYZ:
            axis_name = getattr(self.source, axis)
            if axis_name is None:
                continue

            if self.state[f"slice_{axis}_type"] == "range":
                slices[axis_name] = [
                    *self.state[f"slice_{axis}_range"],
                    int(self.state[f"slice_{axis}_step"]),
                ]
                slices[axis_name][1] += 1  # end is exclusive
            else:
                slices[axis_name] = self.state[f"slice_{axis}_cut"]

        self.source.slices = slices
        ds = self.source()
        self.state.dataset_bounds = ds.bounds

        self.ctrl.view_reset_clipping_range()
        self.ctrl.view_update()

    @change("slice_t")
    def _on_slice_t(self, slice_t, **_):
        if self.state.import_pending:
            return

        self.source.t_index = slice_t
        self.ctrl.view_update()

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


class ControlPanel(v3.VCard):
    def __init__(
        self,
        source,
        toggle,
        load_dataset,
        update_rendering,
        import_file_upload,
        export_file_download,
        xr_update_info="xr_update_info",
        source_update_rendering="source_update_rendering",
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
                    "Globe Exlorer",
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
                        with v3.VListItem(
                            title="Export state file",
                            disabled=("can_load",),
                            click=f"utils.download('xarray-state.json', trigger('{download_export}'), 'text/plain')",
                        ):
                            with html.Template(v_slot_prepend=True):
                                v3.VIcon("mdi-cloud-download-outline", classes="mr-n5")

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
            ):
                DataOrigin(load_dataset)
                self.ctrl[xr_update_info] = DataInformation().update_information
                self.ctrl[source_update_rendering] = RenderingSettings(
                    source,
                    update_rendering,
                ).update_from_source
