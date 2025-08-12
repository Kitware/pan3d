from pan3d.ui.rendering_settings import RenderingSettingsBasic
from pan3d.widgets.time_navigation import TimeNavigation
from pan3d.widgets.vector_property_control import VectorPropertyControl
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ContourRenderingSettings(RenderingSettingsBasic):
    def __init__(self, source, update_rendering, **kwargs):
        super().__init__(source, update_rendering, **kwargs)

        self.source = source

        with self.content:
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

            # Update TimeNavigation widget through context
            if self.ctx.has("time_nav"):
                self.ctx.time_nav.labels = source.t_labels
                self.ctx.time_nav.index = source.t_index
