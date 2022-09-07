from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify, vtk, html


# Create single page layout type
# (FullScreenPage, SinglePage, SinglePageWithDrawer)
def initialize(server):
    state, ctrl = server.state, server.controller
    state.trame__title = "Pan3D Viewer"

    with SinglePageWithDrawerLayout(server) as layout:
        # Toolbar
        layout.title.set_text("Pan3D Viewer")
        with layout.toolbar:
            layout.toolbar.dense = True
            layout.toolbar.align = "center"
            vuetify.VSpacer()
            vuetify.VSelect(
                v_show="view_mode === 'view_grid'",
                v_model=("grid_active_array", "Solid Color"),
                items=(
                    "['Solid Color'].concat(grid_point_data, grid_cell_data).map((v) => v.split('/').pop())",
                ),
                dense=True,
                hide_details=True,
                classes="mx-2",
                style="max-width: 200px",
            )

            with vuetify.VBtn(
                v_show="view_mode === 'view_grid'",
                icon=True,
                click=ctrl.reset_camera,
            ):
                vuetify.VIcon("mdi-crop-free")

            vuetify.VCheckbox(
                v_show="view_mode === 'view_grid'",
                v_model=("view_edge_visiblity", True),
                dense=True,
                hide_details=True,
                on_icon="mdi-border-all",
                off_icon="mdi-border-outside",
                classes="ma-2",
            )

            vuetify.VCheckbox(
                v_model=("view_mode", "edit_grid"),
                dense=True,
                hide_details=True,
                on_icon="mdi-vector-square-edit",
                off_icon="mdi-rotate-3d",
                true_value="edit_grid",
                false_value="view_grid",
                change=ctrl.reset_camera,
                classes="ma-2",
            )

        # Drawer
        with layout.drawer:
            with vuetify.VTreeview(
                dense=True,
                activatable=True,
                items=("array_tree",),
                update_active="array_active = $event?.[0]",
            ):
                with vuetify.Template(v_slot_label="{ item }"):
                    html.Span("{{ item.name }}", classes="text-subtitle-2")
                with vuetify.Template(v_slot_append="{ item }"):
                    vuetify.VSpacer()
                    html.Span(
                        "{{ item.type }} {{ item.dimensions }}",
                        v_if="item.dimensions",
                        classes="text-caption",
                    )

        # Content
        with layout.content:
            with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
                with vtk.VtkRemoteView(
                    ctrl.get_render_window(),
                    v_show="view_mode === 'view_grid'",
                    interactive_ratio=1,
                ) as vtk_view:
                    ctrl.view_update = vtk_view.update
                    ctrl.reset_camera = vtk_view.reset_camera

                with vuetify.VCol(
                    v_show="view_mode === 'edit_grid'", classes="fill-height"
                ):
                    with vuetify.VCard():
                        with vuetify.VCardTitle("Grid", classes="py-1"):
                            vuetify.VSpacer()
                            vuetify.VSelect(
                                v_model=("grid_type", "vtkRectilinearGrid"),
                                items=(
                                    "grid_types",
                                    [
                                        {
                                            "text": "Image data",
                                            "value": "vtkImageData",
                                        },
                                        {
                                            "text": "Rectilinear grid",
                                            "value": "vtkRectilinearGrid",
                                        },
                                        # {
                                        #     "text": "Geometry surface mesh",
                                        #     "value": "vtkPolyData",
                                        # },
                                        # {
                                        #     "text": "Unstructured grid",
                                        #     "value": "vtkUnstructuredGrid",
                                        # },
                                    ],
                                ),
                                dense=True,
                                hide_details=True,
                                style="max-width: 300px;",
                            )
                        vuetify.VDivider()
                        with vuetify.VCardText():
                            with vuetify.VCol(v_if="grid_type == 'vtkImageData'"):
                                with vuetify.VRow():
                                    html.Div(
                                        "Dimensions",
                                        classes="text-subtitle-1 pr-2 pt-1",
                                        style="width: 100px;",
                                    )
                                    vuetify.VTextField(
                                        label="X",
                                        v_model="grid_dimensions[0]",
                                        type="Number",
                                        dense=True,
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_dimensions')",
                                    )
                                    vuetify.VTextField(
                                        label="Y",
                                        v_model="grid_dimensions[1]",
                                        dense=True,
                                        type="Number",
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_dimensions')",
                                    )
                                    vuetify.VTextField(
                                        label="Z",
                                        v_model="grid_dimensions[2]",
                                        dense=True,
                                        type="Number",
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_dimensions')",
                                    )
                                with vuetify.VRow(classes="py-6"):
                                    html.Div(
                                        "Spacing",
                                        classes="text-subtitle-1 pr-2 pt-1",
                                        style="width: 100px;",
                                    )
                                    vuetify.VTextField(
                                        label="X",
                                        v_model="grid_spacing[0]",
                                        type="Number",
                                        dense=True,
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_spacing')",
                                    )
                                    vuetify.VTextField(
                                        label="Y",
                                        v_model="grid_spacing[1]",
                                        dense=True,
                                        type="Number",
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_spacing')",
                                    )
                                    vuetify.VTextField(
                                        label="Z",
                                        v_model="grid_spacing[2]",
                                        dense=True,
                                        type="Number",
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_spacing')",
                                    )
                                with vuetify.VRow():
                                    html.Div(
                                        "Origin",
                                        classes="text-subtitle-1 pr-2 pt-1",
                                        style="width: 100px;",
                                    )
                                    vuetify.VTextField(
                                        label="X",
                                        v_model="grid_origin[0]",
                                        type="Number",
                                        dense=True,
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_origin')",
                                    )
                                    vuetify.VTextField(
                                        label="Y",
                                        v_model="grid_origin[1]",
                                        dense=True,
                                        type="Number",
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_origin')",
                                    )
                                    vuetify.VTextField(
                                        label="Z",
                                        v_model="grid_origin[2]",
                                        dense=True,
                                        type="Number",
                                        hide_details=True,
                                        classes="mx-1 py-0",
                                        change="flushState('grid_origin')",
                                    )
                            with vuetify.VCol(v_if="grid_type == 'vtkRectilinearGrid'"):
                                with vuetify.VRow():
                                    html.Div("X:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_x_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VBtn(
                                        "Use {{ array_info?.name }}",
                                        v_if="array_info?.dimensions?.length === 1",
                                        x_small=True,
                                        classes="mx-1",
                                        click=(ctrl.grid_bind_x, "[array_info?.name]"),
                                    )
                                    vuetify.VBtn(
                                        "Use {{ array_info?.name }} (cell)",
                                        v_if="array_info?.dimensions?.length === 1",
                                        x_small=True,
                                        classes="mx-1",
                                        click=(
                                            ctrl.grid_bind_x,
                                            "[array_info?.name, true]",
                                        ),
                                    )
                                with vuetify.VRow():
                                    html.Div("Y:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_y_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VBtn(
                                        "Use {{ array_info?.name }}",
                                        v_if="array_info?.dimensions?.length === 1",
                                        x_small=True,
                                        classes="mx-1",
                                        click=(ctrl.grid_bind_y, "[array_info?.name]"),
                                    )
                                    vuetify.VBtn(
                                        "Use {{ array_info?.name }} (cell)",
                                        v_if="array_info?.dimensions?.length === 1",
                                        x_small=True,
                                        classes="mx-1",
                                        click=(
                                            ctrl.grid_bind_y,
                                            "[array_info?.name, true]",
                                        ),
                                    )
                                with vuetify.VRow():
                                    html.Div("Z:", classes="text-subtitle-2 pr-2")
                                    html.Div("{{ grid_z_array || 'Undefined' }}")
                                    vuetify.VSpacer()
                                    vuetify.VBtn(
                                        "Use {{ array_info?.name }}",
                                        v_if="array_info?.dimensions?.length === 1",
                                        x_small=True,
                                        classes="mx-1",
                                        click=(ctrl.grid_bind_z, "[array_info?.name]"),
                                    )
                                    vuetify.VBtn(
                                        "Use {{ array_info?.name }} (cell)",
                                        v_if="array_info?.dimensions?.length === 1",
                                        x_small=True,
                                        classes="mx-1",
                                        click=(
                                            ctrl.grid_bind_z,
                                            "[array_info?.name, true]",
                                        ),
                                    )

                    with vuetify.VCard(classes="my-2"):
                        with vuetify.VCardTitle("Point Data", classes="py-1"):
                            vuetify.VSpacer()
                            html.Div(
                                "{{ grid_point_dimensions }}", classes="text-caption"
                            )
                            vuetify.VSpacer()
                            with vuetify.VBtn(
                                icon=True, small=True, click=ctrl.grid_clear_point_data
                            ):
                                vuetify.VIcon("mdi-autorenew")
                        vuetify.VDivider()
                        with vuetify.VCardText():
                            with vuetify.VList(dense=True):
                                with vuetify.VListItem(
                                    v_for="(item, i) in grid_point_data",
                                    key="i",
                                ):
                                    with vuetify.VListItemContent():
                                        vuetify.VListItemTitle("{{ item }}")
                                    with vuetify.VListItemIcon(
                                        click=(ctrl.grid_remove_point_data, "[item]")
                                    ):
                                        vuetify.VIcon(
                                            "mdi-delete-forever-outline", small=True
                                        )
                        with vuetify.VCardActions():
                            vuetify.VBtn(
                                "Add {{ array_info?.name }}",
                                v_if="array_info?.dimensions?.length === 3",
                                x_small=True,
                                block=True,
                                disabled=(
                                    "!array_info.dimensions.every((v, i) => v === grid_point_dimensions[i])",
                                ),
                                click=(ctrl.grid_add_point_data, "[array_info?.name]"),
                            )

                    with vuetify.VCard(classes="my-2"):
                        with vuetify.VCardTitle("Cell Data", classes="py-1"):
                            vuetify.VSpacer()
                            html.Div(
                                "{{ grid_cell_dimensions }}", classes="text-caption"
                            )
                            vuetify.VSpacer()
                            with vuetify.VBtn(
                                icon=True, small=True, click=ctrl.grid_clear_cell_data
                            ):
                                vuetify.VIcon("mdi-autorenew")
                        vuetify.VDivider()
                        with vuetify.VCardText():
                            with vuetify.VList(dense=True):
                                with vuetify.VListItem(
                                    v_for="(item, i) in grid_cell_data",
                                    key="i",
                                ):
                                    with vuetify.VListItemContent():
                                        vuetify.VListItemTitle("{{ item }}")
                                    with vuetify.VListItemIcon(
                                        click=(ctrl.grid_remove_cell_data, "[item]")
                                    ):
                                        vuetify.VIcon(
                                            "mdi-delete-forever-outline", small=True
                                        )
                        with vuetify.VCardActions():
                            vuetify.VBtn(
                                "Add {{ array_info?.name }}",
                                v_if="array_info?.dimensions?.length === 3",
                                block=True,
                                x_small=True,
                                disabled=(
                                    "!array_info.dimensions.every((v, i) => v === grid_cell_dimensions[i])",
                                ),
                                click=(ctrl.grid_add_cell_data, "[array_info?.name]"),
                            )

        # Footer
        # layout.footer.hide()
