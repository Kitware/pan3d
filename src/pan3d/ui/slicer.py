from pan3d.ui.shared_components import (
    ScalingControls,
    UpdateButton,
)
from pan3d.utils.common import RenderingSettingsBasic
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
            ScalingControls().create()

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

            UpdateButton(update_rendering).create()

    def update_from_source(self, source=None):
        # Call base implementation
        super().update_from_source(source)

        if self.source is None:
            return

        # Additional slicer-specific logic
        ds = self.source()
        bounds = ds.bounds
        origin = [
            0.5 * (bounds[0] + bounds[1]),
            0.5 * (bounds[2] + bounds[3]),
            0.5 * (bounds[4] + bounds[5]),
        ]

        with self.state as state:
            # Override axis_names to filter out None values
            state.axis_names = [
                x
                for x in [self.source.x, self.source.y, self.source.z]
                if x is not None
            ]

            # Update state from dataset
            state.bounds = ds.bounds
            state.cut_x = origin[0]
            state.cut_y = origin[1]
            state.cut_z = origin[2]
            state.slice_axis = (
                self.source.z if self.source.z is not None else self.source.y
            )
            state.slice_axes = state.axis_names
