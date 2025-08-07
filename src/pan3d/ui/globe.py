from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.constants import XYZ
from pan3d.widgets import ClipSliceControl
from pan3d.widgets.level_of_detail import LevelOfDetail
from pan3d.widgets.time_navigation import TimeNavigation
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class GlobeRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source
        self.state.setdefault("dataset_bounds", [0, 1, 0, 1, 0, 1])

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
            # Clip/Slice controls for all axes
            ClipSliceControl(
                axis_names_var="axis_names",
                dataset_bounds_var="dataset_bounds",
                slice_extents_var="slice_extents",
                type_vars=["slice_x_type", "slice_y_type", "slice_z_type"],
                range_vars=["slice_x_range", "slice_y_range", "slice_z_range"],
                cut_vars=["slice_x_cut", "slice_y_cut", "slice_z_cut"],
                step_vars=["slice_x_step", "slice_y_step", "slice_z_step"],
            )
            v3.VDivider()

            # Level of detail / Slice steps
            LevelOfDetail(
                step_x_name="slice_x_step",
                step_y_name="slice_y_step",
                step_z_name="slice_z_step",
                axis_names_var="axis_names",
                min_value=1,
                classes="mx-2 my-2",
            )
            # Time navigation
            TimeNavigation(
                v_if="slice_t_max > 0",
                index_name="slice_t",
                labels_name="t_labels",
                labels=[],
                ctx_name="time_nav",
                classes="mx-2 my-2",
            )
            v3.VDivider()
            # Update button
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

            # Update dataset bounds for each axis
            bounds = []
            for axis in XYZ:
                axis_name = getattr(source, axis)
                if axis_name and axis_name in source.slice_extents:
                    extent = source.slice_extents[axis_name]
                    bounds.extend([extent[0], extent[1]])
                else:
                    bounds.extend([0, 1])
            state.dataset_bounds = bounds
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

            # Update TimeNavigation widget through context
            if hasattr(self.ctx, "time_nav"):
                self.ctx.time_nav.labels = source.t_labels
                self.ctx.time_nav.index = source.t_index
