import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleSwitch,  # noqa: F401
    vtkInteractorStyleTerrain,
)
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from pan3d.filters.globe import ProjectToSphere
from pan3d.ui.globe import GlobeRenderingSettings
from pan3d.ui.vtk_view import Pan3DView
from pan3d.utils.common import ControlPanel, Explorer, SummaryToolbar
from pan3d.utils.globe import get_continent_outlines, get_globe, get_globe_textures
from pan3d.widgets.scalar_bar import ScalarBar
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3

# Prevent view-up warning
vtkObject.GlobalWarningDisplayOff()


class GlobeExplorer(Explorer):
    """
    A Trame based pan3D explorer to visualize 3D geographic data projected onto a globe
    representing the earth or projected using various cartographic projections.
    The prerequisite is that the coordinates of the dataset need to be in lat-long format.
    This explorer uses the pan3D DatasetBuilder and it's operability with xarray to fetch
    relevant data and visualizes it using VTK while interacting with the slice in 2D or 3D.
    """

    def __init__(
        self, xarray=None, source=None, pipeline=None, server=None, local_rendering=None
    ):
        super().__init__(xarray, source, pipeline, server, local_rendering)
        if self.source is None:
            self.source = vtkXArrayRectilinearSource()  # To initialize the pipeline
        self.textures = get_globe_textures()
        self.state.textures = list(self.textures.keys())

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
        self.interactor.SetInteractorStyle(vtkInteractorStyleTerrain())

        self.globe = get_globe()
        self.gmapper = vtkPolyDataMapper(input_data_object=self.globe)
        self.gactor = vtkActor(mapper=self.gmapper, visibility=1)

        self.continents = get_continent_outlines()
        self.cmapper = vtkPolyDataMapper(input_data_object=self.continents)
        self.cactor = vtkActor(mapper=self.cmapper, visibility=1)

        tail = self.extend_pipeline(head=self.source, pipeline=pipeline)

        dglobe = ProjectToSphere()
        dglobe.isData = True
        dglobe.input_connection = tail.output_port
        self.dglobe = dglobe
        # Need explicit geometry extraction when used with WASM
        self.geometry = vtkGeometryFilter(input_connection=self.dglobe.output_port)

        self.mapper = vtkPolyDataMapper(input_connection=self.geometry.output_port)
        self.actor = vtkActor(mapper=self.mapper, visibility=0)

        # Camera
        camera = self.renderer.GetActiveCamera()
        camera.SetFocalPoint(0, 0, 0)
        camera.SetPosition(0, -1, 0)
        camera.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()

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
                "trame__title": "Globe Viewer",
                "slice_extents": {},
                "axis_names": [],
                "t_labels": [],
                "max_time_width": 0,
                "max_time_index_width": 0,
                "dataset_bounds": [0, 1, 0, 1, 0, 1],
                "render_shadow": False,
            }
        )
        with VAppLayout(self.server, fill_height=True) as layout:
            self.ui = layout

            # 3D view
            Pan3DView(
                self.render_window,
                local_rendering=self.local_rendering,
                widgets=[self.widget],
                disable_style_toggle=True,
                disable_roll=True,
                disable_axis_align=True,
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

            with ControlPanel(
                enable_data_selection=(self.xarray is None),
                source=self.source,
                toggle="control_expended",
                load_dataset=self.load_dataset,
                import_file_upload=self.import_file_upload,
                export_file_download=self.export_state,
                xr_update_info="xr_update_info",
                panel_label="Globe Explorer",
            ).ui_content:
                GlobeRenderingSettings(
                    ctx_name="rendering",
                    source=self.source,
                    update_rendering=self.update_rendering,
                )

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("opacity", "representation", "cell_size", "render_shadow")
    def _on_change_opacity(
        self, representation, opacity, cell_size, render_shadow, **_
    ):
        property = self.actor.property
        property.render_lines_as_tubes = render_shadow
        property.render_points_as_spheres = render_shadow
        property.line_width = cell_size
        property.point_size = cell_size
        property.opacity = float(opacity) if representation == 2 else 1
        property.representation = representation

        self.ctrl.view_update()

    @change("bump_radius")
    def _on_bump_radius_change(self, bump_radius, **_):
        self.dglobe.bump_radius = bump_radius
        self.ctrl.view_update()

    @change("texture")
    def _on_texture_preset(self, texture, **_):
        self.gactor.SetTexture(self.textures[texture])
        self.ctrl.view_update()

    def update_rendering(self, reset_camera=False):
        self.state.dirty_data = False

        self.gactor.visibility = 1
        self.gactor.SetTexture(self.textures[self.state.texture])
        self.renderer.AddActor(self.gactor)

        self.cactor.visibility = 1
        self.cactor.GetProperty().SetRepresentationToWireframe()
        self.cactor.GetProperty().SetColor(1.0, 1.0, 1.0)
        self.renderer.AddActor(self.cactor)

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
    app = GlobeExplorer()
    app.start()


if __name__ == "__main__":
    main()
