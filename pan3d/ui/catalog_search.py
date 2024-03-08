from trame.widgets import html
from trame.widgets import vuetify3 as vuetify


class CatalogSearch(vuetify.VDialog):
    def __init__(
        self,
        update_catalog_search_term_function,
        catalog_search_function,
        catalog_term_search_function,
        catalog="catalog",
        available_catalogs="available_catalogs",
        ui_search_catalogs="ui_search_catalogs",
        catalog_current_search="catalog_current_search",
        ui_catalog_term_search_loading="ui_catalog_term_search_loading",
        ui_catalog_search_message="ui_catalog_search_message",
    ):
        super().__init__(v_model=(ui_search_catalogs,), max_width=800)
        with self:
            with vuetify.Template(v_slot_activator=("{ props }",)):
                vuetify.VBtn(
                    "Search Catalogs",
                    click=f"{ui_search_catalogs} = true",
                    size="small",
                    block=True,
                    classes="my-2",
                )
            with vuetify.VCard():
                with vuetify.VCardText():
                    vuetify.VBtn(
                        flat=True,
                        icon="mdi-close",
                        style="float: right",
                        click=f"{ui_search_catalogs} = false",
                    )
                    vuetify.VCardTitle("Search a catalog")

                    vuetify.VSelect(
                        label="Choose a catalog",
                        v_show=(f"{available_catalogs}.length > 1",),
                        items=(available_catalogs, []),
                        v_model=(catalog,),
                        item_title="name",
                        density="compact",
                        return_object=True,
                        hide_details=True,
                    )

                    vuetify.VCardSubtitle(
                        "Select or enter search terms",
                        classes="mt-5",
                        style="display: inline-block",
                    )
                    with vuetify.VTooltip(
                        location="bottom",
                        text="For each search term, you may specify one or more acceptable values.",
                    ):
                        with vuetify.Template(v_slot_activator=("{ props }",)):
                            vuetify.VIcon(
                                v_bind="props",
                                icon="mdi-information-outline",
                                style="vertical-align: baseline",
                            )

                    with vuetify.VBtn(
                        size="small",
                        classes="mt-3",
                        style="float: right",
                        loading=(ui_catalog_term_search_loading,),
                        disabled=(ui_catalog_term_search_loading,),
                        click=catalog_term_search_function,
                    ):
                        html.Span("Search for term options")
                        vuetify.VTooltip(
                            activator="parent",
                            location="bottom",
                            text="""
                                Perform an unfiltered search on the catalog
                                to find all unique values for all searchable terms.
                                The results will appear as selectable options in
                                the value input dropdowns.
                                """,
                        )

                    with vuetify.VTable(v_if=(catalog,), style="max-height: 500px"):
                        with html.Tbody():
                            with html.Tr(
                                v_for=(f"term in {catalog}.search_terms",),
                            ):
                                html.Td("{{ term.key }}", style="width: 100px")
                                with html.Td():
                                    vuetify.VCombobox(
                                        label="Enter value",
                                        items=("term.options", []),
                                        multiple=True,
                                        chips=True,
                                        closable_chips=True,
                                        clearable=True,
                                        model_value=(
                                            f"{catalog_current_search}[term.key]",
                                            [],
                                        ),
                                        update_modelValue=(
                                            update_catalog_search_term_function,
                                            "[term.key, $event]",
                                        ),
                                    )

                    with vuetify.VBtn(
                        color="primary",
                        style="float: right",
                        loading=(ui_catalog_term_search_loading,),
                        disabled=(ui_catalog_term_search_loading,),
                        click=catalog_search_function,
                    ):
                        html.Span("Search")
                        vuetify.VTooltip(
                            activator="parent",
                            location="bottom",
                            text="""
                                Perform a filtered search with the union of all selected terms.
                                The results will be grouped and added to the list of available datasets.
                                """,
                        )

                    html.Span(
                        "{{ %s }}" % ui_catalog_search_message,
                        v_show=ui_catalog_search_message,
                    )
