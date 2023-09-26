from trame.widgets import html
from trame.widgets import vuetify3 as vuetify
from .coordinate_configure import CoordinateConfigure


class AxisSelection(vuetify.VNavigationDrawer):
    def __init__(
        self,
        coordinate_select_axis_function,
        coordinate_change_slice_function,
        coordinate_toggle_expansion_function,
        active_array="active_array",
        coordinates="coordinates",
        expanded_coordinates="expanded_coordinates",
        x_array="x_array",
        y_array="y_array",
        z_array="z_array",
        t_array="t_array",
        t_index="t_index",
        t_max="t_max",
    ):
        super().__init__(
            model_value=(active_array,),
            classes="pa-2",
            width="350",
            location="right",
            permanent=True,
            style="position: absolute",
        )
        axes = [
            {
                "label": "X",
                "name_var": x_array,
                "index_var": "undefined",
            },
            {
                "label": "Y",
                "name_var": y_array,
                "index_var": "undefined",
            },
            {
                "label": "Z",
                "name_var": z_array,
                "index_var": "undefined",
            },
            {
                "label": "T",
                "name_var": t_array,
                "index_var": t_index,
            },
        ]
        with self:
            with vuetify.VExpansionPanels(
                model_value=([0, 1],),
                multiple=True,
                accordion=True,
                v_if=coordinates,
            ):
                with vuetify.VExpansionPanel(title="Assigned Coordinates"):
                    with vuetify.VExpansionPanelText():
                        for axis in axes:
                            with vuetify.VSheet(classes="d-flex"):
                                html.Span(axis["label"], classes="pt-2")
                                with html.Div(
                                    v_show=f"{axis['name_var']}", style="width: 100%"
                                ):
                                    CoordinateConfigure(
                                        axes,
                                        coordinates,
                                        "%s.find((c) => c.name === %s)"
                                        % (coordinates, axis["name_var"]),
                                        expanded_coordinates,
                                        coordinate_select_axis_function,
                                        coordinate_change_slice_function,
                                        coordinate_toggle_expansion_function,
                                        axis_info=axis,
                                    )
                                with vuetify.VCard(
                                    v_show=f"!{axis['name_var']}",
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
                            v_for="coord in coordinates",
                            v_show="![%s, %s, %s, %s].includes(coord.name)"
                            % (x_array, y_array, z_array, t_array),
                        ):
                            CoordinateConfigure(
                                axes,
                                coordinates,
                                "coord",
                                expanded_coordinates,
                                coordinate_select_axis_function,
                                coordinate_change_slice_function,
                                coordinate_toggle_expansion_function,
                            )
                        html.Span(
                            "No coordinates remain.",
                            v_show="""
                                coordinates.every(
                                    (c) => [%s, %s, %s, %s].includes(c.name)
                                )
                            """
                            % (x_array, y_array, z_array, t_array),
                            classes="mx-5",
                        )
