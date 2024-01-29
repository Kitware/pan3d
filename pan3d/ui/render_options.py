from trame.widgets import vuetify3 as vuetify


class RenderOptions(vuetify.VMenu):
    def __init__(
        self,
        x_scale="render_x_scale",
        y_scale="render_y_scale",
        z_scale="render_z_scale",
        colormap="render_colormap",
        colormap_options="render_colormap_options",
        transparency="render_transparency",
        transparency_function="render_transparency_function",
        transparency_function_options="render_transparency_function_options",
        scalar_warp="render_scalar_warp",
    ):
        super().__init__(
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
                    icon="mdi-cog",
                    style="position: absolute; right: 20px; top: 20px; z-index:2",
                )
            with vuetify.VCard(classes="pa-3"):
                vuetify.VSelect(
                    label="Colormap",
                    v_model=(colormap,),
                    items=(colormap_options,),
                    density="compact",
                )
                vuetify.VCheckbox(
                    label="Transparency", v_model=(transparency,), density="compact"
                )
                vuetify.VSelect(
                    label="Transparency Function",
                    v_show=(transparency,),
                    v_model=(transparency_function,),
                    items=(transparency_function_options,),
                    density="compact",
                )
                vuetify.VCheckbox(
                    label="Warp by Scalars", v_model=(scalar_warp,), density="compact"
                )
                with vuetify.VContainer(classes="d-flex pa-0", style="column-gap: 3px"):
                    vuetify.VTextField(
                        v_model=(x_scale,),
                        label="X Scale",
                        min=1,
                        step=1,
                        hide_details=True,
                        density="compact",
                        style="width: 80px",
                        type="number",
                        __properties=["min", "step"],
                    )
                    vuetify.VTextField(
                        v_model=(y_scale,),
                        label="Y Scale",
                        min=1,
                        step=1,
                        hide_details=True,
                        density="compact",
                        style="width: 80px",
                        type="number",
                        __properties=["min", "step"],
                    )
                    vuetify.VTextField(
                        v_model=(z_scale,),
                        label="Z Scale",
                        min=1,
                        step=1,
                        hide_details=True,
                        density="compact",
                        style="width: 80px",
                        type="number",
                        __properties=["min", "step"],
                    )
