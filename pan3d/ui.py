from trame.widgets import html, vuetify
from pyvista.trame.ui import plotter_ui


# Create single page layout type
# (FullScreenPage, SinglePage, SinglePageWithDrawer)
def initialize(layout, ctrl):
    with layout:
        layout.title.set_text("Pan3D Viewer")
        with layout.toolbar:
            layout.toolbar.dense = True
            layout.toolbar.align = "center"

            vuetify.VProgressCircular(
                v_show=("loading",),
                indeterminate=True,
                classes="mx-10",
            )

            vuetify.VSpacer()
            with vuetify.VBtn(
                click=ctrl.reset,
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

        # Drawer
        with layout.drawer:
            with html.Div(classes="pa-2"):
                vuetify.VSelect(
                    label="Choose a dataset",
                    v_model="dataset_path",
                    items=("available_datasets",),
                    item_text="name",
                    item_value="url",
                    hide_details=True,
                    dense=True,
                    clearable=True,
                    outlined=True,
                    classes="pt-1",
                    click_clear=ctrl.clear_dataset,
                )

                html.A(
                    "More information about this dataset",
                    href=("more_info_link",),
                    v_show=("more_info_link",),
                    target="_blank",
                )

                vuetify.VCardText(
                    "Available Arrays",
                    v_show="dataset_ready",
                    classes="font-weight-bold",
                )
                vuetify.VCardText(
                    "No data variables found.",
                    v_show=("dataset_ready && data_vars.length === 0",),
                )
                with vuetify.VTreeview(
                    v_show="dataset_ready",
                    dense=True,
                    activatable=True,
                    active=("[array_active]",),
                    items=("data_vars",),
                    item_key="name",
                    update_active="array_active = $event[0]",
                    multiple_active=False,
                ):
                    with vuetify.Template(v_slot_label="{ item }"):
                        html.Span("{{ item?.name }}", classes="text-subtitle-2")

                attrs_headers = [
                    {"text": "key", "value": "key"},
                    {"text": "value", "value": "value"},
                ]
                vuetify.VCardText(
                    "Data Attributes",
                    v_show="data_attrs.length",
                    classes="font-weight-bold",
                )
                vuetify.VDataTable(
                    v_show="data_attrs.length",
                    dense=True,
                    items=("data_attrs",),
                    headers=("headers", attrs_headers),
                    hide_default_header=True,
                )

        # Content
        with layout.content:
            vuetify.VBanner(
                "{{ error_message }}",
                v_show=("error_message",),
            )
            with html.Div(
                classes="d-flex",
                style="flex-direction: column; height: 100%",
            ):
                with vuetify.VContainer(
                    v_show="array_active",
                    classes="pa-2",
                    fluid=True,
                ):
                    with vuetify.VCol():
                        with vuetify.VRow():
                            html.Div("X:", classes="text-subtitle-2 pr-2")
                            vuetify.VSelect(
                                v_model=("x_array", None),
                                items=("coordinates",),
                                hide_details=True,
                                dense=True,
                                clearable="True",
                                clear="x_array = undefined",
                                style="max-width: 250px;",
                            )
                            vuetify.VSlider(
                                v_show="x_array",
                                v_model=("x_scale", 0),
                                classes="ml-2",
                                label="Scale",
                                thumb_label=True,
                                min=1,
                                max=10,
                                dense=True,
                                hide_details=True,
                                style="max-width: 250px;",
                            )

                        with vuetify.VRow():
                            html.Div("Y:", classes="text-subtitle-2 pr-2")
                            vuetify.VSelect(
                                v_model=("y_array", None),
                                items=("coordinates",),
                                hide_details=True,
                                dense=True,
                                clearable="True",
                                clear="y_array = undefined",
                                style="max-width: 250px;",
                            )
                            vuetify.VSlider(
                                v_show="y_array",
                                v_model=("y_scale", 0),
                                classes="ml-2",
                                label="Scale",
                                thumb_label=True,
                                min=1,
                                max=10,
                                dense=True,
                                hide_details=True,
                                style="max-width: 250px;",
                            )

                        with vuetify.VRow():
                            html.Div("Z:", classes="text-subtitle-2 pr-2")
                            vuetify.VSelect(
                                v_model=("z_array", None),
                                items=("coordinates",),
                                hide_details=True,
                                dense=True,
                                clearable="True",
                                clear="z_array = undefined",
                                style="max-width: 250px;",
                            )
                            vuetify.VSlider(
                                v_show="z_array",
                                v_model=("z_scale", 0),
                                classes="ml-2",
                                label="Scale",
                                thumb_label=True,
                                min=1,
                                max=10,
                                dense=True,
                                hide_details=True,
                                style="max-width: 250px;",
                            )

                        with vuetify.VRow():
                            html.Div("T:", classes="text-subtitle-2 pr-2")
                            vuetify.VSelect(
                                v_model=("t_array", None),
                                items=("coordinates",),
                                hide_details=True,
                                dense=True,
                                clearable="True",
                                clear="t_array = undefined",
                                style="max-width: 250px;",
                            )
                            vuetify.VSlider(
                                v_show="t_array && t_max > 0",
                                v_model=("t_index", 0),
                                classes="ml-2",
                                label="Index",
                                thumb_label=True,
                                min=0,
                                max=("t_max", 0),
                                step=1,
                                dense=True,
                                hide_details=True,
                                style="max-width: 250px;",
                            )

                with html.Div(
                    v_show="array_active",
                    style="height: 100%; position: relative;",
                ):
                    with plotter_ui(
                        ctrl.get_plotter(),
                        interactive_ratio=1,
                    ) as plot_view:
                        ctrl.view_update = plot_view.update
                        ctrl.reset_camera = plot_view.reset_camera

        # Footer
        layout.footer.hide()
