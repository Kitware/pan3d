from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkRenderWindow,
    vtkActor,
    vtkPolyDataMapper,
)
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkDataSetAttributes
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkIOLegacy import vtkDataSetReader
from vtkmodules.vtkFiltersCore import vtkCellDataToPointData
from vtkmodules.vtkFiltersModeling import (
    vtkBandedPolyDataContourFilter,
    vtkLoopSubdivisionFilter,
)
from vtkmodules.vtkFiltersCore import vtkAssignAttribute

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

import xarray as xr
from pathlib import Path

from trame.decorators import TrameApp, change
from trame.app import get_server

from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3, html

from pan3d.utils.convert import to_float, to_image
from pan3d.utils.presets import apply_preset, COLOR_PRESETS

from pan3d.ui.vtk_view import Pan3DView
from pan3d.ui.css import base, preview


@TrameApp()
class ContourExplorer:
    def __init__(self, server=None, local_rendering=None):
        self.server = get_server(server, client_type="vue3")
        self.server.enable_module(base)
        self.server.enable_module(preview)

        # CLI
        self.server.cli.add_argument(
            "--wasm",
            help="Use WASM for local rendering",
            action="store_true",
        )
        self.server.cli.add_argument(
            "--vtkjs",
            help="Use vtk.js for local rendering",
            action="store_true",
        )
        self.server.cli.add_argument(
            "--mesh",
            help="Geometry file",
        )
        self.server.cli.add_argument(
            "--fields",
            help="Fields HDF5 file",
        )

        args, _ = self.server.cli.parse_known_args()
        mesh_file = Path(args.mesh).resolve()
        fields_file = Path(args.fields).resolve()

        # Local rendering
        self.local_rendering = local_rendering
        if args.wasm:
            self.local_rendering = "wasm"
        if args.vtkjs:
            self.local_rendering = "vtkjs"

        # setup
        self.last_field = None
        self.last_preset = None
        self.xr = xr.open_dataset(fields_file, engine="netcdf4")
        self.mesh = vtkDataSetReader(file_name=str(mesh_file))()
        self._setup_vtk()
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self):
        self.renderer = vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtkRenderWindowInteractor()
        self.render_window = vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # Need explicit geometry extraction when used with WASM
        self.geometry = vtkDataSetSurfaceFilter(input_data=self.mesh)
        self.cell2point = vtkCellDataToPointData(
            input_connection=self.geometry.output_port
        )
        self.refine = vtkLoopSubdivisionFilter(
            input_connection=self.cell2point.output_port, number_of_subdivisions=1
        )
        self.assign = vtkAssignAttribute(input_connection=self.refine.output_port)
        self.assign.Assign(
            "scalars",
            vtkDataSetAttributes.SCALARS,
            vtkDataObject.FIELD_ASSOCIATION_POINTS,
        )
        self.bands = vtkBandedPolyDataContourFilter(
            input_connection=self.assign.output_port,
            generate_contour_edges=1,
        )
        self.mapper = vtkPolyDataMapper(
            input_connection=self.bands.output_port,
            scalar_visibility=1,
            interpolate_scalars_before_mapping=1,
        )
        self.mapper.SelectColorArray("scalars")
        self.mapper.SetScalarModeToUsePointFieldData()
        self.actor = vtkActor(mapper=self.mapper)

        # contour lines
        self.mapper_lines = vtkPolyDataMapper(
            input_connection=self.bands.GetOutputPort(1),
        )
        self.actor_lines = vtkActor(mapper=self.mapper_lines)
        self.actor_lines.property.color = [0, 0, 0]
        self.actor_lines.property.line_width = 2

        self.renderer.AddActor(self.actor)
        self.renderer.AddActor(self.actor_lines)

        self.renderer.ResetCamera(self.mesh.bounds)

        self.interactor.Initialize()

        axes_actor = vtkAxesActor()
        self.widget = vtkOrientationMarkerWidget()
        self.widget.SetOrientationMarker(axes_actor)
        self.widget.SetInteractor(self.interactor)
        self.widget.SetViewport(0.85, 0, 1, 0.15)
        self.widget.EnabledOn()
        self.widget.InteractiveOff()

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    @property
    def state(self):
        """Returns the current the trame server state."""
        return self.server.state

    @property
    def ctrl(self):
        """Returns the Controller for the trame server."""
        return self.server.controller

    # -------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------

    def _build_ui(self, **kwargs):
        self.state.update(
            {
                "trame__title": "Contour Explorer",
                "import_pending": False,
                "control_expended": True,
                "axis_names": ["X", "Y", "Z"],
                "scale_x": 1,
                "scale_y": 1,
                "scale_z": 0.01,
            }
        )

        fields = list(self.xr.keys())
        active_field = fields[0]
        nb_times = self.xr[active_field].shape[0]

        with VAppLayout(self.server, fill_height=True) as layout:
            self.ui = layout

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
                        "Contours Explorer",
                        v_show="control_expended",
                        classes="text-h6 px-2",
                    )
                    v3.VSpacer()

                with v3.VCardText(
                    v_show=("control_expended", True),
                    classes="controller-content py-1 mt-10 px-0",
                ):

                    # Actor scaling
                    with v3.VTooltip(text="Representation scaling"):
                        with html.Template(v_slot_activator="{ props }"):
                            with v3.VRow(
                                v_bind="props",
                                no_gutter=True,
                                classes="align-center my-0 mx-0 border-b-thin",
                            ):
                                v3.VIcon(
                                    "mdi-ruler-square",
                                    classes="ml-2 text-medium-emphasis",
                                )
                                with v3.VCol(classes="pa-0", v_if="axis_names?.[0]"):
                                    v3.VTextField(
                                        v_model=("scale_x", 1),
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                        reverse=True,
                                        raw_attrs=[
                                            'pattern="^\d*(\.\d)?$"',  # noqa: W605
                                            'min="0.001"',
                                            'step="0.1"',
                                        ],
                                        type="number",
                                    )
                                with v3.VCol(classes="pa-0", v_if="axis_names?.[1]"):
                                    v3.VTextField(
                                        v_model=("scale_y", 1),
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                        reverse=True,
                                        raw_attrs=[
                                            'pattern="^\d*(\.\d)?$"',  # noqa: W605
                                            'min="0.001"',
                                            'step="0.1"',
                                        ],
                                        type="number",
                                    )
                                with v3.VCol(classes="pa-0", v_if="axis_names?.[2]"):
                                    v3.VTextField(
                                        v_model=("scale_z", 1),
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                        reverse=True,
                                        raw_attrs=[
                                            'pattern="^\d*(\.\d)?$"',  # noqa: W605
                                            'min="0.001"',
                                            'step="0.1"',
                                        ],
                                        type="number",
                                    )

                    v3.VSelect(
                        placeholder="Color By",
                        prepend_inner_icon="mdi-format-color-fill",
                        v_model=("field", fields[0]),
                        items=("fields", fields),
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )
                    v3.VDivider()
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
                        v_model=("color_preset", "Cool to Warm"),
                        items=("color_presets", COLOR_PRESETS),
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )

                    v3.VDivider()

                    # contours
                    with v3.VTooltip(
                        text=("`Number of contours: ${nb_contours}`",),
                    ):
                        with html.Template(v_slot_activator="{ props }"):
                            with html.Div(
                                classes="d-flex pr-2",
                                v_bind="props",
                            ):
                                v3.VSlider(
                                    v_model=("nb_contours", 20),
                                    min=2,
                                    max=50,
                                    step=1,
                                    prepend_icon="mdi-fingerprint",
                                    hide_details=True,
                                    density="compact",
                                    flat=True,
                                    variant="solo",
                                )

                    v3.VDivider()
                    # Time slider
                    with v3.VTooltip(
                        v_if="slice_t_max > 0",
                        text=("`time: ${time_idx + 1} / ${slice_t_max+1}`",),
                    ):
                        with html.Template(v_slot_activator="{ props }"):
                            with html.Div(
                                classes="d-flex pr-2",
                                v_bind="props",
                            ):
                                v3.VSlider(
                                    prepend_icon="mdi-clock-outline",
                                    v_model=("time_idx", 0),
                                    min=0,
                                    max=("slice_t_max", nb_times - 1),
                                    step=1,
                                    hide_details=True,
                                    density="compact",
                                    flat=True,
                                    variant="solo",
                                )

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("scale_x", "scale_y", "scale_z")
    def _on_scale_change(self, scale_x, scale_y, scale_z, **_):
        self.actor.SetScale(
            to_float(scale_x),
            to_float(scale_y),
            to_float(scale_z),
        )
        self.actor_lines.SetScale(
            to_float(scale_x),
            to_float(scale_y),
            to_float(scale_z),
        )

        if self.actor.visibility:
            self.renderer.ResetCamera()

            if self.local_rendering:
                self.ctrl.view_update(push_camera=True)

            self.ctrl.view_reset_camera()

    @change("field", "time_idx")
    def _on_update_data(self, field, time_idx, **_):
        # update array
        array = self.xr[field][time_idx].values
        self.mesh.cell_data["scalars"] = array

        # update range
        if self.last_field != field:
            self.last_field = field
            self.reset_color_range()

        self.ctrl.view_update()

    @change("color_min", "color_max", "color_preset", "nb_contours")
    def _on_update_color_range(
        self, nb_contours, color_min, color_max, color_preset, **_
    ):
        if self.last_preset != color_preset:
            self.last_preset = color_preset
            apply_preset(self.actor, [color_min, color_max], color_preset)
            self.state.preset_img = to_image(self.actor.mapper.lookup_table, 255)

        self.mapper.SetScalarRange(color_min, color_max)
        self.bands.GenerateValues(nb_contours, [color_min, color_max])
        self.ctrl.view_update()

    def reset_color_range(self):
        if self.state.field is None:
            return

        field_array = self.xr[self.state.field].values
        with self.state:
            self.state.color_min = float(field_array.min())
            self.state.color_max = float(field_array.max())


def main():
    app = ContourExplorer()
    app.server.start()


if __name__ == "__main__":
    main()
