from vtkmodules.vtkCommonCore import vtkLookupTable

from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkDataSetMapper,
    vtkActor,
    vtkPolyDataMapper,
)

from vtkmodules.vtkRenderingAnnotation import (
    vtkAxesActor,
)
from vtkmodules.vtkCommonDataModel import (
    vtkPlane,
)
from vtkmodules.vtkFiltersModeling import (
    vtkOutlineFilter,
)
from vtkmodules.vtkFiltersCore import (
    vtkCutter,
)

from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

from pan3d.xarray.algorithm import vtkXArrayRectilinearSource

from trame_client.widgets.core import TrameDefault
from trame.decorators import change
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3, html

from pan3d.utils.convert import to_image
from pan3d.utils.presets import set_preset
from pan3d.utils.common import Explorer, SummaryToolbar, ControlPanel

from pan3d.ui.vtk_view import Pan3DView, Pan3DScalarBar
from pan3d.ui.slicer import SliceRenderingSettings


class SliceExplorer(Explorer):
    """
    A Trame based pan3D explorer to visualize 3D using slices along different dimensions

    This explorer uses the pan3D DatasetBuilder and it's operability with xarray to fetch
    relevant data and allows users to specify a specific slice of interest and visualize it
    using VTK while interacting with the slice in 2D or 3D.
    """

    def __init__(self, xarray=None, source=None, server=None, local_rendering=None):
        super().__init__(xarray, source, server, local_rendering)
        self.xarray = xarray

        self._setup_vtk()
        self._build_ui()

    def _setup_vtk(self):
        self.source = vtkXArrayRectilinearSource(self.xarray)

        ds = self.source()
        bounds = ds.bounds
        self.normal = [0, 0, 1]
        self.origin = [
            0.5 * (bounds[0] + bounds[1]),
            0.5 * (bounds[2] + bounds[3]),
            0.5 * (bounds[4] + bounds[5]),
        ]

        # Create lookup table
        self.lut = vtkLookupTable()

        # Build rendering pipeline
        self.renderer = vtkRenderer()
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow()

        plane = vtkPlane()
        plane.SetOrigin(self.origin)
        plane.SetNormal(self.normal)
        cutter = vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.input_connection = self.source.output_port
        slice_actor = vtkActor()
        slice_mapper = vtkDataSetMapper(lookup_table=self.lut)
        slice_mapper.SetInputConnection(cutter.GetOutputPort())
        slice_mapper.SetScalarModeToUsePointFieldData()
        slice_mapper.InterpolateScalarsBeforeMappingOn()
        slice_actor.SetMapper(slice_mapper)
        self.plane = plane
        self.cutter = cutter
        self.slice_actor = slice_actor
        self.slice_mapper = slice_mapper

        outline = vtkOutlineFilter()
        outline_actor = vtkActor()
        outline_mapper = vtkPolyDataMapper(lookup_table=self.lut)
        outline.input_connection = self.source.output_port
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        self.outline = outline
        self.outline_actor = outline_actor
        self.outline_mapper = outline_mapper

        data_actor = vtkActor()
        data_mapper = vtkDataSetMapper(lookup_table=self.lut)
        data_mapper.input_connection = self.source.output_port
        data_actor.SetMapper(data_mapper)
        data_actor.GetProperty().SetOpacity(0.1)
        data_actor.SetVisibility(False)
        self.data_actor = data_actor
        self.data_mapper = data_mapper

        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.render_window.OffScreenRenderingOn()
        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.renderer.AddActor(self.outline_actor)
        self.renderer.AddActor(self.data_actor)
        self.renderer.AddActor(self.slice_actor)

        axes_actor = vtkAxesActor()
        self.widget = vtkOrientationMarkerWidget()
        self.widget.SetOrientationMarker(axes_actor)
        self.widget.SetInteractor(self.interactor)
        self.widget.SetViewport(0.85, 0, 1, 0.15)
        self.widget.EnabledOn()
        self.widget.InteractiveOff()

    # -------------------------------------------------------------------------
    # GUI definition
    # -------------------------------------------------------------------------

    def _build_ui(self, *args, **kwargs):
        self.state.update(
            {
                "trame__title": "Slice Explorer",
                "import_pending": False,
                "control_expended": True,
                "axis_names": ["X", "Y", "Z"],
                "scale_x": 1,
                "scale_y": 1,
                "scale_z": 1,
                "cut_x": 0.5,
                "cut_y": 0.5,
                "cut_z": 0.5,
                "bounds": [0.0, 1.0, 0.0, 1.0, 0.0, 1.0],
                "slice_axis": "Z",
            }
        )
        with VAppLayout(self.server, fill_height=True) as layout:
            self.ui = layout

            with v3.VCard(
                classes="pa-1 align-center justify-center",
                rounded="lg",
                style="""
                          position: absolute;
                          top: 50%;
                          right: 1rem;
                          opacity: 0.8;
                          display: flex;
                          flex-direction: column;
                          z-index: 1;
                          """,
            ):
                with v3.VTooltip(text="Data Representation Mode"):
                    with html.Template(v_slot_activator="{ props }"):
                        with v3.VBtnToggle(
                            v_bind="props",
                            v_model=(
                                "representation_mode",
                                TrameDefault(
                                    representation_mode=["outline"],
                                    outline=True,
                                    tdata=False,
                                ),
                            ),
                            multiple=True,
                            variant="outlined",
                            disabled=("view_mode === '2D'",),
                            style="flex-direction: column;",
                        ):
                            v3.VBtn(
                                icon="mdi-cube-outline",
                                value="outline",
                                click="outline = !outline",
                            )
                            v3.VBtn(
                                icon="mdi-texture-box",
                                value="transparent",
                                click="tdata = !tdata",
                            )
                v3.VDivider(classes="my-2")
                with v3.VTooltip(text="Slice View Mode (2D/3D)"):
                    with html.Template(v_slot_activator="{ props }"):
                        with v3.VBtnToggle(
                            v_bind="props",
                            v_model=("view_mode", "3D"),
                            mandatory=True,
                            variant="outlined",
                            style="flex-direction: column;",
                        ):
                            v3.VBtn(icon="mdi-video-2d", value="2D")
                            v3.VBtn(icon="mdi-video-3d", value="3D")

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
                panel_label="Slice Explorer",
            ).ui_content:
                self.ctrl.source_update_rendering_panel = SliceRenderingSettings(
                    self.source,
                    self.update_rendering,
                ).update_from_source

    def update_rendering(self, reset_camera=False):
        self.renderer.ResetCamera()

        if self.local_rendering:
            self.ctrl.view_update(push_camera=True)

        self.ctrl.view_reset_camera()

    # -------------------------------------------------------------------------
    # Property API
    # -------------------------------------------------------------------------

    @property
    def slice_axis(self):
        """
        Returns the active axis along which the slice is performed
        """
        return self.state.slice_axis

    @slice_axis.setter
    def slice_axis(self, axis: str) -> None:
        """
        Sets the active axis along which the slice is performed
        """
        with self.state:
            self.state.slice_axis = axis

    @property
    def slice_value(self):
        """
        Returns the value(origin) for the dimension along which the slice
        is performed
        """
        s = self.state
        axis = "xyz"[s.slice_axes.index(s.slice_axis)]
        return s[f"cut_{axis}"]

    @slice_value.setter
    def slice_value(self, value: float) -> None:
        """
        Sets the value(origin) for the dimension along which the slice
        is performed
        """
        with self.state:
            s = self.state
            axis = "xyz"[s.slice_axes.index(s.slice_axis)]
            s[f"cut_{axis}"] = value

    @property
    def view_mode(self):
        """
        Returns the interaction mode (2D/3D) for the slice
        """
        return self.state.view_mode

    @view_mode.setter
    def view_mode(self, mode):
        """
        Sets the interaction mode (2D/3D) for the slice,
        and updates camera accordingly. Uses isometric view for 3D
        """
        with self.state:
            self.state.view_mode = mode

    @property
    def scale_axis(self):
        s = self.state
        return [s.x_scale, s.y_scale, s.z_scale]

    @scale_axis.setter
    def scale_axis(self, sfac):
        s = self.state
        s.x_scale = float(sfac[0])
        s.y_scale = float(sfac[1])
        s.z_scale = float(sfac[2])
        self.slice_actor.SetScale(*sfac)
        self.data_actor.SetScale(*sfac)
        self.outline_actor.SetScale(*sfac)
        self.on_view_mode_change(s.view_mode)

    @property
    def color_map(self):
        """
        Returns the color map currently used for visualization
        """
        return self.state.cmap

    @color_map.setter
    def color_map(self, cmap):
        """
        Sets the color map used for visualization
        """
        with self.state:
            self.state.cmap = cmap

    # -------------------------------------------------------------------------
    # UI triggers
    # -------------------------------------------------------------------------

    @change("scale_x", "scale_y", "scale_z")
    def _on_scale_change(self, scale_x, scale_y, scale_z, **_):
        scales = [float(scale_x), float(scale_y), float(scale_z)]
        self.slice_actor.SetScale(*scales)
        self.data_actor.SetScale(*scales)
        self.outline_actor.SetScale(*scales)

        self.renderer.ResetCamera()

        self.on_view_mode_change(self.state.view_mode)

    @change("color_by")
    def _on_color_by_change(self, color_by, **_):
        if color_by is None:
            return

        color_min, color_max = self.source().point_data[color_by].GetRange()

        self.slice_mapper.SetScalarRange(color_min, color_max)
        self.slice_mapper.SelectColorArray(color_by)

        self.state.color_min = color_min
        self.state.color_max = color_max

    @change("color_min", "color_max", "color_preset", "nan_color")
    def _on_update_color_range(
        self, color_min, color_max, color_preset, nan_color, nan_colors, **_
    ):
        set_preset(self.lut, color_preset)
        self.state.preset_img = to_image(self.lut, 255)

        color = nan_colors[nan_color]
        self.lut.SetNanColor(color)

        color_min = float(color_min)
        color_max = float(color_max)
        self.slice_mapper.SetScalarRange(color_min, color_max)
        self.ctrl.view_update()

    def _set_view_2D(self, axis):
        camera = self.renderer.GetActiveCamera()
        view_up = [0, 0, 1] if axis == 1 else [0, 1, 0]
        direction = [0, 0, 0]
        direction[axis] = 1
        camera.SetFocalPoint(0, 0, 0)
        camera.SetPosition(*direction)
        camera.SetViewUp(*view_up)
        camera.OrthogonalizeViewUp()

        self.outline_actor.SetVisibility(False)
        self.data_actor.SetVisibility(False)

        self.renderer.ResetCamera()
        self.ctrl.view_update()

    def _set_view_3D(self):
        if self.state.outline:
            self.outline_actor.SetVisibility(True)
        if self.state.tdata:
            self.data_actor.SetVisibility(True)

        self.renderer.ResetCamera()
        self.ctrl.view_update()

    @change("view_mode")
    def on_view_mode_change(self, view_mode, **_):
        """
        Performs all the steps necessary when user toggles the view mode
        """
        if view_mode == "3D":
            self._set_view_3D()
        elif view_mode == "2D":
            s = self.state
            axis_idx = s.axis_names.index(s.slice_axis)
            self._set_view_2D(axis_idx)

    @change("slice_axis", "slice_t", "cut_x", "cut_y", "cut_z")
    def _on_data_change(
        self, slice_axis, axis_names, slice_t, cut_x, cut_y, cut_z, **_
    ):
        """
        Performs all the steps necessary when the user updates any properties
        that requires a new data update. E.g. changing the data variable for
        visualization, or changing active time, or changing slice value.
        """
        normal = [0, 0, 0]
        normal[axis_names.index(slice_axis)] = 1
        origin = [
            float(cut_x),
            float(cut_y),
            float(cut_z),
        ]

        self.source.t_index = slice_t
        self.plane.SetOrigin(origin)
        self.plane.SetNormal(normal)

        if self.state.view_mode == "2D":
            self.on_view_mode_change("2D")
            self.renderer.ResetCamera()

        self.ctrl.view_update()

    @change("outline", "tdata")
    def _on_rep_change(self, outline, tdata, **_):
        """
        Performs all the steps necessary when user specifies 3D interaction options
        """
        self.outline_actor.SetVisibility(outline)
        self.data_actor.SetVisibility(tdata)
        self.ctrl.view_update()


def main():
    app = SliceExplorer()
    app.start()


if __name__ == "__main__":
    main()
