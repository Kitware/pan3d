from pan3d.ui.shared_components import (
    AxisSlicingControls,
    ScalingControls,
    SliceSteppingControls,
    UpdateButton,
)
from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.constants import XYZ
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class RenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source
        self.state.setdefault("slice_extents", {})
        self.state.setdefault("axis_names", [])
        self.state.setdefault("t_labels", [])
        self.state.setdefault("max_time_width", 0)
        self.state.setdefault("max_time_index_width", 0)
        self.state.setdefault("dataset_bounds", [0, 1, 0, 1, 0, 1])

        with self.content:
            v3.VDivider()

            # Axis slicing controls
            axis_controls = AxisSlicingControls()
            for _component in axis_controls.create():
                pass  # Component is rendered by being in the context

            v3.VDivider()

            # Slice stepping controls
            SliceSteppingControls().create()

            # Actor scaling
            ScalingControls().create()

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

            UpdateButton(update_rendering).create()

    def update_from_source(self, source=None):
        # Call base implementation
        super().update_from_source(source or self.source)

        if self.source is None:
            return

        # Additional preview-specific logic
        with self.state as state:
            slices = self.source.slices
            for axis in XYZ:
                # default
                axis_extent = state.slice_extents.get(getattr(self.source, axis))
                state[f"slice_{axis}_range"] = axis_extent
                state[f"slice_{axis}_cut"] = 0
                state[f"slice_{axis}_step"] = 1
                state[f"slice_{axis}_type"] = "range"

                # use slice info if available
                axis_slice = slices.get(getattr(self.source, axis))
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
