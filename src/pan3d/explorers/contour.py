from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkActor,
    vtkPolyDataMapper,
)
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkDataSetAttributes
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkFiltersCore import vtkCellDataToPointData, vtkTriangleFilter
from vtkmodules.vtkFiltersModeling import (
    vtkBandedPolyDataContourFilter,
    vtkLoopSubdivisionFilter,
)
from vtkmodules.vtkFiltersCore import vtkAssignAttribute
from vtkmodules.vtkCommonCore import vtkLookupTable

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

from pan3d.xarray.algorithm import vtkXArrayRectilinearSource

from trame.decorators import change

from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3

from pan3d.utils.convert import to_float, to_image
from pan3d.utils.presets import set_preset
from pan3d.utils.common import Explorer, SummaryToolbar, ControlPanel

from pan3d.ui.vtk_view import Pan3DView, Pan3DScalarBar

from pan3d.ui.contour import ContourRenderingSettings


class ContourExplorer(Explorer):
    def __init__(self, xarray=None, source=None, server=None, local_rendering=None):
        super().__init__(xarray, source, server, local_rendering)
        self.xarray = xarray

        # setup
        self.last_field = None
        self.last_preset = None

        self._setup_vtk()
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self):
        self.source = vtkXArrayRectilinearSource(input=self.xarray)

        ds = self.source()

        self.lut = vtkLookupTable()

        self.renderer = vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # Need explicit geometry extraction when used with WASM
        self.geometry = vtkDataSetSurfaceFilter(
            input_connection=self.source.output_port
        )
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
            lookup_table=self.lut,
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

    def _build_ui(self, **kwargs):
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
            Pan3DScalarBar(
                v_show="!control_expended",
                v_if="color_by",
                img_src="preset_img",
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
                self.ctrl.source_update_rendering_panel = ContourRenderingSettings(
                    self.source,
                    self.update_rendering,
                ).update_from_source

    def update_rendering(self, reset_camera=False):
        self.renderer.ResetCamera()

        if self.local_rendering:
            self.ctrl.view_update(push_camera=True)

        self.ctrl.view_reset_camera()

    def reset_color_range(self):
        if self.state.color_by is None:
            return

        field_array = self.source.input[self.state.color_by].values
        with self.state:
            self.state.color_min = float(field_array.min())
            self.state.color_max = float(field_array.max())

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

    @change("color_by", "time_idx")
    def _on_update_data(self, color_by, time_idx, **_):
        if self.source.input is None:
            return

        self.source.t_index = time_idx
        self.source.arrays = [color_by]
        self.assign.Assign(
            color_by,
            vtkDataSetAttributes.SCALARS,
            vtkDataObject.FIELD_ASSOCIATION_POINTS,
        )
        self.mapper.SelectColorArray(color_by)
        self.mapper.Update()
        # update range
        if self.last_field != color_by:
            self.last_field = color_by
            self.reset_color_range()

        self.ctrl.view_update()

    @change("color_min", "color_max", "color_preset", "nan_color", "nb_contours")
    def _on_update_color_range(
        self, nb_contours, color_min, color_max, color_preset, **_
    ):
        if self.last_preset != color_preset:
            self.last_preset = color_preset
            set_preset(self.lut, color_preset)
            self.state.preset_img = to_image(self.lut, 255)

        self.mapper.SetScalarRange(color_min, color_max)
        self.bands.GenerateValues(nb_contours, [color_min, color_max])
        self.ctrl.view_update()


def main():
    app = ContourExplorer()
    app.server.start()


if __name__ == "__main__":
    main()
