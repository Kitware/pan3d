import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from pan3d.ui.layouts import StandardExplorerLayout
from pan3d.ui.preview import RenderingSettings
from pan3d.utils.common import Explorer
from pan3d.utils.convert import to_float
from pan3d.widgets.pan3d_view import Pan3DView
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change


class XArrayViewer(Explorer):
    """Create a Trame GUI for a Pan3D XArray Viewer"""

    def __init__(
        self, xarray=None, source=None, pipeline=None, server=None, local_rendering=None
    ):
        """Create an instance of the XArrayViewer class."""
        super().__init__(xarray, source, pipeline, server, local_rendering)
        self.xarray = xarray

        self._setup_vtk(pipeline)
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self, pipeline=None):
        self.renderer = vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.source = vtkXArrayRectilinearSource(input=self.xarray)

        tail = self.extend_pipeline(head=self.source, pipeline=pipeline)

        self.geometry = vtkGeometryFilter(input_connection=tail.output_port)

        self.mapper = vtkPolyDataMapper(
            input_connection=self.geometry.output_port,
        )
        self.actor = vtkActor(mapper=self.mapper, visibility=0)

        self.interactor.Initialize()

        axes_actor = vtkAxesActor()
        self.widget = vtkOrientationMarkerWidget()
        self.widget.SetOrientationMarker(axes_actor)
        self.widget.SetInteractor(self.interactor)
        self.widget.SetViewport(0.85, 0, 1, 0.15)
        self.widget.EnabledOn()
        self.widget.InteractiveOff()

        if self.anari:
            from pan3d.utils import anari

            anari.setup(self.renderer)

    # -------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------

    def _build_ui(self, **kwargs):
        self.state.trame__title = "XArray Viewer"

        # Use the standard UI creation method
        with StandardExplorerLayout(explorer=self, title="XArray Viewer") as self.ui:
            with self.ui.content:
                Pan3DView(
                    render_window=self.render_window,
                    local_rendering=self.local_rendering,
                    widgets=[self.widget],
                )
            with self.ui.control_panel:
                RenderingSettings(
                    ctx_name="rendering",
                    source=self.source,
                    update_rendering=self.update_rendering,
                )

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("scale_x", "scale_y", "scale_z")
    def _on_scale_change(self, scale_x, scale_y, scale_z, **_):
        self.actor.SetScale(
            to_float(scale_x),
            to_float(scale_y),
            to_float(scale_z),
        )

        if self.state.import_pending:
            return

        if self.actor.visibility:
            self.renderer.ResetCamera()

            if self.local_rendering:
                self.ctrl.view_update(push_camera=True)

            self.ctrl.view_reset_camera()

    # -----------------------------------------------------
    # Triggers
    # -----------------------------------------------------

    def update_rendering(self, reset_camera=False):
        self.state.dirty_data = False

        if self.actor.visibility == 0:
            self.actor.visibility = 1
            self.renderer.AddActor(self.actor)
            self.renderer.ResetCamera()
            if self.ctrl.view_update_force.exists():
                self.ctrl.view_update_force(push_camera=True)

        if reset_camera:
            self.ctrl.view_reset_camera()
        else:
            self.ctrl.view_update()


# -----------------------------------------------------------------------------
# Main executable
# -----------------------------------------------------------------------------


def main():
    app = XArrayViewer()
    app.start()


if __name__ == "__main__":
    main()
