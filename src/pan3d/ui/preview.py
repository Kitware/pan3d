from pan3d.utils.common import RenderingSettingsBasic
from pan3d.utils.constants import XYZ
from pan3d.widgets import ClipSliceControl, LevelOfDetail, ScaleControl, TimeNavigation
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
            # X crop/cut
            ClipSliceControl(
                axis="x",
                axis_name_expr="axis_names?.[0]",
                bounds_min_expr="dataset_bounds[0]",
                bounds_max_expr="dataset_bounds[1]",
                extents_min_expr="slice_extents[axis_names[0]][0]",
                extents_max_expr="slice_extents[axis_names[0]][1]",
            )

            # Y crop/cut
            ClipSliceControl(
                axis="y",
                axis_name_expr="axis_names?.[1]",
                bounds_min_expr="dataset_bounds[2]",
                bounds_max_expr="dataset_bounds[3]",
                extents_min_expr="slice_extents[axis_names[1]][0]",
                extents_max_expr="slice_extents[axis_names[1]][1]",
            )

            # Z crop/cut
            ClipSliceControl(
                axis="z",
                axis_name_expr="axis_names?.[2]",
                bounds_min_expr="dataset_bounds[4]",
                bounds_max_expr="dataset_bounds[5]",
                extents_min_expr="slice_extents[axis_names[2]][0]",
                extents_max_expr="slice_extents[axis_names[2]][1]",
            )

            v3.VDivider()

            # Slice steps
            LevelOfDetail(
                step_x_name="slice_x_step",
                step_y_name="slice_y_step",
                step_z_name="slice_z_step",
                axis_names_var="axis_names",
                min_value=1,
            )

            # Actor scaling
            ScaleControl(
                scale_x_name="scale_x",
                scale_y_name="scale_y",
                scale_z_name="scale_z",
                axis_names_var="axis_names",
                min_value=0.001,
                max_value=100,
                step=0.1,
                density="compact",
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
        self.source = source or self.source

        with self.state as state:
            state.data_arrays_available = source.available_arrays
            state.data_arrays = source.arrays
            # state.color_by = None
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
