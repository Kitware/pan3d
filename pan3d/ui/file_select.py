from trame.widgets import html, vuetify3 as vuetify
from trame.app import get_server

server = get_server()


class FileSelect(vuetify.VCard):
    def __init__(
        self,
        import_function,
        export_function,
        dialog_shown="dialog_shown",
        selected_config_file="selected_config_file",
        state_export="state_export",
        dialog_message="dialog_message",
    ):
        def submit():
            files = server.state[selected_config_file]
            if files and len(files) > 0:
                file_content = server.state[selected_config_file][0]["content"]
                import_function(file_content)

        super().__init__()
        with self:
            with vuetify.VCardText(v_show=dialog_shown):
                vuetify.VBtn(
                    flat=True,
                    icon="mdi-close",
                    style="float: right",
                    click="%s = undefined" % dialog_shown,
                )
                vuetify.VCardTitle(
                    "{{ %s }}" % dialog_message,
                    v_show=dialog_message,
                )
                with html.Div(v_show="!%s" % dialog_message):
                    vuetify.VCardTitle("{{ %s }} File Select" % dialog_shown)

                    vuetify.VFileInput(
                        v_model=selected_config_file,
                        v_show=f"{dialog_shown} === 'Import'",
                        accept=".json",
                        label="Config File",
                    )
                    vuetify.VTextField(
                        v_model=selected_config_file,
                        v_show=f"{dialog_shown} === 'Export'",
                        label="Download Location",
                        placeholder="Use Default Download Location",
                        prepend_icon="mdi-paperclip",
                        # FileSystem API is only available on some browsers:
                        # https://caniuse.com/native-filesystem-api
                        click="""
                            if ($event){
                                try {
                                    window.showSaveFilePicker({
                                        suggestedName: 'pan3d_state.json',
                                        types: [{
                                            accept: {
                                                'application/json': ['.json']
                                            }
                                        }]
                                    }).then((handle) => {
                                        handle.createWritable().then((writable) => {
                                            writable.write(JSON.stringify(%s, null, 4));
                                            writable.close();
                                            %s = 'Export complete.'
                                        })
                                    });
                                } catch {}
                            }
                        """
                        % (state_export, dialog_message),
                    )

                    vuetify.VBtn(
                        v_show=selected_config_file,
                        variant="tonal",
                        text=(dialog_shown,),
                        click=submit,
                        style="width: 100%",
                    )
