from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper,
    vtkActor,
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
)

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTerrain
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonCore import vtkLookupTable, vtkObject

import json
import traceback
from pathlib import Path

from trame.decorators import change
from trame.app import asynchronous

from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3

from pan3d.xarray.algorithm import vtkXArrayRectilinearSource

from pan3d.utils.convert import update_camera, to_image
from pan3d.utils.presets import set_preset

from pan3d.ui.vtk_view import Pan3DView, Pan3DScalarBar
from pan3d.ui.globe import GlobeRenderingSettings

from pan3d.utils.common import Explorer, SummaryToolbar, ControlPanel

from pan3d.filters.globe import ProjectToSphere
from pan3d.utils.globe import get_globe, get_globe_textures, get_continent_outlines

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

    def __init__(self, xarray=None, source=None, server=None, local_rendering=None):
        super().__init__(xarray, source, server, local_rendering)
        self.xarray = xarray

        self.textures = get_globe_textures()
        self.state.textures = list(self.textures.keys())

        self._setup_vtk()
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self):
        self.lut = vtkLookupTable()

        self.renderer = vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.SetInteractorStyle(vtkInteractorStyleTerrain())

        self.source = vtkXArrayRectilinearSource(input=self.xarray)

        self.globe = get_globe()
        self.gmapper = vtkPolyDataMapper(input_data_object=self.globe)
        self.gactor = vtkActor(mapper=self.gmapper, visibility=1)

        self.continents = get_continent_outlines()
        self.cmapper = vtkPolyDataMapper(input_data_object=self.continents)
        self.cactor = vtkActor(mapper=self.cmapper, visibility=1)

        dglobe = ProjectToSphere()
        dglobe.isData = True
        dglobe.input_connection = self.source.output_port
        self.dglobe = dglobe
        # Need explicit geometry extraction when used with WASM
        self.geometry = vtkDataSetSurfaceFilter(
            input_connection=self.dglobe.output_port
        )

        self.mapper = vtkPolyDataMapper(
            input_connection=self.geometry.output_port, lookup_table=self.lut
        )
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
                self.ctrl.source_update_rendering_panel = GlobeRenderingSettings(
                    self.source,
                    self.update_rendering,
                ).update_from_source

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("color_by")
    def _on_color_by(self, color_by, **__):
        if self.source.input is None:
            return

        ds = self.source()
        if color_by in ds.point_data.keys():
            array = ds.point_data[color_by]
            min_value, max_value = array.GetRange()

            self.state.color_min = min_value
            self.state.color_max = max_value

            self.mapper.SelectColorArray(color_by)
            self.mapper.SetScalarModeToUsePointFieldData()
            self.mapper.InterpolateScalarsBeforeMappingOn()
            self.mapper.SetScalarVisibility(1)
        else:
            self.mapper.SetScalarVisibility(0)
            self.state.color_min = 0
            self.state.color_max = 1

    @change("color_preset", "color_min", "color_max", "nan_color")
    def _on_color_preset(
        self,
        nan_color,
        nan_colors,
        color_preset,
        color_min,
        color_max,
        opacity,
        **_,
    ):
        color_min = float(color_min)
        color_max = float(color_max)
        self.mapper.SetScalarRange(color_min, color_max)

        set_preset(self.lut, color_preset)
        self.state.preset_img = to_image(self.lut, 255)

        color = nan_colors[nan_color]
        self.lut.SetNanColor(color)

        self.ctrl.view_update()

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

    @change("data_origin_order")
    def _on_order_change(self, **_):
        if self.state.import_pending:
            return

        self.state.load_button_text = "Load"
        self.state.can_load = True

    # -----------------------------------------------------
    # Triggers
    # -----------------------------------------------------
    def _import_file_upload(self, files):
        self.import_state(json.loads(files[0].get("content")))

    def _process_cli(self, **_):
        args, _ = self.server.cli.parse_known_args()

        # Skip if xarray provided
        if self.source.input:
            if not self.source.arrays:
                self.source.arrays = self.source.available_arrays
            self.ctrl.xr_update_info(self.source.input, self.source.available_arrays)
            self.ctrl.source_update_rendering_panel(self.source)
            self._update_rendering(reset_camera=True)
            self.state.show_rendering = True
            return

        # import state
        if args.import_state:
            self._import_file_from_path(args.import_state)

        # load xarray (file)
        elif args.xarray_file:
            self.state.import_pending = True
            with self.state:
                self._load_dataset("file", args.xarray_file)
                self.state.data_origin_id = str(Path(args.xarray_file).resolve())
            self.state.import_pending = False

        # load xarray (url)
        elif args.xarray_url:
            self.state.import_pending = True
            with self.state:
                self._load_dataset("url", args.xarray_url)
                self.state.data_origin_id = args.xarray_url
            self.state.import_pending = False

    def _import_file_from_path(self, file_path):
        if file_path is None:
            return

        file_path = Path(file_path)
        if file_path.exists():
            self.import_state(json.loads(file_path.read_text("utf-8")))

    def _load_dataset(self, source, id, order="C", config=None):
        self.state.data_origin_source = source
        self.state.data_origin_id = id
        self.state.load_button_text = "Loaded"
        self.state.can_load = False
        self.state.show_data_information = True

        if config is None:
            config = {
                "arrays": [],
                "slices": {},
            }

        try:
            self.source.load(
                {
                    "data_origin": {
                        "source": source,
                        "id": id,
                        "order": order,
                    },
                    "dataset_config": config,
                }
            )
            if self.actor.visibility:
                self.renderer.RemoveActor(self.actor)
                self.actor.visibility = 0

            # Make sure arrays are available
            if not self.source.arrays:
                self.source.arrays = self.source.available_arrays

            # Extract UI
            self.ctrl.xr_update_info(self.source.input, self.source.available_arrays)
            self.ctrl.source_update_rendering_panel(self.source)

            # no error
            self.state.data_origin_error = False
        except Exception as e:
            self.state.data_origin_error = (
                f"Error occurred while trying to load data. {e}"
            )
            self.state.data_origin_id_error = True
            self.state.load_button_text = "Load"
            self.state.can_load = True
            self.state.show_data_information = False

            print(traceback.format_exc())

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

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def export_state(self):
        """Return a json dump of the reader and viewer state"""
        camera = self.renderer.active_camera
        state_to_export = {
            **self.source.state,
            "xr-globe": {
                "view_3d": self.state.view_3d,
                "color_by": self.state.color_by,
                "color_preset": self.state.color_preset,
                "color_min": self.state.color_min,
                "color_max": self.state.color_max,
                "scale_x": self.state.scale_x,
                "scale_y": self.state.scale_y,
                "scale_z": self.state.scale_z,
            },
            "camera": {
                "position": camera.position,
                "view_up": camera.view_up,
                "focal_point": camera.focal_point,
                "parallel_projection": camera.parallel_projection,
                "parallel_scale": camera.parallel_scale,
            },
        }
        return json.dumps(state_to_export, indent=2)

    def import_state(self, data_state):
        """
        Read the current state to load the data and visualization setup if any.

        Parameters:
            - data_state (dict): reader (+viewer) state to reset to
        """
        self.state.import_pending = True
        try:
            data_origin = data_state.get("data_origin")
            source = data_origin.get("source")
            id = data_origin.get("id")
            order = data_origin.get("order", "C")
            config = data_state.get("dataset_config")
            globe_state = data_state.get("xr-globe", {})
            camera_state = data_state.get("camera", {})

            # load data and initial rendering setup
            with self.state:
                self._load_dataset(source, id, order, config)
                self.state.update(globe_state)

            # override computed color range using state values
            with self.state:
                self.state.update(globe_state)

            # update camera and render
            update_camera(self.renderer.active_camera, camera_state)
            self._update_rendering()
        finally:
            self.state.import_pending = False

    async def _save_dataset(self, file_path):
        output_path = Path(file_path).resolve()
        self.source.input.to_netcdf(output_path)

    def save_dataset(self, file_path):
        """
        Write XArray data into a file using a background task.
        So when used programmatically, make sure you await the returned task.

        Parameters:
            - file_path (str): path to use for writing the file

        Returns:
            writing task
        """
        self.state.show_save_dialog = False
        return asynchronous.create_task(self._save_dataset(file_path))

    async def _async_display(self):
        await self.ui.ready
        self.ui._ipython_display_()

    def _ipython_display_(self):
        asynchronous.create_task(self._async_display())


# -----------------------------------------------------------------------------
# Main executable
# -----------------------------------------------------------------------------


def main():
    app = GlobeExplorer()
    app.start()


if __name__ == "__main__":
    main()
