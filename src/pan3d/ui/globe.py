from pan3d.ui.shared_components import (
    AxisSlicingControls,
    SliceSteppingControls,
    UpdateButton,
)
from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.constants import XYZ
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

            # Axis slicing controls
            axis_controls = AxisSlicingControls()
            for _component in axis_controls.create():
                pass  # Component is rendered by being in the context

            v3.VDivider()

            # Slice stepping controls
            SliceSteppingControls().create()

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
        super().update_from_source(source)

        if self.source is None:
            return

        # Additional globe-specific logic
        with self.state as state:
            state.color_by = None
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
