from trame.widgets import html, vuetify


class AxisSelection(vuetify.VNavigationDrawer):
    def __init__(
        self,
        array_active="array_active",
        coordinates="coordinates",
        x_array="x_array",
        x_scale="x_scale",
        y_array="y_array",
        y_scale="y_scale",
        z_array="z_array",
        z_scale="z_scale",
        t_array="t_array",
        t_index="t_index",
        t_max="t_max",
    ):
        super().__init__(
            value=(array_active,),
            classes="pa-2",
            width="300",
            right=True,
            style="position: absolute; top: 50px",
        )
        with self:
            # TODO: redesign this drawer
            with vuetify.VCol():
                with vuetify.VRow():
                    html.Div("X:", classes="text-subtitle-2 pr-2")
                    vuetify.VSelect(
                        v_model=(x_array, None),
                        items=(coordinates,),
                        hide_details=True,
                        dense=True,
                        clearable="True",
                        clear=f"{x_array} = undefined",
                        style="max-width: 250px;",
                    )
                    vuetify.VSlider(
                        v_show=x_array,
                        v_model=(x_scale, 0),
                        classes="ml-2",
                        label="Scale",
                        thumb_label=True,
                        min=1,
                        max=10,
                        dense=True,
                        hide_details=True,
                        style="max-width: 250px;",
                    )

                with vuetify.VRow():
                    html.Div("Y:", classes="text-subtitle-2 pr-2")
                    vuetify.VSelect(
                        v_model=(y_array, None),
                        items=(coordinates,),
                        hide_details=True,
                        dense=True,
                        clearable="True",
                        clear=f"{y_array} = undefined",
                        style="max-width: 250px;",
                    )
                    vuetify.VSlider(
                        v_show=y_array,
                        v_model=(y_scale, 0),
                        classes="ml-2",
                        label="Scale",
                        thumb_label=True,
                        min=1,
                        max=10,
                        dense=True,
                        hide_details=True,
                        style="max-width: 250px;",
                    )

                with vuetify.VRow():
                    html.Div("Z:", classes="text-subtitle-2 pr-2")
                    vuetify.VSelect(
                        v_model=(z_array, None),
                        items=(coordinates,),
                        hide_details=True,
                        dense=True,
                        clearable="True",
                        clear=f"{z_array} = undefined",
                        style="max-width: 250px;",
                    )
                    vuetify.VSlider(
                        v_show=z_array,
                        v_model=(z_scale, 0),
                        classes="ml-2",
                        label="Scale",
                        thumb_label=True,
                        min=1,
                        max=10,
                        dense=True,
                        hide_details=True,
                        style="max-width: 250px;",
                    )

                with vuetify.VRow():
                    html.Div("T:", classes="text-subtitle-2 pr-2")
                    vuetify.VSelect(
                        v_model=(t_array, None),
                        items=(coordinates,),
                        hide_details=True,
                        dense=True,
                        clearable="True",
                        clear=f"{t_array} = undefined",
                        style="max-width: 250px;",
                    )
                    vuetify.VSlider(
                        v_show=f"{t_array} && {t_max} > 0",
                        v_model=(t_index, 0),
                        classes="ml-2",
                        label="Index",
                        thumb_label=True,
                        min=0,
                        max=(t_max, 0),
                        step=1,
                        dense=True,
                        hide_details=True,
                        style="max-width: 250px;",
                    )
