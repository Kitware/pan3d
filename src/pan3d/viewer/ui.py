from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import html, vtk, vuetify


# Create single page layout type
# (FullScreenPage, SinglePage, SinglePageWithDrawer)
def initialize(server):
    state, ctrl = server.state, server.controller
    state.trame__title = "Pan3D Viewer"

    with SinglePageWithDrawerLayout(server) as layout:
        # Toolbar
        layout.title.set_text("Pan3D Viewer")
        with layout.toolbar:
            layout.toolbar.dense = True
            layout.toolbar.align = "center"
            vuetify.VSpacer()

            vuetify.VCheckbox(
                v_model=("view_edge_visiblity", True),
                dense=True,
                hide_details=True,
                on_icon="mdi-border-all",
                off_icon="mdi-border-outside",
                classes="ma-2",
            )

            with vuetify.VBtn(
                icon=True,
                click=ctrl.build,
            ):
                vuetify.VIcon("mdi-crop-free")

        # Drawer
        with layout.drawer:
            with vuetify.VTreeview(
                dense=True,
                activatable=True,
                items=("data_vars",),
                update_active="array_active = data_vars[$event[0] || 0]?.name",
                # TODO: set active/selected on startup
                multiple_active=False,
            ):
                with vuetify.Template(v_slot_label="{ item }"):
                    html.Span("{{ item?.name }}", classes="text-subtitle-2")

        # Content
        with layout.content:
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                with vuetify.VCol(
                    v_show="array_active",
                    classes="fill-height",
                ):
                    with vuetify.VCard(style="flex: none;"):
                        vuetify.VDivider()
                        with vuetify.VCardText():
                            with vuetify.VCol():
                                with vuetify.VRow():
                                    html.Div("X:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_x_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VSlider(
                                        label="X Scale",
                                        v_show="grid_x_array",
                                        v_model=("x_scale", 0),
                                        min=1,
                                        max=1000,
                                        step=10,
                                        dense=True,
                                        hide_details=True,
                                        style="max-width: 250px;",
                                    )
                                    vuetify.VSelect(
                                        v_model=("grid_x_array", None),
                                        items=("coordinates",),
                                        hide_details=True,
                                        dense=True,
                                        style="max-width: 250px;",
                                    )
                                with vuetify.VRow():
                                    html.Div("Y:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_y_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VSlider(
                                        label="Y Scale",
                                        v_show="grid_y_array",
                                        v_model=("y_scale", 0),
                                        min=1,
                                        max=1000,
                                        step=10,
                                        dense=True,
                                        hide_details=True,
                                        style="max-width: 250px;",
                                    )
                                    vuetify.VSelect(
                                        v_model=("grid_y_array", None),
                                        items=("coordinates",),
                                        hide_details=True,
                                        dense=True,
                                        style="max-width: 250px;",
                                    )
                                with vuetify.VRow():
                                    html.Div("Z:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_z_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VSlider(
                                        label="Z Scale",
                                        v_show="grid_z_array",
                                        v_model=("z_scale", 0),
                                        min=1,
                                        max=1000,
                                        step=10,
                                        dense=True,
                                        hide_details=True,
                                        style="max-width: 250px;",
                                    )
                                    vuetify.VSelect(
                                        v_model=("grid_z_array", None),
                                        items=("coordinates",),
                                        hide_details=True,
                                        dense=True,
                                        style="max-width: 250px;",
                                    )
                                with vuetify.VRow():
                                    html.Div("T:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_t_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VSlider(
                                        label="Time",
                                        v_show="grid_t_array && time_max > 0",
                                        v_model=("time_index", 0),
                                        min=0,
                                        max=("time_max", 0),
                                        step=1,
                                        dense=True,
                                        hide_details=True,
                                        style="max-width: 250px;",
                                    )
                                    vuetify.VSelect(
                                        v_model=("grid_t_array", None),
                                        items=("coordinates",),
                                        hide_details=True,
                                        dense=True,
                                        style="max-width: 250px;",
                                    )
                    with html.Div(
                        style="display: flex; flex: 1; height: calc(100vh - 300px);"
                    ):
                        with vtk.VtkRemoteView(
                            ctrl.get_render_window(),
                            # v_show="view_mode === 'view_grid'",
                            interactive_ratio=1,
                        ) as vtk_view:
                            ctrl.view_update = vtk_view.update
                            ctrl.reset_camera = vtk_view.reset_camera

        # Footer
        # layout.footer.hide()
