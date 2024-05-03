from trame.widgets import html
from trame.widgets import vuetify3 as vuetify


class BoundsConfigure(vuetify.VMenu):
    def __init__(
        self,
        coordinate_change_bounds_function,
        da_coordinates="da_coordinates",
        da_auto_slicing="da_auto_slicing",
        da_x="da_x",
        da_y="da_y",
        da_z="da_z",
    ):
        super().__init__(
            v_if=(da_auto_slicing,),
            location="start",
            transition="slide-y-transition",
            close_on_content_click=False,
        )
        with self:
            with vuetify.Template(
                activator="{ props }",
                __properties=[
                    ("activator", "v-slot:activator"),
                ],
            ):
                vuetify.VBtn(
                    v_bind=("props",),
                    size="small",
                    icon="mdi-tune-variant",
                    style="position: absolute; left: 20px; top: 60px; z-index:2",
                )
            with vuetify.VCard(classes="pa-6", style="width: 320px"):
                with html.Div(
                    v_for=(f"coord in {da_coordinates}",),
                ):
                    with vuetify.VRangeSlider(
                        v_if=(f"[{da_x}, {da_y}, {da_z}].includes(coord.name)",),
                        model_value=("coord.bounds",),
                        label=("coord.name",),
                        strict=True,
                        hide_details=True,
                        step=1,
                        min=("coord.full_bounds[0]",),
                        max=("coord.full_bounds[1]",),
                        thumb_label=True,
                        style="width: 250px",
                        end=(coordinate_change_bounds_function, "[coord.name, $event]"),
                        __events=[("end", "end")],
                    ):
                        with vuetify.Template(v_slot_thumb_label=("{ modelValue }",)):
                            html.Span(
                                ("{{ coord.labels[modelValue] }}",),
                                style="white-space: nowrap",
                            )
