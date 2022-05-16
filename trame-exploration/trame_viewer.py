import numpy as np
import pyvista as pv

from trame.app import get_server, jupyter
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, vuetify

from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

# -----------------------------------------------------------------------------
# Initialize a trame server
# -----------------------------------------------------------------------------
server = get_server()
state, ctrl = server.state, server.controller
ctrl.on_server_ready.add(ctrl.view_update)

# -----------------------------------------------------------------------------
# PyVista / VTK pipline
# -----------------------------------------------------------------------------

PLOTTER = pv.Plotter()
DAYS = None

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------

@state.change("time")
def update_time(time, **kwargs):
    ctrl.time_update(time)
    ctrl.view_update()

    state.time_label = "Day: {:d}".format(DAYS[time] - DAYS[0])

# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------

def register_dataset(ds, remote_rendering=True):
    global DAYS
    DAYS = ds.time.values.astype('timedelta64[D]').astype('int')
    state.time_max = len(ds.time) - 1

    xg = ds.XG_agg.values
    yg = ds.YG_agg.values
    zg = ds.Zl.values

    # manually extend arrays
    dxg = xg[-1] - xg[-2]
    xg = np.concatenate([xg, [xg[-1] + dxg]])

    dyg = yg[-1] - yg[-2]
    yg = np.concatenate([yg, [yg[-1] + dyg]])

    dz = ds.drF.values
    zg = np.concatenate([zg, [zg[-1] - dz[-1]]])

    aspect = 0.3e3
    offset = 4000

    T_sargs = dict(height=0.25, vertical=True, position_x=0.05, position_y=0.05)
    eddy_sargs = dict(height=0.25, vertical=True, position_x=0.9, position_y=0.05)
    cpos = [(-7660.16298698021, -12605.978568447243, 12085.265135261985),
             (5610.073566725802, 1485.4731686040536, -552.5943624341437),
             (0.38039384351927424, 0.39270852688016344, 0.8373055217351943)]
    PLOTTER.camera_position = cpos


    grid_l = pv.RectilinearGrid(xg/aspect, yg/aspect + offset, zg)
    grid_r = pv.RectilinearGrid(xg/aspect + 2*offset, yg/aspect - offset, zg)

    def load_fields(time):
        grid_l.cell_data["T"] = ds["T"][time].values.flatten()
        grid_r.cell_data["eddy_forc"] = ds["eddyV"][time].values.flatten()

    # Preload initial timestep in mesh
    load_fields(0)

    if remote_rendering:
        PLOTTER.clear()
        PLOTTER.add_mesh(grid_l, show_edges=True, scalars='T',
                 clim=[0, 8], cmap='magma',
                 scalar_bar_args=T_sargs, show_scalar_bar=True)
        PLOTTER.add_mesh(grid_r, show_edges=True, scalars='eddy_forc',
                 clim=[-2e5, 2e5], cmap='RdBu_r',
                 scalar_bar_args=eddy_sargs, show_scalar_bar=True)
        ctrl.time_update = load_fields
    else:
        geo_filter = vtkDataSetSurfaceFilter()
        poly_l = vtkPolyData()
        poly_r = vtkPolyData()

        def load_fields_for_local(time):
            load_fields(time)

            geo_filter.SetInputData(grid_l)
            geo_filter.Update()
            poly_l.ShallowCopy(geo_filter.GetOutput())

            geo_filter.SetInputData(grid_r)
            geo_filter.Update()
            poly_r.ShallowCopy(geo_filter.GetOutput())

            PLOTTER.clear()
            PLOTTER.add_mesh(poly_l, show_edges=True, scalars='T',
                 clim=[0, 8], cmap='magma',
                 scalar_bar_args=T_sargs, show_scalar_bar=True)
            PLOTTER.add_mesh(poly_r, show_edges=True, scalars='eddy_forc',
                 clim=[-2e5, 2e5], cmap='RdBu_r',
                 scalar_bar_args=eddy_sargs, show_scalar_bar=True)

        ctrl.time_update = load_fields_for_local

    # Make sure regardless of rendering we have the first ts
    ctrl.time_update(0)

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

def register_ui(server, remote_rendering=True, name="main"):
    with SinglePageLayout(server, name) as layout:
        with layout.toolbar as tb:
            tb.clear()
            with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
                vuetify.VIcon("mdi-crop-free")
            vuetify.VSlider(
                label="Time",
                v_model=("time", 0),
                min=0, max=("time_max", 0), step=1,
                dense=True, hide_details=True, style="max-width: 300px;",
            )
            tb.add_child("{{ time }}")
            vuetify.VSpacer()
            tb.add_child("{{ time_label }}")


        with layout.content:
            with vuetify.VContainer(fluid=True, classes="fill-height pa-0 ma-0"):
                view = None
                if remote_rendering:
                    view = vtk.VtkRemoteView(PLOTTER.ren_win, interactive_ratio=1)
                else:
                    view = vtk.VtkLocalView(PLOTTER.ren_win)
                ctrl.view_update = view.update
                ctrl.view_reset_camera = view.reset_camera

# -----------------------------------------------------------------------------
# Jupyter helper
# -----------------------------------------------------------------------------
def show(ds, remote_rendering=True):
    register_dataset(ds, remote_rendering)
    register_ui(server, remote_rendering=remote_rendering)
    jupyter.show(server)
    # ctrl.view_reset_camera()
