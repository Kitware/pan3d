import vtk
import numpy as np
import pandas as pd
from pathlib import Path

from trame.app import get_server
from trame_client.widgets.core import TrameDefault
from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3 as v3, vtk as vtkw, html, client
from pan3d.dataset_builder import DatasetBuilder
from pan3d.ui.common import NumericField

from pan3d.utils.presets import update_preset, use_preset, COLOR_PRESETS


def get_time_labels(times):
    return [pd.to_datetime(time).strftime("%Y-%m-%d %H:%M:%S") for time in times]


@TrameApp()
class SliceExplorer:
    """
    A Trame based pan3D explorer to visualize 3D using slices along different dimensions

    This explorer uses the pan3D DatasetBuilder and it's operability with xarray to fetch
    relevant data and allows users to specify a specific slice of interest and visualize it
    using VTK while interacting with the slice in 2D or 3D.
    """

    def __init__(self, builder: DatasetBuilder = None, server=None):
        # trame setup
        self.server = get_server(server)
        if self.server.hot_reload:
            self.ctrl.on_server_reload.add(self._build_ui)

        # CLI
        parser = self.server.cli
        parser.add_argument("--config-path", required=(builder is None))
        args, _ = parser.parse_known_args()

        # Setup builder if needed
        self.builder = builder
        if self.builder is None:
            config_path = Path(args.config_path).resolve()
            if config_path.exists():
                self.builder = DatasetBuilder()
                self.builder.import_config(str(config_path))
            else:
                print(f'--config-path "{str(config_path)}" must point to a valid path.')
                exit(1)

        self.dims = dict(
            [
                (x, y)
                for (x, y) in zip(
                    [self.builder.x, self.builder.y, self.builder.z], ["x", "y", "z"]
                )
                if x is not None
            ]
        )
        self.extents = self.builder.extents

        slice_dim = list(self.dims.keys())[0]
        ext = self.extents[slice_dim]
        self.state.update(
            dict(
                slice_dim=slice_dim,
                dimval=float(ext[0] + (ext[1] - ext[0]) / 2),
                dimmin=float(ext[0]),
                dimmax=float(ext[1]),
                varmin=0.0,
                varmax=0.0,
                t_labels=get_time_labels(self.builder.t_values),
                x_scale=1.0,
                y_scale=1.0,
                z_scale=1.0,
            )
        )

        self.t_cache = {}
        self.vars = list(self.builder.dataset.data_vars.keys())
        self.var_ranges = self.builder.var_ranges

        extents = list(self.extents.values())
        self.origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2),
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2),
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2),
        ]
        self.normal = [1, 0, 0]
        self.lengths = [
            float(extents[0][1] - extents[0][0]),
            float(extents[1][1] - extents[1][0]),
            float(extents[2][1] - extents[2][0]),
        ]
        self._generate_vtk_pipeline()
        self._build_ui()

    def _generate_vtk_pipeline(self):
        self._renderer = vtk.vtkRenderer()
        self._interactor = vtk.vtkRenderWindowInteractor()
        self._render_window = vtk.vtkRenderWindow()

        var_range = self.var_ranges[self.vars[0]]

        plane = vtk.vtkPlane()
        plane.SetOrigin(self.origin)
        plane.SetNormal(self.normal)
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(self.builder.mesh)
        slice_actor = vtk.vtkActor()
        slice_mapper = vtk.vtkDataSetMapper()
        slice_mapper.SetInputConnection(cutter.GetOutputPort())
        slice_mapper.SetScalarRange(float(var_range[0]), float(var_range[1]))
        slice_actor.SetMapper(slice_mapper)
        self._plane = plane
        self._cutter = cutter
        self._slice_actor = slice_actor
        self._slice_mapper = slice_mapper

        outline = vtk.vtkOutlineFilter()
        outline_actor = vtk.vtkActor()
        outline_mapper = vtk.vtkPolyDataMapper()
        outline.SetInputData(self.builder.mesh)
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        self._outline = outline
        self._outline_actor = outline_actor
        self._outline_mapper = outline_mapper

        data_actor = vtk.vtkActor()
        data_mapper = vtk.vtkDataSetMapper()
        data_mapper.SetInputData(self.builder.mesh)
        data_mapper.SetScalarRange(float(var_range[0]), float(var_range[1]))
        data_actor.SetMapper(data_mapper)
        data_actor.GetProperty().SetOpacity(0.1)
        data_actor.SetVisibility(False)
        self._data_actor = data_actor
        self._data_mapper = data_mapper

        sbar_actor = vtk.vtkScalarBarActor()
        sbar_actor.SetLookupTable(self._slice_mapper.GetLookupTable())
        sbar_actor.SetMaximumHeightInPixels(600)
        sbar_actor.SetMaximumWidthInPixels(100)
        sbar_actor.SetTitleRatio(0.2)
        lprop: vtk.vtkTextProperty = sbar_actor.GetLabelTextProperty()
        lprop.SetColor(0.5, 0.5, 0.5)
        tprop: vtk.vtkTextProperty = sbar_actor.GetTitleTextProperty()
        tprop.SetColor(0.5, 0.5, 0.5)
        self._sbar_actor = sbar_actor

        self._renderer.SetBackground(1.0, 1.0, 1.0)
        self._render_window.OffScreenRenderingOn()
        self._render_window.AddRenderer(self._renderer)
        self._interactor.SetRenderWindow(self._render_window)
        self._interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self._renderer.AddActor(self._outline_actor)
        self._renderer.AddActor(self._data_actor)
        self._renderer.AddActor(self._slice_actor)
        self._renderer.AddActor(self._sbar_actor)

        self._renderer.ResetCamera()

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
    def coords_time(self):
        """
        Returns the values for time coordinates for user to select
        """
        return self.builder.dataset.coords[self.builder.t].to_numpy()

    @property
    def t_slice(self):
        """
        Property representing the current time slice for the dataset from the
        DatasetBuilder, and is extracted by setting the current active time value
        as a xarray selection for the time slice
        """
        datavar = self.state.data_var
        # m = self.state.time_active
        m = self.builder.t_values[self.state.time_active]
        mesh = self.t_cache.get((m, datavar))
        ttype = self.builder.dataset.coords[self.builder.t].dtype
        if mesh is None:
            criteria = {}
            if ttype.kind in ["O", "M"]:
                criteria[self.builder.t] = np.datetime64(m, "ns")
            else:
                criteria[self.builder.t] = m
            da = self.builder.dataset[datavar].sel(**criteria, method="nearest")
            da.load()
            mesh = da.pyvista.mesh(x=self.builder.x, y=self.builder.y, z=self.builder.z)
            self.t_cache[(m, datavar)] = mesh
        return mesh

    @property
    def slice_dimension(self):
        """
        Returns the active dimension along with the slice is performed
        """
        return self.state.slice_dim

    @slice_dimension.setter
    def slice_dimension(self, dim: str) -> None:
        """
        Sets the active dimension along which the slice is performed
        """
        with self.state:
            self.state.slice_dim = dim
            self.update_slicer_dimension(dim)

    @property
    def slice_value(self):
        """
        Returns the value(origin) for the dimension along which the slice
        is performed
        """
        return self.state.dimval

    @slice_value.setter
    def slice_value(self, value: float) -> None:
        """
        Sets the value(origin) for the dimension along which the slice
        is performed
        """
        with self.state:
            self.state.dimval = value

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
        self._slice_actor.SetScale(s.x_scale, s.y_scale, s.z_scale)
        self._data_actor.SetScale(s.x_scale, s.y_scale, s.z_scale)
        self._outline_actor.SetScale(s.x_scale, s.y_scale, s.z_scale)
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
        use_preset(self._slice_actor, self._data_actor, self._sbar_actor, cmap)
        self.ctrl.view_update()

    @change("logscale")
    def _on_log_scale_change(self, logscale, **_):
        """
        Performs all the steps necessary when user toggles log scale for color map
        """
        update_preset(self._slice_actor, self._sbar_actor, logscale)
        self.ctrl.view_update()

    def _set_view_2D(self, origin, dimension):
        camera = self._renderer.GetActiveCamera()
        position = camera.GetPosition()
        norm = np.linalg.norm(np.array(origin) - np.array(position))
        position = origin[:]
        self._outline_actor.SetVisibility(False)
        self._data_actor.SetVisibility(False)
        position[dimension] = norm
        view_up = [0, 0.0, 1.0] if dimension == 1 else [0, 1.0, 0.0]
        camera.SetPosition(position)
        camera.SetViewUp(view_up)
        camera.SetFocalPoint(origin)
        camera.OrthogonalizeViewUp()
        self._renderer.SetActiveCamera(camera)
        self._renderer.ResetCamera()
        self.ctrl.view_update()

    def _set_view_3D(self, origin):
        camera = self._renderer.GetActiveCamera()
        position = camera.GetPosition()
        norm = np.linalg.norm(np.array(origin) - np.array(position))
        camera.SetPosition(norm, norm, norm)
        camera.SetViewUp(0.0, 1.0, 0.0)
        if self.state.outline:
            self._outline_actor.SetVisibility(True)
        if self.state.tdata:
            self._data_actor.SetVisibility(True)
        self._renderer.SetActiveCamera(camera)
        self._renderer.ResetCamera()
        self.ctrl.view_update()

    @change("view_mode")
    def on_view_mode_change(self, view_mode, **_):
        """
        Performs all the steps necessary when user toggles the view mode
        """
        s = self.state
        slice_dim = s.slice_dim
        slice_i = (
            0
            if self.dims[slice_dim] == "x"
            else 1 if self.dims[slice_dim] == "y" else 2
        )
        extents = list(self.extents.values())
        origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2) * s.x_scale,
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2) * s.y_scale,
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2) * s.z_scale,
        ]
        if view_mode == "3D":
            self._set_view_3D(origin)
        elif view_mode == "2D":
            self._set_view_2D(origin, slice_i)

    @change("data_var", "time_active", "dimval")
    def _on_data_change(self, **_):
        """
        Performs all the steps necessary when the user updates any properties
        that requires a new data update. E.g. changing the data variable for
        visualization, or changing active time, or changing slice value.
        """
        dimval = self.state.dimval
        slice_dim = self.state.slice_dim
        normal = [0, 0, 0]
        slice_i = (
            0
            if self.dims[slice_dim] == "x"
            else 1 if self.dims[slice_dim] == "y" else 2
        )
        normal[slice_i] = 1

        extents = list(self.extents.values())
        origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2),
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2),
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2),
        ]
        origin[slice_i] = dimval

        self._plane.SetOrigin(origin)
        self._plane.SetNormal(normal)

        self._cutter.SetInputData(self.t_slice)
        self._cutter.Update()
        output = self._cutter.GetOutput()
        vrange = output.GetPointData().GetArray(self.state.data_var).GetRange()
        self._slice_mapper.SetScalarRange(float(vrange[0]), float(vrange[1]))
        self.state.varmin = float(vrange[0])
        self.state.varmax = float(vrange[1])
        self._sbar_actor.SetLookupTable(self._slice_mapper.GetLookupTable())

        if self.state.view_mode == "2D":
            self.on_view_mode_change("2D")
            self._renderer.ResetCamera()

        self.ctrl.view_update()

    @change("outline", "tdata")
    def _on_rep_change(self, outline, tdata, **_):
        """
        Performs all the steps necessary when user specifies 3D interaction options
        """
        self._outline_actor.SetVisibility(outline)
        self._data_actor.SetVisibility(tdata)
        self.ctrl.view_update()

    @change("varmin", "varmax")
    def _on_scalar_change(self, varmin, varmax, **_):
        """
        Performs all the steps necessary when user specifies values for scalar range explicitly
        """
        self._slice_mapper.SetScalarRange(float(varmin), float(varmax))
        self._sbar_actor.SetLookupTable(self._slice_mapper.GetLookupTable())
        self.ctrl.view_update()

    # -------------------------------------------------------------------------
    # UI triggers
    # -------------------------------------------------------------------------

    def on_axis_scale_change(self, axis, value):
        """
        Performs all the steps necessary when user specifies scaling along a certain axis
        """
        s = self.state
        axis_names = ["x_scale", "y_scale", "z_scale"]
        axis_name = axis_names[axis]
        # If value is the same as previous no scaling is needed
        if s[axis_name] == value:
            return
        # Update all the actors to scale based on new value
        s[axis_name] = value
        scales = [s[n] for n in axis_names]
        self._slice_actor.SetScale(*scales)
        self._data_actor.SetScale(*scales)
        self._outline_actor.SetScale(*scales)
        # Update view
        self.on_view_mode_change(s.view_mode)

    def update_slicer_dimension(self, dim):
        """
        Update values for min/max and current slice values
        """
        ext = self.extents[dim]
        self.state.dimval = float(ext[0] + (ext[1] - ext[0]) / 2)
        self.state.dimmin = float(ext[0])
        self.state.dimmax = float(ext[1])

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
                    title.set_text("Pan3D: Slice Explorer")
                    title.style = "flex: none;"
                    self.state.trame__title = "Slice Explorer"

                v3.VSpacer()

                v3.VSelect(
                    prepend_inner_icon="mdi-palette",
                    # label="Color By",
                    v_model=("data_var", next(iter(self.vars))),
                    items=("data_vars", self.vars),
                    variant="outlined",
                    max_width="25vw",
                    **style,
                )
                v3.VSpacer()

                with v3.VBtnToggle(
                    v_model=(
                        "rep_options",
                        TrameDefault(
                            rep_options=["outline"], outline=True, tdata=False
                        ),
                    ),
                    multiple=True,
                    variant="outlined",
                    **style,
                    disabled=("view_mode === '2D'",),
                    classes="mx-4",
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
                    **style,
                ):
                    v3.VBtn(icon="mdi-video-2d", value="2D")
                    v3.VBtn(icon="mdi-video-3d", value="3D")

                v3.VBtn(
                    icon="mdi-crop-free",
                    click=self.ctrl.view_reset_camera,
                    classes="ml-4",
                )

                v3.VSwitch(
                    v_model=("vscroll", False),
                    classes="mx-4",
                    **style,
                    false_icon="mdi-rotate-3d",
                    true_icon="mdi-arrow-vertical-lock",
                    inset=True,
                    color="red",
                    base_color="green",
                )

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
                                "{{t_labels[time_active]}}", classes="text-subtitle-1"
                            )
                        v3.VSlider(
                            classes="mx-2",
                            min=0,
                            max=("t_size", self.builder.t_size - 1),
                            v_model=("time_active", 0),
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
                                "{{parseFloat(dimval).toFixed(2)}}",
                                classes="text-subtitle-1",
                            )
                        v3.VSelect(
                            v_model=("slice_dim",),
                            items=("slice_dims", list(self.dims.keys())),
                            update_modelValue=(
                                self.update_slicer_dimension,
                                "[$event]",
                            ),
                            **style,
                        )

                        v3.VSlider(
                            v_model=("dimval",),
                            min=("dimmin",),
                            max=("dimmax",),
                            **style,
                        )

                        with v3.VRow():
                            with v3.VCol():
                                html.Div(
                                    "{{parseFloat(dimmin).toFixed(2)}}",
                                    classes="font-weight-medium",
                                )
                            with v3.VCol(classes="text-right"):
                                html.Div(
                                    "{{parseFloat(dimmax).toFixed(2)}}",
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
                                    label=("slice_dims[0]",),
                                    model_value=("x_scale",),
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
                                    label=("slice_dims[1]",),
                                    model_value=("y_scale",),
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
                                    label=("slice_dims[2]",),
                                    model_value=("z_scale",),
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
                                    v_model=("varmin",),
                                    label="min",
                                    outlined=True,
                                    **style,
                                )
                            with v3.VCol():
                                v3.VTextField(
                                    v_model=("varmax",),
                                    label="max",
                                    outlined=True,
                                    **style,
                                )

            # Content
            with layout.content:
                # 3d view
                with html.Div(
                    style="position:absolute; top: 0; left: 0; width: 100%; height: 100%;",
                ):
                    with vtkw.VtkRemoteView(
                        self._render_window, interactive_ratio=1
                    ) as view:
                        self.ctrl.view_update = view.update
                        self.ctrl.view_reset_camera = view.reset_camera

                # Scroll locking overlay
                html.Div(
                    v_show="vscroll",
                    style="position:absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;",
                )

                # Sliders overlay
                with html.Div(
                    v_if="!main_drawer",
                    classes="d-flex align-center flex-column",
                    style="position: absolute; left: 0; top: var(--v-layout-top); bottom: var(--v-layout-bottom); z-index: 2; pointer-events: none; min-width: 5rem;",
                ):
                    html.Div(
                        "{{slice_dim}}",
                        classes="text-subtitle-1 text-capitalize text-left",
                        style="transform-origin: 50% 50%; transform: rotate(-90deg) translateX(-100%) translateY(-1rem); position: absolute;",
                    )
                    html.Div(
                        "{{parseFloat(dimmax).toFixed(2)}}",
                        classes="text-subtitle-1 mx-1",
                    )
                    v3.VSlider(
                        thumb_label="always",
                        thumb_size=16,
                        style="pointer-events: auto;",
                        hide_details=True,
                        classes="flex-fill",
                        direction="vertical",
                        v_model=("dimval",),
                        min=("dimmin",),
                        max=("dimmax",),
                    )

                    html.Div(
                        "{{parseFloat(dimmin).toFixed(2)}}",
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
                            "Time: {{t_labels[time_active]}}",
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
                        max=self.builder.t_size - 1,
                        v_model=("time_active", 0),
                        step=1,
                    )
            return layout


def main():
    app = SliceExplorer()
    app.server.start()


if __name__ == "__main__":
    main()
