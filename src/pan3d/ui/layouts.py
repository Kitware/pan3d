"""Standard layout templates for Pan3D explorers."""

from pan3d.ui.vtk_view import Pan3DView
from pan3d.utils.common import ControlPanel
from pan3d.widgets.error_alert import ErrorAlert
from pan3d.widgets.save_dataset_dialog import SaveDatasetDialog
from pan3d.widgets.scalar_bar import ScalarBar
from pan3d.widgets.time_navigation import TimeNavigation
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import vuetify3 as v3


class StandardExplorerLayout:
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
        view_class=Pan3DView,
        view_kwargs=None,
        rendering_settings_class=None,
        rendering_settings_kwargs=None,
        additional_content=None,
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
        self.explorer = explorer
        self.title = title
        self.view_class = view_class
        self.view_kwargs = view_kwargs or {}
        self.rendering_settings_class = rendering_settings_class
        self.rendering_settings_kwargs = rendering_settings_kwargs or {}
        self.additional_content = additional_content

    def build(self):
        """Build and return the standard layout."""
        explorer = self.explorer
        explorer.state.trame__title = self.title

        with VAppLayout(explorer.server, fill_height=True) as layout:
            explorer.ui = layout

            # 3D view
            self.view_class(
                explorer.render_window,
                local_rendering=explorer.local_rendering,
                widgets=[explorer.widget] if hasattr(explorer, "widget") else [],
                **self.view_kwargs,
            )

            # Scalar bar
            ScalarBar(
                ctx_name="scalar_bar",
                v_show="!control_expended",
                v_if="color_by",
            )

            # Save dialog
            explorer.save_dialog = SaveDatasetDialog(
                save_callback=explorer._handle_save_dataset_base,
                v_model=("show_save_dialog", False),
                save_path_model=("save_dataset_path", "dataset.nc"),
                title="Save dataset to disk",
            )

            # Error messages
            explorer.error_alert = ErrorAlert(
                error_key="data_origin_error",
                title="Error",
                position="fixed",
                location="bottom",
            )

            # Time navigation toolbar
            with v3.VCard(
                v_show="!control_expended",
                v_if="slice_t_max > 0",
                classes="time-navigation-toolbar",
                rounded="pill",
                style=(
                    "position: absolute; bottom: 1rem; left: 50%; "
                    "transform: translateX(-50%);"
                ),
            ):
                explorer.time_nav_widget = TimeNavigation(
                    index_name="slice_t",
                    labels_name="t_labels",
                    labels=[],
                    ctx_name="time_nav",
                )

            # Additional content (e.g., slice controls, analytics drawer)
            if self.additional_content:
                self.additional_content(layout)

            # Control panel
            with ControlPanel(
                enable_data_selection=(explorer.xarray is None),
                toggle="control_expended",
                load_dataset=explorer.load_dataset,
                import_file_upload=explorer.import_file_upload,
                export_file_download=explorer.export_state,
                xr_update_info="xr_update_info",
                panel_label=self.title,
            ).ui_content:
                if self.rendering_settings_class:
                    rendering_settings = self.rendering_settings_class(
                        ctx_name="rendering",
                        source=explorer.source,
                        update_rendering=explorer.update_rendering,
                        **self.rendering_settings_kwargs,
                    )

                    # If source already has data, update the rendering settings
                    if (
                        explorer.source
                        and hasattr(explorer.source, "input")
                        and explorer.source.input is not None
                    ):
                        rendering_settings.update_from_source(explorer.source)

        return layout
