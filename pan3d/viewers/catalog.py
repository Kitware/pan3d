import json
import asyncio
from pathlib import Path

from trame.decorators import TrameApp, change
from trame.app import get_server

from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.widgets import vuetify3 as v3, html
from trame_client.widgets.core import TrameDefault

from pan3d import catalogs as pan3d_catalogs
from pan3d.ui.catalog_search import CatalogSearch
from pan3d.xarray.algorithm import vtkXArrayRectilinearSource


@TrameApp()
class CatalogBrowser:
    def __init__(self, server=None):
        self.server = get_server(server)
        self.current_event_loop = asyncio.get_event_loop()

        # dev setup
        if self.server.hot_reload:
            self.ctrl.on_server_reload.add(self._build_ui)

        # Xarray helper
        self.reader = vtkXArrayRectilinearSource()

        # List options
        self.state.update(
            {
                "xr_meta": {},
                "xr_vars": [],
                "available_datasets": [],
                "available_data_groups": [],
            }
        )
        self.state.available_catalogs = pan3d_catalogs.list_availables_search()

        # self.state.available_datasets = [
        #     {
        #         "id": "MITgcm_channel_flatbottom_02km_run01_phys-mon",
        #         "subtitle": "MITgcm channel simulations with flat bottom at 2km resolution physics field monthly mean climatology\n",
        #         "value": {
        #             "source": "pangeo",
        #             "id": "MITgcm_channel_flatbottom_02km_run01_phys-mon",
        #         },
        #     },
        # ]

        # Build UI
        self.ui = None
        self._build_ui()

    # -------------------------------------------------------------------------
    # Trame API
    # -------------------------------------------------------------------------

    def start(self, **kwargs):
        """Initialize the UI and start the server for GeoTrame."""
        self.ui.server.start(**kwargs)

    @property
    async def ready(self):
        """Coroutine to wait for the GeoTrame server to be ready."""
        await self.ui.ready

    @property
    def state(self):
        """Returns the current State of the Trame server."""
        return self.server.state

    @property
    def ctrl(self):
        """Returns the Controller for the Trame server."""
        return self.server.controller

    # -------------------------------------------------------------------------
    # GUI
    # -------------------------------------------------------------------------

    def _build_ui(self, *args, **kwargs):
        self.state.trame__title = "XArray Catalog Browser"
        with SinglePageWithDrawerLayout(self.server, full_height=True) as layout:
            self.ui = layout

            with layout.toolbar as tb:
                tb.density = "compact"
                layout.title.set_text("XArray Catalog Browser")
                v3.VSpacer()
                v3.VBtn(
                    icon="mdi-search-web",
                    click="ui_search_catalogs = !ui_search_catalogs",
                )
                v3.VProgressLinear(
                    indeterminate=("trame__busy",),
                    absolute=True,
                    location="bottom",
                    color="primary",
                    bg_color="rgba(0,0,0,0)",
                    opacity=0.2,
                    height=3,
                )

            CatalogSearch(
                update_catalog_search_term_function=self._update_catalog_search_term,
                catalog_search_function=self._catalog_search,
                catalog_term_search_function=self._catalog_term_option_search,
            )

            with layout.drawer as drawer:
                drawer.width = 350
                with v3.VToolbar(
                    density="compact",
                    flat=True,
                    color="white",
                    classes="pa-1 border-b-thin",
                ):
                    v3.VTextField(
                        placeholder="filter...",
                        v_model=("filter_query", ""),
                        density="compact",
                        hide_details=True,
                        prepend_inner_icon="mdi-magnify",
                        variant="outlined",
                        rounded=True,
                        clearable=True,
                    )
                    v3.VBtn(
                        icon="mdi-trash-can-outline",
                        flat=True,
                        density="compact",
                        classes="mx-1",
                        click="selected_dataset=[];available_datasets=[];",
                    )

                v3.VList(
                    mandatory=True,
                    selectable=True,
                    density="compact",
                    items=(
                        "available_datasets.filter((v) => !filter_query || (filter_query.length === 0) || v.subtitle.toLowerCase().includes(filter_query.toLowerCase()) || v.id.toLowerCase().includes(filter_query.toLowerCase()))",
                        TrameDefault(
                            available_datasets=[],
                            selected_dataset=[],
                        ),
                    ),
                    item_props=True,
                    item_value="value",
                    lines="three",
                    raw_attrs=['v-model:selected="selected_dataset"'],
                )

            with layout.content:
                with v3.VContainer(fluid=True, classes="full-height pa-0"):
                    with v3.VCard(flat=True, tile=True, v_if="selected_dataset.length"):
                        with v3.VCardTitle(
                            "{{ selected_dataset[0]?.id}}",
                            classes="d-flex",
                        ):
                            v3.VSpacer()
                            v3.VLabel("({{ selected_dataset[0]?.source }})")
                            v3.VBtn(
                                icon="mdi-cloud-download-outline",
                                density="compact",
                                click=self.save_data_origin,
                                flat=True,
                                classes="ml-2",
                            )
                            v3.VBtn(
                                icon="mdi-file-download-outline",
                                density="compact",
                                click=self.save_dataset,
                                flat=True,
                                classes="ml-2",
                            )
                        v3.VDivider()
                        v3.VSelect(
                            label="Coordinates",
                            v_model=("xr_coord", None),
                            items=("xr_coords", []),
                            density="compact",
                            hide_details=True,
                            flat=True,
                            variant="outlined",
                            classes="ma-2",
                        )

                        with v3.VTable(density="compact"):
                            with html.Tbody():
                                with html.Tr(
                                    v_for="attr, j in xr_meta[xr_coord] || []",
                                    key="j",
                                ):
                                    html.Td("{{ attr.key }}")
                                    html.Td("{{ attr.value }}")

                        v3.VSelect(
                            label="Data arrays",
                            v_model=("xr_array", None),
                            items=("xr_arrays", []),
                            density="compact",
                            hide_details=True,
                            flat=True,
                            variant="outlined",
                            classes="ma-2",
                        )

                        with v3.VTable(density="compact"):
                            with html.Tbody():
                                with html.Tr(
                                    v_for="attr, j in xr_meta[xr_array] || []",
                                    key="j",
                                ):
                                    html.Td("{{ attr.key }}")
                                    html.Td("{{ attr.value }}")
                        v3.VSelect(
                            v_if="xr_vars.length",
                            label="Variables",
                            v_model=("xr_var", None),
                            items=("xr_vars", []),
                            density="compact",
                            hide_details=True,
                            flat=True,
                            variant="outlined",
                            classes="ma-2",
                        )

                        with v3.VTable(density="compact", v_if="xr_vars.length"):
                            with html.Tbody():
                                with html.Tr(
                                    v_for="attr, j in xr_meta[xr_var] || []",
                                    key="j",
                                ):
                                    html.Td("{{ attr.key }}")
                                    html.Td("{{ attr.value }}")
                    v3.VCardText(
                        "Search dataset from the catalogs and select one from the list on the left to explore its content.",
                        v_else=True,
                    )

    # -------------------------------------------------------------------------
    # Triggers
    # -------------------------------------------------------------------------

    def _update_catalog_search_term(self, term_key, term_value):
        self.state.catalog_current_search[term_key] = term_value
        self.state.dirty("catalog_current_search")

    def _catalog_search(self):
        def load_results():
            catalog_id = self.state.catalog.get("id")
            results, group_name, message = pan3d_catalogs.search(
                catalog_id, **self.state.catalog_current_search
            )

            if len(results) > 0:
                self.state.available_data_groups.append(
                    {"name": group_name, "value": group_name}
                )
                self.state.available_datasets.extend(results)
                self.state.ui_catalog_search_message = message
                self.state.dirty("available_data_groups", "available_datasets")
            else:
                self.state.ui_catalog_search_message = (
                    "No results found for current search criteria."
                )

        self.run_as_async(
            load_results,
            loading_state="ui_catalog_term_search_loading",
            error_state="ui_catalog_search_message",
            unapplied_changes_state=None,
        )

    def _catalog_term_option_search(self):
        def load_terms():
            catalog_id = self.state.catalog.get("id")
            search_options = pan3d_catalogs.get_search_options(catalog_id)
            self.state.available_catalogs = [
                (
                    {
                        **catalog,
                        "search_terms": [
                            {"key": k, "options": v} for k, v in search_options.items()
                        ],
                    }
                    if catalog.get("id") == catalog_id
                    else catalog
                )
                for catalog in self.state.available_catalogs
            ]
            for catalog in self.state.available_catalogs:
                if catalog.get("id") == catalog_id:
                    self.state.catalog = catalog

        self.run_as_async(
            load_terms,
            loading_state="ui_catalog_term_search_loading",
            error_state="ui_catalog_search_message",
            unapplied_changes_state=None,
        )

    def run_as_async(
        self,
        function,
        loading_state="ui_loading",
        error_state="ui_error_message",
        unapplied_changes_state="ui_unapplied_changes",
    ):
        async def run():
            with self.state:
                if loading_state is not None:
                    self.state[loading_state] = True
                if error_state is not None:
                    self.state[error_state] = None
                if unapplied_changes_state is not None:
                    self.state[unapplied_changes_state] = False

            await asyncio.sleep(0.001)

            with self.state:
                try:
                    function()
                except Exception as e:
                    if error_state is not None:
                        self.state[error_state] = str(e)
                    else:
                        raise e
                if loading_state is not None:
                    self.state[loading_state] = False

            await asyncio.sleep(0.001)

        if self.current_event_loop.is_running():
            asyncio.run_coroutine_threadsafe(run(), self.current_event_loop)
        else:
            # Pytest environment needs synchronous execution
            function()

    def save_data_origin(self):
        selected_dataset = self.state.selected_dataset
        if not selected_dataset:
            return

        file = Path(f"{selected_dataset[0].get('id')}.data-origin.json")
        file.write_text(json.dumps(dict(data_origin=selected_dataset[0])))

    def save_dataset(self):
        selected_dataset = self.state.selected_dataset
        if not selected_dataset:
            return

        name = f"{selected_dataset[0].get('id')}.nc"

        self.reader.input.to_netcdf(name)

    # -----------------------------------------------------
    # State change callbacks
    # -----------------------------------------------------

    @change("ui_search_catalogs")
    def _on_change_ui_search_catalogs(self, ui_search_catalogs, **kwargs):
        if ui_search_catalogs:
            self.state.catalog = self.state.available_catalogs[0]
        else:
            self.state.catalog = None

    @change("catalog")
    def _on_change_catalog(self, **_):
        self.state.catalog_current_search = {}
        self.state.ui_catalog_search_message = None

    @change("selected_dataset")
    def on_selection_change(self, selected_dataset, **_):
        if not selected_dataset:
            self.state.xarray_info = []
            return

        # Load metadata
        self.reader.load(dict(data_origin=selected_dataset[0]))
        xr = self.reader.input
        available_arrays = self.reader.available_arrays

        # Extract metadata
        xr_meta = {}
        xr_coords = []
        xr_arrays = []
        xr_vars = []

        coords = set(xr.coords.keys())
        data = set(available_arrays or [])
        for name in xr.variables:
            attrs = xr_meta.setdefault(name, [])
            attrs.extend(
                [{"key": str(k), "value": str(v)} for k, v in xr[name].attrs.items()]
            )
            attrs.insert(
                0,
                {"key": "type", "value": str(xr[name].dtype)},
            )
            attrs.insert(
                0,
                {
                    "key": "shape",
                    "value": list(xr[name].shape),
                },
            )
            if name in coords:
                xr_coords.append(name)
                length = xr[name].size
                shape = xr[name].shape
                if length > 1 and len(shape) == 1:
                    attrs.insert(
                        0,
                        {
                            "key": "range",
                            "value": f"[{xr[name].values[0]}, {xr[name].values[-1]}]",
                        },
                    )

            elif name in data:
                attrs.insert(
                    0,
                    {
                        "key": "dimensions",
                        "value": f'({",".join(xr[name].dims)})',
                    },
                )
                xr_arrays.append(name)
            else:
                xr_vars.append(name)

        # Update UI
        self.state.xr_meta = xr_meta
        self.state.xr_coords = xr_coords
        self.state.xr_arrays = xr_arrays
        self.state.xr_vars = xr_vars
        self.state.xr_coord = xr_coords[0] if len(xr_coords) else ""
        self.state.xr_array = xr_arrays[0] if len(xr_arrays) else ""
        self.state.xr_var = xr_vars[0] if len(xr_vars) else ""


# -----------------------------------------------------------------------------
# Main executable
# -----------------------------------------------------------------------------


def main():
    app = CatalogBrowser()
    app.start()


if __name__ == "__main__":
    main()
