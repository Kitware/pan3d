from trame.widgets import html, vuetify
from pyvista.trame.ui import plotter_ui


class RenderArea:
    def __init__(self, layout):
        ctrl = layout.server.controller
        with layout:
            with layout.content:
                vuetify.VBanner(
                    "{{ error_message }}",
                    v_show=("error_message",),
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
