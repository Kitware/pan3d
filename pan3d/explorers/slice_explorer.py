from trame.app import get_server
from trame.decorators import TrameApp, change
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3 as v3, vtk as vtkw, html
from pan3d.dataset_builder import DatasetBuilder
import vtk, numpy as np

colors = [
    "Rainbow",       
    "Inv Rainbow",   
    "Greyscale",     
    "Inv Greyscale", 
]

class LookupTable:
    Rainbow = 0
    Inverted_Rainbow = 1
    Greyscale = 2
    Inverted_Greyscale = 3

# Color Map Callbacks
def use_preset(sactor : vtk.vtkActor, dactor : vtk.vtkActor, preset : str) -> None:
    s_lut = sactor.GetMapper().GetLookupTable()
    d_lut = dactor.GetMapper().GetLookupTable()
    if preset == "Rainbow":
        s_lut.SetHueRange(0.666, 0.0)
        s_lut.SetSaturationRange(1.0, 1.0)
        s_lut.SetValueRange(1.0, 1.0)
        d_lut.SetHueRange(0.666, 0.0)
        d_lut.SetSaturationRange(1.0, 1.0)
        d_lut.SetValueRange(1.0, 1.0)
    elif preset == "Inv Rainbow":
        s_lut.SetHueRange(0.0, 0.666)
        s_lut.SetSaturationRange(1.0, 1.0)
        s_lut.SetValueRange(1.0, 1.0)
        d_lut.SetHueRange(0.0, 0.666)
        d_lut.SetSaturationRange(1.0, 1.0)
        d_lut.SetValueRange(1.0, 1.0)
    elif preset == "Greyscale":
        s_lut.SetHueRange(0.0, 0.0)
        s_lut.SetSaturationRange(0.0, 0.0)
        s_lut.SetValueRange(0.0, 1.0)
        d_lut.SetHueRange(0.0, 0.0)
        d_lut.SetSaturationRange(0.0, 0.0)
        d_lut.SetValueRange(0.0, 1.0)
    elif preset == "Inv Greyscale":
        s_lut.SetHueRange(0.0, 0.666)
        s_lut.SetSaturationRange(0.0, 0.0)
        s_lut.SetValueRange(1.0, 0.0)
        d_lut.SetHueRange(0.0, 0.666)
        d_lut.SetSaturationRange(0.0, 0.0)
        d_lut.SetValueRange(1.0, 0.0)
    s_lut.Build()
    d_lut.Build()

def update_preset(actor: vtk.vtkActor, logcale : bool) -> None:
    lut = actor.GetMapper().GetLookupTable()
    if logcale:
        print("Setting log scale")
        lut.SetScaleToLog10()
    else:
        print("Setting linear scale")
        lut.SetScaleToLinear()
    lut.Build()

