from pathlib import Path

import healpy as hp
import numpy as np
import vtk
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
import xarray as xr
from vtk.util import numpy_support
from vtkmodules.vtkCommonCore import vtkLookupTable

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from pan3d.ui.css import base, preview
from pan3d.utils.convert import to_image
from pan3d.utils.presets import PRESETS, set_preset
from pan3d.widgets.pan3d_view import Pan3DView
from trame.app import TrameApp
from trame.decorators import change
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame.widgets import vuetify3 as v3


def load_to_vtk(file_path):
    ds = xr.open_zarr(file_path)
    nside = 64
    n_cells = 12 * nside**2
    pixel_indices = np.arange(n_cells)
    R_earth = 6371.0

    # Generate Quad Boundaries (NESTED)
    boundaries = hp.boundaries(nside, pixel_indices, step=1, nest=True).transpose(
        0, 2, 1
    )
    # Per-quad vertices.
    points_per_cell = boundaries.shape[1]
    if points_per_cell != 4:
        msg = (
            f"Expected 4 quad vertices per cell, got points_per_cell={points_per_cell}"
        )
        raise ValueError(msg)

    all_points_np = (
        boundaries.reshape(-1, 3).astype(np.float32) * R_earth
    )  # (n_cells*4, 3)

    # Weld identical vertices across neighboring cells to remove border cracks.
    # We quantize coordinates to make floating-point differences mergeable.
    eps = 1e-5 * R_earth
    q = np.round(all_points_np / eps).astype(np.int64)

    # Important: with both return_index=True and return_inverse=True, numpy returns:
    # (unique_values, unique_indices, inverse_mapping) in that order.
    _, unique_index, inverse = np.unique(
        q, axis=0, return_inverse=True, return_index=True
    )
    unique_points_np = all_points_np[unique_index].astype(np.float32)
    cell_point_ids = inverse.reshape(n_cells, points_per_cell)

    # Extract MSL data
    data_values_np = ds.msl.isel(time=0, ensemble=0).values.flatten().astype(np.float32)

    # ==========================================
    # PART 2: CONVERT TO VTK OBJECTS (Fixed Functions)
    # ==========================================
    # 1. Create vtkPoints
    points = vtk.vtkPoints()
    # Correct function: numpy_to_vtk
    vtk_pts_array = numpy_support.numpy_to_vtk(unique_points_np, deep=True)
    points.SetData(vtk_pts_array)

    # 2. Create vtkCellArray (Connect points into Quads)
    # Using vtkQuad cells keeps the intended quad structure.
    cells = vtk.vtkCellArray()
    for i in range(n_cells):
        quad = vtk.vtkQuad()
        pid0, pid1, pid2, pid3 = cell_point_ids[i]
        quad.GetPointIds().SetId(0, int(pid0))
        quad.GetPointIds().SetId(1, int(pid1))
        quad.GetPointIds().SetId(2, int(pid2))
        quad.GetPointIds().SetId(3, int(pid3))
        cells.InsertNextCell(quad)

    # 3. Create vtkUnstructuredGrid
    u_grid = vtk.vtkUnstructuredGrid()
    u_grid.SetPoints(points)
    u_grid.SetCells(vtk.VTK_QUAD, cells)

    # 4. Attach Cell Data (MSL)
    # Correct function: numpy_to_vtk
    msl_vtk_array = numpy_support.numpy_to_vtk(data_values_np, deep=True)
    msl_vtk_array.SetName("msl")
    u_grid.GetCellData().SetScalars(msl_vtk_array)

    # Also compute point scalars by averaging the surrounding quad values.
    # This enables smooth (vertex-interpolated) color gradients across the globe.
    num_points = unique_points_np.shape[0]
    pt_ids = cell_point_ids.reshape(-1).astype(np.int64)  # (n_cells*4,)
    pt_vals = np.repeat(data_values_np, 4).astype(np.float32)

    pt_count = np.bincount(pt_ids, minlength=num_points).astype(np.float32)
    pt_sum = np.bincount(pt_ids, weights=pt_vals, minlength=num_points).astype(
        np.float32
    )
    point_values_np = np.divide(
        pt_sum, pt_count, out=np.zeros_like(pt_sum), where=pt_count > 0
    )

    msl_point_vtk_array = numpy_support.numpy_to_vtk(
        point_values_np.astype(np.float32, copy=False), deep=True
    )
    msl_point_vtk_array.SetName("msl")
    u_grid.GetPointData().SetScalars(msl_point_vtk_array)

    return u_grid


