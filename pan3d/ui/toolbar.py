from trame.widgets import html
from trame.widgets import vuetify3 as vuetify
from .file_select import FileSelect


class Toolbar(html.Div):
    def __init__(
        self,
        reset_function,
        import_function,
        export_function,
        ui_dialog_shown="ui_dialog_shown",
        ui_loading="ui_loading",
        ui_unapplied_changes="ui_unapplied_changes",
        da_active="da_active",
        da_size="da_size",
    ):
        super().__init__(
            classes="d-flex flex-row-reverse pa-3 fill-height", style="column-gap: 10px"
        )
        with self:
            vuetify.VProgressCircular(
                v_show=(ui_loading,),
                indeterminate=True,
                classes="mx-10",
            )
            with vuetify.VBtn(
                click=reset_function,
                v_show=ui_unapplied_changes,
                variant="tonal",
            ):
                html.Span("Apply & Render")
                html.Span("({{ %s }})" % da_size, v_show=da_size)
            vuetify.VBtn(
                click=f"{ui_dialog_shown} = 'Export'",
                variant="tonal",
                text="Export",
            )
            vuetify.VBtn(
                click=f"{ui_dialog_shown} = 'Import'",
                variant="tonal",
                text="Import",
            )
            with vuetify.VDialog(v_model=ui_dialog_shown, max_width=800):
                FileSelect(
                    import_function,
                    export_function,
                    ui_dialog_shown=ui_dialog_shown,
                )
