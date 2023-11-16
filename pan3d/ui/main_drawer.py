from trame.widgets import html
from trame.widgets import vuetify3 as vuetify


class MainDrawer(vuetify.VNavigationDrawer):
    def __init__(
        self,
        dataset_ready="dataset_ready",
        dataset_path="dataset_path",
        da_attrs="da_attrs",
        da_vars="da_vars",
        da_vars_attrs="da_vars_attrs",
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
                hide_details=True,
            )

            with vuetify.VListItem(v_show=(dataset_ready,)):
                with html.Div(
                    classes="d-flex pa-2", style="justify-content: space-between"
                ):
                    html.Span("Attributes")
                    with vuetify.VDialog(max_width=800):
                        with vuetify.Template(v_slot_activator="{ props }"):
                            vuetify.VBtn(
                                icon="mdi-dots-horizontal",
                                size="x-small",
                                variant="plain",
                                v_bind="props",
                            )
                        with vuetify.VCard():
                            vuetify.VCardTitle(
                                "Dataset Attributes",
                                v_show=f"{da_attrs}.length",
                                classes="font-weight-bold",
                            )
                            vuetify.VCardText(
                                "No attributes.", v_show=f"{da_attrs}.length === 0"
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

            html.A(
                "More information about this dataset",
                href=(ui_more_info_link,),
                v_show=(ui_more_info_link,),
                target="_blank",
                classes="mx-3",
            )

            vuetify.VDivider(v_show=(dataset_ready,), classes="my-2")

            vuetify.VCardText(
                "Available Arrays",
                v_show=dataset_ready,
                classes="font-weight-bold",
            )
            vuetify.VCardText(
                "No data variables found.",
                v_show=(f"{dataset_ready} && {da_vars}.length === 0",),
            )
            with vuetify.VListItem(
                v_for=f"array in {da_vars}",
                active=(f"array.name === {da_active}",),
                click=f"{da_active} = array.name",
            ):
                with html.Div(
                    classes="d-flex pa-2", style="justify-content: space-between"
                ):
                    html.Span("{{ array.name }}")
                    with vuetify.VDialog(max_width=800):
                        with vuetify.Template(v_slot_activator="{ props }"):
                            vuetify.VBtn(
                                icon="mdi-dots-horizontal",
                                size="x-small",
                                variant="plain",
                                v_bind="props",
                            )
                        with vuetify.VCard():
                            vuetify.VCardTitle(
                                "Array Attributes",
                                classes="font-weight-bold",
                            )
                            vuetify.VCardText(
                                "No attributes.",
                                v_show=f"{da_vars_attrs}[array.name].length === 0",
                            )
                            with vuetify.VTable(
                                v_show=f"{da_vars_attrs}[array.name].length",
                                density="compact",
                            ):
                                with html.Tbody():
                                    with html.Tr(
                                        v_for=f"data_attr in {da_vars_attrs}[array.name]",
                                    ):
                                        html.Td("{{ data_attr.key }}")
                                        html.Td("{{ data_attr.value }}")