class HealPixViewer(TrameApp):
    def __init__(self, server=None, local_rendering=None):
        super().__init__(server, client_type="vue3")
        self.server.enable_module(base)
        self.server.enable_module(preview)

        # CLI
        self.server.cli.add_argument(
            "--wasm",
            help="Use WASM for local rendering",
            action="store_true",
        )
        self.server.cli.add_argument(
            "--anari",
            help="Use anari for remote rendering",
            action="store_true",
        )

        self.server.cli.add_argument(
            "--data",
            help="Zarr file to load",
        )

        args, _ = self.server.cli.parse_known_args()
        self.anari = args.anari
        zarr_file = Path(args.data).resolve()

        # Local rendering
        self.local_rendering = local_rendering
        if args.wasm:
            self.local_rendering = "wasm"

        # setup
        self.last_preset = None
        self.ds = load_to_vtk(zarr_file)
        self._setup_vtk()
        self._build_ui()
        self.reset_color_range()

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
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.mapper = vtk.vtkDataSetMapper(
            input_data=self.ds,
            scalar_visibility=1,
            interpolate_scalars_before_mapping=1,
            lookup_table=self.lut,
        )
        self.actor = vtkActor(mapper=self.mapper)
        self.renderer.AddActor(self.actor)

        self.actor.property.ambient = 0.2
        self.actor.property.diffuse = 0.8
        self.actor.property.specular = 0.2
        self.actor.property.specular_power = 10.0

        self.renderer.ResetCamera()
        self.interactor.Initialize()

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
    # UI
    # -------------------------------------------------------------------------

    def _build_ui(self, **kwargs):
        self.state.update(
            {
                "trame__title": "HEALPix Explorer",
                "axis_names": ["X", "Y", "Z"],
            }
        )

        with VAppLayout(self.server, fill_height=True) as self.ui:
            # 3D view
            Pan3DView(
                self.render_window,
                local_rendering=self.local_rendering,
                widgets=[self.widget],
            )

            # Control panel
            with v3.VCard(
                classes="controller", rounded=("control_expended || 'circle'",)
            ):
                with v3.VCardTitle(
                    classes=(
                        "`d-flex pa-1 position-fixed bg-white ${control_expended ? 'controller-content rounded-t border-b-thin':'rounded-circle'}`",
                    ),
                    style="z-index: 1;",
                ):
                    v3.VProgressLinear(
                        v_if=("control_expended", True),
                        indeterminate=("trame__busy",),
                        bg_color="rgba(0,0,0,0)",
                        absolute=True,
                        color="primary",
                        location="bottom",
                        height=2,
                    )
                    v3.VProgressCircular(
                        v_else=True,
                        bg_color="rgba(0,0,0,0)",
                        indeterminate=("trame__busy",),
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;",
                        color="primary",
                        width=3,
                    )
                    v3.VBtn(
                        icon="mdi-close",
                        v_if="control_expended",
                        click="control_expended = !control_expended",
                        flat=True,
                        size="sm",
                    )
                    v3.VBtn(
                        icon="mdi-menu",
                        v_else=True,
                        click="control_expended = !control_expended",
                        flat=True,
                        size="sm",
                    )
                    if self.server.hot_reload:
                        v3.VBtn(
                            v_show="control_expended",
                            icon="mdi-refresh",
                            flat=True,
                            size="sm",
                            click=self.ctrl.on_server_reload,
                        )
                    v3.VSpacer()
                    html.Div(
                        "HEALPix Viewer",
                        v_show="control_expended",
                        classes="text-h6 px-2",
                    )
                    v3.VSpacer()

                with v3.VCardText(
                    v_show=("control_expended", True),
                    classes="controller-content py-1 mt-10 px-0",
                ):
                    with v3.VRow(no_gutters=True, classes="align-center mr-0"):
                        with v3.VCol():
                            v3.VTextField(
                                prepend_inner_icon="mdi-water-minus",
                                v_model_number=("color_min", 0),
                                type="number",
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                            )
                        with v3.VCol():
                            v3.VTextField(
                                prepend_inner_icon="mdi-water-plus",
                                v_model_number=("color_max", 1),
                                type="number",
                                hide_details=True,
                                density="compact",
                                flat=True,
                                variant="solo",
                                reverse=True,
                            )
                        with html.Div(classes="flex-0"):
                            v3.VBtn(
                                icon="mdi-arrow-split-vertical",
                                size="sm",
                                density="compact",
                                flat=True,
                                variant="outlined",
                                classes="mx-2",
                                click=self.reset_color_range,
                            )
                    # v3.VDivider()
                    with html.Div(classes="mx-2"):
                        html.Img(
                            src=("preset_img", None),
                            style="height: 0.75rem; width: 100%;",
                            classes="rounded-lg border-thin",
                        )
                    v3.VSelect(
                        placeholder="Color Preset",
                        prepend_inner_icon="mdi-palette",
                        v_model=("color_preset", "Fast"),
                        items=("color_presets", list(PRESETS.keys())),
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("color_min", "color_max", "color_preset")
    def _on_update_color_range(self, color_min, color_max, color_preset, **_):
        if self.last_preset != color_preset:
            self.last_preset = color_preset
            set_preset(self.lut, color_preset)
            self.state.preset_img = to_image(self.lut, 255)

        self.mapper.SetScalarRange(color_min, color_max)
        self.ctrl.view_update()

    def reset_color_range(self):
        array = self.ds.GetPointData().GetScalars()
        vmin, vmax = array.GetRange(-1)
        try:
            p1, p99 = np.nanpercentile(array, [1, 99])
            if np.isfinite(p1) and np.isfinite(p99) and p99 > p1:
                vmin, vmax = float(p1), float(p99)
        except Exception:
            pass

        with self.state:
            self.state.color_min = float(vmin)
            self.state.color_max = float(vmax)


def main():
    app = HealPixViewer()
    app.server.start()


if __name__ == "__main__":
    main()
