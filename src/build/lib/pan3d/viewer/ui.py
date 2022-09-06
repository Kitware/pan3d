from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, vtk, html


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
            vuetify.VSpacer()
            with vuetify.VBtn(icon=True, click=ctrl.reset_camera):
                vuetify.VIcon("mdi-crop-free")

        with layout.drawer:
            with vuetify.VTreeview(
                dense=True,
                activatable=True,
                items=("zarr_tree",),
            ):
                with vuetify.Template(v_slot_label="{ item }"):
                    html.Span("{{ item.name }}", classes="text-subtitle-2")
                with vuetify.Template(v_slot_append="{ item }"):
                    vuetify.VSpacer()
                    html.Span("{{ item.type }} {{ item.dimensions }}", v_if="item.dimensions", classes="text-caption")

        # Main content
        with layout.content:
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                with vtk.VtkRemoteView(ctrl.get_render_window()) as vtk_view:
                    ctrl.reset_camera = vtk_view.reset_camera

        # Footer
        layout.footer.hide()
