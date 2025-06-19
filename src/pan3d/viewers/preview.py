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

from pan3d.ui.preview import RenderingSettings
from pan3d.ui.vtk_view import Pan3DView
from pan3d.utils.common import ControlPanel, Explorer, SummaryToolbar
from pan3d.utils.convert import to_float
from pan3d.widgets.scalar_bar import ScalarBar
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3


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

    # -------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------

    def _build_ui(self, **kwargs):
        self.state.trame__title = "XArray Viewer"

        with VAppLayout(self.server, fill_height=True) as layout:
            self.ui = layout

            # 3D view
            Pan3DView(
                self.render_window,
                local_rendering=self.local_rendering,
                widgets=[self.widget],
            )

            # Scalar bar
            ScalarBar(
                ctx_name="scalar_bar",
                v_show="!control_expended",
                v_if="color_by",
            )

            # Save dialog
            with v3.VDialog(v_model=("show_save_dialog", False)):
                with v3.VCard(classes="mx-auto w-50"):
                    v3.VCardTitle("Save dataset to disk")
                    v3.VDivider()
                    with v3.VCardText():
                        v3.VTextField(
                            label="File path to save",
                            v_model=("save_dataset_path", ""),
                            hide_details=True,
                        )
                    with v3.VCardActions():
                        v3.VSpacer()
                        v3.VBtn(
                            "Save",
                            classes="text-none",
                            variant="flat",
                            color="primary",
                            click=(self.save_dataset, "[save_dataset_path]"),
                        )
                        v3.VBtn(
                            "Cancel",
                            classes="text-none",
                            variant="flat",
                            click="show_save_dialog=false",
                        )

            # Error messages
            v3.VAlert(
                v_if=("data_origin_error", False),
                border="start",
                max_width=700,
                rounded="lg",
                text=("data_origin_error", ""),
                title="Failed to load data",
                type="error",
                variant="tonal",
                style="position:absolute;bottom:1rem;right:1rem;",
            )

            # Summary toolbar
            SummaryToolbar(
                v_show="!control_expended",
                v_if="slice_t_max > 0",
            )

            # Control panel
            with ControlPanel(
                enable_data_selection=(self.xarray is None),
                toggle="control_expended",
                load_dataset=self.load_dataset,
                import_file_upload=self.import_file_upload,
                export_file_download=self.export_state,
                xr_update_info="xr_update_info",
            ).ui_content:
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
