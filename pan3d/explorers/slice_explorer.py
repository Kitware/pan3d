from trame.app import get_server
from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3 as v3, vtk as vtkw, html
from pan3d.dataset_builder import DatasetBuilder
import vtk
import numpy as np

from pan3d.explorers.utilities import apply_preset
from pan3d.explorers.utilities import hsv_colors, rgb_colors

colors = []
colors.extend(list(hsv_colors.keys()))
colors.extend(list(rgb_colors.keys()))


def use_preset(
    sactor: vtk.vtkActor, dactor: vtk.vtkActor, sbar: vtk.vtkActor, preset: str
) -> None:
    """
    Given the slice, data, and scalar bar actor, applies the provided preset
    and updates the actors and the scalar bar
    """
    srange = sactor.GetMapper().GetScalarRange()
    drange = dactor.GetMapper().GetScalarRange()
    actors = [sactor, dactor]
    ranges = [srange, drange]
    for actor, range in zip(actors, ranges):
        apply_preset(actor, range, preset)
    sactor.GetMapper().SetScalarRange(srange[0], srange[1])
    dactor.GetMapper().SetScalarRange(drange[0], drange[1])
    sbar.SetLookupTable(sactor.GetMapper().GetLookupTable())


def update_preset(actor: vtk.vtkActor, sbar: vtk.vtkActor, logcale: bool) -> None:
    """
    Given an actor, scalar bar, and the option for whether to use log scale,
    make changes to the lookup table for the actor, and update the scalar bar
    """
    lut = actor.GetMapper().GetLookupTable()
    if logcale:
        lut.SetScaleToLog10()
    else:
        lut.SetScaleToLinear()
    lut.Build()
    sbar.SetLookupTable(lut)


