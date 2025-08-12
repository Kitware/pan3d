from pan3d.ui.rendering_settings import RenderingSettingsBasic
from pan3d.utils.constants import XYZ
from pan3d.widgets import ClipSliceControl, TimeNavigation, VectorPropertyControl
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
            # Clip/Slice controls for all axes
            ClipSliceControl(
                axis_names_var="axis_names",
                dataset_bounds_var="dataset_bounds",
                slice_extents_var="slice_extents",
                type_vars=["slice_x_type", "slice_y_type", "slice_z_type"],
                range_vars=["slice_x_range", "slice_y_range", "slice_z_range"],
                cut_vars=["slice_x_cut", "slice_y_cut", "slice_z_cut"],
                step_vars=["slice_x_step", "slice_y_step", "slice_z_step"],
                ctx_name="clip_slice",
            )

            v3.VDivider()

            # Slice steps / Level of detail
            VectorPropertyControl(
                property_name="step",
                icon="mdi-stairs",
                tooltip="Level Of Details / Slice stepping",
                x_name="slice_x_step",
                y_name="slice_y_step",
                z_name="slice_z_step",
                axis_names_var="axis_names",
                default_value=1,
                min_value=1,
            )

            # Actor scaling
            VectorPropertyControl(
                property_name="scale",
                icon="mdi-ruler-square",
                tooltip="Representation scaling",
                x_name="scale_x",
                y_name="scale_y",
                z_name="scale_z",
                axis_names_var="axis_names",
                default_value=1,
                min_value=0.001,
                max_value=100,
                step=0.1,
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

            # Update ClipSliceControl widget through context
            if self.ctx.has("clip_slice"):
                self.ctx.clip_slice.update_slice_values(source, source.slices)

            # Update TimeNavigation widget through context
            if self.ctx.has("time_nav"):
                self.ctx.time_nav.labels = source.t_labels
                self.ctx.time_nav.index = source.t_index
