import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from vtkmodules.vtkCommonDataModel import (
    vtkPlane,
)
from vtkmodules.vtkFiltersCore import (
    vtkCutter,
)
from vtkmodules.vtkFiltersModeling import (
    vtkOutlineFilter,
)

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import (
    vtkAxesActor,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from pan3d.ui.slicer import SliceRenderingSettings
from pan3d.ui.vtk_view import Pan3DView
from pan3d.utils.common import ControlPanel, Explorer, SummaryToolbar
from pan3d.widgets.scalar_bar import ScalarBar
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class Pan3DSlicerView(Pan3DView):
    def __init__(self, render_window, **kwargs):
        super().__init__(render_window=render_window, **kwargs)
        with self.toolbar:
            v3.VDivider()
            with v3.VTooltip(text="Slice View Mode (2D/3D)"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VCheckbox(
                        v_bind="props",
                        v_model=("view_mode", "3D"),
                        true_icon="mdi-video-2d",
                        false_icon="mdi-video-3d",
                        density="compact",
                        hide_details=True,
                        true_value="2D",
                        false_value="3D",
                    )
            v3.VDivider()
            with v3.VTooltip(text="Outline 3D Data Extents"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VCheckbox(
                        v_bind="props",
                        v_model=("outline", True),
                        true_icon="mdi-cube-outline",
                        false_icon="mdi-cube-outline",
                        density="compact",
                        hide_details=True,
                        disabled=("view_mode === '2D'",),
                    )
            with v3.VTooltip(text="Use Transparency for 3D Data"):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VCheckbox(
                        v_bind="props",
                        v_model=("tdata", True),
                        true_icon="mdi-texture-box",
                        false_icon="mdi-texture-box",
                        density="compact",
                        hide_details=True,
                        disabled=("view_mode === '2D'",),
                    )


class SliceSummary(html.Div):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self:
            html.Div(
                "{{slice_axis}}",
                classes="text-subtitle-1 text-capitalize text-left",
                style="transform-origin: 50% 50%; transform: rotate(-90deg) translateX(-100%) translateY(-1rem); position: absolute;",
            )
            html.Div(
                "{{parseFloat(bounds[slice_axes.indexOf(slice_axis)*2 + 1]).toFixed(2)}}",
                classes="text-subtitle-1 mx-1",
            )
            v3.VSlider(
                v_show="slice_axis === slice_axes[0]",
                thumb_label="always",
                thumb_size=16,
                style="pointer-events: auto;",
                hide_details=True,
                classes="flex-fill",
                direction="vertical",
                v_model=("cut_x",),
                min=("bounds[0]",),
                max=("bounds[1]",),
            )
            v3.VSlider(
                v_show="slice_axis === slice_axes[1]",
                thumb_label="always",
                thumb_size=16,
                style="pointer-events: auto;",
                hide_details=True,
                classes="flex-fill",
                direction="vertical",
                v_model=("cut_y",),
                min=("bounds[2]",),
                max=("bounds[3]",),
            )
            v3.VSlider(
                v_show="slice_axis === slice_axes[2]",
                thumb_label="always",
                thumb_size=16,
                style="pointer-events: auto;",
                hide_details=True,
                classes="flex-fill",
                direction="vertical",
                v_model=("cut_z",),
                min=("bounds[4]",),
                max=("bounds[5]",),
            )

            html.Div(
                "{{parseFloat(bounds[slice_axes.indexOf(slice_axis)*2]).toFixed(2)}}",
                classes="text-subtitle-1 mx-1",
            )


class SliceExplorer(Explorer):
    """
    A Trame based pan3D explorer to visualize 3D using slices along different dimensions

    This explorer uses the pan3D DatasetBuilder and it's operability with xarray to fetch
    relevant data and allows users to specify a specific slice of interest and visualize it
    using VTK while interacting with the slice in 2D or 3D.
    """

    def __init__(
        self, xarray=None, source=None, pipeline=None, server=None, local_rendering=None
    ):
        super().__init__(xarray, source, pipeline, server, local_rendering)
        if self.source is None:
            self.source = vtkXArrayRectilinearSource()  # To initialize the pipeline

        self._setup_vtk(pipeline)
        self._build_ui()

    def _setup_vtk(self, pipeline=None):
        ds = self.source()
        bounds = ds.bounds
        self.normal = [0, 0, 1]
        self.origin = [
            0.5 * (bounds[0] + bounds[1]),
            0.5 * (bounds[2] + bounds[3]),
            0.5 * (bounds[4] + bounds[5]),
        ]

        # Build rendering pipeline
        self.renderer = vtkRenderer()
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow()

        tail = self.extend_pipeline(head=self.source, pipeline=pipeline)

        plane = vtkPlane()
        plane.SetOrigin(self.origin)
        plane.SetNormal(self.normal)
        cutter = vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.input_connection = tail.output_port
        slice_actor = vtkActor()
        slice_mapper = vtkDataSetMapper()
        slice_mapper.SetInputConnection(cutter.GetOutputPort())
        slice_mapper.SetScalarModeToUsePointFieldData()
        slice_mapper.InterpolateScalarsBeforeMappingOn()
        slice_actor.SetMapper(slice_mapper)
        self.plane = plane
        self.cutter = cutter
        self.slice_actor = slice_actor
        self.mapper = slice_mapper

        outline = vtkOutlineFilter()
        outline_actor = vtkActor()
        outline_mapper = vtkPolyDataMapper()
        outline.input_connection = self.source.output_port
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        self.outline = outline
        self.outline_actor = outline_actor
        self.outline_mapper = outline_mapper

        data_actor = vtkActor()
        data_mapper = vtkDataSetMapper()
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

            # 3D view
            Pan3DSlicerView(
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

            # Sliders overlay
            SliceSummary(
                v_if="!control_expended",
                classes="d-flex align-center flex-column",
                style="position: absolute; left: 0; top: 10%; bottom: 10%; z-index: 2; pointer-events: none; min-width: 5rem;",
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
                SliceRenderingSettings(
                    ctx_name="rendering",
                    source=self.source,
                    update_rendering=self.update_rendering,
                )

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
