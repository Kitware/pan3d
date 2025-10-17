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

from pan3d.ui.layouts import StandardExplorerLayout
from pan3d.ui.slicer import SliceRenderingSettings
from pan3d.utils.common import Explorer
from pan3d.widgets.pan3d_view import Pan3DView
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from trame.decorators import change
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


class SliceSummary(v3.VCard):
    def __init__(
        self,
        axis_names="axis_names",
        slice_axis="slice_axis",
        cut_x="cut_x",
        cut_y="cut_y",
        cut_z="cut_z",
        bounds="bounds",
        **kwargs,
    ):
        super().__init__(
            classes="slice-summary",
            rounded="pill",
            **kwargs,
        )

        with self:
            with v3.VRow(classes="align-center mx-2 my-0"):
                v3.VSelect(
                    v_model=(slice_axis,),
                    items=(axis_names,),
                    hide_details=True,
                    density="compact",
                    variant="solo",
                    flat=True,
                    max_width=100,
                )
                v3.VSpacer()
                html.Span(
                    "{{parseFloat(cut_x).toFixed(2)}}",
                    v_show=f"{slice_axis} === {axis_names}[0]",
                    classes="text-subtitle-1",
                )
                html.Span(
                    "{{parseFloat(cut_y).toFixed(2)}}",
                    v_show=f"{slice_axis} === {axis_names}[1]",
                    classes="text-subtitle-1",
                )
                html.Span(
                    "{{parseFloat(cut_z).toFixed(2)}}",
                    v_show=f"{slice_axis} === {axis_names}[2]",
                    classes="text-subtitle-1",
                )
            with v3.VRow(classes="mx-2 my-0"):
                v3.VSlider(
                    v_show=f"{slice_axis} === {axis_names}[0]",
                    v_model=(cut_x,),
                    min=(f"{bounds}[0]",),
                    max=(f"{bounds}[1]",),
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
                )
                v3.VSlider(
                    v_show=f"{slice_axis} === {axis_names}[1]",
                    v_model=(cut_y,),
                    min=(f"{bounds}[2]",),
                    max=(f"{bounds}[3]",),
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
                )
                v3.VSlider(
                    v_show=f"{slice_axis} === {axis_names}[2]",
                    v_model=(cut_z,),
                    min=(f"{bounds}[4]",),
                    max=(f"{bounds}[5]",),
                    hide_details=True,
                    density="compact",
                    flat=True,
                    variant="solo",
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

        if self.anari:
            from pan3d.utils import anari

            anari.setup(self.renderer)

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

        # Use the standard UI creation method
        with StandardExplorerLayout(explorer=self, title="Slice Explorer") as self.ui:
            with self.ui.content:
                Pan3DSlicerView(
                    render_window=self.render_window,
                    local_rendering=self.local_rendering,
                    widget=[self.widget],
                )
                SliceSummary(
                    v_show="!control_expended",
                    style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); z-index: 2;",
                )
            with self.ui.control_panel:
                SliceRenderingSettings(
                    ctx_name="rendering",
                    source=self.source,
                    update_rendering=self.update_rendering,
                )

    def update_rendering(self, reset_camera=False):
        self.state.dirty_data = False

        # Ensure actors are visible
        if self.slice_actor.GetVisibility() == 0:
            self.slice_actor.SetVisibility(1)
        if self.data_actor.GetVisibility() == 0 and self.state.tdata:
            self.data_actor.SetVisibility(1)

        self.renderer.ResetCamera()

        if reset_camera:
            self.ctrl.view_reset_camera()
        else:
            self.ctrl.view_update()

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
