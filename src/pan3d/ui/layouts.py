"""Standard layout templates for Pan3D explorers."""

from pan3d.ui.control_panel import ControlPanel
from pan3d.widgets.error_alert import ErrorAlert
from pan3d.widgets.save_dataset_dialog import SaveDatasetDialog
from pan3d.widgets.scalar_bar import ScalarBar
from pan3d.widgets.summary_toolbar import SummaryToolbar
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame.widgets import vuetify3 as v3


class StandardExplorerLayout(VAppLayout):
    """
    Standard layout template for Pan3D explorers.

    This class provides a consistent UI structure for all explorers:
    - 3D view with VTK
    - Scalar bar
    - Save dialog
    - Error alerts
    - Time navigation
    - Control panel with rendering settings
    """

    def __init__(
        self,
        explorer,
        title="Explorer",
    ):
        """
        Create a standard explorer layout.

        Parameters:
            explorer: The explorer instance (must have server, render_window, etc.)
            title: Title for the explorer
            view_class: Class to use for 3D view (default: Pan3DView)
            view_kwargs: Additional kwargs for view class
            rendering_settings_class: Class for rendering settings UI
            rendering_settings_kwargs: Additional kwargs for rendering settings
            additional_content: Function to add additional content (called with layout)
        """
        super().__init__(explorer.server, fill_height=True)

        self.title = title
        self.state.trame__title = self.title

        with self:
            with v3.VMain(style="position: relative"):
                with html.Div(
                    style="position: relative; width: 100%; height: 100%;",
                ) as self.content:
                    # Scalar bar
                    ScalarBar(
                        ctx_name="scalar_bar",
                        v_show="!control_expended",
                        v_if="color_by",
                    )

                    # Save dialog
                    # Expect user to set the save_callback using context obj
                    SaveDatasetDialog(
                        ctx_name="save_dialog",
                        v_model=("show_save_dialog", False),
                        save_path_model=("save_dataset_path", "dataset.nc"),
                        title="Save dataset to disk",
                    )

                    # Error messages
                    ErrorAlert(
                        ctx_name="error_alert",
                        error_key="data_origin_error",
                        title="Error",
                        position="fixed",
                        location="bottom",
                    )

                    # Summary toolbar
                    SummaryToolbar(
                        v_show="!control_expended",
                        v_if="slice_t_max > 0",
                    )

                    # Control panel
                    self._control_panel = ControlPanel(
                        enable_data_selection=(explorer.xarray is None),
                        toggle="control_expended",
                        load_dataset=explorer.load_dataset,
                        import_file_upload=explorer.import_file_upload,
                        export_file_download=explorer.export_state,
                        xr_update_info="xr_update_info",
                        panel_label=self.title,
                    )

    @property
    def control_panel(self):
        return self._control_panel.ui_content
