import math

from trame.widgets import vuetify3 as v3, html

from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.convert import max_str_length


class ContourRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering):
        super().__init__(source, update_rendering)

        self.source = source
        fields = list(self.source.available_arrays)
        active_field = fields[0] if len(fields) > 0 else None
        nb_times = (
            self.source.input[active_field].shape[0] if active_field is not None else 0
        )

        with self.content:
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
                                    'pattern="^\d*(\.\d)?$"',  # noqa: W605
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
                                    'pattern="^\d*(\.\d)?$"',  # noqa: W605
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
                                    'pattern="^\d*(\.\d)?$"',  # noqa: W605
                                    'min="0.001"',
                                    'step="0.1"',
                                ],
                                type="number",
                            )

            # contours
            with v3.VTooltip(
                text=("`Number of contours: ${nb_contours}`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            v_model=("nb_contours", 20),
                            min=2,
                            max=50,
                            step=1,
                            prepend_icon="mdi-fingerprint",
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )

            v3.VDivider()
            # Time slider
            with v3.VTooltip(
                v_if="slice_t_max > 0",
                text=("`time: ${time_idx + 1} / ${slice_t_max+1}`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    with html.Div(
                        classes="d-flex pr-2",
                        v_bind="props",
                    ):
                        v3.VSlider(
                            prepend_icon="mdi-clock-outline",
                            v_model=("time_idx", 0),
                            min=0,
                            max=("slice_t_max", nb_times - 1),
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
            self.state.color_by = None
            self.state.axis_names = [source.x, source.y, source.z]
            self.state.slice_extents = source.slice_extents

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
