from trame.widgets import html
from trame.widgets import vuetify3 as vuetify


class Toolbar(html.Div):
    def __init__(
        self,
        reset=None,
        loading="loading",
        unapplied_changes="unapplied_changes",
        array_active="array_active",
        da_size="da_size",
        view_edge_visibility="view_edge_visibility",
    ):
        super().__init__(
            classes="d-flex flex-row-reverse pa-3 fill-height", style="column-gap: 10px"
        )
        with self:
            vuetify.VProgressCircular(
                v_show=(loading,),
                indeterminate=True,
                classes="mx-10",
            )
            with vuetify.VBtn(
                click=reset,
                v_show=unapplied_changes,
                small=True,
            ):
                html.Span("Apply & Render")
                html.Span("({{ %s }})" % da_size, v_show=da_size)
            vuetify.VCheckbox(
                v_model=(view_edge_visibility, True),
                v_show=array_active,
                density="compact",
                true_icon="mdi-border-all",
                false_icon="mdi-border-outside",
            )
