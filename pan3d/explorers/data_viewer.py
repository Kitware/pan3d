import vtk

from trame.app import get_server
from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as v3, vtk as vtkw, client

from pan3d.xarray.algorithm import vtkXArrayRectilinearSource


@TrameApp()
class XArrayViewer:
    """
    A Trame based pan3D explorer to visualize vtk data.
    """

    def __init__(self, server=None):
        # trame setup
        self.server = get_server(server)
        if self.server.hot_reload:
            self.ctrl.on_server_reload.add(self._build_ui)

        self.renderer = vtk.vtkRenderer(background=(1, 1, 1))
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.render_window = vtk.vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.source = vtkXArrayRectilinearSource()
        self.mapper = vtk.vtkDataSetMapper(input_connection=self.source.output_port)
        self.actor = vtk.vtkActor(mapper=self.mapper, visibility=0)

        self.renderer.AddActor(self.actor)

        self._build_ui()

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    @property
    def ctrl(self):
        return self.server.controller

    @property
    def state(self):
        return self.server.state

    def start(self, **kwargs):
        return self.server.start(**kwargs)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def xarray(self):
        return self.source.input

    @xarray.setter
    def xarray(self, value):
        self.source.input = value
        self.source.apply_coords()
        self.source.arrays = self.source.available_arrays

        with self.state:
            self.state.fields = self.source.available_arrays
            self.state.active_field = self.source.available_arrays[0]
            self.state.t_idx = self.source.t_index
            self.state.t_max = self.source.t_size - 1

        self.actor.visibility = 1
        self.reset_camera()

    def update(self):
        self.ctrl.view_update()

    def reset_camera(self):
        self.ctrl.view_reset_camera()

    # -------------------------------------------------------------------------
    # Reactive API
    # -------------------------------------------------------------------------

    @change("active_field")
    def _rescale_colors(self, active_field, **_):
        if self.xarray is None:
            return

        ds = self.source()
        min_value, max_value = ds.point_data[active_field].GetRange(-1)

        self.mapper.SetScalarRange(min_value, max_value)
        self.mapper.SelectColorArray(active_field)
        self.mapper.SetScalarModeToUsePointFieldData()
        self.mapper.InterpolateScalarsBeforeMappingOn()

        self.update()

    @change("t_idx")
    def _on_t_change(self, t_idx, **_):
        self.source.t_index = t_idx
        self.update()

    def refresh_data(self):
        self.state.fields = self.source().point_data.keys()
        self._rescale_colors(self.state.active_field)

    # -------------------------------------------------------------------------
    # GUI definition
    # -------------------------------------------------------------------------

    def _build_ui(self, *args, **kwargs):
        with SinglePageLayout(self.server, full_height=True) as layout:
            self.ui = layout
            client.Style("html, body {  overflow: hidden; }")

            # Toolbar
            with layout.toolbar as tb:
                tb.density = "compact"

                v3.VProgressLinear(
                    indeterminate=True,
                    absolute=True,
                    style="opacity: 0.25;",
                    striped=True,
                    color="primary",
                    height=60,
                    active=("trame__busy",),
                )

                with layout.title as title:
                    title.set_text("Pan3D: Data Viewer")
                    title.style = "flex: none;"
                    self.state.trame__title = "Data Viewer"

                v3.VSpacer()
                v3.VSelect(
                    v_model=("active_field", None),
                    items=("fields", []),
                    density="compact",
                    hide_details=True,
                    style="max-width: 20vw;",
                )
                v3.VBtn(
                    icon="mdi-refresh",
                    click=(self.refresh_data),
                )
                v3.VSpacer()

                v3.VBtn(
                    icon="mdi-crop-free",
                    click=self.ctrl.view_reset_camera,
                    classes="ml-4",
                )

            # Footer
            if not self.server.hot_reload:
                layout.footer.hide()

            # Content
            with layout.content:
                with v3.VContainer(fluid=True, classes="fill-height pa-0"):
                    with vtkw.VtkRemoteView(
                        self.render_window, interactive_ratio=1
                    ) as view:
                        self.ctrl.view_update = view.update
                        self.ctrl.view_reset_camera = view.reset_camera

                    v3.VSlider(
                        v_model=("t_idx", 0),
                        max=("t_max", 0),
                        min=0,
                        step=1,
                        hide_details=True,
                        v_show="t_max > 0",
                        style="z-index: 1; position: absolute; bottom: 0.5rem; left: 1rem; right: 1rem;",
                    )


def main():
    app = XArrayViewer()
    app.server.start()


if __name__ == "__main__":
    main()
