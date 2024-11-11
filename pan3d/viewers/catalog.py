import asyncio

from trame.decorators import TrameApp, change
from trame.app import get_server

from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as v3

from pan3d import catalogs as pan3d_catalogs
from pan3d.ui.catalog_search import CatalogSearch


@TrameApp()
class CatalogBrowser:
    def __init__(self, server=None):
        self.server = get_server(server)
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

    def _build_ui(self):
        self.state.trame__title = "XArray Catalog Browser"
        with SinglePageLayout(self.server, full_height=True) as layout:
            self.ui = layout
            with layout.content:
                v3.VBtn("Hello")
                CatalogSearch(
                    update_catalog_search_term_function=self._update_catalog_search_term,
                    catalog_search_function=self._catalog_search,
                    catalog_term_search_function=self._catalog_term_option_search,
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
                self.state.available_datasets[group_name] = results
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
    def _on_change_catalog(self, catalog, **kwargs):
        self.state.catalog_current_search = {}
        self.state.ui_catalog_search_message = None


# -----------------------------------------------------------------------------
# Main executable
# -----------------------------------------------------------------------------


def main():
    app = CatalogBrowser()
    app.start()


if __name__ == "__main__":
    main()
