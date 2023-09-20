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
        def submit_import():
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
                    vuetify.VBtn(
                        v_show=f"{dialog_shown} === 'Import' && {selected_config_file}",
                        variant="tonal",
                        text=(dialog_shown,),
                        click=submit_import,
                        style="width: 100%",
                    )

                    vuetify.VTextField(
                        v_model=selected_config_file,
                        v_show=f"{dialog_shown} === 'Export' && {selected_config_file} != false",
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
                        % (state_export, dialog_message, selected_config_file),
                    )
                    vuetify.VBtn(
                        v_show=f"{dialog_shown} === 'Export' && {selected_config_file} === false",
                        variant="tonal",
                        text="Download pan3d_state.json",
                        click="""
                            var content = JSON.stringify(%s, null, 4);
                            var a = window.document.createElement('a');
                            a.href = 'data:application/json;charset=utf-8,'  + encodeURIComponent(content);
                            a.download = 'pan3d_state.json';
                            a.style.display = 'none';
                            window.document.body.appendChild(a);
                            a.click()
                            window.document.body.removeChild(a);
                            %s = 'Export complete.'
                        """
                        % (state_export, dialog_message),
                        style="width: 100%",
                    )
