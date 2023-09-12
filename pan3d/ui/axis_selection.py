from trame.widgets import html
from trame.widgets import vuetify3 as vuetify
from .coordinate_configure import CoordinateConfigure


class AxisSelection(vuetify.VNavigationDrawer):
    def __init__(
        self,
        coordinate_select_axis_function,
        coordinate_change_slice_function,
        array_active="array_active",
        coordinates="coordinates",
        x_array="x_array",
        y_array="y_array",
        z_array="z_array",
        t_array="t_array",
        t_index="t_index",
        t_max="t_max",
    ):
        super().__init__(
            model_value=(array_active,),
            classes="pa-2",
            width="400",
            location="right",
            permanent=True,
            style="position: absolute",
        )
        axes = [
            {
                "label": "X",
                "name_var": x_array,
                "index_var": "undefined",
                "max_var": "undefined",
            },
            {
                "label": "Y",
                "name_var": y_array,
                "index_var": "undefined",
                "max_var": "undefined",
            },
            {
                "label": "Z",
                "name_var": z_array,
                "index_var": "undefined",
                "max_var": "undefined",
            },
            {
                "label": "T",
                "name_var": t_array,
                "index_var": t_index,
                "max_var": t_max,
            },
        ]
        with self:
            with vuetify.VExpansionPanels(
                model_value=([0, 1],),
                multiple=True,
                accordion=True,
                v_show=coordinates,
            ):
                with vuetify.VExpansionPanel(title="Assigned Coordinates"):
                    with vuetify.VExpansionPanelText():
                        for axis in axes:
                            with vuetify.VSheet(classes="d-flex"):
                                html.Span(axis["label"])
                                CoordinateConfigure(
                                    axes,
                                    coordinates,
                                    "%s.find((c) => c.name === %s)"
                                    % (coordinates, axis["name_var"]),
                                    coordinate_select_axis_function,
                                    coordinate_change_slice_function,
                                    axis_info=axis,
                                )
                                vuetify.VSheet(
                                    v_show=f"!{axis['name_var']}",
                                    rounded=True,
                                    color="grey lighten-2",
                                    style="flex-grow: 1",
                                    height="40",
                                    classes="ml-3 mb-1",
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
                                coordinate_select_axis_function,
                                coordinate_change_slice_function,
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
