import vtk
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor

import json
import math
import traceback
from pathlib import Path

from trame.decorators import TrameApp, change, trigger
from trame.app import get_server

from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html, client, vtk as vtkw, vuetify3 as v3

from pan3d import catalogs as pan3d_catalogs
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource
from pan3d.utils.presets import apply_preset, COLOR_PRESETS


class CollapsableSection:
    id_count = 0

    def __init__(self, title, var_name=None, expended=False):
        CollapsableSection.id_count += 1
        show = var_name or f"show_section_{CollapsableSection.id_count}"
        with v3.VCardSubtitle(
            classes="px-0 ml-n3 d-flex align-center font-weight-bold pointer",
            click=f"{show} = !{show}",
        ) as container:
            v3.VIcon(
                f"{{{{ {show} ? 'mdi-menu-down' : 'mdi-menu-right' }}}}",
                size="sm",
                classes="pa-0 ma-0",
            )
            container.add_child(title)
        self.content = v3.VSheet(
            border="opacity-25 thin",
            classes="overflow-hidden mx-auto mt-1 mb-2",
            rounded="lg",
            v_show=(show, expended),
        )


def to_float(v):
    v = float(v)
    if math.isnan(v) or v < 0.0001:
        v = 0.0001
    return v


def update_camera(camera, props):
    for k, v in props.items():
        setattr(camera, k, v)


XYZ = ["x", "y", "z"]
SLICE_VARS = ["slice_{}_range", "slice_{}_cut", "slice_{}_type", "slice_{}_step"]
VIEW_UPS = {
    (1, 1, 1): (0, 0, 1),
    (-1, -1, 1): (0, 0, 1),
    (1, 0, 0): (0, 0, 1),
    (0, 1, 0): (0, 0, 1),
    (0, 0, 1): (0, 1, 0),
}


