import math

from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.constants import XYZ
from pan3d.utils.convert import max_str_length
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class GlobeRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source

        with self.content:
            v3.VDivider()
            v3.VSelect(
                placeholder="Globe Texture",
                prepend_inner_icon="mdi-earth",
                v_model=("texture", self.state.textures[0]),
                items=("textures", []),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            v3.VSelect(
                placeholder="Data Representation",
                prepend_inner_icon=(
                    "['mdi-dots-triangle', 'mdi-triangle-outline','mdi-triangle'][representation]",
                ),
                v_model=("representation", 2),
                items=(
                    "representations",
                    [
                        {"title": "Surface", "value": 2},
                        {"title": "Wireframe", "value": 1},
                        {"title": "Points", "value": 0},
                    ],
                ),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            with v3.VTooltip(
                v_if="representation !== 2",
                text=(
                    "`${representation ? 'Line Size' : 'Point Size' }: ${cell_size} - Shadow: ${render_shadow ? 'On': 'Off'}`",
                ),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            classes="pr-3 ml-3",
                            prepend_icon="mdi-format-line-weight",
                            v_model=("cell_size", 1),
                            min=1,
                            max=100,
                            step=1,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                            click_prepend="render_shadow = !render_shadow",
                        )
            with v3.VTooltip(
                v_if="representation === 2",
                text=("`Opacity: ${opacity.toFixed(2)}`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            classes="pr-3 ml-3",
                            prepend_icon="mdi-circle-opacity",
                            v_model=("opacity", 1.0),
                            min=0.0,
                            max=1.0,
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )

            with v3.VTooltip(
                text=("`Bump Radius: ${bump_radius}`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            classes="pr-3 ml-3",
                            prepend_icon="mdi-signal-distance-variant",
                            v_model=("bump_radius", 10),
                            min=10,
                            max=1000,
                            step=10,
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
                            v_model=("slice_x_range", None),
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
                            v_model=("slice_y_range", None),
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
                            v_model=("slice_z_range", None),
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
            return

        with self.state as state:
            state.data_arrays_available = source.available_arrays
            state.data_arrays = source.arrays
            state.color_by = None
            state.axis_names = [source.x, source.y, source.z]
            state.slice_extents = source.slice_extents
            slices = source.slices
            for axis in XYZ:
                # default
                axis_extent = state.slice_extents.get(getattr(source, axis))
                state[f"slice_{axis}_range"] = axis_extent
                state[f"slice_{axis}_cut"] = 0
                state[f"slice_{axis}_step"] = 1
                state[f"slice_{axis}_type"] = "range"

                # use slice info if available
                axis_slice = slices.get(getattr(source, axis))
                if axis_slice is not None:
                    if isinstance(axis_slice, int):
                        # cut
                        state[f"slice_{axis}_cut"] = axis_slice
                        state[f"slice_{axis}_type"] = "cut"
                    else:
                        # range
                        state[f"slice_{axis}_range"] = [
                            axis_slice[0],
                            axis_slice[1] - 1,
                        ]  # end is inclusive
                        state[f"slice_{axis}_step"] = axis_slice[2]

            # Update time
            state.slice_t = source.t_index
            state.slice_t_max = source.t_size - 1
            state.t_labels = source.t_labels
            state.max_time_width = math.ceil(0.58 * max_str_length(state.t_labels))
            if state.slice_t_max > 0:
                state.max_time_index_width = math.ceil(
                    0.6 + (math.log10(state.slice_t_max + 1) + 1) * 2 * 0.58
                )
