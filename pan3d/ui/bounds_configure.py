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
        da_t="da_t",
        da_t_index="da_t_index",
        current_time="ui_current_time_string",
        cube_view_mode="cube_view_mode",
        cube_preview="cube_preview",
        cube_preview_face="cube_preview_face",
        cube_preview_face_options="cube_preview_face_options",
        cube_preview_axes="cube_preview_axes",
    ):
        super().__init__(
            v_if=(da_auto_slicing,),
            location="start",
            transition="slide-y-transition",
            close_on_content_click=False,
            persistent=True,
            no_click_animation=True,
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
            with vuetify.VCard(classes="pa-3", style="width: 325px"):
                vuetify.VCardTitle("Configure Bounds")
                vuetify.VSelect(
                    v_if=(cube_view_mode,),
                    v_model=(cube_preview_face,),
                    items=(cube_preview_face_options, []),
                    label="Face",
                    hide_details=True,
                    style="float:right",
                )
                vuetify.VCheckbox(
                    v_model=(cube_view_mode,), label="Cube View", hide_details=True
                )
                with html.Div(
                    v_for=(f"coord in {da_coordinates}",),
                ):
                    with vuetify.VRangeSlider(
                        v_if=(
                            f"""
                            ({da_x} === coord.name && (!{cube_view_mode} || {cube_preview_face}.includes('X'))) ||
                            ({da_y} === coord.name && (!{cube_view_mode} || {cube_preview_face}.includes('Y'))) ||
                            ({da_z} === coord.name && (!{cube_view_mode} || {cube_preview_face}.includes('Z')))
                        """,
                        ),
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
                with html.Div(
                    v_for=(f"coord in {da_coordinates}",),
                ):
                    with vuetify.VSlider(
                        v_model=(da_t_index),
                        v_if=(f"{da_t} === coord.name",),
                        label=("coord.name",),
                        min=("coord.full_bounds[0]",),
                        max=("coord.full_bounds[1] - 1",),
                        step=1,
                        thumb_label=True,
                    ):
                        with vuetify.Template(v_slot_thumb_label=("{ modelValue }",)):
                            html.Span(
                                ("{{ coord.labels[modelValue] }}",),
                                style="white-space: nowrap",
                            )
