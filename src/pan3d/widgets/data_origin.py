"""Data Origin widget for selecting and loading data from various sources."""

from pan3d import catalogs as pan3d_catalogs
from pan3d.ui.collapsible import CollapsableSection
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class DataOrigin(CollapsableSection):
    """
    Data origin selection widget that matches the original behavior.

    Extends CollapsableSection to provide a collapsible panel for data source selection.

    Note: This widget uses fixed state variable names (data_origin_source, data_origin_id, etc.)
    instead of the namespace pattern because these variables are accessed across multiple
    components in the application.
    """

    def __init__(self, load_dataset):
        """
        Initialize the DataOrigin widget.

        Args:
            load_dataset: Callback function to load the dataset
        """
        super().__init__("Data origin", "show_data_origin", True)

        self.state.load_button_text = "Load"
        self.state.can_load = True
        self.state.data_origin_id_to_desc = {}

        with self.content:
            v3.VSelect(
                label="Source",
                v_model=("data_origin_source", "xarray"),
                items=(
                    "data_origin_sources",
                    pan3d_catalogs.list_availables(),
                ),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
            )
            v3.VDivider()
            v3.VTextField(
                placeholder="Location",
                v_if="['file', 'url'].includes(data_origin_source)",
                v_model=("data_origin_id", ""),
                hide_details=True,
                density="compact",
                flat=True,
                variant="solo",
                append_inner_icon=(
                    "data_origin_id_error ? 'mdi-file-document-alert-outline' : undefined",
                ),
                error=("data_origin_id_error", False),
            )

            with v3.VTooltip(
                v_else=True,
                text=("`${ data_origin_id_to_desc[data_origin_id] }`",),
            ):
                with html.Template(v_slot_activator="{ props }"):
                    v3.VSelect(
                        v_bind="props",
                        label="Name",
                        v_model="data_origin_id",
                        items=("data_origin_ids", []),
                        hide_details=True,
                        density="compact",
                        flat=True,
                        variant="solo",
                    )
            v3.VDivider()
            v3.VBtn(
                "{{ load_button_text }}",
                block=True,
                classes="text-none",
                flat=True,
                density="compact",
                rounded=0,
                disabled=("!data_origin_id?.length || !can_load",),
                color=("can_load ? 'primary': undefined",),
                click=(
                    load_dataset,
                    "[data_origin_source, data_origin_id, data_origin_order]",
                ),
            )
