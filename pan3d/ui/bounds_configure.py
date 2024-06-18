from trame.widgets import html
from trame.widgets import vuetify3 as vuetify

from .pan3d_components.widgets import PreviewBounds


class BoundsConfigure(vuetify.VMenu):
    def __init__(
        self,
        coordinate_change_bounds_function,
        snap_camera_function,
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
                vuetify.VCheckbox(
                    v_model=(cube_view_mode,),
                    label="Interactive Preview",
                    hide_details=True,
                )
                vuetify.VSelect(
                    v_if=(cube_view_mode,),
                    v_model=(cube_preview_face,),
                    items=(cube_preview_face_options, []),
                    label="Face",
                    hide_details=True,
                    style="float:left",
                )
                vuetify.VBtn(
                    v_if=(cube_view_mode,),
                    size="small",
                    icon="mdi-video-marker",
                    click=snap_camera_function,
                    style="float:right",
                )
                with html.Div(v_if=(cube_view_mode,)):
                    PreviewBounds(
                        v_if=(cube_preview,),
                        preview=(cube_preview,),
                        axes=(cube_preview_axes,),
                        coordinates=(da_coordinates,),
                        update_bounds=(
                            coordinate_change_bounds_function,
                            "[$event.name, $event.bounds]",
                        ),
                    )
                with html.Div(
                    v_for=(f"coord in {da_coordinates}",),
                ):
                    with html.Div(
                        v_if=(
                            f"""
                            ({da_x} === coord.name && (!{cube_view_mode} || {cube_preview_face}.includes('X'))) ||
                            ({da_y} === coord.name && (!{cube_view_mode} || {cube_preview_face}.includes('Y'))) ||
                            ({da_z} === coord.name && (!{cube_view_mode} || {cube_preview_face}.includes('Z')))
                        """,
                        ),
                        style="text-transform: capitalize",
                    ):
                        html.Span("{{ coord.name.replaceAll('_', ' ') }}")
                        with vuetify.VRangeSlider(
                            model_value=("coord.bounds",),
                            strict=True,
                            hide_details=True,
                            step=1,
                            min=("coord.full_bounds[0]",),
                            max=("coord.full_bounds[1]",),
                            thumb_label=True,
                            classes=("coord.name +'-slider px-3'",),
                            end=(
                                coordinate_change_bounds_function,
                                "[coord.name, $event]",
                            ),
                            __events=[("end", "end")],
                        ):
                            with vuetify.Template(
                                v_slot_thumb_label=("{ modelValue }",)
                            ):
                                html.Span(
                                    ("{{ coord.labels[modelValue] }}",),
                                    style="white-space: nowrap",
                                )
                with html.Div(
                    v_for=(f"coord in {da_coordinates}",),
                ):
                    with html.Div(
                        v_if=(f"{da_t} === coord.name",),
                        style="text-transform: capitalize",
                    ):
                        html.Span("{{ coord.name }}")
                        with vuetify.VSlider(
                            v_model=(da_t_index),
                            min=("coord.full_bounds[0]",),
                            max=("coord.full_bounds[1] - 1",),
                            step=1,
                            thumb_label=True,
                            classes="px-3",
                        ):
                            with vuetify.Template(
                                v_slot_thumb_label=("{ modelValue }",)
                            ):
                                html.Span(
                                    ("{{ coord.labels[modelValue] }}",),
                                    style="white-space: nowrap",
                                )
