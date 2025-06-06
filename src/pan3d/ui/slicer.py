import math

from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.convert import max_str_length
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class SliceRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source

        style = {"density": "compact", "hide_details": True}
        with self.content:
            # -- Slice section
            v3.VDivider()
            with v3.VRow(classes="mx-2 my-0 align-center"):
                html.Span("Slice", classes="text-h6 font-weight-medium")
                v3.VSpacer()
                html.Span(
                    "{{parseFloat(cut_x).toFixed(2)}}",
                    v_show="slice_axis === axis_names[0]",
                    classes="text-subtitle-1",
                )
                html.Span(
                    "{{parseFloat(cut_y).toFixed(2)}}",
                    v_show="slice_axis === axis_names[1]",
                    classes="text-subtitle-1",
                )
                html.Span(
                    "{{parseFloat(cut_z).toFixed(2)}}",
                    v_show="slice_axis === axis_names[2]",
                    classes="text-subtitle-1",
                )
            with v3.VRow(classes="mx-2 my-0"):
                v3.VSelect(
                    v_model=("slice_axis",),
                    items=("axis_names",),
                    **style,
                )
            with v3.VRow(classes="mx-2 my-0"):
                v3.VSlider(
                    v_show="slice_axis === axis_names[0]",
                    v_model=("cut_x",),
                    min=("bounds[0]",),
                    max=("bounds[1]",),
                    **style,
                )
                v3.VSlider(
                    v_show="slice_axis === axis_names[1]",
                    v_model=("cut_y",),
                    min=("bounds[2]",),
                    max=("bounds[3]",),
                    **style,
                )
                v3.VSlider(
                    v_show="slice_axis === axis_names[2]",
                    v_model=("cut_z",),
                    min=("bounds[4]",),
                    max=("bounds[5]",),
                    **style,
                )

            with v3.VRow(classes="mx-2 my-0"):
                with v3.VCol():
                    html.Div(
                        "{{parseFloat(bounds[axis_names.indexOf(slice_axis)*2]).toFixed(2)}}",
                        classes="font-weight-medium",
                    )
                with v3.VCol(classes="text-right"):
                    html.Div(
                        "{{parseFloat(bounds[axis_names.indexOf(slice_axis)*2 + 1]).toFixed(2)}}",
                        classes="font-weight-medium",
                    )

            v3.VDivider()
            # Actor scaling
            with v3.VTooltip(text="Representation scaling"):
                with html.Template(v_slot_activator="{ props }"):
                    with v3.VRow(
                        v_bind="props",
                        no_gutter=True,
                        classes="align-center my-0 mx-0 border-b-thin",
                    ):
                        v3.VIcon(
                            "mdi-ruler-square",
                            classes="ml-2 text-medium-emphasis",
                        )
                        with v3.VCol(classes="pa-0", v_if="axis_names?.[0]"):
                            v3.VTextField(
                                v_model=("scale_x", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[
                                    'pattern="^\d*(\.\d)?$"',
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if="axis_names?.[1]"):
                            v3.VTextField(
                                v_model=("scale_y", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[
                                    'pattern="^\d*(\.\d)?$"',
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )
                        with v3.VCol(classes="pa-0", v_if="axis_names?.[2]"):
                            v3.VTextField(
                                v_model=("scale_z", 1),
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                                raw_attrs=[
                                    'pattern="^\d*(\.\d)?$"',
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )
            v3.VDivider()
            # Time slider
            with v3.VTooltip(
                v_if="slice_t_max > 0",
                text=("`time: ${slice_t + 1} / ${slice_t_max+1}`",),
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

        ds = source()
        bounds = ds.bounds
        origin = [
            0.5 * (bounds[0] + bounds[1]),
            0.5 * (bounds[2] + bounds[3]),
            0.5 * (bounds[4] + bounds[5]),
        ]
        with self.state as state:
            state.data_arrays_available = source.available_arrays
            state.data_arrays = source.arrays

            state.color_by = None
            state.axis_names = [
                x for x in [source.x, source.y, source.z] if x is not None
            ]
            state.slice_extents = source.slice_extents

            # Update time
            state.slice_t = source.t_index
            state.slice_t_max = source.t_size - 1
            state.t_labels = source.t_labels
            state.max_time_width = math.ceil(0.58 * max_str_length(state.t_labels))

            if state.slice_t_max > 0:
                state.max_time_index_width = math.ceil(
                    0.6 + (math.log10(state.slice_t_max + 1) + 1) * 2 * 0.58
                )

            # Update state from dataset
            state.bounds = ds.bounds
            state.cut_x = origin[0]
            state.cut_y = origin[1]
            state.cut_z = origin[2]
            state.slice_axis = source.z if source.z is not None else source.y
            state.slice_axes = state.axis_names
