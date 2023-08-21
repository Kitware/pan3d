from trame.widgets import html, vuetify


class MainDrawer:
    def __init__(self):
        with html.Div(classes="pa-2"):
            vuetify.VSelect(
                label="Choose a dataset",
                v_model="dataset_path",
                items=("available_datasets",),
                item_text="name",
                item_value="url",
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-1",
            )

            html.A(
                "More information about this dataset",
                href=("more_info_link",),
                v_show=("more_info_link",),
                target="_blank",
            )

            vuetify.VCardText(
                "Available Arrays",
                v_show="dataset_ready",
                classes="font-weight-bold",
            )
            vuetify.VCardText(
                "No data variables found.",
                v_show=("dataset_ready && data_vars.length === 0",),
            )
            with vuetify.VTreeview(
                v_show="dataset_ready",
                dense=True,
                activatable=True,
                active=("[array_active]",),
                items=("data_vars",),
                item_key="name",
                update_active="""
                            array_active = $event[0];
                            x_array = null;
                            y_array = null;
                            z_array = null;
                            t_array = null;
                            t_index = 0;
                        """,
                multiple_active=False,
            ):
                with vuetify.Template(v_slot_label="{ item }"):
                    html.Span("{{ item?.name }}", classes="text-subtitle-2")

            attrs_headers = [
                {"text": "key", "value": "key"},
                {"text": "value", "value": "value"},
            ]
            vuetify.VCardText(
                "Data Attributes",
                v_show="data_attrs.length",
                classes="font-weight-bold",
            )
            vuetify.VDataTable(
                v_show="data_attrs.length",
                dense=True,
                items=("data_attrs",),
                headers=("headers", attrs_headers),
                hide_default_header=True,
            )
