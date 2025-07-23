from pan3d.ui.shared_components import (
    ScalingControls,
    UpdateButton,
)
from pan3d.utils.common import RenderingSettingsBasic
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ContourRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source

        with self.content:
            # Actor scaling
            ScalingControls().create()

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

        # Additional contour-specific logic
        with self.state as state:
            state.color_by = None
