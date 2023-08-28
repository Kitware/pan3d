from trame.widgets import html
from trame.widgets import vuetify3 as vuetify


class MainDrawer(html.Div):
    def __init__(
        self,
        dataset_ready="dataset_ready",
        dataset_path="dataset_path",
        data_vars="data_vars",
        data_attrs="data_attrs",
        available_datasets="available_datasets",
        more_info_link="more_info_link",
        array_active="array_active",
        x_array="x_array",
        y_array="y_array",
        z_array="z_array",
        t_array="t_array",
        t_index="t_index",
    ):
        super().__init__(classes="pa-2")
        with self:
            vuetify.VSelect(
                label="Choose a dataset",
                v_model=dataset_path,
                items=(available_datasets,),
                item_title="name",
                item_value="url",
                density="compact",
            )

            html.A(
                "More information about this dataset",
                href=(more_info_link,),
                v_show=(more_info_link,),
                target="_blank",
            )

            vuetify.VCardText(
                "Available Arrays",
                v_show=dataset_ready,
                classes="font-weight-bold",
            )
            vuetify.VCardText(
                "No data variables found.",
                v_show=(f"{dataset_ready} && {data_vars}.length === 0",),
            )
            vuetify.VList(
                v_show=dataset_ready,
                items=(f"{data_vars}",),
                item_title="name",
                item_value="name",
                selected=(f"[{array_active}]",),
                update_selected=f"""
                    {array_active} = $event[0];
                    {x_array} = undefined;
                    {y_array} = undefined;
                    {z_array} = undefined;
                    {t_array} = undefined;
                    {t_index} = 0;
                """,
            )
            vuetify.VCardText(
                "Data Attributes",
                v_show=f"{data_attrs}.length",
                classes="font-weight-bold",
            )
            with vuetify.VTable(
                v_show=f"{dataset_ready} && {data_attrs}.length",
                density="compact",
            ):
                with html.Tbody():
                    with html.Tr(
                        v_for=f"data_attr in {data_attrs}",
                    ):
                        html.Td("{{ data_attr.key }}")
                        html.Td("{{ data_attr.value }}")
