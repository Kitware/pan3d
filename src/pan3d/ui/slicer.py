from pan3d.ui.rendering_settings import RenderingSettingsBasic
from pan3d.widgets.slice_control import SliceControl
from pan3d.widgets.time_navigation import TimeNavigation
from pan3d.widgets.vector_property_control import VectorPropertyControl
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class SliceRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source

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

            # Use SliceControl widget for the rest
            SliceControl(
                slice_axis_var="slice_axis",
                axis_names_var="axis_names",
                cut_x_var="cut_x",
                cut_y_var="cut_y",
                cut_z_var="cut_z",
                bounds_var="bounds",
                show_value_display=False,  # We already have custom display above
                show_bounds=True,
            )

            v3.VDivider()
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
            v3.VDivider()
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

            # Update TimeNavigation widget through context
            if self.ctx.has("time_nav"):
                self.ctx.time_nav.labels = source.t_labels
                self.ctx.time_nav.index = source.t_index

            # Update state from dataset
            state.bounds = ds.bounds
            state.cut_x = origin[0]
            state.cut_y = origin[1]
            state.cut_z = origin[2]
            state.slice_axis = source.z if source.z is not None else source.y
            state.slice_axes = state.axis_names
