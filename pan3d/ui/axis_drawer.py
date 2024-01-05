from trame.widgets import html
from trame.widgets import vuetify3 as vuetify
from .coordinate_configure import CoordinateConfigure


class AxisDrawer(vuetify.VNavigationDrawer):
    def __init__(
        self,
        coordinate_select_axis_function,
        coordinate_change_slice_function,
        coordinate_toggle_expansion_function,
        ui_axis_drawer="ui_axis_drawer",
        ui_expanded_coordinates="ui_expanded_coordinates",
        ui_current_time_string="ui_current_time_string",
        da_active="da_active",
        da_coordinates="da_coordinates",
        da_x="da_x",
        da_y="da_y",
        da_z="da_z",
        da_t="da_t",
        da_t_index="da_t_index",
    ):
        super().__init__(
            v_model=(ui_axis_drawer,),
            classes="pa-2",
            width="350",
            location="right",
            permanent=True,
            style="position: absolute",
        )
        axes = [
            {
                "label": "X",
                "name_var": da_x,
                "index_var": "undefined",
            },
            {
                "label": "Y",
                "name_var": da_y,
                "index_var": "undefined",
            },
            {
                "label": "Z",
                "name_var": da_z,
                "index_var": "undefined",
            },
            {
                "label": "T",
                "name_var": da_t,
                "index_var": da_t_index,
            },
        ]
        with self:
            with vuetify.VExpansionPanels(
                model_value=("[0, 1]",),
                multiple=True,
                accordion=True,
                v_if=(da_coordinates,),
            ):
                with vuetify.VExpansionPanel(title="Assigned Coordinates"):
                    with vuetify.VExpansionPanelText():
                        for axis in axes:
                            with vuetify.VSheet(classes="d-flex"):
                                html.Span(axis["label"], classes="pt-2")
                                with html.Div(
                                    v_show=(f"{axis['name_var']}",), style="width: 100%"
                                ):
                                    CoordinateConfigure(
                                        axes,
                                        da_coordinates,
                                        f"{da_coordinates}.find((c) => c.name === {axis['name_var']})",
                                        ui_expanded_coordinates,
                                        ui_current_time_string,
                                        coordinate_select_axis_function,
                                        coordinate_change_slice_function,
                                        coordinate_toggle_expansion_function,
                                        axis_info=axis,
                                    )
                                with vuetify.VCard(
                                    v_show=(f"!{axis['name_var']}",),
                                    height="45",
                                    classes="ml-3 mb-1",
                                    style="flex-grow: 1",
                                ):
                                    vuetify.VCardSubtitle(
                                        f"No coordinate assigned to {axis['label']}",
                                        classes="text-center pt-3",
                                    )

                with vuetify.VExpansionPanel(title="Available Coordinates"):
                    with vuetify.VExpansionPanelText():
                        with html.Div(
                            v_for=("coord in da_coordinates",),
                            v_show=(
                                f"![{da_x}, {da_y}, {da_z}, {da_t}].includes(coord.name)",
                            ),
                        ):
                            CoordinateConfigure(
                                axes,
                                da_coordinates,
                                "coord",
                                ui_expanded_coordinates,
                                ui_current_time_string,
                                coordinate_select_axis_function,
                                coordinate_change_slice_function,
                                coordinate_toggle_expansion_function,
                            )
                        html.Span(
                            "No coordinates remain.",
                            v_show=(
                                f"""
                                da_coordinates.every(
                                    (c) => [{da_x}, {da_y}, {da_z}, {da_t}].includes(c.name)
                                )
                            """,
                            ),
                            classes="mx-5",
                        )