@TrameApp()
class SliceExplorer:
    def __init__(self, builder : DatasetBuilder, server=None):
        self.server = get_server(server)
        self.builder = builder
        self.dims    = dict([(x, y) for (x, y) in zip([builder.x, builder.y, builder.z], ['x', 'y','z']) if not x is None])
        self.extents = builder.extents

        self._ui = None
        self.state.slice_dim = list(self.dims.keys())[0]
        ext = self.extents[self.state.slice_dim]
        self.state.dimval = float(ext[0] + (ext[1] - ext[0]) / 2)
        self.state.dimmin = float(ext[0])
        self.state.dimmax = float(ext[1])
        self.state.varmin = 0.
        self.state.varmax = 0.

        self.t_cache = {}
        self.vars = list(builder.dataset.data_vars.keys())
        self.var_ranges = builder.var_ranges

        self.render_window  = vtk.vtkRenderWindow()
        self.renderer       = vtk.vtkRenderer()
        self.interactor     = vtk.vtkRenderWindowInteractor()

        extents = list(self.extents.values())
        self.origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2), 
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2), 
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2)
        ] 
        self.normal = [1, 0, 0]
        self.lengths = [
            float(extents[0][1] - extents[0][0]),
            float(extents[1][1] - extents[1][0]),
            float(extents[2][1] - extents[2][0]),
        ]

        self.plane = vtk.vtkPlane()
        self.plane.SetOrigin(self.origin)
        self.plane.SetNormal(self.normal)

        self.cutter = vtk.vtkCutter()
        self.cutter.SetCutFunction(self.plane)
        self.cutter.SetInputData(self.builder.mesh)

        var_range = self.var_ranges[self.vars[0]]
        self.slice_actor          = vtk.vtkActor()        
        self.slice_mapper         = vtk.vtkDataSetMapper()
        self.slice_mapper.SetInputConnection(self.cutter.GetOutputPort())
        self.slice_mapper.SetScalarRange(float(var_range[0]), float(var_range[1]))
        self.slice_actor.SetMapper(self.slice_mapper)

        self.outline            = vtk.vtkOutlineFilter()
        self.tubify             = vtk.vtkTubeFilter()
        self.outline_actor      = vtk.vtkActor()
        self.outline_mapper     = vtk.vtkPolyDataMapper()
        self.outline.SetInputData(builder.mesh)
        self.tubify.SetInputConnection(self.outline.GetOutputPort())
        self.outline_mapper.SetInputConnection(self.tubify.GetOutputPort())
        self.outline_actor.SetMapper(self.outline_mapper)
        self.outline_actor.GetProperty().SetColor(0.5, 0.5, 0.5)

        self.data_actor          = vtk.vtkActor()        
        self.data_mapper         = vtk.vtkDataSetMapper()
        self.data_mapper.SetInputData(builder.mesh)
        self.data_mapper.SetScalarRange(float(var_range[0]), float(var_range[1]))
        self.data_actor.SetMapper(self.data_mapper)
        self.data_actor.GetProperty().SetOpacity(0.1)

        self.sbar_actor = vtk.vtkScalarBarActor()
        self.sbar_actor.SetLookupTable(self.slice_mapper.GetLookupTable())
        self.sbar_actor.SetMaximumHeightInPixels(600)
        self.sbar_actor.SetMaximumWidthInPixels(150)
        self.sbar_actor.SetTitleRatio(0.2) 
        lprop : vtk.vtkTextProperty = self.sbar_actor.GetLabelTextProperty()
        lprop.SetColor(0.5, 0.5, 0.5)
        tprop : vtk.vtkTextProperty = self.sbar_actor.GetTitleTextProperty()
        tprop.SetColor(0.5, 0.5, 0.5)

        self.renderer.SetBackground(1., 1., 1.)
        self.render_window.OffScreenRenderingOn()
        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.renderer.AddActor(self.outline_actor)
        self.renderer.AddActor(self.slice_actor)
        self.renderer.AddActor(self.sbar_actor)

        self.renderer.ResetCamera()


    @property
    def ctrl(self):
        return self.server.controller
        
    @property
    def state(self):
        return self.server.state

    @property
    def t_slice(self):
        datavar = self.state.data_var
        m       = self.state.time_active
        mesh    = self.t_cache.get((m, datavar))
        if mesh is None:
            criteria = {}
            criteria[self.builder.t] = m
            da = self.builder.dataset[datavar].sel(**criteria)
            da.load()
            mesh = da.pyvista.mesh(x=self.builder.x, y=self.builder.y, z=self.builder.z)
            self.t_cache[(m, datavar)] = mesh
        return mesh
 
    @property
    def slice_dimension(self):
        return self.state.slice_dim

    @slice_dimension.setter
    def slice_dimension(self, dim : str) -> None:
        print(f"Setting slice dimension to {dim}")
        self.state.slice_dim = dim
        self.UpdateSlicer(dim)
        self.on_data_change()

    @property
    def slice_value(self):
        return self.state.dimval

    @slice_value.setter
    def slice_value(self, value : float) -> None:
        print(f"Updating slice value tp {value}")
        self.state.dimval = value
        self.on_data_change()

    @property
    def view_mode(self):
        return self.state.view_mode
    
    @view_mode.setter
    def view_mode(self, mode):
        self.state.view_mode = mode
        self.on_view_mode_change("2D")

    @property
    def color_map(self):
        return self.state.cmap
    
    @color_map.setter
    def color_map(self, cmap):
        self.state.cmap = cmap
        self.on_colormap_change(cmap)

    @change("cmap")
    def on_colormap_change(self, cmap, **_):
        use_preset(self.slice_actor, self.data_actor, cmap)
        self.ctrl.view_update() 

    @change("logscale")
    def on_log_scale_change(self, logscale, **_):
        update_preset(self.slice_actor, logscale)
        self.ctrl.view_update() 

    @change("view_mode")
    def on_view_mode_change(self, view_mode, **_):
        slice_dim = self.state.slice_dim
        slice_i     = 0 if self.dims[slice_dim] == 'x' else 1 if self.dims[slice_dim] == 'y' else 2

        extents = list(self.extents.values())
        origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2), 
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2), 
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2)
        ]

        camera = self.renderer.GetActiveCamera()
        pos = camera.GetPosition()
        norm = np.linalg.norm(np.array(origin) - np.array(pos))
        print(f"Origin and norm : {origin, norm}")
        if self.state.view_mode == '3D':
            camera.SetPosition(norm, norm, norm)
            camera.SetViewUp(0., 1., 0.)
        elif self.state.view_mode == '2D':
            self.renderer.RemoveActor(self.outline_actor)
            self.renderer.RemoveActor(self.data_actor)
            if slice_i == 0:
                camera.SetPosition(norm, origin[1], origin[2])
                camera.SetViewUp(0., 1., 0.)
            elif slice_i == 1:
                camera.SetPosition(origin[0], norm, origin[2])
                camera.SetViewUp(0., 0., 1.)
            elif slice_i == 2:
                camera.SetPosition(origin[0], origin[1], norm)
                camera.SetViewUp(0., 1., 0.)
            camera.SetFocalPoint(origin[0], origin[1], origin[2])
            camera.OrthogonalizeViewUp()
        self.renderer.SetActiveCamera(camera)
        self.renderer.ResetCamera()
        self.ctrl.view_update()

    @change("data_var", "time_active", "dimval")
    def on_data_change(self, **_):
        dimval    = self.state.dimval
        slice_dim = self.state.slice_dim
        normal      = [0, 0, 0]
        slice_i     = 0 if self.dims[slice_dim] == 'x' else 1 if self.dims[slice_dim] == 'y' else 2
        normal[slice_i] = 1
        
        extents = list(self.extents.values())
        origin = [
            float(extents[0][0] + (extents[0][1] - extents[0][0]) / 2), 
            float(extents[1][0] + (extents[1][1] - extents[1][0]) / 2), 
            float(extents[2][0] + (extents[2][1] - extents[2][0]) / 2)
        ] 
        origin[slice_i] = dimval
        
        self.plane.SetOrigin(origin)
        self.plane.SetNormal(normal)

        self.cutter.SetInputData(self.t_slice)
        self.cutter.SetCutFunction(self.plane)
        self.cutter.Update()
        output = self.cutter.GetOutput()
        vrange = output.GetPointData().GetArray(self.state.data_var).GetRange()
        self.slice_mapper.SetScalarRange(float(vrange[0]), float(vrange[1]))
        self.state.varmin = float(vrange[0])
        self.state.varmax = float(vrange[1])
        self.sbar_actor.SetLookupTable(self.slice_mapper.GetLookupTable())

        if self.state.view_mode == "2D":
            self.on_view_mode_change("2D")
            self.renderer.ResetCamera()

        self.ctrl.view_update()

    @change("outline", "tdata")
    def on_rep_change(self, outline, tdata, **_):
        if outline: 
            self.renderer.AddActor(self.outline_actor)
        else:
            self.renderer.RemoveActor(self.outline_actor)
        if tdata:
            self.renderer.AddActor(self.data_actor)
        else:
            self.renderer.RemoveActor(self.data_actor)
        self.ctrl.view_update()

    @change("varmin", "varmax")
    def on_scalar_change(self, varmin, varmax, **_):
        self.slice_mapper.SetScalarRange(float(varmin), float(varmax))
        self.sbar_actor.SetLookupTable(self.slice_mapper.GetLookupTable())
        self.ctrl.view_update()
        
    @property
    def levcoords(self):
        return self.builder.dataset.coords["level"].to_numpy()

    @property
    def timecoords(self):
        return self.builder.dataset.coords["month"].to_numpy()
    
    def UpdateSlicer(self, dim):
        ext = self.extents[dim]
        self.state.dimval = float(ext[0] + (ext[1] - ext[0]) / 2)
        self.state.dimmin = float(ext[0])
        self.state.dimmax = float(ext[1])

    def start(self, **kwargs):
        self.ui.server.start(**kwargs)

    @property
    def ui(self):
        if self._ui:
            return self._ui

        style = dict(density="compact", hide_details=True)

        with SinglePageWithDrawerLayout(self.server, full_height=True) as layout:
            self._ui = layout
            layout.title.set_text("Slice Explorer")
            
            with layout.toolbar.clear():
                v3.VBtn(icon="mdi-crop-free", click=self.ctrl.view_reset_camera)

                with v3.VBtnToggle(
                    v_model=("view_mode", "3D"), 
                    mandatory=True, 
                    variant="outlined",
                    classes="mx-4",
                    **style,
                ):
                    v3.VBtn(icon="mdi-video-2d", value="2D"),
                    v3.VBtn(icon="mdi-video-3d", value="3D"),
                
                #with v3.VItemGroup(v_model=("rep3d", [True, False])):
                html.Div("3D Representation", v_show="view_mode === '3D'", **style)
                v3.VCheckbox(v_model=("outline", True), v_show="view_mode === '3D'", label="Outline", **style)
                v3.VCheckbox(v_model=("tdata", False), v_show="view_mode === '3D'", label="Semi-Transparent Data", **style)

                v3.VSpacer()

                v3.VSwitch(
                    label="Scroll",
                    color="primary",
                    v_model=("vscroll", False),
                    **style,
                )

            with layout.drawer as drawer:
                drawer.width = 400                
                with v3.VCard() :
                    with v3.VCardTitle():
                        html.Div(
                            "Slice Setting"
                        )
                    with v3.VCardText():
                        v3.VSelect(
                            label="Time",
                            v_model=("time_active", next(iter(self.timecoords.tolist()))),
                            items=("times_available", self.timecoords.tolist()),
                        )
                
                        v3.VSelect(
                            label="Slice Dimension",
                            v_model=("slice_dim",),
                            items=("slice_dims", list(self.dims.keys())),
                            update_modelValue=(self.UpdateSlicer, "[$event]"),
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
                        html.Div(
                            "Color Setting"
                        )
                    with v3.VCardText():
                        v3.VSelect(
                            v_model=("cmap", next(iter(colors))),
                            items=("colormaps", colors),
                            outlined=True,
                            dense=True,
                            hide_details=True,
                            classes="pt-1",
                        )
                        v3.VCheckbox(
                            label="Use log scale",
                            v_model=("logscale", False)
                        )
                        with html.Div("Scalar Range"):
                            v3.VTextField(v_model=("varmin",), label="min", outlined=True, style="height=50px")
                            v3.VTextField(v_model=("varmax",), label="max", outlined=True, style="height=50px")
                            with v3.VBtn(icon=True, outlined=True, style="height: 40px; width: 40px", ):
                                v3.VIcon("mdi-restore")

            with layout.content:
                with vtkw.VtkRemoteView(self.render_window, interactive_ratio=1) as view:
                    self.ctrl.view_update = view.update
                    self.ctrl.view_reset_camera = view.reset_camera
                html.Div(v_show="vscroll",
                         style="position:absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;") 

            return layout