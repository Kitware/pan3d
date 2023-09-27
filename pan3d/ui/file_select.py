from trame.widgets import html, vuetify3 as vuetify
from trame.app import get_server

server = get_server()


class FileSelect(vuetify.VCard):
    def __init__(
        self,
        import_function,
        export_function,
        ui_dialog_shown="ui_dialog_shown",
        ui_selected_config_file="ui_selected_config_file",
        state_export="state_export",
        ui_dialog_message="ui_dialog_message",
    ):
        def submit_import():
            files = server.state[ui_selected_config_file]
            if files and len(files) > 0:
                file_content = server.state[ui_selected_config_file][0]["content"]
                import_function(file_content)

        super().__init__()
        with self:
            with vuetify.VCardText(v_show=ui_dialog_shown):
                vuetify.VBtn(
                    flat=True,
                    icon="mdi-close",
                    style="float: right",
                    click=f"{ui_dialog_shown} = undefined",
                )
                vuetify.VCardTitle(
                    "{{ %s }}" % ui_dialog_message,
                    v_show=ui_dialog_message,
                )
                with html.Div(v_show=f"!{ui_dialog_message}"):
                    vuetify.VCardTitle("{{ %s }} File Select" % ui_dialog_shown)

                    vuetify.VFileInput(
                        v_model=ui_selected_config_file,
                        v_show=f"{ui_dialog_shown} === 'Import'",
                        accept=".json",
                        label="Config File",
                    )
                    vuetify.VBtn(
                        v_show=f"{ui_dialog_shown} === 'Import' && {ui_selected_config_file}",
                        variant="tonal",
                        text=(ui_dialog_shown,),
                        click=submit_import,
                        style="width: 100%",
                    )

                    vuetify.VTextField(
                        v_model=ui_selected_config_file,
                        v_show=f"{ui_dialog_shown} === 'Export' && {ui_selected_config_file} != false",
                        label="Download Location",
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
                                } catch {
                                    %s = false;
                                    window.alert('Your browser does not support selecting a download location. Your download will be made to the default location, saved as pan3d_state.json.')
                                }
                            }
                        """
                        % (state_export, ui_dialog_message, ui_selected_config_file),
                    )
                    vuetify.VBtn(
                        v_show=f"{ui_dialog_shown} === 'Export' && {ui_selected_config_file} === false",
                        variant="tonal",
                        text="Download pan3d_state.json",
                        click=f"""
                            var content = JSON.stringify({state_export}, null, 4);
                            var a = window.document.createElement('a');
                            a.href = 'data:application/json;charset=utf-8,'  + encodeURIComponent(content);
                            a.download = 'pan3d_state.json';
                            a.style.display = 'none';
                            window.document.body.appendChild(a);
                            a.click()
                            window.document.body.removeChild(a);
                            {ui_dialog_message} = 'Export complete.'
                        """,
                        style="width: 100%",
                    )
