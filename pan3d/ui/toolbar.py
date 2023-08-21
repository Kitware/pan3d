from trame.widgets import html, vuetify


class Toolbar(html.Div):
    def __init__(self, reset=None):
        super().__init__(style="width: 90%; display: flex")
        with self:
            vuetify.VProgressCircular(
                v_show=("loading",),
                indeterminate=True,
                classes="mx-10",
            )
            vuetify.VSpacer()
            with vuetify.VBtn(
                click=reset,
                v_show="unapplied_changes",
                classes="mr-5",
                small=True,
            ):
                html.Span("Apply & Render")
                html.Span("({{ da_size }})", v_show="da_size")
            resolutions = [
                0.001,
                0.01,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
            ]
            vuetify.VSelect(
                label="Resolution",
                v_model=("resolution", 1.0),
                v_show="array_active",
                items=(resolutions,),
                hide_details=True,
                dense=True,
                style="max-width: 100px",
                classes="mt-3",
            )
            vuetify.VCheckbox(
                v_model=("view_edge_visibility", True),
                v_show="array_active",
                dense=True,
                hide_details=True,
                on_icon="mdi-border-all",
                off_icon="mdi-border-outside",
            )