@TrameApp()
class SliceExplorer:
    """
    A Trame based pan3D explorer to visualize 3D using slices along different dimensions

    This explorer uses the pan3D DatasetBuilder and it's operability with xarray to fetch
    relevant data and allows users to specify a specific slice of interest and visualize it
    using VTK while interacting with the slice in 2D or 3D.
    """

    def __init__(self, builder: DatasetBuilder = None, server=None):
        self.server = get_server(server)

        parser = self.server.cli
        parser.add_argument("--config_path")
        args, _ = self.server.cli.parse_known_args()

        if builder is None:
            import os

            if args.config_path is None or not os.path.exists(args.config_path):
                raise AttributeError(
                    "Need an instance of DatasetBuilder or a valid config path build one"
                )
                exit(1)
            else:
                builder = DatasetBuilder()
                builder.import_config(args.config_path)
                self.builder = builder
        else:
            self.builder = builder

        self.dims = dict(
            [
                (x, y)
                for (x, y) in zip([builder.x, builder.y, builder.z], ["x", "y", "z"])
                if x is not None
            ]
        )
        self.extents = builder.extents

        self._ui = None
        self.state.slice_dim = list(self.dims.keys())[0]
        ext = self.extents[self.state.slice_dim]
        self.state.dimval = float(ext[0] + (ext[1] - ext[0]) / 2)
        self.state.dimmin = float(ext[0])
        self.state.dimmax = float(ext[1])
        self.state.varmin = 0.0
        self.state.varmax = 0.0

        self.t_cache = {}
        self.vars = list(builder.dataset.data_vars.keys())
        self.var_ranges = builder.var_ranges

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
        self.ui = self._build_ui()

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
        tubify = vtk.vtkTubeFilter()
        tubify.SetInputConnection(outline.GetOutputPort())
        outline_mapper.SetInputConnection(tubify.GetOutputPort())
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        self._outline = outline
        self._tubify = tubify
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
        sbar_actor.SetMaximumWidthInPixels(150)
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

    @property
    def ctrl(self):
        return self.server.controller

    @property
    def state(self):
        return self.server.state

    @property
    def t_slice(self):
        """
        Property representing the current time slice for the dataset from the
        DatasetBuilder, and is extracted by setting the current active time value
        as a xarray selection for the time slice
        """
        datavar = self.state.data_var
        m = self.state.time_active
        mesh = self.t_cache.get((m, datavar))
        builder = self.builder
        ttype = builder.dataset.coords[builder.t].dtype
        if mesh is None:
            criteria = {}
            if ttype.kind in ["O", "M"]:
                print(np.datetime64(m, "ns"))
                criteria[builder.t] = np.datetime64(m, "ns")
            else:
                criteria[builder.t] = m
            da = builder.dataset[datavar].sel(**criteria, method="nearest")
            da.load()
            mesh = da.pyvista.mesh(x=builder.x, y=builder.y, z=builder.z)
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
            self.on_data_change()

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
            self.on_data_change()

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
            self.on_view_mode_change(mode)

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
            self.on_colormap_change(cmap)

    @change("cmap")
    def on_colormap_change(self, cmap, **_):
        """
        Performs all the steps necessary to visualize correct data when the
        color map is updated
        """
        use_preset(self._slice_actor, self._data_actor, self._sbar_actor, cmap)
        self.ctrl.view_update()

    @change("logscale")
    def on_log_scale_change(self, logscale, **_):
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
        slice_dim = self.state.slice_dim
        slice_i = (
            0
            if self.dims[slice_dim] == "x"
            else 1
            if self.dims[slice_dim] == "y"
            else 2
        )
        extents = list(self.extents.values())
        origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2),
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2),
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2),
        ]
        if view_mode == "3D":
            self._set_view_3D(origin)
        elif view_mode == "2D":
            self._set_view_2D(origin, slice_i)

    @change("data_var", "time_active", "dimval")
    def on_data_change(self, **_):
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
            else 1
            if self.dims[slice_dim] == "y"
            else 2
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
    def on_rep_change(self, outline, tdata, **_):
        """
        Performs all the steps necessary when user specifies 3D interaction options
        """
        self._outline_actor.SetVisibility(outline)
        self._data_actor.SetVisibility(tdata)
        self.ctrl.view_update()

    @change("varmin", "varmax")
    def on_scalar_change(self, varmin, varmax, **_):
        """
        Performs all the steps necessary when user specifies values for scalar range explicitly
        """
        self._slice_mapper.SetScalarRange(float(varmin), float(varmax))
        self._sbar_actor.SetLookupTable(self._slice_mapper.GetLookupTable())
        self.ctrl.view_update()

    @property
    def coords_time(self):
        """
        Returns the values for time coordinates for user to select
        """
        return self.builder.dataset.coords[self.builder.t].to_numpy()

    def update_slicer_dimension(self, dim):
        """
        Update values for min/max and current slice values
        """
        ext = self.extents[dim]
        self.state.dimval = float(ext[0] + (ext[1] - ext[0]) / 2)
        self.state.dimmin = float(ext[0])
        self.state.dimmax = float(ext[1])

    def start(self, **kwargs):
        self.ui.server.start(**kwargs)

    def _build_ui(self):
        style = dict(density="compact", hide_details=True)
        with SinglePageWithDrawerLayout(self.server, full_height=True) as layout:
            self._ui = layout
            layout.title.set_text("Slice Explorer")

            with layout.toolbar.clear():
                with v3.VBtn(
                    size="x-large",
                    classes="pa-0 ma-0",
                    style="min-width: 60px",
                    click="main_drawer = !main_drawer",
                ):
                    v3.VIcon("mdi-database-cog-outline")
                    v3.VIcon(
                        "{{ main_drawer ? 'mdi-chevron-left' : 'mdi-chevron-right' }}"
                    )

                with v3.VBtnToggle(
                    v_model=("view_mode", "3D"),
                    mandatory=True,
                    variant="outlined",
                    classes="mx-4",
                    **style,
                ):
                    v3.VBtn(icon="mdi-video-2d", value="2D"),
                    v3.VBtn(icon="mdi-video-3d", value="3D"),

                html.Div("3D Representation", v_show="view_mode === '3D'", **style)
                v3.VCheckbox(
                    v_model=("outline", True),
                    v_show="view_mode === '3D'",
                    label="Outline",
                    **style,
                )
                v3.VCheckbox(
                    v_model=("tdata", False),
                    v_show="view_mode === '3D'",
                    label="Semi-Transparent Data",
                    **style,
                )
                v3.VSpacer()
                v3.VSwitch(
                    label="Disable Scroll",
                    color="primary",
                    v_model=("vscroll", False),
                    **style,
                )

            with layout.drawer as drawer:
                drawer.width = 400
                with v3.VCard():
                    with v3.VCardTitle():
                        html.Div("Slice Setting")
                    with v3.VCardText():
                        v3.VSelect(
                            label="Time",
                            v_model=(
                                "time_active",
                                next(iter(self.coords_time.tolist())),
                            ),
                            items=("times_available", self.coords_time.tolist()),
                        )

                        v3.VSelect(
                            label="Slice Dimension",
                            v_model=("slice_dim",),
                            items=("slice_dims", list(self.dims.keys())),
                            update_modelValue=(
                                self.update_slicer_dimension,
                                "[$event]",
                            ),
                        )

                        v3.VSlider(
                            thumb_size=16,
                            thumb_label=True,
                            v_model=("dimval",),
                            min=("dimmin",),
                            max=("dimmax",),
                        )

                        v3.VSelect(
                            label="Variable",
                            v_model=("data_var", next(iter(self.vars))),
                            items=("data_vars", self.vars),
                        )

                with v3.VCard():
                    with v3.VCardTitle():
                        html.Div("Color Setting")
                    with v3.VCardText():
                        v3.VSelect(
                            v_model=("cmap", next(iter(colors))),
                            items=("colormaps", colors),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                            classes="pt-1",
                        )
                        v3.VCheckbox(label="Use log scale", v_model=("logscale", False))
                        with html.Div("Scalar Range"):
                            v3.VTextField(
                                v_model=("varmin",),
                                label="min",
                                outlined=True,
                                style="height=50px",
                            )
                            v3.VTextField(
                                v_model=("varmax",),
                                label="max",
                                outlined=True,
                                style="height=50px",
                            )
                            with v3.VBtn(
                                icon=True,
                                outlined=True,
                                style="height: 40px; width: 40px",
                            ):
                                v3.VIcon("mdi-restore")

            with layout.content:
                with vtkw.VtkRemoteView(
                    self._render_window, interactive_ratio=1
                ) as view:
                    self.ctrl.view_update = view.update
                    self.ctrl.view_reset_camera = view.reset_camera
                html.Div(
                    v_show="vscroll",
                    style="position:absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;",
                )

            return layout
