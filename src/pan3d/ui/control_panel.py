"""Control panel UI component for Pan3D explorers."""

from pan3d.widgets.data_information import DataInformation
from pan3d.widgets.data_origin import DataOrigin
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class ControlPanel(v3.VCard):
    """
    Control panel component that provides data selection, import/export,
    and dataset information display.

    This panel includes:
    - Data origin selection (when enabled)
    - Import/export state functionality
    - Save dataset to disk
    - Data information display
    """

    def __init__(
        self,
        enable_data_selection,
        toggle,
        load_dataset,
        import_file_upload,
        export_file_download,
        xr_update_info="xr_update_info",
        panel_label="XArray Viewer",
        **kwargs,
    ):
        """
        Initialize the ControlPanel.

        Parameters:
            enable_data_selection: Whether to show data selection UI
            toggle: State variable name for panel expansion toggle
            load_dataset: Callback function for loading datasets
            import_file_upload: Callback function for importing state files
            export_file_download: Callback function for exporting state
            xr_update_info: Controller method name for updating data info
            panel_label: Label to display in the panel header
            **kwargs: Additional arguments passed to VCard
        """
        super().__init__(
            classes="controller",
            rounded=(f"{toggle} || 'circle'",),
            **kwargs,
        )

        # state initialization
        self.state.import_pending = False

        # extract trigger name
        download_export = self.ctrl.trigger_name(export_file_download)

        with self:
            with v3.VCardTitle(
                classes=(
                    f"`d-flex pa-1 position-fixed bg-white ${{ {toggle} ? 'controller-content rounded-t border-b-thin':'rounded-circle'}}`",
                ),
                style="z-index: 1;",
            ):
                v3.VProgressLinear(
                    v_if=toggle,
                    indeterminate=("trame__busy",),
                    bg_color="rgba(0,0,0,0)",
                    absolute=True,
                    color="primary",
                    location="bottom",
                    height=2,
                )
                v3.VProgressCircular(
                    v_else=True,
                    bg_color="rgba(0,0,0,0)",
                    indeterminate=("trame__busy",),
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;",
                    color="primary",
                    width=3,
                )
                v3.VBtn(
                    icon="mdi-close",
                    v_if=toggle,
                    click=f"{toggle} = !{toggle}",
                    flat=True,
                    size="sm",
                )
                v3.VBtn(
                    icon="mdi-menu",
                    v_else=True,
                    click=f"{toggle} = !{toggle}",
                    flat=True,
                    size="sm",
                )
                if self.server.hot_reload:
                    v3.VBtn(
                        v_show=toggle,
                        icon="mdi-refresh",
                        flat=True,
                        size="sm",
                        click=self.ctrl.on_server_reload,
                    )
                v3.VSpacer()
                html.Div(
                    panel_label,
                    v_show=toggle,
                    classes="text-h6 px-2",
                )
                v3.VSpacer()

                with v3.VMenu(v_if=toggle, density="compact"):
                    with html.Template(v_slot_activator="{props}"):
                        v3.VBtn(
                            v_bind="props",
                            icon="mdi-file-arrow-left-right-outline",
                            flat=True,
                            size="sm",
                            classes="mx-1",
                        )
                    with v3.VList(density="compact"):
                        if enable_data_selection:
                            with v3.VListItem(
                                title="Export state file",
                                disabled=("can_load",),
                                click=f"utils.download('xarray-state.json', trigger('{download_export}'), 'text/plain')",
                            ):
                                with html.Template(v_slot_prepend=True):
                                    v3.VIcon(
                                        "mdi-cloud-download-outline", classes="mr-n5"
                                    )

                        with v3.VListItem(
                            title="Import state file",
                            click="trame.utils.get('document').querySelector('#fileImport').click()",
                        ):
                            html.Input(
                                id="fileImport",
                                hidden=True,
                                type="file",
                                change=(
                                    import_file_upload,
                                    "[$event.target.files]",
                                ),
                                __events=["change"],
                            )
                            with html.Template(v_slot_prepend=True):
                                v3.VIcon("mdi-cloud-upload-outline", classes="mr-n5")
                        v3.VDivider()
                        with v3.VListItem(
                            title="Save dataset to disk",
                            disabled=("can_load",),
                            click="show_save_dialog = true",
                        ):
                            with html.Template(v_slot_prepend=True):
                                v3.VIcon("mdi-file-download-outline", classes="mr-n5")

            with v3.VCardText(
                v_show=(toggle, True),
                classes="controller-content py-1 mt-10",
            ) as ui_content:
                self.ui_content = ui_content
                if enable_data_selection:
                    DataOrigin(load_dataset)

                self._data_info = DataInformation()
                self.ctrl[xr_update_info] = self._data_info.update_information
