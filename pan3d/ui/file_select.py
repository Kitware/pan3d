from trame.widgets import vuetify3 as vuetify
from trame.app import get_server

server = get_server()


class FileSelect(vuetify.VCard):
    def __init__(
        self,
        import_function,
        export_function,
        dialog_shown="dialog_shown",
        selected_config_file="selected_config_file",
    ):
        def submit():
            files = server.state[selected_config_file]
            if files and len(files) > 0:
                file_content = server.state[selected_config_file][0]["content"]
                if server.state[dialog_shown] == "Import":
                    import_function(file_content)
                elif server.state[dialog_shown] == "Export":
                    export_function(file_content)

        super().__init__()
        with self:
            with vuetify.VCardText(v_show=dialog_shown):
                vuetify.VBtn(
                    flat=True,
                    icon="mdi-close",
                    style="float: right",
                    click="%s = undefined" % dialog_shown,
                )
                vuetify.VCardTitle("{{ %s }} File Select" % dialog_shown)
                vuetify.VFileInput(
                    v_model=selected_config_file,
                    accept=".json",
                    label="Config File",
                )
                vuetify.VBtn(
                    v_show=selected_config_file,
                    variant="tonal",
                    text=(dialog_shown,),
                    click=submit,
                    style="width: 100%",
                )
