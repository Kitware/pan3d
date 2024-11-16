import sys
import json
from pathlib import Path

from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkDataSetMapper,
    vtkActor,
    vtkPolyDataMapper,
    vtkTextProperty,
)
from vtkmodules.vtkRenderingAnnotation import (
    vtkScalarBarActor,
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

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

from pan3d.xarray.algorithm import vtkXArrayRectilinearSource

from trame.app import get_server
from trame_client.widgets.core import TrameDefault
from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3 as v3, html, client

from pan3d.ui.vtk_view import Pan3DView
from pan3d.ui.common import NumericField
from pan3d.utils.presets import update_preset, use_preset, COLOR_PRESETS


@TrameApp()
class XArraySlicer:
    """
    A Trame based pan3D explorer to visualize 3D using slices along different dimensions

    This explorer uses the pan3D DatasetBuilder and it's operability with xarray to fetch
    relevant data and allows users to specify a specific slice of interest and visualize it
    using VTK while interacting with the slice in 2D or 3D.
    """

    def __init__(self, source=None, server=None):
        # trame setup
        self.server = get_server(server)
        if self.server.hot_reload:
            self.ctrl.on_server_reload.add(self._build_ui)

        # CLI
        parser = self.server.cli
        parser.add_argument(
            "--import-state",
            help="Pass a string with this argument to specify a startup configuration. This value must be a local path to a JSON file which adheres to the schema specified in the [Configuration Files documentation](../api/configuration.md).",
            required=(source is None),
        )
        args, _ = parser.parse_known_args()

        # Check if we have what we need
        config_file = Path(args.import_state) if args.import_state else None
        if (config_file is None or not config_file.exists()) and source is None:
            parser.print_help()
            sys.exit(0)

        # Build Viz and UI
        self.ui = None
        self._setup_vtk(source, config_file)
        self._build_ui()

    def _setup_vtk(self, source=None, import_state=None):
        if source is not None:
            self.source = source
        elif import_state is not None:
            self.source = vtkXArrayRectilinearSource()
            self.source.load(json.loads(import_state.read_text()))
        else:
            print(
                "XArraySlicer can only work when passed a data source or a state to import."
            )
            sys.exit(1)

        # Extract data info
        ds = self.source()
        bounds = ds.bounds
        self.normal = [0, 0, 1]
        self.origin = [
            0.5 * (bounds[0] + bounds[1]),
            0.5 * (bounds[2] + bounds[3]),
            0.5 * (bounds[4] + bounds[5]),
        ]

        # Update state from dataset
        self.state.t_index = self.source.t_index
        self.state.bounds = bounds
        self.state.cut_x = self.origin[0]
        self.state.cut_y = self.origin[1]
        self.state.cut_z = self.origin[2]
        self.state.available_fields = list(ds.point_data.keys())
        self.state.color_by = self.state.available_fields[0]
        self.state.t_labels = self.source.t_labels
        self.state.slice_axes = [self.source.x, self.source.y, self.source.z]
        self.state.slice_axis = self.source.z

        color_range = ds.point_data[self.state.color_by].GetRange()

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
        slice_mapper = vtkDataSetMapper()
        slice_mapper.SetInputConnection(cutter.GetOutputPort())
        slice_mapper.SetScalarRange(*color_range)
        slice_mapper.SelectColorArray(self.state.color_by)
        slice_mapper.SetScalarModeToUsePointFieldData()
        slice_mapper.InterpolateScalarsBeforeMappingOn()
        slice_actor.SetMapper(slice_mapper)
        self.plane = plane
        self.cutter = cutter
        self.slice_actor = slice_actor
        self.slice_mapper = slice_mapper

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
        data_mapper.SetScalarRange(*color_range)
        data_actor.SetMapper(data_mapper)
        data_actor.GetProperty().SetOpacity(0.1)
        data_actor.SetVisibility(False)
        self.data_actor = data_actor
        self.data_mapper = data_mapper

        sbar_actor = vtkScalarBarActor()
        sbar_actor.SetLookupTable(self.slice_mapper.GetLookupTable())
        sbar_actor.SetMaximumHeightInPixels(600)
        sbar_actor.SetMaximumWidthInPixels(100)
        sbar_actor.SetTitleRatio(0.2)
        lprop: vtkTextProperty = sbar_actor.GetLabelTextProperty()
        lprop.SetColor(0.5, 0.5, 0.5)
        tprop: vtkTextProperty = sbar_actor.GetTitleTextProperty()
        tprop.SetColor(0.5, 0.5, 0.5)
        self.sbar_actor = sbar_actor

        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.render_window.OffScreenRenderingOn()
        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.renderer.AddActor(self.outline_actor)
        self.renderer.AddActor(self.data_actor)
        self.renderer.AddActor(self.slice_actor)
        self.renderer.AddActor(self.sbar_actor)

        self.renderer.ResetCamera()

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
    # Reactive state listeners
    # -------------------------------------------------------------------------

    @change("cmap")
    def _on_colormap_change(self, cmap, **_):
        """
        Performs all the steps necessary to visualize correct data when the
        color map is updated
        """
        use_preset(self.slice_actor, self.data_actor, self.sbar_actor, cmap)
        self.ctrl.view_update()

    @change("logscale")
    def _on_log_scale_change(self, logscale, **_):
        """
        Performs all the steps necessary when user toggles log scale for color map
        """
        update_preset(self.slice_actor, self.sbar_actor, logscale)
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
            axis_idx = s.slice_axes.index(s.slice_axis)
            self._set_view_2D(axis_idx)

    @change("color_by")
    def _on_color_by_change(self, color_by, **_):
        if color_by is None:
            return

        color_min, color_max = self.source().point_data[color_by].GetRange()

        self.slice_mapper.SetScalarRange(color_min, color_max)
        self.slice_mapper.SelectColorArray(color_by)
        self.sbar_actor.SetLookupTable(self.slice_mapper.GetLookupTable())

        self.state.color_min = color_min
        self.state.color_max = color_max

    @change("slice_axis", "t_index", "cut_x", "cut_y", "cut_z")
    def _on_data_change(
        self, slice_axis, slice_axes, t_index, cut_x, cut_y, cut_z, **_
    ):
        """
        Performs all the steps necessary when the user updates any properties
        that requires a new data update. E.g. changing the data variable for
        visualization, or changing active time, or changing slice value.
        """
        self.normal = [0, 0, 0]
        self.normal[slice_axes.index(slice_axis)] = 1
        self.origin = [
            float(cut_x),
            float(cut_y),
            float(cut_z),
        ]

        self.source.t_index = t_index
        self.plane.SetOrigin(self.origin)
        self.plane.SetNormal(self.normal)

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

    @change("color_min", "color_max")
    def _on_scalar_change(self, color_min, color_max, **_):
        """
        Performs all the steps necessary when user specifies values for scalar range explicitly
        """
        self.slice_mapper.SetScalarRange(float(color_min), float(color_max))
        self.sbar_actor.SetLookupTable(self.slice_mapper.GetLookupTable())
        self.ctrl.view_update()

    # -------------------------------------------------------------------------
    # UI triggers
    # -------------------------------------------------------------------------

    def on_axis_scale_change(self, idx, value):
        """
        Performs all the steps necessary when user specifies scaling along a certain axis
        """
        s = self.state
        axis_names = ["x_scale", "y_scale", "z_scale"]
        if s[axis_names[idx]] == value:
            return

        s[axis_names[idx]] = value
        scales = [s[n] for n in axis_names]
        self.slice_actor.SetScale(*scales)
        self.data_actor.SetScale(*scales)
        self.outline_actor.SetScale(*scales)
        # Update view
        self.on_view_mode_change(s.view_mode)

    # -------------------------------------------------------------------------
    # GUI definition
    # -------------------------------------------------------------------------

    def _build_ui(self, *args, **kwargs):
        style = dict(density="compact", hide_details=True)
        with SinglePageWithDrawerLayout(self.server, full_height=True) as layout:
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
                    title.set_text("XArray Slicer")
                    title.style = "flex: none;"
                    self.state.trame__title = "XArray Slicer"

                v3.VSpacer()

                v3.VSelect(
                    prepend_inner_icon="mdi-palette",
                    v_model=("color_by", None),
                    items=("available_fields", []),
                    variant="outlined",
                    max_width="25vw",
                    **style,
                )
                v3.VSpacer()

                with v3.VBtnToggle(
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
                    **style,
                    disabled=("view_mode === '2D'",),
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

                with v3.VBtnToggle(
                    v_model=("view_mode", "3D"),
                    mandatory=True,
                    variant="outlined",
                    classes="mx-4",
                    **style,
                ):
                    v3.VBtn(icon="mdi-video-2d", value="2D")
                    v3.VBtn(icon="mdi-video-3d", value="3D")

            # Footer
            if not self.server.hot_reload:
                layout.footer.hide()

            # Drawer
            with layout.drawer as drawer:
                drawer.width = 420
                drawer.style = "background: none; border: none; pointer-events: none;"
                drawer.tile = True

                with v3.VCard(
                    classes="ml-2 mt-3 mr-6", elevation=5, style="pointer-events: auto;"
                ):
                    with v3.VCardText():
                        # -- Time section
                        with v3.VRow(classes="ma-0 align-center"):
                            html.Span("Time", classes="text-h6 font-weight-medium")
                            v3.VSpacer()
                            html.Span(
                                "{{t_labels[t_index]}}", classes="text-subtitle-1"
                            )
                        v3.VSlider(
                            classes="mx-2",
                            min=0,
                            max=self.source.t_size - 1,
                            v_model=("t_index", 0),
                            step=1,
                            **style,
                        )
                        with v3.VRow():
                            with v3.VCol():
                                html.Div(
                                    "{{t_labels[0]}}", classes="font-weight-medium"
                                )
                            with v3.VCol(classes="text-right"):
                                html.Div(
                                    "{{t_labels[t_labels.length - 1]}}",
                                    classes="font-weight-medium",
                                )

                        # -- Slice section
                        v3.VDivider(classes="mx-n4 my-1")
                        with v3.VRow(classes="ma-0 align-center"):
                            html.Span("Slice", classes="text-h6 font-weight-medium")
                            v3.VSpacer()
                            html.Span(
                                "{{parseFloat(cut_x).toFixed(2)}}",
                                v_show="slice_axis === slice_axes[0]",
                                classes="text-subtitle-1",
                            )
                            html.Span(
                                "{{parseFloat(cut_y).toFixed(2)}}",
                                v_show="slice_axis === slice_axes[1]",
                                classes="text-subtitle-1",
                            )
                            html.Span(
                                "{{parseFloat(cut_z).toFixed(2)}}",
                                v_show="slice_axis === slice_axes[2]",
                                classes="text-subtitle-1",
                            )
                        v3.VSelect(
                            v_model=("slice_axis",),
                            items=("slice_axes", []),
                            **style,
                        )

                        v3.VSlider(
                            v_show="slice_axis === slice_axes[0]",
                            v_model=("cut_x",),
                            min=("bounds[0]",),
                            max=("bounds[1]",),
                            **style,
                        )
                        v3.VSlider(
                            v_show="slice_axis === slice_axes[1]",
                            v_model=("cut_y",),
                            min=("bounds[2]",),
                            max=("bounds[3]",),
                            **style,
                        )
                        v3.VSlider(
                            v_show="slice_axis === slice_axes[2]",
                            v_model=("cut_z",),
                            min=("bounds[4]",),
                            max=("bounds[5]",),
                            **style,
                        )

                        with v3.VRow():
                            with v3.VCol():
                                html.Div(
                                    "{{parseFloat(bounds[slice_axes.indexOf(slice_axis)*2]).toFixed(2)}}",
                                    classes="font-weight-medium",
                                )
                            with v3.VCol(classes="text-right"):
                                html.Div(
                                    "{{parseFloat(bounds[slice_axes.indexOf(slice_axis)*2 + 1]).toFixed(2)}}",
                                    classes="font-weight-medium",
                                )

                        # -- Scaling section
                        v3.VDivider(classes="mx-n4 my-1")
                        with v3.VRow(classes="ma-0 align-center"):
                            html.Span("Scaling", classes="text-h6 font-weight-medium")

                        with v3.VRow(classes="mt-n2"):
                            with v3.VCol(
                                cols=4,
                                classes="text-center font-weight-medium d-flex flex-column",
                            ):
                                NumericField(
                                    label=("slice_axes[0]",),
                                    model_value=("x_scale", 1),
                                    update_event=(
                                        self.on_axis_scale_change,
                                        "[0, Number($event.target.value)]",
                                    ),
                                    **style,
                                )
                            with v3.VCol(
                                cols=4,
                                classes="text-center font-weight-medium d-flex flex-column",
                            ):
                                NumericField(
                                    label=("slice_axes[1]",),
                                    model_value=("y_scale", 1),
                                    update_event=(
                                        self.on_axis_scale_change,
                                        "[1, Number($event.target.value)]",
                                    ),
                                    **style,
                                )
                            with v3.VCol(
                                cols=4,
                                classes="text-center font-weight-medium d-flex flex-column",
                            ):
                                NumericField(
                                    label=("slice_axes[2]",),
                                    model_value=("z_scale", 1),
                                    update_event=(
                                        self.on_axis_scale_change,
                                        "[2, Number($event.target.value)]",
                                    ),
                                    **style,
                                )

                        # -- Color presets
                        v3.VDivider(classes="mx-n4 mt-2 mb-1")
                        with v3.VRow(classes="ma-0 align-center"):
                            html.Span(
                                "Color Settings", classes="text-h6 font-weight-medium"
                            )
                            v3.VSpacer()
                            v3.VSwitch(
                                v_model=("logscale", False),
                                true_icon="mdi-math-log",
                                false_icon="mdi-vector-line",
                                inset=True,
                                **style,
                            )
                        v3.VSelect(
                            label="Preset",
                            v_model=("cmap", COLOR_PRESETS[0]),
                            items=("colormaps", COLOR_PRESETS),
                            outlined=True,
                            **style,
                        )
                        # v3.VCheckbox(label="Use log scale", v_model=("logscale", False))
                        with v3.VRow(classes="mt-1"):
                            with v3.VCol():
                                v3.VTextField(
                                    v_model=("color_min",),
                                    label="min",
                                    outlined=True,
                                    **style,
                                )
                            with v3.VCol():
                                v3.VTextField(
                                    v_model=("color_max",),
                                    label="max",
                                    outlined=True,
                                    **style,
                                )

            # Content
            with layout.content:
                # 3D view
                Pan3DView(
                    self.render_window,
                    axis_names="slice_axes",
                    style="position: absolute; left: 0; top: var(--v-layout-top); bottom: var(--v-layout-bottom); z-index: 0; width: 100%;",
                )

                # Sliders overlay
                with html.Div(
                    v_if="!main_drawer",
                    classes="d-flex align-center flex-column",
                    style="position: absolute; left: 0; top: var(--v-layout-top); bottom: var(--v-layout-bottom); z-index: 2; pointer-events: none; min-width: 5rem;",
                ):
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
                with html.Div(
                    v_if="!main_drawer",
                    classes="align-center flex-column",
                    style="position: absolute; bottom: var(--v-layout-bottom); right: 1rem; width: calc(100% - 10rem);",
                ):
                    with v3.VRow(classes="pa-0 ma-0 d-flex justify-space-between"):
                        html.Div(
                            "{{t_labels[0]}}",
                            classes="text-subtitle-1",
                        )
                        html.Div(
                            "Time: {{t_labels[t_index]}}",
                            classes="text-subtitle-1",
                        )
                        html.Div(
                            "{{t_labels[t_labels.length - 1]}}",
                            classes="text-subtitle-1",
                        )
                    v3.VSlider(
                        style="pointer-events: auto;",
                        classes="mt-n2 mb-1",
                        hide_details=True,
                        min=0,
                        max=self.source.t_size - 1,
                        v_model=("t_index", 0),
                        step=1,
                    )
            return layout


def main():
    app = XArraySlicer()
    app.start()


if __name__ == "__main__":
    main()