@TrameApp()
class XarrayPreview:
    """Create a Trame GUI for a Pan3D Xarray dataset"""

    def __init__(
        self,
        server=None,
    ):
        """Create an instance of the XarrayPreview class.

        Parameters:
            server: Trame server name or instance.
        """
        self.server = get_server(server, client_type="vue3")
        if self.server.hot_reload:
            self.ctrl.on_server_reload.add(self._build_ui)

        # cli
        self.server.cli.add_argument(
            "--import-state",
            help="Provide path to state file to import",
        )
        self.server.cli.add_argument(
            "--xarray-file",
            help="Provide path to xarray file",
        )
        self.ctrl.on_server_ready.add(self._process_cli)

        # GUI initial state
        self.state.update(
            {
                "slice_extents": {},
                "axis_names": [],
                "load_button_text": "Load",
                "can_load": True,
                "xarray_info": [],
                "view_locked": False,
                "view_3d": True,
                "t_labels": [],
                "dataset_bounds": [0, 1, 0, 1, 0, 1],
                "data_origin_id_to_desc": {},
            }
        )
        self._import_pending = False
        self.ui = None
        self._setup_vtk()
        self._build_ui()

    # -------------------------------------------------------------------------
    # VTK Setup
    # -------------------------------------------------------------------------

    def _setup_vtk(self):
        self.renderer = vtk.vtkRenderer(background=(0.8, 0.8, 0.8))
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.render_window = vtk.vtkRenderWindow(off_screen_rendering=1)

        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        self.source = vtkXArrayRectilinearSource()
        self.mapper = vtk.vtkDataSetMapper(input_connection=self.source.output_port)
        self.actor = vtk.vtkActor(mapper=self.mapper, visibility=0)

        self.interactor.Initialize()

        axes_actor = vtkAxesActor()
        self.widget = vtkOrientationMarkerWidget()
        self.widget.SetOrientationMarker(axes_actor)
        self.widget.SetInteractor(self.interactor)
        self.widget.EnabledOff()
        self.widget.SetViewport(0.85, 0, 1, 0.15)

        self.renderer.AddActor(self.actor)

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    def start(self, **kwargs):
        """Initialize the UI and start the server for GeoTrame."""
        self.ui.server.start(**kwargs)

    @property
    async def ready(self):
        """Coroutine to wait for the GeoTrame server to be ready."""
        await self.ui.ready

    @property
    def state(self):
        """Returns the current State of the Trame server."""
        return self.server.state

    @property
    def ctrl(self):
        """Returns the Controller for the Trame server."""
        return self.server.controller

    # -------------------------------------------------------------------------
    # UI
    # -------------------------------------------------------------------------

    def _build_ui(self, **kwargs):
        self.state.trame__title = "Pan3D Xarray Preview"

        with VAppLayout(self.server, fill_height=True) as layout:
            client.Style(Path(__file__).with_name("preview.css").read_text())
            self.ui = layout

            # 3D view
            with vtkw.VtkRemoteView(self.render_window, interactive_ratio=1) as view:
                self.ctrl.view_update = view.update
                self.ctrl.view_reset_camera = view.reset_camera

            # Scroll locking overlay
            html.Div(v_show="view_locked", classes="view-lock")

            # 3D toolbox
            with v3.VCard(classes="view-toolbar pa-1", rounded="lg"):
                with v3.VTooltip(text="Lock view interaction"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon=(
                                "view_locked ? 'mdi-lock-outline' : 'mdi-lock-off-outline'",
                            ),
                            click="view_locked = !view_locked",
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Reset camera"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-crop-free",
                            click=self.ctrl.view_reset_camera,
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Toggle between 3D/2D interaction"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon=("view_3d ? 'mdi-rotate-orbit' : 'mdi-cursor-move'",),
                            click="view_3d = !view_3d",
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Rotate left 90"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-rotate-left",
                            click=(self._rotate_camera, "[-1]"),
                        )
                with v3.VTooltip(text="Rotate right 90"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-rotate-right",
                            click=(self._rotate_camera, "[+1]"),
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text=("`Look toward ${axis_names[0]}`",)):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-x-arrow",
                            click=(self._reset_camera_to_axis, "[[1,0,0]]"),
                        )
                with v3.VTooltip(text=("`Look toward ${axis_names[1]}`",)):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-y-arrow",
                            click=(self._reset_camera_to_axis, "[[0,1,0]]"),
                        )

                with v3.VTooltip(text=("`Look toward ${axis_names[2]}`",)):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-z-arrow",
                            click=(self._reset_camera_to_axis, "[[0,0,1]]"),
                        )
                v3.VDivider(classes="my-1")
                with v3.VTooltip(text="Look toward at an angle"):
                    with html.Template(v_slot_activator="{ props }"):
                        v3.VBtn(
                            v_bind="props",
                            flat=True,
                            density="compact",
                            icon="mdi-axis-arrow",
                            click=(self._reset_camera_to_axis, "[[1,1,1]]"),
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
                classes="alert-position",
            )

            # Control panel
            with v3.VCard(
                classes="controller",
                rounded=("control_expended || 'circle'",),
            ):
                with v3.VCardTitle(
                    classes=(
                        "`d-flex pa-1 position-fixed bg-white border-b-thin ${control_expended?'controller-content rounded-t':'rounded-circle'}`",
                    ),
                    style="z-index: 1;",
                ):
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
                        "Xarray Preview",
                        v_show="control_expended",
                        classes="text-h6 px-2",
                    )
                    v3.VSpacer()

                    with v3.VMenu(v_if="control_expended", density="compact"):
                        with html.Template(v_slot_activator="{props}"):
                            v3.VBtn(
                                v_bind="props",
                                icon="mdi-file-arrow-left-right-outline",
                                flat=True,
                                size="sm",
                                classes="mx-1",
                            )
                        with v3.VList(density="compact"):
                            with v3.VListItem(
                                title="Export state file",
                                disabled=("can_load",),
                                click="utils.download('xarray-state.txt', trigger('download_export'), 'text/plain')",
                            ):
                                with html.Template(v_slot_prepend=True):
                                    v3.VIcon(
                                        "mdi-cloud-download-outline", classes="mr-n5"
                                    )

                            with v3.VListItem(
                                title="Import state file",
                                click="trame.utils.get('document').querySelector('#fileImport').click()",
                            ):
                                html.Input(
                                    id="fileImport",
                                    hidden=True,
                                    type="file",
                                    change=(
                                        self._import_file_upload,
                                        "[$event.target.files]",
                                    ),
                                    __events=["change"],
                                )
                                with html.Template(v_slot_prepend=True):
                                    v3.VIcon(
                                        "mdi-cloud-upload-outline", classes="mr-n5"
                                    )

                with v3.VCardText(
                    v_show=("control_expended", True),
                    classes="controller-content py-1 mt-10",
                ):
                    with CollapsableSection(
                        "Data origin", "show_data_origin", True
                    ).content:
                        v3.VSelect(
                            label="Source",
                            v_model=("data_origin_source", "xarray"),
                            items=(
                                "data_origin_sources",
                                pan3d_catalogs.list_availables(),
                            ),
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                        )
                        v3.VDivider()
                        v3.VTextField(
                            placeholder="Location",
                            v_if="['file', 'url'].includes(data_origin_source)",
                            v_model=("data_origin_id", ""),
                            hide_details=True,
                            density="compact",
                            flat=True,
                            variant="solo",
                            append_inner_icon=(
                                "data_origin_id_error ? 'mdi-file-document-alert-outline' : undefined",
                            ),
                            error=("data_origin_id_error", False),
                        )

                        with v3.VTooltip(
                            v_else=True,
                            text=("`${ data_origin_id_to_desc[data_origin_id] }`",),
                        ):
                            with html.Template(v_slot_activator="{ props }"):
                                v3.VSelect(
                                    v_bind="props",
                                    label="Name",
                                    v_model="data_origin_id",
                                    items=("data_origin_ids", []),
                                    hide_details=True,
                                    density="compact",
                                    flat=True,
                                    variant="solo",
                                )

                        v3.VDivider()
                        v3.VBtn(
                            "{{ load_button_text }}",
                            block=True,
                            classes="text-none",
                            flat=True,
                            density="compact",
                            rounded=0,
                            disabled=("!data_origin_id?.length || !can_load",),
                            color=("can_load ? 'primary': undefined",),
                            click=(
                                self._load_dataset,
                                "[data_origin_source, data_origin_id]",
                            ),
                        )

                    with CollapsableSection(
                        "Data information", "show_data_information"
                    ).content:
                        with v3.VTable(density="compact", hover=True):
                            with html.Tbody():
                                with html.Template(
                                    v_for="item, i in xarray_info", key="i"
                                ):
                                    with v3.VTooltip():
                                        with html.Template(
                                            v_slot_activator="{ props }"
                                        ):
                                            with html.Tr(
                                                v_bind="props", classes="pointer"
                                            ):
                                                with html.Td(
                                                    classes="d-flex align-center text-no-wrap"
                                                ):
                                                    v3.VIcon(
                                                        "{{ item.icon }}",
                                                        size="sm",
                                                        classes="mr-2",
                                                    )
                                                    html.Div("{{ item.name }}")
                                                html.Td(
                                                    "{{ item.length }}",
                                                    classes="text-right",
                                                )

                                        with v3.VTable(
                                            density="compact",
                                            theme="dark",
                                            classes="no-bg ma-0 pa-0",
                                        ):
                                            with html.Tbody():
                                                with html.Tr(
                                                    v_for="attr, j in item.attrs",
                                                    key="j",
                                                ):
                                                    html.Td(
                                                        "{{ attr.key }}",
                                                    )
                                                    html.Td(
                                                        "{{ attr.value }}",
                                                    )

                    with CollapsableSection("Rendering", "show_rendering").content:
                        v3.VSelect(
                            placeholder="Data arrays",
                            prepend_inner_icon="mdi-database",
                            hide_selected=True,
                            v_model=("data_arrays", []),
                            items=("data_arrays_available", []),
                            multiple=True,
                            hide_details=True,
                            density="compact",
                            chips=True,
                            closable_chips=True,
                            flat=True,
                            variant="solo",
                        )
                        v3.VDivider()
                        v3.VSelect(
                            placeholder="Color By",
                            prepend_inner_icon="mdi-format-color-fill",
                            v_model=("color_by", None),
                            items=("data_arrays", []),
                            clearable=True,
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
                                    v_model_number=("color_min", 0.45),
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
                                    v_model_number=("color_max", 5.45),
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
                                    click=self._reset_color_range,
                                )
                        v3.VDivider()
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
                        # X crop/cut
                        with v3.VTooltip(
                            v_if="axis_names?.[0]",
                            text=(
                                "`${axis_names[0]}: [${dataset_bounds[0]}, ${dataset_bounds[1]}] ${slice_x_type ==='range' ? ('(' + slice_x_range.map((v,i) => v+1).concat(slice_x_step).join(', ') + ')'): slice_x_cut}`",
                            ),
                        ):
                            with html.Template(v_slot_activator="{ props }"):
                                with html.Div(
                                    classes="d-flex",
                                    v_if="axis_names?.[0]",
                                    v_bind="props",
                                ):
                                    v3.VRangeSlider(
                                        v_if="slice_x_type === 'range'",
                                        prepend_icon="mdi-axis-x-arrow",
                                        v_model=("slice_x_range", [0, 1]),
                                        min=("slice_extents[axis_names[0]][0]",),
                                        max=("slice_extents[axis_names[0]][1]",),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                    v3.VSlider(
                                        v_else=True,
                                        prepend_icon="mdi-axis-x-arrow",
                                        v_model=("slice_x_cut", 0),
                                        min=("slice_extents[axis_names[0]][0]",),
                                        max=("slice_extents[axis_names[0]][1]",),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                    v3.VCheckbox(
                                        v_model=("slice_x_type", "range"),
                                        true_value="range",
                                        false_value="cut",
                                        true_icon="mdi-crop",
                                        false_icon="mdi-box-cutter",
                                        hide_details=True,
                                        density="compact",
                                        size="sm",
                                        classes="mx-2",
                                    )

                        # Y crop/cut
                        with v3.VTooltip(
                            v_if="axis_names?.[1]",
                            text=(
                                "`${axis_names[1]}: [${dataset_bounds[2]}, ${dataset_bounds[3]}] ${slice_y_type ==='range' ? ('(' + slice_y_range.map((v,i) => v+1).join(', ') + ', 1)'): slice_y_cut}`",
                            ),
                        ):
                            with html.Template(v_slot_activator="{ props }"):
                                with html.Div(
                                    classes="d-flex",
                                    v_if="axis_names?.[1]",
                                    v_bind="props",
                                ):
                                    v3.VRangeSlider(
                                        v_if="slice_y_type === 'range'",
                                        prepend_icon="mdi-axis-y-arrow",
                                        v_model=("slice_y_range", [0, 1]),
                                        min=("slice_extents[axis_names[1]][0]",),
                                        max=("slice_extents[axis_names[1]][1]",),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                    v3.VSlider(
                                        v_else=True,
                                        prepend_icon="mdi-axis-y-arrow",
                                        v_model=("slice_y_cut", 0),
                                        min=("slice_extents[axis_names[1]][0]",),
                                        max=("slice_extents[axis_names[1]][1]",),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                    v3.VCheckbox(
                                        v_model=("slice_y_type", "range"),
                                        true_value="range",
                                        false_value="cut",
                                        true_icon="mdi-crop",
                                        false_icon="mdi-box-cutter",
                                        hide_details=True,
                                        density="compact",
                                        size="sm",
                                        classes="mx-2",
                                    )

                        # Z crop/cut
                        with v3.VTooltip(
                            v_if="axis_names?.[2]",
                            text=(
                                "`${axis_names[2]}: [${dataset_bounds[4]}, ${dataset_bounds[5]}] ${slice_z_type ==='range' ? ('(' + slice_z_range.map((v,i) => v+1).join(', ') + ', 1)'): slice_z_cut}`",
                            ),
                        ):
                            with html.Template(v_slot_activator="{ props }"):
                                with html.Div(
                                    classes="d-flex",
                                    v_bind="props",
                                ):
                                    v3.VRangeSlider(
                                        v_if="slice_z_type === 'range'",
                                        prepend_icon="mdi-axis-z-arrow",
                                        v_model=("slice_z_range", [0, 1]),
                                        min=("slice_extents[axis_names[2]][0]",),
                                        max=("slice_extents[axis_names[2]][1]",),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                    v3.VSlider(
                                        v_else=True,
                                        prepend_icon="mdi-axis-z-arrow",
                                        v_model=("slice_z_cut", 0),
                                        min=("slice_extents[axis_names[2]][0]",),
                                        max=("slice_extents[axis_names[2]][1]",),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                    v3.VCheckbox(
                                        v_model=("slice_z_type", "range"),
                                        true_value="range",
                                        false_value="cut",
                                        true_icon="mdi-crop",
                                        false_icon="mdi-box-cutter",
                                        hide_details=True,
                                        density="compact",
                                        size="sm",
                                        classes="mx-2",
                                    )
                                v3.VDivider()

                        # Slice steps
                        with v3.VTooltip(text="Level Of Details / Slice stepping"):
                            with html.Template(v_slot_activator="{ props }"):
                                with v3.VRow(
                                    v_bind="props",
                                    no_gutter=True,
                                    classes="align-center my-0 mx-0 border-b-thin",
                                ):
                                    v3.VIcon(
                                        "mdi-stairs",
                                        classes="ml-2 text-medium-emphasis",
                                    )
                                    with v3.VCol(
                                        classes="pa-0", v_if="axis_names?.[0]"
                                    ):
                                        v3.VTextField(
                                            v_model_number=("slice_x_step", 1),
                                            hide_details=True,
                                            density="compact",
                                            flat=True,
                                            variant="solo",
                                            reverse=True,
                                            raw_attrs=['min="1"'],
                                            type="number",
                                        )
                                    with v3.VCol(
                                        classes="pa-0", v_if="axis_names?.[1]"
                                    ):
                                        v3.VTextField(
                                            v_model_number=("slice_y_step", 1),
                                            hide_details=True,
                                            density="compact",
                                            flat=True,
                                            variant="solo",
                                            reverse=True,
                                            raw_attrs=['min="1"'],
                                            type="number",
                                        )
                                    with v3.VCol(
                                        classes="pa-0", v_if="axis_names?.[2]"
                                    ):
                                        v3.VTextField(
                                            v_model_number=("slice_z_step", 1),
                                            hide_details=True,
                                            density="compact",
                                            flat=True,
                                            variant="solo",
                                            reverse=True,
                                            raw_attrs=['min="1"'],
                                            type="number",
                                        )

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
                                    with v3.VCol(
                                        classes="pa-0", v_if="axis_names?.[0]"
                                    ):
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
                                    with v3.VCol(
                                        classes="pa-0", v_if="axis_names?.[1]"
                                    ):
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
                                    with v3.VCol(
                                        classes="pa-0", v_if="axis_names?.[2]"
                                    ):
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

                        # Time slider
                        with v3.VTooltip(
                            v_if="slice_t_max > 0",
                            text=(
                                "`time: ${t_labels[slice_t]} (${slice_t+1}/${slice_t_max+1})`",
                            ),
                        ):
                            with html.Template(v_slot_activator="{ props }"):
                                with html.Div(
                                    classes="d-flex pr-2",
                                    v_bind="props",
                                ):
                                    v3.VSlider(
                                        prepend_icon="mdi-clock-outline",
                                        v_model=("slice_t", 0),
                                        min=0,
                                        max=("slice_t_max", 0),
                                        step=1,
                                        hide_details=True,
                                        density="compact",
                                        flat=True,
                                        variant="solo",
                                    )
                                v3.VDivider()
                        v3.VBtn(
                            "Update 3D view",
                            block=True,
                            classes="text-none",
                            flat=True,
                            density="compact",
                            rounded=0,
                            disabled=("data_arrays.length === 0",),
                            color=(
                                "dirty_data && data_arrays.length ? 'primary': undefined",
                            ),
                            click=(self._update_rendering, "[true]"),
                        )

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------
    @change("data_origin_source")
    def _on_data_origin_source(self, data_origin_source, **kwargs):
        if self._import_pending:
            return

        self.state.data_origin_id = ""
        results, *_ = pan3d_catalogs.search(data_origin_source)
        self.state.data_origin_ids = [v["name"] for v in results]
        self.state.data_origin_id_to_desc = {
            v["name"]: v["description"] for v in results
        }

    @change("data_origin_id")
    def _on_data_origin_id(self, data_origin_id, data_origin_source, **kwargs):
        if self._import_pending:
            return

        self.state.load_button_text = "Load"
        self.state.can_load = True

        if data_origin_source == "file":
            self.state.data_origin_id_error = not Path(data_origin_id).exists()
        elif self.state.data_origin_id_error:
            self.state.data_origin_id_error = False

    @change("slice_t", *[var.format(axis) for axis in XYZ for var in SLICE_VARS])
    def _on_slice_change(self, slice_t, **_):
        if self._import_pending:
            return

        slices = {self.source.t: slice_t}
        for axis in XYZ:
            axis_name = getattr(self.source, axis)
            if axis_name is None:
                continue

            if self.state[f"slice_{axis}_type"] == "range":
                slices[axis_name] = [
                    *self.state[f"slice_{axis}_range"],
                    int(self.state[f"slice_{axis}_step"]),
                ]
                slices[axis_name][1] += 1  # end is exclusive
            else:
                slices[axis_name] = self.state[f"slice_{axis}_cut"]

        self.source.slices = slices
        ds = self.source()
        self.state.dataset_bounds = ds.bounds
        self.renderer.ResetCameraClippingRange()
        self.ctrl.view_update()

    @change("data_arrays")
    def _on_array_selection(self, data_arrays, **_):
        if self._import_pending:
            return

        self.state.dirty_data = True
        if len(data_arrays) == 1:
            self.state.color_by = data_arrays[0]
        elif len(data_arrays) == 0:
            self.state.color_by = None

        self.source.arrays = data_arrays

    @change("slice_t")
    def _on_slice_t(self, slice_t, **_):
        if self._import_pending:
            return

        self.source.t_index = slice_t
        self.ctrl.view_update()

    @change("view_3d")
    def _on_view_type_change(self, view_3d, **_):
        # FIXME properly swap interactor style
        if view_3d:
            # self.interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            self.renderer.GetActiveCamera().SetParallelProjection(0)
        else:
            # self.interactor.GetInteractorStyle().SetCu()
            self.renderer.GetActiveCamera().SetParallelProjection(1)

        if not self._import_pending:
            self.ctrl.view_reset_camera()

    @change("color_by")
    def _on_color_by(self, color_by, **__):
        if self.source.input is None:
            return

        ds = self.source()
        if color_by in ds.point_data.keys():
            array = ds.point_data[color_by]
            min_value, max_value = array.GetRange()

            self.state.color_min = min_value
            self.state.color_max = max_value

            self.mapper.SelectColorArray(color_by)
            self.mapper.SetScalarModeToUsePointFieldData()
            self.mapper.InterpolateScalarsBeforeMappingOn()
            self.mapper.SetScalarVisibility(1)
        else:
            self.mapper.SetScalarVisibility(0)
            self.state.color_min = 0
            self.state.color_max = 1

    @change("color_preset", "color_min", "color_max")
    def _on_color_preset(self, color_preset, color_min, color_max, **_):
        color_min = float(color_min)
        color_max = float(color_max)
        self.mapper.SetScalarRange(color_min, color_max)
        apply_preset(self.actor, [color_min, color_max], color_preset)
        self.ctrl.view_update()

    @change("scale_x", "scale_y", "scale_z")
    def _on_scale_change(self, scale_x, scale_y, scale_z, **_):
        self.actor.SetScale(
            to_float(scale_x),
            to_float(scale_y),
            to_float(scale_z),
        )

        if self._import_pending:
            return

        if self.actor.visibility:
            self.ctrl.view_reset_camera()

    # -----------------------------------------------------
    # Triggers
    # -----------------------------------------------------

    def _import_file_upload(self, files):
        self.import_state(json.loads(files[0].get("content")))

    def _process_cli(self, **_):
        args, _ = self.server.cli.parse_known_args()

        # import state
        if args.import_state:
            self._import_file_from_path(args.import_state)

        # load xarray
        elif args.xarray_file:
            self._import_pending = True
            with self.state:
                self._load_dataset("file", args.xarray_file)
                self.state.data_origin_id = str(Path(args.xarray_file).resolve())
            self._import_pending = False

    def _import_file_from_path(self, file_path):
        if file_path is None:
            return

        file_path = Path(file_path)
        if file_path.exists():
            self.import_state(json.loads(file_path.read_text("utf-8")))

    def _load_dataset(self, source, id, config=None):
        self.state.data_origin_source = source
        self.state.data_origin_id = id
        self.state.load_button_text = "Loaded"
        self.state.can_load = False
        self.state.show_data_information = True

        if config is None:
            config = {
                "arrays": [],
                "slices": {},
            }

        try:
            self.source.load(
                {
                    "data_origin": {
                        "source": source,
                        "id": id,
                    },
                    "dataset_config": config,
                }
            )
            self.actor.visibility = 0

            # Extract UI
            self.__update_data_information()
            self.__update_ui_from_source()

            # no error
            self.state.data_origin_error = False
        except Exception as e:
            self.state.data_origin_error = (
                f"Error occurred while trying to load data. {e}"
            )
            self.state.data_origin_id_error = True
            self.state.load_button_text = "Load"
            self.state.can_load = True
            self.state.show_data_information = False

            print(traceback.format_exc())

    def __update_data_information(self):
        xr = self.source.input
        xarray_info = []
        coords = set(xr.coords.keys())
        data = set(self.source.available_arrays)
        for name in xr.variables:
            icon = "mdi-variable"
            order = 3
            length = f'({",".join(xr[name].dims)})'
            if name in coords:
                icon = "mdi-ruler"
                order = 1
                length = xr[name].size
            if name in data:
                icon = "mdi-database"
                order = 2
            xarray_info.append(
                {
                    "order": order,
                    "icon": icon,
                    "name": name,
                    "length": length,
                    "type": str(xr[name].dtype),
                    "attrs": [
                        {"key": "type", "value": str(xr[name].dtype)},
                    ]
                    + [
                        {"key": str(k), "value": str(v)}
                        for k, v in xr[name].attrs.items()
                    ],
                }
            )
        xarray_info.sort(key=lambda item: item["order"])

        # Update UI
        self.state.xarray_info = xarray_info

    def __update_ui_from_source(self):
        """Gather source state information and current application state from it"""
        with self.state:
            self.state.data_arrays_available = self.source.available_arrays
            self.state.data_arrays = self.source.arrays
            self.state.color_by = None
            self.state.axis_names = [self.source.x, self.source.y, self.source.z]
            self.state.slice_extents = self.source.slice_extents
            slices = self.source.slices
            for axis in XYZ:
                # default
                axis_extent = self.state.slice_extents.get(getattr(self.source, axis))
                self.state[f"slice_{axis}_range"] = axis_extent
                self.state[f"slice_{axis}_cut"] = 0
                self.state[f"slice_{axis}_step"] = 1
                self.state[f"slice_{axis}_type"] = "range"

                # use slice info if available
                axis_slice = slices.get(getattr(self.source, axis))
                if axis_slice is not None:
                    if isinstance(axis_slice, int):
                        # cut
                        self.state[f"slice_{axis}_cut"] = axis_slice
                        self.state[f"slice_{axis}_type"] = "cut"
                    else:
                        # range
                        self.state[f"slice_{axis}_range"] = axis_slice[:2]
                        self.state[f"slice_{axis}_step"] = axis_slice[2]

            # Update time
            self.state.slice_t = self.source.t_index
            self.state.slice_t_max = self.source.t_size - 1
            self.state.t_labels = self.source.t_labels

    def _update_rendering(self, reset_camera=False):
        self.state.dirty_data = False
        self.actor.visibility = 1
        self.widget.EnabledOn()
        self.widget.InteractiveOff()
        if reset_camera:
            self.ctrl.view_reset_camera()
        else:
            self.ctrl.view_update()

    def _reset_camera_to_axis(self, axis):
        camera = self.renderer.active_camera
        camera.focal_point = (0, 0, 0)
        camera.position = axis
        camera.view_up = VIEW_UPS.get(tuple(axis))
        self.ctrl.view_reset_camera()

    def _rotate_camera(self, direction):
        camera = self.renderer.active_camera
        a = [*camera.view_up]
        b = [camera.focal_point[i] - camera.position[i] for i in range(3)]
        view_up = [
            direction * (a[1] * b[2] - a[2] * b[1]),
            direction * (a[2] * b[0] - a[0] * b[2]),
            direction * (a[0] * b[1] - a[1] * b[0]),
        ]
        camera.view_up = view_up
        self.ctrl.view_update()

    def _reset_color_range(self):
        color_by = self.state.color_by
        ds = self.source()
        if color_by in ds.point_data.keys():
            array = ds.point_data[color_by]
            min_value, max_value = array.GetRange()

            self.state.color_min = min_value
            self.state.color_max = max_value
        else:
            self.state.color_min = 0
            self.state.color_max = 1

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    @trigger("download_export")
    def export_state(self):
        camera = self.renderer.active_camera
        state_to_export = {
            **self.source.state,
            "preview": {
                "view_3d": self.state.view_3d,
                "color_by": self.state.color_by,
                "color_preset": self.state.color_preset,
                "color_min": self.state.color_min,
                "color_max": self.state.color_max,
                "scale_x": self.state.scale_x,
                "scale_y": self.state.scale_y,
                "scale_z": self.state.scale_z,
            },
            "camera": {
                "position": camera.position,
                "view_up": camera.view_up,
                "focal_point": camera.focal_point,
                "parallel_projection": camera.parallel_projection,
                "parallel_scale": camera.parallel_scale,
            },
        }
        return json.dumps(state_to_export, indent=2)

    def import_state(self, data_state):
        self._import_pending = True
        try:
            data_origin = data_state.get("data_origin")
            source = data_origin.get("source")
            id = data_origin.get("id")
            config = data_state.get("dataset_config")
            preview_state = data_state.get("preview", {})
            camera_state = data_state.get("camera", {})

            # load data and initial rendering setup
            with self.state:
                self._load_dataset(source, id, config)
                self.state.update(preview_state)

            # override computed color range using state values
            with self.state:
                self.state.update(preview_state)

            # update camera and render
            update_camera(self.renderer.active_camera, camera_state)
            self._update_rendering()
        finally:
            self._import_pending = False


# -----------------------------------------------------------------------------
# Main executable
# -----------------------------------------------------------------------------


def main():
    app = XarrayPreview()
    app.server.start()


if __name__ == "__main__":
    main()
