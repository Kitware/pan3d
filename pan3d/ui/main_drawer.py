from trame.widgets import html
from trame.widgets import vuetify3 as vuetify


class MainDrawer(vuetify.VNavigationDrawer):
    def __init__(
        self,
        dataset_ready="dataset_ready",
        dataset_path="dataset_path",
        da_vars="da_vars",
        da_attrs="da_attrs",
        available_datasets="available_datasets",
        ui_main_drawer="ui_main_drawer",
        ui_more_info_link="ui_more_info_link",
        da_active="da_active",
        da_x="da_x",
        da_y="da_y",
        da_z="da_z",
        da_t="da_t",
        da_t_index="da_t_index",
    ):
        super().__init__(
            v_model=ui_main_drawer, classes="pa-2", permanent=True, width=300
        )
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
                href=(ui_more_info_link,),
                v_show=(ui_more_info_link,),
                target="_blank",
            )

            vuetify.VCardText(
                "Available Arrays",
                v_show=dataset_ready,
                classes="font-weight-bold",
            )
            vuetify.VCardText(
                "No data variables found.",
                v_show=(f"{dataset_ready} && {da_vars}.length === 0",),
            )
            vuetify.VList(
                v_show=dataset_ready,
                items=(f"{da_vars}",),
                item_title="name",
                item_value="name",
                selected=(f"[{da_active}]",),
                update_selected=f"""
                    {da_active} = $event[0];
                    {da_x} = undefined;
                    {da_y} = undefined;
                    {da_z} = undefined;
                    {da_t} = undefined;
                    {da_t_index} = 0;
                """,
            )
            vuetify.VCardText(
                "Data Attributes",
                v_show=f"{da_attrs}.length",
                classes="font-weight-bold",
            )
            with vuetify.VTable(
                v_show=f"{dataset_ready} && {da_attrs}.length",
                density="compact",
            ):
                with html.Tbody():
                    with html.Tr(
                        v_for=f"data_attr in {da_attrs}",
                    ):
                        html.Td("{{ data_attr.key }}")
                        html.Td("{{ data_attr.value }}")
