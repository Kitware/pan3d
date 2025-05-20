from trame.widgets import html, vuetify3 as vuetify
from trame.app import get_server

server = get_server()


class FileSelect(vuetify.VCard):
    def __init__(
        self,
        import_function,
        export_function,
        ui_action_name="ui_action_name",
        ui_action_config_file="ui_action_config_file",
        state_export="state_export",
        ui_action_message="ui_action_message",
        ui_import_loading="ui_import_loading",
    ):
        super().__init__()
        with self:
            with vuetify.VCardText(v_show=(ui_action_name,)):
                vuetify.VBtn(
                    flat=True,
                    icon="mdi-close",
                    style="float: right",
                    click=f"{ui_action_name} = undefined",
                )
                vuetify.VCardTitle(
                    "{{ %s }}" % ui_action_message,
                    v_show=(ui_action_message,),
                )
                with html.Div(v_show=(f"!{ui_action_message}",)):
                    vuetify.VCardTitle("{{ %s }} File Select" % ui_action_name)

                    vuetify.VFileInput(
                        v_model=(ui_action_config_file,),
                        v_show=(f"{ui_action_name} === 'Import'",),
                        accept=".json",
                        label="Config File",
                    )
                    vuetify.VBtn(
                        v_show=(
                            f"{ui_action_name} === 'Import' && {ui_action_config_file} && !{ui_import_loading}",
                        ),
                        variant="tonal",
                        text=(ui_action_name,),
                        click=import_function,
                        style="width: 100%",
                    )
                    vuetify.VCardSubtitle(
                        "Reading configuration file and applying changes...",
                        v_show=(ui_import_loading,),
                    )
                    vuetify.VProgressLinear(
                        v_show=(ui_import_loading,),
                        indeterminate=True,
                    )

                    vuetify.VTextField(
                        v_model=(ui_action_config_file,),
                        v_show=(
                            f"{ui_action_name} === 'Export' && {ui_action_config_file} != false",
                        ),
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
                        % (state_export, ui_action_message, ui_action_config_file),
                    )
                    vuetify.VBtn(
                        v_show=(
                            f"{ui_action_name} === 'Export' && {ui_action_config_file} === false",
                        ),
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
                            {ui_action_message} = 'Export complete.'
                        """,
                        style="width: 100%",
                    )
