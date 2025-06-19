import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkDataSetAttributes
from vtkmodules.vtkFiltersCore import (
    vtkAssignAttribute,
    vtkCellDataToPointData,
    vtkTriangleFilter,
)
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersModeling import (
    vtkBandedPolyDataContourFilter,
    vtkLoopSubdivisionFilter,
)

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

from pan3d.ui.contour import ContourRenderingSettings
from pan3d.ui.vtk_view import Pan3DView
from pan3d.utils.common import ControlPanel, Explorer, SummaryToolbar
from pan3d.utils.convert import to_float
from pan3d.widgets.scalar_bar import ScalarBar
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3


class ContourExplorer(Explorer):
    def __init__(
        self, xarray=None, source=None, pipeline=None, server=None, local_rendering=None
    ):
        super().__init__(xarray, source, server, pipeline, local_rendering)

        if self.source is None:
            self.source = vtkXArrayRectilinearSource(
                input=self.xarray
            )  # To initialize the pipeline

        # setup
        self.last_field = None
        self.last_preset = None

        self._setup_vtk(pipeline)
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self, pipeline=None):
        ds = self.source()

        self.renderer = vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # Need explicit geometry extraction when used with WASM
        tail = self.extend_pipeline(head=self.source, pipeline=pipeline)
        self.geometry = vtkGeometryFilter(input_connection=tail.output_port)
        self.triangle = vtkTriangleFilter(input_connection=self.geometry.output_port)
        self.cell2point = vtkCellDataToPointData(
            input_connection=self.triangle.output_port
        )
        self.refine = vtkLoopSubdivisionFilter(
            input_connection=self.cell2point.output_port, number_of_subdivisions=1
        )
        self.assign = vtkAssignAttribute(input_connection=self.refine.output_port)
        self.assign.Assign(
            None,
            vtkDataSetAttributes.SCALARS,
            vtkDataObject.FIELD_ASSOCIATION_POINTS,
        )
        self.bands = vtkBandedPolyDataContourFilter(
            input_connection=self.assign.output_port,
            generate_contour_edges=1,
        )
        self.mapper = vtkPolyDataMapper(
            input_connection=self.bands.output_port,
            scalar_visibility=1,
            interpolate_scalars_before_mapping=1,
        )
        self.mapper.SetScalarModeToUsePointFieldData()
        self.actor = vtkActor(mapper=self.mapper)

        # contour lines
        self.mapper_lines = vtkPolyDataMapper(
            input_connection=self.bands.GetOutputPort(1),
        )
        self.actor_lines = vtkActor(mapper=self.mapper_lines)
        self.actor_lines.property.color = [0, 0, 0]
        self.actor_lines.property.line_width = 2

        self.renderer.AddActor(self.actor)
        self.renderer.AddActor(self.actor_lines)

        self.renderer.ResetCamera(ds.bounds)

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

    def _build_ui(self, **_):
        self.state.update(
            {
                "trame__title": "Contour Explorer",
                "import_pending": False,
                "control_expended": True,
                "axis_names": ["X", "Y", "Z"],
                "scale_x": 1,
                "scale_y": 1,
                "scale_z": 0.01,
            }
        )
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
                source=self.source,
                toggle="control_expended",
                load_dataset=self.load_dataset,
                import_file_upload=self.import_file_upload,
                export_file_download=self.export_state,
                xr_update_info="xr_update_info",
                panel_label="Contour Explorer",
            ).ui_content:
                ContourRenderingSettings(
                    ctx_name="rendering",
                    source=self.source,
                    update_rendering=self.update_rendering,
                )

    def update_rendering(self, reset_camera=False):
        self.renderer.ResetCamera()

        if self.local_rendering:
            self.ctrl.view_update(push_camera=True)

        self.ctrl.view_reset_camera()

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
        self.actor_lines.SetScale(
            to_float(scale_x),
            to_float(scale_y),
            to_float(scale_z),
        )
        self.renderer.ResetCamera()

        if self.local_rendering:
            self.ctrl.view_update(push_camera=True)

        self.ctrl.view_reset_camera()

    @change("color_by", "nb_contours", "color_min", "color_max")
    def _on_color_by_change(
        self, color_by, nb_contours, color_min, color_max, **kwargs
    ):
        self.assign.Assign(
            color_by,
            vtkDataSetAttributes.SCALARS,
            vtkDataObject.FIELD_ASSOCIATION_POINTS,
        )
        self.bands.GenerateValues(nb_contours, [color_min, color_max])
        super()._on_color_properties_change(**kwargs)


def main():
    app = ContourExplorer()
    app.server.start()


if __name__ == "__main__":
    main()
